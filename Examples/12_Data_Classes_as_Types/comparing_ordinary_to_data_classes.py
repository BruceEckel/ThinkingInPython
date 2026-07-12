# comparing_ordinary_to_data_classes.py
from dataclasses import dataclass
from typing import ClassVar
from display import REDEFINED_DUNDERS, display_object

def show(obj: object) -> None:
    display_object(obj, REDEFINED_DUNDERS, exclude=("__hash__",))

class A:
    x: int
    s: str

show(A())
#: [Attributes]
#:   None
#: [Methods]
#:   None

class B:
    x: int = 42
    s: str = "Answer"

show(B())
#: [Attributes]
#:   • s: str = 'Answer' [CV]
#:   • x: int = 42 [CV]
#: [Methods]
#:   None

@dataclass
class C:
    x: int
    s: str

show(C(11, "this is C"))
#: [Attributes]
#:   • s: str = 'this is C'
#:   • x: int = 11
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, s: str) -> None
#:   • __repr__(self)

@dataclass
class D:
    x: int = 99
    s: ClassVar[str] = "this is D"

show(D)
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'this is D' [CV]
#:   • x: int = 99 [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)

show(D())
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'this is D' [CV]
#:   • x: int = 99
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)
