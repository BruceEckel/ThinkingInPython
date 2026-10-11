# exercise_1.py
from collections.abc import Callable

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Callable[[T], None]] = []

    def connect(
        self, responder: Callable[[T], None]
    ) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        for responder in self._responders:
            responder(data)

calls: list[tuple[str, int]] = []
broadcaster = Broadcaster[int]()
broadcaster.connect(lambda v: calls.append(("A", v)))
broadcaster.connect(lambda v: calls.append(("B", v)))
broadcaster.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
