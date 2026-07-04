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

if __name__ == "__main__":
    pool = Pool(Connection(1), Connection(2))
    with pool.lease() as conn:
        print(conn.query("SELECT name FROM users"))
        print("available during lease:", pool.available())
    print("available after lease:", pool.available())
    try:
        with pool.lease() as conn:
            raise RuntimeError("crash during query")
    except RuntimeError:
        pass
    print("available after crash:", pool.available())
#: connection 1: SELECT name FROM users
#: available during lease: 1
#: available after lease: 2
#: available after crash: 2
