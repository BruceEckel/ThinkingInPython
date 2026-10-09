# model_view_controller.py
from typing import Protocol
from counter_model import Counter
from record import record

class KeyHandler(Protocol):
    def key(self, char: str) -> None: ...

@record
class View:  # Draws
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.draw)

    def draw(self, count: int) -> None:
        print(f"count: {count}")

@record
class Controller:  # Interprets
    model: Counter

    def key(self, char: str) -> None:
        match char:
            case "+":
                self.model.increment()
            case "-":
                self.model.decrement()
            case _:
                pass

class IgnoringController:  # Reads input, changes nothing
    def key(self, char: str) -> None: ...

model = Counter()
view = View(model)
controller: KeyHandler = Controller(model)
for char in "++-x":
    controller.key(char)
#: count: 1
#: count: 2
#: count: 1
controller = IgnoringController()  # View and model stay
for char in "+++":
    controller.key(char)
print(model.count)
#: 1
