# task_runner.py
from collections import deque
from collections.abc import Callable, Iterator

type Job = Callable[[], Iterator[str]]

ready: deque[Iterator[str]] = deque()

def task(fn: Job) -> Job:
    ready.append(fn())
    return fn

@task
def download() -> Iterator[str]:
    for part in ("headers", "body", "checksum"):
        yield f"download: {part}"

@task
def index() -> Iterator[str]:
    yield "index: build"
    yield "index: merge"

def task_runner() -> None:
    while ready:
        job = ready.popleft()
        try:
            print(next(job))
        except StopIteration:
            continue  # Finished: never requeued
        ready.append(job)

task_runner()
#: download: headers
#: index: build
#: download: body
#: index: merge
#: download: checksum
