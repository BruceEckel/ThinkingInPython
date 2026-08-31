# exercise_6.py
import copy
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

class History[S]:
    def __init__(self, initial: S) -> None:
        self._present = initial
        self._past: list[S] = []
        self._future: list[S] = []

    @property
    def present(self) -> S:
        return self._present

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        self._future.append(self._present)
        self._present = self._past.pop()
        return self._present

def restore_field(
    history: History[Drawing], name: str, past: Drawing
) -> None:
    change = {name: getattr(past, name)}
    history.do(copy.replace(history.present, **change))

history = History(Drawing("Duck"))
history.do(history.present.draw("body"))
checkpoint = history.present
history.do(copy.replace(history.present, title="Goose"))
history.do(history.present.draw("beak"))
history.do(history.present.draw("tail"))
print(history.present)
#: Drawing(title='Goose', strokes=('body', 'beak', 'tail'))
restore_field(history, "strokes", checkpoint)
print(history.present)
#: Drawing(title='Goose', strokes=('body',))
print(history.undo())
#: Drawing(title='Goose', strokes=('body', 'beak', 'tail'))
