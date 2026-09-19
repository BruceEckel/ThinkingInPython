# async_self_removing_listener.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncListener[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[AsyncListener[T]] = []

    def subscribe(
        self, listener: AsyncListener[T]
    ) -> None:
        self._listeners.append(listener)

    def unsubscribe(
        self, listener: AsyncListener[T]
    ) -> None:
        self._listeners.remove(listener)

    async def announce(self, data: T) -> None:
        await asyncio.gather(
            *(fn(data) for fn in self._listeners))

source = Broadcaster[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    source.unsubscribe(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    source.subscribe(once)
    source.subscribe(always)
    await source.announce(1)
    await source.announce(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
