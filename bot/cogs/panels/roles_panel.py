import discord
from discord.ext import commands
import json
import logging
import os

logger = logging.getLogger(__name__)

PANEL_CHANNEL_ID = 1462944485905268816
STATE_FILE = "bot/data/roles_lol_state.json"

ROLES_LOL = [
    {"name": "Top",     "id": 1462935762059268230, "emoji": "🛡️"},
    {"name": "Jungle",  "id": 1462936035943256166, "emoji": "🌿"},
    {"name": "Mid",     "id": 1462936144642834635, "emoji": "⚡"},
    {"name": "ADC",     "id": 1462957491779276993, "emoji": "🏹"},
    {"name": "Support", "id": 1462936193611206912, "emoji": "💊"},
]


def load_state() -> dict:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("roles_panel: state file corrupted, resetting.")
        return {}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


class RoleToggleView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        member_role_ids = {r.id for r in member.roles}
        for item in ROLES_LOL:
            has_role = item["id"] in member_role_ids
            btn = discord.ui.Button(
                label=item["name"],
                emoji=item["emoji"],
                style=discord.ButtonStyle.success if has_role else discord.ButtonStyle.secondary,
                row=0,
            )
            btn.callback = self._make_toggle_cb(item["id"])
            self.add_item(btn)

    def _make_toggle_cb(self, role_id: int):
        async def callback(interaction: discord.Interaction):
            if not isinstance(interaction.user, discord.Member):
                return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)
            me = interaction.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return await interaction.response.send_message("❌ Permission bot : Gérer les rôles.", ephemeral=True)
            role = interaction.guild.get_role(role_id)
            if not role:
                return await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
            if role.position >= me.top_role.position:
                return await interaction.response.send_message(
                    f"❌ Mon rôle est trop bas pour attribuer **{role.name}**.", ephemeral=True
                )
            try:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role, reason="Role panel toggle")
                else:
                    await interaction.user.add_roles(role, reason="Role panel toggle")
            except discord.Forbidden:
                return await interaction.response.send_message("❌ Hiérarchie insuffisante.", ephemeral=True)
            except discord.HTTPException as e:
                logger.warning("RoleToggleView: erreur HTTP: %s", e)
                return await interaction.response.send_message("❌ Erreur Discord lors de la mise à jour.", ephemeral=True)
            fresh = await interaction.guild.fetch_member(interaction.user.id)
            await interaction.response.edit_message(view=RoleToggleView(fresh))
        return callback


class RolePanelMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Mes Rôles",
        style=discord.ButtonStyle.primary,
        emoji="🎮",
        custom_id="role_lol:open",
    )
    async def open_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        await interaction.response.send_message(
            "🎮 **Tes rôles League of Legends**\n"
            "🟢 Vert = rôle actif  •  ⬜ Gris = rôle inactif",
            view=RoleToggleView(interaction.user),
            ephemeral=True
        )


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._views_registered = False

    def build_embed(self) -> discord.Embed:
        return discord.Embed(
            title="✨ Choisis ton rôle League of Legends",
            description=(
                "Clique sur **Mes Rôles** pour sélectionner tes rôles.\n\n"
                "🟢 **Vert** = rôle actif\n"
                "⬜ **Gris** = rôle inactif\n\n"
                "*Tu peux activer plusieurs rôles simultanément.*"
            ),
            color=discord.Color.blurple()
        )

    async def ensure_panel_message(self):
        channel = self.bot.get_channel(PANEL_CHANNEL_ID)
        if channel is None:
            return

        state = load_state()
        message_id = state.get("panel_message_id")

        view = RolePanelMainView()
        embed = self.build_embed()

        msg = None
        if message_id:
            try:
                msg = await channel.fetch_message(int(message_id))
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                msg = None

        try:
            if msg:
                await msg.edit(embed=embed, view=view)
            else:
                new_msg = await channel.send(embed=embed, view=view)
                state["panel_message_id"] = new_msg.id
                save_state(state)
        except discord.HTTPException as e:
            logger.warning("RolesCog: erreur lors de l'upsert du panel: %s", e)

    @commands.Cog.listener()
    async def on_ready(self):
        first_ready = not self._views_registered
        if first_ready:
            self.bot.add_view(RolePanelMainView())
            self._views_registered = True
            self.bot._startup_queue.put_nowait(self.ensure_panel_message)
        else:
            await self.ensure_panel_message()


async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))
