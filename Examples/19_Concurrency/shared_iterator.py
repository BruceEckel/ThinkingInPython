# shared_iterator.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Final

LIMIT: Final[int] = 200

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

def report(label: str, source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(list, source) for _ in range(8)]
        taken = [*f.result() for f in futures]
    print(f"{label}: {len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

report("shared", Tickets(LIMIT))
#: shared: 200 distinct, duplicates True
report("serialized",
       threading.serialize_iterator(Tickets(LIMIT)))
#: serialized: 200 distinct, duplicates False
