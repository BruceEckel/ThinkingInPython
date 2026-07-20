# utils/fetch_demo.py
import asyncio

PAIRS = [
    ("a", 0.01),
    ("b", 0.02),
    ("c", 0.03),
    ("d", 0.2),
    ("e", 0.3),
]

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item == "c":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()
