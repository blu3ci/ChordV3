from discord import DiscordException


class NotConnectedToVCError(DiscordException):
    pass


class AuthorNotInBotVCError(DiscordException):
    pass


class BotNotInVCError(DiscordException):
    pass


class BotNotPlayingError(DiscordException):
    pass


class BotIsPlayingError(DiscordException):
    pass


class BotAlreadyInVCError(Exception):
    pass


class BotNotInVCError(Exception):
    pass
