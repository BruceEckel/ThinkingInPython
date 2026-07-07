# Flyweight: Solutions

## 1. Door and tree kinds, plus `walkable_neighbors()`

```python
# exercise_1.py
from dataclasses import dataclass
from functools import cache
from typing import Final, Literal, cast

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
    return cast(Symbol, char)

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
cells = [t for row in field for t in row]
print(len(cells), len({id(t) for t in cells}))
#: 24 5
```

Adding two symbols to `SPECS` (and to the `Symbol` literal so the
checker still catches a mismatch between the two) is the whole change
needed to support door and tree tiles; `tile()` and `parse_map()`
never change. Twenty-four cells still collapse to only five distinct
objects, one per kind (`grass`, `water`, `rock`, `door`, `tree`),
however large the map grows, because `@cache` keys on the symbol
alone.

## 2. `tracemalloc`, cached vs. uncached `tile()`

```python
# exercise_2.py
import tracemalloc
from dataclasses import dataclass
from functools import cache
from typing import Final, Literal, cast

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
    return cast(Symbol, char)

def make_map(size: int) -> str:
    row = "".join(".~#"[i % 3] for i in range(size))
    return "\n".join(row for _ in range(size))

for size in (50, 100, 200):
    text = make_map(size)
    tracemalloc.start()
    cached_field = [[cached_tile(to_symbol(s)) for s in line]
                    for line in text.split()]
    _, cached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    uncached_field = [[uncached_tile(to_symbol(s)) for s in line]
                       for line in text.split()]
    _, uncached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ratio = round(uncached_peak / cached_peak, 1)
    print(size, "ratio uncached/cached:", ratio)
#: 50 ratio uncached/cached: 9.8
#: 100 ratio uncached/cached: 9.9
#: 200 ratio uncached/cached: 11.1
```

The ratio grows as the map grows: from roughly 10x at a 50x50 map to
over 11x at 200x200. The cached version's peak memory stays flat at
essentially three `Tile` objects no matter the map size, while the
uncached version allocates a brand-new `Tile` for every single cell,
so its memory grows with the number of cells (quadratically with map
side length). The flyweight's advantage is not a fixed multiplier; it
widens as the map grows, because the cached cost is constant and the
uncached cost is not.

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

Setting `walkable = False` on the tile at `(0, 0)` changes it for
every other grass cell in the map too, because all four cells share
one `MutableTile` object; there is only one grass tile in memory, and
every cell just holds a reference to it. A test that pins down the bug:

```python
# test_ch36_mutation_leak.py
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

def test_mutation_without_frozen_leaks_across_cells() -> None:
    field = [[mutable_tile(s) for s in line]
             for line in "..\n..".split()]
    field[0][0].walkable = False
    assert field[1][1].walkable is False  # Bug: cell leaked
```

Restoring `frozen=True` turns this same test into a demonstration of
the fix: `field[0][0].walkable = False` would instead raise
`FrozenInstanceError` immediately, since a frozen `Tile` cannot be
mutated at all, which is exactly what makes sharing it safe.

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
    back_rank = [Kind.ROOK, Kind.KNIGHT, Kind.BISHOP, Kind.QUEEN,
                 Kind.KING, Kind.BISHOP, Kind.KNIGHT, Kind.ROOK]
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
    board[dst] = board.pop(src)  # Overwrites dst's old occupant

def promote(
    board: dict[Square, Piece], square: Square, kind: Kind
) -> None:
    current = board[square]
    board[square] = piece(current.color, kind)  # A shared Piece

board = starting_position()
print(len(board), len({id(p) for p in board.values()}))
#: 32 12
move(board, ("e", 2), ("e", 4))
print(("e", 2) in board, board[("e", 4)].kind)
#: False Kind.PAWN
promote(board, ("e", 4), Kind.QUEEN)
print(board[("e", 4)])
#: Piece(color=<Color.WHITE: 'white'>, kind=<Kind.QUEEN: 'Q'>)
```

Thirty-two occupied squares, but only twelve distinct `Piece` objects:
two colors times six kinds. Every white pawn is the very same object,
and likewise for every other color-and-kind combination; the board is
just a `dict` mapping squares to references, the extrinsic position
kept separate from the intrinsic color-and-kind that `@cache` shares.

Capturing needs no `Piece` object destroyed at all. `board[dst] = ...`
simply replaces whatever reference was at `dst` (the captured piece)
with the moving piece's reference. The captured piece's *flyweight* is
untouched. Twelve `Piece` objects still exist even after every piece
on the board has been captured, because those flyweights represent "a
white rook" in the abstract, not any particular rook on the board;
capturing only removes a board *position*.

Promotion swaps which flyweight a square points to, since a `Piece`
cannot change color or kind (it is frozen): `piece(current.color,
kind)` looks up (or builds) a different, shared `Piece`, and the board
simply points at it instead.

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

_pool: WeakValueDictionary[RGB, Color] = WeakValueDictionary()

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

This is `weak_pool.py`'s exact shape applied to colors instead of
symbols: a factory function, `make_color()`, replacing the
`Color(...)` constructor call, and a `WeakValueDictionary` instead of
a plain `dict`. Being a plain function rather than an overridden
`__new__()` means `Color` can stay an ordinary frozen `@dataclass`,
with a real `__repr__()` and `__eq__()` generated for free, unlike
`interned_color.py`'s `Color`, which loses both by skipping
`__init__()`. Once every reference to the fifty-shade palette and both
crimson names is gone, nothing keeps those `Color` objects alive, and
the pool empties itself with no explicit cleanup.

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

    def __new__(cls, red: int, green: int, blue: int) -> Color:
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
# test_ch36_out_of_range.py
from typing import ClassVar
import pytest

type RGB = tuple[int, int, int]

class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int, blue: int) -> Color:
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
out-of-range component is rejected before either finding a cached
instance or building a new one; no invalid `Color` is ever pooled or
returned. This is the same *parse, don't validate* move
[Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes with `__post_init__()`, applied to a class that validates in
`__new__()` instead because it needs to intercept construction for
interning.
