# exercise_8.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(type(self.number) is int,
              f"Stars({self.number!r})", "needs an int")
        check(1 <= self.number <= 10,
              f"Stars({self.number})")

print(Stars(5))
#: Stars(number=5)
for bad in (5.5, True, "five"):
    expect(TypeFailure, Stars, bad)  # type: ignore
#: [TypeFailure] Stars(5.5) needs an int
#: [TypeFailure] Stars(True) needs an int
#: [TypeFailure] Stars('five') needs an int

print(issubclass(bool, int), isinstance(True, int))
#: True True
