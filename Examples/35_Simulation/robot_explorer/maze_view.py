# robot_explorer/maze_view.py
import tkinter as tk
from game import GameBuilder, solution, string_maze
from items import Urge

CELL = 20
FILL = {"#": "dimgray", "!": "tomato", ".": "khaki",
        "_": "white", "R": "royalblue"}
MOVES = {"n": Urge.NORTH, "s": Urge.SOUTH,
         "e": Urge.EAST, "w": Urge.WEST}

def show(maze: str = string_maze, moves: str = solution,
         step_ms: int = 80) -> None:
    "Draw the maze and step the robot through the moves."
    game = GameBuilder(maze)
    rows = maze.splitlines()
    width = max(len(row) for row in rows)
    root = tk.Tk()
    root.title("Robot in a Maze")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=width * CELL, height=len(rows) * CELL)
    canvas.pack()

    def draw() -> None:
        canvas.delete("all")
        for (row, col), room in game.rooms.items():
            symbol = ("R" if room is game.robot.room
                      else str(room.occupant))
            canvas.create_rectangle(
                col * CELL, row * CELL,
                (col + 1) * CELL, (row + 1) * CELL,
                fill=FILL.get(symbol, "palegreen"), outline="gray")

    queue = list("".join(moves.split()))

    def step() -> None:
        draw()
        if queue:
            game.robot.move(MOVES[queue.pop(0)])
            root.after(step_ms, step)

    step()
    root.mainloop()

if __name__ == "__main__":
    show()
