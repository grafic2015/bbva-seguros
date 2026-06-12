"""Bus de eventos. El pipeline (threads) publica; los WebSockets reciben."""

import asyncio
from typing import Any


def _safe_put(q: asyncio.Queue, event: dict) -> None:
    try:
        q.put_nowait(event)
    except asyncio.QueueFull:
        pass


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)

    def publish(self, event: dict[str, Any]) -> None:
        """Thread-safe: puede llamarse desde hilos del pipeline."""
        loop = self._loop
        if loop and not loop.is_closed():
            for q in list(self._subscribers):
                loop.call_soon_threadsafe(_safe_put, q, event)
        else:
            for q in list(self._subscribers):
                _safe_put(q, event)


bus = EventBus()
