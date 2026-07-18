# async_mechanics.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)  # A stand-in for a network wait
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    results = await asyncio.gather(  # Run all three concurrently
        fetch("a", 0.03), fetch("b", 0.02), fetch("c", 0.01))
    print(results)

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C']
