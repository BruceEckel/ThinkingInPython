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

async def alarm(celsius: float) -> None:
    if celsius > 100:
        await asyncio.sleep(0.05)  # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)  # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer(15.0)
    t.subscribe(alarm)
    t.subscribe(log_reading)
    await t.set_celsius(20)  # Below the alarm threshold
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
