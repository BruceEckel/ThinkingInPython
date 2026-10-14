# enum_states.py
from collections.abc import Callable
from enum import Enum
from mouse_action import MouseAction as M
from record import record

type Behavior = Callable[[M], str]
type Transition = Callable[[M], TrapState]

@record
class State:
    behavior: Behavior
    transition: Transition

def waiting(input_: M) -> TrapState:
    match input_:
        case M.APPEARS:
            return TrapState.LURING
        case _:
            return TrapState.WAITING

def luring(input_: M) -> TrapState:
    match input_:
        case M.RUNS_AWAY:
            return TrapState.WAITING
        case M.ENTERS:
            return TrapState.TRAPPING
        case _:
            return TrapState.LURING

def trapping(input_: M) -> TrapState:
    match input_:
        case M.ESCAPES:
            return TrapState.WAITING
        case M.TRAPPED:
            return TrapState.HOLDING
        case _:
            return TrapState.TRAPPING

def holding(input_: M) -> TrapState:
    match input_:
        case M.REMOVED:
            return TrapState.WAITING
        case _:
            return TrapState.HOLDING

class TrapState(State, Enum):
    WAITING = (lambda _: "Broadcasting cheese smell",
               waiting)
    LURING = (lambda _: "Presenting Cheese, door open",
              luring)
    TRAPPING = (lambda _: "Closing door", trapping)
    HOLDING = (lambda _: "Mouse caught", holding)

class StateMachine:
    def __init__(self, start: TrapState) -> None:
        self.state = start

    def output(self, input_: M) -> str:
        result = self.state.behavior(input_)
        self.state = self.state.transition(input_)
        return result
