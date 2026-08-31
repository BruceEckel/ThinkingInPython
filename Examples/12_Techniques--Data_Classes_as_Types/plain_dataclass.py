# plain_dataclass.py
from dataclasses import dataclass
from comparison import show

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

print(C.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
