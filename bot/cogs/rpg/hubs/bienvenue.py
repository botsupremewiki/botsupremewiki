"""
Hub Bienvenue — message d'accueil expliquant tous les hubs.
Canal : 1480619312715792535
"""
from __future__ import annotations
import discord
from discord.ext import commands
from bot.cogs.rpg.models import HUB_CHANNELS


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="⚔️ Bienvenue dans le RPG !",
        description=(
            "Bienvenue dans l'aventure ! Ce serveur abrite un **RPG complet** "
            "entièrement jouable via des boutons et des menus.\n\n"
            "Voici un guide des différents hubs disponibles :"
        ),
        color=0x5865F2,
    )

    embed.add_field(
        name="🏫 Hubs Principaux",
        value=(
            f"<#{HUB_CHANNELS['classe']}> — Choisissez ou changez de classe\n"
            f"<#{HUB_CHANNELS['profil']}> — Profil, inventaire, forgeron, prestige & récompenses\n"
            f"<#{HUB_CHANNELS['metiers']}> — Métiers de récolte, craft et conception\n"
            f"<#{HUB_CHANNELS['banque']}> — Banque sécurisée (résiste aux prestiges)\n"
        ),
        inline=False,
    )

    embed.add_field(
        name="⚔️ Hubs de Combat",
        value=(
            f"<#{HUB_CHANNELS['monde']}> — Combat par zones (1-10,000)\n"
            f"<#{HUB_CHANNELS['donjons']}> — Donjons Classiques, Élite & Abyssaux\n"
            f"<#{HUB_CHANNELS['raids']}> — Raids multi-joueurs (5 joueurs max)\n"
            f"<#{HUB_CHANNELS['world_boss']}> — World Boss hebdomadaire\n"
            f"<#{HUB_CHANNELS['pvp']}> — Combats JcJ classés\n"
        ),
        inline=False,
    )

    embed.add_field(
        name="💰 Hubs Économiques",
        value=(
            f"<#{HUB_CHANNELS['hotel_ventes']}> — Hôtel des Ventes entre joueurs\n"
            f"<#{HUB_CHANNELS['echanges']}> — Échanges sécurisés entre joueurs\n"
        ),
        inline=False,
    )

    embed.add_field(
        name="🏆 Hubs Sociaux",
        value=(
            f"<#{HUB_CHANNELS['quetes']}> — Quêtes principales & secondaires\n"
            f"<#{HUB_CHANNELS['titres']}> — Exploits & titres débloquables\n"
            f"<#{HUB_CHANNELS['classement']}> — Classements (Général, World Boss, PvP)\n"
        ),
        inline=False,
    )

    embed.add_field(
        name="📖 Comment jouer ?",
        value=(
            "1. Va dans <#{ch_classe}> pour choisir ta **classe**\n"
            "2. Commence à combattre dans <#{ch_monde}> pour gagner de l'**XP**, de l'**or** et des **équipements**\n"
            "3. Gère tes items depuis <#{ch_profil}>\n"
            "4. Apprends un **métier** pour crafter des consommables et des équipements\n"
            "5. Affronte des boss de plus en plus puissants !\n\n"
            "💡 **Conseil débutant** : Suis les **quêtes** — elles te guident pas à pas et offrent les meilleures récompenses en début de partie !\n\n"
            "**Regen passive** : +3% HP & +3 énergie toutes les 10 minutes 💤\n"
            "**Prestige** : Atteins le niveau 1000 et recommence plus fort !\n"
        ).replace("{ch_classe}", str(HUB_CHANNELS['classe'])).replace("{ch_monde}", str(HUB_CHANNELS['monde'])).replace("{ch_profil}", str(HUB_CHANNELS['profil'])),
        inline=False,
    )

    embed.set_footer(text="Bonne aventure, héros ! ⚔️")

    view = discord.ui.View()
    wiki_btn = discord.ui.Button(
        label="📖 Wiki",
        url="https://botsupremewiki.netlify.app",
        style=discord.ButtonStyle.link,
    )
    view.add_item(wiki_btn)
    return embed, view


async def setup(bot: commands.Bot):
    pass  # Pas de cog, géré par core.py
