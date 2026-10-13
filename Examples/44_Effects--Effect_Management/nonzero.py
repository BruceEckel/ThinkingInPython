# nonzero.py
from record import record

@record
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value
