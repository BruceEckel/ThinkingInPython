# Flyweight: Solutions

## 1. Door and tree kinds, plus `walkable_neighbors()`

> Add door (`+`, walkable) and tree (`T`, not walkable)
> kinds to `tile_map.py`.
> Extend `Symbol` and `SPECS` to match,
> then write `walkable_neighbors(field, row, col)` returning the count of adjacent walkable cells.
> Confirm the tile pool size still equals the number of kinds,
> however large the map.

<details>
<summary>Where to look</summary>

[Typing the Symbol Set](../../Chapters/35_Patterns--Flyweight.md#typing-the-symbol-set) shows `Symbol` and `SPECS` naming the same kinds, so the two grow together.
Add the new symbols to both and leave `tile()` alone.
For `walkable_neighbors()`, visit the four adjacent cells, skip any outside the grid, and count those whose `walkable` is true.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "#", "+", "T"]
type TileSpec = tuple[str, bool]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

    def label(self, row: int, col: int) -> str:
        ...

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
    "+": ("door", True),
    "T": ("tree", False),
}

@cache
def tile(symbol: Symbol) -> Tile:
    ...

def to_symbol(char: str) -> Symbol:
    ...

def parse_map(text: str) -> list[list[Tile]]:
    ...

def walkable_neighbors(
    field: list[list[Tile]], row: int, col: int
) -> int:
    ...
```

<details>
<summary>Solution</summary>

If you add `"+"` and `"T"` to `SPECS` but leave `Symbol` listing three kinds,
the script still runs and prints `24 5`.
`ty` rejects the `SPECS` annotation with an `invalid-assignment` error,
because the dictionary now holds keys that `Symbol` does not list.
The solution adds both symbols to the `Symbol` literal,
so the two tables name the same five kinds.

```python
# exercise_1.py
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "#", "+", "T"]
type TileSpec = tuple[str, bool]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

    def label(self, row: int, col: int) -> str:
        return f"{self.name} at ({row}, {col})"

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
    "+": ("door", True),
    "T": ("tree", False),
}

@cache
def tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def to_symbol(char: str) -> Symbol:
    if char not in SPECS:
        raise KeyError(char)
    return char

def parse_map(text: str) -> list[list[Tile]]:
    return [[tile(to_symbol(s)) for s in line]
            for line in text.split()]

def walkable_neighbors(
    field: list[list[Tile]], row: int, col: int
) -> int:
    count = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row + dr, col + dc
        if 0 <= r < len(field) and 0 <= c < len(field[r]):
            if field[r][c].walkable:
                count += 1
    return count

field = parse_map("""
    ..~~+.
    ..~~T#
    ......
    ##..~~
""")
cells = [*row for row in field]
print(len(cells), len({id(t) for t in cells}))
#: 24 5
```

**Name each new kind in both tables.** Door and tree tiles need two new symbols in `SPECS`, and the same two
in the `Symbol` literal, so the type checker still flags a `SPECS` key
that `Symbol` does not list. The edit stops there. `tile()` and
`parse_map()` stay as they are.

**Confirm one tile per kind.** Twenty-four cells collapse to five
distinct objects, one per kind (`grass`, `water`, `rock`, `door`,
`tree`), and that count stays at five however large the map grows,
because `@cache` keys on the symbol alone.

</details>
</details>
</details>

## 2. `tracemalloc`, shared vs. unshared tiles

> Use `tracemalloc` to compare the memory `parse_map()` uses on a large map when every cell shares its `Tile` against when each cell gets a new one,
> by removing `@cache` from `tile()`.
> How does the ratio change as the map grows?

<details>
<summary>Where to look</summary>

[Intrinsic and Extrinsic State](../../Chapters/35_Patterns--Flyweight.md#intrinsic-and-extrinsic-state) compares a map that shares its tiles with one that builds a tile per cell.
Write two factories, one with `@cache` and one without, and build the same map with each between `tracemalloc.start()` and `tracemalloc.get_traced_memory()`.
Repeat for several map sizes and compare the peaks as a ratio.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
import tracemalloc
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "#"]
type TileSpec = tuple[str, bool]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@cache
def shared_tile(symbol: Symbol) -> Tile:
    ...

def unshared_tile(symbol: Symbol) -> Tile:
    ...

def to_symbol(char: str) -> Symbol:
    ...

def make_map(size: int) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you leave out the first `tracemalloc.stop()`,
tracing runs straight through both builds,
and the ratio comes out larger at every size.
The unshared peak then counts the shared field, which is still alive, on top of its own.
The solution stops tracing after each build,
so each peak measures that build's allocations alone.

```python
# exercise_2.py
import tracemalloc
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "#"]
type TileSpec = tuple[str, bool]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@cache
def shared_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def unshared_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def to_symbol(char: str) -> Symbol:
    if char not in SPECS:
        raise KeyError(char)
    return char

def make_map(size: int) -> str:
    row = "".join(".~#"[i % 3] for i in range(size))
    return "\n".join(row for _ in range(size))

for size in (50, 100, 200):
    text = make_map(size)
    tracemalloc.start()
    shared_field = [[shared_tile(to_symbol(s))
                     for s in line]
                    for line in text.split()]
    _, shared_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    unshared_field = [[unshared_tile(to_symbol(s))
                       for s in line]
                      for line in text.split()]
    _, unshared_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ratio = round(unshared_peak / shared_peak, 1)
    print(size, "ratio unshared/shared:", ratio)
#: 50 ratio unshared/shared: 6.2
#: 100 ratio unshared/shared: 6.2
#: 200 ratio unshared/shared: 6.9
```

**Compare the peaks across sizes.** The ratio holds near six at every size: about 6x at a 50x50 map,
close to 7x at 200x200. Both peaks grow with the number of
cells, because both versions build the same nested list of references.
The two versions differ in what one cell costs. A cell in the shared field
costs one reference into a pool of three `Tile` objects, while a cell
in the unshared field costs a brand-new `Tile`, roughly six times as
much memory. The flyweight's saving is therefore per cell. The
multiplier stays near six, and the bytes saved grow with the map.

`Tile` is a record, so each unshared `Tile` is a slotted instance
with no `__dict__`. With `@dataclass(frozen=True)` in place of `@record` the
same run reports a ratio near ten, because every unshared `Tile`
then carries a dictionary too.

</details>
</details>
</details>

## 3. Replacing `@record` with `@dataclass` exposes the sharing bug

> Replace `@record` on `Tile` with `@dataclass` and set `field[0][0].walkable = False` on a parsed map.
> Write a test that exposes the resulting bug, then restore `@record`.

<details>
<summary>Where to look</summary>

[Freezing the Shared Tile](../../Chapters/35_Patterns--Flyweight.md#freezing-the-shared-tile) explains why a flyweight must be immutable.
The pool holds one object per kind,
so assigning to an attribute through one cell
is visible through every cell that shares it.
In the test, assign through one cell, then assert on a different cell of the same kind.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from dataclasses import dataclass
from functools import cache
from typing import Final

SPECS: Final[dict[str, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@dataclass  # Not a record
class MutableTile:
    symbol: str
    name: str
    walkable: bool

@cache
def mutable_tile(symbol: str) -> MutableTile:
    ...
```

<details>
<summary>Solution</summary>

If you assert on the cell through which you made the assignment,
the test passes whether or not the cells share a tile.
With `@cache` removed from `mutable_tile()`,
`field[0][0].walkable` is still `False` after the assignment, and no bug shows.
The test asserts on `field[1][1]` instead, a different grass cell,
whose `walkable` turns `False` only when the cells share one `MutableTile`.

```python
# exercise_3.py
from dataclasses import dataclass
from functools import cache
from typing import Final

SPECS: Final[dict[str, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@dataclass  # Not a record
class MutableTile:
    symbol: str
    name: str
    walkable: bool

@cache
def mutable_tile(symbol: str) -> MutableTile:
    name, walkable = SPECS[symbol]
    return MutableTile(symbol, name, walkable)

field = [[mutable_tile(s) for s in line]
         for line in "..\n..".split()]
field[0][0].walkable = False  # Meant to change one cell...
print(field[0][1].walkable, field[1][0].walkable,
      field[1][1].walkable)
#: False False False
```

**Expose the shared state.** Setting `walkable = False` on the tile at `(0, 0)` changes `walkable`
for every other grass cell in the map too, because all four cells
share one `MutableTile` object. This test pins down the bug:

```python
# test_ch35_mutation_leak.py
from dataclasses import dataclass
from functools import cache
from typing import Final

SPECS: Final[dict[str, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@dataclass  # Not a record
class MutableTile:
    symbol: str
    name: str
    walkable: bool

@cache
def mutable_tile(symbol: str) -> MutableTile:
    name, walkable = SPECS[symbol]
    return MutableTile(symbol, name, walkable)

def test_mutation_without_frozen_leaks_across_cells(
) -> None:
    field = [[mutable_tile(s) for s in line]
             for line in "..\n..".split()]
    field[0][0].walkable = False
    assert field[1][1].walkable is False  # Bug: cell leaked
```

If you restore `@record`, this test stops at its assignment.
`field[0][0].walkable = False` raises a `FrozenInstanceError`,
because a record rejects assignment to every attribute. The assignment
the bug needs fails, and that refusal makes sharing one
object safe.

</details>
</details>
</details>

## 4. Modeling chess

> Model chess: a frozen `Piece` (color, kind)
> and a board that is a `dict` mapping squares to pieces.
> A full opening position holds thirty-two piece references.
> How many `Piece` objects exist?
> How do you capture and promote?

<details>
<summary>Where to look</summary>

[Intrinsic and Extrinsic State](../../Chapters/35_Patterns--Flyweight.md#intrinsic-and-extrinsic-state) separates what a piece is (color and kind) from where it stands.
Share the first through a `@cache` factory keyed on color and kind, and keep the second as the `dict` key.
A capture or a promotion then puts a different shared `Piece` on a square and leaves every `Piece` object unchanged.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from enum import Enum
from functools import cache
from record import record

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Kind(Enum):
    PAWN = "P"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"

@record
class Piece:
    color: Color
    kind: Kind

@cache
def piece(color: Color, kind: Kind) -> Piece:
    ...

type Square = tuple[str, int]

def starting_position() -> dict[Square, Piece]:
    ...

def move(
    board: dict[Square, Piece], src: Square, dst: Square
) -> None:
    # Overwrites dst's old occupant
    ...

def promote(
    board: dict[Square, Piece], square: Square, kind: Kind
) -> None:
    ...
```

<details>
<summary>Solution</summary>

If you promote by assigning to the piece, as in `board[square].kind = kind`,
the frozen `Piece` rejects the assignment with a `FrozenInstanceError`.
If you drop the freeze so the assignment succeeds,
promoting the pawn on `e4` turns every white pawn into a queen,
because every white pawn is the same object.
`promote()` leaves the shared `Piece` alone and points the square at a different one.

```python
# exercise_4.py
from enum import Enum
from functools import cache
from record import record

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Kind(Enum):
    PAWN = "P"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"

@record
class Piece:
    color: Color
    kind: Kind

@cache
def piece(color: Color, kind: Kind) -> Piece:
    return Piece(color, kind)

type Square = tuple[str, int]

def starting_position() -> dict[Square, Piece]:
    board: dict[Square, Piece] = {}
    back_rank = [Kind.ROOK, Kind.KNIGHT, Kind.BISHOP,
                 Kind.QUEEN, Kind.KING, Kind.BISHOP,
                 Kind.KNIGHT, Kind.ROOK]
    for file, kind in zip("abcdefgh", back_rank):
        board[(file, 1)] = piece(Color.WHITE, kind)
        board[(file, 8)] = piece(Color.BLACK, kind)
    for file in "abcdefgh":
        board[(file, 2)] = piece(Color.WHITE, Kind.PAWN)
        board[(file, 7)] = piece(Color.BLACK, Kind.PAWN)
    return board

def move(
    board: dict[Square, Piece], src: Square, dst: Square
) -> None:
    # Overwrites dst's old occupant
    board[dst] = board.pop(src)

def promote(
    board: dict[Square, Piece], square: Square, kind: Kind
) -> None:
    current = board[square]
    # A shared Piece
    board[square] = piece(current.color, kind)

board = starting_position()
print(len(board), len({id(p) for p in board.values()}))
#: 32 12
move(board, ("e", 2), ("e", 4))
print(("e", 2) in board, board[("e", 4)].kind)
#: False Kind.PAWN
promote(board, ("e", 4), Kind.QUEEN)
queen = board[("e", 4)]
print(queen.color, queen.kind)
#: Color.WHITE Kind.QUEEN
```

**Share one piece per color and kind.** `starting_position()` fills thirty-two squares with twelve
distinct `Piece` objects: two colors times six kinds. Every white pawn
is the same object, and every other color-and-kind combination
collapses the same way. The board is a `dict` mapping squares to
references. That mapping keeps the extrinsic position separate from
the intrinsic color-and-kind that `@cache` shares.

**Capture by replacing a reference.** Capturing leaves every `Piece` object alive. `board[dst] = ...`
replaces the reference at `dst`, the captured piece, with the moving
piece's reference. The captured piece's flyweight stays in the cache,
because it represents "a black knight" in the abstract rather than any
particular knight on a square. A capture removes a position from the
board, and the twelve `Piece` objects remain however many captures
follow.

**Promote by switching flyweights.** `promote()` points a square at a different flyweight, because a frozen
`Piece` cannot change its color or kind. `piece(current.color, kind)`
looks up (or builds) a different shared `Piece`, and the board points
at that one instead.

</details>
</details>
</details>

## 5. `interned_color.py`, rewritten on a weak pool

> Rewrite `interned_color.py` to hold its pool weakly, as `weak_pool.py` does,
> and show that building and dropping a palette of colors leaves the pool empty.
> Say what the rewrite gave up to get there.

<details>
<summary>Where to look</summary>

[A Pool That Does Not Leak](../../Chapters/35_Patterns--Flyweight.md#a-pool-that-does-not-leak) holds its flyweights in a `WeakValueDictionary` behind a factory function.
Apply that shape to `Color`, and remember that a weak reference needs a slot for it, which `record()` does not forward.
To see what the rewrite gives up, compare how callers construct a `Color` here with [Interning in the Constructor](../../Chapters/35_Patterns--Flyweight.md#interning-in-the-constructor).

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

type RGB = tuple[int, int, int]

@dataclass(frozen=True, slots=True, weakref_slot=True)
class Color:
    red: int
    green: int
    blue: int

def make_color(red: int, green: int, blue: int) -> Color:
    ...
```

<details>
<summary>Solution</summary>

If you keep `@record` on `Color`,
the first `make_color()` call raises a `TypeError` at `_pool[key] = found`,
because the `WeakValueDictionary` cannot create a weak reference to a slotted `Color` with no `__weakref__` slot.
The solution writes the `dataclass` call out with `weakref_slot=True`,
which adds that one slot and still no `__dict__`.

```python
# exercise_5.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

type RGB = tuple[int, int, int]

@dataclass(frozen=True, slots=True, weakref_slot=True)
class Color:
    red: int
    green: int
    blue: int

_pool: Final[WeakValueDictionary[RGB, Color]] = (
    WeakValueDictionary())

def make_color(red: int, green: int, blue: int) -> Color:
    key = (red, green, blue)
    found = _pool.get(key)
    if found is None:
        found = Color(red, green, blue)
        _pool[key] = found
    return found

palette = [make_color(r, 0, 0) for r in range(50)]
print(len(_pool))
#: 50
crimson_a = make_color(220, 20, 60)
crimson_b = make_color(220, 20, 60)
print(crimson_a is crimson_b)
#: True
bypass = Color(220, 20, 60)
print(bypass == crimson_a, bypass is crimson_a)
#: True False
del palette, crimson_a, crimson_b
print(len(_pool))
#: 0
```

**Pool colors weakly behind a factory.** This listing is `weak_pool.py`'s shape applied to colors: a factory
function, `make_color()`, and a `WeakValueDictionary` for the pool.
`Color` is a frozen data class, so it gets a generated `__repr__()`,
`__eq__()`, and `__hash__()`, as the record `Color` in
`interned_color.py` does. Like `weak_pool.py`'s `Name`, this `Color`
writes the `dataclass` call in full, because a weak reference needs
`weakref_slot=True`, which `record()` does not forward.

**Empty the pool on release.** Once `del` drops every
reference to the fifty-shade palette and both crimson names, nothing
keeps those `Color` objects alive, and the pool empties itself with no
explicit cleanup.

The rewrite gives up the constructor syntax and the guarantee that
comes with it. `Color(220, 20, 60)` still runs, but it skips the pool and
builds a second object equal to the pooled one, the same bypass a
direct `Tile(...)` makes in the chapter. Weak references do not force
that trade. `__new__()` can look in a `WeakValueDictionary` as easily
as in a `dict`, as
[Choosing a *Flyweight* and Its Pool](../../Chapters/35_Patterns--Flyweight.md#choosing-a-flyweight-and-its-pool)
says, on a `Color` declared with the same
`@dataclass(frozen=True, slots=True, weakref_slot=True)` line.

</details>
</details>
</details>

## 6. Constraining `interned_color.py`'s components

> Constrain `red`, `green`, and `blue` to `0`-`255` in `interned_color.py`.
> Raise `ValueError` from `__new__()` for an out-of-range component,
> and write a test for it.

<details>
<summary>Where to look</summary>

[Interning in the Constructor](../../Chapters/35_Patterns--Flyweight.md#interning-in-the-constructor) puts the pool lookup in `__new__()`.
Check each component against the range at the top of `__new__()`, before the lookup, so an invalid `Color` never reaches the pool.
The test uses `pytest.raises(ValueError)` once for a component above the range and once for one below it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import ClassVar
from exceptions import expect
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(
        cls, red: int, green: int, blue: int
    ) -> Color:
        ...
```

<details>
<summary>Solution</summary>

If you validate the components in `__post_init__()`,
`Color(300, 0, 0)` still raises a `ValueError`,
but only after `__new__()` has pooled the instance.
`Color._pool` then keeps an out-of-range `Color(red=300, green=0, blue=0)`.
The solution checks the components at the top of `__new__()`, before the lookup,
so an invalid `Color` stays out of the pool.

```python
# exercise_6.py
from typing import ClassVar
from exceptions import expect
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(
        cls, red: int, green: int, blue: int
    ) -> Color:
        components = (("red", red), ("green", green),
                      ("blue", blue))
        for name, value in components:
            if not (0 <= value <= 255):
                raise ValueError(
                    f"{name}={value} out of range 0-255")
        key: RGB = (red, green, blue)
        if key not in cls._pool:
            cls._pool[key] = super().__new__(cls)
        return cls._pool[key]

expect(ValueError, Color, 300, 0, 0)
#: [ValueError] red=300 out of range 0-255
```

```python
# test_ch35_out_of_range.py
from typing import ClassVar
import pytest
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(
        cls, red: int, green: int, blue: int
    ) -> Color:
        components = (("red", red), ("green", green),
                      ("blue", blue))
        for name, value in components:
            if not (0 <= value <= 255):
                raise ValueError(
                    f"{name}={value} out of range 0-255")
        key: RGB = (red, green, blue)
        if key not in cls._pool:
            cls._pool[key] = super().__new__(cls)
        return cls._pool[key]

def test_out_of_range_component_raises() -> None:
    with pytest.raises(ValueError):
        Color(256, 0, 0)
    with pytest.raises(ValueError):
        Color(0, -1, 0)
```

**Validate before the pool lookup.** The check runs first in `__new__()`, before the pool lookup, so
`__new__()` raises a `ValueError` for an out-of-range component before
it can find a pooled instance or build a new one. Every `Color` that
`__new__()` pools or returns has in-range components.

The check is the same *parse, don't validate* move
[Data Classes as Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#parse-dont-validate)
makes with `__post_init__()`. Here the class validates in `__new__()`
instead, because interning must intercept construction.

</details>
</details>
</details>

## 7. `tile_map.py` rebuilt on the enum

> Rewrite `tile_map.py` on top of `tile_enum.py`'s `Tile`,
> so `parse_map()` returns `list[list[Tile]]` of enum members and `to_symbol()` disappears.
> What does the type checker now catch that the `Literal` version caught,
> and what does it catch that the `Literal` version did not?

<details>
<summary>Where to look</summary>

[A Fixed Set: Enum](../../Chapters/35_Patterns--Flyweight.md#a-fixed-set-enum) lets the language hold the pool, so `Tile(symbol)` is the lookup.
Move the spec table into the member values and delete `to_symbol()`.
For the comparison, consider where each version reports a wrong symbol: a misspelled member, and a symbol that arrives as data.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from enum import Enum
from exceptions import expect

class Tile(Enum):
    GRASS = (".", True)
    WATER = ("~", False)
    ROCK = ("#", False)

    walkable: bool

    def __new__(cls, symbol: str, walkable: bool) -> Tile:
        ...

def parse_map(text: str) -> list[list[Tile]]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from enum import Enum
from exceptions import expect

class Tile(Enum):
    GRASS = (".", True)
    WATER = ("~", False)
    ROCK = ("#", False)

    walkable: bool

    def __new__(cls, symbol: str, walkable: bool) -> Tile:
        member = object.__new__(cls)
        member._value_ = symbol
        member.walkable = walkable
        return member

def parse_map(text: str) -> list[list[Tile]]:
    return [[Tile(s) for s in line]
            for line in text.split()]

field = parse_map("""
    ..~~..
    ..~~.#
    ......
    ##..~~
""")
cells = [*row for row in field]
print(len(cells), len({id(t) for t in cells}))
#: 24 3
print(field[0][2] is field[3][5], field[0][2].walkable)
#: True False
expect(ValueError, parse_map, "?")
#: [ValueError] '?' is not a valid Tile
```

**Let the enum hold the pool.** `SPECS`, `tile()` and `to_symbol()` all disappear. The member tuples
are the spec table, and `Tile(s)` is the pool lookup. `Tile(s)` checks
membership at runtime against the value-to-member table the metaclass
builds, the check `to_symbol()` does by hand.

The type checker still catches what the `Literal` version catches
where the mistake can still occur. A `match` over `Tile` that leaves out a
member draws the same `invalid-return-type` as a `match` over `Symbol`
that leaves out a symbol. The enum rules out the drift against which
the `SPECS` annotation guards, a key that `Symbol` does not list,
because the enum declares the set once instead of twice.

The enum adds one check. A misspelled or missing member, such as
`Tile.DOOR`, is an `unresolved-attribute` error. The `Literal` version
misses the matching mistake. `@cache` hides `tile()`'s `Symbol`
parameter from callers, so `tile("+")` passes the type checker and
fails at runtime with a `KeyError`.

An unknown symbol that arrives as data is a runtime failure in both
versions. The type checker passes `Tile("?")`, and the call raises a
`ValueError`.

The enum gives up the moment of failure. `to_symbol()` raises a
`KeyError` at a named boundary. `Tile("?")` raises a `ValueError`
from deep inside `parse_map()`'s comprehension.
If the boundary matters, keep a `to_tile()` wrapper that catches the
`ValueError` and re-raises it with the offending line and column.

</details>
</details>
</details>

## 8. Four threads on a cold key

> Make `tile()`'s body slow,
> with a `time.sleep(0.05)` before it builds the `Tile`,
> and call it from four threads with the same, previously unseen symbol.
> How many `Tile` objects get built,
> and how many distinct objects do the four threads hold?
> Fix it two ways: populate the pool eagerly at import,
> and guard the factory with a `threading.Lock`.

<details>
<summary>Where to look</summary>

[Sharing, Not Caching](../../Chapters/35_Patterns--Flyweight.md#sharing-not-caching) says a flyweight's factory exists to guarantee identity, and [Interning in the Constructor](../../Chapters/35_Patterns--Flyweight.md#interning-in-the-constructor) says `@cache` checks the key and stores the result in separate steps.
The `time.sleep()` widens the gap between those steps, so every thread can miss before any thread stores.
For the fixes, build every `Tile` into a table before starting any thread, and separately wrap the call to `tile()` in a `threading.Lock`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
import threading
import time
from collections.abc import Callable
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "^", "*"]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

SPECS: Final[dict[Symbol, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "^": ("hill", True),
    "*": ("sand", True),
}

@cache
def tile(symbol: Symbol) -> Tile:
    # Widen the window between miss and store
    ...

def gather(
    factory: Callable[[Symbol], Tile], symbol: Symbol
) -> list[Tile]:
    "Call factory(symbol) from four threads at once."
    ...

EAGER: Final[dict[Symbol, Tile]] = {
    s: Tile(s, *spec) for s, spec in SPECS.items()}

def eager_tile(symbol: Symbol) -> Tile:
    ...

def locked_tile(symbol: Symbol) -> Tile:
    ...
```

<details>
<summary>Solution</summary>

If you put the lock inside `tile()`, around the sleep and the
build, the listing's last line prints `4` instead of `1`.
`@cache` checks the key before the body runs, so all four threads
miss and then take turns building their own `Tile`.
The lock orders the builds without preventing any of them.
The solution wraps the call to `tile()`, so the lookup, the build,
and the store all run under one lock.

```python
# exercise_8.py
import threading
import time
from collections.abc import Callable
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "^", "*"]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

SPECS: Final[dict[Symbol, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "^": ("hill", True),
    "*": ("sand", True),
}

@cache
def tile(symbol: Symbol) -> Tile:
    # Widen the window between miss and store
    time.sleep(0.05)
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def gather(
    factory: Callable[[Symbol], Tile], symbol: Symbol
) -> list[Tile]:
    "Call factory(symbol) from four threads at once."
    out: list[Tile] = []
    lock = threading.Lock()

    def worker() -> None:
        found = factory(symbol)
        with lock:
            out.append(found)

    threads = [threading.Thread(target=worker)
               for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return out

raced = gather(tile, "^")
print(len(raced), len({id(t) for t in raced}))
#: 4 4

EAGER: Final[dict[Symbol, Tile]] = {
    s: Tile(s, *spec) for s, spec in SPECS.items()}

def eager_tile(symbol: Symbol) -> Tile:
    return EAGER[symbol]

print(len({id(t) for t in gather(eager_tile, "*")}))
#: 1

guard = threading.Lock()

def locked_tile(symbol: Symbol) -> Tile:
    with guard:
        return tile(symbol)

print(len({id(t) for t in gather(locked_tile, "~")}))
#: 1
```

**Expose the cold-key race.** Each thread builds its own `Tile` and keeps it, so `is` fails between
all four results. `@cache` looks up the key, misses, calls the
function, and stores the result. No lock spans those steps, so four
threads that all miss on the same cold key all run the body. The last
store wins the cache, and every later caller gets that one object,
while the three losing threads hold objects nothing else sees.

Nothing here is a `@cache` defect. A cache that holds a lock across
the call serializes every miss in the program, a worse default than
occasionally building a value twice. For an ordinary memoized
computation, a duplicate build costs time but not correctness.
*Flyweight* raises the stakes, because its whole point is that
`tile("^") is tile("^")`.

**Fill the pool eagerly.** The eager fix builds every value before any
thread exists, so every lookup hits, and only a miss can start a race.
It is the better answer whenever the whole value set fits in one small
table, the same condition that makes an `Enum` work. The eager lookup
is one `dict` index, with no lock to take.

**Guard the factory with a lock.** The lock fix handles an unbounded
value set. Every lookup now serializes, including the hits, which are
the overwhelming majority once the pool is warm. If that serialization
matters, lock only on the miss path with a hand-written pool, checking
the key again inside the lock, since another thread may have filled
that entry while this one waited.

</details>
</details>
</details>
