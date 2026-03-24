import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import json
import math
import time
from dotenv import load_dotenv

# --- CONFIGURATION ---
LEADERBOARD_FILE       = "bot/data/lol_leaderboard.json"
LEADERBOARD_CHANNEL_ID = 1468251391775473795

# Message sur lequel le bouton "Mettre à jour" est affiché
RANK_BUTTON_CHANNEL_ID = 1468251391775473795  # même canal que le classement
RANK_BUTTON_MESSAGE_ID = 1475304070133579909

# Cooldown en secondes (2 minutes par défaut)
RANK_COOLDOWN_SECONDS = 120

SOLO_ROLES = {
    "IRON": 1462939213161824370,
    "BRONZE": 1462939266773684479,
    "SILVER": 1462939333102141626,
    "GOLD": 1462939411799871599,
    "PLATINUM": 1462939465776369805,
    "EMERALD": 1462939558852169789,
    "DIAMOND": 1462939664192245907,
    "MASTER": 1462939783037845637,
    "GRANDMASTER": 1462939857927143634,
    "CHALLENGER": 1462939935878418626,
    "UNRANKED": 1463004116950192180
}

FLEX_ROLES = {
    "IRON": 1463003693778604227,
    "BRONZE": 1464429192006467720,
    "SILVER": 1463003739328610410,
    "GOLD": 1463003764427329586,
    "PLATINUM": 1463003788112822487,
    "EMERALD": 1463003863945838847,
    "DIAMOND": 1463003994434703421,
    "MASTER": 1463004021492027403,
    "GRANDMASTER": 1463004045454213223,
    "CHALLENGER": 1463004089288753333,
    "UNRANKED": 1463004142460080159
}

POSITION_ROLES = {
    "Top":     1462935762059268230,
    "Jungle":  1462936035943256166,
    "Mid":     1462936144642834635,
    "ADC":     1462957491779276993,
    "Support": 1462936193611206912,
}

# Cooldowns en mémoire : user_id → timestamp du dernier update
_rank_cooldowns: dict[int, float] = {}


# ─── Fonctions leaderboard ────────────────────────────────────────────────────

def load_leaderboard() -> dict:
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump({"message_id": None, "players": {}}, f)
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_leaderboard(data: dict) -> None:
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ─── Modal de saisie du Riot ID ───────────────────────────────────────────────

class RankModal(discord.ui.Modal, title="Mettre à jour mon classement LoL"):
    def __init__(self, cog: "RiotStats", stored_riot_id: str | None):
        super().__init__()
        self.cog            = cog
        self.stored_riot_id = stored_riot_id

        if stored_riot_id:
            self.riot_id_input = discord.ui.TextInput(
                label="Pseudo#Tag (laisser vide = garder l'actuel)",
                placeholder=stored_riot_id,
                required=False,
                max_length=60,
            )
        else:
            self.riot_id_input = discord.ui.TextInput(
                label="Pseudo#Tag League of Legends",
                placeholder="ex : MonPseudo#EUW",
                required=True,
                max_length=60,
            )
        self.add_item(self.riot_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        riot_id = self.riot_id_input.value.strip()

        # Si le champ est vide et que l'utilisateur est déjà enregistré
        if not riot_id:
            if self.stored_riot_id:
                riot_id = self.stored_riot_id
            else:
                await interaction.response.send_message(
                    "❌ Tu dois entrer un Pseudo#Tag.", ephemeral=True
                )
                return

        # Appliquer le cooldown au moment de la soumission
        _rank_cooldowns[interaction.user.id] = time.time()

        await self.cog._process_rank_update(interaction, interaction.user, riot_id)


# ─── Vue persistante avec le bouton ──────────────────────────────────────────

class RankUpdateView(discord.ui.View):
    def __init__(self, cog: "RiotStats"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Mettre à jour mon classement",
        style=discord.ButtonStyle.primary,
        emoji="🏆",
        custom_id="lol:rank_update",
    )
    async def rank_update(self, interaction: discord.Interaction, _button: discord.ui.Button):
        # Vérification cooldown
        now       = time.time()
        last      = _rank_cooldowns.get(interaction.user.id, 0)
        remaining = RANK_COOLDOWN_SECONDS - (now - last)
        if remaining > 0:
            minutes = math.ceil(remaining / 60)
            await interaction.response.send_message(
                f"⏳ Doucement ! Attends encore **{minutes} minute(s)** avant de remettre à jour ton classement.",
                ephemeral=True,
            )
            return

        # Vérifier si déjà enregistré → pseudo actuel affiché en placeholder
        data           = load_leaderboard()
        user_info      = data["players"].get(str(interaction.user.id))
        stored_riot_id = user_info.get("riot_id") if user_info else None

        modal = RankModal(self.cog, stored_riot_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Classement par rôle",
        style=discord.ButtonStyle.secondary,
        emoji="🎯",
        custom_id="lol:role_leaderboard",
    )
    async def role_leaderboard(self, interaction: discord.Interaction, _button: discord.ui.Button):
        user_role_ids = {r.id for r in interaction.user.roles}

        # Trouver les positions du joueur
        user_positions = [name for name, rid in POSITION_ROLES.items() if rid in user_role_ids]
        if not user_positions:
            await interaction.response.send_message(
                "❌ Tu n'as aucun rôle de position (Top/Jungle/Mid/ADC/Support).",
                ephemeral=True,
            )
            return

        data    = load_leaderboard()
        players = data.get("players", {})

        embeds = []
        for position in user_positions:
            pos_role_id = POSITION_ROLES[position]

            # Filtrer les joueurs du leaderboard qui ont ce rôle
            ranked = []
            for uid_str, info in players.items():
                member = interaction.guild.get_member(int(uid_str))
                if member and any(r.id == pos_role_id for r in member.roles):
                    ranked.append((uid_str, info))

            ranked.sort(key=lambda x: x[1].get("total_score", 0), reverse=True)

            embed = discord.Embed(
                title=f"🎯 Classement {position}",
                color=discord.Color.blurple(),
            )

            if not ranked:
                embed.description = "*Aucun joueur avec ce rôle n'est inscrit au classement.*"
            else:
                lines = []
                for i, (uid_str, info) in enumerate(ranked[:15]):
                    medal   = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"**{i+1}.**"
                    riot_id = info.get("riot_id", "Inconnu")
                    score   = info.get("total_score", 0)
                    sq_tier = info.get("solo_tier", "Unranked").capitalize()
                    sq_rank = info.get("solo_rank", "")
                    sq_wr   = info.get("solo_wr", 0)
                    sq_emoji = self.cog.format_rank_emoji(sq_tier)
                    lines.append(
                        f"{medal} <@{uid_str}> (`{riot_id}`) — **{score} pts**\n"
                        f"└ {sq_emoji} {sq_tier} {sq_rank} | {sq_wr}% WR"
                    )
                embed.description = "\n".join(lines)

            embeds.append(embed)

        await interaction.response.send_message(embeds=embeds, ephemeral=True)


# ─── Cog principal ────────────────────────────────────────────────────────────

class RiotStats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        """Enregistre la vue persistante et ajoute le bouton au message cible."""
        self.bot.add_view(RankUpdateView(self))
        self.bot.loop.create_task(self._attach_button_to_message())

    async def _attach_button_to_message(self):
        """Attend que le bot soit prêt, puis édite le message pour y ajouter le bouton."""
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(RANK_BUTTON_CHANNEL_ID)
        if not channel:
            return
        try:
            msg = await channel.fetch_message(RANK_BUTTON_MESSAGE_ID)
            await msg.edit(view=RankUpdateView(self))
        except Exception as e:
            print(f"[RiotStats] Impossible d'attacher le bouton au message {RANK_BUTTON_MESSAGE_ID}: {e}")

    def get_api_key(self):
        load_dotenv("c:/Users/eliot/Desktop/work/discord/bot-ultime/.env", override=True)
        return os.getenv("RIOT_API_KEY")

    async def fetch(self, session, url):
        key = self.get_api_key()
        if not key:
            return {"_error": "NO_API_KEY"}
        headers = {"X-Riot-Token": key}
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"_error": response.status}
        except Exception as e:
            return {"_error": f"Exception: {str(e)}"}

    async def get_puuid(self, game_name: str, tag_line: str) -> dict:
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, url)

    async def get_summoner_id(self, puuid: str, region: str = "euw1") -> dict:
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, url)

    async def get_ranked_stats(self, puuid: str, region: str = "euw1") -> dict:
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
        async with aiohttp.ClientSession() as session:
            return await self.fetch(session, url)

    def calculate_score(self, wins: int, losses: int, tier: str) -> float:
        total_games = wins + losses
        if total_games == 0:
            return 0.0
        winrate          = wins / total_games
        multiplier       = 1.0 + (total_games * 0.001)
        performance_score = (winrate * 100) * multiplier
        tier_scores = {
            "IRON": 10, "BRONZE": 10,
            "SILVER": 25, "GOLD": 25,
            "PLATINUM": 50, "EMERALD": 50,
            "DIAMOND": 100, "MASTER": 150, "GRANDMASTER": 150, "CHALLENGER": 200,
            "UNRANKED": 0
        }
        rank_bonus = tier_scores.get(tier.upper(), 0)
        return round(performance_score + rank_bonus, 2)

    async def update_leaderboard_message(self):
        channel = self.bot.get_channel(LEADERBOARD_CHANNEL_ID)
        if not channel:
            return

        data    = load_leaderboard()
        players = data.get("players", {})
        sorted_players = sorted(players.items(), key=lambda x: x[1].get("total_score", 0), reverse=True)

        embed = discord.Embed(
            title="🏆 Classement League of Legends du Serveur",
            color=discord.Color.gold()
        )

        desc = "Le palmarès de la Saison 2026 !\nUtilise le bouton **Mettre à jour mon classement** pour actualiser ta position !\n\n"

        if not sorted_players:
            desc += "*Aucun joueur n'est classé pour le moment.*"
        else:
            board_text = ""
            for i, (user_id, p_info) in enumerate(sorted_players[:20]):
                medal    = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"**{i+1}.**"
                riot_id  = p_info.get("riot_id", "Inconnu")
                score    = p_info.get("total_score", 0)
                sq_tier  = p_info.get("solo_tier", "Unranked").capitalize()
                sq_rank  = p_info.get("solo_rank", "")
                sq_wr    = p_info.get("solo_wr", 0)
                sq_games = p_info.get("solo_wins", 0) + p_info.get("solo_losses", 0)
                fx_tier  = p_info.get("flex_tier", "Unranked").capitalize()
                fx_rank  = p_info.get("flex_rank", "")
                fx_wr    = p_info.get("flex_wr", 0)
                fx_games = p_info.get("flex_wins", 0) + p_info.get("flex_losses", 0)
                sq_emoji = self.format_rank_emoji(sq_tier)
                fx_emoji = self.format_rank_emoji(fx_tier)
                board_text += f"{medal} <@{user_id}> (`{riot_id}`) - **{score} pts**\n"
                board_text += f"└ {sq_emoji} **SoloQ**: {sq_tier} {sq_rank} | {sq_wr}% WR | {sq_games} games\n"
                board_text += f"└ {fx_emoji} **FlexQ**: {fx_tier} {fx_rank} | {fx_wr}% WR | {fx_games} games\n\n"
            desc += board_text

        embed.description = desc

        message_id = data.get("message_id")
        msg = None
        if message_id:
            try:
                msg = await channel.fetch_message(int(message_id))
            except Exception:
                pass

        if msg:
            try:
                await msg.edit(embed=embed)
            except Exception:
                pass
        else:
            try:
                new_msg = await channel.send(embed=embed)
                data["message_id"] = new_msg.id
                save_leaderboard(data)
            except Exception:
                pass

    def format_rank_emoji(self, tier: str) -> str:
        tier_emojis = {
            "IRON": "🟤", "BRONZE": "🟠", "SILVER": "⚪", "GOLD": "🟡",
            "PLATINUM": "🟢", "EMERALD": "🟩", "DIAMOND": "💎",
            "MASTER": "🟣", "GRANDMASTER": "🔴", "CHALLENGER": "👑",
            "UNRANKED": "➖"
        }
        return tier_emojis.get(tier.upper(), "🏅")

    async def _process_rank_update(
        self,
        interaction: discord.Interaction,
        target_member: discord.Member,
        riot_id: str,
        region: str = "euw1",
    ):
        if not self.get_api_key():
            await interaction.response.send_message(
                "❌ La clé API Riot n'est pas configurée dans le fichier `.env`.",
                ephemeral=True
            )
            return

        if "#" not in riot_id:
            await interaction.response.send_message(
                "❌ Format invalide. Utilise le format `Pseudo#Tag` (ex : MonPseudo#EUW)",
                ephemeral=True
            )
            return

        region = region.lower()
        if region in ["euw", "eu"]:  region = "euw1"
        if region in ["eune"]:       region = "eun1"
        if region in ["na"]:         region = "na1"

        await interaction.response.defer(ephemeral=True)
        game_name, tag_line = riot_id.split("#", 1)

        # 1. PUUID
        account_data = await self.get_puuid(game_name, tag_line)
        if "_error" in account_data:
            err = account_data["_error"]
            if err == 404:
                await interaction.followup.send(f"❌ Joueur **{riot_id}** introuvable (404).", ephemeral=True)
            elif err == 403:
                await interaction.followup.send("❌ Clé API Riot invalide ou expirée (403).", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erreur API Riot : `{err}`", ephemeral=True)
            return

        puuid = account_data.get("puuid")

        # 2. Summoner
        summoner_data = await self.get_summoner_id(puuid, region)
        if "_error" in summoner_data:
            err = summoner_data["_error"]
            msg = (f"❌ Pas de profil LoL pour **{riot_id}** sur `{region}`." if err == 404
                   else f"❌ Erreur Summoner API : `{err}`.")
            await interaction.followup.send(msg, ephemeral=True)
            return

        # 3. Stats Ranked
        stats_data = await self.get_ranked_stats(puuid, region)
        if isinstance(stats_data, dict) and "_error" in stats_data:
            await interaction.followup.send(
                f"❌ Impossible de récupérer le classement (erreur API : `{stats_data['_error']}`).",
                ephemeral=True
            )
            return

        solo_queue = flex_queue = None
        if isinstance(stats_data, list):
            for queue in stats_data:
                if queue.get("queueType") == "RANKED_SOLO_5x5":
                    solo_queue = queue
                elif queue.get("queueType") == "RANKED_FLEX_SR":
                    flex_queue = queue

        # Parse Solo Queue
        sq_tier   = solo_queue.get("tier", "UNRANKED").capitalize() if solo_queue else "Unranked"
        sq_rank   = solo_queue.get("rank", "")              if solo_queue else ""
        sq_lp     = solo_queue.get("leaguePoints", 0)       if solo_queue else 0
        sq_wins   = solo_queue.get("wins", 0)               if solo_queue else 0
        sq_losses = solo_queue.get("losses", 0)             if solo_queue else 0
        sq_total  = sq_wins + sq_losses
        sq_wr     = round((sq_wins / sq_total) * 100, 1)    if sq_total > 0 else 0

        # Parse Flex Queue
        fx_tier   = flex_queue.get("tier", "UNRANKED").capitalize() if flex_queue else "Unranked"
        fx_rank   = flex_queue.get("rank", "")              if flex_queue else ""
        fx_lp     = flex_queue.get("leaguePoints", 0)       if flex_queue else 0
        fx_wins   = flex_queue.get("wins", 0)               if flex_queue else 0
        fx_losses = flex_queue.get("losses", 0)             if flex_queue else 0
        fx_total  = fx_wins + fx_losses
        fx_wr     = round((fx_wins / fx_total) * 100, 1)    if fx_total > 0 else 0

        season_total  = sq_total  + fx_total
        season_wins   = sq_wins   + fx_wins
        season_losses = sq_losses + fx_losses
        season_wr     = round((season_wins / season_total) * 100, 1) if season_total > 0 else 0

        solo_score  = self.calculate_score(sq_wins, sq_losses, sq_tier)
        flex_score  = self.calculate_score(fx_wins, fx_losses, fx_tier)
        total_score = round(solo_score + (flex_score * 0.7), 2)

        # Sauvegarde
        lb_data = load_leaderboard()
        lb_data["players"][str(target_member.id)] = {
            "riot_id": riot_id,
            "region": region.upper(),
            "total_score": total_score,
            "solo_tier": sq_tier, "solo_rank": sq_rank,
            "solo_wins": sq_wins, "solo_losses": sq_losses, "solo_wr": sq_wr,
            "flex_tier": fx_tier, "flex_rank": fx_rank,
            "flex_wins": fx_wins, "flex_losses": fx_losses, "flex_wr": fx_wr,
            "winrate": season_wr, "total_games": season_total,
        }
        save_leaderboard(lb_data)
        self.bot.loop.create_task(self.update_leaderboard_message())

        # Attribution des rôles
        if isinstance(target_member, discord.Member):
            all_role_ids  = list(SOLO_ROLES.values()) + list(FLEX_ROLES.values())
            roles_to_remove = [r for r in target_member.roles if r.id in all_role_ids]
            solo_role_id  = SOLO_ROLES.get(sq_tier.upper(), SOLO_ROLES["UNRANKED"])
            flex_role_id  = FLEX_ROLES.get(fx_tier.upper(), FLEX_ROLES["UNRANKED"])
            roles_to_add  = [r for rid in [solo_role_id, flex_role_id]
                             if (r := interaction.guild.get_role(rid))]
            roles_to_remove = [r for r in roles_to_remove if r not in roles_to_add]
            try:
                if roles_to_remove:
                    await target_member.remove_roles(*roles_to_remove, reason="Bot Ultime: rang LoL")
                if roles_to_add:
                    await target_member.add_roles(*roles_to_add, reason="Bot Ultime: rang LoL")
            except discord.Forbidden:
                print("Permissions insuffisantes pour attribuer les rôles.")
            except Exception as e:
                print(f"Erreur rôles : {e}")

        # Embed de réponse
        sq_emoji = self.format_rank_emoji(sq_tier)
        fx_emoji = self.format_rank_emoji(fx_tier)
        profile_icon_id = summoner_data.get("profileIconId", 1)

        embed = discord.Embed(
            title=f"Statistiques Saison en Cours — {game_name}#{tag_line} ({region.upper()})",
            color=discord.Color.from_rgb(0, 170, 255),
        )
        embed.set_thumbnail(
            url=f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{profile_icon_id}.jpg"
        )
        embed.add_field(
            name="🏆 Classement Actuel",
            value=(
                f"**Soloqueue**\n"
                f"{sq_emoji} **{sq_tier} {sq_rank}** — {sq_lp} LP\n"
                f"*{sq_wins}V – {sq_losses}D  ({sq_wr}% WR)*\n\n"
                f"**Draft Ranked Flex**\n"
                f"{fx_emoji} **{fx_tier} {fx_rank}** — {fx_lp} LP\n"
                f"*{fx_wins}V – {fx_losses}D  ({fx_wr}% WR)*"
            ),
            inline=False,
        )
        embed.add_field(
            name="🌍 Saison (Solo + Flex)",
            value=(
                f"⚔️ **Parties** : {season_total} | ✅ {season_wins}V ❌ {season_losses}D\n"
                f"📊 **Winrate global** : **{season_wr}%**\n"
                f"⭐ **Score Bot Ultime** : **{total_score} pts** ✨"
            ),
            inline=False,
        )
        embed.set_footer(text=f"Score mis à jour pour {target_member.display_name} !")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ─── Commande admin (sans cooldown, pour les modérateurs) ─────────────────

    @app_commands.command(
        name="admin_rank",
        description="Met à jour manuellement le classement d'un joueur (admin, sans cooldown)",
    )
    @app_commands.describe(
        membre="Le membre Discord à mettre à jour",
        riot_id="Son pseudo Riot complet (ex : Faker#KR1)",
        region="Sa région (ex : euw1, na1, kr) — défaut : euw1",
    )
    async def admin_rank(
        self,
        interaction: discord.Interaction,
        membre: discord.Member,
        riot_id: str,
        region: str = "euw1",
    ):
        await self._process_rank_update(interaction, membre, riot_id, region)


async def setup(bot: commands.Bot):
    await bot.add_cog(RiotStats(bot))
