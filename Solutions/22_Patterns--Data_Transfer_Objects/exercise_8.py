# exercise_8.py
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

    def __add__(self, other: tuple[float, ...]) -> Self:
        x, y = other
        return type(self)(self.x + x, self.y + y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

p = Point(1.0, 2.0) + Point(3.0, 4.0)
print(p, type(p).__name__)
#: Point(4.0, 6.0) Point
print(p + (1.0, 1.0), p == (4.0, 6.0))
#: Point(5.0, 7.0) True
print(p[:1], (1.0, 1.0) + p)
#: (4.0,) (1.0, 1.0, 4.0, 6.0)
