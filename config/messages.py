from enum import StrEnum


class CommandDescription(StrEnum):
    NICK: str = "Changes the bot's nickname."
    CONNECT: str = "Connect to a voice channel."
    DISCONNECT: str = "Disconnect from a voice channel."
    PLAY: str = "Plays a song."
    STOP: str = "Stops the song."
    RESUME: str = "Resumes the current song."
    PAUSE: str = "Pauses the song."
    SKIP: str = "Skip to the next song."
    PREV: str = "Play the previous song."


class CommandArgDescription(StrEnum):
    NEW_NICK: str = "New nickname (use 'reset' to reset the nick)"


class Message(StrEnum):
    CHANGE_NICK: str = "✏️ Updated my nickname to "
    CONNECTED_TO_VC = "✅ Connected to "
