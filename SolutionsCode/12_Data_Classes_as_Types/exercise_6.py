# exercise_6.py
import inspect
from dataclasses import dataclass, fields
from typing import ClassVar

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

@dataclass(frozen=True)
class Stars:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")
        Stars.built += 1

print([f.name for f in fields(Stars)])
#: ['number']
print(inspect.signature(Stars.__init__))
#: (self, number: int) -> None

for n in (3, 4, 5):
    Stars(n)
print(Stars.built)
#: 3

@dataclass(frozen=True)
class Wrong:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        self.built += 1  # type: ignore

try:
    Wrong(1)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'built'
