# box_observer.py
# A visual ColorBoxes: the model-view split wired with the classic
# Observer. The model holds the grid and announces each change; the
# view observes it and repaints. Every function that computes returns
# a value; only the view's draw() touches the screen.
import tkinter as tk
from typing import Any

from observer import Observable, Observer

COLORS = ("skyblue", "palegreen", "khaki")
type Grid = dict[tuple[int, int], str]   # (column, row) -> color


def new_grid(size: int) -> Grid:
    "Build a size x size grid, banded into three colors."
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}


def adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    "True if two distinct cells touch, including diagonally."
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


def recolored(grid: Grid, clicked: tuple[int, int]) -> Grid:
    "Return a new grid: every neighbor of the click takes its color."
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked) else current
            for cell, current in grid.items()}


class BoxModel(Observable):
    "The subject: holds the grid and announces every change."
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: tuple[int, int]) -> None:
        self.grid = recolored(self.grid, cell)
        self.set_changed()
        self.notify_observers(self.grid)


def show(model: BoxModel, cell: int = 60) -> None:
    "The only function that touches the screen."
    root = tk.Tk()
    root.title("ColorBoxes")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=model.size * cell,
                       height=model.size * cell)
    canvas.pack()

    def draw(grid: Grid) -> None:
        for (x, y), color in grid.items():
            canvas.create_rectangle(
                x * cell, y * cell, (x + 1) * cell, (y + 1) * cell,
                fill=color, outline="white")

    # The observer is the view: repaint when the model changes.
    class View(Observer):
        def update(self, observable: Any, grid: Any) -> None:
            draw(grid)

    model.add_observer(View())
    canvas.bind("<Button-1>",
                lambda e: model.click((e.x // cell, e.y // cell)))
    draw(model.grid)
    root.mainloop()


if __name__ == "__main__":
    show(BoxModel(8))
