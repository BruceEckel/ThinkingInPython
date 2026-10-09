# model_view_controller.py
from typing import Protocol
from counter_model import Counter
from record import record

class Keys(Protocol):
    def key(self, char: str) -> None: ...

class View:  # Draws, and holds no model
    def draw(self, count: int) -> None:
        print(f"count: {count}")

@record
class StepKeys:  # Interprets, and holds the model
    model: Counter

    def key(self, char: str) -> None:
        match char:
            case "+":
                self.model.add(1)
            case "-":
                self.model.add(-1)
            case _:
                pass

class NoKeys:  # Reads input and changes nothing
    def key(self, char: str) -> None: ...

model = Counter()
view = View()
model.connect(view.draw)
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
