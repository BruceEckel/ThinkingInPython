# sharing.py
from frozen_sketch import Drawing

before = Drawing("Duck").draw("circle")
after = before.draw("beak")
print(after.strokes[0] is before.strokes[0])
#: True
print(after.strokes is before.strokes, len(after.strokes))
#: False 2
