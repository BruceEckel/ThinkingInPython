# test_ch36_erase_mutable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        self.strokes: list[str] = []

    def draw(self, stroke: str) -> None:
        self.strokes.append(stroke)

    def erase(self) -> None:
        if self.strokes:
            self.strokes.pop()

    def save(self) -> Memento:
        return Memento(tuple(self.strokes))

    def restore(self, memento: Memento) -> None:
        self.strokes = list(memento.strokes)

class History[S]:
    def __init__(self, initial: S) -> None:
        self.present = initial
        self.past: list[S] = []

    def do(self, new_state: S) -> None:
        self.past.append(self.present)
        self.present = new_state

def test_erase_does_not_affect_existing_memento() -> None:
    sketch = Sketch()
    sketch.draw("a")
    sketch.draw("b")
    checkpoint = sketch.save()
    sketch.erase()
    assert sketch.strokes == ["a"]
    assert checkpoint.strokes == ("a", "b")  # Untouched

def test_erase_leaves_history_states_untouched() -> None:
    sketch = Sketch()
    sketch.draw("a")
    history = History(sketch.save())
    sketch.draw("b")
    history.do(sketch.save())
    sketch.erase()
    assert history.present.strokes == ("a", "b")
    assert history.past[0].strokes == ("a",)
