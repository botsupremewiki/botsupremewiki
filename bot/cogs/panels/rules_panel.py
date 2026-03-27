import discord
from discord.ext import commands
import json
import logging
import os

logger = logging.getLogger(__name__)

RULES_CHANNEL_ID = 1474493045901754398
STATE_FILE = "bot/data/rules_state.json"

# Rôles à ajouter quand la personne accepte le règlement
ROLES_ON_ACCEPT = [
    1474444018988613776,  # Bots
    1474444062948982854,  # Classement
    1474562360026075409,  # Général
    1474444144792568024,  # LOL
    1474444191361929286,  # TFT
    1474444214237532220,  # Arc Raiders
    1474562674900730027,  # AFK
    1474444276136939663,  # RPG
    1474444312518328401,  # Autre
    1474556096105677011,  # Règles
    1475346687085252648,  # Mini-jeux
    1480238800931393668,  # Casino
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
        logger.warning("rules_panel: state file corrupted, resetting.")
        return {}

def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)

def build_rules_embed() -> discord.Embed:
    embed = discord.Embed(
        title="📜 Règlement du serveur",
        description=(
            "Lis attentivement les règles.\n"
            "En cliquant sur **✅ J’accepte**, tu confirmes les respecter.\n\n"
            "────────────────────"
        ),
    )
    embed.add_field(name="1️⃣ Serveur", value="Aucune critique sur le serveur en lui même ne sera toléré.", inline=False)
    embed.add_field(name="2️⃣ Respect", value="Que du harcèlement, de la discrimination ou de la toxicité.", inline=False)
    embed.add_field(name="3️⃣ Contenu", value="Si possible du contenu NSFW, choquant ou illégal.", inline=False)
    embed.add_field(name="4️⃣ Spam / Pub", value="Pas de spam, flood, ni pub non autorisée sauf si tu donnes argent.", inline=False)
    embed.set_footer(text="Le staff peut sanctionner si nécessaire.")
    return embed


class RulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="J’accepte le règlement",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="rules:accept",
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Utilisable uniquement sur un serveur.", ephemeral=True)

        # ✅ IMPORTANT: on répond instant pour éviter "Échec de l'interaction"
        await interaction.response.defer(ephemeral=True)

        me = interaction.guild.me
        if not me or not me.guild_permissions.manage_roles:
            return await interaction.followup.send(
                "❌ Je n’ai pas la permission **Gérer les rôles**.",
                ephemeral=True
            )

        member = interaction.user
        member_role_ids = {r.id for r in member.roles}

        roles_to_add = []
        missing_roles = []

        for rid in ROLES_ON_ACCEPT:
            role = interaction.guild.get_role(rid)
            if not role:
                missing_roles.append(rid)
                continue
            if rid not in member_role_ids:
                roles_to_add.append(role)

        if not roles_to_add:
            msg = "✅ Tu as déjà tout ce qu’il faut."
            if missing_roles:
                msg += f"\n⚠️ Rôles introuvables: {', '.join(map(str, missing_roles))}"
            return await interaction.followup.send(msg, ephemeral=True)

        try:
            await member.add_roles(*roles_to_add, reason="Accepted rules")
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ Je ne peux pas ajouter ces rôles (hiérarchie). "
                "Mets le rôle du bot **au-dessus** des rôles à donner.",
                ephemeral=True
            )

        added_names = ", ".join(r.name for r in roles_to_add)
        msg = f"✅ Règlement accepté. Rôles ajoutés : **{added_names}**"
        if missing_roles:
            msg += f"\n⚠️ Rôles introuvables: {', '.join(map(str, missing_roles))}"

        await interaction.followup.send(msg, ephemeral=True)


class RulesPanelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._views_registered = False

    async def ensure_rules_message(self):
        channel = self.bot.get_channel(RULES_CHANNEL_ID)
        if channel is None:
            return

        state = load_state()
        message_id = state.get("rules_message_id")

        embed = build_rules_embed()
        view = RulesView()

        msg = None
        if message_id:
            try:
                msg = await channel.fetch_message(int(message_id))
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                msg = None

        try:
            if msg:
                # Reset la view/bouton à chaque démarrage
                await msg.edit(embed=embed, view=view)
            else:
                new_msg = await channel.send(embed=embed, view=view)
                state["rules_message_id"] = new_msg.id
                save_state(state)
        except discord.HTTPException as e:
            logger.warning("RulesPanelCog: erreur lors de l'upsert du panel: %s", e)

    @commands.Cog.listener()
    async def on_ready(self):
        # View persistante: bouton utilisable après redémarrage
        first_ready = not self._views_registered
        if first_ready:
            self.bot.add_view(RulesView())
            self._views_registered = True
            self.bot._startup_queue.put_nowait(self.ensure_rules_message)
        else:
            await self.ensure_rules_message()


async def setup(bot: commands.Bot):
    await bot.add_cog(RulesPanelCog(bot))