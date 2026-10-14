# trap_tables.py
from typing import ClassVar, override
from mouse import Mouse
from state_machine import StateMachine
from table_state import TableState

class Waiting(TableState):
    @override
    def run(self) -> None:
        print("Broadcasting cheese smell")

class Luring(TableState):
    @override
    def run(self) -> None:
        print("Presenting Cheese, door open")

class Trapping(TableState):
    @override
    def run(self) -> None:
        print("Closing door")

class Holding(TableState):
    @override
    def run(self) -> None:
        print("Mouse caught")

class MouseTrap(StateMachine):
    waiting: ClassVar[TableState] = Waiting()
    luring: ClassVar[TableState] = Luring()
    trapping: ClassVar[TableState] = Trapping()
    holding: ClassVar[TableState] = Holding()

    def __init__(self) -> None:
        super().__init__(MouseTrap.waiting)

MouseTrap.waiting.transitions = {
    Mouse.APPEARS: MouseTrap.luring,
}
MouseTrap.luring.transitions = {
    Mouse.RUNS_AWAY: MouseTrap.waiting,
    Mouse.ENTERS: MouseTrap.trapping,
}
MouseTrap.trapping.transitions = {
    Mouse.ESCAPES: MouseTrap.waiting,
    Mouse.TRAPPED: MouseTrap.holding,
}
MouseTrap.holding.transitions = {
    Mouse.REMOVED: MouseTrap.waiting,
}
