import datetime

import discord
from discord import Option
from discord.ext import commands

import config
import music
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
        song: Option(
            str,
            config.CommandArgDescription.PLAY_SONG,
        ),
    ):
        await ctx.defer()

        if not ctx.voice_client:
            await self.bot.get_cog("General").connect(ctx, None)

        voice_client: music.Player = ctx.voice_client

        song: music.Song = await voice_client.downloader.get_song(ctx, song)

        voice_client.playlist.add_song(song)

        await voice_client.play()

    @discord.slash_command(description=config.CommandDescription.STOP)
    @utils.perform_pre_checks
    async def stop(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        voice_client.playlist.clear()
        voice_client.stop()

        embed = ui.ChordEmbed(config.Message.STOPPED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.SKIP)
    @utils.perform_pre_checks
    async def skip(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        voice_client.stop()

        embed = ui.ChordEmbed(config.Message.SKIPPED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.PREV)
    @utils.perform_pre_checks
    async def prev(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        prev_song = voice_client.playlist.prev_song()

        if isinstance(prev_song, music.Song):
            voice_client.stop()
            embed = ui.ChordEmbed(config.Message.PREV_SONG)
        else:
            embed = ui.ChordEmbed(config.Message.NO_PREV_SONG)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.RESUME)
    @utils.perform_pre_checks
    async def resume(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client.is_paused():
            raise utils.BotIsPlayingError

        voice_client.resume()

        embed = ui.ChordEmbed(config.Message.RESUMED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.PAUSE)
    @utils.perform_pre_checks
    async def pause(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if voice_client.is_paused():
            raise utils.BotNotPlayingError

        voice_client.pause()

        embed = ui.ChordEmbed(config.Message.PAUSED)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.VOLUME)
    @utils.perform_pre_checks
    async def volume(
        self,
        ctx: discord.ApplicationContext,
        value: Option(
            int,
            config.CommandArgDescription.VOLUME_VALUE,
            required=False,
            default=None,
            min_value=0,
            max_value=config.MAX_VOLUME,
        ),
    ):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if type(value) is int:
            voice_client.volume = value

        embed = ui.ChordEmbed(f"{config.Message.VOLUME} ``{ctx.voice_client.volume}%``")

        await ctx.respond(embed=embed)

    @discord.slash_command(name="247", description=config.CommandDescription.NO_DISCONNECT_MODE)
    @utils.perform_pre_checks
    async def no_disconnect_mode(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if voice_client.auto_disconnect:
            voice_client.auto_disconnect = False
            embed = ui.ChordEmbed(config.Message.NO_DISCONNECT_MODE_ON)

        else:
            voice_client.auto_disconnect = True
            embed = ui.ChordEmbed(config.Message.NO_DISCONNECT_MODE_OFF)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.SEEK)
    @utils.perform_pre_checks
    async def seek(
        self, ctx: discord.ApplicationContext, timestamp: Option(str, description=config.CommandArgDescription.SEEK)
    ):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        try:
            parser = datetime.datetime.strptime(timestamp, "%H:%M:%S")
            seconds = datetime.timedelta(
                hours=parser.hour, minutes=parser.minute, seconds=parser.second
            ).total_seconds()
        except ValueError:
            raise utils.FailedToParseTimeFormatError

        await voice_client.seek(int(seconds))

        embed = ui.ChordEmbed(f"{config.Message.SEEKED} {timestamp}")

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.LOOP_SONG)
    @utils.perform_pre_checks
    async def loop(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        voice_client.playlist.toggle_loop()

        if voice_client.playlist.loop:
            embed = ui.ChordEmbed(config.Message.SONG_LOOP_ON)
        else:
            embed = ui.ChordEmbed(config.Message.SONG_LOOP_OFF)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.LOOP_PLAYLIST)
    @utils.perform_pre_checks
    async def loop_all(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        voice_client.playlist.toggle_loop_all()

        if voice_client.playlist.loop_all:
            embed = ui.ChordEmbed(config.Message.PLAYLIST_LOOP_ON)
        else:
            embed = ui.ChordEmbed(config.Message.PLAYLIST_LOOP_OFF)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.NOW_PLAYING)
    @utils.perform_pre_checks
    async def np(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        embed = ui.NowPlayingEmbed(voice_client.playlist.current)

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.PLAYLIST)
    @utils.perform_pre_checks
    async def playlist(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        await ui.PlaylistPaginatorView(ctx).send()

    @discord.slash_command(description=config.CommandDescription.SHUFFLE)
    @utils.perform_pre_checks
    async def shuffle(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        voice_client.playlist.shuffle()

        embed = ui.ChordEmbed(config.Message.SHUFFLED_PLAYLIST)

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))
