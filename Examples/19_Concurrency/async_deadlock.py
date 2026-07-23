# async_deadlock.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(first: asyncio.Lock, second: asyncio.Lock) -> None:
    async with first:
        await asyncio.sleep(0.01)  # Let the other task grab its lock
        async with second:
            pass  # Never reached

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker(lock_a, lock_b),
                worker(lock_b, lock_a),
            ),
            timeout=0.5,
        )
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: deadlock detected
