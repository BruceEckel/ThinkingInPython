# memento_type_safety.py
from dataclasses import FrozenInstanceError
from sketch import Memento, Sketch

def restore_tuple(strokes: tuple[str, ...]) -> None:
    print(strokes)

def restore_memento(memento: Memento) -> None:
    print(memento.strokes)

sketch = Sketch()
sketch.draw("circle")
checkpoint = sketch.save()

restore_tuple(checkpoint.strokes)
#: ('circle',)
restore_tuple(("unrelated", "tuple"))
#: ('unrelated', 'tuple')

restore_memento(checkpoint)
#: ('circle',)
# ty: tuple[str, str] is not a Memento:
try:
    restore_memento(("unrelated", "tuple"))  # type: ignore
except AttributeError as e:
    print(e)
#: 'tuple' object has no attribute 'strokes'

try:
    # ty: strokes is read-only on Memento:
    checkpoint.strokes = ("forged",)  # type: ignore
except FrozenInstanceError as e:
    print(type(e).__name__)
#: FrozenInstanceError
