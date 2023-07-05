import asyncio

import discord

from logger import setup_logger

log = setup_logger(__name__)


class Player(discord.VoiceClient):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel):
        super().__init__(client, channel)

        self.client: discord.Bot = client
        self.channel: discord.VoiceChannel = channel

    async def connect(self, *, reconnect: bool = True, timeout: float | None = None):
        await super().connect(reconnect=reconnect, timeout=timeout)

        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True)
        
        self.loop.create_task(self._voice_channel_timeout())
        
        log.info(f"{self.channel.guild.name}: Bot connected to {self.channel}")

    async def _voice_channel_timeout(self):
        while True:
            await asyncio.sleep(5)
            if len(self.client.get_channel(self.channel.id).members) == 1:
                await self.disconnect()
                break
