# table_state.py
from abc import ABC, abstractmethod
from state import State

class NoTransition(RuntimeError):
    "This state's table has no entry for the input."

class TableState(ABC):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @abstractmethod
    def run(self) -> None: ...

    def __str__(self) -> str:
        return type(self).__name__

    def next(self, input_: object) -> State:
        try:
            return self.transitions[input_]
        except KeyError:
            raise NoTransition(
                f"{type(self).__name__}: "
                f"no transition on {input_}") from None
