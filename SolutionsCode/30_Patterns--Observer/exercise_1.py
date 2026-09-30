# exercise_1.py
from collections.abc import Callable
from typing import Any

class Broadcaster:
    def __init__(self) -> None:
        self._responders: list[Callable] = []

    def connect(self, responder: Callable) -> None:
        self._responders.append(responder)

    def announce(self, *args: Any) -> None:
        for responder in self._responders:
            responder(*args)

calls: list[tuple[str, int]] = []
broadcaster = Broadcaster()
broadcaster.connect(lambda v: calls.append(("A", v)))
broadcaster.connect(lambda v: calls.append(("B", v)))
broadcaster.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
