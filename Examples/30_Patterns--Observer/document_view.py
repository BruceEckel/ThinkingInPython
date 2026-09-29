# document_view.py
from counter_model import Counter
from record import record

@record
class View:
    model: Counter

    def draw(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:
        if char == "+":
            self.model.add(1)
        elif char == "-":
            self.model.add(-1)

model = Counter()
view = View(model)
model.subscribe(view.draw)
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
