# exercise_9.py
import asyncio
from stateless import Async, Depend, run, run_async, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched {url}"

def report(url: str) -> Depend[Async, str]:
    body = yield from wait(fetch(url))
    return f"{body = }, {len(body) = }"

def report_all(urls: list[str]) -> Depend[Async, list[str]]:
    reports: list[str] = []
    for url in urls:
        reports.append((yield from report(url)))
    return reports

async def main() -> None:
    try:
        run(report_all(["a"]))
    except RuntimeError as e:
        print("run():", e)
    for line in await run_async(report_all(["a", "b", "c"])):
        print(line)

asyncio.run(main())
#: run(): asyncio.run() cannot be called from a running event loop
#: body = 'fetched a', len(body) = 9
#: body = 'fetched b', len(body) = 9
#: body = 'fetched c', len(body) = 9
