# partial_restore.py
import copy
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.apply(lambda d: d.draw("circle"))
checkpoint = history.present
history.apply(lambda d: d.draw("beak"))
history.apply(lambda d: copy.replace(d, title="Goose"))
history.apply(lambda d: d.draw("scribble"))
print(history.present)
#: Goose: circle beak scribble
history.apply(lambda d: copy.replace(
    d, strokes=checkpoint.strokes))
print(history.present)
#: Goose: circle
print(history.undo())
#: Goose: circle beak scribble
