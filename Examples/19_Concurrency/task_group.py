# task_group.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                item: tg.create_task(fetch(item, delay))
                for item, delay in PAIRS
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
#: d: started
#: e: started
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: cancelled
#: e: cancelled
