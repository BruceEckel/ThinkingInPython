# tabledriven/state_machine.py
# A generic table-driven state machine.
#
# The whole machine is one transition table. Because Python
# functions are first-class, a transition's condition and action are
# just callables, so the Condition and Transition classes a Java
# version needs disappear.
from collections.abc import Callable
from enum import Enum
from typing import Any

# (condition, action, next_state); condition and action may be None.
# A state is any Enum member, so a misspelled state is a type error
# rather than a silent dead end.
type Transition = tuple[
    Callable[..., bool] | None, Callable[..., None] | None, Enum
]
type Table = dict[tuple[Enum, type], list[Transition]]


class StateMachine:
    def __init__(self, initial: Enum, table: Table) -> None:
        self.state = initial
        self.table = table

    def handle(self, event: Any) -> None:
        for condition, action, next_state in self.table.get(
                (self.state, type(event)), []):
            if condition is None or condition(event):
                if action is not None:
                    action(event)
                self.state = next_state
                return
        raise RuntimeError(
            f"no transition from {self.state!r} "
            f"on {type(event).__name__}")
