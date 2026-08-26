# async_locks.py
import asyncio

counter = 0
lock = asyncio.Lock()

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        async with lock:
            value = counter  # Read
            # Yield to the event loop
            await asyncio.sleep(0)
            counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
