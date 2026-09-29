# exercise_10.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        results = await asyncio.gather(*(
            fetch(item, delay, t0)
            for item, delay in PAIRS))
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
