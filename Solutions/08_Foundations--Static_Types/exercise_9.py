# exercise_9.py

class Box:
    def __init__(self, val: str | None) -> None:
        self.val = val

    def reset(self) -> None:
        self.val = None

def show(b: Box) -> str:
    val = b.val
    if val is not None:
        b.reset()
        return val.upper()
    return "(nothing)"

box = Box("hi")
print(show(box))
#: HI
print(box.val)
#: None
