import discord

import config
from logger import setup_logger

log = setup_logger(__name__)

bot = discord.Bot()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play"))

    log.info("Successfully logged in as %s | id: %i" % (bot.user.name, bot.user.id))


bot.load_extensions("cogs")

bot.run(config.BOT_TOKEN)
