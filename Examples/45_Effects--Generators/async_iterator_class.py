# async_iterator_class.py
import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import override

@dataclass
class Countdown(AsyncIterator[int]):
    n: int

    @override
    async def __anext__(self) -> int:
        if self.n == 0:
            raise StopAsyncIteration
        await asyncio.sleep(0)
        value = self.n
        self.n -= 1
        return value

async def main() -> None:
    it = Countdown(3)
    print(await it.__anext__())
    print(await it.__anext__())
    async for n in it:
        print(f"{n = }")

asyncio.run(main())
#: 3
#: 2
#: n = 1
