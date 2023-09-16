import datetime
import math
from collections import deque

import discord
from discord.ui import View, button

import config
import music
import ui


class PlaylistPaginatorView(View):
    def __init__(self, ctx: discord.ApplicationContext):
        super().__init__(timeout=None)

        self.ctx = ctx
        self.queue: deque[music.Song] = self.ctx.voice_client.playlist.queue.copy()
        self.queue.appendleft(self.ctx.voice_client.playlist.current)

        self.current_page: int = 1
        self.total_pages: int = 1

        self.separator: int = config.MAX_SONGS_PER_PLAYLIST_PAGE

    async def send(self):
        await self.ctx.respond(embed=self.get_embed(), view=self)

    def get_total_duration(self):
        total_seconds: int = 0

        try:
            if total_seconds == 0:
                durations = [str(ui.NowPlayingEmbed.parse_duration(track.duration)) for track in self.queue]
                for duration in durations:
                    parser = datetime.datetime.strptime(duration, "%H:%M:%S")
                    total_seconds += datetime.timedelta(
                        hours=parser.hour,
                        minutes=parser.minute,
                        seconds=parser.second,
                    ).total_seconds()
        except (ValueError, AttributeError):
            return str(datetime.timedelta(seconds=0))
        return str(datetime.timedelta(seconds=total_seconds))

    def get_embed(self):
        formatted_playlist: str = (
            f"📜 Playlist Length: {len(self.queue)} | ⌛ Duration: ``{self.get_total_duration()}``\n"
        )

        self.total_pages = int(math.ceil(len(self.queue) / self.separator))

        try:
            for index, track in enumerate(self.queue):
                if (self.current_page - 1) * self.separator > index:
                    continue

                if index == self.current_page * self.separator:
                    break

                formatted_playlist += f"\n**``{index + 1}`` - [{track.title}](<{track.original_url}>) - {track.requester} - ``{ui.NowPlayingEmbed.parse_duration(track.duration)}``**"  # noqa
        except AttributeError:
            self.total_pages = 0

        if self.total_pages == 0:
            embed = ui.ChordEmbed(config.Message.PLAYLIST_EMPTY)
            self.total_pages = 1
        else:
            embed = ui.BasicEmbed(title="🎶 Playlist", description=formatted_playlist)

        self.update_buttons()

        return embed

    async def edit_embed(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    def update_buttons(self):
        page_counter: discord.ui.Button = self.children[-1]
        page_counter.label = f"{self.current_page}/{self.total_pages}"

        first_page_btn: discord.ui.Button = self.children[0]
        prev_page_btn: discord.ui.Button = self.children[1]
        next_page_btn: discord.ui.Button = self.children[2]
        last_page_btn: discord.ui.Button = self.children[3]

        for child in self.children[: len(self.children) - 1]:
            child.disabled = False

        if self.current_page == 1:
            first_page_btn.disabled = True
            prev_page_btn.disabled = True

        if self.current_page == self.total_pages:
            next_page_btn.disabled = True
            last_page_btn.disabled = True

    @button(label="<<")
    async def first_page_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1

        await self.edit_embed(interaction)

    @button(label="<", style=discord.ButtonStyle.danger)
    async def prev_page_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self.current_page == 1:
            self.current_page -= 1

        await self.edit_embed(interaction)

    @button(label=">", style=discord.ButtonStyle.primary)
    async def next_page_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        await self.edit_embed(interaction)

    @button(label=">>")
    async def last_page_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = self.total_pages

        await self.edit_embed(interaction)

    @button(label="0/0", disabled=True)
    async def page_counter_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass
