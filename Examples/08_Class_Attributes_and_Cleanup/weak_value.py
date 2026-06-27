# weak_value.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[WeakValueDictionary[int, Counter]] = (
        WeakValueDictionary())

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

print(Counter.live_count())
#: First deleted
#: 2 Counter objects remaining
#: Second deleted
#: 1 Counter objects remaining
#: Third deleted
#: Last Counter object deleted
#: 3
counters.pop()               # Release "Third"
print(Counter.live_count())
#: 2
counters.pop()               # Release "Second"
print(Counter.live_count())
#: 1
counters.clear()             # Release "First"
print(Counter.live_count())
#: 0
