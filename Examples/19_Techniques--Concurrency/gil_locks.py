# gil_locks.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor

counter = 0
lock = threading.Lock()

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        with lock:
            value = counter  # Read
            time.sleep(0.000_001)  # Let others run
            counter = value + 1  # Write back

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lock preserves every update: "
      f"{counter == 8 * 50}")
#: lock preserves every update: True
