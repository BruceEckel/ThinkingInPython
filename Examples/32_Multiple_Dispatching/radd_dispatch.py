# radd_dispatch.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Meters:
    n: float

    def __add__(self, other: object) -> Any:
        print(f"__add__({self!r}, {other!r})")
        if isinstance(other, Meters):
            return Meters(self.n + other.n)
        if isinstance(other, int | float):
            return Meters(self.n + other)
        return NotImplemented

    def __radd__(self, other: object) -> Any:
        print(f"__radd__({self!r}, {other!r})")
        if isinstance(other, int | float):
            return Meters(other + self.n)
        return NotImplemented

print(Meters(3) + Meters(4))
#: __add__(Meters(n=3), Meters(n=4))
#: Meters(n=7)
print(Meters(3) + 4)  # The left operand handles it
#: __add__(Meters(n=3), 4)
#: Meters(n=7)
print(4 + Meters(3))  # Int declines; the right operand handles it
#: __radd__(Meters(n=3), 4)
#: Meters(n=7)
try:
    Meters(3) + "four"  # Both sides decline
except TypeError as e:
    print(type(e).__name__)
#: __add__(Meters(n=3), 'four')
#: TypeError
