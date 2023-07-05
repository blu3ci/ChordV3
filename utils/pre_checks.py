import functools

import discord

from . import exceptions


class PreCheck:
    def __init__(self, ctx: discord.ApplicationContext) -> None:
        self.ctx = ctx

    async def check_author_in_vc(self) -> None:
        if not self.ctx.author.voice:
            raise exceptions.NotConnectedToVCError

    async def check_author_and_bot_same_vc(self) -> None:
        if self.ctx.voice_client and not (self.ctx.voice_client.channel == self.ctx.author.voice.channel):
            raise exceptions.AuthorNotInBotVCError

    async def run_checks(self) -> None:
        await self.check_author_in_vc()
        await self.check_author_and_bot_same_vc()


def perform_pre_checks(func):
    @functools.wraps(func)
    async def wrapper(cog: discord.Cog, ctx: discord.application_command, *args, **kwargs):
        checker = PreCheck(ctx)
        await checker.run_checks()
        await func(cog, ctx, *args, **kwargs)

    return wrapper
