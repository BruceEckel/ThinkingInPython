# concurrent_tee.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Final

READERS: Final[int] = 4

def numbers(limit: int) -> Iterator[int]:
    for n in range(limit):
        time.sleep(0.000_001)  # Let other threads run
        yield n

streams = threading.concurrent_tee(numbers(100), READERS)
with ThreadPoolExecutor(max_workers=READERS) as pool:
    print(list(pool.map(sum, streams)))
#: [4950, 4950, 4950, 4950]
