# ch19_ordered_locks.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(first: asyncio.Lock, second: asyncio.Lock) -> None:
    async with first:
        await asyncio.sleep(0.01)  # Let the other task run
        async with second:
            pass

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker(lock_a, lock_b),
                worker(lock_a, lock_b),  # The same order
            ),
            timeout=0.5,
        )
        print("both workers finished")
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: both workers finished
