# enum_states.py
from collections.abc import Callable
from enum import Enum
from mouse_action import MouseAction as M
from record import record

type Behavior = Callable[[M], str]
type Transition = Callable[[M], MouseTrap]

@record
class State:
    behavior: Behavior
    transition: Transition

def waiting_next(input_: M) -> MouseTrap:
    match input_:
        case M.APPEARS:
            return MouseTrap.LURING
        case _:
            return MouseTrap.WAITING

def luring_next(input_: M) -> MouseTrap:
    match input_:
        case M.RUNS_AWAY:
            return MouseTrap.WAITING
        case M.ENTERS:
            return MouseTrap.TRAPPING
        case _:
            return MouseTrap.LURING

def trapping_next(input_: M) -> MouseTrap:
    match input_:
        case M.ESCAPES:
            return MouseTrap.WAITING
        case M.TRAPPED:
            return MouseTrap.HOLDING
        case _:
            return MouseTrap.TRAPPING

def holding_next(input_: M) -> MouseTrap:
    match input_:
        case M.REMOVED:
            return MouseTrap.WAITING
        case _:
            return MouseTrap.HOLDING

class MouseTrap(State, Enum):
    WAITING = (lambda _: "Broadcasting cheese smell",
               waiting_next)
    LURING = (lambda _: "Presenting Cheese, door open",
              luring_next)
    TRAPPING = (lambda _: "Closing door", trapping_next)
    HOLDING = (lambda _: "Mouse caught", holding_next)

class StateMachine:
    def __init__(self, start: MouseTrap) -> None:
        self.state = start

    def output(self, input_: M) -> str:
        result = self.state.behavior(input_)
        self.state = self.state.transition(input_)
        return result
