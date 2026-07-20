# gather_with_exceptions.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    results = await asyncio.gather(
        *(fetch(item, delay) for item, delay in PAIRS),
        return_exceptions=True,
    )
    for (item, _), result in zip(PAIRS, results):
        match result:
            case BaseException():
                print(f"{item}: raised {result!r}")
            case _:
                print(f"{item}: {result}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: a: fetched
#: b: fetched
#: d: fetched
#: e: fetched
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: D
#: e: E
