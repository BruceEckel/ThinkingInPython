# exercise_1.py
from __future__ import annotations

class RealConnection:
    def __init__(self, number: int) -> None:
        self.number = number

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

class ConnectionManager:
    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._in_use = 0
        self._next_number = 1

    def checkout(self) -> ConnectionProxy:
        if self._in_use >= self._limit:
            raise RuntimeError("no connections available")
        self._in_use += 1
        conn = RealConnection(self._next_number)
        self._next_number += 1
        return ConnectionProxy(conn, self)

    def _check_in(self) -> None:
        self._in_use -= 1

class ConnectionProxy:
    def __init__(self, real: RealConnection,
                 manager: ConnectionManager) -> None:
        self._real = real
        self._manager = manager
        self._checked_in = False

    def query(self, sql: str) -> str:
        if self._checked_in:
            raise RuntimeError("connection already checked in")
        return self._real.query(sql)

    def check_in(self) -> None:
        if not self._checked_in:
            self._checked_in = True
            self._manager._check_in()

manager = ConnectionManager(limit=2)
c1 = manager.checkout()
c2 = manager.checkout()
try:
    manager.checkout()
except RuntimeError as e:
    print("caught:", e)
#: caught: no connections available
c1.check_in()
c3 = manager.checkout()  # Succeeds: c1's slot was released
print(c3.query("SELECT 2"))
#: connection 3: SELECT 2
