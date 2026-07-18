# blocking_the_loop.py
import asyncio
import time
from collections.abc import Awaitable, Iterable

async def yielding_wait() -> None:
    await asyncio.sleep(0.05)  # Suspends this task only

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the whole event loop

async def elapsed(tasks: Iterable[Awaitable[None]]) -> float:
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    return time.perf_counter() - start

async def main() -> None:
    t_yield = await elapsed(yielding_wait() for _ in range(5))
    t_block = await elapsed(blocking_wait() for _ in range(5))
    print(f"awaited sleeps overlap: {t_yield < 0.05 * 2}")
    print(f"blocking sleeps serialize: {t_block >= 0.05 * 5}")

asyncio.run(main())
#: awaited sleeps overlap: True
#: blocking sleeps serialize: True
