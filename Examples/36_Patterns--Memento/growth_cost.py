# growth_cost.py
from frozen_sketch import Drawing

drawing = Drawing("Duck")
pointers = 0
for i in range(2000):
    drawing = drawing.draw(str(i))
    pointers += len(drawing.strokes)
print(pointers, len(drawing.strokes))
#: 2001000 2000
