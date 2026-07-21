# semaphore_limit.py
import threading
import time

active = 0
peak = 0
lock = threading.Lock()
pool = threading.Semaphore(2)  # At most 2 workers at once

def worker() -> None:
    global active, peak
    with pool:
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.05)
        with lock:
            active -= 1

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"peak concurrent workers: {peak}")
#: peak concurrent workers: 2
