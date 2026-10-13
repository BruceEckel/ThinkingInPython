# pool_contention.py
import threading
import time
from typing import Final
from object_pool import Connection, Pool

WORKERS: Final[int] = 8
ROUNDS: Final[int] = 200
pool = Pool(Connection(1), Connection(2))
lock = threading.Lock()
held = 0
peak = 0

def borrow() -> None:
    global held, peak
    for _ in range(ROUNDS):
        with pool.lease():
            with lock:
                held += 1
                peak = max(peak, held)
            time.sleep(0.000_001)
            with lock:
                held -= 1

workers = [threading.Thread(target=borrow)
           for _ in range(WORKERS)]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()
print("peak leases:", peak)
#: peak leases: 2
print("pool size after:", pool.available())
#: pool size after: 2
