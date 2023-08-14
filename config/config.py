import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
EMBED_COLOR = 0x3205bb

MAX_VOLUME = 200
DEFAULT_VOLUME = 100
PLAYER_DISCONNECT_TIMEOUT = 30
MAX_SONGS_PER_PLAYLIST_PAGE = 10

MAX_HISTORY_QUEUE_SIZE = 15

FFMPEG_EXEC_LOCATION = f"{os.getcwd()}\\bin\\ffmpeg.exe"  # install dir (use ffmpeg if added to path)
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") or ""
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") or ""

SPOTIPY_CACHE_DIR = os.path.join(os.getcwd(), ".spotipy_cache")
