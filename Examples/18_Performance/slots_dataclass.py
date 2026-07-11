# slots_dataclass.py
import sys
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
try:
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError

@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int

@dataclass(frozen=True, slots=True)
class FrozenSlottedPoint:
    x: int
    y: int

fp = FrozenPoint(1, 2)
try:
    # Frozen prevents new attributes, not just reassignment:
    fp.z = 3  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: FrozenInstanceError

frozen_bytes = sys.getsizeof(fp) + sys.getsizeof(fp.__dict__)
slotted_bytes = sys.getsizeof(FrozenSlottedPoint(1, 2))
print(f"slots at least 5x smaller: "
      f"{slotted_bytes * 5 < frozen_bytes}")
#: slots at least 5x smaller: True
