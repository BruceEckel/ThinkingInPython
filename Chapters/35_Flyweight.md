# Flyweight

Some programs need enormous numbers of fine-grained objects:
the characters in a document, the tiles in a game map,
the strings in a compiler's symbol table.
The *Flyweight* pattern supports them by sharing.
Instead of many objects,
you keep one object per distinct value and reference it many times.

Two ideas make sharing work.

First, split each object's state in two.
*Intrinsic state* belongs to the value and is identical across every use,
so it can live in the shared object.
*Extrinsic state* varies per use, so it must live outside,
supplied by the context.
Second, route construction through a factory that returns the already-existing instance for a given value.

Handing out one object under many names is only safe when nobody can change it,
so a flyweight must be immutable (see [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)).

## Python Uses Flyweights

CPython flyweights its most common values.

It creates small integers once and shares them:

```python
# small_integer_flyweights.py
low, low2 = int("256"), int("256")
high, high2 = int("100000"), int("100000")
print(low is low2, high is high2)
#: True False
```

Both `int("256")` calls return the same cached object,
while each `int("100000")` call builds a fresh one.

String *interning* keeps one copy of identifier-like strings.
`sys.intern()` gives you the string pool directly:

```python
# string_interning.py
from sys import intern

joined = "".join(["fly", "weight"])
joined2 = "".join(["fly", "weight"])
print(joined == joined2, joined is joined2)
#: True False
print(intern(joined) is intern(joined2))
#: True
```

The two `join()` calls build equal but distinct strings,
and `intern()` maps both to one shared copy.
Interned strings make comparison cheap.
Equal means identical, so `==` collapses to a pointer check.

The small-integer cache and string interning are CPython implementation details,
not language guarantees.
Do not write code that depends on them, but notice the technique.

## Intrinsic and Extrinsic State

A map can hold millions of cells, but only a handful of tile kinds.
Here, we'll limit it to grass, water, and rock.

The tile's symbol, name, and walkability are intrinsic,
so they go in a frozen data class.

The tile's position is extrinsic.
It is the cell's coordinates in the grid, so the `Tile` object never stores it.

The factory pairs `functools.cache` with a constructor function,
the same building block behind [Singleton](24_Singleton.md#when-you-want-a-class-cache-the-instance)'s cached factory.
There the function took no arguments,
so caching produced one shared instance overall.
Here `tile()` takes a symbol,
so caching produces one shared instance per distinct symbol instead.

![Two water cells at opposite corners of the grid are the same object; the whole 24-cell map reduces to 3 shared Tile instances](_images/flyweight_tiles)

```python
# tile_map.py
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

if __name__ == "__main__":
    field = parse_map("""
        ..~~..
        ..~~.#
        ......
        ##..~~
    """)
    cells = [t for row in field for t in row]
    print(len(cells), len({id(t) for t in cells}))
    print(field[0][2] is field[3][5])
#: 24 3
#: True
```

Twenty-four cells, three objects.
The grid can grow to any size and the object count stays at the number of tile kinds,
because `@cache` returns the same `Tile` for the same symbol every time.
A cell's position never needs storing.
Asking "is the cell at row 1, column 5 walkable?" is `field[1][5].walkable`,
with the coordinates supplied by the asker.
That is the intrinsic/extrinsic split doing its work.

`Symbol` names the closed set of valid map characters,
so `Tile.symbol` and `SPECS` can only hold one of them.
Add a kind to `SPECS` without adding it to `Symbol`, or the reverse,
and the checker rejects the mismatch.
`tile()` trusts its argument is already a `Symbol`,
so the untrusted boundary is `to_symbol()`,
the one place raw text meets the checked type.
It checks membership in `SPECS` at runtime,
then calls `cast()` to tell the checker what that check just proved.
`cast()` changes nothing at runtime.
It exists only for the checker and the reader (see [Static Typing](08_Static_Typing.md#typing-decorators-and-directives)),
so use it only where, as here,
you have already verified what the checker cannot:
that `char` is one of the three symbols.

```python
# test_tile_map.py
import pytest
from tile_map import parse_map, tile, to_symbol

def test_same_symbol_same_object() -> None:
    assert tile(".") is tile(".")
    assert tile(".") is not tile("#")

def test_map_shares_tiles() -> None:
    field = parse_map("..\n~~")
    assert field[0][0] is field[0][1]
    assert field[1][0] is field[1][1]
    assert not field[1][0].walkable

def test_unknown_symbol_raises() -> None:
    with pytest.raises(KeyError):
        to_symbol("?")
```

Because `Tile` is frozen, sharing is invisible to clients.
Nothing they can do to one cell's tile affects another,
because nothing they can do affects the tile.

Remove `frozen=True` and the pattern fails.
Mutate the grass tile in one cell and every grass cell in the map changes.

## Interning in the Constructor

A factory function like `tile()` is an honest extra name.
Its different syntax warns callers that something unusual is happening.
If you want callers to keep writing `Color(...)`,
hide the pool inside `__new__` instead.
This is the same maneuver the [Singleton](24_Singleton.md#the-classic-implementations) chapter uses.
Here the cache is keyed by the constructor arguments instead of a single fixed key:

```python
# interned_color.py
from typing import ClassVar

type RGB = tuple[int, int, int]

class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int, blue: int) -> Color:
        key: RGB = (red, green, blue)
        cached: Color | None = cls._pool.get(key)
        if cached is not None:
            return cached
        self = super().__new__(cls)
        self.red, self.green, self.blue = red, green, blue
        cls._pool[key] = self
        return self

if __name__ == "__main__":
    crimson = Color(220, 20, 60)
    print(crimson is Color(220, 20, 60))
    print(len(Color._pool))
#: True
#: 1
```

The construction syntax is unchanged,
and callers cannot tell they received a shared object (this is how CPython's small-integer cache does it).
The cost is bookkeeping by hand.
Python calls `__init__()` on whatever `__new__()` returns,
so an `__init__()` here would re-run on the cached instance at every construction.
Skipping `__init__()` means skipping `@dataclass` too,
since a dataclass only generates `__init__()`.
`Color` loses the `__repr__()` and `__eq__()` that `Tile` gets,
so printing a `Color` falls back to the default `object.__repr__()`.
A `defaultdict` cannot replace `_pool` either,
because building a `Color` needs the three color components,
not just the key that names them.
Unless you need the constructor syntax,
the `@cache` factory from `tile_map.py` does the same job with less machinery.

## A Pool That Does Not Leak

Both pools so far hold their objects forever.
`@cache` keeps strong references to every argument and result,
and `Color._pool` never shrinks.
For tile kinds and colors that is fine, since the universe of values is small.
When the universe is unbounded, such as symbols in a long-running parser,
the pool becomes a memory leak.
`weakref.WeakValueDictionary` fixes this.
It holds its values weakly,
so an entry disappears as soon as no one else uses the object:

```python
# weak_pool.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

@dataclass(frozen=True)
class Symbol:
    name: str

_pool: Final[WeakValueDictionary[str, Symbol]] = (
    WeakValueDictionary())

def symbol(name: str) -> Symbol:
    found: Symbol | None = _pool.get(name)
    if found is None:
        found = Symbol(name)
        _pool[name] = found
    return found

if __name__ == "__main__":
    alpha = symbol("alpha")
    alias = symbol("alpha")
    print(alpha is alias, len(_pool))
    del alpha, alias
    print(len(_pool))
#: True 1
#: 0
```

While any reference to the `Symbol` survives,
every call to `symbol("alpha")` returns that same object.
When the last reference dies,
CPython's reference counting frees the object and the pool entry evaporates with it.
The pool guarantees sharing without extending lifetimes,
which is the same design as `sys.intern()`.
If you want bounded memory with fixed construction cost instead,
`functools.lru_cache(maxsize=n)` gives the factory an eviction policy,
at the price of keeping the most recent `n` alive.

```python
# test_weak_pool.py
from weak_pool import _pool, symbol

def test_symbols_are_shared() -> None:
    keep = symbol("x")
    assert symbol("x") is keep
    assert symbol("y") is not keep

def test_pool_releases_unused() -> None:
    temp = symbol("temp")
    assert "temp" in _pool
    del temp
    assert "temp" not in _pool
```

## A Fixed Set: Enum

When you know the full set of shared values as you write the program,
you do not need a pool at runtime.
An [Enum](12_Data_Classes_as_Types.md#enums-are-types-too) is a flyweight pool the language maintains for you.
Python constructs each member once, at class creation,
and any reference produces that one object.

```python
# tile_enum.py
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

if __name__ == "__main__":
    print(Tile.GRASS is Tile["GRASS"] is Tile("."))
    print(Tile.WATER.value, Tile.WATER.walkable)
    print([t.value for t in Tile])
#: True
#: ~ False
#: ['.', '~', '#']
```

`walkable` is a bare annotation, not a `ClassVar`.
It declares a per-member attribute, the same role a dataclass field plays,
except `__new__()` assigns it by hand instead of a generated `__init__()`.
`__new__()` runs before any member becomes visible,
so there is no window where `walkable` is unset.
It needs no default or sentinel.

Each member's tuple goes to `__new__()`,
which stores the walkability and assigns `_value_`,
so the member's value is its map symbol rather than the tuple.
The customization must happen in `__new__()`.
The lookup table behind `Tile(".")` keys on the value `__new__()` establishes,
so setting `_value_` later, in `__init__()`,
would leave that table keyed by the tuples.
With `_value_` set in `__new__()`, `Tile(".")` is a lookup.

`object.__new__(cls)` builds a bare instance directly,
skipping `Tile.__new__()` so the call does not recurse.
`_value_` is not an ordinary attribute name.
Enum's metaclass reads it to build the `Tile(".")` lookup table and the member's `repr()`,
so it keeps that exact name rather than something like `_symbol_`.

Name, symbol, and attribute access all land on the same shared member.
The enum version also brings iteration, exhaustive `match`,
and protection against inventing a tile kind that does not exist.
The constraint is less flexibility.
`tile()` could load `SPECS` from a file, while `Tile.GRASS` is source code.
The table-driven state machine in [State Machines](31_State_Machines.md#table-driven-state-machine) exploits the same property,
using members as shared, comparable states.

## Flyweights in the Wild

The pattern is easy to spot once you know its shape.
Compilers and interpreters intern identifiers so that scope lookups compare pointers instead of characters.
Column stores such as Pandas and Polars offer categorical types.
A column of a million country names stores small integer codes into a pool of distinct strings.
Text systems share one glyph object per character and font,
with each occurrence supplying its own position.
In every case the benefit is the same:
memory proportional to the number of distinct values, not the number of uses,
and equality checks that collapse to identity.

## Exercises

1.  Add door (`+`, walkable) and tree (`T`, not walkable) kinds to `tile_map.py`.
    Extend `Symbol` and `SPECS` to match,
    then write `walkable_neighbors(field, row, col)` returning the count of adjacent walkable cells.
    Confirm the tile pool size still equals the number of kinds,
    however large the map.
2.  Use `tracemalloc` to compare `parse_map()` on a large map against a version whose `tile()` has no `@cache`.
    How does the ratio change as the map grows?
3.  Remove `frozen=True` from `Tile` and set `field[0][0].walkable = False` on a parsed map.
    Write a test that exposes the resulting bug, then restore `frozen=True`.
4.  Model chess: a frozen `Piece` (color, kind) and a board that is a `dict` mapping squares to pieces.
    A full opening position holds thirty-two piece references.
    How many `Piece` objects exist?
    How do you capture and promote?
5.  Rewrite `interned_color.py` to use the weak pool technique from `weak_pool.py`,
    and show that building and dropping a palette of colors leaves the pool empty.
6.  Constrain `red`, `green`, and `blue` to `0`-`255` in `interned_color.py`.
    Raise `ValueError` from `__new__()` for an out-of-range component,
    and write a test for it.
