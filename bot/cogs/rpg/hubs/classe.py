"""
Hub Classe — sélection/changement de classe.
Canal : 1465541336361996504
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    ALL_CLASSES, CLASSES_STANDARD, CLASSES_PREMIUM,
    CLASS_EMOJI, CLASS_DESCRIPTION, BASE_STATS,
    ROLE_PREMIUM, ROLE_RPG, LEVEL_GROWTH,
)

# ─── Emojis de stats ───────────────────────────────────────────────────────

STAT_EMOJI = {
    "hp":          "❤️",
    "p_atk":       "⚔️",
    "m_atk":       "🔮",
    "p_def":       "🛡️",
    "m_def":       "✨",
    "p_pen":       "🩸",
    "m_pen":       "💥",
    "speed":       "⚡",
    "crit_chance": "🎯",
    "crit_damage": "💢",
}

STAT_LABEL = {
    "hp":          "Points de Vie",
    "p_atk":       "Attaque Physique",
    "m_atk":       "Attaque Magique",
    "p_def":       "Défense Physique",
    "m_def":       "Défense Magique",
    "p_pen":       "Pénétration Physique",
    "m_pen":       "Pénétration Magique",
    "speed":       "Vitesse",
    "crit_chance": "Chance Critique",
    "crit_damage": "Dégâts Critiques",
}

# Stats affichées dans l'ordre
STAT_ORDER = ["hp", "p_atk", "m_atk", "p_pen", "m_pen", "p_def", "m_def", "speed", "crit_chance", "crit_damage"]


def _build_class_info_embed(class_name: str) -> discord.Embed:
    """Construit l'embed de détail d'une classe (passif + stats de base + croissance)."""
    emoji = CLASS_EMOJI.get(class_name, "⚔️")
    description = CLASS_DESCRIPTION.get(class_name, "")
    lines = description.split("\n", 1)
    flavor  = lines[0] if len(lines) > 0 else ""
    passive = lines[1] if len(lines) > 1 else ""

    is_premium = class_name in CLASSES_PREMIUM
    color = 0xFFD700 if is_premium else 0x5865F2

    embed = discord.Embed(
        title=f"{emoji} {class_name}" + (" ⭐" if is_premium else ""),
        description=f"*{flavor}*\n\n{passive}",
        color=color,
    )

    # Stats niveau 1
    base = BASE_STATS.get(class_name, {})
    stats_lines = []
    for stat in STAT_ORDER:
        val = base.get(stat, 0)
        se  = STAT_EMOJI[stat]
        sl  = STAT_LABEL[stat]
        if isinstance(val, float):
            stats_lines.append(f"{se} **{sl}** : {val:.2f}")
        else:
            stats_lines.append(f"{se} **{sl}** : {val:,}")

    embed.add_field(
        name="📊 Stats niveau 1",
        value="\n".join(stats_lines),
        inline=True,
    )

    # Croissance par niveau
    growth_lines = []
    for stat in STAT_ORDER:
        val = LEVEL_GROWTH.get(stat, 0)
        se  = STAT_EMOJI[stat]
        sl  = STAT_LABEL[stat]
        if isinstance(val, float) and val != int(val):
            growth_lines.append(f"{se} **{sl}** : +{val}")
        else:
            growth_lines.append(f"{se} **{sl}** : +{int(val)}")

    embed.add_field(
        name="📈 Croissance / niveau",
        value="\n".join(growth_lines),
        inline=True,
    )

    if is_premium:
        embed.set_footer(text="Classe Premium — réservée aux membres Premium.")
    else:
        embed.set_footer(text="Classe Standard — accessible à tous.")

    return embed


# ─── Bouton de confirmation (vue éphémère, non persistante) ────────────────

class ConfirmClassView(discord.ui.View):
    def __init__(self, class_name: str):
        super().__init__(timeout=60)
        self.class_name = class_name

    @property
    def _confirm_button(self):
        # Dynamically accessed; the button is added via decorator below
        return None

    async def _do_confirm(self, interaction: discord.Interaction):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)

        # Bloquer si classe déjà choisie
        if player.get("class"):
            embed = discord.Embed(
                title="❌ Classe déjà choisie",
                description=(
                    f"Tu possèdes déjà la classe {CLASS_EMOJI.get(player['class'], '')} **{player['class']}**.\n"
                    "Il n'est pas possible de changer de classe."
                ),
                color=0xFF4444,
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        # Vérification premium (double-check côté serveur)
        if self.class_name in CLASSES_PREMIUM and interaction.guild:
            role_premium = interaction.guild.get_role(ROLE_PREMIUM)
            has_premium = role_premium in interaction.user.roles if role_premium else False
            if not has_premium:
                embed = discord.Embed(
                    title="⭐ Classe Premium",
                    description=f"La classe **{self.class_name}** est réservée aux membres **Premium**.",
                    color=0xFFD700,
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

        # Affecter la classe
        await db.update_player(interaction.user.id, **{"class": self.class_name})

        # Mettre à jour les HP
        from bot.cogs.rpg.models import compute_class_stats, compute_max_hp
        cs     = compute_class_stats(self.class_name, player["level"], player.get("prestige_level", 0))
        max_hp = compute_max_hp(cs)
        await db.update_player(interaction.user.id, current_hp=max_hp)

        # Donner le rôle RPG si absent
        if interaction.guild:
            role_rpg = interaction.guild.get_role(ROLE_RPG)
            if role_rpg and role_rpg not in interaction.user.roles:
                try:
                    await interaction.user.add_roles(role_rpg)
                except Exception:
                    pass

        emoji = CLASS_EMOJI.get(self.class_name, "⚔️")
        embed = discord.Embed(
            title=f"✅ Classe choisie : {emoji} {self.class_name} !",
            description=(
                f"Ta classe a bien été définie à **{self.class_name}**.\n"
                "Bonne chance dans ton aventure !"
            ),
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=embed, view=None)


# On crée le bouton confirm dynamiquement pour avoir un label dynamique
class _ConfirmButton(discord.ui.Button):
    def __init__(self, class_name: str):
        emoji = CLASS_EMOJI.get(class_name, "⚔️")
        super().__init__(
            label=f"Choisir {class_name}",
            style=discord.ButtonStyle.success,
            emoji=emoji,
        )
        self.class_name = class_name

    async def callback(self, interaction: discord.Interaction):
        assert isinstance(self.view, ConfirmClassView)
        await self.view._do_confirm(interaction)


def build_confirm_view(class_name: str) -> ConfirmClassView:
    view = ConfirmClassView(class_name)
    view.add_item(_ConfirmButton(class_name))
    return view


# ─── Bouton d'info de classe (persistant) ─────────────────────────────────

class ClassInfoButton(discord.ui.Button):
    def __init__(self, class_name: str, row: int):
        emoji      = CLASS_EMOJI.get(class_name, "⚔️")
        is_premium = class_name in CLASSES_PREMIUM
        label      = f"⭐ {class_name}" if is_premium else class_name
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary if is_premium else discord.ButtonStyle.primary,
            emoji=None,
            row=row,
            custom_id=f"rpg:classe:info:{class_name.replace(' ', '_')}",
        )
        self.class_name = class_name

    async def callback(self, interaction: discord.Interaction):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)

        # Vérifier accès premium
        if self.class_name in CLASSES_PREMIUM and interaction.guild:
            role_premium = interaction.guild.get_role(ROLE_PREMIUM)
            has_premium  = role_premium in interaction.user.roles if role_premium else False
            if not has_premium:
                embed = discord.Embed(
                    title="⭐ Classe Premium",
                    description=(
                        f"La classe **{self.class_name}** est réservée aux membres **Premium**.\n"
                        "Rejoins le rang Premium pour y accéder !"
                    ),
                    color=0xFFD700,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        # Joueur a déjà une classe → bloqué définitivement
        if player.get("class"):
            current_emoji = CLASS_EMOJI.get(player["class"], "")
            embed = discord.Embed(
                title="🔒 Classe déjà choisie",
                description=(
                    f"Tu possèdes déjà la classe {current_emoji} **{player['class']}**.\n\n"
                    "Il n'est pas possible de changer de classe."
                ),
                color=0xFF4444,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Afficher l'embed de détail + bouton de confirmation
        embed = _build_class_info_embed(self.class_name)
        view  = build_confirm_view(self.class_name)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ─── Vue persistante du hub ────────────────────────────────────────────────

class ClasseHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        for cls in CLASSES_STANDARD:
            self.add_item(ClassInfoButton(cls, row=0))
        for cls in CLASSES_PREMIUM:
            self.add_item(ClassInfoButton(cls, row=1))


# ─── Build du hub ──────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    standard_lines = "\n".join(
        f"{CLASS_EMOJI[c]} **{c}** — {CLASS_DESCRIPTION[c].split(chr(10))[0]}"
        for c in CLASSES_STANDARD
    )
    premium_lines = "\n".join(
        f"{CLASS_EMOJI[c]} **{c}** ⭐ — {CLASS_DESCRIPTION[c].split(chr(10))[0]}"
        for c in CLASSES_PREMIUM
    )

    embed = discord.Embed(
        title="⚔️ Choix de Classe",
        description=(
            "Choisis ta **classe** pour commencer l'aventure.\n"
            "Chaque classe possède un **passif unique** qui définit ton style de jeu.\n"
            "Tu peux changer de classe à chaque **Prestige**.\n\n"
            "**Classes Standard**\n"
            f"{standard_lines}\n\n"
            "**Classes Premium** ⭐\n"
            f"{premium_lines}"
        ),
        color=0x5865F2,
    )
    embed.set_footer(text="Clique sur le nom d'une classe pour voir ses détails et la choisir.")

    view = ClasseHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
