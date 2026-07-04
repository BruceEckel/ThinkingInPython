# mouse_trap2.py
# A better mousetrap using tables
from pathlib import Path
from typing import ClassVar, override
from mouse_action import MouseAction
from state import State
from state_machine import StateMachine

class StateT(State):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @override
    def next(self, event: object) -> State:
        if event in self.transitions:
            return self.transitions[event]
        raise RuntimeError(
            "Input not supported for current state")

class Waiting(StateT):
    @override
    def run(self) -> None:
        print("Waiting: Broadcasting cheese smell")

class Luring(StateT):
    @override
    def run(self) -> None:
        print("Luring: Presenting Cheese, door open")

class Trapping(StateT):
    @override
    def run(self) -> None:
        print("Trapping: Closing door")

class Holding(StateT):
    @override
    def run(self) -> None:
        print("Holding: Mouse caught")

class MouseTrap(StateMachine):
    waiting: ClassVar[StateT] = Waiting()
    luring: ClassVar[StateT] = Luring()
    trapping: ClassVar[StateT] = Trapping()
    holding: ClassVar[StateT] = Holding()

    def __init__(self) -> None:
        StateMachine.__init__(self, MouseTrap.waiting)

# Every state object now exists, so each table can name
# its next states directly:
MouseTrap.waiting.transitions = {
    MouseAction.APPEARS: MouseTrap.luring,
}
MouseTrap.luring.transitions = {
    MouseAction.RUNS_AWAY: MouseTrap.waiting,
    MouseAction.ENTERS: MouseTrap.trapping,
}
MouseTrap.trapping.transitions = {
    MouseAction.ESCAPES: MouseTrap.waiting,
    MouseAction.TRAPPED: MouseTrap.holding,
}
MouseTrap.holding.transitions = {
    MouseAction.REMOVED: MouseTrap.waiting,
}

text = Path("mouse_moves.txt").read_text()
moves = [line.strip() for line in text.splitlines()
         if line.strip() and not line.startswith("#")]
MouseTrap().run_all([MouseAction(m) for m in moves[:9]])
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
