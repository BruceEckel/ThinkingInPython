# await_coroutine.py
import asyncio
from stateless import Async, Depend, run, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"body of {url}"

def report(url: str) -> Depend[Async, int]:
    body = yield from wait(fetch(url))
    return len(body)

print(run(report("http://example.com")))
#: 26
