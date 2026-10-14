# task_group.py
import asyncio
from fetch_demo import FETCHES, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                job.item: tg.create_task(fetch(job, t0))
                for job in FETCHES
            }
    except* ValueError as group:
        for exc in group.exceptions:
            print(f"caught: {exc}")
    for item, task in tasks.items():
        if task.cancelled():
            print(f"{item}: cancelled")
        elif (exc := task.exception()) is not None:
            print(f"{item}: raised {exc!r}")
        else:
            print(f"{item}: {task.result()}")

asyncio.run(main())
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: caught: fetch('d') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: cancelled
#: f: cancelled
