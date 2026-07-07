# exercise_5.py
import threading
from queue import PriorityQueue

tasks: PriorityQueue = PriorityQueue()

def submit(jobs):
    for job in jobs:
        tasks.put(job)

threads = [
    threading.Thread(
        target=submit,
        args=([(3, "backup"), (1, "page oncall")],)),
    threading.Thread(
        target=submit,
        args=([(2, "rotate logs"), (1, "alert")],)),
    threading.Thread(
        target=submit,
        args=([(1, "zzz"), (3, "aaa")],)),
]
for t in threads:
    t.start()
for t in threads:
    t.join()

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (1, 'zzz')
#: (2, 'rotate logs')
#: (3, 'aaa')
#: (3, 'backup')
