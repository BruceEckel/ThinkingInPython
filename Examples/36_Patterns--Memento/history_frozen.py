# history_frozen.py
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.apply(lambda d: d.draw("circle"))
history.apply(lambda d: d.draw("beak"))
print(history.present)
#: Duck: circle beak
print(history.undo())
#: Duck: circle
print(history.redo())
#: Duck: circle beak
