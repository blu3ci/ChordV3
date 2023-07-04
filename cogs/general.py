import discord
from discord.ext import commands

import config
import ui
from logger import setup_logger

log = setup_logger(__name__)


class General(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @discord.slash_command(description=config.CommandDescription.NICK)
    @discord.default_permissions(change_nickname=True)
    async def nick(
        self, ctx: discord.ApplicationContext, nick: discord.Option(str, config.CommandArgDescription.NEW_NICK)
    ):
        if nick.lower() == "reset":
            nick = self.bot.user.name

        await ctx.guild.me.edit(nick=nick)

        embed = ui.ChordEmbed(f"{config.Message.CHANGE_NICK} ``{nick}``")

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(General(bot))
