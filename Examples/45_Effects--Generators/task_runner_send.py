# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable

def answer(request: str) -> str:
    return f"answer to {request}"

def download() -> Generator[str, str]:
    reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Generator[str, str]:
    yield "index: build"
    yield "index: merge"

def task_runner(
    jobs: Iterable[Generator[str, str]]
) -> None:
    ready = deque((job, next(job)) for job in jobs)
    while ready:
        job, request = ready.popleft()
        print(request)
        try:
            request = job.send(answer(request))
        except StopIteration:
            continue
        ready.append((job, request))

task_runner([download(), index()])
#: download: headers?
#: download: answer to download: headers?
#: index: build
#: download: checksum
#: index: merge
