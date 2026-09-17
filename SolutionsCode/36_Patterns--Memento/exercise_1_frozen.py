# exercise_1_frozen.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def erase(self) -> Drawing:
        return replace(self, strokes=self.strokes[:-1])

before = Drawing("Duck").draw("circle").draw("beak")
after = before.erase()
print(before.strokes, after.strokes)
#: ('circle', 'beak') ('circle',)
