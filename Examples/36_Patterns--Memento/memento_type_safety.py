# memento_type_safety.py
from dataclasses import FrozenInstanceError
from exceptions import expect, expected
from sketch import Sketch

def restore_tuple(sketch: Sketch,
                  strokes: tuple[str, ...]) -> None:
    sketch.strokes = list(strokes)

sketch = Sketch()
sketch.draw("circle")
checkpoint = sketch.save()

restore_tuple(sketch, checkpoint.strokes)
print(sketch)
#: circle
restore_tuple(sketch, ("unrelated", "tuple"))
print(sketch)
#: unrelated tuple

sketch.restore(checkpoint)
print(sketch)
#: circle
# ty: tuple[str, str] is not a Memento:
expect(AttributeError, sketch.restore,
       ("unrelated", "tuple"))  # type: ignore
#: [AttributeError] 'tuple' object has no attribute
#: 'strokes'

with expected(FrozenInstanceError):
    # ty: strokes is read-only on Memento:
    checkpoint.strokes = ("forged",)  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'strokes'
