# point_record.py
from exceptions import ignore
from record import record

@record
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
print(p == Point(1, 2), hasattr(p, "__dict__"))
#: True False
with ignore(AttributeError):
    p.x = 3  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'x'
