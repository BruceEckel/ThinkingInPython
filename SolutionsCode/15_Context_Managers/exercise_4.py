# exercise_4.py
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Queue

@dataclass(frozen=True)
class Connection:
    number: int

class Pool[R]:
    def __init__(self, *items: R) -> None:
        self._available: Queue[R] = Queue()
        for item in items:
            self._available.put(item)

    @contextmanager
    def lease(self) -> Iterator[R]:
        item = self._available.get()
        try:
            yield item
        finally:
            self._available.put(item)

    def available(self) -> int:
        return self._available.qsize()

pool = Pool(Connection(1), Connection(2))
with pool.lease() as c1:
    with pool.lease() as c2:
        print("available while both leased:", pool.available())
print("available after both returned:", pool.available())
#: available while both leased: 0
#: available after both returned: 2
