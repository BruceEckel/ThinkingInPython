# test_ch36_erase_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(self, strokes=(*self.strokes, stroke))

    def erase(self) -> Drawing:
        return replace(self, strokes=self.strokes[:-1])

def test_erase_returns_new_drawing_leaving_original() -> None:
    before = Drawing("Duck").draw("circle").draw("beak")
    after = before.erase()
    assert before.strokes == ("circle", "beak")  # Untouched
    assert after.strokes == ("circle",)
