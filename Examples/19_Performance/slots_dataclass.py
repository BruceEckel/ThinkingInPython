# slots_dataclass.py
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
