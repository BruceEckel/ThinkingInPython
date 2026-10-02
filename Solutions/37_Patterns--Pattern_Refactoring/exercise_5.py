# exercise_5.py
from functools import singledispatch
from typing import ClassVar
from exceptions import expect
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Paper(Trash):
    value: ClassVar[float] = 0.10

class Plastic(Trash):
    value: ClassVar[float] = 0.15

@singledispatch
def hazard(t: Trash) -> str:
    return "none"

@hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

print(hazard(Plastic(1.0)))
#: none

@singledispatch
def strict_hazard(t: Trash) -> str:
    raise NotImplementedError(
        f"no hazard rule for {type(t).__name__}")

@strict_hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

@strict_hazard.register
def _(t: Paper) -> str:
    return "none"

print(strict_hazard(Paper(1.0)))
#: none
expect(NotImplementedError, strict_hazard, Plastic(1.0))
#: [NotImplementedError] no hazard rule for Plastic
