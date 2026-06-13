# Observer/BoxObserver.py
# A headless version of the ColorBoxes Observer example. Boxes in a grid
# observe a shared Observable; "clicking" one recolors its neighbors.
import sys
from typing import Any

sys.path += ['../Util']
from Observer import Observer, Observable  # type: ignore


class BoxObservable(Observable):
    # You must subclass Observable and call setChanged(), or notify does nothing:
    def notifyObservers(self, arg: Any = None) -> None:
        self.setChanged()
        Observable.notifyObservers(self, arg)


class Box(Observer):
    def __init__(self, x: int, y: int, color: str,
                 notifier: BoxObservable) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.notifier = notifier
        notifier.addObserver(self)

    def click(self) -> None:
        # A click announces this box to every observer:
        self.notifier.notifyObservers(self)

    def update(self, observable: Any, clicked: "Box") -> None:
        if self is not clicked and self.next_to(clicked):
            self.color = clicked.color

    def next_to(self, other: "Box") -> bool:
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1


def make_grid(size: int, notifier: BoxObservable) -> list[list["Box"]]:
    return [[Box(x, y, f"color{(x + y) % 3}", notifier)
             for y in range(size)]
            for x in range(size)]


if __name__ == "__main__":
    notifier = BoxObservable()
    grid = make_grid(5, notifier)
    center = grid[2][2]
    center.color = "red"
    center.click()
    print(f"(1,1) -> {grid[1][1].color}")
    print(f"(2,3) -> {grid[2][3].color}")
    print(f"(0,0) -> {grid[0][0].color}")
    assert grid[1][1].color == "red"   # diagonally adjacent: changed
    assert grid[2][3].color == "red"   # adjacent: changed
    assert grid[0][0].color != "red"   # two away: unchanged
    print("Observer notifications verified.")
