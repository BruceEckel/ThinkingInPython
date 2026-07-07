# exercise_3.py
from dataclasses import dataclass

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")

    def f1(self) -> Stars:
        return Stars(self.number + 5)

print(Stars(2).f1())
#: Stars(number=7)
try:
    Stars(4).f1().f1()  # 4+5=9 legal, then 9+5=14 illegal
except TypeFailure as e:
    print("caught postcondition failure:", e)
#: caught postcondition failure: Stars(14)
