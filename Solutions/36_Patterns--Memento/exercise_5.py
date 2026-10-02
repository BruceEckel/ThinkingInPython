# exercise_5.py
from exceptions import expect

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
        previous = self._past.pop()
        self._future.append(self._present)
        self._present = previous
        return self._present

    def redo(self) -> S:
        following = self._future.pop()
        self._past.append(self._present)
        self._present = following
        return self._present

    def goto(self, steps_back: int) -> S:
        if not 0 <= steps_back <= len(self._past):
            raise IndexError(f"cannot go back {steps_back}")
        for _ in range(steps_back):
            self.undo()
        return self._present

h = History(0)
h.do(1)
h.do(2)
h.do(3)
print(h.goto(2))
#: 1
print(h.redo(), h.redo())
#: 2 3
expect(IndexError, h.goto, 4)
#: [IndexError] cannot go back 4
print(h.present)
#: 3
