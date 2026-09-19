# async_self_removing_listener.py
import asyncio
from async_broadcaster import Broadcaster

source = Broadcaster[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    source.unsubscribe(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    source.subscribe(once)
    source.subscribe(always)
    await source.announce(1)
    await source.announce(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
