# broadcaster.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def disconnect(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
