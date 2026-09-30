# async_self_removing_responder.py
import asyncio
from async_broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Disconnects mid-notification
    broadcaster.disconnect(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    broadcaster.connect(once)
    broadcaster.connect(always)
    await broadcaster.announce(1)
    await broadcaster.announce(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
