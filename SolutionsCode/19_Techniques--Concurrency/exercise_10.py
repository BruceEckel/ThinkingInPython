# exercise_10.py
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

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item in ("c", "d"):
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    try:
        results = await asyncio.gather(
            *(fetch(item, delay) for item, delay in PAIRS),
        )
    except ValueError as e:
        print(f"gather raised {e!r}")
        return
    print(results)

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: f: started
#: a: fetched
#: b: fetched
#: gather raised ValueError("fetch('c') failed")
