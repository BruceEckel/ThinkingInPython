# exercise_2.py
from collections.abc import Callable
from typing import Any

class Observable:
    def __init__(self) -> None:
        self._observers: list[Callable] = []

    def subscribe(self, observer: Callable) -> None:
        self._observers.append(observer)

    def notify(self, *args: Any) -> None:
        for obs in self._observers:
            obs(*args)

calls: list[tuple[str, int]] = []
observable = Observable()
observable.subscribe(lambda v: calls.append(("A", v)))
observable.subscribe(lambda v: calls.append(("B", v)))
observable.notify(42)
print(calls)
#: [('A', 42), ('B', 42)]
