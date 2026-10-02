# exercise_8.py
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, ShutDown

type Job = tuple[int, str]  # (priority, description)

tasks: PriorityQueue[Job] = PriorityQueue()

def enqueue(jobs: list[Job]) -> None:
    for job in jobs:
        tasks.put(job)

def consume() -> None:
    while True:
        try:
            print(tasks.get())
        except ShutDown:
            return

with ThreadPoolExecutor(max_workers=4) as pool:
    producers = [
        pool.submit(enqueue,
                    [(3, "backup"), (1, "page oncall")]),
        pool.submit(enqueue,
                    [(2, "rotate logs"), (1, "alert")]),
        pool.submit(enqueue,  # The third producer
                    [(1, "zzz"), (3, "aaa")]),
    ]
    for p in producers:
        p.result()  # Surface any producer failure
    consumer = pool.submit(consume)
    tasks.shutdown()
    consumer.result()
#: (1, 'alert')
#: (1, 'page oncall')
#: (1, 'zzz')
#: (2, 'rotate logs')
#: (3, 'aaa')
#: (3, 'backup')
