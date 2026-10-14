# rats_and_mazes/rats_and_mazes.py
import asyncio
from blackboard import Blackboard
from maze import Maze

async def main() -> None:
    maze = Maze.from_file("amaze.txt")
    blackboard = Blackboard(maze)
    await blackboard.explore()
    for message in blackboard.messages:
        print(message)
    print("Mapped maze (# wall, . visited):")
    print(blackboard.render())
    print(f"{len(blackboard.messages)} rats mapped "
          f"{len(blackboard.visited)} cells.")

asyncio.run(main())
#: Rat 1 ran (1, 1) to (7, 5).
#: Rat 2 ran (6, 3) to (3, 3).
#: Rat 3 ran (6, 1) to (15, 1).
#: Rat 5 ran (12, 13) to (19, 13).
#: Rat 6 ran (8, 9) to (9, 11).
#: Rat 9 ran (16, 5) to (17, 5).
#: Rat 8 ran (15, 6) to (13, 5).
#: Rat 7 ran (10, 9) to (13, 9).
#: Rat 4 ran (18, 1) to (1, 13).
#: Mapped maze (# wall, . visited):
#: #####################
#: #.#...........#.....#
#: #.#.#.#######.###.#.#
#: #.#.#.......#.....#.#
#: #.#####.###.#######.#
#: #.....#.#...#.....#.#
#: #####.###.#####.###.#
#: #...#.....#.....#...#
#: #.#.#######.###.#.###
#: #.#.........#...#...#
#: #.#####.#.#########.#
#: #.....#.#.#.........#
#: #####.#.###.#########
#: #.....#.............#
#: #####################
#: 9 rats mapped 139 cells.
