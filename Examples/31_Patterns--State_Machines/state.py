# state.py
from collections.abc import Callable
from record import record

@record
class State:
    message: str
    next: Callable[[object], State]
    action: Callable[[], None] = lambda: None

    def run(self) -> None:
        print(self.message)
        self.action()
