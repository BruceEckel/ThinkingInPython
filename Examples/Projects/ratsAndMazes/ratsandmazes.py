# Projects/ratsAndMazes/ratsandmazes.py
# Turn a pack of rats loose on the maze and print what they mapped.
from __future__ import annotations

from blackboard import Blackboard
from maze import Maze


def main() -> None:
    maze = Maze.from_file("amaze.txt")
    blackboard = Blackboard(maze)
    blackboard.explore()
    print("Mapped maze (# wall, . visited):")
    print(blackboard.render())
    print(f"{len(blackboard.threads)} rats mapped "
          f"{len(blackboard.visited)} cells.")


if __name__ == "__main__":
    main()
