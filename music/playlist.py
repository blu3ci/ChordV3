import random
from collections import deque

import config

from .song import Song


class Playlist:
    def __init__(self) -> None:
        self._queue = deque()
        self._queue_history = deque()

        self._loop = False
        self._loop_all = False

        self._current: Song | None = None

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def queue(self) -> deque[Song]:
        return self._queue

    @property
    def queue_history(self) -> deque[Song]:
        return self._queue_history

    @property
    def loop(self) -> bool:
        return self._loop

    @property
    def loop_all(self) -> bool:
        return self._loop_all

    @property
    def current(self) -> Song | None:
        return self._current

    def toggle_loop(self) -> bool:
        if self._loop:
            self._loop = False
        else:
            self._loop = True

        self._loop_all = False

        return self._loop

    def toggle_loop_all(self) -> bool:
        if self._loop_all:
            self._loop_all = False
        else:
            self._loop_all = True

        self._loop = False

        return self._loop_all

    def next_song(self) -> Song | None:
        played_song = self._current

        if len(self._queue_history) > config.MAX_HISTORY_QUEUE_SIZE:
            self._queue_history.pop()

        if played_song is not None:
            self._queue_history.appendleft(played_song)

            if self._loop:
                self._queue.appendleft(played_song)

            if self._loop_all:
                self._queue.append(played_song)

        if len(self._queue) == 0:
            self._current = None
            return None

        self._current: Song = self._queue.popleft()

        return self._current

    def prev_song(self) -> Song | None:
        if len(self._queue_history) == 0:
            return None

        last_song = self._queue_history.popleft()
        self._queue.appendleft(last_song)

        return last_song

    def add_song(self, song: Song) -> Song:
        self._queue.append(song)

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def clear(self) -> None:
        self._queue.clear()

        self._loop = False
        self._loop_all = False

    def reset(self) -> None:
        self._queue.clear()
        self._queue_history.clear()

        self._current = None
        self._loop = False
        self._loop_all = False
