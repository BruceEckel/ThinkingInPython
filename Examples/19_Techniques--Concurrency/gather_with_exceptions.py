# gather_with_exceptions.py
import asyncio
from typing import assert_never
from fetch_demo import FETCHES, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    results = await asyncio.gather(
        *(fetch(job, t0) for job in FETCHES),
        return_exceptions=True,
    )
    for job, result in zip(FETCHES, results):
        match result:
            case BaseException():
                print(f"{job.item}: raised {result!r}")
            case str():
                print(f"{job.item}: {result}")
            case _:
                assert_never(result)

asyncio.run(main())
#: a: fetched
#: b: fetched
#: e: fetched
#: f: fetched
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: E
#: f: F
