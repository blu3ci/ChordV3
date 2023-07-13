import logging

import discord

import config
from logger import setup_logger

log = setup_logger(__name__)


class ChordBot(discord.Bot):
    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play"))

        log.info("Successfully logged in as %s | id: %i" % (bot.user.name, bot.user.id))
        log.info("Active in %i servers | %s" % (len(bot.guilds), ", ".join([guild.name for guild in bot.guilds])))

        setup_logger("discord", level=logging.INFO)

    async def on_application_command(self, context: discord.ApplicationContext):
        log.info("/%s has been executed by %s" % (context.command, context.author.name))


if __name__ == "__main__":
    bot = ChordBot()

    cogs = ["cogs.errors", "cogs.general", "cogs.music"]

    for cog in cogs:
        bot.load_extension(cog)

    bot.run(config.BOT_TOKEN)
