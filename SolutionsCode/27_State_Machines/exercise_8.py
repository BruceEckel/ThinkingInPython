# exercise_8.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class HVACState(Enum):
    OFF = auto()
    HEATING = auto()
    COOLING = auto()

class TooCold:
    pass
class TooHot:
    pass
class AtTarget:
    pass
class TurnOff:
    pass

class HVAC(StateMachine):
    def __init__(self) -> None:
        table: Table = {
            (HVACState.OFF, TooCold):
                [(None, None, HVACState.HEATING)],
            (HVACState.OFF, TooHot):
                [(None, None, HVACState.COOLING)],
            (HVACState.HEATING, AtTarget):
                [(None, None, HVACState.OFF)],
            (HVACState.COOLING, AtTarget):
                [(None, None, HVACState.OFF)],
            (HVACState.HEATING, TurnOff):
                [(None, None, HVACState.OFF)],
            (HVACState.COOLING, TurnOff):
                [(None, None, HVACState.OFF)],
        }
        super().__init__(HVACState.OFF, table)

hvac = HVAC()
hvac.handle(TooCold())
print(hvac.state)
#: HVACState.HEATING
hvac.handle(AtTarget())
print(hvac.state)
#: HVACState.OFF
