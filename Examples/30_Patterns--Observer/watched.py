# watched.py
from collections.abc import Callable

type AttrResponder = Callable[[str, object], None]

class Watched:
    _responders: list[AttrResponder]  # Bare annotation

    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        # __setattr__() reads _responders before it
        # stores, so no assignment can create it
        self.__dict__["_responders"] = []
        self.celsius = celsius
        self.humidity = humidity

    def connect(self, responder: AttrResponder) -> None:
        self._responders.append(responder)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        responders = list(self._responders)
        super().__setattr__(name, value)
        for responder in responders:
            responder(name, value)

w = Watched(20.0, 0.4)
changes: list[tuple[str, object]] = []
w.connect(lambda n, v: changes.append((n, v)))
w.celsius = 25.0
w.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
