# exercise_7.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass(frozen=True)
class Month:
    name: str
    n: int

def make_months() -> list[Month]:
    return [Month("January", 1), Month("February", 2)]

with expected(ValueError):
    @dataclass(frozen=True)
    class Broken:
        months: list[Month] = field(
            default_factory=make_months)
        index: dict[str, Month] = {}
#: [ValueError] mutable default <class 'dict'> for field
#: index is not allowed: use default_factory

@dataclass(frozen=True)
class Fixed:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict)

@dataclass(frozen=True)
class WrongFactory:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=list)  # type: ignore

print(Fixed().index, WrongFactory().index)
#: {} []
