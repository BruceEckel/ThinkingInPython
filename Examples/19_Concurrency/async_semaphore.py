# async_semaphore.py
import asyncio

active = 0
peak = 0
pool = asyncio.Semaphore(2)  # At most 2 tasks at once

async def worker() -> None:
    global active, peak
    async with pool:
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.05)
        active -= 1

async def main() -> None:
    await asyncio.gather(*(worker() for _ in range(5)))
    print(f"peak concurrent workers: {peak}")

asyncio.run(main())
#: peak concurrent workers: 2
