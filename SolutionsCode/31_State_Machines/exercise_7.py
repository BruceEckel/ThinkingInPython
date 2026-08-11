# exercise_7.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@dataclass
class TemperatureReading:
    degrees: float

class HVAC(StateMachine):
    def __init__(self, target: float = 20, band: float = 2) -> None:
        self.target = target
        self.band = band
        table: Table = {
            (HVACState.IDLE, TemperatureReading): [
                (self.too_cold, None, HVACState.HEATING),
                (self.too_hot, None, HVACState.COOLING),
                (None, None, HVACState.IDLE),
            ],
            (HVACState.HEATING, TemperatureReading): [
                (self.too_cold, None, HVACState.HEATING),
                (None, None, HVACState.IDLE),
            ],
            (HVACState.COOLING, TemperatureReading): [
                (self.too_hot, None, HVACState.COOLING),
                (None, None, HVACState.IDLE),
            ],
        }
        super().__init__(HVACState.IDLE, table)

    def too_cold(self, r: TemperatureReading) -> bool:
        return r.degrees < self.target - self.band

    def too_hot(self, r: TemperatureReading) -> bool:
        return r.degrees > self.target + self.band

hvac = HVAC()
for degrees in [15, 17, 21, 30, 20]:
    hvac.handle(TemperatureReading(degrees))
    print(degrees, hvac.state.name)
#: 15 HEATING
#: 17 HEATING
#: 21 IDLE
#: 30 COOLING
#: 20 IDLE
