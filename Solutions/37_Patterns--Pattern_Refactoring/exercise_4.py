# exercise_4.py
from collections import defaultdict
from functools import singledispatch
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    bin: ClassVar[type[Trash]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "bin" not in cls.__dict__:
            cls.bin = cls

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class CrushedAluminum(Aluminum):
    value: ClassVar[float] = 1.67
    bin: ClassVar[type[Trash]] = Aluminum

class Glass(Trash):
    value: ClassVar[float] = 0.23

@singledispatch
def recycling_note(t: Trash) -> str:
    return "no special handling"

@recycling_note.register
def _(t: Aluminum) -> str:
    return "crush and bale"

pieces: list[Trash] = [
    Aluminum(30.0), CrushedAluminum(20.0), Glass(10.0)]

exact: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    exact[type(t)].append(t)
print(sorted(k.__name__ for k in exact))
#: ['Aluminum', 'CrushedAluminum', 'Glass']

crushed = CrushedAluminum(1.0)
print(f"{type(crushed).__name__}: "
      f"{recycling_note(crushed)}")
#: CrushedAluminum: crush and bale

shared: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    shared[t.bin].append(t)
print(sorted(k.__name__ for k in shared))
#: ['Aluminum', 'Glass']
