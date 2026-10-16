# exercise_5.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(f"counter: {counter} of {8 * 50}")

asyncio.run(main())
#: counter: 400 of 400
