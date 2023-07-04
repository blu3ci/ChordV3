from discord import Embed

import config


class BasicEmbed(Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(color=config.EMBED_COLOR, *args, **kwargs)


class ChordEmbed(BasicEmbed):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(description=message, *args, **kwargs)
