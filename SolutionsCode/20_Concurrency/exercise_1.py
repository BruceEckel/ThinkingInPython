# exercise_1.py
import asyncio

async def fetch(item):
    await asyncio.sleep(0.01)
    return item.upper()

async def main():
    print(await asyncio.gather(
        fetch("a"), fetch("b"), fetch("c"), fetch("d")))

asyncio.run(main())
#: ['A', 'B', 'C', 'D']
