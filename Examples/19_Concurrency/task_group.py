# task_group.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item == "b":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    pairs = [("a", 0.25), ("b", 0.05), ("c", 0.01)]
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                item: tg.create_task(fetch(item, delay))
                for item, delay in pairs
            }
    except* ValueError as group:
        print(f"caught: {group.exceptions[0]}")
    for item, task in tasks.items():
        if task.cancelled():
            print(f"{item}: cancelled")
        elif (exc := task.exception()) is not None:
            print(f"{item}: raised {exc!r}")
        else:
            print(f"{item}: {task.result()}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: c: fetched
#: caught: fetch('b') failed
#: a: cancelled
#: b: raised ValueError("fetch('b') failed")
#: c: C
