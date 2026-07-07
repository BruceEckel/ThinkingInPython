# exercise_1.py
from typing import Any

class ExpensiveResource:
    def __init__(self) -> None:
        print("creating ExpensiveResource (slow!)")
        self.data = [1, 2, 3]

    def query(self) -> list:
        return self.data

class LazyProxy:
    def __init__(self) -> None:
        self._real: ExpensiveResource | None = None

    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            self._real = ExpensiveResource()
        return getattr(self._real, name)

print("proxy created, nothing built yet")
p = LazyProxy()
print("about to query")
print(p.query())
#: proxy created, nothing built yet
#: about to query
#: creating ExpensiveResource (slow!)
#: [1, 2, 3]
