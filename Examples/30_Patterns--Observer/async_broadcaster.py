# async_broadcaster.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[AsyncResponder[T]] = []

    def subscribe(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.append(responder)

    def unsubscribe(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.remove(responder)

    async def announce(self, data: T) -> None:
        # Fan out to every responder, then wait for all
        await asyncio.gather(
            *(fn(data) for fn in self._responders))

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
