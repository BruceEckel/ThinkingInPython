# class_var.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0  # One shared value, not per-instance
    label: str  # A normal instance variable

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

a = Tally("a")
b = Tally("b")
print(Tally.total)  # 2: shared by the whole class
# a.total = 99  # ty: cannot assign ClassVar "total" via instance
