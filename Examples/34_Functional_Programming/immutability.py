# immutability.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
try:
    setattr(p, "x", 5)  # A frozen instance rejects assignment
except AttributeError as e:
    print(e)
#: cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
