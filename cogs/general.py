import discord
from discord.ext import commands

from logger import setup_logger

log = setup_logger(__name__)


class General(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(General(bot))
