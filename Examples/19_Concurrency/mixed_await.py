# mixed_await.py
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

async def io_price(order: int) -> int:
    await asyncio.sleep(0.05)  # A native coroutine
    return order * 10

def blocking_price(order: int) -> int:
    time.sleep(0.05)  # A blocking call, needs a thread
    return order * 10

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Needs its own process
        total += 1
    return order * 10

async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool, cpu_price, order)

async def main() -> None:
    with ProcessPoolExecutor() as pool:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(io_price(1)),
                tg.create_task(asyncio.to_thread(blocking_price, 2)),
                tg.create_task(process_price(pool, 3)),
            ]
    print([t.result() for t in tasks])

if __name__ == "__main__":
    asyncio.run(main())
