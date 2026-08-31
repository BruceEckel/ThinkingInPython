# exercise_11.py
import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id",
                                         default="-")
current = "-"  # The same idea as a plain global

async def handle(name: str) -> None:
    global current
    current = name
    await asyncio.sleep(0)  # Stand-in for a database call
    print(f"context {request_id.get()}, global {current}")

async def main() -> None:
    # Set once, before any task exists
    request_id.set("main")
    async with asyncio.TaskGroup() as group:
        for name in ("req-1", "req-2", "req-3"):
            group.create_task(handle(name))
    print(f"after: context {request_id.get()}, "
          f"global {current}")

asyncio.run(main())
#: context main, global req-3
#: context main, global req-3
#: context main, global req-3
#: after: context main, global req-3
