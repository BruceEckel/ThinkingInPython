# test_ch15_both_leased.py
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

def test_both_leased_at_once() -> None:
    pool = Pool(Connection(1), Connection(2))
    with pool.lease() as first:  # [1]
        with pool.lease() as second:  # [2]
            assert second is not first
            assert pool.available() == 0
    assert pool.available() == 2
