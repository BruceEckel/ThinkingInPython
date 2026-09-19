# exercise_1.py
from collections.abc import Callable
from typing import Any

class Broadcaster:
    def __init__(self) -> None:
        self._listeners: list[Callable] = []

    def subscribe(self, listener: Callable) -> None:
        self._listeners.append(listener)

    def announce(self, *args: Any) -> None:
        for listener in self._listeners:
            listener(*args)

calls: list[tuple[str, int]] = []
source = Broadcaster()
source.subscribe(lambda v: calls.append(("A", v)))
source.subscribe(lambda v: calls.append(("B", v)))
source.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
