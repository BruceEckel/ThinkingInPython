# exercise_5.py
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> object | None: ...
    def set(self, key: str, value: object) -> None: ...

class NullCache:
    def get(self, key: str) -> object | None:
        return None

    def set(self, key: str, value: object) -> None:
        pass

nc = NullCache()
nc.set("a", 1)
print(nc.get("a"))
#: None
