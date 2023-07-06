import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
EMBED_COLOR = 0x781753

MAX_VOLUME = 200
DEFAULT_VOLUME = 100
PLAYER_DISCONNECT_TIMEOUT = 30

MAX_HISTORY_QUEUE_SIZE = 15

FFMPEG_EXEC_LOCATION = f"{os.getcwd()}\\bin\\ffmpeg.exe"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") or ""
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_SECRET") or ""
