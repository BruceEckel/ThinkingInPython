# interned_color.py
from typing import ClassVar
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int,
                blue: int) -> Color:
        key: RGB = (red, green, blue)
        if key not in cls._pool:
            cls._pool[key] = super().__new__(cls)
        return cls._pool[key]

crimson = Color(220, 20, 60)
print(crimson is Color(220, 20, 60))
#: True
print(len(Color._pool))
#: 1
