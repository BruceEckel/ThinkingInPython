# model_view_controller.py
from typing import Protocol
from counter_model import Counter

class Keys(Protocol):
    def key(self, char: str) -> None: ...

class View:  # Draws, and holds no model
    def draw(self, count: int) -> None:
        print(f"count: {count}")

class StepKeys:  # Interprets, and holds the model
    def __init__(self, model: Counter) -> None:
        self._model = model

    def key(self, char: str) -> None:
        if char == "+":
            self._model.add(1)
        elif char == "-":
            self._model.add(-1)

class NoKeys:  # Reads input and changes nothing
    def key(self, char: str) -> None: ...

model = Counter()
view = View()
model.subscribe(view.draw)
control: Keys = StepKeys(model)
for char in "++-x":
    control.key(char)
#: count: 1
#: count: 2
#: count: 1
control = NoKeys()  # View and model untouched
for char in "+++":
    control.key(char)
print(model.count)
#: 1
