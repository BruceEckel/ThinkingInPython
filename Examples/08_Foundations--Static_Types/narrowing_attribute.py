# narrowing_attribute.py

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

try:
    show(Box("hi"))
except AttributeError as e:
    print(e)
#: 'NoneType' object has no attribute 'upper'
