# slots_dataclass.py
from dataclasses import dataclass
from exceptions import expected

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
with expected(AttributeError):
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
#: [AttributeError] 'Point' object has no attribute 'z' and
#: no __dict__ for setting new attributes
