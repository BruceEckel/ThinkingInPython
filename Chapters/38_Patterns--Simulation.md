# Simulation

Each object in a simulation follows a rule of its own and knows nothing of the whole.
What the rules produce together, as time steps forward,
can be more than anyone wrote down.

A simulation models a set of objects that act on their own and interact through shared state.
This chapter builds three,
each giving its agents less to work with than the last.
A pack of rats coordinates through a shared blackboard,
a single robot walks a maze where each object it meets decides what happens,
and a plate of vibrating sand runs on grains that hold nothing but a position.
The first two confirm a design you can predict from the code.
The third produces a pattern no one wrote down as a picture:
the formula fixes its shape, and the grains gather on it.

The first example, the pack of rats, puts asyncio tasks,
a shared coordination object,
and structural typing together in one small program.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
introduces the `asyncio` mechanics (`async def`, `await`, `gather`, `run`).

## Rats & Mazes

The problem has three types.

A *maze* holds its own layout.
Given a coordinate, it reports whether each neighboring cell is a wall or an opening,
and it hands out an entry point.
The maze decides nothing; it only reports what a coordinate contains.

A *blackboard* is the shared surface on which every rat writes.
*Blackboard* is a classic coordination pattern.
Independent agents read from and write to one common data structure instead of calling each other directly.
Here the blackboard owns the maze, records which cells the rats have explored,
hands out rat numbers, and creates the task for each new rat.
The rats run as cooperative `asyncio` tasks.
They take turns, one at a time, so the blackboard needs no lock:
each rat finishes its update before the next one runs.

A *rat* explores.
Each rat runs as its own task.
From its current cell it calls `claim()` on each of the four neighbors,
and each open, unclaimed one becomes a move.
Claiming a cell both marks it visited and reserves it,
so no two rats claim the same cell.
When a rat claims more than one neighbor,
it keeps the first for itself and spawns a new rat at each of the others.
After every move it yields so its siblings can run.
When every neighbor is a wall or already claimed,
the rat has reached a dead end and its task ends.
When the last rat's task ends,
the pack has claimed every cell reachable from the entry.

### The Rat and the Blackboard

The rat never imports the blackboard.
It needs only an object with matching methods,
so a `Protocol` describes what it expects.
That `Protocol` is [structural typing](08_Foundations--Static_Types.md#structural-typing-with-protocols).
The rat works with anything that can claim a cell, spawn a rat,
record a message, and hand out a number.

```python
# rats_and_mazes/rat.py
import asyncio
from dataclasses import dataclass, field
from typing import Final, Protocol

# South, north, west, east
DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

class Recorder(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...

@dataclass
class Rat:
    blackboard: Recorder
    x: int
    y: int
    number: int = field(init=False)

    def __post_init__(self) -> None:
        self.number = self.blackboard.next_number()
        self.blackboard.log(
            f"Rat {self.number} starts at "
            f"{(self.x, self.y)}.")

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
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
            # Yield so sibling rats can run
            await asyncio.sleep(0)
```

`number` comes from a call to `blackboard.next_number()`,
which advances a counter, so no static default can supply it.
`field(init=False)` leaves `number` out of the generated `__init__`.
The generated `__init__` calls `__post_init__` as its last step,
when `blackboard`, `x`, and `y` already hold their values,
so `__post_init__` fills in `number` and logs the rat's start.

The maze is a grid of characters.
A `*` is a wall and a space is an opening.
Out-of-bounds coordinates count as walls, so the rats stay inside.

```python
# rats_and_mazes/maze.py
from enum import StrEnum
from pathlib import Path
from typing import Self

type Coord = tuple[int, int]  # (column, row)

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [
            r.ljust(self.width, self.Cell.WALL)
            for r in rows]

    @classmethod
    def from_text(cls, text: str) -> Self:
        rows = [
            line for line in text.splitlines()
            if line and not line.lstrip().startswith("#")]
        return cls(rows)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        return cls.from_text(
            Path(filename).read_text(encoding="utf-8"))

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")
```

`Cell` nests inside `Maze` because it names concepts only `Maze` uses.
It is a `StrEnum` rather than an `Enum`, so each member is also a `str`.
That is why `WALL` serves as the fill character for `ljust()`,
and `self.rows[y][x]` compares equal to `Cell.OPEN` on an open cell.

The blackboard holds everything the rats share.
`claim()` holds the rule the whole program depends on.
It tests and marks a cell in one step with no `await` in between,
so a single rat gets each cell even when several reach it.
Its atomicity comes from the absence of that `await` rather than from a lock:
the [read-modify-write race](19_Techniques--Concurrency.md#a-single-thread-still-races)
needs a suspension point inside the update,
and `claim()` runs from its test to its `add()` as one synchronous stretch.
Exercise 3 inserts a suspension point and counts the cells claimed twice.
`next_number()` hands out rat numbers from `itertools.count()`,
the [endless counter](23_Patterns--Iterators.md#reusable-algorithms).
`explore()` claims the entry and creates the first rat's task inside an `asyncio.TaskGroup`:

```python
# rats_and_mazes/blackboard.py
import asyncio
import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field
from maze import Coord, Maze
from rat import Rat

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(
        init=False, default_factory=set)
    tasks: list[asyncio.Task[None]] = field(
        init=False, default_factory=list)
    messages: list[str] = field(
        init=False, default_factory=list)
    _numbers: Iterator[int] = field(
        init=False,
        default_factory=lambda: itertools.count(1))
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        # No await between test and add, so it is atomic
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(self.group.create_task(rat.run()))

    def next_number(self) -> int:
        return next(self._numbers)

    def log(self, message: str) -> None:
        self.messages.append(message)

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

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

A `TaskGroup` stays open until every task inside it has finished,
including tasks created after the block began.
That matches this problem: each rat can create more rats.
A single `asyncio.gather(*self.tasks)` would await only the tasks in the list at the moment of the call,
because `gather()` fixes its argument list then,
and most of the rats do not exist yet.

`group` carries `field(init=False)`, and only `explore()` assigns it.
The robot example later in this chapter declares `Robot.room` the same way,
without assigning it.
The other four `init=False` fields, `visited`, `tasks`, `messages`,
and `_numbers`, are internal bookkeeping:
`init=False` keeps them out of the generated signature,
and each `default_factory` builds a fresh object per blackboard.

### Running the Maze

The maze layout lives in a text file.
The loader skips blank lines and any line beginning with `#`,
including the first line, which names the file's path.
The rest is the maze.

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

The demo awaits `explore()`,
then prints the first eight log messages and the mapped maze.
The log shows what the map cannot.
Rat 1 spawns rat 2 and then dead-ends before rat 2 does:
`__post_init__` assigns each number at spawn time,
so the numbers follow spawn order rather than completion order.
The full log runs to eighteen messages, two per rat.

```python
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
```

`amaze.txt` has no loop:
every open cell connects to the rest of the maze by exactly one path.
So every `claim()` the run above rejects on an open cell is a rat testing a cell already claimed:
its own previous cell,
or the parent's cell when a newly spawned rat tests its neighbors.
Only a maze with a loop lets two rats try to claim the same new cell,
the race the atomicity resolves.

### Contention on a Loop

A maze with a loop closes a second path between two cells,
so two different rats can reach the same open cell from opposite directions.
Eight open cells around one wall block are enough to force the race:

```python
# rats_and_mazes/ring_contention.py
import asyncio
from typing import override
from blackboard import Blackboard
from maze import Maze

RING = """\
*****
*   *
* * *
*   *
*****
"""

class CountingBlackboard(Blackboard):
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.taken = 0

    @override
    def claim(self, x: int, y: int) -> bool:
        won = super().claim(x, y)
        if not won and self.maze.is_open(x, y):
            self.taken += 1
        return won

async def main() -> None:
    maze = Maze.from_text(RING)
    blackboard = CountingBlackboard(maze)
    await blackboard.explore()
    for message in blackboard.messages:
        print(message)
    backtracks = len(blackboard.visited) - 1
    print(f"{blackboard.taken} rejections, "
          f"{backtracks} from backtracking alone.")

asyncio.run(main())
#: Rat 1 starts at (1, 1).
#: Rat 2 starts at (2, 1).
#: Rat 1 dead-ends at (2, 3).
#: Rat 2 dead-ends at (3, 3).
#: 9 rejections, 7 from backtracking alone.
```

The entry has two open neighbors,
so rat 1 keeps one neighbor and spawns rat 2 at the other.
`CountingBlackboard` tallies every `claim()` rejected on an open cell.
Seven of the nine rejections are backtracking:
each rat tests the cell it came from, once per cell other than the entry,
and `len(blackboard.visited) - 1` counts those cells.
The other two belong to the loop's closing edge, tested from both ends:
rat 1 dead-ends at `(2, 3)` because rat 2 already claimed `(3, 3)`,
and rat 2 dead-ends at `(3, 3)` because rat 1 already claimed `(2, 3)`.
Each rat loses a cell to the other, not to itself.
That is the race `claim()`'s atomicity exists to resolve,
and a perfect maze like `amaze.txt` never produces it.

### Testing Full Coverage

However the tasks interleave,
the rats cover every cell reachable from the entry,
because every claimed cell gets a rat,
and that rat tests all four of its neighbors.
The test verifies this by comparing the cells the rats visited against a flood fill of the same maze.
Coverage does not depend on atomic claiming: `visited` is a set,
so a cell claimed twice still counts once.
Atomicity adds the other guarantee, one rat per cell,
which only a count like exercise 3's can see.

```python
# rats_and_mazes/test_rats_and_mazes.py
import asyncio
from typing import Final
from blackboard import Blackboard
from maze import Coord, Maze

LAYOUT: Final[str] = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""

def flood(maze: Maze, start: Coord) -> set[Coord]:
    seen: set[Coord] = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not maze.is_open(x, y):
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y),
                  (x, y + 1), (x, y - 1)]
    return seen

def test_rats_map_every_reachable_cell() -> None:
    maze = Maze.from_text(LAYOUT)
    blackboard = Blackboard(maze)
    asyncio.run(blackboard.explore())
    assert blackboard.visited == flood(maze, maze.entry())
```

### Watching the Pack

The same model drives a GUI demonstration.
`rats_view.py` lets the rats finish exploring,
records the order in which they claimed cells,
and replays that order on a `tkinter` canvas.
The canvas shows the walls in gray, then each claimed cell turns green in turn,
so you watch the pack move through the maze from the entry outward.
The view records the order by subclassing `Blackboard` and overriding `claim()`,
so the model stays as written.
Each of this chapter's three views is a separate file holding all the display code,
the model-view split of [*Observer*](30_Patterns--Observer.md#a-visual-example-a-model-and-its-view).
The subscription half of *Observer* is absent.
No model in this chapter notifies a view,
so each view drives or replays its model itself.
The harness skips `rats_view.py`, like every windowed view in this book.

```python
# rats_and_mazes/rats_view.py
import asyncio
import tkinter as tk
from typing import Final, override
from blackboard import Blackboard
from maze import Coord, Maze

CELL: Final[int] = 26

class RecordingBlackboard(Blackboard):
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.order: list[Coord] = []

    @override
    def claim(self, x: int, y: int) -> bool:
        claimed = super().claim(x, y)
        if claimed:
            self.order.append((x, y))
        return claimed

def show(layout: str = "amaze.txt",
         step_ms: int = 60) -> None:
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
            x * CELL, y * CELL,
            (x + 1) * CELL, (y + 1) * CELL,
            fill=color, outline="gray")

    for y in range(maze.height):
        for x in range(maze.width):
            box(x, y,
                "white" if maze.is_open(x, y)
                else "dimgray")

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

Concurrency here organizes the code and adds no speed.
Every rat awaits `asyncio.sleep(0)` at the same point,
so the tasks take turns in round robin and the run stays deterministic.
The tasks run one at a time,
so the design runs no faster than a single-threaded worklist:
a plain stack of frontiers, popped and pushed in a loop,
visits the same 139 cells.
What `asyncio` provides is control flow:
each rat's own path through the maze stays one `while` loop in `run()`,
instead of a stack of pending frontiers that one function pushes and pops by hand.
What it adds is the event loop,
a component whose one job here is to hand the turn from rat to rat.

Jeremy Meyer wrote the original Java version of this example.

## A Robot in a Maze

Concurrency is one way to build a simulation.
Object-oriented design is another.
This second example, adapted from my *Atomic Kotlin* book,
walks a single robot through a maze.
It shows how polymorphism removes conditionals.
A `Room` calls its occupant's `interact()`,
and each type of occupant defines its own.

### Rooms, Robots, and the Item Factory

The occupants are `Item`s.
`Room.enter()` calls `occupant.interact()` and returns the room in which the robot ends up.
A wall returns the robot's current room,
food replaces itself with `Empty` and returns its own room,
a teleport returns its paired room.
No `if` or `elif` on the type of occupant appears in the movement code:

```python
# robot_explorer/items.py
from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar, override

if TYPE_CHECKING:
    from world import Room

class Urge(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()

class Item:
    symbol: ClassVar[str] = ""

    def interact(self, robot: Robot, room: Room) -> Room:
        return room  # Default: the robot enters the room

    def __str__(self) -> str:
        return self.symbol

class Robot(Item):
    symbol: ClassVar[str] = "R"
    # Set by the builder when the robot is placed
    room: Room

    def __init__(self) -> None:
        # Set when the robot reaches the end
        self.finished = False

    def move(self, urge: Urge) -> None:
        self.room = self.room.doors.open(urge).enter(self)

class Wall(Item):
    symbol: ClassVar[str] = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return robot.room  # Cannot pass: stay put

class Food(Item):
    symbol: ClassVar[str] = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten
        return room

class Teleport(Item):
    symbol: ClassVar[str] = ""  # Set per target letter
    target_room: Room  # Paired up by the builder

    def __init__(self, target: str) -> None:
        self.target = target

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return self.target_room

    @override
    def __str__(self) -> str:
        return self.target

class Empty(Item):
    symbol: ClassVar[str] = "_"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return room

class Edge(Item):
    symbol: ClassVar[str] = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        # The void outside the maze: stay put
        return robot.room

class EndGame(Item):
    symbol: ClassVar[str] = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        robot.finished = True  # Recorded, not printed
        return room

def item_factory(symbol: str) -> Item:
    for item_type in Item.__subclasses__():
        if symbol == item_type.symbol:
            return item_type()
    # Anything else is a teleport target
    return Teleport(symbol)
```

`world.py` imports `Edge`, `Item`, `Robot`, and `Urge` from `items.py`,
so `from world import Room` here is circular.
`TYPE_CHECKING` is `True` only for a type checker reading the file and `False` at runtime,
so the runtime skips that import and the cycle exists for the checker alone.
Every use of `Room` in `items.py` is an annotation (`room: Room`, `-> Room`),
never a runtime lookup.

`Robot` holds its two pieces of state in different ways.
`__init__` assigns `finished`, so each robot owns its own flag from the start.
`room` gets a bare declaration, `room: Room`,
which tells the type checker the attribute's type and keeps that type `Room` instead of `Room | None`,
so code that reads `room` skips the `None` check.
`GameBuilder` creates the attribute by assigning `robot.room` when it places the robot.
Reading `room` before then raises an `AttributeError`,
and the builder runs first, so every read comes after.

`item_factory()` turns a maze character into an `Item`.
It searches `Item.__subclasses__()` for a matching `symbol`,
so a new kind of item registers itself: define the subclass with its symbol,
and the factory finds it.
That search is the [registry idea](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary),
using the class hierarchy as the registry.
`__subclasses__()` reports only direct subclasses,
so a new item must inherit from `Item` itself.
If you derive a class from `Food` to inherit its behavior,
that class is a grandchild of `Item`.
`Item.__subclasses__()` leaves it out,
so the loop falls through to its last line and builds a `Teleport`.
The same chapter's [Simple *Factory Method*](27_Patterns--Factory.md#simple-factory-method)
describes the recursion for deeper hierarchies,
and that chapter's exercise 9 writes the recursion.

A `Room` holds one item and connects to its neighbors through a `Doors` object.
Doors that lead nowhere point at one shared `EDGE` room,
the void outside the maze,
so the robot can try any direction without a special case.
`EDGE` is a [*Null Object*](20_Patterns--Rethinking_Objects.md#null-object).
It takes `enter()` like any other room,
and its `Edge` occupant's `interact()` returns `robot.room`,
so the robot stays where it was.

![The maze as a graph of rooms, with teleport jumps and one shared EDGE room](_images/maze_graph)

`Doors.connect()` links each room to its neighbors on the grid.
Teleports add links that cross the grid:
two rooms whose `Teleport` items share a target letter lead to each other.

```python
# robot_explorer/world.py
from typing import Final
from items import Edge, Item, Robot, Urge

type Coord = tuple[int, int]  # (row, col)
type RoomMap = dict[Coord, Room]

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
        self.neighbors: dict[Urge, Room] = {}

    def connect(self, row: int, col: int,
                rooms: RoomMap) -> None:
        for urge, coord in {
            Urge.NORTH: (row - 1, col),
            Urge.SOUTH: (row + 1, col),
            Urge.EAST: (row, col + 1),
            Urge.WEST: (row, col - 1),
        }.items():
            if coord in rooms:
                self.neighbors[urge] = rooms[coord]

    def open(self, urge: Urge) -> Room:
        return self.neighbors.get(urge, EDGE)

# Created once both classes exist; its own doors stay unset
EDGE: Final[Room] = Room(Edge())
```

The `Coord` here counts `(row, col)`,
the opposite order from the rats example's `(column, row)`,
because `GameBuilder` walks the maze text line by line.

One move is one chain.
`Robot.move()` calls `doors.open(urge)`, which returns the neighboring room,
`EDGE` when no door leads that way.
That room's `enter()` passes the robot to its occupant's `interact()`,
and whatever room `interact()` returns becomes `robot.room`.
Every rule of the game lives in some `interact()`.

### Building the Maze in Stages

`GameBuilder` assembles the maze in three stages: a room for every character,
then the connections between rooms, then the teleport pairs.
Each stage depends on the one before it,
so splitting them into labeled passes keeps each stage separate instead of interleaving all three in one loop.
[Factory](27_Patterns--Factory.md#builder)
counts `GameBuilder` among the cases where *Builder* survives in Python,
because construction here is a process rather than a single call.
`run()` walks a string of moves, and `show_maze()` renders the current state:

```python
# robot_explorer/game.py
from itertools import groupby
from items import Empty, Robot, Teleport, Urge, item_factory
from world import Room, RoomMap

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[Room] = []
        # Stage 1: a Room for every character
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
        # Stage 2: connect each room to its neighbors
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        # Stage 3: pair teleports sharing a target letter
        def target(room: Room) -> str:
            assert isinstance(room.occupant, Teleport)
            return room.occupant.target

        teleports.sort(key=target)
        for letter, group in groupby(teleports, key=target):
            pair = list(group)
            assert len(pair) == 2, letter
            room1, room2 = pair
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
```

Stage 3 pairs the teleports.
Sorting by target letter puts each pair of partners side by side.
`groupby(teleports, key=target)` then walks the sorted rooms in one pass,
yielding each run of matching letters,
and `pair = list(group)` collects each run.
`assert len(pair) == 2, letter` checks a rule the maze layout must obey:
every target letter marks exactly two rooms.
A typo that gives a letter one room, or three, fails here at build time,
naming the offending letter.
If you remove the check, the build still stops,
at `room1, room2 = pair` on the next line.
The `ValueError` that unpacking raises says how many values it expected and leaves you to find the letter.
The `assert isinstance` lines that follow serve the type checker as much as safety.
Each narrows the occupant to `Teleport` before the code assigns `target_room`.

Stage 1 does test types,
with `isinstance(occupant, Robot)` and `isinstance(occupant, Teleport)`.
That is not the type switch that polymorphism removes.
`GameBuilder` still must tell the kinds of item apart, once,
and the movement code that runs afterward never tests a type again.

The `Robot` branch builds `Room(Empty())` rather than `Room(occupant)`.
The robot is the one item that moves,
so its cell gets an `Empty` occupant and behaves like any other empty room once the robot moves away.
`show_maze()` draws the `R` by checking which room the robot is in rather than reading an occupant.

### Choosing the Path

The robot can now move, but nothing supplies its moves.
`run()` replays a string of `n`/`s`/`e`/`w` characters,
and so far a person writes that string, as the test does with `game.run("e")`.
For the whole maze, `solve()` computes the string.
`solve()` searches the room graph and returns the same kind of string,
so `game.run(solve(game))` walks the route the search found.

`solve()` is a breadth-first search over `Room` objects.
It expands the room reached in the fewest moves first,
so the first route it finds to the `!` is a shortest one.
It makes the same `doors.open(urge)` calls `Robot.move()` makes,
so it works entirely in rooms and the moves between them.
`landing()` decides whether a door is passable by testing the occupant's type with `isinstance`,
and that test reproduces what `Room.enter()` gets from `interact()`.
For a `Wall` or an `Edge` it returns `None`, for a `Teleport` the target room,
and for anything else the room itself:

```python
# robot_explorer/solver.py
from collections import deque
from typing import Final
from game import GameBuilder
from items import Edge, EndGame, Teleport, Urge, Wall
from world import Room

MOVES: Final[dict[Urge, str]] = {
    Urge.NORTH: "n", Urge.SOUTH: "s",
    Urge.EAST: "e", Urge.WEST: "w"}

def landing(room: Room, urge: Urge) -> Room | None:
    # Where a door leads, or None when it is blocked
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall | Edge):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder) -> str:
    start = game.robot.room
    queue: deque[tuple[Room, str]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if isinstance(room.occupant, EndGame):
            return path
        for urge, char in MOVES.items():
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + char))
    raise ValueError("No path to the EndGame room")
```

`seen` holds `Room` objects.
`Room` defines no `__eq__`,
so it keeps `object`'s identity comparison and identity hash.
A graph search needs identity,
because two rooms holding the same kind of item are still two different places.
`solve()` adds a room to `seen` when the room enters the queue,
rather than when it leaves, so each room enters the queue once.

Searching leaves the maze as it was.
`solve()` reads doors and occupants and never calls `enter()`,
so every `.` stays in place and the robot stays where it started.
The path `solve()` returns is the string `run()` expects:

```python
# robot_explorer/robot_demo.py
from game import GameBuilder, string_maze
from solver import solve

game = GameBuilder(string_maze)
print("start:")
print(game.show_maze())
#: start:
#: ###############################
#: #R#.____#____.#_______#_______#
#: #_###_#_###_#_#_#_#####_#####_#
#: #___#_#___#_#_#_#.#__b__#___#_#
#: ###_#_###_#_#_###_#_#####_#_#_#
#: #.#_#_#.__#_#__.#_#__b__#_#___#
#: #_#_#_#_###_###_#_#####_#_#####
#: #_#_#_#__.#_#_#_____#___#_____#
#: #_#_#_###_#_#_#_#####_#######_#
#: #.#___#___#_#___#____.#_____#_#
#: #_#####_###_#_###_#####_#_###_#
#: #___#a__#.__#.__#__.#___#_#___#
#: #_#_#_###_#####_###_###_###_#_#
#: #_#.#_#___#!______#_____#___#_#
#: #_#_#_###_#############_#_###_#
#: #_#_#__a#_______________#___#_#
#: #_#####_###_###########_###_#_#
#: #_____#.__#_#___#_____#_#___#_#
#: #_#_#####_###_#_#_###_###_###_#
#: #.#___________#___#____.__#___#
#: ###############################
solution = solve(game)
print(len(solution), "moves")
#: 198 moves
game.run(solution)
if game.robot.finished:
    print("Game over!")
#: Game over!
print("\nfinal:")
print(game.show_maze())
#:
#: final:
#: ###############################
#: #_#.____#_____#_______#_______#
#: #_###_#_###_#_#_#_#####_#####_#
#: #___#_#___#_#_#_#.#__b__#___#_#
#: ###_#_###_#_#_###_#_#####_#_#_#
#: #.#_#_#___#_#___#_#__b__#_#___#
#: #_#_#_#_###_###_#_#####_#_#####
#: #_#_#_#___#_#_#_____#___#_____#
#: #_#_#_###_#_#_#_#####_#######_#
#: #.#___#___#_#___#_____#_____#_#
#: #_#####_###_#_###_#####_#_###_#
#: #___#a__#___#___#___#___#_#___#
#: #_#_#_###_#####_###_###_###_#_#
#: #_#.#_#___#R______#_____#___#_#
#: #_#_#_###_#############_#_###_#
#: #_#_#__a#_______________#___#_#
#: #_#####_###_###########_###_#_#
#: #_____#___#_#___#_____#_#___#_#
#: #_#_#####_###_#_#_###_###_###_#
#: #.#___________#___#_______#___#
#: ###############################
```

The robot eats the food along its path, jumps through both teleports
(`a`, then `b`), and reaches the `!` that ends the game.
The teleports are not shortcuts but the only way through.
If `landing()` returns `None` for them, as it does for a `Wall`,
`solve()` raises a `ValueError`,
because every route to the `!` passes through a teleport.

### Testing the Walk

`show_maze()` renders the maze into a string,
so a test can check the model without opening a window.
Build the maze, search it, walk the result,
and check that the robot finished on the `!` square:

```python
# robot_explorer/test_robot.py
from game import GameBuilder, string_maze
from items import EndGame
from solver import solve

def test_search_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solve(game))
    room = game.robot.room
    # Finished on the "!"
    assert isinstance(room.occupant, EndGame)
    assert game.robot.finished  # And the model recorded it

def test_walls_block_and_food_is_eaten() -> None:
    # Robot, food, wall in one row
    game = GameBuilder("R.#")
    start = game.robot.room
    game.run("e")  # East: eat the food and move in
    assert "." not in game.show_maze()  # Food gone
    assert game.robot.room is not start
    blocked = game.robot.room
    game.run("e")  # East again: a wall, so stay put
    assert game.robot.room is blocked
```

### Watching the Robot

The same model drives a graphical view.
`maze_view.py` builds the maze, calls `solve()` for the route,
draws each room as a colored cell,
and steps the robot along that route on a timer.
The view is the only part that touches the screen,
and no module of the model imports it.

```python
# robot_explorer/maze_view.py
import tkinter as tk
from typing import Final
from game import GameBuilder, string_maze
from items import Urge
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

Three ideas from earlier chapters make up the design.
[Polymorphism](20_Patterns--Rethinking_Objects.md#what-is-polymorphism)
replaces a type switch,
a [factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary)
builds objects from data,
and a [*Null Object*](20_Patterns--Rethinking_Objects.md#null-object)
removes the check for a missing door.
None of them needs concurrency.

Two resources go further:
a survey of [algorithms to create mazes](https://en.wikipedia.org/wiki/Maze_generation_algorithm),
and Craig Reynolds on [steering behavior for autonomous moving objects](https://www.red3d.com/cwr/steer/),
the starting point for a robot that steers continuously instead of planning a grid path before it moves.

## Order from Noise

The two simulations so far confirm designs.
The rats cover every reachable cell, one rat per cell,
because `claim()` is atomic.
The robot reaches the goal because polymorphism handles every encounter.
Both times you know the outcome in advance and run the program to confirm it.
The third example gives you only half the outcome.
`amplitude()` fixes the shape the sand will trace:
the curves are the formula's zero set.
No line of the code computes how two thousand independent random walks reach that shape and stay there.
That is simulation's other purpose,
to discover behavior instead of confirming it.

In 1787 Ernst Chladni sprinkled sand across a metal plate and drew a violin bow along its edge.
The bow made the plate ring.
A ringing plate moves unevenly.
Standing waves divide it into regions that swing up and down,
and the *nodal lines* between them stay still.
The vibration bounces sand out of the moving regions.
When a grain comes to rest on a still line, nothing kicks it away again.
Within seconds the random motion sweeps the sand into sharp, symmetric curves.
Bowing a different spot rings the plate in a different mode and draws a different figure.

### The Model

The model is small.
`amplitude()` is the standing-wave field of a square plate ringing in mode `(m, n)`.
Physics supplies the formula, an approximation for a plate with free edges.
Treat it as given; only its shape matters here.
The field is zero along curves, and those curves are the nodal lines.
A `Grain` is a position.
All the simulation's logic sits in `step()`.
Every grain takes one random step,
and the plate's vibration at that grain's location scales the step.
Grains never read each other's positions and store nothing but their own.

```python
# chladni_plate/chladni.py
import math
import random
from dataclasses import dataclass

type Mode = tuple[int, int]  # Vibration pattern (m, n)

def amplitude(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.cos(m * math.pi * x)
        * math.cos(n * math.pi * y)
        - math.cos(n * math.pi * x)
        * math.cos(m * math.pi * y))

def bounce(v: float) -> float:
    if v < 0.0:
        return -v
    if v > 1.0:
        return 2.0 - v
    return v

@dataclass
class Grain:
    x: float
    y: float

class Plate:
    def __init__(self, grains: int, mode: Mode,
                 seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.mode = mode
        self.grains = [
            Grain(self.rng.random(), self.rng.random())
            for _ in range(grains)]

    def step(self, kick: float = 0.05) -> None:
        for g in self.grains:
            a = amplitude(g.x, g.y, self.mode)
            g.x = bounce(
                g.x + self.rng.uniform(-kick, kick) * a)
            g.y = bounce(
                g.y + self.rng.uniform(-kick, kick) * a)

    def agitation(self) -> float:
        return sum(
            amplitude(g.x, g.y, self.mode)
            for g in self.grains) / len(self.grains)

    def render(self, width: int = 57,
               height: int = 30) -> str:
        counts: list[list[int]] = [
            [0] * width for _ in range(height)]
        for g in self.grains:
            col = min(int(g.x * width), width - 1)
            row = min(int(g.y * height), height - 1)
            counts[row][col] += 1
        shades = " .:*#"
        return "\n".join(
            "".join(shades[min(c, len(shades) - 1)]
                    for c in row).rstrip()
            for row in counts)
```

`bounce()` reflects a kicked grain off the edge instead of letting it leave the plate.
`agitation()` measures the mean vibration strength directly under the grains.
Grains scattered at random sample the field's average, so agitation starts high.
A grain resting on a nodal line contributes zero.
One number says how settled the sand is.
`render()` draws grain density as characters, as `Blackboard.render()` does,
so the model can show its state without a window.
The demo calls `step()` 1200 times, printing agitation at four checkpoints:

```python
# chladni_plate/chladni_demo.py
from chladni import Plate

plate = Plate(grains=2000, mode=(2, 3), seed=42)
steps = 0
for target in (0, 100, 400, 1200):
    for _ in range(target - steps):
        plate.step()
    steps = target
    print(f"steps {target:4}: "
          f"agitation {plate.agitation():.3f}")
#: steps    0: agitation 0.585
#: steps  100: agitation 0.073
#: steps  400: agitation 0.005
#: steps 1200: agitation 0.000
print(plate.render())
#: .:.                   #                      #
#:  *##                  .#                     #
#:    .##                 ##                    #
#:      :##                ##                    #
#:        ###               ####                 #*
#:          ###                ######             ##########
#:            ##*                    ########
#:              ##:                         ###
#:                ##                          ##
#:                  ##                         #
#:                    ##                       ##
#:                      ##                      #
#: #######               .##                    #:
#:       ##*               ###                   #
#:         ##                ###                 ##
#:          ##                 ###                ##
#:           #                   ##*               ###
#:           .#                    ##:               #######
#:            #                      ##
#:            ##                       ##
#:             #                         ##
#:             ##                          ##
#:              :##                         *##
#:                .#######                    *##
#: #########*            *#####:                *##
#:          *#                 ###.               ###
#:           #                    ##                ###
#:            #                    ##                 ###
#:            #                     ##                  ##.
#:            #                      #                   .##
```

### What the Numbers Show

Agitation collapses toward zero, and the picture shows why.
The grains have gathered on the nodal lines of mode `(2, 3)`.
Nothing steered them there.
In a loud region the kicks stay large,
so a grain keeps moving until a random step crosses a quiet line,
where the kicks shrink toward zero.
Noise can carry a grain into a quiet place.
It cannot carry the grain back out.
The randomness produces the order instead of opposing it.

The curves themselves come from the formula alone.
A plot of `amplitude()`'s zero set draws them.
The run demonstrates the gathering, not the shape: random,
uncoordinated steps concentrate onto a curve that no grain,
and no line of `step()`, ever names.

### Testing a Random Process

A test cannot predict where a particular grain ends up after hundreds of random kicks.
It checks the aggregate instead.
Four hundred steps must divide agitation by ten,
and no kick may leave a grain outside the plate.
Seeding `random.Random` makes any failure reproducible.

```python
# chladni_plate/test_chladni.py
from chladni import Plate

def test_noise_settles_grains_onto_quiet_lines() -> None:
    plate = Plate(grains=500, mode=(2, 3), seed=1)
    before = plate.agitation()
    for _ in range(400):
        plate.step()
    assert plate.agitation() < before / 10

def test_kicks_never_knock_grains_off_the_plate() -> None:
    plate = Plate(grains=200, mode=(3, 5), seed=2)
    for _ in range(300):
        plate.step(kick=0.2)
    assert all(0.0 <= g.x <= 1.0 and 0.0 <= g.y <= 1.0
               for g in plate.grains)
```

### Watching It Happen

The `tkinter` view shows what the text version cannot:
the collapse as it unfolds, and the pattern surviving a change of rules.
Each grain keeps one color from a small palette,
so you can watch individual grains mix while the collective figure forms.
Every 200 frames the view switches the plate to a new mode.
The old figure now lies on loud regions of the new field.
The grains scatter, mix, and gather into a different figure.
The order belongs not to the grains but to the field on which they sit.

```python
# chladni_plate/chladni_view.py
import itertools
import tkinter as tk
from typing import Final
from chladni import Mode, Plate

SIZE: Final[int] = 560
DOT: Final[int] = 3
COLORS: Final[list[str]] = [
    "gold", "coral", "palegreen", "skyblue", "plum"]
MODES: Final[list[Mode]] = [(1, 2), (2, 3), (3, 4), (3, 5)]

def show(grains: int = 1200, step_ms: int = 30,
         frames_per_mode: int = 200) -> None:
    plate = Plate(grains, MODES[0])
    root = tk.Tk()
    root.title(f"Chladni Plate {plate.mode}")
    canvas = tk.Canvas(root, width=SIZE, height=SIZE,
                       background="black",
                       highlightthickness=0)
    canvas.pack()
    palette = itertools.cycle(COLORS)
    dots = [
        canvas.create_oval(0, 0, DOT, DOT, outline="",
                           fill=next(palette))
        for _ in plate.grains]
    modes = itertools.cycle(MODES[1:] + MODES[:1])
    frames = itertools.count(1)

    def frame() -> None:
        if next(frames) % frames_per_mode == 0:
            plate.mode = next(modes)
            root.title(f"Chladni Plate {plate.mode}")
        for _ in range(3):
            plate.step()
        for dot, g in zip(dots, plate.grains):
            canvas.moveto(dot, g.x * SIZE - DOT / 2,
                          g.y * SIZE - DOT / 2)
        root.after(step_ms, frame)

    frame()
    root.mainloop()

if __name__ == "__main__":
    show()
```

`itertools.cycle()` constructs an infinite iterator from any finite iterable.
It yields the source's elements in sequence and starts over when it reaches the end.
`itertools.count(1)` numbers the frames,
the same endless counter that numbered the rats.

## The Less the Agents Know

The chapter begins by defining a simulation as objects that act on their own and interact through shared state.
The grains are the limiting case of that definition.
The shared state is the plate,
and a grain's whole interaction with it is one read of the field at its own position.
Even so, structure that no agent encodes appears in the aggregate.
This is *emergence*:
global order arising from local rules that never mention it.
The less each agent's rule uses, the more the run can tell you,
because the outcome comes from the interactions rather than from the instructions.

The model has one limit.
If you run it longer, agitation keeps falling.
A grain moves roughly five orders of magnitude less per step at 20,000 steps than it does at 100.
The nodal lines keep thinning as long as `step()` keeps running,
so in any one run the step count, not the plate, sets their width.
Real sand on a real bowed plate settles into a moving equilibrium instead of freezing.
Exercise 7 asks you to tell the physics from the rule that models it:
swap `amplitude()`'s formula for a membrane's,
and watch every figure change while nothing else in the program does.

When behavior emerges, reading the code is not enough.
Run it.

## Exercises

1.  Test a `Rat` with a fake blackboard.
    Because `Rat` depends only on the `Recorder` `Protocol`,
    you can drive it with a stand-in.
    Write a fake whose `claim()` returns a scripted sequence of results and whose `spawn()` only records the coordinates it receives,
    run one rat with `asyncio.run(rat.run())`,
    and assert which cell the rat kept for itself and which cells it spawned.
    You need no real `Blackboard`, `Maze`, or task scheduling.
2.  Report the cells the rats never reach.
    After `explore()` finishes,
    compare `blackboard.visited` against every open cell of the `Maze` and print the open cells that no rat claimed.
    Build a maze for which that set is not empty,
    and explain what makes a cell unreachable.
3.  Break the atomicity of `claim()`.
    Make `claim()` an `async def`,
    which forces the same change on the `Recorder` protocol,
    `Rat.run()`'s comprehension, and `explore()`.
    Put `await asyncio.sleep(0)` between the membership test and `self.visited.add(...)`.
    Then count how many calls return `True` and compare that count with `len(blackboard.visited)`,
    using a maze that contains a loop.
    `amaze.txt` is a perfect maze,
    so no two rats ever reach one unclaimed cell and the counts always agree.
    `test_rats_and_mazes.py` still passes, because `visited` is a set.
    The guarantee that broke is "one rat per cell", not "every cell visited".
    What happens to the two rats that both claimed one cell,
    and why does the original `claim()`, with no `await` inside it,
    need no lock?
4.  Add a new kind of `Item` to the robot maze.
    Define a `Coin` subclass of `Item` with the symbol `$`.
    Its `interact()` removes itself the way `Food` does and adds one to a coin count carried by the `Robot`.
    Place a few `$` characters in the maze and report how many the robot collects.
    `item_factory()`, `Room`, and `GameBuilder` stay as they are.
    Explain why the factory finds your new item on its own,
    and what the factory does if you derive `Coin` from `Food` instead.
5.  Send the robot to something other than the `!`.
    `solve()` stops at whatever room holds an `EndGame`,
    the one goal it can express.
    Replace that `isinstance` test with a `Callable[[Room], bool]` parameter,
    so the caller says what counts as arriving,
    and change nothing else in the search,
    beyond letting `solve()` return `None` when no room matches.
    Then use the new parameter to feed the robot:
    search for the nearest room holding a `Food`, walk there,
    and repeat until no `Food` remains, then search for the `!` and walk that.
    Report how many pieces of food the robot ate and how many moves the whole tour took.
    The run answers two questions for you.
    Why does the search have to run again after every meal instead of once at the start?
    And why does asking for the nearest food each time not produce the shortest tour that eats everything?
6.  Freeze the plate.
    Run the Chladni view with `MODES` starting at `(2, 2)`.
    Work out what `amplitude()` returns whenever `m == n`,
    and explain why the result is neither chaos nor a figure.
    Then explain why the main diagonal shows up in every figure this plate makes.
    Swapping `x` and `y` in the two terms of `amplitude()` is the clue.
7.  Change the physics.
    Replace the body of `amplitude()` with `abs(math.sin(m * math.pi * x) * math.sin(n * math.pi * y))`,
    the standing waves of a membrane fixed at its edges, like a drumhead.
    Predict the figures before you run the view.
    Why are the nodal lines now straight?
8.  Tune the noise.
    Rerun `chladni_demo.py` passing `kick=0.005` and then `kick=0.5` to `plate.step()`,
    printing agitation at the same checkpoints.
    One setting produces order too slowly.
    The other drives agitation down as convincingly as the default kick,
    yet the figure never appears.
    Explain both failures, and why an intermediate kick avoids them.
