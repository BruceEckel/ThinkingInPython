# box_view.py
import tkinter as tk
from typing import Any, override
from box_observer import BoxModel, Grid
from observer import Observer

def show(model: BoxModel, cell: int = 60) -> None:
    "Open the window and keep it in step with the model."
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

    class View(Observer):  # Repaints on every model change
        @override
        def update(self, observable: Any, grid: Any) -> None:
            draw(grid)

    model.add_observer(View())
    canvas.bind("<Button-1>",
                lambda e: model.click((e.x // cell, e.y // cell)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
