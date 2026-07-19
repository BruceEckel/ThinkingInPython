# to_thread.py
import asyncio
import time
from collections.abc import Awaitable, Iterable

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the event loop

async def offloaded_wait() -> None:
    await asyncio.to_thread(time.sleep, 0.05)  # Runs in a thread

async def elapsed(tasks: Iterable[Awaitable[None]]) -> float:
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    return time.perf_counter() - start

async def main() -> None:
    t_block = await elapsed(blocking_wait() for _ in range(5))
    t_offload = await elapsed(offloaded_wait() for _ in range(5))
    print(f"blocking sleeps serialize: {t_block >= 0.05 * 5}")
    print(f"offloaded sleeps overlap: {t_offload < 0.05 * 2}")

asyncio.run(main())
#: blocking sleeps serialize: True
#: offloaded sleeps overlap: True
