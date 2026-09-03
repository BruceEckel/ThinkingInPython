# async_self_removing_observer.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver[T] = Callable[[T], Awaitable[None]]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver[T]] = []

    def subscribe(
        self, observer: AsyncObserver[T]
    ) -> None:
        self._observers.append(observer)

    def unsubscribe(
        self, observer: AsyncObserver[T]
    ) -> None:
        self._observers.remove(observer)

    async def notify(self, data: T) -> None:
        await asyncio.gather(
            *(obs(data) for obs in self._observers))

obs = Observable[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    obs.unsubscribe(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    obs.subscribe(once)
    obs.subscribe(always)
    await obs.notify(1)
    await obs.notify(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
