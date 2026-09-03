# gather_orphan.py
import asyncio

async def loud(data: int) -> None:
    raise ValueError(f"bad: {data}")

async def slow(data: int) -> None:
    await asyncio.sleep(0.05)
    print(f"slow finished: {data}")

async def main() -> None:
    try:
        await asyncio.gather(loud(1), slow(1))
    except ValueError as e:
        print(f"caught: {e}")
    await asyncio.sleep(0.25)  # Let the orphan finish

asyncio.run(main())
#: caught: bad: 1
#: slow finished: 1
