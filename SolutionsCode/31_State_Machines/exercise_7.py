# exercise_7.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class ElevatorState(Enum):
    IDLE = auto()
    MOVING_UP = auto()
    MOVING_DOWN = auto()
    DOORS_OPEN = auto()

class CallButton:
    def __init__(self, floor: int) -> None:
        self.floor = floor

class ArrivedAtFloor:
    pass
class DoorsClosed:
    pass

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
                (None, self.open_doors, ElevatorState.DOORS_OPEN),
            ],
            (ElevatorState.MOVING_UP, ArrivedAtFloor):
                [(None, self.open_doors, ElevatorState.DOORS_OPEN)],
            (ElevatorState.MOVING_DOWN, ArrivedAtFloor):
                [(None, self.open_doors, ElevatorState.DOORS_OPEN)],
            (ElevatorState.DOORS_OPEN, DoorsClosed):
                [(None, None, ElevatorState.IDLE)],
        }
        super().__init__(ElevatorState.IDLE, table)

    def above(self, call: CallButton) -> bool:
        return call.floor > self.floor

    def below(self, call: CallButton) -> bool:
        return call.floor < self.floor

    def set_target(self, call: CallButton) -> None:
        self.target = call.floor

    def open_doors(self, event: object) -> None:
        self.floor = self.target

elevator = Elevator(floor=0)
elevator.handle(CallButton(3))
print(elevator.state, elevator.floor)
#: ElevatorState.MOVING_UP 0
elevator.handle(ArrivedAtFloor())
print(elevator.state, elevator.floor)
#: ElevatorState.DOORS_OPEN 3
