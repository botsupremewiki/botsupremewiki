import discord
from discord.ext import commands
import json
import logging
import os

logger = logging.getLogger(__name__)

PANEL_CHANNEL_ID = 1462944485905268816
STATE_FILE = "bot/data/roles_lol_state.json"

ROLES_LOL = [
    {"name": "Top", "id": 1462935762059268230},
    {"name": "Jungle", "id": 1462936035943256166},
    {"name": "Mid", "id": 1462936144642834635},
    {"name": "ADC", "id": 1462957491779276993},
    {"name": "Support", "id": 1462936193611206912}
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

class RoleButton(discord.ui.Button):
    def __init__(self, role_name: str, role_id: int):
        super().__init__(
            label=role_name,
            style=discord.ButtonStyle.secondary,
            custom_id=f"role_lol:{role_id}"
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ Rôle introuvable sur le serveur.", ephemeral=True)
        
        # Vérification des permissions
        me = interaction.guild.me
        if not me or not me.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Je n'ai pas la permission de gérer les rôles.", ephemeral=True)
        if role.position >= me.top_role.position:
            return await interaction.response.send_message(f"❌ Mon rôle est placé trop bas pour attribuer le rôle {role.name}.", ephemeral=True)

        try:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"📉 Tu as retiré ton rôle **{role.name}**.", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"📈 Tu as ajouté le rôle **{role.name}** !", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je ne peux pas modifier ce rôle (hiérarchie).", ephemeral=True)
        except discord.HTTPException as e:
            logger.warning("RoleButton: erreur HTTP en modifiant le rôle: %s", e)
            await interaction.response.send_message("❌ Erreur Discord en modifiant le rôle.", ephemeral=True)

class MyRolesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Mes rôles",
            style=discord.ButtonStyle.primary,
            custom_id="role_lol:my_roles",
            emoji="📌",
            row=1  # Placée sur la deuxième ligne
        )
        
    async def callback(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        role_ids = [r["id"] for r in ROLES_LOL]
        user_roles = [r for r in interaction.user.roles if r.id in role_ids]
        
        if not user_roles:
            return await interaction.response.send_message("Tu n'as aucun rôle parmi Top, Jungle, Mid, ADC ou Support pour le moment.", ephemeral=True)
        
        roles_str = "\n".join([f"• {r.name}" for r in user_roles])
        await interaction.response.send_message(f"📌 **Tes rôles actuels :**\n{roles_str}", ephemeral=True)

class RolePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Ajout des boutons de rôles
        for role_data in ROLES_LOL:
            self.add_item(RoleButton(role_name=role_data["name"], role_id=role_data["id"]))
            
        # Ajout du bouton "Mes rôles"
        self.add_item(MyRolesButton())

class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._views_registered = False

    def build_embed(self) -> discord.Embed:
        return discord.Embed(
            title="✨ Choisis ton rôle League of Legends",
            description=(
                "Clique sur un bouton pour **ajouter** ou **retirer** ton rôle.\n"
                "📌 Utilise **Mes rôles** pour voir ta sélection actuelle.\n\n"
                "*Tu peux changer de rôle à tout moment.*"
            ),
            color=discord.Color.blurple()
        )

    async def ensure_panel_message(self):
        channel = self.bot.get_channel(PANEL_CHANNEL_ID)
        if channel is None:
            return

        state = load_state()
        message_id = state.get("panel_message_id")

        view = RolePanelView()
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
        # On enregistre la vue au démarrage pour que les boutons restent interactifs
        if not self._views_registered:
            self.bot.add_view(RolePanelView())
            self._views_registered = True

        # On s'assure que le message est présent et à jour dans le salon
        await self.ensure_panel_message()

async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))
