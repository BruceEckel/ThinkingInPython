# exercise_4.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(frozen=True)
class PositiveInt:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(
                f"PositiveInt needs a positive value: "
                f"{self.value}")

def slope(rise: int, run: PositiveInt) -> float:
    return rise / run.value

print(slope(10, PositiveInt(2)))
#: 5.0
for bad in (0, -1):
    expect(ValueError, PositiveInt, bad)
#: [ValueError] PositiveInt needs a positive value: 0
#: [ValueError] PositiveInt needs a positive value: -1
