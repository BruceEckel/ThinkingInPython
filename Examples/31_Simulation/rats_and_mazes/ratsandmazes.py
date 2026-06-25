# rats_and_mazes/ratsandmazes.py
# Turn a pack of rats loose on the maze and print what they mapped.

import asyncio
from blackboard import Blackboard
from maze import Maze

async def main() -> None:
    maze = Maze.from_file("amaze.txt")
    blackboard = Blackboard(maze)
    await blackboard.explore()
    print("Mapped maze (# wall, . visited):")
    print(blackboard.render())
    print(f"{len(blackboard.tasks)} rats mapped "
          f"{len(blackboard.visited)} cells.")

asyncio.run(main())
## Mapped maze (# wall, . visited):
## #####################
## #.#...........#.....#
## #.#.#.#######.###.#.#
## #.#.#.......#.....#.#
## #.#####.###.#######.#
## #.....#.#...#.....#.#
## #####.###.#####.###.#
## #...#.....#.....#...#
## #.#.#######.###.#.###
## #.#.........#...#...#
## #.#####.#.#########.#
## #.....#.#.#.........#
## #####.#.###.#########
## #.....#.............#
## #####################
## 9 rats mapped 139 cells.
