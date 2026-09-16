# exercise_5.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class Meters:
    n: float

    def __sub__(self, other: object) -> Meters:
        if isinstance(other, Meters):
            return Meters(self.n - other.n)
        if isinstance(other, int | float):
            return Meters(self.n - other)
        return NotImplemented

    def __rsub__(self, other: object) -> Meters:
        if isinstance(other, int | float):
            # Not self.n - other
            return Meters(other - self.n)
        return NotImplemented

print(Meters(10) - Meters(3), Meters(10) - 3)
#: Meters(n=7) Meters(n=7)
print(10 - Meters(3))
#: Meters(n=7)
with ignore(TypeError):
    "ten" - Meters(3)
#: TypeError("unsupported operand type(s) for -: 'str' and
#: 'Meters'")
