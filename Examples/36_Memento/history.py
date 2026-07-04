# history.py

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

    def redo(self) -> S:
        self._past.append(self._present)
        self._present = self._future.pop()
        return self._present

    def can_undo(self) -> bool:
        return bool(self._past)

    def can_redo(self) -> bool:
        return bool(self._future)

if __name__ == "__main__":
    from frozen_sketch import Sketch
    history = History(Sketch("Duck"))
    history.do(history.present.draw("circle"))
    history.do(history.present.draw("beak"))
    print(history.present)
    print(history.undo())
    print(history.redo())
#: Duck: circle beak
#: Duck: circle
#: Duck: circle beak
