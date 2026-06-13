# StateMachine/mousetrap1/MouseTrapTest.py
# State Machine pattern using 'if' statements
# to determine the next state.
import sys
sys.path += ['..', '../mouse']
from State import State
from StateMachine import StateMachine
from MouseAction import MouseAction  # type: ignore
# A different subclass for each state:

class Waiting(State):
    def run(self):
        print("Waiting: Broadcasting cheese smell")

    def next(self, input):
        if input == MouseAction.appears:
            return MouseTrap.luring
        return MouseTrap.waiting

class Luring(State):
    def run(self):
        print("Luring: Presenting Cheese, door open")

    def next(self, input):
        if input == MouseAction.runsAway:
            return MouseTrap.waiting
        if input == MouseAction.enters:
            return MouseTrap.trapping
        return MouseTrap.luring

class Trapping(State):
    def run(self):
        print("Trapping: Closing door")

    def next(self, input):
        if input == MouseAction.escapes:
            return MouseTrap.waiting
        if input == MouseAction.trapped:
            return MouseTrap.holding
        return MouseTrap.trapping

class Holding(State):
    def run(self):
        print("Holding: Mouse caught")

    def next(self, input):
        if input == MouseAction.removed:
            return MouseTrap.waiting
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

with open("../mouse/MouseMoves.txt") as f:
    moves = [line.strip() for line in f
             if line.strip() and not line.startswith('#')]
MouseTrap().runAll([MouseAction(m) for m in moves])
