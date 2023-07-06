import discord
from discord.ext import commands

import config
import utils
from logger import setup_logger

log = setup_logger(__name__)


class Music(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @discord.slash_command(description=config.CommandDescription.PLAY)
    @utils.perform_pre_checks
    async def play(
        self,
        ctx: discord.ApplicationContext,
        song: discord.Option(
            str,
            config.CommandArgDescription.PLAY_SONG,
        ),
    ):
        if not ctx.voice_client:
            await self.bot.get_cog("General").connect(ctx, None)

        await ctx.voice_client.play(ctx, song)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))
