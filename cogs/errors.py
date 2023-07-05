import discord
from discord.ext import commands

from logger import setup_logger

log = setup_logger(__name__)


class Errors(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(
        self, context: discord.ApplicationContext, exception: discord.DiscordException
    ):
        log.error(exception)
        if isinstance(exception, discord.ApplicationCommandInvokeError):
            if not context.author.voice:
                await context.respond("join a voice channel dummy")

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Errors(bot))
