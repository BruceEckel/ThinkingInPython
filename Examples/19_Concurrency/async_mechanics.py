# async_mechanics.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    # Stand-in for a network request
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    x = fetch("a", 0.03)  # Nothing runs yet
    print(type(x).__name__)
    # Run all three concurrently
    results = await asyncio.gather(
        x, fetch("b", 0.02), fetch("c", 0.01))
    print(results)

asyncio.run(main())
#: coroutine
#: a: started
#: b: started
#: c: started
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C']
