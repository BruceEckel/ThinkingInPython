# frozen_inheritance.py
from dataclasses import dataclass
from exceptions import expected

@dataclass(frozen=True)
class Frozen:
    a: int

@dataclass
class Plain:
    a: int

with expected(TypeError):
    @dataclass
    class Thawed(Frozen):  # type: ignore
        b: int
#: [TypeError] cannot inherit non-frozen dataclass from a
#: frozen one

with expected(TypeError):
    @dataclass(frozen=True)
    class Chilled(Plain):  # type: ignore
        b: int
#: [TypeError] cannot inherit frozen dataclass from a non-
#: frozen one
