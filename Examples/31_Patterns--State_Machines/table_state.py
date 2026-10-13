# table_state.py
from abc import ABC, abstractmethod
from state import State

class TableState(ABC):
    def __init__(self) -> None:
        self.transitions: dict[object, State] = {}

    @abstractmethod
    def run(self) -> None: ...

    def next(self, input_: object) -> State:
        try:
            return self.transitions[input_]
        except KeyError:
            raise RuntimeError(
                f"{type(self).__name__}: no transition "
                f"on {input_}") from None
