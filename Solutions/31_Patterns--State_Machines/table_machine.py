# table_machine.py
from collections.abc import Callable, Sequence
from enum import Enum
from typing import Any
from record import record

@record
class Rule[I]:
    state: Enum
    input_type: type[I]
    next_state: Enum
    action: Callable[[I], None] | None = None
    condition: Callable[[I], bool] | None = None

type Table = dict[tuple[Enum, type], list[Rule[Any]]]

class NoTransition(RuntimeError):
    "No rule matched this state and input."

class StateMachine:
    def __init__(self, initial: Enum,
                 rules: Sequence[Rule[Any]]) -> None:
        self.state = initial
        self.table: Table = {}
        for rule in rules:
            key = (rule.state, rule.input_type)
            self.table.setdefault(key, []).append(rule)

    def handle(self, input_: object) -> None:
        for rule in self.table.get(
                (self.state, type(input_)), []):
            condition = rule.condition
            if condition is None or condition(input_):
                if rule.action is not None:
                    rule.action(input_)
                self.state = rule.next_state
                return
        raise NoTransition(
            f"no rule from {self.state!r} "
            f"on {type(input_).__name__}")
