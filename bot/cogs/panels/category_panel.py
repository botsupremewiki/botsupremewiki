import discord
from discord.ext import commands
import json
import logging
import os

logger = logging.getLogger(__name__)

PANEL_CHANNEL_ID = 1468755906304020602
STATE_FILE = "bot/data/panel_state.json"

TOGGLES = [
    {"key": "Bots",        "role_id": 1474444018988613776, "category_id": 1468716773820989695, "emoji": "🤖"},
    {"key": "Classement",  "role_id": 1474444062948982854, "category_id": 1468760267549839490, "emoji": "🏆"},
    {"key": "LOL",         "role_id": 1474444144792568024, "category_id": 1430956420014018753, "emoji": "⚔️"},
    {"key": "Mini-jeux",   "role_id": 1475346687085252648, "category_id": 1475317047998283866, "emoji": "🎮"},
    {"key": "TFT",         "role_id": 1474444191361929286, "category_id": 1462928391832600775, "emoji": "🧩"},
    {"key": "Arc Raiders", "role_id": 1474444214237532220, "category_id": 1462932316438401199, "emoji": "🏹"},
    {"key": "RPG",         "role_id": 1474444276136939663, "category_id": 1464924308215169034, "emoji": "🐉"},
    {"key": "Casino",      "role_id": 1480238800931393668, "category_id": 1480238509968199770, "emoji": "🎰"},
    {"key": "Autre",       "role_id": 1474444312518328401, "category_id": 1462928084607959227, "emoji": "📦"},
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
        logger.warning("category_panel: state file corrupted, resetting.")
        return {}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


class CategoryToggleView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        member_role_ids = {r.id for r in member.roles}
        for i, item in enumerate(TOGGLES):
            has_role = item["role_id"] in member_role_ids
            btn = discord.ui.Button(
                label=item["key"],
                emoji=item["emoji"],
                style=discord.ButtonStyle.success if has_role else discord.ButtonStyle.secondary,
                row=i // 5,
            )
            btn.callback = self._make_toggle_cb(item["role_id"])
            self.add_item(btn)

    def _make_toggle_cb(self, role_id: int):
        async def callback(interaction: discord.Interaction):
            if not isinstance(interaction.user, discord.Member):
                return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)
            me = interaction.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return await interaction.response.send_message("❌ Permission bot : Gérer les rôles.", ephemeral=True)
            user_role_ids = {r.id for r in interaction.user.roles}
            role = interaction.guild.get_role(role_id)
            if not role:
                return await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
            try:
                if role_id in user_role_ids:
                    await interaction.user.remove_roles(role, reason="Category visibility toggle")
                else:
                    await interaction.user.add_roles(role, reason="Category visibility toggle")
            except discord.Forbidden:
                return await interaction.response.send_message(
                    "❌ Hiérarchie : mets le rôle du bot au-dessus des rôles catégorie.", ephemeral=True
                )
            except discord.HTTPException as e:
                logger.warning("CategoryToggleView: erreur HTTP: %s", e)
                return await interaction.response.send_message("❌ Erreur Discord lors de la mise à jour.", ephemeral=True)
            fresh = await interaction.guild.fetch_member(interaction.user.id)
            await interaction.response.edit_message(view=CategoryToggleView(fresh))
        return callback


class CategoryPanelMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Mes préférences",
        style=discord.ButtonStyle.primary,
        emoji="⚙️",
        custom_id="category_panel:open",
    )
    async def open_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        await interaction.response.send_message(
            "⚙️ **Tes préférences de catégories**\n"
            "🟢 Vert = catégorie visible  •  ⬜ Gris = catégorie masquée",
            view=CategoryToggleView(interaction.user),
            ephemeral=True
        )


class CategoryPanelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._views_registered = False

    def build_embed(self) -> discord.Embed:
        return discord.Embed(
            title="🎛️ Préférences de catégories",
            description=(
                "Clique sur **Mes préférences** pour choisir les catégories que tu veux voir.\n\n"
                "🟢 **Vert** = catégorie visible (rôle actif)\n"
                "⬜ **Gris** = catégorie masquée (pas de rôle)"
            ),
        )

    async def ensure_panel_message(self):
        channel = self.bot.get_channel(PANEL_CHANNEL_ID)
        if channel is None:
            return

        state = load_state()
        message_id = state.get("panel_message_id")

        view = CategoryPanelMainView()
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
            logger.warning("CategoryPanelCog: erreur lors de l'upsert du panel: %s", e)

    @commands.Cog.listener()
    async def on_ready(self):
        first_ready = not self._views_registered
        if first_ready:
            self.bot.add_view(CategoryPanelMainView())
            self._views_registered = True
            self.bot._startup_queue.put_nowait(self.ensure_panel_message)
        else:
            await self.ensure_panel_message()


async def setup(bot: commands.Bot):
    await bot.add_cog(CategoryPanelCog(bot))
