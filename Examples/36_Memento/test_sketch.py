# test_sketch.py
from sketch import Sketch

def test_restore_rewinds_state() -> None:
    sketch = Sketch()
    sketch.draw("a")
    checkpoint = sketch.save()
    sketch.draw("b")
    sketch.restore(checkpoint)
    assert sketch.strokes == ["a"]

def test_memento_ignores_later_drawing() -> None:
    sketch = Sketch()
    sketch.draw("a")
    checkpoint = sketch.save()
    sketch.draw("b")
    assert checkpoint.strokes == ("a",)

def test_drawing_after_restore_spares_memento() -> None:
    sketch = Sketch()
    checkpoint = sketch.save()
    sketch.restore(checkpoint)
    sketch.draw("x")
    assert checkpoint.strokes == ()
