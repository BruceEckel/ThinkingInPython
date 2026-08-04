# context_var.py
import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")
current = "-"  # The same idea as a plain global

async def handle(name: str) -> None:
    global current
    current = name
    request_id.set(name)
    await asyncio.sleep(0)  # Stand-in for a database call
    print(f"context {request_id.get()}, global {current}")

async def main() -> None:
    async with asyncio.TaskGroup() as group:
        for name in ("req-1", "req-2", "req-3"):
            group.create_task(handle(name))
    print(f"after: context {request_id.get()}, global {current}")

asyncio.run(main())
#: context req-1, global req-3
#: context req-2, global req-3
#: context req-3, global req-3
#: after: context -, global req-3
