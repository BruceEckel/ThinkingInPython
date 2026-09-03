# slotted_no_weakref.py
from weakref import finalize

class Slotted:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

try:
    finalize(Slotted("x"), print, "closed")
except TypeError as e:
    print(type(e).__name__)
#: TypeError
