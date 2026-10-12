# mouse_trap_tables.py
from typing import ClassVar, override
from mouse_action import MouseAction
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
