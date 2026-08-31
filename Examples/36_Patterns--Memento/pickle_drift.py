# pickle_drift.py
import pickle
import sketch_v1
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV1(("circle", "beak")))
sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
try:
    print(restored.title)
except AttributeError as e:
    print(e)
#: 'SketchV2' object has no attribute 'title'
