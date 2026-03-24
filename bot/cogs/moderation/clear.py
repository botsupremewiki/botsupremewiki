import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Supprime des messages")
    @app_commands.describe(amount="Nombre de messages à supprimer (défaut: 20)")
    async def clear(self, interaction: discord.Interaction, amount: int = 20):

        # Vérifie permission
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(
                "❌ Tu n'as pas la permission de supprimer des messages.",
                ephemeral=True
            )

        # Limite de sécurité
        if amount < 1:
            return await interaction.response.send_message(
                "❌ Le nombre doit être supérieur à 0.",
                ephemeral=True
            )

        if amount > 100:
            return await interaction.response.send_message(
                "❌ Maximum 100 messages à la fois.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=amount)
        except discord.Forbidden:
            return await interaction.followup.send("❌ Je n'ai pas la permission de supprimer des messages ici.", ephemeral=True)
        except discord.HTTPException as e:
            return await interaction.followup.send(f"❌ Erreur Discord lors de la suppression : {e}", ephemeral=True)

        await interaction.followup.send(
            f"🧹 {len(deleted)} messages supprimés.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot))