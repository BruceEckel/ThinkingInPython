# weather_station.py
from collections.abc import Callable

type AttrResponder = Callable[[str, object], None]

class WeatherStation:
    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        self.celsius = celsius
        self.humidity = humidity

    @property
    def _responders(self) -> list[AttrResponder]:
        return self.__dict__.setdefault("_responders", [])

    def connect(self, responder: AttrResponder) -> None:
        self._responders.append(responder)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        responders = list(self._responders)
        super().__setattr__(name, value)
        for responder in responders:
            responder(name, value)

station = WeatherStation(20.0, 0.4)
changes: list[tuple[str, object]] = []
station.connect(lambda n, v: changes.append((n, v)))
station.celsius = 25.0
station.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
