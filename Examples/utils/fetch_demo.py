# utils/fetch_demo.py
import asyncio
from typing import Final
from record import record

@record
class Fetch:
    item: str
    delay: float
    fails: bool = False

FETCHES: Final[list[Fetch]] = [
    Fetch("a", 0.01),
    Fetch("b", 0.02),
    Fetch("c", 0.03, fails=True),
    Fetch("d", 0.03, fails=True),
    Fetch("e", 0.2),
    Fetch("f", 0.3),
]

async def sleep_until(when: float) -> None:
    loop = asyncio.get_running_loop()
    woken: asyncio.Future[None] = loop.create_future()
    timer = loop.call_at(when, woken.set_result, None)
    try:
        await woken
    finally:
        timer.cancel()

async def fetch(job: Fetch, t0: float) -> str:
    await sleep_until(t0 + job.delay)
    if job.fails:
        raise ValueError(f"fetch({job.item!r}) failed")
    print(f"{job.item}: fetched")
    return job.item.upper()
