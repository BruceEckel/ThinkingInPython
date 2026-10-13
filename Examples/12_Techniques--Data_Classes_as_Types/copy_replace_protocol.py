# copy_replace_protocol.py
import copy
from typing import Self

class Color:
    def __init__(self, red: int, green: int,
                 blue: int) -> None:
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self) -> str:
        return (f"Color({self.red}, {self.green}, "
                f"{self.blue})")

    def __replace__(self, **changes: int) -> Self:
        current = {"red": self.red, "green": self.green,
                   "blue": self.blue}
        return type(self)(**(current | changes))

teal = Color(0, 128, 128)
print(teal)
#: Color(0, 128, 128)
lighter = copy.replace(teal, red=64)
print(lighter)
#: Color(64, 128, 128)
