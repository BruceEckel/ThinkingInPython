# test_ch37_erase_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(self, strokes=(*self.strokes, stroke))

    def erase(self) -> Sketch:
        return replace(self, strokes=self.strokes[:-1])

def test_erase_returns_new_sketch_leaving_original() -> None:
    before = Sketch("Duck").draw("circle").draw("beak")
    after = before.erase()
    assert before.strokes == ("circle", "beak")  # Untouched
    assert after.strokes == ("circle",)
