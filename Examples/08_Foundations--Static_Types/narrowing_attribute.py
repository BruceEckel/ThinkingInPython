# narrowing_attribute.py
from exceptions import expect

class Box:
    def __init__(self, val: str | None) -> None:
        self.val = val

    def reset(self) -> None:
        self.val = None

def show(b: Box) -> str:
    if b.val is not None:
        b.reset()  # ty can't see this clears val
        return b.val.upper()
    return "(nothing)"

expect(AttributeError, show, Box("hi"))
#: [AttributeError] 'NoneType' object has no attribute
#: 'upper'
