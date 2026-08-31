# exercise_5.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count):
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main():
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
