from dataclasses import dataclass
from enum import Enum, auto

import discord


class SongType(Enum):
    YOUTUBE = auto()
    SPOTIFY = auto()
    SOTIFY_ALBUM = auto()
    SPOTIFY_PLAYLIST = auto()
    CUSTOM = auto()


@dataclass
class Song:
    audio_source_url: str
    original_url: str
    title: str
    duration: int | str
    uploader: str
    thumbnail: str
    song_type: SongType
    context: discord.ApplicationContext | None = None
    requester: str | None = None
