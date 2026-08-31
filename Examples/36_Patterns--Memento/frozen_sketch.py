# frozen_sketch.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def __str__(self) -> str:
        drawn = " ".join(self.strokes) or "(blank)"
        return f"{self.title}: {drawn}"

if __name__ == "__main__":
    before = Drawing("Duck").draw("circle").draw("beak")
    after = before.draw("scribble")
    print(after)
    print(before)
#: Duck: circle beak scribble
#: Duck: circle beak
