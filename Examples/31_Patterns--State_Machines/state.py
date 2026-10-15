# state.py
from collections.abc import Callable
from record import record

@record
class State[I]:
    message: str
    next: Callable[[I], State[I]]
    action: Callable[[], None] = lambda: None

    def run(self) -> None:
        print(self.message)
        self.action()
