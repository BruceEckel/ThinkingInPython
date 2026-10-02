# exercise_7.py
from concurrent.futures import ThreadPoolExecutor

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        # Write back, with nothing in between
        counter = value + 1

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: False
