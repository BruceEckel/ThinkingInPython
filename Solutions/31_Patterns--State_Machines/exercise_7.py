# exercise_7.py
from enum import Enum, auto
from record import record
from table_machine import Rule, StateMachine

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@record
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@record
class DoorSensor:
    blocked: bool

class Elevator(StateMachine):
    def __init__(self, floor: int = 0) -> None:
        self.floor = floor
        self.target = floor
        rules = [
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.MOVING_UP, self.set_target,
                 self.above),
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.MOVING_DOWN, self.set_target,
                 self.below),
            Rule(ElevatorState.IDLE, CallButton,
                 ElevatorState.DOORS_OPEN),
            Rule(ElevatorState.MOVING_UP, ArrivedAtFloor,
                 ElevatorState.DOORS_OPEN, self.arrive),
            Rule(ElevatorState.MOVING_DOWN, ArrivedAtFloor,
                 ElevatorState.DOORS_OPEN, self.arrive),
            Rule(ElevatorState.DOORS_OPEN, CloseDoors,
                 ElevatorState.DOORS_CLOSING),
            Rule(ElevatorState.DOORS_CLOSING, DoorSensor,
                 ElevatorState.DOORS_OPEN,
                 condition=self.obstructed),
            Rule(ElevatorState.DOORS_CLOSING, DoorSensor,
                 ElevatorState.IDLE),
        ]
        super().__init__(ElevatorState.IDLE, rules)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def arrive(self, input_: object) -> None:
        self.floor = self.target

    def obstructed(self, sensor: DoorSensor) -> bool:
        return sensor.blocked

elevator = Elevator(floor=0)
elevator.handle(CallButton(3))
print(elevator.state, elevator.floor)
#: ElevatorState.MOVING_UP 0
elevator.handle(ArrivedAtFloor())
print(elevator.state, elevator.floor)
#: ElevatorState.DOORS_OPEN 3
elevator.handle(CloseDoors())
elevator.handle(DoorSensor(blocked=True))
print(elevator.state)
#: ElevatorState.DOORS_OPEN
elevator.handle(CloseDoors())
elevator.handle(DoorSensor(blocked=False))
print(elevator.state)
#: ElevatorState.IDLE
