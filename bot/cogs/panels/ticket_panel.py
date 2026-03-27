import discord
from discord.ext import commands
import json
import logging
import os

logger = logging.getLogger(__name__)

# ⚠️ REMPLACE CES ID PAR LES BONS ! ⚠️
TICKET_PANEL_CHANNEL_ID = 1463037892757557464  # L'ID du salon où afficher les boutons (le salon ticket public)
TICKET_CATEGORY_ID = 1430956420014018752       # L'ID de la catégorie où les tickets seront créés (facultatif, tu peux mettre None)
STAFF_ROLE_ID = 1441539810069053440            # Le rôle Staff qui aura accès aux tickets

STATE_FILE = "bot/data/ticket_state.json"

TICKET_TYPES = [
    {"label": "Problème technique / Bug / Bot", "emoji": "🛠️", "color": discord.ButtonStyle.primary, "prefix": "bug"},
    {"label": "Signalement d'un utilisateur", "emoji": "🚨", "color": discord.ButtonStyle.danger, "prefix": "report"},
    {"label": "Demande ou problème de rôle", "emoji": "🎭", "color": discord.ButtonStyle.primary, "prefix": "role"},
    {"label": "Suggestion / idée", "emoji": "💡", "color": discord.ButtonStyle.primary, "prefix": "idea"},
    {"label": "Autre sujet", "emoji": "❓", "color": discord.ButtonStyle.primary, "prefix": "other"},
]

def load_state() -> dict:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"panel_message_id": None, "active_tickets": {}}, f)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("ticket_panel: state file corrupted, resetting.")
        return {"panel_message_id": None, "active_tickets": {}}

def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)

class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket:btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            return
        
        # On lit l'état pour supprimer la restriction d'un seul ticket
        state = load_state()
        user_id_to_remove = None
        for uid, cid in state.get("active_tickets", {}).items():
            if cid == interaction.channel.id:
                user_id_to_remove = uid
                break
        
        if user_id_to_remove:
            del state["active_tickets"][user_id_to_remove]
            save_state(state)

        await interaction.response.send_message("Suppression du ticket en cours...", ephemeral=True)
        try:
            await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")
        except discord.Forbidden:
            await interaction.followup.send("❌ Je n'ai pas la permission de supprimer ce salon.", ephemeral=True)
        except discord.HTTPException as e:
            logger.warning("CloseTicketButton: erreur lors de la suppression du salon: %s", e)

class TicketButton(discord.ui.Button):
    def __init__(self, t_type: dict):
        super().__init__(
            label=t_type["label"],
            style=t_type["color"],
            emoji=t_type["emoji"],
            custom_id=f"create_ticket:{t_type['prefix']}"
        )
        self.t_type = t_type

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Serveur uniquement.", ephemeral=True)

        user_id_str = str(interaction.user.id)
        state = load_state()

        # Vérifier si l'utilisateur a déjà un ticket
        active_tickets = state.get("active_tickets", {})
        if user_id_str in active_tickets:
            existing_channel_id = active_tickets[user_id_str]
            existing_channel = interaction.guild.get_channel(existing_channel_id)
            if existing_channel:
                return await interaction.response.send_message(
                    f"❌ Tu as déjà un ticket ouvert ici : {existing_channel.mention}",
                    ephemeral=True
                )
            else:
                # Le salon n'existe plus (supprimé manuellement), on nettoie l'état
                del active_tickets[user_id_str]

        # Création du salon
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        # Définition des permissions (Le membre peut voir/écrire, @everyone ne peut rien voir)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        # Ajouter le rôle staff si configuré
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{interaction.user.name.lower()}"
        
        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category if isinstance(category, discord.CategoryChannel) else None,
                overwrites=overwrites,
                reason=f"Ticket ouvert par {interaction.user}"
            )
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Impossible de créer le ticket (vérifie mes permissions).", ephemeral=True)
        except discord.HTTPException as e:
            logger.warning("TicketButton: erreur HTTP lors de la création du salon: %s", e)
            return await interaction.response.send_message("❌ Erreur Discord lors de la création du ticket.", ephemeral=True)

        # Enregistrer le ticket
        active_tickets[user_id_str] = ticket_channel.id
        state["active_tickets"] = active_tickets
        save_state(state)

        # Envoyer le premier message dans le ticket
        embed = discord.Embed(
            title=f"{self.t_type['emoji']} {self.t_type['label']}",
            description=f"Bonjour {interaction.user.mention},\n\nLe staff va s'occuper de ta demande le plus rapidement possible.\nExplique en détail ton besoin ici.",
            color=discord.Color.gold()
        )
        
        # Le bouton de fermeture
        await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=CloseTicketButton())

        await interaction.response.send_message(
            f"✅ Ton ticket a été créé : {ticket_channel.mention}",
            ephemeral=True
        )

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        for t_type in TICKET_TYPES:
            self.add_item(TicketButton(t_type))


class TicketPanelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._views_registered = False

    def build_embed(self) -> discord.Embed:
        return discord.Embed(
            title="🎟️ Support & Tickets",
            description=(
                "Besoin d'aide ou de contacter le staff ?\n\n"
                "**Choisis la raison de ton ticket :**\n\n"
                "🛠️ **Problème technique / Bug / Bot**\n"
                "🚨 **Signalement d'un utilisateur**\n"
                "🎭 **Demande ou problème de rôle**\n"
                "💡 **Suggestion / idée**\n"
                "❓ **Autre sujet**\n\n"
                "*Un seul ticket à la fois par utilisateur.*"
            ),
            color=discord.Color.dark_theme()
        )

    async def ensure_panel_message(self):
        channel = self.bot.get_channel(TICKET_PANEL_CHANNEL_ID)
        if channel is None:
            return

        state = load_state()
        message_id = state.get("panel_message_id")

        view = TicketPanelView()
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
            logger.warning("TicketPanelCog: erreur lors de l'upsert du panel: %s", e)

    @commands.Cog.listener()
    async def on_ready(self):
        first_ready = not self._views_registered
        if first_ready:
            self.bot.add_view(TicketPanelView())
            self.bot.add_view(CloseTicketButton()) # Important pour que les boutons des tickets actuels restent fonctionnels
            self._views_registered = True
            self.bot._startup_queue.put_nowait(self.ensure_panel_message)
        else:
            await self.ensure_panel_message()

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketPanelCog(bot))
