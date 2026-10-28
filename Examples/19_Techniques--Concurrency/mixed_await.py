# mixed_await.py
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from pricing import Price, cpu_price

async def io_price(order: int) -> Price:
    await asyncio.sleep(0.05)  # Native coroutine
    return order * 10

def blocking_price(order: int) -> Price:
    time.sleep(0.05)  # Blocking call, needs a thread
    return order * 10

async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> Price:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool,
                                      cpu_price, order)

async def main(pool: ProcessPoolExecutor) -> None:
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(io_price(1)),
            tg.create_task(
                asyncio.to_thread(blocking_price, 2)),
            tg.create_task(process_price(pool, 3)),
        ]
    print([t.result() for t in tasks])

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        asyncio.run(main(pool))
