# object_pool.py
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Queue

@dataclass(frozen=True)
class Connection:
    number: int

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

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
