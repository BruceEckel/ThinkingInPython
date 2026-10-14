# exercise_10.py
import asyncio
from fetch_demo import FETCHES, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        results = await asyncio.gather(*(
            fetch(job, t0) for job in FETCHES))
    except ValueError as e:
        print(f"gather raised {e!r}")
        return
    print(results)

asyncio.run(main())
#: a: fetched
#: b: fetched
#: gather raised ValueError("fetch('c') failed")
