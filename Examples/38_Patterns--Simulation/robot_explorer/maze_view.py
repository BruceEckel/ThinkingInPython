# robot_explorer/maze_view.py
import tkinter as tk
from typing import Final
from game import GameBuilder
from items import Urge
from robot_maze import string_maze
from solver import solve

CELL: Final[int] = 20
FILL: Final[dict[str, str]] = {
    "#": "dimgray", "!": "tomato", ".": "khaki",
    "_": "white", "R": "royalblue"}
MOVES: Final[dict[str, Urge]] = {
    "n": Urge.NORTH, "s": Urge.SOUTH,
    "e": Urge.EAST, "w": Urge.WEST}

def show(maze: str = string_maze,
         step_ms: int = 80) -> None:
    game = GameBuilder(maze)
    moves = solve(game)
    rows = maze.splitlines()
    width = max(len(row) for row in rows)
    root = tk.Tk()
    root.title("Robot in a Maze")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=width * CELL,
                       height=len(rows) * CELL)
    canvas.pack()

    def draw() -> None:
        canvas.delete("all")
        for (row, col), room in game.rooms.items():
            symbol = ("R" if room is game.robot.room
                      else str(room.occupant))
            canvas.create_rectangle(
                col * CELL, row * CELL,
                (col + 1) * CELL, (row + 1) * CELL,
                fill=FILL.get(symbol, "palegreen"),
                outline="gray")

    route = iter(moves)

    def step() -> None:
        draw()
        move = next(route, None)
        if move is not None:
            game.robot.move(MOVES[move])
            root.after(step_ms, step)

    step()
    root.mainloop()

if __name__ == "__main__":
    show()
