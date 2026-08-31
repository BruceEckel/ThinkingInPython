# exercise_6.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()
    DOORS_CLOSING = auto()

@dataclass
class CallButton:
    floor: int

class ArrivedAtFloor:
    pass
class CloseDoors:
    pass

@dataclass
class DoorSensor:
    blocked: bool

class Elevator(StateMachine):
    def __init__(self, floor: int = 0) -> None:
        self.floor = floor
        self.target = floor
        table: Table = {
            (ElevatorState.IDLE, CallButton): [
                (self.above, self.set_target,
                 ElevatorState.MOVING_UP),
                (self.below, self.set_target,
                 ElevatorState.MOVING_DOWN),
                (None, None, ElevatorState.DOORS_OPEN),
            ],
            (ElevatorState.MOVING_UP, ArrivedAtFloor):
                [(None, self.arrive,
                  ElevatorState.DOORS_OPEN)],
            (ElevatorState.MOVING_DOWN, ArrivedAtFloor):
                [(None, self.arrive,
                  ElevatorState.DOORS_OPEN)],
            (ElevatorState.DOORS_OPEN, CloseDoors):
                [(None, None, ElevatorState.DOORS_CLOSING)],
            (ElevatorState.DOORS_CLOSING, DoorSensor): [
                (self.obstructed, None,
                 ElevatorState.DOORS_OPEN),
                (None, None, ElevatorState.IDLE),
            ],
        }
        super().__init__(ElevatorState.IDLE, table)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def arrive(self, event: object) -> None:
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
