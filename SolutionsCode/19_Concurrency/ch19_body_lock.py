# ch19_body_lock.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Final

LIMIT: Final[int] = 200
lock = threading.Lock()

@dataclass
class Tickets:
    limit: int
    next_number: int = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        if self.next_number >= self.limit:
            raise StopIteration
        current = self.next_number
        time.sleep(0.000_001)  # Let other threads run
        self.next_number = current + 1
        return current

def drain(source: Iterator[int]) -> list[int]:
    out: list[int] = []
    for item in source:  # next() runs here, unguarded
        with lock:
            out.append(item)  # Only the body is protected
    return out

def report(source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(drain, source)
                   for _ in range(8)]
        taken = [*f.result() for f in futures]
    print(f"{len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

report(Tickets(LIMIT))
#: 200 distinct, duplicates True
