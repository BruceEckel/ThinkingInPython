# shared_generator.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Final

LIMIT: Final[int] = 200

def numbers(limit: int) -> Iterator[int]:
    for n in range(limit):
        time.sleep(0.000_001)  # Let other threads run
        yield n

guarded = threading.synchronized_iterator(numbers)

def outcome(source: Iterator[int]) -> str:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(list, source)
                   for _ in range(8)]
    failed = sum(f.exception() is not None for f in futures)
    taken = sum(len(f.result()) for f in futures
                if f.exception() is None)
    return f"{taken} taken, any thread failed: {failed > 0}"

print("plain:      ", outcome(numbers(LIMIT)))
#: plain:       200 taken, any thread failed: True
print("synchronized:", outcome(guarded(LIMIT)))
#: synchronized: 200 taken, any thread failed: False
