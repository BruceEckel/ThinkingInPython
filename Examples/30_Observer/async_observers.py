# async_observers.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver = Callable[[float], Awaitable[None]]

class Observable:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver] = []

    def subscribe(self, observer: AsyncObserver) -> None:
        self._observers.append(observer)

    async def notify(self, data: float) -> None:
        # Fan out to every observer at once, then wait for all
        await asyncio.gather(*(obs(data) for obs in self._observers))

class Thermometer(Observable):
    def __init__(self) -> None:
        super().__init__()
        self._celsius = 0.0

    @property
    def celsius(self) -> float:
        return self._celsius

    async def set_celsius(self, value: float) -> None:
        # A property setter cannot be awaited
        self._celsius = value
        await self.notify(value)

async def alarm(celsius: float) -> None:
    if celsius > 100:
        await asyncio.sleep(0.02)  # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)  # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer()
    t.subscribe(alarm)
    t.subscribe(log_reading)
    await t.set_celsius(20)  # Below the alarm threshold
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
