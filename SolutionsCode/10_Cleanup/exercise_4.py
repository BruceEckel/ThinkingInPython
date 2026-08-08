# exercise_4.py
from typing import ClassVar

class Counter:
    _instances: ClassVar[dict[int, Counter]] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = [Counter(name) for name in ("First", "Second", "Third")]
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.clear()
print(Counter.live_count())
#: 3
