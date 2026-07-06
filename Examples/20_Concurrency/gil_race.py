# gil_race.py
import threading
import time

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        time.sleep(0.000_001)  # Let other threads run
        counter = value + 1  # Write back

threads = [
    threading.Thread(target=increment, args=(50,))
    for _ in range(8)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: True
