# weak_value.py
from weakref import WeakValueDictionary


class Counter:
    _instances: WeakValueDictionary[int, Counter] = (
        WeakValueDictionary())

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)


counters = [Counter(name) for name in ["First", "Second", "Third"]]
print(Counter.live_count())  # 3
counters.pop()               # Release "Third"
print(Counter.live_count())  # 2
counters.pop()               # Release "Second"
print(Counter.live_count())  # 1
counters.clear()             # Release "First"
print(Counter.live_count())  # 0
