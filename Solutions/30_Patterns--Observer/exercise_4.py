# exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[AsyncResponder[T]] = []

    def connect(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.append(responder)

    async def announce(self, data: T) -> None:
        results = await asyncio.gather(
            *(responder(data)
              for responder in self._responders),
            return_exceptions=True)
        failures = [
            r for r in results
            if isinstance(r, BaseException)]
        if failures:
            raise BaseExceptionGroup(
                "responder failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    broadcaster = Broadcaster[int]()
    broadcaster.connect(broken)
    broadcaster.connect(record)
    try:
        await broadcaster.announce(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
