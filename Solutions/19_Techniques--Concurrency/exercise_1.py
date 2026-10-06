# exercise_1.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    x = fetch("a", 0.03)
    print(type(x).__name__)
    results = await asyncio.gather(
        x, fetch("b", 0.02),
        fetch("c", 0.01), fetch("d", 0.005))
    print(results)

asyncio.run(main())
#: coroutine
#: a: started
#: b: started
#: c: started
#: d: started
#: d: resumed
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C', 'D']
