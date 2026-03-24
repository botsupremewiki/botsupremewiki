"""
RPG Cog — enregistrement de toutes les vues persistantes et du RPGCore.
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import HUB_CHANNELS

# Import de tous les hubs
from bot.cogs.rpg.hubs import bienvenue, classe, profil, metiers, banque, monde
from bot.cogs.rpg.hubs import donjons, raids, world_boss, hotel_ventes, echanges
from bot.cogs.rpg.hubs import titres, pvp, classement, admin

# Import des vues persistantes à re-enregistrer au démarrage
from bot.cogs.rpg.hubs.classe import ClasseHubView
from bot.cogs.rpg.hubs.profil import ProfilHubView
from bot.cogs.rpg.hubs.metiers import MetiersHubView
from bot.cogs.rpg.hubs.banque import BanqueHubView
from bot.cogs.rpg.hubs.monde import MondeHubView
from bot.cogs.rpg.hubs.donjons import DonjonsHubView
from bot.cogs.rpg.hubs.raids import RaidsHubView
from bot.cogs.rpg.hubs.world_boss import WorldBossHubView
from bot.cogs.rpg.hubs.hotel_ventes import HotelVentesHubView
from bot.cogs.rpg.hubs.echanges import EchangesHubView
from bot.cogs.rpg.hubs.titres import TitresHubView
from bot.cogs.rpg.hubs.pvp import TaverneHubView
from bot.cogs.rpg.hubs.classement import ClassementHubView
from bot.cogs.rpg.hubs.admin import AdminHubView


async def setup(bot: commands.Bot):
    """Appelé par bot.load_extension('bot.cogs.rpg')."""
    # Initialiser la DB
    await db.init_db()

    # Enregistrer toutes les vues persistantes (pour survivre aux redémarrages)
    bot.add_view(ClasseHubView(bot))
    bot.add_view(ProfilHubView(bot))
    bot.add_view(MetiersHubView(bot))
    bot.add_view(BanqueHubView(bot))
    bot.add_view(MondeHubView(bot))
    bot.add_view(DonjonsHubView(bot))
    bot.add_view(RaidsHubView(bot))
    bot.add_view(WorldBossHubView(bot))
    bot.add_view(HotelVentesHubView(bot))
    bot.add_view(EchangesHubView(bot))
    bot.add_view(TitresHubView(bot))
    bot.add_view(TaverneHubView(bot))
    bot.add_view(ClassementHubView(bot))
    bot.add_view(AdminHubView(bot))

    # Charger le Cog RPGCore (tâches de fond)
    from bot.cogs.rpg.core import RPGCore
    await bot.add_cog(RPGCore(bot))
