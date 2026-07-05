# priority_queue.py
import threading
from queue import PriorityQueue

tasks: PriorityQueue[tuple[int, str]] = PriorityQueue()

def submit(jobs: list[tuple[int, str]]) -> None:
    for job in jobs:
        tasks.put(job)

threads = [
    threading.Thread(
        target=submit,
        args=([(3, "backup"), (1, "page oncall")],),
    ),
    threading.Thread(
        target=submit,
        args=([(2, "rotate logs"), (1, "alert")],),
    ),
]
for t in threads:
    t.start()
for t in threads:
    t.join()

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (2, 'rotate logs')
#: (3, 'backup')
