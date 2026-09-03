# pool_contention.py
import threading
from object_pool import Connection, Pool

WORKERS = 8
ROUNDS = 200
pool = Pool(Connection(1), Connection(2))
lock = threading.Lock()
held = 0
over_capacity = False

def borrow() -> None:
    global held, over_capacity
    for _ in range(ROUNDS):
        with pool.lease():
            with lock:
                held += 1
                if held > 2:
                    over_capacity = True
            with lock:
                held -= 1

workers = [threading.Thread(target=borrow)
           for _ in range(WORKERS)]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()
print("over capacity:", over_capacity)
print("pool size after:", pool.available())
#: over capacity: False
#: pool size after: 2
