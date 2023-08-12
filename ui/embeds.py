import datetime

from discord import Embed

import config
from music import PartialSong, Song


class BasicEmbed(Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(color=config.EMBED_COLOR, *args, **kwargs)


class ChordEmbed(BasicEmbed):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(description=message, *args, **kwargs)


class NowPlayingEmbed(BasicEmbed):
    def __init__(self, song: Song, *args, **kwargs):
        super().__init__(
            title=config.Message.NOW_PLAYING, description=f"``{song.title}``", url=song.original_url, *args, **kwargs
        )
        super().add_field(name="Uploader", value=f"``{song.uploader}``", inline=True)
        super().add_field(name="Duration", value=f"``{self.parse_duration(song.duration)}``", inline=True)
        super().add_field(name="Requester", value=song.requester, inline=True)
        super().set_thumbnail(url=song.thumbnail)

    @staticmethod
    def parse_duration(duration: int | str):
        if isinstance(duration, int):
            return datetime.timedelta(seconds=duration)

        return duration


class QueuedEmbed(NowPlayingEmbed):
    def __init__(self, song: Song | list[PartialSong], *args, **kwargs):
        super().__init__(song, *args, **kwargs)
        self.title = config.Message.QUEUED
