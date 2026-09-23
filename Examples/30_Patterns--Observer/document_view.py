# document_view.py
from counter_model import Counter

class View:
    def __init__(self, model: Counter) -> None:
        self._model = model

    def draw(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:
        if char == "+":
            self._model.add(1)
        elif char == "-":
            self._model.add(-1)

model = Counter()
view = View(model)
model.subscribe(view.draw)
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
