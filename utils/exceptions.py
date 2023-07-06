from discord import DiscordException


class NotConnectedToVCError(DiscordException):
    pass


class AuthorNotInBotVCError(DiscordException):
    pass


class BotNotPlayingError(DiscordException):
    pass


class BotIsPlayingError(DiscordException):
    pass


class BotAlreadyInVCError(Exception):
    pass


class BotNotInVCError(Exception):
    pass


class FailedToDownloadSongError(Exception):
    def __init__(self, query: str) -> None:
        self.query = query
        super().__init__(query)


class FailedToParseTimeFormatError(Exception):
    pass
