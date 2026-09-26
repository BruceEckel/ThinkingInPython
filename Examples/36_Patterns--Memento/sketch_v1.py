# sketch_v1.py
from record import record

@record(slots=False)
class SketchV1:
    strokes: tuple[str, ...]
