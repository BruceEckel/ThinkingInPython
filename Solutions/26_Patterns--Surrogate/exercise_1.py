# exercise_1.py
from typing import Any

class Expensive:
    def __init__(self) -> None:
        print("Expensive built")

    def query(self) -> str:
        return "result"

class Lazy:
    def __init__(self, description: str) -> None:
        self._description = description
        self._answered = 0
        self._real: Expensive | None = None

    @property
    def description(self) -> str:
        self._answered += 1
        return self._description

    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            print(f"{self._answered} answered before build")
            self._real = Expensive()
        return getattr(self._real, name)

p = Lazy("a slow query")
for _ in range(3):
    print(p.description)
#: a slow query
#: a slow query
#: a slow query
print(p.query())  # [1]
#: 3 answered before build
#: Expensive built
#: result
print(p.query())  # [2]
#: result
