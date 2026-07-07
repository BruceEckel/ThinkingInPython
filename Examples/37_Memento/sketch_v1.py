# sketch_v1.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SketchV1:
    strokes: tuple[str, ...]
