# async_manager.py
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def session(name: str) -> AsyncIterator[str]:
    print(f"open {name}")
    await asyncio.sleep(0.01)  # Setup that waits
    try:
        yield name
    finally:
        await asyncio.sleep(0.01)  # Cleanup that waits
        print(f"close {name}")

async def main() -> None:
    async with session("db") as s:
        print(f"using {s}")

asyncio.run(main())
#: open db
#: using db
#: close db
