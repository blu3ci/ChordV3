import asyncio
import re
from functools import partial

import yt_dlp

import config
import utils
from logger import setup_logger

from .song import Song, SongType


class Downloader:
    def __init__(self):
        self.ytdlp_opts = {
            "format": "bestaudio/best",
            "ffmpeg_location": config.FFMPEG_EXEC_LOCATION,
            "outtmpl": "downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "logger": setup_logger("yt_dlp"),
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",  # noqa
        }

    async def get_song(self, query: str) -> Song:
        try:
            if self.is_url(query):
                result_data = await self._extract_url(query)
            else:
                result_data = await self._extract_search(query)
        except (IndexError, yt_dlp.utils.DownloadError):
            raise utils.FailedToDownloadSongError(query)

        url = result_data["webpage_url"]

        return Song(
            audio_source_url=result_data["url"],
            original_url=url,
            title=result_data["title"],
            duration=result_data.get("duration", "🔴 LIVE"),
            uploader=result_data["uploader"],
            thumbnail=result_data["thumbnails"][0]["url"],
            song_type=self.get_song_type(url),
        )

    async def _extract_search(self, query: str) -> Song:
        result_data = await self._extract_url(f"ytsearch1:{query}")

        result_data = result_data["entries"][0]

        return result_data

    async def _extract_url(self, url: str) -> Song:
        with yt_dlp.YoutubeDL(self.ytdlp_opts) as ydl:
            loop = asyncio.get_event_loop()
            partial_func = partial(ydl.extract_info, url, download=False)

            result_data = await loop.run_in_executor(None, partial_func)

        return result_data

    def get_song_type(self, url: str) -> SongType:
        regexes = {
            SongType.YOUTUBE: r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$"  # noqa
        }

        for song_type, regex in regexes.items():
            if re.match(regex, url):
                return song_type

        return SongType.CUSTOM

    def is_url(self, url: str) -> bool:
        url_regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")  # noqa
        return True if url_regex.match(url) else False
