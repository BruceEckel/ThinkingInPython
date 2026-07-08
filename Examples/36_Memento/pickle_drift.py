# pickle_drift.py
import pickle
from dataclasses import dataclass
import sketch_v1
from sketch_v1 import SketchV1

blob = pickle.dumps(SketchV1(("circle", "beak")))

@dataclass(frozen=True)
class SketchV2:
    strokes: tuple[str, ...]
    title: str

sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
try:
    print(restored.title)
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError 'SketchV2' object has no attribute 'title'
