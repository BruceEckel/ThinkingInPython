# rats_and_mazes/rats_view.py
# A tkinter view of the rats mapping the maze. The model (maze.py,
# blackboard.py, rat.py) does the exploring. This file runs it and
# replays the order the cells were claimed as an animation. The model
# itself is checked headlessly in test_ratsandmazes.py.
import asyncio
import tkinter as tk
from typing import override
from blackboard import Blackboard
from maze import Maze

CELL = 26

class RecordingBlackboard(Blackboard):
    "A blackboard that also remembers the order cells were claimed."
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.order: list[tuple[int, int]] = []

    @override
    def claim(self, x: int, y: int) -> bool:
        claimed = super().claim(x, y)
        if claimed:
            self.order.append((x, y))
        return claimed

def show(layout: str = "amaze.txt", step_ms: int = 60) -> None:
    "Run the rats, then replay the cells they claimed, in order."
    maze = Maze.from_file(layout)
    board = RecordingBlackboard(maze)
    asyncio.run(board.explore())

    root = tk.Tk()
    root.title("Rats and Mazes")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=maze.width * CELL,
                       height=maze.height * CELL)
    canvas.pack()

    def box(x: int, y: int, color: str) -> None:
        canvas.create_rectangle(
            x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
            fill=color, outline="gray")

    for y in range(maze.height):
        for x in range(maze.width):
            box(x, y, "white" if maze.is_open(x, y) else "dimgray")

    cells = iter(board.order)

    def step() -> None:
        cell = next(cells, None)
        if cell is not None:
            box(cell[0], cell[1], "palegreen")
            root.after(step_ms, step)

    step()
    root.mainloop()

if __name__ == "__main__":
    show()
