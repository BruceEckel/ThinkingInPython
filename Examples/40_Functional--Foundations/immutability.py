# immutability.py
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

p = Point(1, 2)
with expected(AttributeError):
    # A frozen instance rejects assignment
    setattr(p, "x", 5)
#: [FrozenInstanceError] cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(p, moved)
#: Point(x=1, y=2) Point(x=11, y=2)
