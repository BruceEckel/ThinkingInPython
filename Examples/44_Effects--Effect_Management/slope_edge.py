# slope_edge.py
from dataclasses import dataclass
from result import Err, Ok
from safe import safe

@dataclass(frozen=True)
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value

@safe
def parse_run(text: str) -> NonZero:
    return NonZero(int(text))

for text in ["2", "0"]:
    match parse_run(text):
        case Ok(run):
            print(slope(10, run))
        case Err(error):
            print(f"{text!r}: {type(error).__name__}")
#: 5.0
#: '0': ValueError
