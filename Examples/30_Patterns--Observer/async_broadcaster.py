# async_broadcaster.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncListener[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[AsyncListener[T]] = []

    def subscribe(self, listener: AsyncListener[T]) -> None:
        self._listeners.append(listener)

    def unsubscribe(
        self, listener: AsyncListener[T]
    ) -> None:
        self._listeners.remove(listener)

    async def announce(self, data: T) -> None:
        # Fan out to every listener, then wait for all
        await asyncio.gather(
            *(fn(data) for fn in self._listeners))

class Thermometer(Broadcaster[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    async def set_celsius(self, value: float) -> None:
        # A property setter cannot be awaited
        self._celsius = value
        await self.announce(value)
