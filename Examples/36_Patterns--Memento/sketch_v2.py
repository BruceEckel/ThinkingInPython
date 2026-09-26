# sketch_v2.py
from record import record

@record(slots=False)
class SketchV2:
    strokes: tuple[str, ...]
    title: str
