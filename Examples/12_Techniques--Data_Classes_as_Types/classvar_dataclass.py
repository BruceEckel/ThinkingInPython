# classvar_dataclass.py
from dataclasses import dataclass
from typing import ClassVar
from comparison import show
from exceptions import expect

@dataclass
class D:
    x: int = 99
    s: ClassVar[str] = "Initializer"
    f: ClassVar[float]  # No initializer

show(D)
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'Initializer' [CV]
#:   • x: int = 99 [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)

show(D())
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'Initializer' [CV]
#:   • x: int = 99
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)

for k, v in D.__annotations__.items():
    print(f"'{k}': {v}")
#: 'x': <class 'int'>
#: 's': typing.ClassVar[str]
#: 'f': typing.ClassVar[float]
expect(AttributeError, getattr, D, "f")
#: [AttributeError] type object 'D' has no attribute 'f'
