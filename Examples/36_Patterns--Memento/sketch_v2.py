# sketch_v2.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SketchV2:
    strokes: tuple[str, ...]
    title: str
