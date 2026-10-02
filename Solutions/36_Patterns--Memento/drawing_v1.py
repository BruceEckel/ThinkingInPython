# drawing_v1.py
from record import record

@record(slots=False)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()
