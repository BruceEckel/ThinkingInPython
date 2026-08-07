# exercise_7.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
print(vars(a), vars(Tally)["total"])
#: {'total': 1} 0

class Counting:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        Counting.total += 1  # Name the class, not self

c, d = Counting(), Counting()
print(c.total, d.total, Counting.total)
#: 2 2 2
print(vars(c), vars(Counting)["total"])
#: {} 2
