# ch19_ordered_locks.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(
    name: str, first: asyncio.Lock, second: asyncio.Lock
) -> None:
    async with first:
        print(f"{name}: holds its first lock")
        await asyncio.sleep(0.01)  # Let the other task run
        async with second:
            print(f"{name}: holds both")

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker("task 1", lock_a, lock_b),
                # The same order as task 1
                worker("task 2", lock_a, lock_b),
            ),
            timeout=0.5,
        )
        print("both workers finished")
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: task 1: holds its first lock
#: task 1: holds both
#: task 2: holds its first lock
#: task 2: holds both
#: both workers finished
