# async_mechanics.py
import asyncio

async def fetch(item: str) -> str:
    await asyncio.sleep(0.01)  # A stand-in for a network wait
    return item.upper()

async def main() -> None:
    print(await fetch("solo"))  # Await one coroutine
    print(await asyncio.gather(  # Run several concurrently
        fetch("a"), fetch("b"), fetch("c")))

asyncio.run(main())
#: SOLO
#: ['A', 'B', 'C']
