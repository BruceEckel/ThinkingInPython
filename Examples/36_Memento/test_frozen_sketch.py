# test_frozen_sketch.py
from frozen_sketch import Sketch

def test_draw_returns_new_sketch() -> None:
    before = Sketch("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_replace_carries_other_fields() -> None:
    assert Sketch("Duck").draw("x").title == "Duck"

def test_equal_states_compare_equal() -> None:
    first = Sketch("Duck").draw("circle")
    second = Sketch("Duck").draw("circle")
    assert first == second and first is not second
