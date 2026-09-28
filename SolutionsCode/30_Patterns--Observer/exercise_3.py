# exercise_3.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def subscribe(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        failures: list[Exception] = []
        for responder in list(self._responders):
            try:
                responder(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "responder failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

broadcaster = Broadcaster[int]()
broadcaster.subscribe(broken)
broadcaster.subscribe(received.append)
try:
    broadcaster.announce(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
