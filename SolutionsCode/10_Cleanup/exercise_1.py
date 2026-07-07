# exercise_1.py
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

counters = {}
for name in ["First", "Second", "Third"]:
    counters[name] = Counter(name)

print(Counter.live_count())
#: 3
del counters["Third"]
print(Counter.live_count())
#: 2
del counters["Second"]
print(Counter.live_count())
#: 1
counters.clear()
print(Counter.live_count())
#: 0
