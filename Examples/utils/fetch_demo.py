# utils/fetch_demo.py
import asyncio
from typing import Final

PAIRS: Final[list[tuple[str, float]]] = [
    ("a", 0.01),
    ("b", 0.02),
    ("c", 0.03),
    ("d", 0.03),
    ("e", 0.2),
    ("f", 0.3),
]

async def sleep_until(when: float) -> None:
    loop = asyncio.get_running_loop()
    woken: asyncio.Future[None] = loop.create_future()
    timer = loop.call_at(when, woken.set_result, None)
    try:
        await woken
    finally:
        timer.cancel()

async def fetch(item: str, delay: float, t0: float) -> str:
    print(f"{item}: started")
    await sleep_until(t0 + delay)
    if item in ("c", "d"):
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()
