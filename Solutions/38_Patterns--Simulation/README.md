# Simulation: Solutions

## 1. Testing a `Rat` with a fake blackboard

> Test a `Rat` with a fake blackboard.
> Because `Rat` depends only on the `Board` `Protocol`,
> you can drive it with a stand-in.
> Write a fake whose `claim()` returns a scripted sequence of results and whose `spawn()` records the coordinates it receives instead of starting a rat,
> run one rat with `asyncio.run(rat.run())`,
> and assert which cell the rat kept for itself and which cells it spawned.
> The fake stands in for the real `Blackboard`, `Maze`, and task scheduling.

<details>
<summary>Where to look</summary>

[The Rat and the Blackboard](../../Chapters/38_Patterns--Simulation.md#the-rat-and-the-blackboard)
shows `Rat` calling only the methods of the `Board` `Protocol`.
Write a class with those methods, so it satisfies the `Protocol` by shape.
Make `claim()` return values from an iterator you script,
and have `spawn()` append to a list.
After `asyncio.run(rat.run())`, assert on the rat's position and on that list.

<details>
<summary>Done when</summary>

your test passes against the chapter's `Rat`.
Scripting `claim()` as `[False, True, False, True]` leaves the rat at `(0, -1)` with one spawn at `(1, 0)`,
and the run ends cleanly on the rat's second turn, after your script runs out,
instead of raising a `RuntimeError`.

<details>
<summary>Solution</summary>

The test drives a copy of the chapter's `Rat` with a scripted fake:

```python
# test_ch38_fake_blackboard.py
import asyncio
from dataclasses import dataclass, field
from typing import Final, Protocol

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

class Board(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...

@dataclass
class Rat:
    blackboard: Board
    x: int
    y: int
    number: int = field(init=False)
    start: tuple[int, int] = field(init=False)

    def __post_init__(self) -> None:
        self.number = self.blackboard.next_number()
        self.start = (self.x, self.y)

    async def run(self) -> None:
        while True:
            neighbors = [(self.x + dx, self.y + dy)
                         for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                self.blackboard.log(
                    f"Rat {self.number} ran {self.start} "
                    f"to {(self.x, self.y)}.")
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)  # Sibling rats can run

class FakeBlackboard:
    def __init__(self, claim_results: list[bool]) -> None:
        self.claim_results = iter(claim_results)
        self.spawned: list[tuple[int, int]] = []
        self.messages: list[str] = []

    def claim(self, x: int, y: int) -> bool:
        return next(self.claim_results, False)

    def spawn(self, x: int, y: int) -> None:
        self.spawned.append((x, y))

    def log(self, message: str) -> None:
        self.messages.append(message)

    def next_number(self) -> int:
        return 1

def test_rat_keeps_one_claim_and_spawns_the_rest() -> None:
    # DIRECTIONS tests (0,1), (0,-1), (-1,0), (1,0) in that
    # order. Script the 2nd and 4th as open, the 1st and
    # 3rd as walls or visited:
    fake = FakeBlackboard([False, True, False, True])
    rat = Rat(fake, 0, 0)
    asyncio.run(rat.run())
    # Kept the first successful claim
    assert (rat.x, rat.y) == (0, -1)
    # Spawned a rat at every claim after that
    assert fake.spawned == [(1, 0)]
    assert fake.messages == [
        "Rat 1 ran (0, 0) to (0, -1)."]
```

**Stand in for the blackboard.**
`Rat` depends on the `Board` `Protocol`, not on `Blackboard`,
so any class with the right methods can stand in.

**Script the rat's choices.**
The scripted return values from `claim()` decide which neighbor the rat keeps and where it spawns new rats.

**Stop the rat when the script ends.**
Once the script runs out, `claim()` returns `False` for every cell,
so the rat dead-ends on its second turn, the way it does against walls,
and `run()` returns.
If you call `next(self.claim_results)` without the `False` default,
the fake works for the rat's first turn and fails on its second.
The fifth `claim()` finds the script empty,
so `next()` raises a `StopIteration` inside the coroutine,
and Python turns it into a `RuntimeError` ("coroutine raised StopIteration")
that fails the test.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. Reporting unreached cells

> Report the cells no rat reaches.
> After `explore()` finishes,
> compare `blackboard.visited` against every open cell of the `Maze` and print the open cells that no rat claimed.
> Build a maze for which that set is not empty,
> and explain what makes a cell unreachable.

<details>
<summary>Where to look</summary>

[Running the Maze](../../Chapters/38_Patterns--Simulation.md#running-the-maze)
shows `explore()` starting the exploration from one entry cell and recording what the rats claim in `blackboard.visited`.
Build a set of every open cell in the `Maze` and subtract `visited` from it.
To leave cells in the difference,
draw a maze whose walls split the open cells into separate regions.
Then ask where every rat begins.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        ...

    @classmethod
    def from_text(cls, text: str) -> Self:
        ...

    def is_open(self, x: int, y: int) -> bool:
        ...

    def entry(self) -> Coord:
        ...

@dataclass
class Rat:
    blackboard: Blackboard
    x: int
    y: int

    async def run(self) -> None:
        ...

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        ...

    def spawn(self, x: int, y: int) -> None:
        ...

    async def explore(self) -> None:
        ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your script prints a nonempty set of open cells,
every printed cell lies in a region that walls separate from the cell `Maze.entry()` returns,
and opening a doorway in that wall makes the printed set empty.
You can say why every rat starts inside the entry's region.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

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
        rows = [line for line in text.splitlines() if line]
        return cls(rows)

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")

@dataclass
class Rat:
    blackboard: Blackboard
    x: int
    y: int

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        self.group.create_task(Rat(self, x, y).run())

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

two_rooms: Final[str] = """
*********
*   *   *
*   *   *
*   *   *
*********
"""

async def main() -> None:
    maze = Maze.from_text(two_rooms)
    board = Blackboard(maze)
    await board.explore()
    all_open = {(x, y) for y in range(maze.height)
                for x in range(maze.width)
                if maze.is_open(x, y)}
    unreached = all_open - board.visited
    print(len(unreached), min(unreached), max(unreached))

asyncio.run(main())
#: 9 (5, 1) (7, 3)
```

The smallest and largest unreached cells, `(5, 1)` and `(7, 3)`,
are the corners of the right room.

**Reuse the chapter's classes.**
The classes come from the chapter, with six parts removed: rat numbers, logging,
`render()`, the `Board` `Protocol`, the file loader,
and the comment-line test in `from_text()`.
The removals leave the exploration logic as the chapter wrote it.
`claim()` keeps the chapter's body word for word.
`explore()` still opens a `TaskGroup` and lets `spawn()` add tasks to that group,
because new rats keep arriving after the block begins.

**Split the open cells into two regions.**
Build a maze with two rooms and a solid wall between them:

```
*********
*   *   *
*   *   *
*   *   *
*********
```

The rats start in the left room.
They map every cell of that room,
so `unreached` holds the right room's nine open cells.

A cell is unreachable when every route to it from the entry crosses a wall.
Walls on all four sides of one cell are the smallest case.
Every cell of the right room has open neighbors,
yet the wall between the rooms separates each one from the entry.

The first rat starts on the cell `Maze.entry()` returns,
and every later rat starts on an open cell next to one that a rat occupies.
The rats therefore stay inside the region of open cells joined to the entry,
however many of them spawn.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Breaking `claim()`'s atomicity

> Break the atomicity of `claim()`.
> Make `claim()` an `async def`,
> which forces matching changes in the `Board` protocol,
> `Rat.run()`'s comprehension, and `explore()`.
> Put `await asyncio.sleep(0)` between the membership test and `self.visited.add(...)`.
> Then count how many calls return `True` and compare that count with `len(blackboard.visited)`,
> using a maze that contains a loop.
> `amaze.txt` is a perfect maze, so a single rat reaches each unclaimed cell.
> In that maze the counts always agree.
> `test_rats_and_mazes.py` still passes, because `visited` is a set.
> The guarantee that broke is "one rat per cell", not "every cell visited".
> What happens to the two rats that both claimed one cell,
> and why does the original `claim()`, with no `await` inside it,
> need no lock?

<details>
<summary>Where to look</summary>

[Contention on a Loop](../../Chapters/38_Patterns--Simulation.md#contention-on-a-loop)
shows two rats reaching one unclaimed cell,
and [The Rat and the Blackboard](../../Chapters/38_Patterns--Simulation.md#the-rat-and-the-blackboard)
shows the `claim()` you are changing.
Making `claim()` an `async def` means each caller must `await` it,
so the `Protocol`, the comprehension, and `explore()` all change.
Count the `True` results in a field on the `Blackboard` and compare the count with `len(visited)`.
A coroutine gives up control only at an `await`,
so whether `claim()` needs a lock depends on whether an `await` sits inside it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

LAYOUT: Final[str] = ...

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        ...

    @classmethod
    def from_text(cls, text: str) -> Self:
        ...

    def is_open(self, x: int, y: int) -> bool:
        ...

    def entry(self) -> Coord:
        ...

class Board(Protocol):
    async def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...

@dataclass
class Rat:
    blackboard: Board
    x: int
    y: int

    async def run(self) -> None:
        ...

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    true_claims: int = field(init=False, default=0)
    group: asyncio.TaskGroup = field(init=False)

    async def claim(self, x: int, y: int) -> bool:
        ...

    def spawn(self, x: int, y: int) -> None:
        ...

    async def explore(self) -> None:
        ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

on the seven-by-nine maze from `test_rats_and_mazes.py`,
your count of `True` returns exceeds `len(blackboard.visited)`
(the solution prints 25 against 24), `amaze.txt` gives equal counts,
and taking the `await asyncio.sleep(0)` back out of `claim()` makes the counts agree again.

<details>
<summary>Solution</summary>

If you test the broken `claim()` on `amaze.txt`,
the count of `True` returns equals `len(visited)` on every run,
and the inserted `await` looks harmless.
A perfect maze offers one path to each cell,
so each cell has one rat approaching it.
The solution uses the seven-by-nine maze from `test_rats_and_mazes.py`,
whose loop lets two rats approach one cell from opposite directions.

```python
# exercise_3.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

LAYOUT: Final[str] = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""

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
        rows = [line for line in text.splitlines() if line]
        return cls(rows)

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")

class Board(Protocol):
    async def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...

@dataclass
class Rat:
    blackboard: Board
    x: int
    y: int

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if await self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    true_claims: int = field(init=False, default=0)
    group: asyncio.TaskGroup = field(init=False)

    async def claim(self, x: int, y: int) -> bool:
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            # The gap: another rat can run
            await asyncio.sleep(0)
            self.visited.add((x, y))
            self.true_claims += 1
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        self.group.create_task(Rat(self, x, y).run())

    async def explore(self) -> None:
        start = self.maze.entry()
        await self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

async def main() -> None:
    board = Blackboard(Maze.from_text(LAYOUT))
    await board.explore()
    print("claims that returned True:", board.true_claims)
    print("cells visited:", len(board.visited))

asyncio.run(main())
#: claims that returned True: 25
#: cells visited: 24
```

**Carry the `async` to every caller.**
The one requested change forces three more edits,
because a caller must `await` an `async def` to get its result.
`spawn()` stays synchronous,
because `create_task()` schedules the new rat and returns at once.

**Let two rats claim one cell.**
On the chapter's seven-by-nine test maze,
`claim()` returns `True` 25 times for 24 open cells,
because two rats claimed the same cell.
The first rat to test the shared cell finds it unclaimed and suspends at `await asyncio.sleep(0)` before adding it to `visited`.
The second rat runs during that pause, finds the cell still unclaimed,
and passes the same test.
Both rats then add the cell and return `True`.

Each of the two rats acts on its `True` as if it alone held the shared cell.
Both move into it.
That overlap breaks the invariant of one rat per cell.
The extra `True` sends the second rat into a cell another rat has claimed,
so the second rat repeats the first rat's move.
Here the shared cell is `(5, 5)`, where the loop closes,
so both rats find every neighbor claimed and dead-end there.

The exploration still reaches every cell.
`visited` stays correct too,
because adding a cell to a set a second time leaves the set as it was.
`test_rats_and_mazes.py` asserts the set of cells reached,
so it passes on the broken version every time.
Comparing the count of `True` returns with the size of `visited` exposes the double claim.

The original `claim()` needs no lock because it has no `await` between the test and the add.
A coroutine yields control only at an `await`,
so the two statements run as one atomic step.
The event loop can hand control to another rat before the test or after the add,
but not between them.
Adding the `await` lets the event loop run another rat between the test and the add.
That interleaving breaks the guarantee.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4 and 5: the robot world

Exercises 4 and 5 both build on the same `robot_explorer` world,
so one module holds that shared apparatus once.
Each exercise imports it.

```python
# robot_world.py
from enum import Enum
from itertools import groupby
from typing import ClassVar, Final, override

class Urge(Enum):
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"

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
        self.finished = False
        # Exercise 4: a place to count Coin pickups
        self.coins = 0

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
    symbol: ClassVar[str] = ""  # Shown as its target letter
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

class EndGame(Item):
    symbol: ClassVar[str] = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        robot.finished = True
        return room

def item_factory(symbol: str) -> Item:
    for item_type in Item.__subclasses__():
        if symbol == item_type.symbol:
            return item_type()
    # Anything else is a teleport target
    return Teleport(symbol)

type Coord = tuple[int, int]
type RoomMap = dict[Coord, Room]
type Moves = str

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

# The void outside the maze
EDGE: Final[Room] = Room(Wall())

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[tuple[Teleport, Room]] = []
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
                    teleports.append((occupant, room))
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        teleports.sort(key=lambda entry: entry[0].target)
        for letter, group in groupby(
            teleports, key=lambda entry: entry[0].target
        ):
            pair = list(group)
            assert len(pair) == 2, letter
            (t1, room1), (t2, room2) = pair
            t1.target_room = room2
            t2.target_room = room1

    def run(self, moves: Moves) -> None:
        for char in moves:
            self.robot.move(Urge(char))
```

## 4. A `Coin` item

> Add a new kind of `Item` to the robot maze.
> Define a `Coin` subclass of `Item` with the symbol `$`.
> Its `interact()` removes the coin from its room,
> as `Food`'s `interact()` does for the food,
> and adds one to a coin count carried by the `Robot`.
> Place a few `$` characters in the maze and report how many the robot collects.
> `item_factory()`, `Room`, and `GameBuilder` stay as they are.
> Explain why the factory finds your new item on its own,
> and what the factory does if you derive `Coin` from `Food` instead.

<details>
<summary>Where to look</summary>

[Rooms, Robots, and the Item Factory](../../Chapters/38_Patterns--Simulation.md#rooms-robots-and-the-item-factory)
shows how `Food.interact()` replaces its own occupant and how `item_factory()` finds an `Item` class from its `symbol`.
Give `Coin` the `$` symbol, an `interact()` that does the same replacement,
and a count on `Robot`.
To see why the factory finds `Coin` by itself,
read which classes `Item.__subclasses__()` returns.
Then check whether a class derived from `Food` appears in that list.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import ClassVar, override
from robot_world import (Empty, GameBuilder, Item,
                         Robot, Room)

class Coin(Item):
    symbol: ClassVar[str] = "$"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...
```

<details>
<summary>Done when</summary>

walking the robot over the `$` cells you placed prints that many coins,
and `item_factory("$")` returns a `Coin`.
With two `$` cells, deriving `Coin` from `Food` instead makes `item_factory("$")` return a `Teleport` and leaves the count at `0`.

<details>
<summary>Solution</summary>

If you derive `Coin` from `Food`, the program prints `0`,
and `item_factory("$")` returns a `Teleport`.
`Item.__subclasses__()` returns `Food` and leaves its subclass `Coin` off the list,
so the factory treats `$` as a teleport target.
The solution derives `Coin` from `Item`,
which puts it on the list the factory searches.

```python
# exercise_4.py
from typing import ClassVar, override
from robot_world import (Empty, GameBuilder, Item,
                         Robot, Room)

class Coin(Item):
    symbol: ClassVar[str] = "$"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Collected, like Food
        robot.coins += 1
        return room

game = GameBuilder("#####\nR$$.#\n#####")
game.run("ee")
print(game.robot.coins)
#: 2
```

**Register the item by subclassing.**
`item_factory()` stays as it is.
`__subclasses__()` reports the subclasses that exist at the time of the call,
so `class Coin(Item)` in `exercise_4.py` puts `Coin` on the list the factory searches.

**Act through the shared interface.**
`Room` and `GameBuilder` stay as they are too.
`GameBuilder` singles out `Robot` and `Teleport`, which need extra wiring,
and accepts every other item as the factory returns it.

**Give the robot a counter.**
`robot_world.py` above carries the one new line in `Robot.__init__()`,
`self.coins = 0`, so `exercise_4.py` holds the `Coin` class and the demo.

Deriving `Coin` from `Food` instead breaks the maze.
The cause is where the factory searches, not what `Coin` inherits.
`item_factory()` walks `Item.__subclasses__()`,
which lists the direct subclasses of `Item` and leaves out their descendants,
`Coin(Food)` among them.
The loop runs to its end and falls through to the factory's last line,
which treats every other symbol as a teleport target.
So `item_factory("$")` returns `Teleport("$")`.
The two `$` cells become a teleport pair.
The route `"ee"` sends the robot through a teleporter where the maze should hold a coin,
so `game.robot.coins` stays `0`.
A one-word change to a class header moves `Coin` out of the factory's search.
The factory then silently substitutes a different `Item`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Sending the robot somewhere other than the `!`

> Send the robot to something other than the `!`.
> `solve()` stops at whatever room holds an `EndGame`,
> the one goal it can express.
> Replace that `isinstance()` test with a `Callable[[Room], bool]` parameter,
> so the caller says what counts as arriving,
> and leave the rest of the search as it is,
> beyond letting `solve()` return `None` when the search runs out of rooms.
> Then use the new parameter to feed the robot:
> search for the nearest room holding a `Food`, walk there,
> and repeat until no `Food` remains,
> then search for the `!` and walk the route the search finds.
> Report how many pieces of food the robot ate and how many moves the whole tour took.
> The run answers two questions for you.
> Why must the search run again after every meal instead of once at the start?
> And why does asking for the nearest food each time not produce the shortest tour that eats everything?

<details>
<summary>Where to look</summary>

[Choosing the Path](../../Chapters/38_Patterns--Simulation.md#choosing-the-path)
shows `solve()` searching breadth-first and stopping at the room that holds an `EndGame`.
Replace that `isinstance()` test with a call to the `Callable[[Room], bool]` parameter,
and return `None` when the queue empties.
Write one small predicate function for food and another for the `!`.
Loop with the walrus operator, `while (leg := solve(...)) is not None`,
and walk each leg with `run()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections import deque
from collections.abc import Callable
from typing import Final
from robot_world import (EndGame, Food, GameBuilder, Moves,
                         Room, Teleport, Urge, Wall)

def landing(room: Room, urge: Urge) -> Room | None:
    ...

def solve(game: GameBuilder,
          arrived: Callable[[Room], bool]) -> Moves | None:
    ...

def food(room: Room) -> bool:
    ...

def end(room: Room) -> bool:
    ...

MAZE: Final[str] = ...
```

<details>
<summary>Done when</summary>

on the chapter's `MAZE`, your tour prints `16 meals, 282 moves`,
`game.robot.finished` is `True` at the end,
and the search for food returns `None` once the last `Food` is eaten,
so the script reaches the walk to the `!`.

<details>
<summary>Solution</summary>

If you keep the chapter's final `raise ValueError`,
the food loop ends in a traceback.
After the last meal, the search for more food raises `ValueError`,
and the script stops before the walk to the `!` and before either `print()`.
Returning `None` makes an empty search the loop's ordinary exit.

```python
# exercise_5.py
from collections import deque
from collections.abc import Callable
from typing import Final
from robot_world import (EndGame, Food, GameBuilder, Moves,
                         Room, Teleport, Urge, Wall)

def landing(room: Room, urge: Urge) -> Room | None:
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder,
          arrived: Callable[[Room], bool]) -> Moves | None:
    start = game.robot.room
    queue: deque[tuple[Room, Moves]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if arrived(room):
            return path
        for urge in Urge:
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + urge.value))
    return None

def food(room: Room) -> bool:
    return isinstance(room.occupant, Food)

def end(room: Room) -> bool:
    return isinstance(room.occupant, EndGame)

MAZE: Final[str] = """
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

game = GameBuilder(MAZE)
meals = 0
moves = 0
while (leg := solve(game, food)) is not None:
    game.run(leg)
    meals += 1
    moves += len(leg)
last = solve(game, end)
assert last is not None
game.run(last)
moves += len(last)
print(meals, "meals,", moves, "moves")
#: 16 meals, 282 moves
print("finished:", game.robot.finished)
#: finished: True
```

**Let the caller define arrival.**
`solve()`'s search changes in one place.
The `isinstance(room.occupant, EndGame)` test becomes `arrived(room)`,
a call to a predicate the caller supplies.
The `EndGame` version is now a one-line function on the caller's side, `end()`,
and `food()` is another.

**Report an empty search as `None`.**
The other change is the return type.
The chapter's version raises a `ValueError` when the search runs out of rooms.
A working maze always has a reachable `!`,
so an exhausted search signals a broken maze.
Here, running out of rooms is the ordinary way the food loop ends,
so `solve()` returns `None`.

**Replan after every meal.**
The search must run again after every meal because each meal changes both the search's start and its goal.
`Food.interact()` replaces the food with an `Empty()`,
so the room where the robot arrived stops being a goal.
The robot now stands in that room, so the next search starts there.
A path holds moves from the room where its search began,
so the search at the start plans only the first leg.
Each later leg needs a search of its own.
Each search visits at most the maze's 299 open rooms,
so searching again is quick.

<!-- vale proselint.GenderBias = NO -->
Nearest-first does not give the shortest tour that eats everything.
Choosing the closest food each time is a greedy choice.
It compares the lengths of the next leg alone.
In some mazes the closest food leads to a longer total walk.
Two pieces of food can sit close together down one dead-end corridor while a third sits one step nearer in the opposite direction,
with the rest of the food far beyond it.
Taking the single near piece first means walking to it,
back past the start to the corridor,
and then past the start again toward the rest.
The robot walks the stretch between the start and the single piece three times.

Finding the shortest complete tour is a travelling-salesman problem over the food rooms.
That tour's first leg is often longer than the shortest leg available.
The greedy tour does guarantee that every leg is a shortest path,
which is all breadth-first search guarantees.
<!-- vale proselint.GenderBias = YES -->

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6, 7, and 8: the Chladni plate

The last three exercises all shake the same plate.
One file combines the chapter's `standing_wave.py` and `chladni.py`.
All three exercises import it.
The file makes two changes:
`Plate` takes the field function as a constructor argument instead of calling the module-level `amplitude()`,
and the module adds `membrane()` beside `amplitude()`.
The `field` argument makes exercise 7's different physics a second function rather than an edit.
The `Plate` there takes `field=membrane`,
while the other two exercises keep the default `amplitude()`.

```python
# chladni.py
import math
import random
from collections.abc import Callable
from dataclasses import dataclass

type Mode = tuple[int, int]  # Vibration pattern (m, n)
type Field = Callable[[float, float, Mode], float]

def amplitude(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.cos(m * math.pi * x)
        * math.cos(n * math.pi * y)
        - math.cos(n * math.pi * x)
        * math.cos(m * math.pi * y))

def membrane(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.sin(m * math.pi * x)
        * math.sin(n * math.pi * y))

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
                 seed: int | None = None,
                 field: Field = amplitude) -> None:
        self.rng = random.Random(seed)
        self.mode = mode
        self.field = field
        self.grains = [
            Grain(self.rng.random(), self.rng.random())
            for _ in range(grains)]

    def step(self, kick: float = 0.05) -> None:
        for g in self.grains:
            a = self.field(g.x, g.y, self.mode)
            g.x = bounce(
                g.x + self.rng.uniform(-kick, kick) * a)
            g.y = bounce(
                g.y + self.rng.uniform(-kick, kick) * a)

    def agitation(self) -> float:
        return sum(
            self.field(g.x, g.y, self.mode)
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

## 6. Freezing the plate

> Freeze the plate.
> Run the Chladni view with `MODES` starting at `(2, 2)`.
> Work out what `amplitude()` returns whenever `m == n`,
> and explain why the view shows neither chaos nor a figure.
> Then explain why the main diagonal shows up in every figure this plate makes.
> Swapping `x` and `y` in the two terms of `amplitude()` is the clue.

<details>
<summary>Where to look</summary>

[The Model](../../Chapters/38_Patterns--Simulation.md#the-model)
shows `step()` scaling each grain's random displacement by `amplitude()`.
Substitute `m == n` into the two products of `amplitude()` and compare them.
For the diagonal, swap `x` and `y` and compare the sign of the difference inside `abs()` before and after.
Then ask what that implies where `x == y`.

<details>
<summary>Done when</summary>

`amplitude()` returns `0.0` at any point for mode `(2, 2)`,
a `Plate` in that mode reports agitation `0.000` with every grain at its starting position after 1200 steps,
and `amplitude()` returns `0.0` wherever `x == y`, for every mode you try.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from chladni import Plate, amplitude

print(amplitude(0.31, 0.79, (2, 2)))
#: 0.0
plate = Plate(grains=2000, mode=(2, 2), seed=42)
before = [(g.x, g.y) for g in plate.grains]
for _ in range(1200):
    plate.step()
after = [(g.x, g.y) for g in plate.grains]
print(f"agitation {plate.agitation():.3f}, "
      f"moved {before != after}")
#: agitation 0.000, moved False
print(amplitude(0.37, 0.37, (1, 2)))
#: 0.0
```

**Probe the field at `m == n`.**
With `m == n`, `amplitude()` returns zero everywhere.
Its two terms become `cos(mπx)cos(mπy)` and `cos(mπx)cos(mπy)`,
the same product written twice, and the function subtracts one from the other.
The two multiplications produce identical floats,
so the difference is exactly `0.0` at every point on the plate,
not approximately zero.

**Confirm that every grain stays put.**
A zero field means a zero kick.
`step()` scales each grain's random displacement by the amplitude under that grain,
so `uniform(-kick, kick) * 0.0` comes to zero and leaves each grain where it is.
The view shows neither chaos nor a figure because every grain stays where it started.
It shows the initial random scatter, frozen.

Agitation reads `0.000` from the start,
the same number a perfectly settled plate reports,
so the summary statistic cannot tell "finished" from "never started."

**Probe a point on the diagonal.**
The main diagonal in every figure follows from the same two terms.
Swapping `x` and `y` turns the first term into the second and the second into the first,
so the swap reverses the subtraction inside `amplitude()`'s `abs()`.
On the line `x == y` the swap leaves the point where it was,
so the subtraction there must equal its own negation.
The one number equal to its own negation is zero.
Every mode in which this plate can ring therefore has a nodal line straight down the main diagonal,
so the figures all share that one feature whichever `(m, n)` produced them.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Changing the physics

> Change the physics.
> Replace the body of `amplitude()` with `abs(math.sin(m * math.pi * x) * math.sin(n * math.pi * y))`,
> the standing waves of a membrane clamped at its edges, like a drumhead.
> Predict the figures before you run the view.
> Why are the nodal lines now straight?

<details>
<summary>Where to look</summary>

[What the Numbers Show](../../Chapters/38_Patterns--Simulation.md#what-the-numbers-show)
explains how agitation measures the plate settling toward its nodal lines.
Pass a second field function to `Plate` and compare the figures.
Write the new field as a product of a function of `x` and a function of `y`.
A product is zero when either factor is zero,
so find where each `sin` factor vanishes.

<details>
<summary>Done when</summary>

you wrote your prediction before running the view,
and for mode `(2, 3)` the rendered plate shows one vertical and two horizontal interior lines plus the four edges,
with agitation falling toward zero as in `chladni_demo.py`.
You can name the `sin` factor that draws each line.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from chladni import Plate, membrane

plate = Plate(grains=2000, mode=(2, 3), seed=42,
              field=membrane)
steps = 0
for target in (0, 100, 400, 1200):
    for _ in range(target - steps):
        plate.step()
    steps = target
    print(f"steps {target:4}: "
          f"agitation {plate.agitation():.3f}")
#: steps    0: agitation 0.406
#: steps  100: agitation 0.100
#: steps  400: agitation 0.014
#: steps 1200: agitation 0.002
print(plate.render(width=40, height=20))
#: #:**# ######:#####..#:##*###############
#: #                  ##                  #
#: #                  ##                 .#
#: #    .             ##                  #
#: #                  ##                  #
#: #                  #*                  #
#: ######################*#################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: *                 .##   .             .#
#: ########################################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #               .  ##                  #
#: ##############**##:##.#:##############.#
```

The nodal lines are straight because the new field is a product of one function of `x` and one function of `y`.
The product vanishes when either factor does.
For `m = 2`, `sin(mπx)` is zero at `x = 0, 1/2, 1`, whatever `y` is.
Those three zeros give vertical lines.
For `n = 3`, `sin(nπy)` is zero at `y = 0, 1/3, 2/3, 1`, whatever `x` is,
giving horizontal lines.
Every nodal point lies on one of those seven lines.
The interior lines number `m - 1` vertical and `n - 1` horizontal,
so you can read the mode numbers straight off the picture.

The plate's own field subtracts one product from another,
`cos(mπx)cos(nπy)` minus `cos(nπx)cos(mπy)`.
Each product separates on its own,
but their difference does not factor into a function of `x` times a function of `y`.
The difference is zero along the curves where the two products agree,
which is why the original figures are diagonals, crosses,
and rings rather than a grid.
The subtraction comes from the physics the chapter's formula approximates,
a real plate with free edges rather than a membrane clamped all around its rim.

The simulation machinery stays the same across both fields: same grains,
same random walk, same rule that a grain moves in proportion to the vibration under it.
Only the field changes, and with it every pattern the model produces.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 8. Tuning the noise

> Tune the noise.
> Rerun `chladni_demo.py` passing `kick=0.005` and then `kick=0.5` to `plate.step()`,
> printing agitation at the same checkpoints.
> One setting produces order too slowly.
> The other drives agitation down as convincingly as the default kick,
> yet no figure appears.
> Explain both failures, and why an intermediate kick avoids them.

<details>
<summary>Where to look</summary>

[The Model](../../Chapters/38_Patterns--Simulation.md#the-model)
shows `step()` multiplying the random kick by the amplitude,
so a grain slows as it nears a nodal line.
Loop over the three kick values with a fresh `Plate` for each,
and print agitation at the same checkpoints.
For the large kick, compare a grain's maximum single step with the size of the plate.
[The Model](../../Chapters/38_Patterns--Simulation.md#the-model)
shows `render()`'s figure, which is the check that agitation cannot make.

<details>
<summary>Done when</summary>

after 1200 steps `kick=0.005` still reads far above zero
(the solution, with mode `(2, 3)` and `seed=42`, prints `0.38`),
`kick=0.5` reads `0.00` like the default,
and rendering the `kick=0.5` plate shows nearly every grain heaped in the corners at `(0, 0)` and `(1, 1)`,
off the nodal lines.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from chladni import Plate

for kick in (0.005, 0.05, 0.5):
    plate = Plate(grains=2000, mode=(2, 3), seed=42)
    steps = 0
    readings = []
    for target in (0, 100, 400, 1200):
        for _ in range(target - steps):
            plate.step(kick=kick)
        steps = target
        readings.append(f"{plate.agitation():.2f}")
    print(f"kick {kick:<5}: {' '.join(readings)}")
#: kick 0.005: 0.58 0.56 0.49 0.38
#: kick 0.05 : 0.58 0.07 0.00 0.00
#: kick 0.5  : 0.58 0.11 0.01 0.00
```

`kick=0.005` produces order too slowly.
Each step displaces a grain by at most one percent of the plate,
so a grain starting in the middle of a loud region needs hundreds of steps to walk anywhere near a nodal line.
Rendered, this run still looks like noise with a faint trace of structure in it.
The physics is correct, but the run needs more steps to finish,
more than anyone wants to watch.

`kick=0.5` fails differently.
Its agitation falls to `0.00` as convincingly as it does at the default kick,
but no figure appears.
One kick moves a grain up to half the plate where the amplitude is 1,
and up to the full width where the amplitude peaks at 2,
so a single step can carry a grain across the plate.
Instead of walking toward the nearest nodal line,
the grain jumps to a random spot and stays only if that spot is quiet.
The spots that hold a grain best are the two corners where the main diagonal ends.
At `(0, 0)` and `(1, 1)` the field is zero and also flat,
so it stays weak over a whole patch,
whereas along a nodal line it is weak only in a thin strip.
Rendered, the run shows nearly every grain in those two corners and the nodal lines between them empty.
The low agitation is accurate.
The sand has settled, in the wrong places.

Agitation measures whether the grains sit where the field is weak,
not whether the figure is right,
so one number cannot distinguish a sharp pattern from two blobs.
The render is the check the number cannot perform.

An intermediate kick avoids both failures because the amplitude scaling in `step()` is a feedback loop.
The loop works within a range of step sizes and fails outside it.
A grain in a loud region gets a large kick and moves fast.
As it nears a nodal line the amplitude shrinks and so does its step,
so the grain slows down and settles on the line.
Too small a kick keeps the step small in a loud region too,
so the grain barely travels.
Too large a kick keeps the step large near a nodal line,
since a small amplitude still leaves the step large enough to carry the grain out of the neighborhood in which it was settling.
With the default `0.05`, a grain both travels and settles.
A step is at most a tenth of the plate where the amplitude peaks,
and vanishingly small once a grain arrives.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
