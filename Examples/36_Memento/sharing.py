# sharing.py
from frozen_sketch import Drawing

stroke = "".join(["cir", "cle"])
before = Drawing("Duck", (stroke,))
after = before.draw("beak")
print(after.strokes[0] is stroke)
#: True
print(after.strokes is before.strokes, len(after.strokes))
#: False 2
