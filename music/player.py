import asyncio
import datetime

import discord

import config
import ui
import utils
from logger import setup_logger

from .downloader import Downloader
from .playlist import Playlist
from .song import PartialSong, Song

log = setup_logger(__name__)


class Player(discord.VoiceClient):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel):
        super().__init__(client, channel)

        self.auto_disconnect = True
        self._volume: int = config.DEFAULT_VOLUME

        self._ffmpeg_options = config.FFMPEG_OPTIONS.copy()

        self.downloader = Downloader()
        self._playlist = Playlist()

        self._voice_channel_timeout_task: asyncio.Task | None = None

        self._player_start_time: datetime.datetime | None = None

    @property
    def player_position(self) -> int:
        if not self.is_playing():
            return 0

        args: list[str] = self.source.original._process.args
        seek_time = 0

        for index, arg in enumerate(args):
            if arg == "-ss":
                seek_time = int(args[index + 1])

        duration = (datetime.datetime.now() - self._player_start_time).total_seconds()

        return int(duration + seek_time)

    async def connect(self, *, reconnect: bool = True, timeout: float | None = None) -> None:
        await super().connect(reconnect=reconnect, timeout=timeout)

        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True)

        self._voice_channel_timeout_task = self.loop.create_task(self._voice_channel_timeout())

    async def disconnect(self, *, force: bool = True) -> None:
        await super().disconnect(force=force)
        self._playlist.reset()
        self._voice_channel_timeout_task.cancel()

    async def play(self, song: Song | PartialSong = None) -> None:
        if self.is_playing() or self.is_paused():
            song: Song | PartialSong = song or self._playlist.queue[-1]
            embed = ui.QueuedEmbed(song)
            await song.context.respond(embed=embed)
            return

        song: Song | PartialSong = self._playlist.next_song()

        if song is None:
            return

        song = await self.partial_song_to_song(song)
        
        if song is None:
            await self.play()

        source = discord.FFmpegPCMAudio(
            song.audio_source_url,
            executable=config.FFMPEG_EXEC_LOCATION,
            before_options=self._ffmpeg_options["before_options"],
            options=self._ffmpeg_options["options"],
        )

        super().play(source, after=lambda e: self._next_song_event())

        self._player_start_time = datetime.datetime.now()

        self._player.source = discord.PCMVolumeTransformer(self._player.source, (float(self._volume) / 100.0))

        embed = ui.NowPlayingEmbed(song)
        await song.context.channel.send(embed=embed)

    async def move_to(self, channel: discord.VoiceChannel) -> None:
        await super().move_to(channel=channel)

        await self.guild.change_voice_state(channel=channel, self_deaf=True)

    async def seek(self, position: int) -> None:
        self._player_start_time = datetime.datetime.now()
        await self._update_ffmpeg_options(before_options=f"-ss {position}")

    async def set_effect(self, effect: str) -> None:
        player_pos = self.player_position
        await self._update_ffmpeg_options(
            options=f'-af "{effect}"' if effect else "", overwrite=True,
        )
        await self._update_ffmpeg_options(before_options=f"-ss {player_pos}")

    async def _update_ffmpeg_options(
        self, before_options: str | None = None, options: str | None = None, overwrite: bool = False
    ) -> None:
        song: Song = self._playlist.current

        if not overwrite:
            ffmpeg_options = self._ffmpeg_options.copy()
        else:
            ffmpeg_options = self._ffmpeg_options
            ffmpeg_options.update(config.FFMPEG_OPTIONS)

        old_before_options = ffmpeg_options["before_options"]
        old_options = ffmpeg_options["options"]

        ffmpeg_options.update(
            {
                "before_options": old_before_options + (f" {before_options}" if before_options else ""),
                "options": old_options + (f" {options}" if options else ""),
            }
        )

        self.source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                song.audio_source_url,
                executable=config.FFMPEG_EXEC_LOCATION,
                before_options=ffmpeg_options["before_options"],
                options=ffmpeg_options["options"],
            ),
            (float(self._volume) / 100.0),
        )

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._volume = max(min(value, config.MAX_VOLUME), 0)
        self._player.source.volume = float(self._volume) / 100.0

    @property
    def playlist(self) -> Playlist:
        return self._playlist

    def _next_song_event(self) -> None:
        loop = self.client.loop

        loop.create_task(self.play())

    async def _voice_channel_timeout(self) -> None:
        t1 = datetime.datetime.now()
        while True:
            await asyncio.sleep(2)

            if not self.auto_disconnect:
                continue

            if len(self.channel.members) <= 1:
                if (datetime.datetime.now() - t1).total_seconds() >= config.PLAYER_DISCONNECT_TIMEOUT:
                    await self.disconnect()
                    break
            else:
                t1 = datetime.datetime.now()

    async def partial_song_to_song(self, partial_song: PartialSong | Song) -> Song | None:
        if hasattr(partial_song, "audio_source_url"):
            return partial_song

        try:
            song: Song = await self.downloader.get_song(
                partial_song.context, f"{partial_song.title} by {partial_song.uploader} lyrics"
            )
        except utils.FailedToDownloadSongError:
            return None

        song.title = partial_song.title
        song.original_url = partial_song.original_url
        song.uploader = partial_song.uploader
        song.thumbnail = partial_song.thumbnail

        self._playlist._current = song

        return song
