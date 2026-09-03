# Simulation

A simulation models a set of objects that act on their own and interact through shared state.
This chapter builds three,
each giving its agents less to work with than the last.
A pack of rats coordinates through a shared blackboard,
a single robot walks a maze where each object it meets decides what happens,
and a plate of vibrating sand runs on grains that know nothing.
The first two confirm a design you can predict from the code.
The third produces a pattern nobody wrote down.

The chapter works the first example, the pack of rats, from end to end.
It puts asyncio tasks, a shared coordination object,
and structural typing together in one small program.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
introduces the `asyncio` mechanics (`async def`, `await`, `gather`, `run`).

## Rats & Mazes

The problem has three types.

A *maze* knows its own layout.
Given a coordinate, it reports whether each neighboring cell is a wall or an opening,
and it hands out an entry point.
The maze never decides anything.
It only answers questions.

A *blackboard* is the shared surface on which every rat writes.
Blackboard is a classic coordination pattern.
Independent agents read from and write to one common data structure instead of talking to each other directly.
Here the blackboard owns the maze, records which cells the rats have explored,
hands out rat numbers, and launches new rats.
The rats run as cooperative `asyncio` tasks.
They take turns instead of running at the same instant,
so the blackboard needs no lock.
Nothing interrupts a rat partway through an update.

A *rat* explores.
Each rat runs as its own task.
From its current cell it looks at the four neighbors and tries to claim the open ones.
Claiming a cell both marks it visited and reserves it,
so no two rats cover the same ground.
When a rat finds more than one open neighbor,
it keeps the first for itself and spawns a new rat down each of the others,
then yields so its siblings can run.
When it can claim nothing, it has reached a dead end and its task ends.
When the last rat dies, the pack has mapped every cell reachable from the entry.

### The Rat and the Blackboard

The rat never imports the blackboard.
It needs only an object with matching methods,
so a `Protocol` describes what it expects.
That `Protocol` is structural typing from [Static Types](08_Foundations--Static_Types.md#structural-typing-with-protocols).
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
so it fills in `number` and logs the rat's start.

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

`Cell` nests inside `Maze` because it names concepts only `Maze` uses,
and it is a `StrEnum` rather than an `Enum` so its members keep acting like real strings.
`WALL` still works as the fill character for `ljust()`,
and comparing `self.rows[y][x]` against `Cell.OPEN` still works,
because a `StrEnum` member is its string value.

The blackboard holds everything the rats share.
`claim()` is the heart of the program.
It tests and marks a cell in one step with no `await` in between,
so a single rat gets each cell even when several reach it.
It sidesteps the read-modify-write race from [Concurrency](19_Techniques--Concurrency.md#a-single-thread-still-races).
That race needs a suspension point inside the update,
and `claim()` contains none,
so the atomicity comes from the shape of the code rather than from a lock
(exercise 3 inserts a suspension point and looks at what breaks).
`next_number()` hands out rat numbers from `itertools.count()`,
the endless counter from [Iterators](23_Patterns--Iterators.md#reusable-algorithms).
`explore()` claims the entry and releases the first rat inside an `asyncio.TaskGroup`:

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
That is the shape of this problem: each rat can create more rats.
A single `asyncio.gather(*self.tasks)` would miss most of them,
because `gather()` fixes its argument list at the moment of the call,
before those rats exist.

`group`'s declaration is `field(init=False)`, and only `explore()` assigns it,
the same declaration-without-assignment the robot example later in this chapter uses for `Robot.room`.
The other four fields are internal bookkeeping rather than constructor arguments:
`init=False` keeps them out of the generated signature,
and each `default_factory` builds a fresh object per blackboard.

The maze layout lives in a text file.
The loader drops blank lines and any line beginning with `#`, so the first line,
naming the file's path, drops out and the rest is the maze.

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

Running the demo turns the rats loose,
then prints the first eight log messages and the mapped maze.
The log shows what the map cannot:
rat 1 spawns rat 2 and then dies before rat 2 does,
and numbers arrive in spawn order rather than completion order.
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
Every rejected `claim()` in the run above is a rat looking back at the cell it just left,
never two rats reaching for the same open cell.
On this maze, `claim()`'s atomicity is never tested against two rats, only against one rat's own trail.

### Contention on a Loop

A maze with a loop closes a second path between two cells,
so two different rats can approach the same open cell from opposite directions.
Eight open cells around one wall block, with one loop, are enough to force it:

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

The entry's two open neighbors spawn two rats at once, one per arm of the ring.
`CountingBlackboard` tallies every rejected `claim()`.
Seven of the nine rejections are backtracking, `len(blackboard.visited) - 1`,
one per non-entry cell looking back at the cell it came from.
The other two belong to the loop's closing edge, examined from both ends:
rat 1 dead-ends wanting `(3, 3)`, already claimed by rat 2,
and rat 2 dead-ends wanting `(2, 3)`, already claimed by rat 1.
Each rat loses a cell to the other, not to itself.
That is the race `claim()`'s atomicity exists to resolve,
and a perfect maze like `amaze.txt` never puts it to the test.

### Testing Full Coverage

Because claiming is atomic,
the rats always cover every cell reachable from the entry,
no matter how the tasks interleave.
The test verifies this by comparing the cells the rats visited against a flood fill of the same maze.

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
and replays that order on a `tkinter` canvas: walls in gray,
then each claimed cell turning green one after another,
so you watch the pack move through the maze from the entry outward.
Each of this chapter's three views is a separate file holding all the display code,
the model-view split of [Observer](30_Patterns--Observer.md#a-visual-example-of-observers).
The missing piece is the subscription:
no model in this chapter notifies anybody,
so each view drives or replays its model instead of waiting for a notification.
The harness skips this view, like every windowed view in this book
(`tools/data/norun.txt` lists all three of this chapter's views):

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

Concurrency here is a shape for the code, not a source of speed.
Every rat awaits `asyncio.sleep(0)` at the same point,
so the tasks take turns in round robin and the run stays deterministic.
Nothing runs at the same instant as anything else,
and no thread or process ever overlaps another,
so the design buys no throughput a single-threaded worklist would lack.
A plain stack of frontiers, popped and pushed in a loop, visits the same 139 cells.
What `asyncio` buys is control flow:
each rat's own path through the maze stays one `while` loop in `run()`,
instead of a stack of pending frontiers threaded through one function by hand.
The cost is the runtime itself,
one more moving part for a program that never overlaps anything.

Jeremy Meyer wrote the original Java version of this example.

## A Robot in a Maze

Concurrency is one way to build a simulation.
Object-oriented design is another.
This second example, adapted from my *Atomic Kotlin* book,
walks a single robot through a maze.
It shows how polymorphism removes conditionals.
A `Room` asks its occupant what to do,
and each type of occupant answers for itself.

### Rooms, Robots, and the Item Factory

The occupants are `Item`s.
`Room.enter()` calls `occupant.interact()` and returns the room in which the robot ends up.
A wall keeps the robot where it is, food feeds the robot and lets it in,
a teleport returns a distant room.
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
    symbol = "R"
    # Set by the builder when the robot is placed
    room: Room

    def __init__(self) -> None:
        # Set when the robot reaches the end
        self.finished = False

    def move(self, urge: Urge) -> None:
        self.room = self.room.doors.open(urge).enter(self)

class Wall(Item):
    symbol = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return robot.room  # Cannot pass: stay put

class Food(Item):
    symbol = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten
        return room

class Teleport(Item):
    symbol = ""  # Set per target letter
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
    symbol = "_"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return room

class Edge(Item):
    symbol = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        # The void outside the maze: stay put
        return robot.room

class EndGame(Item):
    symbol = "!"

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

`world.py` imports `Item`, `Robot`, and `Urge` from `items.py`,
so `from world import Room` here is circular.
`TYPE_CHECKING` is `True` only for a type checker reading the file and `False` at runtime,
so that import never runs and no cycle forms.
Every use of `Room` below is an annotation (`room: Room`, `-> Room`),
never a runtime lookup.

`Robot` holds its two pieces of state in different ways.
`__init__` assigns `finished`, so each robot owns its own flag from the start.
`room` gets only a declaration, `room: Room` with no value.
That line tells the type checker a `Room` belongs there and stores nothing at runtime.
`GameBuilder` creates the attribute when it places the robot and sets `robot.room`.
Reading `room` before then raises an `AttributeError`,
and the builder runs first, so every read comes after.
Declaring it this way keeps the type `Room` instead of `Room | None`,
so code that reads `room` skips the `None` check.

`item_factory()` turns a maze character into an `Item`.
It searches `Item.__subclasses__()` for a matching `symbol`,
so adding a new kind of item needs no change here.
If you define the subclass with its symbol, the factory finds it.
This is the registry idea from [Factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary),
using the class hierarchy as the registry.
`__subclasses__()` reports only direct subclasses
(that chapter's [Simple Factory Method](27_Patterns--Factory.md#simple-factory-method) describes the recursion for deeper hierarchies),
so a new item must inherit from `Item` itself.
Deriving from `Food` to borrow its behavior hides the class from the factory,
which falls through to the last line and builds a `Teleport` instead.

A `Room` holds one item and connects to its neighbors through a `Doors` object.
Doors that lead nowhere point at one shared `EDGE` room,
the void outside the maze,
so the robot can try any direction without a special case.
`EDGE` is a [Null Object](20_Patterns--Rethinking_Objects.md#null-object):
it answers like any other room and sends the robot back where it started:

![A room graph: local grid adjacency from Doors.connect(), non-local jumps between rooms that share a Teleport target letter, and every off-map door converging on one shared EDGE room](_images/maze_graph)

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
`Robot.move()` asks `doors.open(urge)` for the neighboring room,
`EDGE` when no door leads that way.
`enter()` hands the robot to that room,
and whatever room its occupant's `interact()` returns becomes `robot.room`.
Every rule of the game lives in some `interact()`.

### Building the Maze in Stages

`GameBuilder` assembles the maze in three stages: a room for every character,
then the connections between rooms, then the teleport pairs.
Each stage depends on the one before it,
so splitting them into labeled passes keeps the construction readable instead of tangling it into one loop.
[Factory](27_Patterns--Factory.md#builder)
counts this as one of the cases where Builder survives in Python,
because construction here is genuinely a process rather than a single call.
`run()` walks a string of moves, and `show_maze()` renders the current state:

```python
# robot_explorer/game.py
# Build the maze in three stages, then run it.

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

solution = (
    "sseesssssseennnnnnnneesseesswwsseesswwsswwsseesseeee"
    "nneesseenneeeesseeeenneennwwnneenneennnnwwwwnnnneess"
    "eennnnwwwwwwsswweesswwsswwwwsseesseeeesswwwwwwwwwwww"
    "wwnnnneennnnnnnnnneesssseesssswwsseesswwww"
)
```

Running the demo prints the maze before and after the walk:

```python
# robot_explorer/robot_demo.py
from game import GameBuilder, solution, string_maze

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

Stage 3 pairs the teleports by target letter.
The sort by target letter puts each pair of partners side by side.
`groupby(teleports, key=target)` then walks the sorted rooms in one pass,
handing each run of matching letters to `pair = list(group)`.
`assert len(pair) == 2, letter` checks the maze's own promise:
every target letter marks exactly two rooms, never one, never three.
A typo that leaves a letter unpaired, or repeats it a third time,
fails here, at build time, naming the offending letter,
instead of leaving a `Teleport` whose `target_room` was never set
for the robot to step into later.
The `assert isinstance` lines that follow are for the type checker as much as for safety:
each proves that the occupant really is a `Teleport` before the code touches `target_room`.

Stage 1 does test types,
with `isinstance(occupant, Robot)` and `isinstance(occupant, Teleport)`.
That is not the type switch polymorphism removes.
`GameBuilder` still must tell the kinds of item apart, once,
and the movement code that runs afterward never asks again.
The `Robot` branch also explains `Room(Empty())`:
the robot is the one item that does not become an occupant.
Its cell gets an `Empty` occupant instead,
so when the robot moves away the room behaves like any other empty room.
`show_maze()` draws the `R` by checking which room the robot holds rather than reading an occupant.

### Testing the Walk

`show_maze()` renders the maze into a string,
so a test can check the model without opening a window.
Build the maze, run the solution,
and check that the robot finished on the `!` square:

```python
# robot_explorer/test_robot.py
from game import GameBuilder, solution, string_maze
from items import EndGame

def test_solution_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solution)
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

That same model drives a graphical view.
`maze_view.py` imports the maze and the moves,
draws each room as a colored cell,
and steps the robot along the solution on a timer.
The view is the only part that touches the screen.

```python
# robot_explorer/maze_view.py
import tkinter as tk
from typing import Final
from game import GameBuilder, solution, string_maze
from items import Urge

CELL: Final[int] = 20
FILL: Final[dict[str, str]] = {
    "#": "dimgray", "!": "tomato", ".": "khaki",
    "_": "white", "R": "royalblue"}
MOVES: Final[dict[str, Urge]] = {
    "n": Urge.NORTH, "s": Urge.SOUTH,
    "e": Urge.EAST, "w": Urge.WEST}

def show(maze: str = string_maze, moves: str = solution,
         step_ms: int = 80) -> None:
    game = GameBuilder(maze)
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

Three ideas from earlier chapters carry the design.
[Polymorphism](20_Patterns--Rethinking_Objects.md#what-is-polymorphism)
replaces a type switch,
a [factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary)
builds objects from data,
and a [Null Object](20_Patterns--Rethinking_Objects.md#null-object)
removes the check for a missing door.
None of them needs concurrency.

Two further resources on mazes:
a survey of [algorithms to create mazes](https://en.wikipedia.org/wiki/Maze_generation_algorithm),
and Craig Reynolds on [steering behavior for autonomous moving objects](https://www.red3d.com/cwr/steer/),
which is where a robot that decided its own route would start.

## Order from Noise

The two simulations so far confirm designs.
The rats cover every reachable cell because `claim()` is atomic.
The robot reaches the goal because polymorphism handles every encounter.
Both times you knew the outcome in advance and ran the program to confirm it.
This final example is different.
`amplitude()` fixes the shape the sand will trace: the curves are its zero set.
No line of the code computes how two thousand independent random walks find that shape and stay there.
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

The model needs almost nothing.
`amplitude()` is the standing-wave field of a square plate ringing in mode `(m, n)`.
Physics supplies the formula, an approximation for a plate with free edges.
Treat it as given.
All that matters here is its shape.
The field is zero along curves, and those curves are the nodal lines.
A `Grain` is a position.
`step()` is the entire simulation.
Every grain takes one random step,
and the plate's vibration at that grain's location scales the step.
Grains never look at each other and remember nothing.
No line of the code decides where a grain settles,
only the local scaling of its own blind steps.

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
Grains scattered at random feel the field's average, so agitation starts high.
A grain resting on a nodal line feels zero.
One number summarizes how settled the sand is.
`render()` draws grain density as characters,
in the same spirit as `Blackboard.render()`,
so the model can show its state without a window.
The demo shakes the plate 1200 times,
printing agitation at four checkpoints along the way:

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
A loud region flings its grains around until a random wander crosses a quiet line,
where the kicks shrink toward nothing.
Noise can carry a grain into a quiet place.
It cannot carry the grain back out.
The randomness is not fighting the order but producing it.
The curves themselves are no mystery:
`amplitude()`'s zero set draws them directly, without simulating a single grain.
What the run demonstrates is the trap, not the shape:
blind, uncoordinated steps concentrate onto a curve that no grain, and no line of `step()`, ever names.

### Testing a Random Process

A test cannot guess where a particular grain ends up after a million random kicks.
It pins down the aggregate instead.
Shaking must collapse agitation, and no kick may throw a grain off the plate.
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

The tkinter view shows what the text version cannot: the collapse as it unfolds,
and the pattern surviving a change of rules.
Each grain keeps one color from a small palette,
so you can watch individual grains mix while the collective figure forms.
Every 200 frames the view switches the plate to a new mode.
The old figure suddenly sits on loud regions of the new field.
It bursts back into chaos, mixes, and condenses into a different figure.
The order is not a property of the grains.
It belongs to the field on which they sit.

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

`itertools.cycle()` constructs an infinite iterator from any finite iterable:
it yields the source's elements in sequence and starts over when it reaches the end.
`itertools.count(1)` numbers the frames,
the same endless counter that numbered the rats.

## The Less the Agents Know

The chapter began by defining a simulation as objects that act on their own and interact through shared state.
The grains push that definition to its limit.
The shared state is the plate, and the grains only read it.
They never sense each other.
Even so, structure that no agent encodes appears in the aggregate.
This is *emergence*:
global order arising from local rules that never mention it.
The less the agents understand, the more the run can tell you,
because the outcome lives in the interactions rather than the instructions.

The model has a limit worth naming.
Run it longer and agitation never stops falling:
a grain moves roughly five orders of magnitude less per step at 20,000 steps than it did at 100.
The nodal lines keep thinning as long as the plate shakes,
so their width in any one run is set by how many steps you ran, not by the plate.
Real sand on a real bowed plate settles into a moving equilibrium instead of freezing.
Telling the physics from the rule that models it is exercise 7's job:
swap `amplitude()`'s formula for a membrane's, and watch which parts of the figure change and which do not.

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
    Make `claim()` an `async def`, which pulls the `Recorder` protocol,
    `Rat.run()`'s comprehension, and `explore()` along with it,
    and put `await asyncio.sleep(0)` between the membership test and `self.visited.add(...)`.
    Then count how many calls return `True` and compare that count with `len(blackboard.visited)`,
    using a maze that contains a loop.
    `amaze.txt` is a perfect maze,
    so no two rats ever reach one unclaimed cell and the counts always agree.
    `test_rats_and_mazes.py` still passes, because `visited` is a set:
    the guarantee that broke is "one rat per cell", not "every cell visited".
    What does the extra success cost the rats,
    and why does the original `claim()`, with no `await` inside it,
    need no lock?
4.  Add a new kind of `Item` to the robot maze.
    Define a `Coin` subclass of `Item` with the symbol `$` whose `interact()` removes itself the way `Food` does and adds one to a coin count carried by the `Robot`.
    Place a few `$` characters in the maze and report how many the robot collects.
    You shouldn't need to touch `item_factory()`, `Room`, or `GameBuilder`.
    Explain why the factory finds your new item on its own,
    and what it does if you derive `Coin` from `Food` instead.
5.  Compute the solution instead of hard-coding it.
    Write a function that takes a `GameBuilder` and searches the rooms for a path from the robot's room to the `EndGame` room,
    the way `flood()` searches maze cells in `test_rats_and_mazes.py`.
    The room graph has no `is_open()`,
    so the occupant decides whether a room is passable:
    refuse any room holding a `Wall` or an `Edge`,
    and follow a `Teleport` to its target room,
    since stepping onto one moves the robot.
    Turning the room path back into `n`/`s`/`e`/`w` means tracking which `Urge` produced each step.
    Your path comes out the same length as the hard-coded `solution`,
    which is already a shortest one,
    so assert only that the robot finishes on the `!` square,
    as `test_robot.py` does.
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
