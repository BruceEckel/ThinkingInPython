# broadcaster.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def subscribe(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def unsubscribe(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)

class Thermometer(Broadcaster[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.announce(value)
