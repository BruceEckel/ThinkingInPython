# sketch.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        self.strokes: list[str] = []

    def draw(self, stroke: str) -> None:
        self.strokes.append(stroke)

    def save(self) -> Memento:
        return Memento(tuple(self.strokes))

    def restore(self, memento: Memento) -> None:
        self.strokes = list(memento.strokes)

    def __str__(self) -> str:
        return " ".join(self.strokes) or "(blank)"

if __name__ == "__main__":
    sketch = Sketch()
    sketch.draw("circle")
    sketch.draw("beak")
    checkpoint = sketch.save()
    sketch.draw("scribble")
    print(sketch)
    sketch.restore(checkpoint)
    print(sketch)
#: circle beak scribble
#: circle beak
