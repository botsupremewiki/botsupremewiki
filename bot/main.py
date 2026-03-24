import logging
import os
import sys
import asyncio
import warnings
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot.cogs.casino.core import CasinoWelcomeView

# Suppression des avertissements de dépréciation sur Windows
if sys.platform == 'win32':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
discord.utils.setup_logging()
logger = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    """
    Charge les cogs depuis bot/cogs/.
    - Sous-dossier avec __init__.py → chargé comme package (bot.cogs.X)
    - Sous-dossier sans __init__.py → chaque .py chargé individuellement
    - Fichier .py direct → chargé directement
    """
    base = "./bot/cogs"

    for entry in os.listdir(base):
        full_path = os.path.join(base, entry)

        # Sous-dossier avec __init__.py → charger comme package
        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
            ext = f"bot.cogs.{entry}"
            try:
                await bot.load_extension(ext)
            except commands.NoEntryPointError:
                # __init__.py sans setup() → charger les fichiers individuellement
                for filename in os.listdir(full_path):
                    if filename.endswith(".py") and not filename.startswith("_"):
                        sub_ext = f"bot.cogs.{entry}.{filename[:-3]}"
                        try:
                            await bot.load_extension(sub_ext)
                        except commands.NoEntryPointError:
                            continue
                        except Exception as e:
                            logger.error("Erreur chargement %s: %s", sub_ext, e)
            except Exception as e:
                logger.error("Erreur chargement %s: %s", ext, e)

        # Sous-dossier sans __init__.py → charger chaque .py individuellement
        elif os.path.isdir(full_path):
            for filename in os.listdir(full_path):
                if filename.endswith(".py") and not filename.startswith("_"):
                    ext = f"bot.cogs.{entry}.{filename[:-3]}"
                    try:
                        await bot.load_extension(ext)
                    except commands.NoEntryPointError:
                        continue
                    except Exception as e:
                        logger.error("Erreur chargement %s: %s", ext, e)

        # Fichier .py direct
        elif entry.endswith(".py") and not entry.startswith("_"):
            ext = f"bot.cogs.{entry[:-3]}"
            try:
                await bot.load_extension(ext)
            except commands.NoEntryPointError:
                continue
            except Exception as e:
                logger.error("Erreur chargement %s: %s", ext, e)

@bot.event
async def on_ready():
    logger.info("Connecté en tant que %s", bot.user)
    try:
        synced = await bot.tree.sync()
        logger.info("%d commandes slash synchronisées", len(synced))
    except Exception as e:
        logger.error("Erreur sync: %s", e)

async def setup_hook():
    """Appelé avant le démarrage de la session du bot."""
    bot.add_view(CasinoWelcomeView(bot))
    await load_cogs()

bot.setup_hook = setup_hook

if __name__ == "__main__":
    bot.run(TOKEN)