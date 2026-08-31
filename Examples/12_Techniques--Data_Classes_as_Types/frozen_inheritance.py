# frozen_inheritance.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Frozen:
    a: int

@dataclass
class Plain:
    a: int

try:
    @dataclass
    class Thawed(Frozen):  # type: ignore
        b: int
except TypeError as e:
    print(e)
#: cannot inherit non-frozen dataclass from a frozen one

try:
    @dataclass(frozen=True)
    class Chilled(Plain):  # type: ignore
        b: int
except TypeError as e:
    print(e)
#: cannot inherit frozen dataclass from a non-frozen one
