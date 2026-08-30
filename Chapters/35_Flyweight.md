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
where the context supplies it.
Second, route construction through a factory that returns the existing instance for a given value.

Handing out one object under many names is safe only when nobody can change it,
so a flyweight must be immutable
(see [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)).

## Python Uses Flyweights

CPython creates small integers once and shares them:

```python
# small_integer_flyweights.py
low, low2 = int("256"), int("256")
high, high2 = int("100000"), int("100000")
print(low is low2, high is high2)
#: True False
```

Both `int("256")` calls return the same cached object,
while each `int("100000")` call builds a fresh one.
The cache covers a fixed range of values chosen at CPython build time.
The number usually quoted is `-5` through `256`, but that is not a guarantee:
the build used here caches up to 1024,
which is why the uncached example is `100000` and not `257`.
Calling `int("...")` on a string, not a literal, matters here.
If you write the literals directly, `low, low2 = 256, 256`,
the demonstration silently breaks:
the compiler pools equal constants within a code object,
so even `100000 is 100000` prints `True`,
sharing that comes from constant folding rather than from the integer cache.
Parsing the value out of a string at runtime defeats the compiler's pooling and leaves only the cache to explain any sharing.
(Python warns about `is` on a literal because the compiler makes the answer misleading.)

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
Here, the handful is grass, water, and rock.

The tile's symbol, name, and walkability are intrinsic,
so they go in a frozen data class.

The tile's position is extrinsic.
It is the cell's coordinates in the grid, so the `Tile` object never stores it.

The factory pairs `functools.cache` with a constructor function,
the same building block behind [Singleton](24_Singleton.md#when-you-want-a-class-cache-the-instance)'s cached factory.
There the function takes no arguments,
so caching produces one shared instance overall.
Here `tile()` takes a symbol,
so caching produces one shared instance per distinct symbol instead.

![Two water cells at opposite corners of the grid are the same object; the whole 24-cell map reduces to 3 shared Tile instances](_images/flyweight_tiles)

```python
# tile_map.py
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

if __name__ == "__main__":
    field = parse_map("""
        ..~~..
        ..~~.#
        ......
        ##..~~
    """)
    cells = [*row for row in field]
    print(len(cells), len({id(t) for t in cells}))
    print(field[0][2] is field[3][5])
#: 24 3
#: True
```

Twenty-four cells, three objects.
`[*row for row in field]` flattens the grid into one list of cells,
the comprehension unpacking from [Comprehensions](16_Comprehensions.md#unpacking-in-comprehensions).
Counting `id(t)` rather than `len(set(cells))` is deliberate.
`Tile` is a frozen data class,
so its generated `__eq__()` compares field values,
and a set of cells would collapse to three with or without sharing.
Only identity proves sharing.
The grid can grow to any size and the object count stays at the number of tile kinds,
because `@cache` returns the same `Tile` for the same symbol every time.
A cell's position never needs storing.
Asking "is the cell at row 1, column 5 walkable?" is `field[1][5].walkable`,
with the asker supplying the coordinates.
The listing shows the object count.
Exercise 2 measures the memory behind it.

### Typing the Symbol Set

`Symbol` names the closed set of valid map characters,
so `Tile.symbol` and `SPECS` can hold only one of them.
If you add a kind to `SPECS` without adding it to `Symbol`, or the reverse,
the type checker rejects the mismatch.
`tile()` trusts its argument is already a `Symbol`,
so the untrusted boundary is `to_symbol()`,
the one place raw text meets the checked type.
It checks membership in `SPECS` at runtime and raises a `KeyError` if the character is not there.
The type checker reads that guard.
`SPECS` has key type `Symbol`,
so reaching the line below means `char not in SPECS` was false,
which narrows `char` to `Symbol`,
and `return char` satisfies the declared return type with nothing added.
The narrowing proves what a `cast()` would assert
(see [Static Typing](08_Static_Typing.md#typing-decorators-and-directives)).
Prefer a guard the type checker can read.
Keep `cast()` for the cases where no guard exists,
because the type checker believes a `cast()` rather than verifying it.

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

Freezing `Tile` hides the sharing from clients.
Nothing they can do to one cell's tile affects another,
because nothing they can do affects the tile.

If you remove `frozen=True`, the pattern fails.
Mutating the grass tile in one cell changes every grass cell in the map.

`frozen=True` must hold all the way down.
It blocks assignment to a field, not mutation inside one,
so a `Tile` holding a `list` would leak that list to every cell that shares the tile
(the shallow-freezing trap in [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)).
Every field here is immutable, which makes the sharing safe.

## Interning in the Constructor

A factory function like `tile()` has a visibly different name and call syntax,
which warns callers of something unusual.
If you want callers to keep writing `Color(...)`,
hide the pool inside `__new__()` instead.
This is the same maneuver the [Singleton](24_Singleton.md#the-classic-implementations)
chapter uses.
Here the cache keys on the constructor arguments instead of a single fixed key.
A pool of singletons keyed this way is sometimes called *Multiton*:

```python
# interned_color.py
from typing import ClassVar

type RGB = tuple[int, int, int]

class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int,
                blue: int) -> Color:
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

The construction syntax stays the same,
and callers cannot tell they received a shared object
(this is how CPython's small-integer cache works).
The cost is bookkeeping by hand.
When `__new__()` returns an instance of the class, as it does here,
Python calls `__init__()` on it,
so an `__init__()` re-runs on the cached instance at every construction.
This class therefore defines no `__init__()`.
The call still reaches `object.__init__()`,
which accepts and ignores the three arguments because this class overrides `__new__()` and not `__init__()`.
That rules out `@dataclass`,
whose generated `__init__()` reintroduces the re-run.
The damage is invisible at first,
since re-assigning the same components changes nothing.
It appears the moment a field has a `default_factory` or `__post_init__()` has a side effect:
both run again on an object that was already finished.
`Color` loses the `__repr__()` and `__eq__()` that `Tile` gets,
so printing a `Color` falls back to the default `object.__repr__()`.
The missing `__eq__()` costs less than it appears:
for a perfectly interned type, equal values are the same object,
so the default identity comparison answers correctly.
`@dataclass(init=False)` could restore those two generated methods, at a price:
the generated `__eq__()` sets `__hash__` to `None` unless you also pass `frozen=True`,
and `frozen=True` then forces `object.__setattr__()` for the by-hand assignment in `__new__()`.
A `defaultdict` cannot replace `_pool` either:
it calls its `default_factory` with no arguments,
so the factory cannot see the components the missing `Color` needs.

`_pool` keys on the components alone, and every subclass inherits it,
so no one can subclass `Color` safely.
A subclass would collide with it,
receiving whichever object asked for those components first.
Key the pool by `(cls, red, green, blue)` if you need to subclass.

The two forms are not quite interchangeable.
`tile()` interns only the calls that go through it,
so `Tile("~", "water", False)` still builds a separate object,
equal to the pooled water tile but not the same one.
`Color(...)` has no such gap, because every construction goes through the pool.
The difference matters when you want to trust `is` instead of `==`.
Unless you need the constructor syntax or that guarantee,
the `@cache` factory from `tile_map.py` does the same job with less machinery.

One more property carries over from [Singleton](24_Singleton.md#when-you-want-a-class-cache-the-instance)'s cached factory:
every lazy check-then-insert pool races under threads.
Two threads asking for the same new color can each build "the" shared object,
one wins the pool, and identity between their two results fails.
`@cache` is not exempt.
Being C code in the standard library invites the assumption that it is atomic,
but the lookup, the call to your function,
and the store are three separate steps.
Threads that all miss on the same key each run the function and each keep their own result.
When flyweights meet threads,
populate the pool eagerly or guard the insert with a lock.

## A Pool That Does Not Leak

Both pools so far hold their objects forever.
`@cache` keeps strong references to every argument and result,
and `Color._pool` never shrinks.
For tile kinds and colors that is fine, since the universe of values is small.
When the universe grows without bound, such as symbols in a long-running parser,
the pool becomes a memory leak.
`weakref.WeakValueDictionary`,
the live-instance registry from [Cleanup](10_Cleanup.md#watching-objects-without-holding-them),
fixes this.
It holds its values weakly,
so an entry disappears as soon as no one else uses the object:

```python
# weak_pool.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

@dataclass(frozen=True)
class Name:
    text: str

_pool: Final[WeakValueDictionary[str, Name]] = (
    WeakValueDictionary())

def name(text: str) -> Name:
    found: Name | None = _pool.get(text)
    if found is None:
        found = Name(text)
        _pool[text] = found
    return found

if __name__ == "__main__":
    alpha = name("alpha")
    alias = name("alpha")
    print(alpha is alias, len(_pool))
    del alpha, alias
    print(len(_pool))
#: True 1
#: 0
```

While any reference to the `Name` survives,
every call to `name("alpha")` returns that same object.
When the last reference dies,
CPython's reference counting frees the object and the pool entry evaporates with it.
The pool guarantees sharing without extending lifetimes,
which is the same design as `sys.intern()`.
If you want a bounded pool instead,
`functools.lru_cache(maxsize=n)` gives the factory an eviction policy,
at the price of keeping the most recent `n` alive whether or not anyone uses them.
Eviction also weakens the sharing guarantee:
requesting an evicted value builds a fresh object,
equal to any surviving original but not the same one.
The weak pool cannot produce such a pair,
because its entry lives as long as anyone holds the object.

Flyweight cuts the number of objects, and `slots=True`
([Performance](18_Performance.md#slots)) cuts the size of each one,
so the two are worth combining once memory is the point.
They collide at one spot:
a slotted class has no `__weakref__` unless you also pass `weakref_slot=True`,
so slotting `Name` without it makes `_pool[text] = found` raise a `TypeError`.

```python
# test_weak_pool.py
from weak_pool import _pool, name

def test_names_are_shared() -> None:
    keep = name("x")
    assert name("x") is keep
    assert name("y") is not keep

def test_pool_releases_unused() -> None:
    temp = name("temp")
    assert "temp" in _pool
    del temp
    assert "temp" not in _pool
```

## A Fixed Set: Enum

When you know the full set of shared values as you write the program,
you need no pool at runtime.
An [Enum](12_Data_Classes_as_Types.md#enums-are-types-too)
is a flyweight pool the language maintains.
Python constructs each member once, at class creation,
and any reference produces that one object.
Here is `tile_map.py`'s `Tile` again, with the pool moved into the language:

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
so nothing can observe an unset `walkable`.
It needs no default or sentinel.

Each member's tuple goes to `__new__()`,
which stores the walkability and assigns `_value_`,
so the member's value is its map symbol rather than the tuple.
`__new__()`, not `__init__()`, must assign `_value_`.
The lookup table behind `Tile(".")` keys on the value `__new__()` establishes,
so setting `_value_` later, in `__init__()`,
leaves that table keyed by the tuples.
With `_value_` set in `__new__()`, `Tile(".")` is a lookup.

`object.__new__(cls)` builds a bare instance directly,
skipping `Tile.__new__()` so the call does not recurse.
`_value_` is not an ordinary attribute name.
Enum's metaclass reads it to build the `Tile(".")` lookup table and the member's `repr()`,
so `__new__()` must assign to that exact name rather than something like `_symbol_`.

Name, symbol, and attribute access all reach the same shared member.
The enum version also brings iteration, exhaustive `match`,
and protection against inventing a tile kind that does not exist.
The cost is flexibility.
`tile()` could load `SPECS` from a file, while `Tile.GRASS` is source code.
The table-driven state machine in [State Machines](31_State_Machines.md#table-driven-state-machine)
exploits the same property, using members as shared, comparable states.

## Which Pool Should You Use?

The chapter showed four mechanisms,
and the question that decides between them is how much you know about the set of values.
If you know it as you write the program,
use an `Enum` and let the language hold the pool.
If callers must keep writing `C(...)`,
intern in `__new__()` and pay the bookkeeping.
If the set grows without bound,
use a `WeakValueDictionary` so the pool cannot become a leak.
Otherwise use a `@cache` factory, which is the least machinery for the job.

## Flyweights in the Wild

Compilers and interpreters intern identifiers so that scope lookups compare pointers instead of characters.
Dataframe libraries such as Pandas and Polars offer categorical types.
A column of a million country names stores small integer codes that index into a pool of distinct strings.
Text systems share one glyph object per character and font,
with each occurrence supplying its own position.
In every case the benefit is the same:
memory proportional to the number of distinct values, not the number of uses,
and, for a type where every instance comes from the pool,
equality checks you can write as `is`.

## Exercises

1.  Add door (`+`, walkable) and tree (`T`, not walkable)
    kinds to `tile_map.py`.
    Extend `Symbol` and `SPECS` to match,
    then write `walkable_neighbors(field, row, col)` returning the count of adjacent walkable cells.
    Confirm the tile pool size still equals the number of kinds,
    however large the map.
2.  Use `tracemalloc` to compare `parse_map()` on a large map against a version whose `tile()` has no `@cache`.
    How does the ratio change as the map grows?
3.  Remove `frozen=True` from `Tile` and set `field[0][0].walkable = False` on a parsed map.
    Write a test that exposes the resulting bug, then restore `frozen=True`.
4.  Model chess: a frozen `Piece` (color, kind)
    and a board that is a `dict` mapping squares to pieces.
    A full opening position holds thirty-two piece references.
    How many `Piece` objects exist?
    How do you capture and promote?
5.  Rewrite `interned_color.py` to use the weak pool technique from `weak_pool.py`,
    and show that building and dropping a palette of colors leaves the pool empty.
6.  Constrain `red`, `green`, and `blue` to `0`-`255` in `interned_color.py`.
    Raise `ValueError` from `__new__()` for an out-of-range component,
    and write a test for it.
7.  Rewrite `tile_map.py` on top of `tile_enum.py`'s `Tile`,
    so `parse_map()` returns `list[list[Tile]]` of enum members and `to_symbol()` disappears.
    What does the type checker now catch that the `Literal` version caught,
    and what does it catch that the `Literal` version did not?
8.  Make `tile()`'s body slow,
    with a `time.sleep(0.05)` before it builds the `Tile`,
    and call it from four threads with the same, previously unseen symbol.
    How many `Tile` objects get built,
    and how many distinct objects do the four threads hold?
    Fix it two ways: populate the pool eagerly at import,
    and guard the factory with a `threading.Lock`.
