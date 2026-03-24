import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

JOIN_CHANNELS = {
    1463053642234990708: {"prefix": "🎮 [Solo/Duo]", "limit": 2},
    1463053689681084541: {"prefix": "⚔️ [Flex]", "limit": 5},
    1463053483321196615: {"prefix": "🐧 [TFT]", "limit": 8}
}

class TempVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels = set()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # 1. Quelqu'un rejoint un salon vocal trigger
        if after.channel is not None and after.channel.id in JOIN_CHANNELS:
            config = JOIN_CHANNELS[after.channel.id]
            category = after.channel.category
            
            try:
                # Création du salon limité avec un nom stylé
                new_channel = await member.guild.create_voice_channel(
                    name=f'{config["prefix"]} {member.display_name}',
                    category=category,
                    user_limit=config["limit"],
                    reason="Bot Ultime: Création de salon vocal temporaire"
                )
                
                # On ajoute le salon à la liste des salons temporaires gérés par le bot
                self.temp_channels.add(new_channel.id)
                
                # On déplace l'utilisateur dedans
                await member.move_to(new_channel, reason="Déplacement dans le salon temporaire")
                
            except discord.Forbidden:
                logger.warning("TempVoice: permissions insuffisantes pour créer/déplacer dans le salon vocal.")
            except discord.HTTPException as e:
                logger.warning("TempVoice: erreur lors de la création du salon vocal: %s", e)
                
        # 2. Quelqu'un quitte un salon vocal (ou change de salon)
        if before.channel is not None:
            # Si le salon quitté fait partie de nos salons temporaires
            if before.channel.id in self.temp_channels:
                # S'il n'y a plus personne dedans
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete(reason="Bot Ultime: Suppression du salon vocal temporaire vide")
                        self.temp_channels.remove(before.channel.id)
                    except discord.NotFound:
                        # Le salon a peut-être déjà été supprimé manuellement par un admin
                        self.temp_channels.remove(before.channel.id)
                    except discord.Forbidden:
                        logger.warning("TempVoice: permissions insuffisantes pour supprimer le salon vocal.")
                    except discord.HTTPException as e:
                        logger.warning("TempVoice: erreur lors de la suppression du salon vocal temp: %s", e)

async def setup(bot: commands.Bot):
    await bot.add_cog(TempVoice(bot))
