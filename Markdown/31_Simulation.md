# Simulation

A simulation models a system as a set of objects that act on their own and interact through shared state.
This chapter works one example from end to end: a pack of rats mapping a maze.
It puts asyncio tasks, a shared coordination object,
and structural typing together in one small program.

## Rats & Mazes

The problem has three objects.

A *maze* knows its own layout and little else.
Given a coordinate, it reports whether each neighboring cell is a wall or an opening,
and it can hand out an entry point.
The maze never decides anything.
It only answers questions.

A *blackboard* is the shared surface every rat writes to.
The blackboard is a classic coordination idea:
independent agents read from and write to one common data structure instead of talking to each other directly.
Here the blackboard owns the maze, records which cells have been explored,
hands out rat numbers, and launches new rats.
The rats run as cooperative `asyncio` tasks.
They take turns instead of running at the same instant, so no lock is needed:
a rat is never interrupted partway through an update.

A *rat* explores.
Each rat runs as its own task.
From its current cell it looks at the four neighbors and tries to claim the open ones.
Claiming a cell is how a rat both marks it visited and reserves it,
so no two rats ever cover the same ground.
When a rat finds more than one open neighbor,
it keeps the first for itself and spawns a new rat down each of the others,
then yields so its siblings can run.
When it can claim nothing, it has reached a dead end and its task ends.
When the last rat dies, the maze is fully mapped.

The rat does not import the blackboard.
It only needs an object with the right methods,
so a `Protocol` describes what it expects.
This is the structural typing from the [Static Typing](07_Static_Typing.md) chapter.
The rat works with anything that can claim a cell, spawn a rat,
record a message, and hand out a number.

```python
# rats_and_mazes/rat.py
# A rat explores the maze as its own task, spawning a new rat at every
# branch. It talks to a blackboard but never imports one: any object
# with the four methods below will do.

import asyncio
from typing import Protocol

# South, north, west, east.
DIRECTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]


class Recorder(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...


class Rat:
    def __init__(self, blackboard: Recorder, x: int, y: int) -> None:
        self.blackboard = blackboard
        self.x = x
        self.y = y
        self.number = blackboard.next_number()
        blackboard.log(f"Rat {self.number} starts at {(x, y)}.")

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy) for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                self.blackboard.log(
                    f"Rat {self.number} dead-ends "
                    f"at {(self.x, self.y)}.")
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)  # Yield so sibling rats can run.
```

The maze is a grid of characters.
A `*` is a wall and a space is an opening.
Out-of-bounds coordinates count as walls, so the rats stay inside.

```python
# rats_and_mazes/maze.py
# Reads a maze layout and reports walls, openings, and an entry point.

from pathlib import Path
from typing import Self


class Maze:
    WALL = "*"
    OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [r.ljust(self.width, self.WALL) for r in rows]

    @classmethod
    def from_text(cls, text: str) -> Self:
        rows = [line for line in text.splitlines()
                if line and not line.lstrip().startswith("#")]
        return cls(rows)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        return cls.from_text(
            Path(filename).read_text(encoding="utf-8"))

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.OPEN)

    def entry(self) -> tuple[int, int]:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")
```

The blackboard holds everything the rats share.
`claim()` is the heart of the program.
It tests and marks a cell in one step with no `await` in between,
so a cell is handed to exactly one rat even when several reach it.
`explore()` claims the entry, releases the first rat, then awaits every task,
including the ones spawned along the way.

```python
# rats_and_mazes/blackboard.py
# The shared surface the rats write to. It owns the maze, records
# visited cells, hands out rat numbers, and launches rats. Cooperative
# async has no preemption, so no lock is needed.

import asyncio
import itertools

from maze import Maze
from rat import Rat


class Blackboard:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: set[tuple[int, int]] = set()
        self.tasks: list[asyncio.Task[None]] = []
        self.messages: list[str] = []
        self._numbers = itertools.count(1)

    def claim(self, x: int, y: int) -> bool:
        # No await between the test and the add, so this is atomic.
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(asyncio.create_task(rat.run()))

    def next_number(self) -> int:
        return next(self._numbers)

    def log(self, message: str) -> None:
        self.messages.append(message)

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        self.spawn(*start)
        # Wait for every rat, including ones spawned while we wait.
        while pending := [t for t in self.tasks if not t.done()]:
            await asyncio.gather(*pending)

    def render(self) -> str:
        lines = []
        for y in range(self.maze.height):
            row = []
            for x in range(self.maze.width):
                if not self.maze.is_open(x, y):
                    row.append("#")
                elif (x, y) in self.visited:
                    row.append(".")
                else:
                    row.append(" ")
            lines.append("".join(row))
        return "\n".join(lines)
```

The maze layout lives in a text file.
The loader skips blank lines and the path comment,
so the file is the maze and nothing else.

```text
# rats_and_mazes/amaze.txt
*********************
* *           *     *
* * * ******* *** * *
* * *       *     * *
* ***** *** ******* *
*     * *   *     * *
***** *** ***** *** *
*   *     *     *   *
* * ******* *** * ***
* *         *   *   *
* ***** * ********* *
*     * * *         *
***** * *** *********
*     *             *
*********************
```

Running it turns the rats loose and prints what they mapped.

```python
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


if __name__ == "__main__":
    asyncio.run(main())
```

Because claiming is atomic,
the rats always cover every cell reachable from the entry,
no matter how the tasks interleave.
A test pins that down by comparing the cells the rats visited against a plain flood fill of the same maze.

```python
# rats_and_mazes/test_ratsandmazes.py
import asyncio

from blackboard import Blackboard
from maze import Maze

LAYOUT = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""


def flood(maze: Maze, start: tuple[int, int]) -> set[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not maze.is_open(x, y):
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def test_rats_map_every_reachable_cell() -> None:
    maze = Maze.from_text(LAYOUT)
    blackboard = Blackboard(maze)
    asyncio.run(blackboard.explore())
    assert blackboard.visited == flood(maze, maze.entry())
```

The same model drives a view.
`rats_view.py` runs the exploration to completion,
records the order the cells were claimed,
and replays that order on a `tkinter` canvas: walls in gray,
then each claimed cell turning green in turn,
so you watch the pack flood the maze from the entry outward.
It only draws, so the harness skips it (`tools/norun.txt`):

```python
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
```

The original Java version of this example was written by Jeremy Meyer.

## A Robot in a Maze

Concurrency is one way to build a simulation.
Object-oriented design is another.
This second example, adapted from my *Atomic Kotlin* book,
walks a single robot through a maze.
Its lesson is how polymorphism removes conditionals:
a `Room` asks its occupant what to do,
and each kind of occupant answers for itself.

The occupants are `Item`s.
`Room.enter()` calls `occupant.interact()`,
and the return value is the room the robot ends up in.
A wall keeps the robot where it is, food is eaten and the robot moves in,
a teleport returns a distant room.
There is no `if` or `elif` on the type of occupant anywhere:

```python
# robot_explorer/items.py
# The things that can occupy a room. Room.enter() calls
# occupant.interact(), and each Item subclass decides what happens.
# There is no conditional on the item's type.

from enum import Enum
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from world import Room


class Urge(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class Item:
    symbol = ""

    def interact(self, robot: Robot, room: Room) -> Room:
        return room  # Default: the robot enters the room.

    def __str__(self) -> str:
        return self.symbol


class Robot(Item):
    symbol = "R"

    def __init__(self) -> None:
        self.room: Room | None = None

    def move(self, urge: Urge) -> None:
        assert self.room is not None
        self.room = self.room.doors.open(urge).enter(self)


class Wall(Item):
    symbol = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert robot.room is not None
        return robot.room  # Cannot pass: stay put.


class Food(Item):
    symbol = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten.
        return room


class Teleport(Item):
    symbol = ""  # Set per target letter

    def __init__(self, target: str) -> None:
        self.target = target
        self.target_room: Room | None = None

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert self.target_room is not None
        return self.target_room

    @override
    def __str__(self) -> str:
        return self.target


class Empty(Item):
    symbol = "_"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return room


class Edge(Item):
    symbol = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert robot.room is not None
        return robot.room  # The void outside the maze: stay put.


class EndGame(Item):
    symbol = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        print("Game over!")
        return room


def item_factory(symbol: str) -> Item:
    for item_type in Item.__subclasses__():
        if symbol == item_type.symbol:
            return item_type()
    return Teleport(symbol)  # Anything else is a teleport target.
```

`item_factory()` turns a maze character into an `Item`.
It searches `Item.__subclasses__()` for a matching `symbol`,
so adding a new kind of item needs no change here:
define the subclass with its symbol and the factory finds it.
This is the registry idea from the [Factory](24_Factory.md) chapter,
using the class hierarchy itself as the registry.

A `Room` holds one item and connects to its neighbors through a `Doors` object.
Doors that lead nowhere point at one shared `EDGE` room,
the void outside the maze,
so the robot can try any direction without a special case:

```python
# robot_explorer/world.py
# A Room holds one Item and connects to neighbors through its Doors.
# Unset doors point at the shared EDGE room outside the maze.

from items import Edge, Item, Robot, Urge


class Room:
    def __init__(self, occupant: Item) -> None:
        self.occupant = occupant
        self.doors = Doors()

    def enter(self, robot: Robot) -> Room:
        return self.occupant.interact(robot, self)

    def __repr__(self) -> str:
        return f"Room({self.occupant})"


class Doors:
    def __init__(self) -> None:
        self.north: Room | None = None
        self.south: Room | None = None
        self.east: Room | None = None
        self.west: Room | None = None

    def connect(self, row: int, col: int,
                rooms: dict[tuple[int, int], Room]) -> None:
        self.north = rooms.get((row - 1, col))
        self.south = rooms.get((row + 1, col))
        self.east = rooms.get((row, col + 1))
        self.west = rooms.get((row, col - 1))

    def open(self, urge: Urge) -> Room:
        neighbor = {
            Urge.NORTH: self.north,
            Urge.SOUTH: self.south,
            Urge.EAST: self.east,
            Urge.WEST: self.west,
        }[urge]
        return neighbor if neighbor is not None else EDGE


# Created once both classes exist; its own doors stay unset.
EDGE = Room(Edge())
```

`GameBuilder` assembles the maze in stages: a room for every character,
then the connections between rooms, then the teleport pairs.
Building in stages, instead of in one tangled constructor,
is the *Builder* pattern.
`run()` walks a string of moves, and `show_maze()` renders the current state:

```python
# robot_explorer/game.py
# The Builder pattern: build the maze in stages, then run it.

from items import Empty, Robot, Teleport, Urge, item_factory
from world import Room


class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: dict[tuple[int, int], Room] = {}
        teleports: list[Room] = []
        # Stage 1: a Room for every character.
        for row, line in enumerate(maze.splitlines()):
            for col, char in enumerate(line):
                occupant = item_factory(char)
                if isinstance(occupant, Robot):
                    room = Room(Empty())
                    self.robot = occupant
                    self.robot.room = room
                else:
                    room = Room(occupant)
                self.rooms[row, col] = room
                if isinstance(occupant, Teleport):
                    teleports.append(room)
        # Stage 2: connect each room to its neighbors.
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        # Stage 3: pair the teleports that share a target letter.
        def target(room: Room) -> str:
            assert isinstance(room.occupant, Teleport)
            return room.occupant.target

        teleports.sort(key=target)
        pairs = iter(teleports)
        for room1, room2 in zip(pairs, pairs):
            assert isinstance(room1.occupant, Teleport)
            assert isinstance(room2.occupant, Teleport)
            room1.occupant.target_room = room2
            room2.occupant.target_room = room1

    def show_maze(self) -> str:
        rows: list[str] = []
        current = -1
        for (row, _), room in self.rooms.items():
            if row != current:
                rows.append("")
                current = row
            if room is self.robot.room:
                rows[-1] += str(self.robot)
            else:
                rows[-1] += str(room.occupant)
        return "\n".join(rows)

    def run(self, solution: str) -> None:
        moves = {"n": Urge.NORTH, "s": Urge.SOUTH,
                 "e": Urge.EAST, "w": Urge.WEST}
        for char in "".join(solution.split()):
            self.robot.move(moves[char])


string_maze = """
###############################
#R#.____#____.#_______#_______#
#_###_#_###_#_#_#_#####_#####_#
#___#_#___#_#_#_#.#__b__#___#_#
###_#_###_#_#_###_#_#####_#_#_#
#.#_#_#.__#_#__.#_#__b__#_#___#
#_#_#_#_###_###_#_#####_#_#####
#_#_#_#__.#_#_#_____#___#_____#
#_#_#_###_#_#_#_#####_#######_#
#.#___#___#_#___#____.#_____#_#
#_#####_###_#_###_#####_#_###_#
#___#a__#.__#.__#__.#___#_#___#
#_#_#_###_#####_###_###_###_#_#
#_#.#_#___#!______#_____#___#_#
#_#_#_###_#############_#_###_#
#_#_#__a#_______________#___#_#
#_#####_###_###########_###_#_#
#_____#.__#_#___#_____#_#___#_#
#_#_#####_###_#_#_###_###_###_#
#.#___________#___#____.__#___#
###############################
""".strip()

solution = (
    "sseesssssseennnnnnnneesseesswwsseesswwsswwsseesseeeenneessee"
    "nneeeesseeeenneennwwnneenneennnnwwwwnnnneesseennnnwwwwwwssww"
    "eesswwsswwwwsseesseeeesswwwwwwwwwwwwwwnnnneennnnnnnnnneessss"
    "eesssswwsseesswwww"
)

if __name__ == "__main__":
    game = GameBuilder(string_maze)
    print("start:")
    print(game.show_maze())
    game.run(solution)
    print("\nfinal:")
    print(game.show_maze())
```

Running it prints the maze before and after the walk.
The robot eats the food along its path, takes a teleport,
and reaches the `!` that ends the game:

    start:
    ###############################
    #R#.____#____.#_______#_______#
    #_###_#_###_#_#_#_#####_#####_#
    #___#_#___#_#_#_#.#__b__#___#_#
    ###_#_###_#_#_###_#_#####_#_#_#
    #.#_#_#.__#_#__.#_#__b__#_#___#
    #_#_#_#_###_###_#_#####_#_#####
    #_#_#_#__.#_#_#_____#___#_____#
    #_#_#_###_#_#_#_#####_#######_#
    #.#___#___#_#___#____.#_____#_#
    #_#####_###_#_###_#####_#_###_#
    #___#a__#.__#.__#__.#___#_#___#
    #_#_#_###_#####_###_###_###_#_#
    #_#.#_#___#!______#_____#___#_#
    #_#_#_###_#############_#_###_#
    #_#_#__a#_______________#___#_#
    #_#####_###_###########_###_#_#
    #_____#.__#_#___#_____#_#___#_#
    #_#_#####_###_#_#_###_###_###_#
    #.#___________#___#____.__#___#
    ###############################
    Game over!

    final:
    ###############################
    #_#.____#_____#_______#_______#
    #_###_#_###_#_#_#_#####_#####_#
    #___#_#___#_#_#_#.#__b__#___#_#
    ###_#_###_#_#_###_#_#####_#_#_#
    #.#_#_#___#_#___#_#__b__#_#___#
    #_#_#_#_###_###_#_#####_#_#####
    #_#_#_#___#_#_#_____#___#_____#
    #_#_#_###_#_#_#_#####_#######_#
    #.#___#___#_#___#_____#_____#_#
    #_#####_###_#_###_#####_#_###_#
    #___#a__#___#___#___#___#_#___#
    #_#_#_###_#####_###_###_###_#_#
    #_#.#_#___#R______#_____#___#_#
    #_#_#_###_#############_#_###_#
    #_#_#__a#_______________#___#_#
    #_#####_###_###########_###_#_#
    #_____#___#_#___#_____#_#___#_#
    #_#_#####_###_#_#_###_###_###_#
    #.#___________#___#_______#___#
    ###############################

The maze rendering, `show_maze()`, returns a string,
so the model's correctness is something a test can pin down with no window in sight.
Build the maze, run the solution,
and check that the robot finished on the `!` square and that the final rendering matches,
food eaten and all:

```python
# robot_explorer/test_robot.py
from game import GameBuilder, solution, string_maze
from items import EndGame

FINISHED = """
###############################
#_#.____#_____#_______#_______#
#_###_#_###_#_#_#_#####_#####_#
#___#_#___#_#_#_#.#__b__#___#_#
###_#_###_#_#_###_#_#####_#_#_#
#.#_#_#___#_#___#_#__b__#_#___#
#_#_#_#_###_###_#_#####_#_#####
#_#_#_#___#_#_#_____#___#_____#
#_#_#_###_#_#_#_#####_#######_#
#.#___#___#_#___#_____#_____#_#
#_#####_###_#_###_#####_#_###_#
#___#a__#___#___#___#___#_#___#
#_#_#_###_#####_###_###_###_#_#
#_#.#_#___#R______#_____#___#_#
#_#_#_###_#############_#_###_#
#_#_#__a#_______________#___#_#
#_#####_###_###########_###_#_#
#_____#___#_#___#_____#_#___#_#
#_#_#####_###_#_#_###_###_###_#
#.#___________#___#_______#___#
###############################
""".strip()


def test_solution_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solution)
    room = game.robot.room
    assert room is not None
    assert isinstance(room.occupant, EndGame)  # Finished on the "!"
    assert game.show_maze() == FINISHED  # Food eaten, robot moved


def test_walls_block_and_food_is_eaten() -> None:
    game = GameBuilder("R.#")  # Robot, food, wall in one row
    start = game.robot.room
    game.run("e")  # east: eat the food and move in
    assert "." not in game.show_maze()  # Food gone
    assert game.robot.room is not start
    blocked = game.robot.room
    game.run("e")  # East again: a wall, so stay put
    assert game.robot.room is blocked
```

That same model drives a graphical view, in its own file.
It imports the maze and the moves, draws each room as a colored cell,
and steps the robot along the solution on a timer.
The view is the only part that touches the screen.
Run it to watch the walk; it opens a window,
so the example harness skips it (listed in `tools/norun.txt`):

```python
# robot_explorer/maze_view.py
# A tkinter view of the robot maze. The model (items.py, world.py,
# game.py) holds the maze and the rules; this file only draws, and
# steps the robot through the solution one move at a time. Run it to
# watch. The same model is checked headlessly in test_robot.py.
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
```

Two patterns from earlier chapters carry the design:
polymorphism replaces a type switch, and a factory builds objects from data.
Neither needs concurrency.

## Other Maze Resources

A discussion of algorithms to create mazes:

<http://www.mazeworks.com/mazegen/mazegen.htm>

A discussion of algorithms for collision detection and steering behavior for autonomous moving objects:

<http://www.red3d.com/cwr/steer/>

## Exercises

1.  Test a `Rat` with a fake blackboard.
    Because `Rat` depends only on the `Recorder` `Protocol`,
    you can drive it with a stand-in.
    Write a fake whose `claim()` returns a scripted sequence of results and whose `spawn()` only records the coordinates it is handed,
    run one rat with `asyncio.run(rat.run())`,
    and assert which cell the rat kept for itself and which cells it spawned.
    No real `Blackboard`, `Maze`, or task scheduling is needed.
2.  Report the cells the rats never reach.
    After `explore()` finishes,
    compare `blackboard.visited` against every open cell of the `Maze` and print the open cells that were never claimed.
    Build a maze for which that set is not empty,
    and explain what makes a cell unreachable.
3.  Break the atomicity of `claim()`.
    Insert an `await asyncio.sleep(0)` between the membership test and `self.visited.add(...)`,
    then run `test_ratsandmazes.py` several times.
    What goes wrong when two rats reach the same cell during that gap,
    and why does the original `claim()`, with no `await` inside it,
    need no lock?
4.  Add a new kind of `Item` to the robot maze.
    Define a `Coin` subclass with the symbol `$` whose `interact()` removes itself the way `Food` does and adds one to a coin count carried by the `Robot`.
    Place a few `$` characters in the maze and report how many the robot collects.
    You should not have to touch `item_factory()`, `Room`, or `GameBuilder`;
    explain why the factory finds your new item on its own.
5.  Compute the solution instead of hard-coding it.
    Write a function that takes a `GameBuilder` and searches the rooms for a path from the robot's room to the `EndGame` room,
    the way `flood()` searches maze cells in `test_ratsandmazes.py`.
    Turn that path into a move string, feed it to `run()`,
    and assert that the robot finishes on the `!` square,
    as `test_robot.py` does.
