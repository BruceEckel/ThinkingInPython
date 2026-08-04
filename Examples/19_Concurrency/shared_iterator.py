# shared_iterator.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Final

LIMIT: Final[int] = 200

class Tickets:
    "Hands out each number once: read, pause, write back."
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.next_number = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        if self.next_number >= self.limit:
            raise StopIteration
        current = self.next_number
        time.sleep(0.000_001)  # Let other threads run
        self.next_number = current + 1
        return current

def report(label: str, source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(list, source) for _ in range(8)]
        taken = [n for f in futures for n in f.result()]
    print(f"{label}: {len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

report("shared", Tickets(LIMIT))
#: shared: 200 distinct, duplicates True
report("serialized",
       threading.serialize_iterator(Tickets(LIMIT)))
#: serialized: 200 distinct, duplicates False
