# effect_marks.py
from record import record

@record
class Hides:
    effects: frozenset[type]

def hides(*effects: type) -> Hides:
    return Hides(frozenset(effects))
