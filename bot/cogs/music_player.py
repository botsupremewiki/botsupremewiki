import discord
from discord.ext import commands
import yt_dlp
import asyncio
import functools
import json
import os

yt_dlp.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractor_args': {'youtube': {'player_client': ['android']}},
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

MUSIC_HUB_CHANNEL_ID = 1468287521656934601
MUSIC_HUB_FILE       = "bot/data/music_hub.json"


# ─── Persistance du message hub ───────────────────────────────────────────────

def load_hub_data() -> dict:
    os.makedirs(os.path.dirname(MUSIC_HUB_FILE), exist_ok=True)
    if not os.path.exists(MUSIC_HUB_FILE):
        with open(MUSIC_HUB_FILE, "w", encoding="utf-8") as f:
            json.dump({"message_id": None}, f)
    with open(MUSIC_HUB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_hub_data(data: dict) -> None:
    os.makedirs(os.path.dirname(MUSIC_HUB_FILE), exist_ok=True)
    with open(MUSIC_HUB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ─── Modal de recherche ───────────────────────────────────────────────────────

class PlayModal(discord.ui.Modal, title="🎵 Jouer une musique"):
    def __init__(self, cog: "MusicCog"):
        super().__init__()
        self.cog = cog
        self.recherche = discord.ui.TextInput(
            label="Titre ou lien YouTube",
            placeholder="ex : Bohemian Rhapsody Queen",
            required=True,
            max_length=200,
        )
        self.add_item(self.recherche)

    async def on_submit(self, interaction: discord.Interaction):
        await self.cog._play(interaction, self.recherche.value.strip())


# ─── Vue persistante (bouton Pause/Resume dynamique) ─────────────────────────

class MusicHubView(discord.ui.View):
    def __init__(self, cog: "MusicCog", paused: bool = False):
        super().__init__(timeout=None)
        self.cog = cog

        # 🎵 Jouer
        b_play = discord.ui.Button(
            label="Jouer", style=discord.ButtonStyle.success,
            emoji="🎵", custom_id="music:play", row=0,
        )
        b_play.callback = self._play_cb
        self.add_item(b_play)

        # ⏸️ Pause  /  ▶️ Resume  (dynamique selon l'état)
        b_pause = discord.ui.Button(
            label="Resume" if paused else "Pause",
            style=discord.ButtonStyle.secondary,
            emoji="▶️" if paused else "⏸️",
            custom_id="music:pause", row=0,
        )
        b_pause.callback = self._pause_cb
        self.add_item(b_pause)

        # ⏭️ Skip
        b_skip = discord.ui.Button(
            label="Skip", style=discord.ButtonStyle.primary,
            emoji="⏭️", custom_id="music:skip", row=0,
        )
        b_skip.callback = self._skip_cb
        self.add_item(b_skip)

        # 🛑 Stop
        b_stop = discord.ui.Button(
            label="Stop", style=discord.ButtonStyle.danger,
            emoji="🛑", custom_id="music:stop", row=0,
        )
        b_stop.callback = self._stop_cb
        self.add_item(b_stop)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    async def _play_cb(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Tu dois être dans un salon vocal pour lancer de la musique !", ephemeral=True
            )
            return
        await interaction.response.send_modal(PlayModal(self.cog))

    async def _pause_cb(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Je ne suis pas connecté à un salon vocal.", ephemeral=True)
            return
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message("❌ Tu dois être dans mon salon vocal.", ephemeral=True)
            return
        if not vc.is_playing() and not vc.is_paused():
            await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)
            return

        if vc.is_paused():
            vc.resume()
        else:
            vc.pause()

        await interaction.response.defer()
        await self.cog._update_hub_message(interaction.guild.id)

    async def _skip_cb(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Je ne suis pas connecté à un salon vocal.", ephemeral=True)
            return
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message("❌ Tu dois être dans mon salon vocal.", ephemeral=True)
            return
        if not vc.is_playing() and not vc.is_paused():
            await interaction.response.send_message("❌ Aucune musique en cours de lecture.", ephemeral=True)
            return

        vc.stop()  # déclenche play_next via after=
        await interaction.response.defer()

    async def _stop_cb(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Je ne suis pas connecté à un salon vocal.", ephemeral=True)
            return
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message("❌ Tu dois être dans mon salon vocal.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        self.cog.queues[guild_id]       = []
        self.cog.current_song[guild_id] = None
        await interaction.response.defer()
        vc.stop()
        await vc.disconnect()
        await self.cog._update_hub_message(guild_id)


# ─── Cog principal ────────────────────────────────────────────────────────────

class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot           = bot
        self.queues:        dict[int, list]      = {}
        self.current_song:  dict[int, str | None] = {}
        self._hub_message:  discord.Message | None = None

    async def cog_load(self):
        self.bot.add_view(MusicHubView(self))
        self.bot.loop.create_task(self._attach_hub_message())

    async def _attach_hub_message(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(MUSIC_HUB_CHANNEL_ID)
        if not channel:
            print(f"[MusicCog] Canal {MUSIC_HUB_CHANNEL_ID} introuvable.")
            return

        hub_data = load_hub_data()
        msg_id   = hub_data.get("message_id")
        embed    = self._build_embed(None, paused=False)
        view     = MusicHubView(self)

        if msg_id:
            try:
                self._hub_message = await channel.fetch_message(int(msg_id))
                await self._hub_message.edit(embed=embed, view=view)
                return
            except Exception:
                pass  # Message supprimé → création

        self._hub_message = await channel.send(embed=embed, view=view)
        hub_data["message_id"] = self._hub_message.id
        save_hub_data(hub_data)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_queue(self, guild_id: int) -> list:
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def _build_embed(self, guild_id: int | None, paused: bool = False) -> discord.Embed:
        current = self.current_song.get(guild_id) if guild_id else None
        queue   = self.get_queue(guild_id)         if guild_id else []

        embed = discord.Embed(title="🎵 Lecteur de Musique", color=discord.Color.purple())

        if current:
            status = f"⏸️ `{current}` *(en pause)*" if paused else f"▶️ `{current}`"
        else:
            status = "*Aucune musique en cours*"
        embed.add_field(name="En cours", value=status, inline=False)

        if queue:
            q_lines = "\n".join(f"**{i+1}.** `{s['title']}`" for i, s in enumerate(queue[:10]))
            if len(queue) > 10:
                q_lines += f"\n*... et {len(queue) - 10} autres morceaux.*"
            embed.add_field(name="📋 File d'attente", value=q_lines, inline=False)
        else:
            embed.add_field(name="📋 File d'attente", value="*Vide*", inline=False)

        embed.set_footer(text="Utilise les boutons ci-dessous pour contrôler la musique !")
        return embed

    async def _update_hub_message(self, guild_id: int | None = None):
        if not self._hub_message:
            return
        paused = False
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if guild and guild.voice_client:
                paused = guild.voice_client.is_paused()
        embed = self._build_embed(guild_id, paused=paused)
        try:
            await self._hub_message.edit(embed=embed, view=MusicHubView(self, paused=paused))
        except Exception as e:
            print(f"[MusicCog] Impossible d'éditer le message hub : {e}")

    # ── Lecture ───────────────────────────────────────────────────────────────

    def play_next(self, guild_id: int):
        """Appelé en callback FFmpeg (thread audio) — doit rester synchrone."""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        vc    = guild.voice_client
        queue = self.get_queue(guild_id)

        if queue:
            next_song = queue.pop(0)
            self.current_song[guild_id] = next_song["title"]
            source = discord.FFmpegPCMAudio(next_song["url"], executable="ffmpeg.exe", **ffmpeg_options)
            vc.play(discord.PCMVolumeTransformer(source, volume=0.5),
                    after=lambda _e: self.play_next(guild_id))
            asyncio.run_coroutine_threadsafe(self._update_hub_message(guild_id), self.bot.loop)
        else:
            self.current_song[guild_id] = None
            asyncio.run_coroutine_threadsafe(vc.disconnect(),                    self.bot.loop)
            asyncio.run_coroutine_threadsafe(self._update_hub_message(guild_id), self.bot.loop)

    async def _play(self, interaction: discord.Interaction, recherche: str):
        """Logique de lecture appelée depuis le modal."""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Tu dois être dans un salon vocal !", ephemeral=True)
            return

        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        vc            = interaction.guild.voice_client

        if not vc:
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        try:
            query      = recherche if recherche.startswith("http") else f"ytsearch:{recherche}"
            extract_fn = functools.partial(ytdl.extract_info, query, download=False)
            data       = await self.bot.loop.run_in_executor(None, extract_fn)

            if "entries" in data:
                data = data["entries"][0]

            song_info = {
                "url":   data["url"],
                "title": data.get("title", "Titre Inconnu"),
            }

            guild_id = interaction.guild.id
            queue    = self.get_queue(guild_id)

            if not vc.is_playing() and not vc.is_paused():
                self.current_song[guild_id] = song_info["title"]
                source = discord.FFmpegPCMAudio(song_info["url"], executable="ffmpeg.exe", **ffmpeg_options)
                vc.play(discord.PCMVolumeTransformer(source, volume=0.5),
                        after=lambda _e: self.play_next(guild_id))
            else:
                queue.append(song_info)

            await self._update_hub_message(guild_id)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la recherche :\n`{e}`", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
