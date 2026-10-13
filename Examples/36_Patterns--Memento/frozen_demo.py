# frozen_demo.py
from frozen_sketch import Drawing

before = Drawing("Duck").draw("circle").draw("beak")
after = before.draw("scribble")
print(after)
#: Duck: circle beak scribble
print(before)
#: Duck: circle beak
