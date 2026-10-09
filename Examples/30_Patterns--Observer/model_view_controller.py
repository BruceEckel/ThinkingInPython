# model_view_controller.py
from typing import Protocol
from counter_model import Counter
from record import record

class KeyHandler(Protocol):
    def key(self, char: str) -> None: ...

@record
class View:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"count: {count}")

@record
class Controller:  # Interprets but doesn't display
    model: Counter

    def key(self, char: str) -> None:
        match char:
            case "+":
                self.model.increment()
            case "-":
                self.model.decrement()
            case _:
                pass

class IgnoringController:  # Ignores input, needs no model
    def key(self, char: str) -> None: ...

model = Counter()
view = View(model)
controller: KeyHandler = Controller(model)
for char in "++-x":
    controller.key(char)
#: count: 1
#: count: 2
#: count: 1
controller = IgnoringController()  # Disables input
for char in "+++":
    controller.key(char)
print(model.count)
#: 1
