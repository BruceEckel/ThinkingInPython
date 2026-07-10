# box_view.py
import tkinter as tk
from box_observer import BoxModel, Grid

def show(model: BoxModel, cell: int = 60) -> None:
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

    model.subscribe(draw)   # Repaint on every model change
    canvas.bind("<Button-1>",
                lambda e: model.click((e.x // cell, e.y // cell)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
