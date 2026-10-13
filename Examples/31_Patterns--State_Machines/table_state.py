# table_state.py
from abc import ABC, abstractmethod
from state import State

class NoTransition(RuntimeError):
    "This state's table has no entry for the input."

class EmptyTable(NoTransition):
    "This state's table was never filled."

class TableState(ABC):
    def __init__(self) -> None:
        self.transitions: dict[object, State] | None = None

    @abstractmethod
    def run(self) -> None: ...

    def next(self, input_: object) -> State:
        name = type(self).__name__
        if self.transitions is None:
            raise EmptyTable(f"{name}: table never filled")
        try:
            return self.transitions[input_]
        except KeyError:
            raise NoTransition(
                f"{name}: no transition on {input_}"
            ) from None
