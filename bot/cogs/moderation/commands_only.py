import discord
from discord.ext import commands

COMMANDS_ONLY_CHANNELS = [
    1444786092552491198,
    1468287521656934601,
    1468251391775473795,
    1468267312493756607,
    1475325945001807952,
    1475332850294329577,
    1475338861197529118,
    1468963221481328827
]

class CommandsOnly(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
            
        if message.channel.id in COMMANDS_ONLY_CHANNELS:
            # Delete any regular text message sent by a user in these channels
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.NotFound:
                pass
                
            # Send an auto-deleting warning message to the user
            try:
                warning_msg = await message.channel.send(
                    f"{message.author.mention} ❌ **Tu n'as pas le droit d'écrire ici !** Ce salon est strictement réservé à l'utilisation des commandes (`/`).",
                    delete_after=5.0
                )
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsOnly(bot))
