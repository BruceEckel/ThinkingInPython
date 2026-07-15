# slope_nonzero.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value

print(slope(10, NonZero(2)))
#: 5.0
with ignore(ValueError):
    NonZero(0)
#: ValueError('NonZero cannot hold 0')
