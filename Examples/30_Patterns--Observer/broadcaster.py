# broadcaster.py
from collections.abc import Callable

type Listener[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Listener[T]) -> None:
        self._listeners.remove(listener)

    def announce(self, data: T) -> None:
        for listener in list(self._listeners):
            listener(data)

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
