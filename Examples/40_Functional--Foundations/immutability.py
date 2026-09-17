# immutability.py
from exceptions import ignore
from record import record

@record
class Point:
    x: int
    y: int

p = Point(1, 2)
with ignore(AttributeError):
    # A frozen instance rejects assignment
    setattr(p, "x", 5)
#: [FrozenInstanceError] cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
