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
    {"key": "RPG",         "role_id": 1480238800931393668, "category_id": 1480238509968199770, "emoji": "🎲"},
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


def _build_options_for(member: discord.Member) -> list[discord.SelectOption]:
    member_role_ids = {r.id for r in member.roles}
    options = []
    for item in TOGGLES:
        role_id = item["role_id"]
        has_role = role_id in member_role_ids

        # ✅ Coché = l'utilisateur A le rôle (donc catégorie visible)
        options.append(
            discord.SelectOption(
                label=item["key"],
                value=str(role_id),
                emoji=item.get("emoji"),
                description="Visible" if has_role else "Masquée",
                default=has_role,
            )
        )
    return options


class CategoryVisibilitySelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        super().__init__(
            placeholder="Coche ce que tu veux VOIR 👀 (coché = rôle donné)",
            min_values=0,
            max_values=len(TOGGLES),
            options=_build_options_for(member),
            custom_id="category_panel:visibility_select",
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        me = interaction.guild.me
        if not me or not me.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Permission bot: Gérer les rôles.", ephemeral=True)

        # Ici: values = rôles que l'utilisateur VEUT AVOIR (donc visible)
        wanted_role_ids = {int(v) for v in self.values}
        user_role_ids = {r.id for r in interaction.user.roles}

        to_add = []
        to_remove = []

        for item in TOGGLES:
            rid = item["role_id"]
            wants_role = rid in wanted_role_ids
            has_role = rid in user_role_ids

            if wants_role and not has_role:
                to_add.append(rid)        # coché => ajouter role catRole
            if (not wants_role) and has_role:
                to_remove.append(rid)     # décoché => retirer role catRole

        try:
            for rid in to_add:
                role = interaction.guild.get_role(rid)
                if role:
                    await interaction.user.add_roles(role, reason="Category visibility toggle (catRole added)")
            for rid in to_remove:
                role = interaction.guild.get_role(rid)
                if role:
                    await interaction.user.remove_roles(role, reason="Category visibility toggle (catRole removed)")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ Hiérarchie: mets le rôle du bot au-dessus des rôles catRole.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            logger.warning("CategoryVisibilitySelect: erreur HTTP lors de la modification des rôles: %s", e)
            return await interaction.response.send_message("❌ Erreur Discord lors de la mise à jour des rôles.", ephemeral=True)

        # Rafraîchir l'UI en fonction des rôles actuels
        await interaction.response.edit_message(
            content="✅ Mis à jour. (coché = rôle donné = visible)",
            view=CategoryPanelEphemeralView(interaction.user)
        )


class CategoryPanelEphemeralView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        self.add_item(CategoryVisibilitySelect(member))


class CategoryPanelMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Préférences",
        style=discord.ButtonStyle.primary,
        emoji="⚙️",
        custom_id="category_panel:open",
    )
    async def open_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        await interaction.response.send_message(
            "🧩 **Choisis les catégories que tu veux voir**\n"
            "✅ Cochée = tu reçois le rôle (visible)\n"
            "⬜ Décochée = rôle retiré (masquée)",
            view=CategoryPanelEphemeralView(interaction.user),
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
                "Clique sur **Préférences** pour choisir les catégories que tu veux voir.\n\n"
                "✅ Cochée = rôle donné (visible)\n"
                "⬜ Décochée = rôle retiré (masquée)"
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
        # IMPORTANT pour que le bouton reste actif après redémarrage
        if not self._views_registered:
            self.bot.add_view(CategoryPanelMainView())
            self._views_registered = True

        await self.ensure_panel_message()


async def setup(bot: commands.Bot):
    await bot.add_cog(CategoryPanelCog(bot))