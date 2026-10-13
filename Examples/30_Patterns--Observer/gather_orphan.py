# gather_orphan.py
import asyncio
from async_broadcaster import AsyncBroadcaster
from exceptions import aexpect

async def failing(data: int) -> None:
    raise ValueError(f"bad: {data}")

async def slow(data: int) -> None:
    await asyncio.sleep(0.05)
    print(f"slow finished: {data}")

async def main() -> None:
    broadcaster = AsyncBroadcaster[int]()
    broadcaster.connect(failing)
    broadcaster.connect(slow)
    await aexpect(ValueError, broadcaster.announce, 1)
    await asyncio.sleep(0.25)  # Let the orphan finish

asyncio.run(main())
#: [ValueError] bad: 1
#: slow finished: 1
