# exercise_1.py
import asyncio

async def fetch(item, delay):
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main():
    results = await asyncio.gather(
        fetch("a", 0.03), fetch("b", 0.02),
        fetch("c", 0.01), fetch("d", 0.005))
    print(results)

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: d: resumed
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C', 'D']
