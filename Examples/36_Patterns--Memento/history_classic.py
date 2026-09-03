# history_classic.py
from history import History
from sketch import Memento, Sketch

sketch = Sketch()
sketch.draw("circle")
history: History[Memento] = History(
    sketch.save())
sketch.draw("beak")
history.do(sketch.save())
sketch.restore(history.undo())
print(sketch)
#: circle
