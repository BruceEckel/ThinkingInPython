# exercise_3.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[WeakValueDictionary[int, Counter]] = (
        WeakValueDictionary())

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_names(cls) -> list[str]:
        return sorted(c.name for c in cls._instances.values())

counters = [Counter(name) for name in ("Charlie", "Alpha", "Bravo")]
print(Counter.live_names())
#: ['Alpha', 'Bravo', 'Charlie']
