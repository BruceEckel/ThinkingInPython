# state.py
from collections.abc import Callable
from record import record

@record
class State:
    message: str
    next: Callable[[object], State]

    def run(self) -> None:
        print(self.message)
