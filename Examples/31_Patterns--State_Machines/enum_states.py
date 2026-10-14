# enum_states.py
from collections.abc import Callable
from enum import Enum
from mouse_action import MouseAction as M
from record import record

type Behavior = Callable[[M], str]
type Transition = Callable[[M], Trap]

@record
class State:
    behavior: Behavior
    transition: Transition

def waiting_next(input_: M) -> Trap:
    match input_:
        case M.APPEARS:
            return Trap.LURING
        case _:
            return Trap.WAITING

def luring_next(input_: M) -> Trap:
    match input_:
        case M.RUNS_AWAY:
            return Trap.WAITING
        case M.ENTERS:
            return Trap.TRAPPING
        case _:
            return Trap.LURING

def trapping_next(input_: M) -> Trap:
    match input_:
        case M.ESCAPES:
            return Trap.WAITING
        case M.TRAPPED:
            return Trap.HOLDING
        case _:
            return Trap.TRAPPING

def holding_next(input_: M) -> Trap:
    match input_:
        case M.REMOVED:
            return Trap.WAITING
        case _:
            return Trap.HOLDING

class Trap(State, Enum):
    WAITING = (lambda _: "Broadcasting cheese smell",
               waiting_next)
    LURING = (lambda _: "Presenting Cheese, door open",
              luring_next)
    TRAPPING = (lambda _: "Closing door", trapping_next)
    HOLDING = (lambda _: "Mouse caught", holding_next)

class StateMachine:
    def __init__(self, start: Trap) -> None:
        self.state = start

    def output(self, input_: M) -> str:
        result = self.state.behavior(input_)
        self.state = self.state.transition(input_)
        return result
