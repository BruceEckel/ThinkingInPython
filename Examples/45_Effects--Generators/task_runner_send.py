# task_runner_send.py
from collections import deque
from collections.abc import Callable, Generator

type Job = Callable[[], Generator[str, str]]

ready: deque[Generator[str, str]] = deque()
to_send: dict[Generator[str, str], str | None] = {}

def task(fn: Job) -> Job:
    job = fn()
    ready.append(job)
    to_send[job] = None
    return fn

def answer(request: str) -> str:
    return f"answer to {request}"

@task
def download() -> Generator[str, str]:
    reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

@task
def index() -> Generator[str, str]:
    yield "index: build"
    yield "index: merge"

def task_runner() -> None:
    while ready:
        job = ready.popleft()
        try:
            request = job.send(to_send.pop(job))  # type: ignore
        except StopIteration:
            continue
        print(request)
        to_send[job] = answer(request)
        ready.append(job)

task_runner()
#: download: headers?
#: index: build
#: download: answer to download: headers?
#: download: checksum
#: index: merge
