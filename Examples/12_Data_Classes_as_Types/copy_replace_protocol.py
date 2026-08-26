# copy_replace_protocol.py
import copy
from typing import Final, Self

SHIFTS: Final[dict[str, int]] = {
    "red": 16, "green": 8, "blue": 0}
MASK: Final[int] = 0xFF

class Color:
    def __init__(self, red: int, green: int,
                 blue: int) -> None:
        channels = {"red": red, "green": green,
                    "blue": blue}
        self.packed = sum(v << SHIFTS[k]
                          for k, v in channels.items())

    @property
    def channels(self) -> dict[str, int]:
        return {n: self.packed >> s & MASK
                for n, s in SHIFTS.items()}

    def __repr__(self) -> str:
        channels = map(str, self.channels.values())
        return f"Color({', '.join(channels)})"

    def __replace__(self, **changes: int) -> Self:
        return type(self)(**(self.channels | changes))

teal = Color(0, 128, 128)
print(teal, hex(teal.packed))
#: Color(0, 128, 128) 0x8080
lighter = copy.replace(teal, red=64)
print(lighter, hex(lighter.packed))
#: Color(64, 128, 128) 0x408080
