# point_tuple.py
from typing import Self

class Point(tuple[float, float]):
    __slots__ = ()

    def __new__(cls, x: float, y: float) -> Self:
        return super().__new__(cls, (x, y))

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

p = Point(1.0, 2.0)
print(p, p.x, p.y)
#: (1.0, 2.0) 1.0 2.0
print(isinstance(p, tuple), p == (1.0, 2.0))
#: True True
print(type(p + (3.0,)).__name__, type(p[:1]).__name__)
#: tuple tuple
print(hasattr(p, "__dict__"))
#: False
