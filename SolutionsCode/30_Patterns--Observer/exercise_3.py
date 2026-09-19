# exercise_3.py
from collections.abc import Callable

type Listener[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def announce(self, data: T) -> None:
        failures: list[Exception] = []
        for listener in list(self._listeners):
            try:
                listener(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "listener failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

source = Broadcaster[int]()
source.subscribe(broken)
source.subscribe(received.append)
try:
    source.announce(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
