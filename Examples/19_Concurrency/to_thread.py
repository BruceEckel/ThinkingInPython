# to_thread.py
import asyncio
import time

async def offloaded_wait() -> None:
    await asyncio.to_thread(time.sleep, 0.05)  # Runs in a thread

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(*(offloaded_wait() for _ in range(5)))
    elapsed = time.perf_counter() - start
    print(f"offloaded sleeps overlap: {elapsed < 0.05 * 2}")

asyncio.run(main())
#: offloaded sleeps overlap: True
