# test_ch37_erase_mutable.py
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

def test_erase_does_not_affect_existing_memento() -> None:
    sketch = Sketch()
    sketch.draw("a")
    sketch.draw("b")
    checkpoint = sketch.save()
    sketch.erase()
    assert sketch.strokes == ["a"]
    assert checkpoint.strokes == ("a", "b")  # Untouched
