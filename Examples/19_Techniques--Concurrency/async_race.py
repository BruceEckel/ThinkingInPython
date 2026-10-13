# async_race.py
import asyncio

counter = 0

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        # Release control to the event loop
        await asyncio.sleep(0)
        counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(f"counter: {counter} of {8 * 50}")

asyncio.run(main())
#: counter: 50 of 400
