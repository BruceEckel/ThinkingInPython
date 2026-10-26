# task_runner.py
from collections import deque
from collections.abc import Iterator

def download() -> Iterator[str]:
    for part in ("headers", "body", "checksum"):
        yield f"download: {part}"

def index() -> Iterator[str]:
    yield "index: build"
    yield "index: merge"

def task_runner(jobs: deque[Iterator[str]]) -> None:
    while jobs:
        job = jobs.popleft()
        try:
            print(next(job))
        except StopIteration:
            continue
        jobs.append(job)

task_runner(deque([download(), index()]))
#: download: headers
#: index: build
#: download: body
#: index: merge
#: download: checksum
