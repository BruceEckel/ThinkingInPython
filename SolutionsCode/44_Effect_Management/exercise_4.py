# exercise_4.py
from dataclasses import dataclass

@dataclass(frozen=True)
class PositiveInt:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(
                f"PositiveInt needs a positive value: {self.value}")

def slope(rise: int, run: PositiveInt) -> float:
    return rise / run.value

print(slope(10, PositiveInt(2)))
#: 5.0
for bad in (0, -1):
    try:
        PositiveInt(bad)
    except ValueError as e:
        print(e)
#: PositiveInt needs a positive value: 0
#: PositiveInt needs a positive value: -1
