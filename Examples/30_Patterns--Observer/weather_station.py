# weather_station.py
from broadcaster import Responder

type Change = tuple[str, object]

class WeatherStation:
    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        self.celsius = celsius
        self.humidity = humidity

    @property
    def _responders(self) -> list[Responder[Change]]:
        return self.__dict__.setdefault("_responders", [])

    def connect(self, responder: Responder[Change]) -> None:
        self._responders.append(responder)

    def disconnect(
        self, responder: Responder[Change]
    ) -> None:
        self._responders.remove(responder)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        responders = list(self._responders)
        super().__setattr__(name, value)
        for responder in responders:
            responder((name, value))

station = WeatherStation(20.0, 0.4)
changes: list[Change] = []
station.connect(changes.append)
station.celsius = 25.0
station.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
