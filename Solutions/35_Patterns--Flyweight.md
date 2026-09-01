# Flyweight: Solutions

## 1. Door and tree kinds, plus `walkable_neighbors()`

```python
# exercise_1.py
from dataclasses import dataclass
from functools import cache
from typing import Final, Literal

type Symbol = Literal[".", "~", "#", "+", "T"]
type TileSpec = tuple[str, bool]

@dataclass(frozen=True)
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

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

Door and tree tiles need two new symbols in `SPECS`, and the same two
in the `Symbol` literal, so the type checker still flags a `SPECS` key
that `Symbol` does not list. That is the entire edit. `tile()` and
`parse_map()` never change. Twenty-four cells collapse to five
distinct objects, one per kind (`grass`, `water`, `rock`, `door`,
`tree`), and that count stays at five however large the map grows,
because `@cache` keys on the symbol alone.

## 2. `tracemalloc`, cached vs. uncached `tile()`

```python
# exercise_2.py
import tracemalloc
from dataclasses import dataclass
from functools import cache
from typing import Final, Literal

type Symbol = Literal[".", "~", "#"]
type TileSpec = tuple[str, bool]

@dataclass(frozen=True)
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
def cached_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def uncached_tile(symbol: Symbol) -> Tile:
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
    cached_field = [[cached_tile(to_symbol(s))
                     for s in line]
                    for line in text.split()]
    _, cached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    uncached_field = [[uncached_tile(to_symbol(s))
                       for s in line]
                      for line in text.split()]
    _, uncached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ratio = round(uncached_peak / cached_peak, 1)
    print(size, "ratio uncached/cached:", ratio)
#: 50 ratio uncached/cached: 9.9
#: 100 ratio uncached/cached: 9.9
#: 200 ratio uncached/cached: 11.1
```

The ratio holds near ten at every size: roughly 10x at a 50x50 map,
a little over 11x at 200x200. Both peaks grow with the number of
cells, because both versions build the same nested list of references.
The two differ in what one cell costs. A cell in the cached field
costs one reference into a pool of three `Tile` objects, while a cell
in the uncached field costs a brand-new `Tile`, roughly ten times as
much memory. The flyweight's saving is therefore per cell: the
multiplier stays near ten, and the bytes saved grow with the map.

## 3. Removing `frozen=True` exposes the sharing bug

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

@dataclass  # No frozen=True
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

Setting `walkable = False` on the tile at `(0, 0)` changes `walkable`
for every other grass cell in the map too, because all four cells
share one `MutableTile` object. Only one grass tile exists in memory,
and every cell holds a reference to that one object. This test pins
down the bug:

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

@dataclass  # No frozen=True
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

Restoring `frozen=True` turns this same test into a demonstration of
the fix. `field[0][0].walkable = False` now raises a
`FrozenInstanceError` immediately, because a frozen dataclass rejects
assignment to every field. That refusal makes sharing one object
safe.

## 4. Modeling chess

```python
# exercise_4.py
from dataclasses import dataclass
from enum import Enum
from functools import cache

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

@dataclass(frozen=True)
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

`starting_position()` fills thirty-two squares with only twelve
distinct `Piece` objects: two colors times six kinds. Every white pawn
is the same object, and every other color-and-kind combination
collapses the same way. The board is a `dict` mapping squares to
references. That mapping keeps the extrinsic position separate from
the intrinsic color-and-kind that `@cache` shares.

Capturing leaves every `Piece` object alive. `board[dst] = ...`
replaces whatever reference sits at `dst` (the captured piece) with
the moving piece's reference. The captured piece's *flyweight* stays
in the cache. Twelve `Piece` objects still exist after captures clear
the whole board, because those flyweights represent "a white rook" in
the abstract rather than any particular rook on a square. Capturing
removes a board *position* and nothing more.

`promote()` swaps which flyweight a square points to, because a frozen
`Piece` cannot change its color or kind. `piece(current.color, kind)`
looks up (or builds) a different shared `Piece`, and the board points
at that one instead.

## 5. `interned_color.py`, rewritten on a weak pool

```python
# exercise_5.py
from dataclasses import dataclass
from weakref import WeakValueDictionary

type RGB = tuple[int, int, int]

@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

_pool: WeakValueDictionary[RGB, Color] = (
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
del palette, crimson_a, crimson_b
print(len(_pool))
#: 0
```

This listing is `weak_pool.py`'s exact shape applied to colors instead
of names: a factory function, `make_color()`, replacing the
`Color(...)` constructor call, and a `WeakValueDictionary` instead of
a plain `dict`. Because `make_color()` is a plain function rather than
an overridden `__new__()`, `Color` stays an ordinary frozen
`@dataclass`, and the decorator generates a real `__repr__()` and
`__eq__()` for it. `interned_color.py`'s `Color` defines no
`__init__()`, and that omission rules out `@dataclass`, so it inherits
`object`'s versions of both. Once `del` drops every reference to the
fifty-shade palette and both crimson names, nothing keeps those
`Color` objects alive, so the pool empties itself with no explicit
cleanup.

## 6. Constraining `interned_color.py`'s components

```python
# exercise_6.py
from typing import ClassVar

type RGB = tuple[int, int, int]

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
        cached = cls._pool.get(key)
        if cached is not None:
            return cached
        self = super().__new__(cls)
        self.red, self.green, self.blue = red, green, blue
        cls._pool[key] = self
        return self

try:
    Color(300, 0, 0)
except ValueError as e:
    print("caught:", e)
#: caught: red=300 out of range 0-255
```

```python
# test_ch35_out_of_range.py
from typing import ClassVar
import pytest

type RGB = tuple[int, int, int]

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
        cached = cls._pool.get(key)
        if cached is not None:
            return cached
        self = super().__new__(cls)
        self.red, self.green, self.blue = red, green, blue
        cls._pool[key] = self
        return self

def test_out_of_range_component_raises() -> None:
    with pytest.raises(ValueError):
        Color(256, 0, 0)
    with pytest.raises(ValueError):
        Color(0, -1, 0)
```

The check runs first in `__new__()`, before the pool lookup, so an
out-of-range component raises a `ValueError` before `__new__()` can
find a cached instance or build a new one. No invalid `Color` is ever
pooled or returned. That check is the same *parse, don't validate* move
[Data Classes as Types](../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes with `__post_init__()`. Here the class validates in `__new__()`
instead, because interning must intercept construction.

## 7. `tile_map.py` rebuilt on the enum

```python
# exercise_7.py
from enum import Enum

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
try:
    parse_map("?")
except ValueError as e:
    print(type(e).__name__, e)
#: ValueError '?' is not a valid Tile
```

`SPECS`, `tile()` and `to_symbol()` all disappear. The member tuples
are the spec table, and `Tile(s)` is the pool lookup. The
value-to-member table the metaclass builds performs the runtime
membership check `to_symbol()` did by hand.

The `Literal` version catches a character `SPECS` does not cover, and
the enum catches the same class of mistake, since a symbol with no
member has no way into the map. The enum adds one thing: the *set
itself* is a single declaration rather than two kept in step. The
`Literal` version could drift, with `Symbol` and `SPECS` disagreeing,
and only the annotation tying the two together catches that drift. The
enum leaves nothing to disagree with.

The enum gives up the moment of failure. `to_symbol()` raises a
`KeyError` at a named boundary the chapter can point at. `Tile("?")`
raises a `ValueError` from deep inside `parse_map()`'s comprehension.
If the boundary matters, keep a `to_tile()` wrapper that catches the
`ValueError` and re-raises it with the offending line and column.

## 8. Four threads on a cold key

```python
# exercise_8.py
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from typing import Final

@dataclass(frozen=True)
class Tile:
    symbol: str
    name: str
    walkable: bool

SPECS: Final[dict[str, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "^": ("hill", True),
    "*": ("sand", True),
}

@cache
def tile(symbol: str) -> Tile:
    # Widen the window between miss and store
    time.sleep(0.1)
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def gather(
    factory: Callable[[str], Tile], symbol: str
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

EAGER: Final[dict[str, Tile]] = {
    s: Tile(s, *spec) for s, spec in SPECS.items()}

def eager_tile(symbol: str) -> Tile:
    return EAGER[symbol]

print(len({id(t) for t in gather(eager_tile, "*")}))
#: 1

guard = threading.Lock()

def locked_tile(symbol: str) -> Tile:
    with guard:
        return tile(symbol)

print(len({id(t) for t in gather(locked_tile, "~")}))
#: 1
```

Each thread builds its own `Tile` and keeps it, so `is` fails between
all four results. `@cache` looks up the key, misses, calls the
function, and stores the result. No lock spans those steps, so four
threads that all miss on the same cold key all run the body. The last
store wins the cache, and every later caller gets that one object,
while the three losing threads hold objects nothing else sees.

Nothing here is a `@cache` defect. A cache that held a lock across the
call would serialize every miss in the program, a worse default than
occasionally building a value twice. For an ordinary memoized
computation, a duplicate build costs time but not correctness.
Flyweight raises the stakes, because its whole point is that
`tile("^") is tile("^")`.

The eager fix builds every value before any thread exists, so no miss
remains to race on. It is the better answer whenever the whole value
set fits in one small table, the same condition that makes an `Enum`
work. It costs nothing at runtime.

The lock fix handles an unbounded value set, and its cost is real.
Every lookup now serializes, including the hits, which are the
overwhelming majority once the pool is warm. If that matters, lock
only on the miss path with a hand-written pool, checking the key again
inside the lock, since another thread may have filled that entry while
this one waited.
