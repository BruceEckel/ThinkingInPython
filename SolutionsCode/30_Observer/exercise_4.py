# exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver[T] = Callable[[T], Awaitable[None]]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver[T]] = []

    def subscribe(self, observer: AsyncObserver[T]) -> None:
        self._observers.append(observer)

    async def notify(self, data: T) -> None:
        results = await asyncio.gather(
            *(obs(data) for obs in self._observers),
            return_exceptions=True)
        failures = [r for r in results if isinstance(r, Exception)]
        if failures:
            raise ExceptionGroup("observer failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    obs = Observable[int]()
    obs.subscribe(broken)
    obs.subscribe(record)
    try:
        await obs.notify(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
