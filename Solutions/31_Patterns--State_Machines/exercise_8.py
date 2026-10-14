# exercise_8.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class HVACState(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

@record
class TemperatureReading:
    degrees: float

class HVAC(StateMachine):
    def __init__(self, target: float = 20,
                 band: float = 2) -> None:
        self.target = target
        self.band = band
        rules = [
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.HEATING,
                 condition=self.too_cold),
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.COOLING,
                 condition=self.too_hot),
            Rule(HVACState.IDLE, TemperatureReading,
                 HVACState.IDLE),
            Rule(HVACState.HEATING, TemperatureReading,
                 HVACState.HEATING,
                 condition=self.too_cold),
            Rule(HVACState.HEATING, TemperatureReading,
                 HVACState.IDLE),
            Rule(HVACState.COOLING, TemperatureReading,
                 HVACState.COOLING,
                 condition=self.too_hot),
            Rule(HVACState.COOLING, TemperatureReading,
                 HVACState.IDLE),
        ]
        super().__init__(HVACState.IDLE, rules)

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
