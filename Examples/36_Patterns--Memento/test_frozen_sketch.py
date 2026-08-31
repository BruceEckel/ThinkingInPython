# test_frozen_sketch.py
from frozen_sketch import Drawing

def test_draw_returns_new_drawing() -> None:
    before = Drawing("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_replace_carries_other_fields() -> None:
    assert Drawing("Duck").draw("x").title == "Duck"
