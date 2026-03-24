import discord
from discord import app_commands
from discord.ext import commands
import os
import logging

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Recharge tous les cogs")
    async def reload(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ Admin uniquement.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        reloaded = []
        failed = []

        cogs_path = "./bot/cogs"
        for entry in os.listdir(cogs_path):
            full_path = os.path.join(cogs_path, entry)
            # Fichier .py direct
            if os.path.isfile(full_path) and entry.endswith(".py") and entry != "__init__.py":
                extension = f"bot.cogs.{entry[:-3]}"
            # Sous-dossier avec __init__.py (cog package)
            elif os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
                extension = f"bot.cogs.{entry}"
            else:
                continue
            try:
                await self.bot.reload_extension(extension)
                reloaded.append(entry)
            except Exception as e:
                failed.append(f"{entry} ({e})")

        # Resync instant sur le serveur
        try:
            await self.bot.tree.sync(guild=interaction.guild)
        except Exception as e:
            logger.warning("tree.sync a échoué lors du reload: %s", e)

        message = f"♻️ Reload terminé.\n\n"
        if reloaded:
            message += f"✅ Reloaded: {', '.join(reloaded)}\n"
        if failed:
            message += f"❌ Failed: {', '.join(failed)}"

        await interaction.followup.send(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))