# mousetrap1/mouse_trap.py
# State Machine pattern using match to determine the next state.
import sys
from pathlib import Path
from typing import override

sys.path += ['..', '../mouse']
from mouse_action import MouseAction  # type: ignore
from state import State
from state_machine import StateMachine

# A different subclass for each state:

class Waiting(State):
    @override
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")

    @override
    def next(self, input: object) -> State:
        match input:
            case MouseAction.APPEARS:
                return MouseTrap.luring
            case _:
                return MouseTrap.waiting

class Luring(State):
    @override
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")

    @override
    def next(self, input: object) -> State:
        match input:
            case MouseAction.RUNS_AWAY:
                return MouseTrap.waiting
            case MouseAction.ENTERS:
                return MouseTrap.trapping
            case _:
                return MouseTrap.luring

class Trapping(State):
    @override
    def run(self) -> None:
        print("Trapping: Closing door")

    @override
    def next(self, input: object) -> State:
        match input:
            case MouseAction.ESCAPES:
                return MouseTrap.waiting
            case MouseAction.TRAPPED:
                return MouseTrap.holding
            case _:
                return MouseTrap.trapping

class Holding(State):
    @override
    def run(self) -> None:
        print("Holding: Mouse caught")

    @override
    def next(self, input: object) -> State:
        match input:
            case MouseAction.REMOVED:
                return MouseTrap.waiting
            case _:
                return MouseTrap.holding

class MouseTrap(StateMachine):
    waiting: State
    luring: State
    trapping: State
    holding: State

    def __init__(self) -> None:
        # Initial state
        StateMachine.__init__(self, MouseTrap.waiting)

# Static variable initialization:
MouseTrap.waiting = Waiting()
MouseTrap.luring = Luring()
MouseTrap.trapping = Trapping()
MouseTrap.holding = Holding()

text = Path("../mouse/mouse_moves.txt").read_text()
moves = [line.strip() for line in text.splitlines()
         if line.strip() and not line.startswith('#')]
MouseTrap().run_all([MouseAction(m) for m in moves])
## Waiting: Broadcasting cheese smell
## mouse appears
## Luring: Presenting Cheese, door open
## mouse runs away
## Waiting: Broadcasting cheese smell
## mouse appears
## Luring: Presenting Cheese, door open
## mouse enters trap
## Trapping: Closing door
## mouse escapes
## Waiting: Broadcasting cheese smell
## mouse appears
## Luring: Presenting Cheese, door open
## mouse enters trap
## Trapping: Closing door
## mouse trapped
## Holding: Mouse caught
## mouse removed
## Waiting: Broadcasting cheese smell
## mouse appears
## Luring: Presenting Cheese, door open
## mouse runs away
## Waiting: Broadcasting cheese smell
## mouse appears
## Luring: Presenting Cheese, door open
## mouse enters trap
## Trapping: Closing door
## mouse trapped
## Holding: Mouse caught
## mouse removed
## Waiting: Broadcasting cheese smell
