# exercise_7.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Month:
    name: str
    n: int

def make_months() -> list[Month]:
    return [Month("January", 1), Month("February", 2)]

try:
    @dataclass(frozen=True)
    class Broken:
        months: list[Month] = field(
            default_factory=make_months)
        index: dict[str, Month] = {}
except ValueError as e:
    print(f"{type(e).__name__}: {str(e).split(': ')[-1]}")
#: ValueError: use default_factory

@dataclass(frozen=True)
class Bare:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict)

@dataclass(frozen=True)
class Subscripted:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(
        default_factory=dict[str, Month])

print(Bare().index, Subscripted().index)
#: {} {}
