# exercise_1.py
from typing import Any

class ExpensiveResource:
    def __init__(self) -> None:
        print("creating ExpensiveResource (slow!)")
        self.data = [1, 2, 3]

    def query(self) -> list[int]:
        return self.data

class LazyProxy:
    def __init__(self, description: str) -> None:
        self._description = description
        self._answered = 0
        self._real: ExpensiveResource | None = None

    @property
    def description(self) -> str:
        self._answered += 1
        return self._description

    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            print(f"{self._answered} answered before build")
            self._real = ExpensiveResource()
        return getattr(self._real, name)

p = LazyProxy("three small integers")
for _ in range(3):
    print(p.description)
#: three small integers
#: three small integers
#: three small integers
print(p.query())
#: 3 answered before build
#: creating ExpensiveResource (slow!)
#: [1, 2, 3]
print(p.query())
#: [1, 2, 3]
