# Observer: Solutions

## 1. A minimal broadcaster-listener pair

```python
# exercise_1.py
from collections.abc import Callable
from typing import Any

class Broadcaster:
    def __init__(self) -> None:
        self._listeners: list[Callable] = []

    def subscribe(self, listener: Callable) -> None:
        self._listeners.append(listener)

    def announce(self, *args: Any) -> None:
        for listener in self._listeners:
            listener(*args)

calls: list[tuple[str, int]] = []
source = Broadcaster()
source.subscribe(lambda v: calls.append(("A", v)))
source.subscribe(lambda v: calls.append(("B", v)))
source.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
```

Like `broadcaster.py`, this solution has no separate `Observer` class at
all. Any callable, here two `lambda`s, is a listener. `subscribe()`
collects them in a list. `announce()` then hands its own arguments to
each one in turn, so every subscribed listener sees the same update,
in subscription order.

## 2. An `announce()` that survives a failing listener

```python
# exercise_2.py
from collections.abc import Callable

type Listener[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def announce(self, data: T) -> None:
        failures: list[Exception] = []
        for listener in list(self._listeners):
            try:
                listener(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "listener failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

source = Broadcaster[int]()
source.subscribe(broken)
source.subscribe(received.append)
try:
    source.announce(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
```

```python
# test_resilient_announce.py
import pytest
from exercise_2 import Broadcaster

def test_later_listener_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    source = Broadcaster[int]()
    source.subscribe(broken)
    source.subscribe(received.append)
    with pytest.raises(ExceptionGroup):
        source.announce(1)
    assert received == [1]
```

The loop catches each failure and keeps going, so subscription order
stops deciding who hears the change. Collecting the exceptions rather
than discarding them is the other half: a listener that fails silently
is worse than one that stops the loop, because nothing reports the
failure.

`ExceptionGroup` is the right container because more than one listener
can fail on a single notification, and the caller needs every failure,
not the first. `except*` then lets a caller handle one kind of failure
and re-raise the rest, something a plain `except` on a single
re-raised exception cannot do.

Catching bare `Exception` here is deliberate: `announce()` has no idea
what its listeners do, so it cannot name their failure modes. Catching
`Exception` still lets `BaseException` through, so a
`KeyboardInterrupt` or an `asyncio.CancelledError` passing through a
listener stops the notification instead of joining `failures`.

## 3. The same rescue, for the async fan-out

```python
# exercise_3.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncListener[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[AsyncListener[T]] = []

    def subscribe(self, listener: AsyncListener[T]) -> None:
        self._listeners.append(listener)

    async def announce(self, data: T) -> None:
        results = await asyncio.gather(
            *(listener(data)
              for listener in self._listeners),
            return_exceptions=True)
        failures = [
            r for r in results if isinstance(r, Exception)]
        if failures:
            raise ExceptionGroup(
                "listener failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    source = Broadcaster[int]()
    source.subscribe(broken)
    source.subscribe(record)
    try:
        await source.announce(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
```

```python
# test_async_resilient_announce.py
import asyncio
import pytest
from exercise_3 import Broadcaster

def test_later_listener_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        source = Broadcaster[int]()
        source.subscribe(broken)
        source.subscribe(record)
        with pytest.raises(ExceptionGroup):
            await source.announce(1)

    asyncio.run(run())
    assert received == [1]
```

`return_exceptions=True` changes `gather()` from "re-raise the first
failure immediately" to "run everything and hand back a list." That
one keyword does what the synchronous version needed a `try` inside a
loop to do, because `gather()` is already the loop.

The results come back in argument order, so the list is a record of
which listener produced what. This version needs the failures alone,
so its comprehension keeps each result for which
`isinstance(r, Exception)` is true. A successful listener returned
`None`, which fails that test and stays out of `failures`.

The exception filter uses `Exception`, not `BaseException`, for the
reason exercise 2 gives, and for a second reason here.
`asyncio.CancelledError` derives from `BaseException`, and
`return_exceptions=True` still returns a cancellation among the
results. Treating that result as an ordinary listener failure would
swallow a cancellation the event loop meant to propagate.

The synchronous and asynchronous versions now answer the same
question, and both end in an `ExceptionGroup`. The difference is only
where the loop lives: written by hand in the synchronous version,
supplied by `gather()` in the async one.

## 4. Turning `box_observer.py` into a flood-fill game

```python
# exercise_4.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return (a != b and abs(a[0] - b[0]) <= 1
            and abs(a[1] - b[1]) <= 1)

class FloodGame:
    ("Flood-fill game: grow a patch "
     "from the origin to fill the board.")
    def __init__(self, size: int,
                 origin: Coord = (0, 0)) -> None:
        self.size = size
        self.grid = new_grid(size)
        self.origin = origin
        self.moves = 0
        self.owned = self._flood(self.grid[origin])

    def _flood(self, color: Color) -> set[Coord]:
        ("Every cell reachable from origin "
         "through same-colored cells.")
        seen: set[Coord] = set()
        stack = [self.origin]
        while stack:
            cell = stack.pop()
            if cell in seen or self.grid.get(cell) != color:
                continue
            seen.add(cell)
            for other in self.grid:
                if (adjacent(cell, other)
                    and other not in seen):
                    stack.append(other)
        return seen

    def select(self, cell: Coord) -> bool:
        ("Recolor the owned patch "
         "to the selected cell's color.")
        new_color = self.grid[cell]
        if new_color == self.grid[self.origin]:
            return False  # No-op: already this color
        for c in self.owned:
            self.grid[c] = new_color
        # Absorb new neighbors
        self.owned = self._flood(new_color)
        self.moves += 1
        return True

    def is_complete(self) -> bool:
        return len(self.owned) == self.size * self.size

game = FloodGame(4)
while not game.is_complete():
    remaining = [
        c for c in game.grid if c not in game.owned]
    game.select(remaining[0])
print("solved in", game.moves, "moves")
#: solved in 6 moves
```

`_flood()` is a plain graph search (depth-first, using a stack)
starting from `origin`, walking to every neighbor `adjacent()` says it
touches, as long as that neighbor is still the same color.
`FloodGame` reuses `new_grid()` from `box_observer.py` unchanged and
adds the `adjacent()` the exercise asks for. `select()` is the game
move: it repaints
every cell in the *currently owned* patch to the selected cell's color,
then re-runs `_flood()` to pick up the neighbors that now match that
new color and have joined the patch. `game.moves` gives the
single-player scoring the exercise asks for:
the moves it takes to make the whole field one color.
Two players can share the same `select()`
method, alternating whose turn supplies the next color, and after a
fixed number of rounds whoever owns the larger patch wins. `FloodGame`
can also inherit from `Broadcaster[Grid]`, as `BoxModel` does, and
call `self.announce(self.grid)` at the end of a successful `select()`.
`box_view.py`'s existing view then repaints after every move. The
drawing code needs no change, but `show()`'s parameter annotation does:
it names `BoxModel`, and a `FloodGame` is not one. Widening it to a
Protocol (or to `Broadcaster[Grid]` plus `size`, `grid`, and
`select()`) lets the same view draw either model.

## 5. A new selection rule, and the same view

```python
# exercise_5.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    def next(self) -> Color:
        colors = list(Color)
        nxt = colors.index(self) + 1
        return colors[nxt % len(colors)]

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    return grid | {cell: color.next()
                   for cell, color in grid.items()
                   if cell[0] == x or cell[1] == y}

def initials(grid: Grid, size: int) -> str:
    return "\n".join(
        " ".join(grid[(x, y)][0] for x in range(size))
        for y in range(size))

grid = new_grid(4)
print(initials(grid, 4))
#: s p k s
#: p k s p
#: k s p k
#: s p k s
print(initials(recolored(grid, (1, 2)), 4))
#: s k k s
#: p s s p
#: s p k s
#: s k k s
```

`Color` and `new_grid()` are copied from `box_observer.py`
unchanged, and `recolored()` is the one function that differs. It
keeps every cell whose column matches the selection's `x` or whose row
matches its `y`, and advances each one. The cells come from `grid`,
so none lies outside it and the `in grid` test goes away.
`initials()` prints each cell's first letter, one row per line. After
selecting column 1, row 2, that column and that row have moved one
color along, and the other nine cells are as they were.

Pasting this `recolored()` over the one in `box_observer.py` changes
what the window does, and `box_view.py` runs as it stands. The view
has two connections to the model. Its mouse handler calls
`model.select()` with a coordinate, and its `draw()` receives a whole
`Grid` and paints every cell. Neither one says which cells a selection
changes, so the view holds nothing that a new rule could make wrong.
The rule sits in `recolored()`, `BoxModel.select()` calls it, and
`announce()` delivers the result. `initials()` makes the same point
from the other side: it is a second view of a `Grid`, written without
knowing the rule.

## 6. Two views on one model

```python
# exercise_6.py
from collections import Counter
from collections.abc import Callable
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    def next(self) -> Color:
        colors = list(Color)
        nxt = colors.index(self) + 1
        return colors[nxt % len(colors)]

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]
type Listener[T] = Callable[[T], None]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def announce(self, data: T) -> None:
        for listener in list(self._listeners):
            listener(data)

class BoxModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)

model = BoxModel(3)

def letters(grid: Grid) -> None:
    for y in range(model.size):
        print(" ".join(grid[(x, y)][0]
                       for x in range(model.size)))

def tally(grid: Grid) -> None:
    counts = Counter(grid.values())
    print(" ".join(f"{c[0]}:{counts[c]}" for c in Color))

model.subscribe(letters)
model.subscribe(tally)
model.select((1, 1))
#: s k k
#: k s p
#: k p p
#: s:2 p:3 k:4
model.select((0, 0))
#: p s k
#: s s p
#: k p p
#: s:3 p:4 k:2
```

The model is `box_observer.py`'s, copied here so the solution runs on
its own: `Color`, `new_grid()`, and `recolored()` unchanged, and a
`Broadcaster` trimmed to the two methods this example calls.
`BoxModel` is the chapter's, and the exercise adds nothing to it.

`letters()` and `tally()` are the two views. Each takes a `Grid` and
returns `None`, the shape `subscribe()` requires, so each is a
listener the same way `draw()` is. `letters()` prints the first
character of each color, one row per line, and `tally()` counts the
colors with a `Counter`.
Neither one names the other, and neither names the model's rule.

`model.select((1, 1))` calls `recolored()` once and `announce()` once,
and `announce()` calls both views in subscription order. They read the
same `Grid` object, so the letters and the counts describe one state
of the model: the first selection advances the five cells of the
cross, which moves two cells out of `skyblue` and two into `khaki`.
The corner selection that follows has three cells inside the grid
rather than five.

Adding a third view means one more `subscribe()` call. `box_view.py`'s
`draw()` is such a view, and `show(model)` attaches it to a model that
already has these two, so the window and the terminal report the same
grid. Running that combination means `show()` takes over with
`root.mainloop()`, so start it last.

## 7. Which colors a grid can reach

```python
# exercise_7.py
from enum import StrEnum
from typing import Final

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

type Coord = tuple[int, int]
type Row = list[int]

MOD: Final[int] = len(Color)

def cross(cell: Coord, size: int) -> list[Coord]:
    x, y = cell
    around = [(x, y), (x - 1, y), (x + 1, y),
              (x, y - 1), (x, y + 1)]
    return [(a, b) for a, b in around
            if 0 <= a < size and 0 <= b < size]

def system(size: int, target: int) -> list[Row]:
    "One row per cell, with the target in the last column."
    cells = [(x, y) for x in range(size)
             for y in range(size)]
    at = {cell: i for i, cell in enumerate(cells)}
    rows = [[0] * (len(cells) + 1) for _ in cells]
    for cell in cells:
        for other in cross(cell, size):
            rows[at[other]][at[cell]] = 1
    for i, (x, y) in enumerate(cells):
        rows[i][-1] = (target - (x + y)) % MOD
    return rows

def solvable(rows: list[Row]) -> bool:
    width = len(rows[0]) - 1
    pivot = 0
    for col in range(width):
        found = next((r for r in range(pivot, len(rows))
                      if rows[r][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = pow(rows[pivot][col], -1, MOD)
        rows[pivot] = [v * scale % MOD for v in rows[pivot]]
        for r, row in enumerate(rows):
            if r != pivot and row[col]:
                factor = row[col]
                rows[r] = [(a - factor * b) % MOD for a, b
                           in zip(row, rows[pivot])]
        pivot += 1
    # A row of zeros with a nonzero target is 0 == 1
    return all(any(row[:-1]) or row[-1] == 0
               for row in rows)

def reachable(size: int) -> list[Color]:
    return [color for target, color in enumerate(Color)
            if solvable(system(size, target))]

for size in range(3, 9):
    names = ", ".join(reachable(size))
    print(f"{size}x{size}: {names or 'nothing'}")
#: 3x3: skyblue, palegreen, khaki
#: 4x4: skyblue, palegreen, khaki
#: 5x5: nothing
#: 6x6: skyblue, palegreen, khaki
#: 7x7: skyblue, palegreen, khaki
#: 8x8: palegreen
```

Selecting a cell adds one, modulo three, to that cell and to each
neighbor `cross()` finds, and selecting it twice adds two. The order
of the selections makes no difference, so a whole sequence of them is
a count per cell, and the puzzle becomes one linear system: `M v = b`,
over the integers mod 3. `M` records which cells each selection
advances, `v` counts the selections, and `b` is how far each cell must
advance to reach the target color. `system()` builds the two together,
one row per cell, with `b` in the last column.

`solvable()` answers whether that system has a solution, and never
computes one: the question is which colors are reachable, not how.
It is Gaussian elimination, with two changes for arithmetic mod 3.
Dividing by a pivot is multiplying by its inverse, which `pow(x, -1,
MOD)` supplies, and every subtraction ends in `% MOD`. Elimination
either finds a pivot in a column or leaves that column free; what
decides the answer is the rows that survive with every coefficient
zero. Such a row states `0 == row[-1]`, so a nonzero last column means
no count of selections reaches that color.

The six sizes split three ways. At 3x3, 6x6, and 7x7 the matrix has
full rank, so every color is reachable from any starting grid. At 4x4
the rank is 14 of 16, and at 8x8 it is 60 of 64: the missing
dimensions are combinations of cells that no selection can change, so
the starting grid must already agree with the target on each of them.
The 4x4 banded grid agrees for all three colors, and the 8x8 grid for
`palegreen` alone, which is the puzzle the window poses. At 5x5 three
dimensions are missing and no color satisfies them, so that board
cannot be made one color at all.

`Color` is a `StrEnum`, so its members go straight into
`", ".join(reachable(size))` with no conversion, the same property
that lets `box_view.py` hand a `Color` to `tkinter`.

## 8. A descriptor per watched attribute

```python
# exercise_8.py
from collections.abc import Callable
from typing import overload

type Listener[T] = Callable[[T], None]

class Notifying[T]:
    def __set_name__(
        self, owner: type, name: str
    ) -> None:
        self.storage = f"_{name}"
        self.listeners = f"_listeners_{name}"

    @overload
    def __get__(self, obj: None,
                owner: type) -> Notifying[T]: ...
    @overload
    def __get__(self, obj: object,
                owner: type) -> T: ...
    def __get__(self, obj: object | None,
                owner: type) -> T | Notifying[T]:
        if obj is None:
            return self  # Thermometer.celsius
        return getattr(obj, self.storage)

    def __set__(self, obj: object, value: T) -> None:
        setattr(obj, self.storage, value)
        for listener in getattr(obj, self.listeners, ()):
            listener(value)

    def subscribe(self, obj: object,
                  listener: Listener[T]) -> None:
        obj.__dict__.setdefault(
            self.listeners, []).append(listener)

class Thermometer:
    celsius = Notifying[float]()
    humidity = Notifying[float]()

    def __init__(self, celsius: float,
                 humidity: float) -> None:
        self.celsius = celsius
        self.humidity = humidity

t = Thermometer(20.0, 0.4)
readings: list[float] = []
humidities: list[float] = []
Thermometer.celsius.subscribe(t, readings.append)
Thermometer.humidity.subscribe(t, humidities.append)
t.celsius = 25.0
t.humidity = 0.5
t.celsius = 150.0
print(readings, humidities)
#: [25.0, 150.0] [0.5]
print(t.celsius, t.humidity)
#: 150.0 0.5
```

`__set_name__()` receives the name each descriptor was assigned to, so
`celsius` and `humidity` derive different attribute names: `_celsius`
and `_listeners_celsius` for one, `_humidity` and
`_listeners_humidity` for the other. Two `Notifying` instances in one
class therefore share no storage and no listener list, which is what
makes the two attributes independent. `Broadcaster` keeps one list for
the whole object; a descriptor keeps one per attribute.

`__set__()` stores the value and then calls each listener registered
for that attribute, the work `Thermometer`'s property setter did with
`self.announce(value)`.

Class access is the part a validating descriptor never needs.
`Thermometer.celsius` calls `__get__()` with `obj` set to `None`, and
returning the descriptor there puts `subscribe()` within reach. The
two `@overload` declarations tell `ty` which of the two results it
gets: `Notifying[T]` from the class, `T` from an instance. Without
them the declared return type is the union, and `t.celsius * 2` would
fail to check. The overloads also check the listener against the
attribute: `Thermometer.celsius.subscribe(t, readings.append)` passes
only because `readings` is a `list[float]`.

Pyright rejects `Thermometer.celsius.subscribe`.
It reads the constructor's `self.celsius = celsius` as declaring an instance attribute of type `float` beside the descriptor,
so it types the class access as `Notifying[float] | float` and reports that `float` has no `subscribe`.
`ty` types the class access from the `__get__()` overload alone.
A codebase on Pyright looks the descriptor up in `type(obj).__dict__` instead,
which draws no complaint from Pyright.

`subscribe()` writes the listener list into the instance's `__dict__`
rather than declaring it on the class, where every instance would
share one list.
