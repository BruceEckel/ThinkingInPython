# ghost_field.py
import pickle
import sketch_v2
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV2(("circle",), "Duck"))
sketch_v2.SketchV2 = SketchV1  # type: ignore
restored = pickle.loads(blob)
print(restored)
#: SketchV1(strokes=('circle',))
print(restored.__dict__)
#: {'strokes': ('circle',), 'title': 'Duck'}
print(restored == SketchV1(("circle",)))
#: True
