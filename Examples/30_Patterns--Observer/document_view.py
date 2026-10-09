# document_view.py
from counter_model import Counter
from record import record

@record
class View:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:  # The controller
        match char:
            case "+":
                self.model.increment()
            case "-":
                self.model.decrement()
            case _:
                pass

view = View(Counter())
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
