# mouse_trap_states.py
from typing import ClassVar
from mouse_action import MouseAction
from mouse_moves import MOVES
from state import State
from state_machine import StateMachine

class Waiting:
    def run(self) -> None:
        print("Broadcasting cheese smell")

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.APPEARS:
                return MouseTrap.luring
            case _:
                return MouseTrap.waiting

class Luring:
    def run(self) -> None:
        print("Presenting Cheese, door open")

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.RUNS_AWAY:
                return MouseTrap.waiting
            case MouseAction.ENTERS:
                return MouseTrap.trapping
            case _:
                return MouseTrap.luring

class Trapping:
    def run(self) -> None:
        print("Closing door")

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.ESCAPES:
                return MouseTrap.waiting
            case MouseAction.TRAPPED:
                return MouseTrap.holding
            case _:
                return MouseTrap.trapping

class Holding:
    def run(self) -> None:
        print("Mouse caught")

    def next(self, input_: object) -> State:
        match input_:
            case MouseAction.REMOVED:
                return MouseTrap.waiting
            case _:
                return MouseTrap.holding

class MouseTrap(StateMachine):
    waiting: ClassVar[State] = Waiting()
    luring: ClassVar[State] = Luring()
    trapping: ClassVar[State] = Trapping()
    holding: ClassVar[State] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)

MouseTrap().run_all(MOVES)
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse runs away -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse escapes -> Waiting
#: Broadcasting cheese smell
#: Waiting mouse appears -> Luring
#: Presenting Cheese, door open
#: Luring mouse enters trap -> Trapping
#: Closing door
#: Trapping mouse trapped -> Holding
#: Mouse caught
#: Holding mouse removed -> Waiting
#: Broadcasting cheese smell

# ESCAPES has no case in Waiting, so case _
# fires and the machine stays at Waiting:
trap = MouseTrap()
#: Broadcasting cheese smell
trap.run_all([MouseAction.ESCAPES])
#: Waiting mouse escapes -> Waiting
#: Broadcasting cheese smell
