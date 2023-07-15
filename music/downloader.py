import asyncio
import re
from collections import deque
from functools import partial

import discord
import yt_dlp
from spotipy import Spotify, SpotifyException
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials

import config
import utils
from logger import setup_logger

from .song import PartialSong, Song, SongType


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

        self.spotify_api = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=config.SPOTIFY_CLIENT_ID,
                client_secret=config.SPOTIFY_CLIENT_SECRET,
                cache_handler=CacheFileHandler(cache_path=config.SPOTIPY_CACHE_DIR),
            )
        )

    async def get_song(self, ctx: discord.ApplicationContext, query: str) -> Song | PartialSong | list[PartialSong]:
        self.ctx = ctx

        past_songs: deque[Song] = ctx.voice_client.playlist.queue_history

        for song in past_songs:
            if query in [song.query, song.title]:
                song.context = ctx
                song.requester = ctx.author.mention

                return song

        try:
            if self.is_url(query):
                song = await self._extract_url(query)
            else:
                song = await self._extract_search(query)
        except (IndexError, yt_dlp.utils.DownloadError):
            raise utils.FailedToDownloadSongError(query)

        if isinstance(song, Song):
            song.query = query

        return song

    async def _extract_search(self, query: str) -> Song:
        url = f"ytsearch1:{query}"

        with yt_dlp.YoutubeDL(self.ytdlp_opts) as ydl:
            loop = asyncio.get_event_loop()
            partial_func = partial(ydl.extract_info, url, download=False)

            result_data = await loop.run_in_executor(None, partial_func)

        result_data = result_data["entries"][0]

        return await self.convert_to_song(result_data)

    async def _extract_url(self, url: str) -> Song:
        if self.get_song_type(url) == SongType.SPOTIFY_TRACK:
            return await self._extract_spotify_track(url)
        elif self.get_song_type(url) == SongType.SPOTIFY_PLAYLIST:
            return await self._extract_spotify_playlist(url)
        elif self.get_song_type(url) == SongType.SPOTIFY_ALBUM:
            return await self._extract_spotify_album(url)
        elif self.get_song_type(url) == SongType.CUSTOM:
            return await self.convert_to_song(
                {
                    "url": url,
                    "webpage_url": url,
                    "title": "<Custom Song>",
                    "uploader": "<No Uploader>",
                    "thumbnail": "",
                    "duration": "<No Duration>",
                }
            )

        with yt_dlp.YoutubeDL(self.ytdlp_opts) as ydl:
            loop = asyncio.get_event_loop()
            partial_func = partial(ydl.extract_info, url, download=False)

            result_data = await loop.run_in_executor(None, partial_func)

        return await self.convert_to_song(result_data)

    async def _extract_spotify_track(self, url: str) -> PartialSong:
        base_url = "https://open.spotify.com/track/"

        try:
            results = self.spotify_api.track(url)
        except SpotifyException:
            raise utils.FailedToDownloadSongError(url)

        artists = ", ".join([artist.get("name") for artist in results["artists"]])
        artists = artists[: len(artists)]

        return PartialSong(
            original_url=base_url + results["album"]["id"],
            title=results["name"],
            duration=int(results["duration_ms"] / 1000),
            uploader=artists,
            thumbnail=results["album"]["images"][0]["url"],
            song_type=SongType.SPOTIFY_TRACK,
            context=self.ctx,
            requester=self.ctx.author.mention,
        )

    async def _extract_spotify_playlist(self, url: str) -> list[PartialSong]:
        try:
            results = self.spotify_api.playlist_items(url)
        except SpotifyException:
            raise utils.FailedToDownloadSongError(url)

        coros = [self._extract_spotify_track(track["track"]["uri"]) for track in results["items"]]

        songs: list[PartialSong] = await asyncio.gather(*coros)

        return songs

    async def _extract_spotify_album(self, url: str) -> list[PartialSong]:
        try:
            results = self.spotify_api.album(url)
        except SpotifyException:
            raise utils.FailedToDownloadSongError(url)

        coros = [self._extract_spotify_track(track["uri"]) for track in results["tracks"]["items"]]

        songs: list[PartialSong] = await asyncio.gather(*coros)

        return songs

    async def convert_to_song(self, result_data: dict) -> Song:
        url = result_data["webpage_url"]

        return Song(
            audio_source_url=result_data["url"],
            original_url=url,
            title=result_data["title"],
            duration=result_data.get("duration", "🔴 LIVE"),
            uploader=result_data["uploader"],
            thumbnail=result_data["thumbnail"],
            song_type=self.get_song_type(url),
            context=self.ctx,
            requester=self.ctx.author.mention,
        )

    def get_song_type(self, url: str) -> SongType:
        regexes = {
            SongType.YOUTUBE: r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$",  # noqa
            SongType.SPOTIFY_TRACK: r"https://open.spotify.com/track/\w+",
            SongType.SPOTIFY_PLAYLIST: r"https://open.spotify.com/playlist/\w+",
            SongType.SPOTIFY_ALBUM: r"https://open.spotify.com/album/\w+",
        }

        for song_type, regex in regexes.items():
            if re.match(regex, url):
                return song_type

        return SongType.CUSTOM

    def is_url(self, url: str) -> bool:
        url_regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")  # noqa
        return True if url_regex.match(url) else False
