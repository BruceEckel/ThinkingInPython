# test_ch36_erase_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def erase(self) -> Drawing:
        return replace(self, strokes=self.strokes[:-1])

class History[S]:
    def __init__(self, initial: S) -> None:
        self.present = initial
        self.past: list[S] = []

    def do(self, new_state: S) -> None:
        self.past.append(self.present)
        self.present = new_state

def test_erase_returns_new_drawing_leaving_original(
) -> None:
    before = Drawing("Duck").draw("circle").draw("beak")
    after = before.erase()
    assert before.strokes == ("circle", "beak")  # Untouched
    assert after.strokes == ("circle",)

def test_erase_leaves_history_states_untouched() -> None:
    before = Drawing("Duck").draw("circle").draw("beak")
    history = History(before)
    history.do(before.erase())
    assert history.present.strokes == ("circle",)
    assert history.past[0] is before
    assert before.strokes == ("circle", "beak")
