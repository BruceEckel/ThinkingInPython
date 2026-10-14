# async_deadlock.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(
    name: str, first: asyncio.Lock, second: asyncio.Lock
) -> None:
    async with first:
        print(f"{name}: holds its first lock")
        # Let the other task grab its lock
        await asyncio.sleep(0.01)
        async with second:
            print(f"{name}: holds both")

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker("task 1", lock_a, lock_b),
                worker("task 2", lock_b, lock_a),
            ),
            timeout=0.5,
        )
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: task 1: holds its first lock
#: task 2: holds its first lock
#: deadlock detected
