# slotted_no_weakref.py
from weakref import finalize
from exceptions import expect

class Slot:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

expect(TypeError, finalize, Slot("x"), print, "closed")
#: [TypeError] cannot create weak reference to 'Slot' object

class WeakSlot:
    __slots__ = ("name", "__weakref__")

    def __init__(self, name: str) -> None:
        self.name = name

finalize(WeakSlot("y"), print, "y", "closed")
#: y closed
