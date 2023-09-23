import datetime
import re

import discord
import httpx
from bs4 import BeautifulSoup
from discord import Option
from discord.ext import commands
from youtubesearchpython import VideosSearch

import config
import music
import ui
import utils
from logger import setup_logger

log = setup_logger(__name__)


class Music(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @staticmethod
    def get_video_results(ctx: discord.AutocompleteContext) -> list[str]:
        song = ctx.options.get("song")

        if not bool(song.strip()):
            voice_client: music.Player = None

            for voice_client in ctx.bot.voice_clients:
                if voice_client.channel in ctx.interaction.guild.channels:
                    voice_client = voice_client

            if voice_client:
                history = [song.title[:100] for song in voice_client.playlist.queue_history][:25]
                return history

            return []

        videos_search = VideosSearch(song, limit=10)
        results = videos_search.result()

        parsed_results = [
            discord.OptionChoice(name=result["title"], value=result["link"]) for result in results["result"]
        ]

        return parsed_results

    @staticmethod
    async def get_lyrics(search: str) -> str | None:
        genius_regex = re.compile(r"https://genius.com/[\w-]+")

        async with httpx.AsyncClient() as aclient:
            response = await aclient.get("https://www.google.com/search", params={"q": f"{search} site:genius.com"})

        genius_link = genius_regex.findall(response.text)

        if not genius_link:
            return None

        async with httpx.AsyncClient() as aclient:
            response = await aclient.get(genius_link[0])

        with open("stuff.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text.replace("<br/>", "\n"), "html.parser")

        verses = soup.find_all(class_="Lyrics__Container-sc-1ynbvzw-5")

        lyrics = ""

        for verse in verses:
            lyrics += verse.get_text()

        return lyrics if lyrics else None

    @staticmethod
    async def get_queue(ctx: discord.AutocompleteContext) -> list[str]:
        voice_client: music.Player = None

        for voice_client in ctx.bot.voice_clients:
            if voice_client.channel in ctx.interaction.guild.channels:
                voice_client = voice_client

        if voice_client is None:
            return []

        return [
            discord.OptionChoice(name=song.title, value=str(index + 1))
            for index, song in enumerate(voice_client.playlist.queue)
        ]

    @discord.slash_command(description=config.CommandDescription.PLAY)
    @utils.perform_pre_checks
    async def play(
        self,
        ctx: discord.ApplicationContext,
        song: Option(str, config.CommandArgDescription.PLAY_SONG, autocomplete=get_video_results,),
    ):
        await ctx.defer()

        if not ctx.voice_client:
            await self.bot.get_cog("General").connect(ctx, None)

        embed = ui.ChordEmbed(config.Message.SEARCH)

        await ctx.respond(embed=embed)

        voice_client: music.Player = ctx.voice_client

        song: music.Song | music.PartialSong | list[music.PartialSong] = await voice_client.downloader.get_song(
            ctx, song
        )

        voice_client.playlist.add_song(song)

        if isinstance(song, list):
            song = song[0]

        await voice_client.play(song=song)

    @discord.slash_command(description=config.CommandDescription.STOP)
    @utils.perform_pre_checks
    async def stop(self, ctx: discord.ApplicationContext):
        voice_client: music.Player = ctx.voice_client

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        voice_client.playlist.clear()
        voice_client.current_effect = None
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

    @discord.slash_command(description=config.CommandDescription.SKIPTO)
    @utils.perform_pre_checks
    async def skipto(
        self,
        ctx: discord.ApplicationContext,
        song: Option(
            str,
            config.CommandArgDescription.SKIPTO,
            autocomplete=discord.utils.basic_autocomplete(get_queue),
            required=True,
        ),
    ):
        voice_client: music.Player = ctx.voice_client

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        if song.isnumeric():
            song = int(song)

        if isinstance(song, str) or len(voice_client.playlist.queue) - 1 < song:
            raise utils.InvalidInputError(song)

        song -= 1
        song_title = voice_client.playlist.queue[song].title

        voice_client.playlist.skipto(song)
        voice_client.stop()

        embed = ui.ChordEmbed(f"{config.Message.SKIPPEDTO} ``{song_title}``")
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

        duration_index = 1
        duration_field = embed.fields[duration_index]
        duration_value = duration_field.value.replace("``", "")

        duration_field.value = f"``{ui.NowPlayingEmbed.parse_duration(voice_client.player_position)}/{duration_value}``"

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

    @discord.slash_command(description=config.CommandDescription.LYRICS)
    @utils.perform_pre_checks
    async def lyrics(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        song = voice_client.playlist.current

        lyrics = await self.get_lyrics(song.title)

        if lyrics is None:
            embed = ui.ChordEmbed(config.Message.COULD_NOT_FIND_LYRICS)
            await ctx.respond(embed=embed)
            return

        lyrics_embeds = []

        max_characters = 4096

        for i in range(int(len(lyrics) / max_characters) + 1):
            lyrics_section = lyrics[i * max_characters : (i + 1) * max_characters]

            if i == 0:
                embed = ui.BasicEmbed(title=song.title, description=lyrics_section)
                embed.set_thumbnail(url=song.thumbnail)
            else:
                embed = ui.BasicEmbed(description=lyrics_section)

            lyrics_embeds.append(embed)

        await ctx.respond(embeds=lyrics_embeds)

    @discord.slash_command(description=config.CommandDescription.EFFECT)
    @utils.perform_pre_checks
    async def effect(
        self,
        ctx: discord.ApplicationContext,
        effect: Option(
            str,
            config.CommandArgDescription.EFFECT,
            required=False,
            autocomplete=discord.utils.basic_autocomplete(
                [discord.OptionChoice(name=name, value=value) for name, value in config.EFFECTS.items()]
            ),
        ),
    ):
        voice_client: music.Player = ctx.voice_client

        if not voice_client:
            raise utils.BotNotInVCError

        if not voice_client.is_playing():
            raise utils.BotNotPlayingError

        if not effect:
            current_effect = (
                [i for i in config.EFFECTS if config.EFFECTS[i] == voice_client.current_effect][0]
                if voice_client.current_effect
                else None
            )

            embed = ui.ChordEmbed(f"{config.Message.CURRENT_EFFECT}{current_effect}")
            await ctx.respond(embed=embed)
            return

        if effect not in config.EFFECTS.values():
            raise utils.InvalidInputError(effect)

        await voice_client.set_effect(effect)

        current_effect = [i for i in config.EFFECTS if config.EFFECTS[i] == voice_client.current_effect][0]

        embed = ui.ChordEmbed(f"{config.Message.EFFECT}{current_effect}")

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))
