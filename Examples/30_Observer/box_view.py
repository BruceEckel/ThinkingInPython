# box_view.py
import tkinter as tk
from box_observer import BoxModel, Grid

def show(model: BoxModel, cell_px: int = 60) -> None:
    root = tk.Tk()
    root.title("ColorBoxes")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=model.size * cell_px,
                       height=model.size * cell_px)
    canvas.pack()

    def draw(grid: Grid) -> None:
        # Or the old rectangles accumulate
        canvas.delete("all")
        for (x, y), color in grid.items():
            canvas.create_rectangle(
                x * cell_px, y * cell_px,
                (x + 1) * cell_px, (y + 1) * cell_px,
                fill=color, outline="white")

    model.subscribe(draw)  # Repaint on every model change
    canvas.bind("<Button-1>",
                lambda e: model.click(
                    (e.x // cell_px, e.y // cell_px)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
