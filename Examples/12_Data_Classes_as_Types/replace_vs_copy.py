# replace_vs_copy.py
import copy
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        print(f"checking {self.number}")
        check(1 <= self.number <= 10, f"Stars({self.number})")

s = Stars(4)
#: checking 4
print(copy.replace(s, number=2))
#: checking 2
#: Stars(number=2)
print(copy.copy(s))
#: Stars(number=4)
print(copy.deepcopy(s))
#: Stars(number=4)
