# exercise_7.py
import copy
import pickle
from dataclasses import dataclass
import drawing_v1
from drawing_v1 import Drawing

blob = pickle.dumps(Drawing("Duck", ("circle",)))
blank = pickle.dumps(Drawing("", ("circle",)))

@dataclass(frozen=True)
class DrawingV2:
    title: str
    strokes: tuple[str, ...] = ()
    layer: int = 1

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("title must not be empty")

drawing_v1.Drawing = DrawingV2  # type: ignore

restored = pickle.loads(blob)
print(type(restored).__name__, restored.layer)
#: DrawingV2 1
print("layer" in restored.__dict__)
#: False

empty = pickle.loads(blank)
print(repr(empty.title))
#: ''
try:
    copy.replace(empty, strokes=())
except ValueError as e:
    print(type(e).__name__, e)
#: ValueError title must not be empty
