# Flyweight

> Thousands of objects carry the same few values.
> *Flyweight* keeps one object per value and shares it among every use.

The characters in a document, the tiles in a game map,
and the strings in a compiler's symbol table are fine-grained objects a program needs in enormous numbers,
and each has far fewer distinct values than uses.
Sharing replaces the many objects with one per distinct value,
referenced many times.

Two ideas make sharing work.

First, split each object's state in two.
*Intrinsic state* belongs to the value and is identical across every use,
so it can live in the shared object.
*Extrinsic state* varies per use, so it must live outside,
where the context supplies it.
Second, construct every object through a factory that returns the existing instance for a given value.

Sharing one object under many names is safe when the object stays the same for everyone,
so a flyweight must be [immutable](20_Patterns--Rethinking_Objects.md#the-immutability-solution).

## Python Uses Flyweights

CPython creates small integers once and shares them:

```python
# small_integer_flyweights.py
low, low2 = int("256"), int("256")
high, high2 = int("100000"), int("100000")
print(low is low2, high is high2)
#: True False
```

Both `int("256")` calls return the same cached object.
Each `int("100000")` call builds a fresh one.
The cache covers a set range of values chosen at CPython build time.
The range usually quoted is `-5` through `256`, but each build picks its own.
This build caches up to 1024,
so the example that needs a fresh object uses `100000` rather than `257`.

The listing parses each value from a string because the compiler pools equal constants within one code object.
With literals, `high, high2 = 100000, 100000` makes `high is high2` print `True`.
That sharing comes from the pooling, not from the integer cache.
Because the result of `is` depends on details like this pooling,
Python emits a `SyntaxWarning` when a literal is an operand of `is`,
as in `high is 100000`.
Parsing at runtime builds the integer after compilation,
so any sharing that remains comes from the cache.

String *interning* keeps one copy of each distinct string in a pool.
CPython interns identifier-like string constants automatically,
and `sys.intern()` adds any string to the pool,
or returns the pooled copy if one exists:

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
Interned strings compare in one step when they are equal,
because for them equal means identical,
and CPython's `==` on two strings checks identity before it compares characters.

The small-integer cache and string interning are CPython implementation details,
not language guarantees.
Do not write code that depends on them, but notice the technique.

## Intrinsic and Extrinsic State

A map can hold millions of cells, but only a handful of tile kinds.
Here, the handful is grass, water, and rock.
A first design gives each cell everything it knows about itself,
its position included:

```python
# unshared_cells.py
from record import record

@record
class Cell:
    symbol: str
    name: str
    walkable: bool
    row: int
    col: int

left = Cell(".", "grass", True, 0, 0)
right = Cell(".", "grass", True, 0, 1)
print(left == right)
#: False
```

The two grass cells differ in `col` alone,
and that difference makes them different values.
No factory can hand one object to both cells,
because no single object holds both positions.
Every cell in the grid is a distinct value,
so the map needs one object per cell.

Sharing starts by moving the position out.
The tile's symbol, name, and walkability are intrinsic.
Every grass cell agrees on them,
so they go in a [record](18_Techniques--Performance.md#record).
The tile's position is extrinsic.
It is the cell's coordinates in the grid, so it stays out of the `Tile` object,
and an operation that needs the position takes it as an argument.

The factory is `tile()`, a constructor function under `functools.cache`.
`@cache` stores each result under its argument,
so every call with the same symbol returns the object the first call built.

![Every water cell in the grid is the same Tile object](_images/flyweight_tiles)

```python
# tile_map.py
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

    def label(self, row: int, col: int) -> str:
        return f"{self.name} at ({row}, {col})"

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
    print(field[0][2].label(0, 2))
    print(field[3][5].label(3, 5))
#: 24 3
#: True
#: water at (0, 2)
#: water at (3, 5)
```

Twenty-four cells, three objects.
`@cache` returns the same `Tile` for the same symbol every time,
so the object count stays at the number of tile kinds however large the grid grows.
`[*row for row in field]` flattens the grid into one list of cells,
the [comprehension unpacking](16_Techniques--Comprehensions.md#unpacking-in-comprehensions).

The listing counts `id(t)` rather than `len(set(cells))` on purpose.
`Tile` is a record, so its generated `__eq__()` compares field values,
and a set of cells collapses to three with or without sharing.
Only identity proves sharing.
The listing shows the object count, not the memory behind it (see exercise 2).

The last two lines call `label()` on one object, the shared water tile,
and get two answers, because each caller passes in the position.
The shared object holds the state common to every use,
and an operation that depends on the use takes that use's context as an argument.
The grid holds each cell's position by where it stores the reference.
Asking "is the cell at row 1, column 5 walkable?" is `field[1][5].walkable`,
with the asker supplying the coordinates.

### Typing the Symbol Set

`Symbol` names the closed set of valid map characters,
so `Tile.symbol` and every key of `SPECS` is one of those characters.
If you add a kind to `SPECS` and leave `Symbol` as it is,
the type checker rejects the mismatch.
`tile()` declares its parameter a `Symbol`,
but `@cache` hides that declaration from callers.
The decorated `tile` is a `functools._lru_cache_wrapper`,
whose call accepts any hashable arguments,
so the type checker passes `tile("?")`,
and the mistake surfaces at runtime as a `KeyError` from `SPECS`.
The boundary is therefore `to_symbol()`,
the one function that takes a `str` and returns a `Symbol`.

`to_symbol()` guards on membership in `SPECS` at runtime and raises a `KeyError` for a character outside it.
The type checker narrows on the same guard.
`SPECS` has key type `Symbol`, so past the guard `char` is a `Symbol`,
and `return char` satisfies the declared return type as written.

The narrowing proves what a [`cast()`](08_Foundations--Static_Types.md#typing-decorators-and-directives)
asserts.
Prefer a guard that lets the type checker narrow.
Keep `cast()` for the cases where no guard exists,
because the type checker accepts a `cast()` without verifying it.

The test file confirms that:

- `tile()` returns one object per symbol and different objects for different symbols.
- A parsed map shares one `Tile` among the cells of each kind.
- `to_symbol()` raises a `KeyError` for a character outside `SPECS`.
- A direct `Tile(...)` call builds an object equal to the pooled tile and distinct from it.

```python
# test_tile_map.py
import pytest
from tile_map import Tile, parse_map, tile, to_symbol

def test_one_object_per_symbol() -> None:
    assert tile(".") is tile(".")
    assert tile(".") is not tile("#")

def test_map_shares_tiles() -> None:
    field = parse_map("..\n~~")
    assert field[0][0] is field[0][1]
    assert field[1][0] is field[1][1]
    assert field[0][0] is not field[1][0]

def test_to_symbol_raises_key_error() -> None:
    with pytest.raises(KeyError):
        to_symbol("?")

def test_direct_construction_bypasses_pool() -> None:
    bypassed = Tile("~", "water", False)
    assert bypassed == tile("~")
    assert bypassed is not tile("~")
```

### Freezing the Shared Tile

Freezing `Tile` makes sharing it safe.
A frozen tile keeps its values for its whole life,
so every cell that shares it reads the same values on every visit.

If you replace `@record` with `@dataclass`, the pattern fails.
Mutating the grass tile in one cell changes every grass cell in the map.

The freezing must hold all the way down.
A record blocks assignment to a field, not mutation inside one,
so a `Tile` holding a `list` hands the same mutable list to every cell that shares the tile,
the [shallow-freezing trap](20_Patterns--Rethinking_Objects.md#the-immutability-solution).
Every field here is immutable, so the sharing is safe.

## Sharing, Not Caching

`@cache` is a caching decorator, but `tile()` uses it for a different job.
A cache saves recomputation.
It returns a stored result instead of computing that result again,
and it can forget any entry while the program's results stay the same,
because the next call rebuilds an equal result at the cost of some time.
Building a `Tile` costs almost nothing, so `tile()` has little time to save.
What `tile()` gets from `@cache` is identity.
Every call for a symbol returns the same object.
A flyweight's factory exists for that sameness.
The figure follows `tile()` through the demo in `tile_map.py` and through `test_direct_construction_bypasses_pool()` in `test_tile_map.py`:

![](_images/flyweight_story)

Steps 1 and 2 show the sameness as two requests arriving at one object,
and step 3 shows why one object can serve every water cell.
The position travels with the call, not with the tile.
Step 4 marks where the guarantee ends.
A `Tile` built without `tile()` equals the shared tile but is a separate object.

The memory saving and every `is` comparison depend on that sameness,
so a factory that forgets an entry and builds a replacement breaks the pattern,
where a cache that forgets an entry runs slower and stays correct.

## Interning in the Constructor

A factory function like `tile()` has a visibly different name and call syntax,
so a caller can see that construction goes through something other than the class.
If you want callers to construct objects with an ordinary class call such as `Color(...)`,
hide the pool inside `__new__()` instead.
[*Singleton*](24_Patterns--Singleton.md#the-classic-implementations)
keeps its pool in `__new__()` the same way.
Here the pool keys on the constructor arguments instead of a single constant key.
A pool of singletons keyed this way is sometimes called *Multiton*.
A *Multiton*'s objects can be mutable, and a flyweight's cannot,
so `Color` is a record:

```python
# interned_color.py
from typing import ClassVar
from record import record

type RGB = tuple[int, int, int]

@record
class Color:
    _pool: ClassVar[dict[RGB, Color]] = {}
    red: int
    green: int
    blue: int

    def __new__(cls, red: int, green: int,
                blue: int) -> Color:
        key: RGB = (red, green, blue)
        if key not in cls._pool:
            cls._pool[key] = super().__new__(cls)
        return cls._pool[key]

if __name__ == "__main__":
    crimson = Color(220, 20, 60)
    print(crimson is Color(220, 20, 60))
    print(len(Color._pool))
#: True
#: 1
```

The construction syntax stays the same,
so a caller sees an ordinary constructor call and receives a shared object.
`int("256")` works the same way.
An ordinary constructor call returns a cached object.

You write the bookkeeping yourself, and `__new__()` brings a rule of its own.
When `__new__()` returns an instance of the class, as it does here,
Python calls `__init__()` on it,
so the record's generated `__init__()` runs at every construction,
including the ones that return a pooled instance.
`__new__()` therefore builds a bare instance and leaves the fields to `__init__()`.
On a pooled instance the re-run assigns the same three components again,
through the `object.__setattr__()` calls a frozen record's `__init__()` makes,
so the object stays as it was.
Once a field has a `default_factory` or `__post_init__()` has a side effect,
the re-run repeats that factory call or that side effect on a finished object.

Every caller that asks for the same components receives the same `Color`,
so a caller that set `crimson.red` would change every crimson in the program.
The record's frozen fields reject that assignment,
and that rejection makes sharing safe here for the reason it is safe for `Tile`.
The record also generates `__repr__()`, `__eq__()`, and `__hash__()`,
so a `Color` prints its components and works as a dict key.

A `defaultdict` calls its `default_factory` with no arguments,
and `super().__new__(cls)` needs the class that asked,
so `_pool` stays a plain dict with an explicit membership test.

`_pool` keys on the components alone, and every subclass shares the one dict,
so the first request for a set of components builds the object and every later one receives it,
whether `Color` or a subclass asks.
Key the pool by `(cls, red, green, blue)` if you need to subclass.

The factory `tile()` and the interning `Color` differ in one guarantee.
`tile()` interns the calls that go through it,
and a direct `Tile("~", "water", False)` bypasses it,
building a second object equal to the pooled water tile.
Every `Color(...)` call looks in the pool first,
so two `Color`s with the same components are the same object and `is` answers what `==` would.
The bookkeeping exists for that guarantee, or for the constructor syntax.
When you need neither,
the `@cache` factory from `tile_map.py` does the same job.

One more property carries over from [*Singleton*](24_Patterns--Singleton.md#the-first-call-race)'s cached factory.
Every lazy check-then-insert pool races under threads.
Two threads asking for the same new color can each build "the" shared object.
The second store overwrites the first,
and the two threads can end up holding distinct objects.
`interned_color.py` adds a second hazard.
`__new__()` pools the object before `__init__()` fills in its fields,
so another thread can receive a `Color` that has no components yet.
`@cache` races the same way.
Its C implementation runs the lookup, the call to your function,
and the store as three separate steps,
so threads that all miss on the same key each run the function and each keep their own result.
When more than one thread uses a pool,
populate the pool eagerly or guard the insert with a lock.

## A Pool That Does Not Leak

Both pools so far hold their objects forever.
`@cache` keeps strong references to every argument and result,
and `Color._pool` grows with every new color.
A map has a handful of tile kinds and a program usually draws from a small palette,
so holding them forever costs little.
When the set of values keeps growing, such as symbols in a long-running parser,
the pool becomes a memory leak.
`weakref.WeakValueDictionary`,
the [live-instance registry](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
fixes the leak.
It holds its values weakly,
so it removes an entry the moment that value's last other reference goes away:

```python
# weak_pool.py
from dataclasses import dataclass
from typing import Final
from weakref import WeakValueDictionary

@dataclass(frozen=True, slots=True, weakref_slot=True)
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
When the last reference goes away,
CPython's reference counting frees the object,
and the weak reference's callback removes the pool entry.
The pool guarantees sharing and lets each object's other references decide its lifetime,
the same design as `sys.intern()`.

*Flyweight* cuts the number of objects,
and [`slots=True`](18_Techniques--Performance.md#slots)
cuts the size of each one,
so the two are worth combining once memory is the point.
`Tile` combines them by being a record.

The combination has one catch.
A weak reference needs a `__weakref__` slot,
and a slotted class gets one only by declaring it, so with `slots=True` alone,
`_pool[text] = found` raises a `TypeError`.
`weakref_slot=True` adds that one slot and no `__dict__`.
`record()` does not pass `weakref_slot` through,
so `Name` writes the `dataclass` call in full.

`functools.lru_cache(maxsize=n)` bounds a pool a different way.
Once it holds `n` entries, it evicts the least recently used one.
That eviction turns the factory back into a cache.
Requesting an evicted value builds a fresh object,
equal to any surviving original and distinct from it,
so two uses of one value can hold two objects,
and an `is` comparison between them answers `False`.
Use `lru_cache` where a stored result saves recomputation,
not as a flyweight factory.
The weak pool avoids that trade.
Its entry lives exactly as long as something references the object,
so every request during that life returns the one object.

The tests confirm that `name()` returns the live `Name` for a repeated text and a different object for a different text,
and that the pool removes an entry once the last reference to its `Name` goes away:

```python
# test_weak_pool.py
from weak_pool import _pool, name

def test_names_are_shared() -> None:
    keep = name("x")
    assert name("x") is keep
    assert name("y") is not keep

def test_pool_removes_unreferenced() -> None:
    temp = name("temp")
    assert "temp" in _pool
    del temp
    assert "temp" not in _pool
```

## A Known Set: Enum

When you know the full set of shared values as you write the program,
you need no pool at runtime.
An [Enum](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too)
is a flyweight pool the language maintains.
Python constructs each member once, at class creation,
and any reference produces that one object.
Here is `tile_map.py`'s `Tile` recast as an enum,
with the pool moved into the language and the member name replacing the `name` field:

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
except that `__new__()` assigns it by hand where a generated `__init__()` would.
`__new__()` runs during class creation,
before the `class` statement binds the name `Tile`,
so every member has its `walkable` by the time any code can read it.
The bare annotation is enough.

Each member's tuple goes to `__new__()`,
which stores the walkability and assigns `_value_`,
so the member's value is its map symbol rather than the tuple.
`__new__()`, not `__init__()`, must assign `_value_`.
Enum reads `_value_` as soon as `__new__()` returns,
so an `__init__()` that assigns `_value_` later comes too late,
and the lookup table behind `Tile(".")` stays keyed by the tuples.
With `_value_` set in `__new__()`, `Tile(".")` is a lookup.

`object.__new__(cls)` builds a bare instance,
skipping `Tile.__new__()` so the call does not recurse.
`_value_` is a name Enum's metaclass reads,
to build the `Tile(".")` lookup table and the member's `repr()`,
so `__new__()` must assign to that exact name rather than a name of its own such as `_symbol_`.

Name, symbol, and attribute access all reach the same shared member.
The enum version also brings iteration, exhaustive `match`,
and a closed set of members.
`Tile("?")` raises a `ValueError`, and `Tile.DOOR` raises an `AttributeError`.

A `match` over `Tile` needs no `case _:` catch-all once every member has a case.
If you leave a member out of a function that declares a return type,
the type checker reports the gap before the code runs:

```python
# tile_enum_match.py
from tile_enum import Tile

# ty: function can implicitly return `None`,
# not assignable to return type `str`
def describe(tile: Tile) -> str:  # type: ignore
    match tile:
        case Tile.GRASS:
            return "grass"
        case Tile.WATER:
            return "water"

if __name__ == "__main__":
    print(describe(Tile.GRASS))
#: grass
```

Without the `# type: ignore`, `ty check` reports:

```
error[invalid-return-type]: Function can implicitly return
`None`, which is not assignable to return type `str`
 --> tile_enum_match.py:6:29
  |
6 | def describe(tile: Tile) -> str:
  |                             ^^^
```

The function returns `None` implicitly for `Tile.ROCK`,
the member the `match` leaves out, and adding that case clears the diagnostic.

The enum gives up loading at runtime.
`tile()` could load `SPECS` from a file, but `Tile.GRASS` is source code.
The [table-driven state machine](31_Patterns--State_Machines.md#table-driven-state-machine)
builds on an `Enum` the same way, using the enum's members as shared,
comparable states.

## Choosing a Flyweight and Its Pool

Three questions decide whether a type is a candidate for *Flyweight*.
First, do uses far outnumber distinct values?
A map with millions of cells and three kinds of tile qualifies.
A list of customer records, each one different, does not.
Second, can everything that varies per use move out of the object?
If a position, an owner, or a count must live inside,
every object is unique and no two uses can share an object,
as `unshared_cells.py` shows.
Third, can you freeze what remains?
Sharing a mutable object lets one use's change appear in every use
(see exercise 3).

When all three answers are yes, the remaining choice is the pool,
and the chapter shows four.
The question that decides between them is how much you know about the set of values.
If you know it as you write the program,
use an `Enum` and let the language hold the pool.
If callers must keep writing `C(...)`,
intern in `__new__()` and write the bookkeeping.
If the set keeps growing,
use a `WeakValueDictionary` so the pool shrinks with the live set.
Otherwise use a `@cache` factory.

These four answers read as an if/elif chain,
but the questions behind them are independent.
Constructor syntax and leak-safety are separate questions,
so `__new__()` interning can hold its pool weakly too.
Key the `WeakValueDictionary` on the constructor arguments the way `interned_color.py` keys `_pool`.
Combine mechanisms when more than one requirement applies.

## Flyweights in the Wild

Compilers and interpreters intern identifiers so that scope lookups compare pointers instead of characters.
Dataframe libraries such as pandas and Polars offer categorical types.
A column of a million country names stores small integer codes that index into a pool of distinct strings.
Text systems share one glyph object per character and font,
with each occurrence supplying its own position.
The benefit is the same in all three:
memory proportional to the number of distinct values, not the number of uses.
When every instance of a type comes from the pool,
you can write its equality checks as `is`.

## Exercises

Try each exercise before opening its [solution](../Solutions/35_Patterns--Flyweight/).

1.  Add door (`+`, walkable) and tree (`T`, not walkable)
    kinds to `tile_map.py`.
    Extend `Symbol` and `SPECS` to match,
    then write `walkable_neighbors(field, row, col)` returning the count of adjacent walkable cells.
    Confirm the tile pool size still equals the number of kinds,
    however large the map.
2.  Use `tracemalloc` to compare the memory `parse_map()` uses on a large map when every cell shares its `Tile` against when each cell gets a new one,
    by removing `@cache` from `tile()`.
    How does the ratio change as the map grows?
3.  Replace `@record` on `Tile` with `@dataclass` and set `field[0][0].walkable = False` on a parsed map.
    Write a test that exposes the resulting bug, then restore `@record`.
4.  Model chess: a frozen `Piece` (color, kind)
    and a board that is a `dict` mapping squares to pieces.
    A full opening position holds thirty-two piece references.
    How many `Piece` objects exist?
    How do you capture and promote?
5.  Rewrite `interned_color.py` to hold its pool weakly, as `weak_pool.py` does,
    and show that building and dropping a palette of colors leaves the pool empty.
    Say what the rewrite gave up to get there.
6.  Constrain `red`, `green`, and `blue` to `0`-`255` in `interned_color.py`.
    Raise `ValueError` from `__new__()` for an out-of-range component,
    and write a test for it.
7.  Rewrite `tile_map.py` on top of `tile_enum.py`'s `Tile`,
    so `parse_map()` returns `list[list[Tile]]` of enum members and `to_symbol()` disappears.
    What does the type checker still catch that the `Literal` version caught,
    and what does it catch that the `Literal` version did not?
8.  Make `tile()`'s body slow,
    with a `time.sleep(0.05)` before it builds the `Tile`,
    and call it from four threads with the same, previously unseen symbol.
    How many `Tile` objects get built,
    and how many distinct objects do the four threads hold?
    Fix it two ways: populate the pool eagerly at import,
    and guard the factory with a `threading.Lock`.
