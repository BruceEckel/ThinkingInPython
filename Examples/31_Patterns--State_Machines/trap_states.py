# trap_states.py
from typing import ClassVar
from mouse import Mouse
from state import State
from state_machine import StateMachine

class Waiting:
    def run(self) -> None:
        print("Broadcasting cheese smell")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case Mouse.APPEARS:
                return MouseTrap.luring
            case _:
                return self

class Luring:
    def run(self) -> None:
        print("Presenting Cheese, door open")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case Mouse.RUNS_AWAY:
                return MouseTrap.waiting
            case Mouse.ENTERS:
                return MouseTrap.trapping
            case _:
                return self

class Trapping:
    def run(self) -> None:
        print("Closing door")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case Mouse.ESCAPES:
                return MouseTrap.waiting
            case Mouse.TRAPPED:
                return MouseTrap.holding
            case _:
                return self

class Holding:
    def run(self) -> None:
        print("Mouse caught")

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        match input_:
            case Mouse.REMOVED:
                return MouseTrap.waiting
            case _:
                return self

class MouseTrap(StateMachine):
    waiting: ClassVar[State] = Waiting()
    luring: ClassVar[State] = Luring()
    trapping: ClassVar[State] = Trapping()
    holding: ClassVar[State] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)
