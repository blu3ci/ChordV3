import discord
from discord.ext import commands

import config
import ui
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

    @discord.slash_command(description=config.CommandDescription.STOP)
    @utils.perform_pre_checks
    async def stop(self, ctx: discord.ApplicationContext):
        if not ctx.voice_client.is_playing():
            raise utils.BotNotPlayingError

        ctx.voice_client.stop()

        embed = ui.ChordEmbed(config.Message.STOPPED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.RESUME)
    @utils.perform_pre_checks
    async def resume(self, ctx: discord.ApplicationContext):
        if not ctx.voice_client.is_paused():
            raise utils.BotIsPlayingError

        ctx.voice_client.resume()

        embed = ui.ChordEmbed(config.Message.RESUMED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.PAUSE)
    @utils.perform_pre_checks
    async def pause(self, ctx: discord.ApplicationContext):
        if ctx.voice_client.is_paused():
            raise utils.BotNotPlayingError

        ctx.voice_client.pause()

        embed = ui.ChordEmbed(config.Message.PAUSED)

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))
