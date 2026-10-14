# exercise_9.py
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
    Fetch("e", 0.005),  # Was 0.2, so e now finishes first
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
#: e: fetched
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: caught: fetch('d') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: E
#: f: cancelled
