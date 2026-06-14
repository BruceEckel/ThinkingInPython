# mousetrap2/MouseTrap2Test.py
# A better mousetrap using tables
import sys
from typing import Any
sys.path += ['..', '../mouse']
from State import State
from StateMachine import StateMachine
from MouseAction import MouseAction  # type: ignore

class StateT(State):
    def __init__(self) -> None:
        self.transitions: dict[Any, Any] | None = None
    def next(self, input):
        assert self.transitions is not None
        if input in self.transitions:
            return self.transitions[input]
        else:
            raise Exception("Input not supported for current state")

class Waiting(StateT):
    def run(self):
        print("Waiting: Broadcasting cheese smell")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.appears : MouseTrap.luring
            }
        return StateT.next(self, input)

class Luring(StateT):
    def run(self):
        print("Luring: Presenting Cheese, door open")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.enters : MouseTrap.trapping,
              MouseAction.runsAway : MouseTrap.waiting
            }
        return StateT.next(self, input)

class Trapping(StateT):
    def run(self):
        print("Trapping: Closing door")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.escapes : MouseTrap.waiting,
              MouseAction.trapped : MouseTrap.holding
            }
        return StateT.next(self, input)

class Holding(StateT):
    def run(self):
        print("Holding: Mouse caught")
    def next(self, input):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
              MouseAction.removed : MouseTrap.waiting
            }
        return StateT.next(self, input)

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

with open("../mouse/MouseMoves.txt") as f:
    moves = [line.strip() for line in f
             if line.strip() and not line.startswith('#')]
mouseMoves = [MouseAction(m) for m in moves]
MouseTrap().runAll(mouseMoves)
