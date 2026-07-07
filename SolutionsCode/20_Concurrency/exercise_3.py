# exercise_3.py
import asyncio

counter = 0

async def increment(count, lock):
    global counter
    for _ in range(count):
        async with lock:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main():
    lock = asyncio.Lock()
    await asyncio.gather(*(increment(50, lock) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
