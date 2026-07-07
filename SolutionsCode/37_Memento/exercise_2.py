# exercise_2.py
class History[S]:
    def __init__(self, initial: S, max_depth: int) -> None:
        self._present = initial
        self._past: list[S] = []
        self._future: list[S] = []
        self._max_depth = max_depth

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        if len(self._past) > self._max_depth:
            self._past.pop(0)  # Discard the oldest
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        self._future.append(self._present)
        self._present = self._past.pop()
        return self._present

    def can_undo(self) -> bool:
        return bool(self._past)

h = History(0, max_depth=2)
h.do(1)
h.do(2)
h.do(3)   # Past would be [0, 1, 2]; 0 is discarded, keeping only 2
print(h._past)
#: [1, 2]
print(h.undo(), h.undo())
#: 2 1
print(h.can_undo())
#: False
