# enum_states.py
from collections.abc import Callable
from enum import Enum
from mouse_action import MouseAction as M
from record import record

type Transition = Callable[[object], TrapState]

@record
class Row:
    message: str
    next: Transition

    def run(self) -> None:
        print(self.message)

def waiting(input_: object) -> TrapState:
    match input_:
        case M.APPEARS:
            return TrapState.LURING
        case _:
            return TrapState.WAITING

def luring(input_: object) -> TrapState:
    match input_:
        case M.RUNS_AWAY:
            return TrapState.WAITING
        case M.ENTERS:
            return TrapState.TRAPPING
        case _:
            return TrapState.LURING

def trapping(input_: object) -> TrapState:
    match input_:
        case M.ESCAPES:
            return TrapState.WAITING
        case M.TRAPPED:
            return TrapState.HOLDING
        case _:
            return TrapState.TRAPPING

def holding(input_: object) -> TrapState:
    match input_:
        case M.REMOVED:
            return TrapState.WAITING
        case _:
            return TrapState.HOLDING

class TrapState(Row, Enum):
    WAITING = ("Broadcasting cheese smell", waiting)
    LURING = ("Presenting Cheese, door open", luring)
    TRAPPING = ("Closing door", trapping)
    HOLDING = ("Mouse caught", holding)

    def __str__(self) -> str:
        return self.name.capitalize()
