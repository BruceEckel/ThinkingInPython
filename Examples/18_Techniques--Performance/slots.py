# slots.py
from exceptions import ignore

class Point:
    __slots__ = ("x", "y")  # No per-instance __dict__
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)
#: 1 2
with ignore(AttributeError):
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
#: AttributeError("'Point' object has no attribute 'z' and
#: no __dict__ for setting new attributes")
