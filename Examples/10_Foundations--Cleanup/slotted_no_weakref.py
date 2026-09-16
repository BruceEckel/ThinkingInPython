# slotted_no_weakref.py
from weakref import finalize
from exceptions import expect

class Slotted:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

expect(TypeError, finalize, Slotted("x"), print, "closed")
#: [TypeError] cannot create weak reference to 'Slotted'
#: object
