# frozen_sketch.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def __str__(self) -> str:
        drawn = " ".join(self.strokes) or "(blank)"
        return f"{self.title}: {drawn}"
