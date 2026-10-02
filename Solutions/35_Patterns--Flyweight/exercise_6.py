# exercise_6.py
from typing import ClassVar
from exceptions import expect
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(
        cls, red: int, green: int, blue: int
    ) -> Color:
        components = (("red", red), ("green", green),
                      ("blue", blue))
        for name, value in components:
            if not (0 <= value <= 255):
                raise ValueError(
                    f"{name}={value} out of range 0-255")
        key: RGB = (red, green, blue)
        if key not in cls._pool:
            cls._pool[key] = super().__new__(cls)
        return cls._pool[key]

expect(ValueError, Color, 300, 0, 0)
#: [ValueError] red=300 out of range 0-255
