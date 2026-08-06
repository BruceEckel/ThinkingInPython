# exercise_5.py
import copy
from dataclasses import dataclass
from typing import Self

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

class Stars:
    def __init__(self, number: int) -> None:
        check(1 <= number <= 10, f"Stars({number})")
        self.number = number

    def __repr__(self) -> str:
        return f"Stars({self.number})"

    def __replace__(self, **changes: int) -> Self:
        return type(self)(**({"number": self.number} | changes))

s = Stars(4)
print(copy.replace(s, number=9))
#: Stars(9)
try:
    copy.replace(s, number=99)
except TypeFailure as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(99)
