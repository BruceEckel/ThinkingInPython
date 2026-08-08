# exercise_5.py
from typing import Any, Final, Self

POOL_SIZE: Final[int] = 2

class PoolExhausted(RuntimeError):
    "No connection is free."

class Connection:
    def __init__(self, number: int) -> None:
        self.number = number

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

class Pool:
    def __init__(self, size: int) -> None:
        self._size = size
        self._free = [Connection(n) for n in range(size)]

    def available(self) -> int:
        return len(self._free)

    def acquire(self) -> ConnectionProxy:
        if not self._free:
            raise PoolExhausted(f"all {self._size} in use")
        return ConnectionProxy(self, self._free.pop(0))

    def release(self, connection: Connection) -> None:
        self._free.append(connection)

class ConnectionProxy:
    def __init__(self, pool: Pool, connection: Connection) -> None:
        self._pool = pool
        self._connection: Connection | None = connection

    def __getattr__(self, name: str) -> Any:
        if self._connection is None:
            raise RuntimeError("connection already released")
        return getattr(self._connection, name)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exception: object) -> None:
        if self._connection is not None:
            self._pool.release(self._connection)
            self._connection = None

pool = Pool(POOL_SIZE)
with pool.acquire() as c1:
    print(c1.query("select 1"))
    with pool.acquire() as c2:
        print(c2.query("select 2"))
        try:
            pool.acquire()
        except PoolExhausted as e:
            print(type(e).__name__, e, pool.available())
    print("inner released:", pool.available())
print("outer released:", pool.available())
#: connection 0: select 1
#: connection 1: select 2
#: PoolExhausted all 2 in use 0
#: inner released: 1
#: outer released: 2
