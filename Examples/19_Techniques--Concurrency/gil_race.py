# gil_race.py
import time
from concurrent.futures import ThreadPoolExecutor

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        time.sleep(0.000_001)  # Let other threads run
        counter = value + 1  # Write back

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: True
