# exercise_5_stray_release.py
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
    semaphore.release()  # Nothing was acquired
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 200
