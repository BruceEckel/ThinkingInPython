# priority_queue.py
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue

type Job = tuple[int, str]  # (priority, description)

tasks: PriorityQueue[Job] = PriorityQueue()

def enqueue(jobs: list[Job]) -> None:
    for job in jobs:
        tasks.put(job)

with ThreadPoolExecutor(max_workers=2) as pool:
    pool.submit(enqueue, [(3, "backup"), (1, "page oncall")])
    pool.submit(enqueue, [(2, "rotate logs"), (1, "alert")])

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (2, 'rotate logs')
#: (3, 'backup')
