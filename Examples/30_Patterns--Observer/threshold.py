# threshold.py
from broadcaster import Broadcaster

class ThresholdThermometer(Broadcaster[float]):
    def __init__(
        self, celsius: float, delta: float
    ) -> None:
        super().__init__()
        self._celsius = celsius
        self._delta = delta

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        change = abs(value - self._celsius)
        self._celsius = value
        if change >= self._delta:
            self.announce(value)

def display(celsius: float) -> None:
    print(f"display: {celsius}C")

log: list[float] = []
t = ThresholdThermometer(20.0, 0.5)
t.subscribe(log.append)
t.subscribe(display)
for reading in [20.2, 20.9, 21.0, 22.0]:
    t.celsius = reading
#: display: 20.9C
#: display: 22.0C
print(log)
#: [20.9, 22.0]
