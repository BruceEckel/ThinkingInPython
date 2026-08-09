# rats_and_mazes/rats_and_mazes.py
import asyncio
from blackboard import Blackboard
from maze import Maze

async def main() -> None:
    maze = Maze.from_file("amaze.txt")
    blackboard = Blackboard(maze)
    await blackboard.explore()
    for message in blackboard.messages[:8]:
        print(message)
    print("Mapped maze (# wall, . visited):")
    print(blackboard.render())
    print(f"{len(blackboard.tasks)} rats mapped "
          f"{len(blackboard.visited)} cells.")

asyncio.run(main())
#: Rat 1 starts at (1, 1).
#: Rat 2 starts at (6, 3).
#: Rat 1 dead-ends at (7, 5).
#: Rat 3 starts at (6, 1).
#: Rat 2 dead-ends at (3, 3).
#: Rat 4 starts at (18, 1).
#: Rat 3 dead-ends at (15, 1).
#: Rat 5 starts at (12, 13).
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
