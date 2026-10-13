# exercise_2.py
from collections import deque

class History[S]:
    def __init__(self, initial: S, max_depth: int) -> None:
        self._present = initial
        self._past: deque[S] = deque(maxlen=max_depth)
        self._future: list[S] = []

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        previous = self._past.pop()
        self._future.append(self._present)
        self._present = previous
        return self._present

    def can_undo(self) -> bool:
        return bool(self._past)

h = History(0, max_depth=2)
h.do(1)
h.do(2)
# Past would be [0, 1, 2]; the bound discards 0
h.do(3)
print(h._past)
#: deque([1, 2], maxlen=2)
print(h.undo(), h.undo())
#: 2 1
print(h.can_undo())
#: False
