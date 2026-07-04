# mousetrap2/mouse_trap2.py
# A better mousetrap using tables
import sys
from pathlib import Path
from typing import Any, ClassVar, override

sys.path += ["..", "../mouse"]
from mouse_action import MouseAction  # type: ignore
from state import State
from state_machine import StateMachine

class StateT(State):
    def __init__(self) -> None:
        self.transitions: dict[Any, Any] = {}
    @override
    def next(self, event: object) -> State:
        if event in self.transitions:
            return self.transitions[event]
        else:
            raise RuntimeError(
                "Input not supported for current state")

class Waiting(StateT):
    @override
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")
    @override
    def next(self, event: object) -> State:
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.APPEARS : MouseTrap.luring
            }
        return StateT.next(self, event)

class Luring(StateT):
    @override
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")
    @override
    def next(self, event: object) -> State:
        if not self.transitions:
            self.transitions = {
              MouseAction.ENTERS : MouseTrap.trapping,
              MouseAction.RUNS_AWAY : MouseTrap.waiting
            }
        return StateT.next(self, event)

class Trapping(StateT):
    @override
    def run(self) -> None:
        print("Trapping: Closing door")
    @override
    def next(self, event: object) -> State:
        if not self.transitions:
            self.transitions = {
              MouseAction.ESCAPES : MouseTrap.waiting,
              MouseAction.TRAPPED : MouseTrap.holding
            }
        return StateT.next(self, event)

class Holding(StateT):
    @override
    def run(self) -> None:
        print("Holding: Mouse caught")
    @override
    def next(self, event: object) -> State:
        if not self.transitions:
            self.transitions = {
              MouseAction.REMOVED : MouseTrap.waiting
            }
        return StateT.next(self, event)

class MouseTrap(StateMachine):
    waiting: ClassVar[State] = Waiting()
    luring: ClassVar[State] = Luring()
    trapping: ClassVar[State] = Trapping()
    holding: ClassVar[State] = Holding()

    def __init__(self) -> None:
        StateMachine.__init__(self, MouseTrap.waiting)

text = Path("../mouse/mouse_moves.txt").read_text()
moves = [line.strip() for line in text.splitlines()
         if line.strip() and not line.startswith("#")]
mouse_moves = [MouseAction(m) for m in moves]
MouseTrap().run_all(mouse_moves)
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse runs away
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse escapes
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse trapped
#: Holding: Mouse caught
#: mouse removed
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse runs away
#: Waiting: Broadcasting cheese smell
#: mouse appears
#: Luring: Presenting Cheese, door open
#: mouse enters trap
#: Trapping: Closing door
#: mouse trapped
#: Holding: Mouse caught
#: mouse removed
#: Waiting: Broadcasting cheese smell
