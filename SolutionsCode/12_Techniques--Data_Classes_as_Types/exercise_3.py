# exercise_3.py
import copy
from dataclasses import dataclass
from typing import NamedTuple

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

class _Stars(NamedTuple):
    number: int

class Stars(_Stars):
    def __new__(cls, number: int) -> Stars:
        check(1 <= number <= 10, f"Stars({number})")
        return super().__new__(cls, number)

print(Stars(5))
#: Stars(number=5)
try:
    Stars(11)
except TypeFailure as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(11)

print(Stars(5)._replace(number=99))
#: Stars(number=99)
print(copy.replace(Stars(5), number=99))
#: Stars(number=99)
