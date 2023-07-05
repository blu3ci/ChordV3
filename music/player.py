import asyncio

import discord

import utils
from logger import setup_logger

log = setup_logger(__name__)


class Player(discord.VoiceClient):
    def __init__(self, client: discord.Bot, channel: discord.VoiceChannel):
        super().__init__(client, channel)

        self.client: discord.Bot = client
        self.channel: discord.VoiceChannel = channel

        self._voice_channel_timeout_task: asyncio.Task = None

    async def connect(self, *, reconnect: bool = True, timeout: float | None = None):
        await super().connect(reconnect=reconnect, timeout=timeout)

        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True)

        self._voice_channel_timeout_task = self.loop.create_task(self._voice_channel_timeout())
        
    async def disconnect(self, *, force: bool = True) -> None:
        await super().disconnect(force=force)
        self._voice_channel_timeout_task.cancel()

    async def move_to(self, channel: discord.VoiceChannel) -> None:
        await super().move_to(channel=channel)

        await self.guild.change_voice_state(channel=channel, self_deaf=True)

    async def _voice_channel_timeout(self):
        while True:
            await asyncio.sleep(5)
            if len(self.client.get_channel(self.channel.id).members) == 1:
                await asyncio.sleep(20)
                if len(self.client.get_channel(self.channel.id).members) == 1:
                    await self.disconnect()
                    break
