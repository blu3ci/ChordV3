import discord
from discord.ext import commands

import config
import utils
from logger import setup_logger
from ui import ChordEmbed

log = setup_logger(__name__)


class Errors(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(
        self, context: discord.ApplicationContext, exception: discord.DiscordException
    ):
        if isinstance(exception.original, utils.NotConnectedToVCError):
            embed = ChordEmbed(config.Message.AUTHOR_NOT_IN_VC)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.AuthorNotInBotVCError):
            embed = ChordEmbed(config.Message.AUTHOR_HAS_TO_BE_IN_SAME_VC_AS_BOT)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.BotNotInVCError):
            embed = ChordEmbed(config.Message.BOT_NOT_IN_VC)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.BotAlreadyInVCError):
            embed = ChordEmbed(config.Message.BOT_ALREADY_CONNECTED)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.BotNotInVCError):
            embed = ChordEmbed(config.Message.BOT_NOT_IN_VC)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.BotIsPlayingError):
            embed = ChordEmbed(config.Message.BOT_IS_PLAYING)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.BotNotPlayingError):
            embed = ChordEmbed(config.Message.BOT_IS_NOT_PLAYING)
            await context.respond(embed=embed)
        elif isinstance(exception.original, utils.FailedToDownloadSongError):
            embed = ChordEmbed(f"{config.Message.COULD_NOT_FIND_SONG}``{exception.original.query}``")
            await context.respond(embed=embed)
        else:
            log.error(exception)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Errors(bot))
