# exercise_6.py
from typing import ClassVar

type RGB = tuple[int, int, int]

class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int, blue: int) -> Color:
        components = (("red", red), ("green", green),
                      ("blue", blue))
        for name, value in components:
            if not (0 <= value <= 255):
                raise ValueError(
                    f"{name}={value} out of range 0-255")
        key: RGB = (red, green, blue)
        cached = cls._pool.get(key)
        if cached is not None:
            return cached
        self = super().__new__(cls)
        self.red, self.green, self.blue = red, green, blue
        cls._pool[key] = self
        return self

try:
    Color(300, 0, 0)
except ValueError as e:
    print("caught:", e)
#: caught: red=300 out of range 0-255
