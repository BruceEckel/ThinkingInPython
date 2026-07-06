# interned_color.py
from typing import ClassVar

type RGB = tuple[int, int, int]

class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int, blue: int) -> Color:
        key: RGB = (red, green, blue)
        cached = cls._pool.get(key)
        if cached is not None:
            return cached
        self = super().__new__(cls)
        self.red, self.green, self.blue = red, green, blue
        cls._pool[key] = self
        return self

if __name__ == "__main__":
    crimson = Color(220, 20, 60)
    print(crimson is Color(220, 20, 60))
    print(len(Color._pool))
#: True
#: 1
