# trap_states.py
from enum import Enum
from mouse import Mouse
from state import State

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

# trap_states.py (continued)
class TrapState(State, Enum):
    WAITING = ("Broadcasting cheese smell", waiting)
    LURING = ("Presenting Cheese, door open", luring)
    TRAPPING = ("Closing door", trapping)
    HOLDING = ("Mouse caught", holding)

    def __str__(self) -> str:
        return self.name.capitalize()
