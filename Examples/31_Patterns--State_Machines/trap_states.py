# trap_states.py
from collections.abc import Callable
from enum import Enum
from mouse import Mouse
from record import record
from state import State

@record
class StateRow:
    message: str
    next: Callable[[object], State]

    def run(self) -> None:
        print(self.message)

def waiting(input_: object) -> TrapState:
    match input_:
        case Mouse.APPEARS:
            return TrapState.LURING
        case _:
            return TrapState.WAITING

def luring(input_: object) -> TrapState:
    match input_:
        case Mouse.RUNS_AWAY:
            return TrapState.WAITING
        case Mouse.ENTERS:
            return TrapState.TRAPPING
        case _:
            return TrapState.LURING

def trapping(input_: object) -> TrapState:
    match input_:
        case Mouse.ESCAPES:
            return TrapState.WAITING
        case Mouse.TRAPPED:
            return TrapState.HOLDING
        case _:
            return TrapState.TRAPPING

def holding(input_: object) -> TrapState:
    match input_:
        case Mouse.REMOVED:
            return TrapState.WAITING
        case _:
            return TrapState.HOLDING

class TrapState(StateRow, Enum):
    WAITING = ("Broadcasting cheese smell", waiting)
    LURING = ("Presenting Cheese, door open", luring)
    TRAPPING = ("Closing door", trapping)
    HOLDING = ("Mouse caught", holding)

    def __str__(self) -> str:
        return self.name.capitalize()
