# test_frozen_sketch.py
from frozen_sketch import Drawing

def test_draw_leaves_old_drawing() -> None:
    before = Drawing("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_draw_keeps_title() -> None:
    assert Drawing("Duck").draw("x").title == "Duck"
