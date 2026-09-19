# exercise_3.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncListener[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[AsyncListener[T]] = []

    def subscribe(self, listener: AsyncListener[T]) -> None:
        self._listeners.append(listener)

    async def announce(self, data: T) -> None:
        results = await asyncio.gather(
            *(listener(data)
              for listener in self._listeners),
            return_exceptions=True)
        failures = [
            r for r in results if isinstance(r, Exception)]
        if failures:
            raise ExceptionGroup(
                "listener failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    source = Broadcaster[int]()
    source.subscribe(broken)
    source.subscribe(record)
    try:
        await source.announce(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
