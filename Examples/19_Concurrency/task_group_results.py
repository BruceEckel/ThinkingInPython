# task_group_results.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return item.upper()

async def main() -> None:
    pairs = [("a", 0.03), ("b", 0.02), ("c", 0.01)]
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(i, d)) for i, d in pairs]
    print([t.result() for t in tasks])

asyncio.run(main())
#: ['A', 'B', 'C']
