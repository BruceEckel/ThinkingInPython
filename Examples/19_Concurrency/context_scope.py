# context_scope.py
import asyncio
import threading
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")

def audit(step: str) -> str:
    main = threading.current_thread() is threading.main_thread()
    where = "main thread" if main else "worker thread"
    return f"[{request_id.get()}] {step} on the {where}"

async def handle(name: str) -> None:
    with request_id.set(name):
        print(audit("start"))
        print(await asyncio.to_thread(audit, "offloaded"))
    print(audit("after the scope"))

asyncio.run(handle("req-7"))
#: [req-7] start on the main thread
#: [req-7] offloaded on the worker thread
#: [-] after the scope on the main thread
