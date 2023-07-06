from discord import Embed

import config
from music import Song


class BasicEmbed(Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(color=config.EMBED_COLOR, *args, **kwargs)


class ChordEmbed(BasicEmbed):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(description=message, *args, **kwargs)


class NowPlayingEmbed(BasicEmbed):
    def __init__(self, song: Song, *args, **kwargs):
        super().__init__(
            title=config.Message.NOW_PLAYING, description=song.title, url=song.original_url, *args, **kwargs
        )
        super().add_field(name="Uploader", value=song.uploader, inline=True)
        super().add_field(name="Duration", value=song.duration, inline=True)
        super().add_field(name="Requester", value=song.requester, inline=True)
        super().set_thumbnail(url=song.thumbnail)


class QueuedEmbed(NowPlayingEmbed):
    def __init__(self, song: Song, *args, **kwargs):
        super().__init__(song, *args, **kwargs)
        super().title = config.Message.QUEUED
