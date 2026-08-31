# exercise_2.py
from dataclasses import dataclass
from functools import cache

@dataclass(frozen=True)
class Connection:
    number: int

class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._all = [Connection(i) for i in range(size)]
        self._available = list(self._all)
        self._leased: set[Connection] = set()

    def acquire(self) -> Connection:
        if not self._available:
            raise RuntimeError("pool exhausted")
        conn = self._available.pop()
        self._leased.add(conn)
        return conn

    def release(self, conn: Connection) -> None:
        self._leased.discard(conn)
        self._available.append(conn)

@cache
def pool() -> ConnectionPool:
    "Always returns the same ConnectionPool instance."
    return ConnectionPool(size=2)

p1 = pool()
p2 = pool()
print(p1 is p2)
#: True
c1 = p1.acquire()
c2 = p1.acquire()
print(c1 != c2)
#: True
try:
    p1.acquire()
except RuntimeError as e:
    print("caught:", e)
#: caught: pool exhausted
p1.release(c1)
c3 = p1.acquire()
print(c3 == c1)
#: True
