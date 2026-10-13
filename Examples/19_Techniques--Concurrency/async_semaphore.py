# async_semaphore.py
import asyncio
from meter import Meter

meter = Meter()
semaphore = asyncio.Semaphore(2)

async def worker() -> None:
    async with semaphore:
        with meter:
            await asyncio.sleep(0.05)

async def main() -> None:
    await asyncio.gather(*(worker() for _ in range(5)))
    print(f"peak concurrent workers: {meter.peak}")

asyncio.run(main())
#: peak concurrent workers: 2
