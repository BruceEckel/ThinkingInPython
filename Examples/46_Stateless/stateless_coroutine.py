# stateless_coroutine.py
import asyncio
from stateless import Async, Depend, run, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched {url}"

def report(url: str) -> Depend[Async, str]:
    body = yield from wait(fetch(url))
    return f"{body = }, {len(body) = }"

print(run(report("http://example.com")))
#: body = 'fetched http://example.com', len(body) = 26
