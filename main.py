import discord

import config
from logger import setup_logger

log = setup_logger(__name__)


class ChordBot(discord.Bot):
    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play"))

        log.info("Successfully logged in as %s | id: %i" % (bot.user.name, bot.user.id))

    async def on_application_command(self, context: discord.ApplicationContext):
        log.info("/%s has been executed by %s" % (context.command.name, context.author.name))


bot = ChordBot()

bot.load_extensions("cogs")

bot.run(config.BOT_TOKEN)
