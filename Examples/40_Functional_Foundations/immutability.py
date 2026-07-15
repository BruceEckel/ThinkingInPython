# immutability.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
with ignore(AttributeError):
    setattr(p, "x", 5)  # A frozen instance rejects assignment
#: FrozenInstanceError("cannot assign to field 'x'")
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
