# task_group.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    await asyncio.sleep(delay)
    if item == "b":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    pairs = [("a", 0.25), ("b", 0.05), ("c", 0.01)]
    try:
        async with asyncio.TaskGroup() as tg:
            for item, delay in pairs:
                tg.create_task(fetch(item, delay))
    except* ValueError as group:
        print(f"caught: {group.exceptions[0]}")

asyncio.run(main())
#: c: fetched
#: caught: fetch('b') failed
