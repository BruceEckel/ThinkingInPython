# partial_restore.py
import copy
from frozen_sketch import Sketch
from history import History

history = History(Sketch("Duck"))
history.do(history.present.draw("circle"))
checkpoint = history.present
history.do(copy.replace(history.present, title="Goose"))
history.do(history.present.draw("scribble"))
print(history.present)
#: Goose: circle scribble
history.do(copy.replace(history.present, strokes=checkpoint.strokes))
print(history.present)
#: Goose: circle
print(history.undo())
#: Goose: circle scribble
