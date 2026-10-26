# async_generator.py
import asyncio
from collections.abc import AsyncGenerator

async def countdown(n: int) -> AsyncGenerator[int]:
    while n > 0:
        await asyncio.sleep(0)
        yield n
        n -= 1

async def main() -> None:
    async for n in countdown(5):
        print(f"{n = }")
    print([n * n async for n in countdown(5)])

asyncio.run(main())
#: n = 5
#: n = 4
#: n = 3
#: n = 2
#: n = 1
#: [25, 16, 9, 4, 1]
