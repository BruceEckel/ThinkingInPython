# counter_near_miss.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
