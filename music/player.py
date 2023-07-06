import asyncio

import discord

import config
import ui
from logger import setup_logger

from .downloader import Downloader
from .song import Song

log = setup_logger(__name__)


class Player(discord.VoiceClient):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel):
        super().__init__(client, channel)

        self._volume: int = config.DEFAULT_VOLUME

        self._ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self._downloader = Downloader()

        self._voice_channel_timeout_task: asyncio.Task = None

    async def connect(self, *, reconnect: bool = True, timeout: float | None = None):
        await super().connect(reconnect=reconnect, timeout=timeout)

        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True)

        self._voice_channel_timeout_task = self.loop.create_task(self._voice_channel_timeout())

    async def disconnect(self, *, force: bool = True) -> None:
        await super().disconnect(force=force)
        self._voice_channel_timeout_task.cancel()

    async def play(self, ctx: discord.ApplicationContext, query: str):
        song: Song = await self._downloader.get_song(query)
        song.context = ctx
        song.requester = ctx.author.mention

        source = discord.FFmpegPCMAudio(
            song.audio_source_url,
            executable=config.FFMPEG_EXEC_LOCATION,
            before_options=self._ffmpeg_options["before_options"],
            options=self._ffmpeg_options["options"],
        )

        super().play(source)

        self._player.source = discord.PCMVolumeTransformer(self._player.source, (float(self._volume) / 100.0))

        embed = ui.NowPlayingEmbed(song)
        await ctx.respond(embed=embed)

    async def move_to(self, channel: discord.VoiceChannel) -> None:
        await super().move_to(channel=channel)

        await self.guild.change_voice_state(channel=channel, self_deaf=True)

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._volume = max(min(value, config.MAX_VOLUME), 0)
        self._player.source.volume = float(self._volume) / 100.0

    async def _voice_channel_timeout(self):
        while True:
            await asyncio.sleep(5)
            if len(self.channel.members) == 1:
                await asyncio.sleep(20)
                if len(self.channel.members) == 1:
                    await self.disconnect()
                    break
