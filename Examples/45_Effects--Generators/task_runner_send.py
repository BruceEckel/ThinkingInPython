# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable
from typing import Final

type Request = str
type Reply = str
type Job = Generator[Request, Reply]

REPLIES: Final[dict[Request, Reply]] = {
    "download: headers?": "200 OK, 512 bytes",
}

def answer(request: Request) -> Reply:
    return REPLIES.get(request, "ok")

def download() -> Job:
    reply: Reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Job:
    yield "index: build"
    yield "index: merge"

def task_runner(jobs: Iterable[Job]) -> None:
    ready: deque[tuple[Job, Request]] = deque()
    for job in jobs:
        try:
            ready.append((job, next(job)))
        except StopIteration:
            pass
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
