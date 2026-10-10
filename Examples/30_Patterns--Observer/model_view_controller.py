# model_view_controller.py
from counter_model import Counter
from record import record

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

@record
class VimController:  # k is up, j is down
    model: Counter

    def key(self, char: str) -> None:
        match char:
            case "k":
                self.model.increment()
            case "j":
                self.model.decrement()
            case _:
                pass

model = Counter()
view = View(model)
controller = Controller(model)
for char in "++-x":
    controller.key(char)
#: count: 1
#: count: 2
#: count: 1
vim = VimController(model)  # Same model, same view
for char in "kkj":
    vim.key(char)
#: count: 2
#: count: 3
#: count: 2
