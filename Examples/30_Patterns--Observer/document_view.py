# document_view.py
from counter_model import Counter
from record import record

@record
class View:
    model: Counter

    def draw(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:  # The controller
        match char:
            case "+":
                self.model.increment()
            case "-":
                self.model.decrement()
            case _:
                pass

model = Counter()
view = View(model)
model.connect(view.draw)
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
