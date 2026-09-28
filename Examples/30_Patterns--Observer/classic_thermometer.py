# classic_thermometer.py
from classic_observer import Subject

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    def set_celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)
