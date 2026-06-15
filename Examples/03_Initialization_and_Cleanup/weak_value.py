# weak_value.py
from weakref import WeakValueDictionary


class Counter:
    _instances: WeakValueDictionary[int, "Counter"] = (
        WeakValueDictionary())

    @property
    def Count(self) -> int:
        return len(self._instances)

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self
        print(name, 'created')

    def __del__(self) -> None:
        print(self.name, 'deleted')
        if self.Count == 0:
            print('Last Counter object deleted')
        else:
            print(self.Count, 'Counter objects remaining')


x = Counter("First")
