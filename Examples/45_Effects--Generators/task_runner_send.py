# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable
from typing import Final

REPLIES: Final[dict[str, str]] = {
    "download: headers?": "200 OK, 512 bytes",
}

def answer(request: str) -> str:
    return REPLIES.get(request, "ok")

def download() -> Generator[str, str]:
    reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Generator[str, str]:
    # Each yield receives the runner's str and discards it
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
#: download: 200 OK, 512 bytes
#: index: build
#: download: checksum
#: index: merge
