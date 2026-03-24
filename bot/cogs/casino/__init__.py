from .core import Casino
from .roulette import RouletteCog
from .blackjack import BlackjackCog
from .poker import PokerCog

async def setup(bot):
    await bot.add_cog(Casino(bot))
    await bot.add_cog(RouletteCog(bot))
    await bot.add_cog(BlackjackCog(bot))
    await bot.add_cog(PokerCog(bot))
