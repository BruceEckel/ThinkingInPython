# exercise_1_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(self, strokes=(*self.strokes, stroke))

    def erase(self) -> Sketch:
        return replace(self, strokes=self.strokes[:-1])

before = Sketch("Duck").draw("circle").draw("beak")
after = before.erase()
print(before.strokes, after.strokes)
#: ('circle', 'beak') ('circle',)
