import discord
from discord import Option
from discord.ext import commands

import config
import ui
import utils
from logger import setup_logger
from music import Player

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

    @discord.slash_command(description=config.CommandDescription.CONNECT)
    @utils.perform_pre_checks
    async def connect(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.VoiceChannel,
            config.CommandArgDescription.CONNECT_CHANNEL,
            required=False,
        ),
    ):
        channel = channel or ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.channel == channel:
            raise utils.BotAlreadyInVCError
        elif ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect(cls=Player)

        embed = ui.ChordEmbed(f"{config.Message.CONNECTED_TO_VC} ``{channel.name}``")

        await ctx.respond(embed=embed)

    @discord.slash_command(description=config.CommandDescription.DISCONNECT)
    @utils.perform_pre_checks
    async def disconnect(self, ctx: discord.ApplicationContext):
        if not ctx.voice_client:
            raise utils.BotNotInVCError

        embed = ui.ChordEmbed(f"{config.Message.BOT_LEFT_VC} ``{ctx.voice_client.channel.name}``")

        await ctx.respond(embed=embed)
        await ctx.voice_client.disconnect()

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("%s cog loaded successfully" % __class__.__name__)

        for command in self.get_commands():
            log.info("Loaded the command /%s successfully" % command)


def setup(bot: discord.Bot):
    bot.add_cog(General(bot))
