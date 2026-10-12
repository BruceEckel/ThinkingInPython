# table_machine.py
from collections.abc import Callable
from enum import Enum

type Transition = tuple[
    Callable[..., bool] | None,
    Callable[..., None] | None, Enum
]
type Table = dict[tuple[Enum, type], list[Transition]]

class NoTransition(RuntimeError):
    "No table row matched this state and input."

class StateMachine:
    def __init__(self, initial: Enum, table: Table) -> None:
        self.state = initial
        self.table = table

    def handle(self, input_: object) -> None:
        for condition, action, next_state in self.table.get(
                (self.state, type(input_)), []):
            if condition is None or condition(input_):
                if action is not None:
                    action(input_)
                self.state = next_state
                return
        raise NoTransition(
            f"no transition from {self.state!r} "
            f"on {type(input_).__name__}")
