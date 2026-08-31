# partial_restore.py
import copy
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.do(history.present.draw("circle"))
checkpoint = history.present
history.do(history.present.draw("beak"))
history.do(copy.replace(history.present, title="Goose"))
history.do(history.present.draw("scribble"))
print(history.present)
#: Goose: circle beak scribble
history.do(copy.replace(history.present,
                        strokes=checkpoint.strokes))
print(history.present)
#: Goose: circle
print(history.undo())
#: Goose: circle beak scribble
