# Data Transfer Objects

The *Messenger* or *Data Transfer Object* is a way to pass a package of information around.
The most typical use is for function return values.
Tuples and dictionaries are often used for that, but both rely on indexing.
A tuple requires the consumer to keep track of numerical order.
A `dict` requires the clumsier `d["name"]` syntax.

A Messenger is an object with attributes corresponding to the names of the data you pass or return:

```python
# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(m.info, m.b, m.more)
#: Spam ['x', 'y'] 11
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11}
```

The constructor replaces the object's `__dict__` with the `dict` the `**kwargs` argument automatically creates.
`vars(m)` returns that same `__dict__`,
and its output shows the attributes and the keyword arguments are one dict:
`m.more = 11` adds a key, just as passing `more=11` to the constructor would.

Because `**kwargs` is the only parameter,
`Messenger` accepts nothing but keyword arguments.
`Messenger("Spam")` raises a `TypeError`.
The `*` marker from [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters)
is unnecessary here, and `def __init__(self, *, **kwargs)` is a syntax error,
since a bare `*` must be followed by a named parameter.

The `m: Any` annotation is not decoration.
Without it, the type checker rejects both `m.more = 11` and `m.info`,
since the `Messenger` class declares no attributes.
`Any` switches the checker off for `m`.
The price of an ad-hoc attribute bag is that no checker knows your attribute names.
A typo like `m.inof` is a runtime `AttributeError`, not a static error.

## The Standard-Library Versions

In the standard Python library, `types.SimpleNamespace` is a `Messenger`.
Here, too, keyword arguments become attributes that land in the instance's `__dict__`:

```python
# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y'], 'more': 11}
```

A `SimpleNamespace` also accepts any name you invent,
so no checker can know which names to expect.

When you want the fields named and checked, declare them.
A `@dataclass` generates `__init__()`, `__repr__()`,
and equality from those declarations, producing a mutable record:

```python
# point_dataclass.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
print(p)
#: Point(x=1.0, y=2.0)
p.x = 3.5
print(p)
#: Point(x=3.5, y=2.0)
```

A `NamedTuple` declares its fields the same way but produces an immutable record.
Because it is a tuple underneath, each field is readable by name or by position:

```python
# color_namedtuple.py
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
print(red)
#: Color(r=255, g=0, b=0)
print(red.r, red[0])
#: 255 255
print(red._replace(g=128))
#: Color(r=255, g=128, b=0)
print(red._asdict(), Color._fields)
#: {'r': 255, 'g': 0, 'b': 0} ('r', 'g', 'b')
```

Printing a `NamedTuple` gives the same readable output a data class gives.
A bare tuple prints `(255, 0, 0)` and leaves you counting positions.
Since the fields cannot be mutated, `_replace()` produces an updated copy.
The leading underscore on `_replace()`, `_asdict()`,
and `_fields` does not mean private.
`NamedTuple` marks its own members that way so they cannot collide with a field you name.
A record is free to declare a field called `replace` or `fields`.

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).

## Returning Multiple Values

This is the return-value use promised at the start.
Here, a function computes two results, returned in a `NamedTuple`:

```python
# fetch_stats.py
from typing import NamedTuple

class Stats(NamedTuple):
    mean: float
    count: int

def summarize(data: list[float]) -> Stats:
    return Stats(sum(data) / len(data), len(data))

print(summarize([2.0, 4.0, 6.0]))
#: Stats(mean=4.0, count=3)
mean, count = summarize([1.0, 3.0])  # Unpacks like a tuple
print(mean, count)
#: 2.0 2
```

Without `Stats` you'd annotate the return as `tuple[float, int]` and return a bare tuple.
Every caller would then own the knowledge that position 0 is the mean and position 1 is the count,
knowledge the code no longer states anywhere.
`Stats` names the slots and documents itself at each call site,
and because a `NamedTuple` is a tuple, you can unpack it.

## A NamedTuple Is Still a Tuple

A `NamedTuple` inherits its equality from `tuple`: positional and type-blind.
Any tuple-shaped value with the same contents compares equal,
including a different record type that happens to have the same shape:

```python
# still_a_tuple.py
from dataclasses import dataclass
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Dimensions(NamedTuple):
    width: int
    height: int
    depth: int

print(Color(1, 2, 3) == Dimensions(1, 2, 3))
#: True
print(Color(1, 2, 3) == (1, 2, 3))
#: True

@dataclass(frozen=True)
class FrozenColor:
    r: int
    g: int
    b: int

@dataclass(frozen=True)
class FrozenDimensions:
    width: int
    height: int
    depth: int

print(FrozenColor(1, 2, 3) == FrozenDimensions(1, 2, 3))
#: False
```

`Color` and `Dimensions` mean different things,
but the first comparison cannot tell them apart.
The frozen data classes can,
because a dataclass's generated `__eq__()` checks the class before the fields.
This refines the selection rule.
Choose `NamedTuple` when tuple behavior is the goal: unpacking,
multiple return values, compatibility with code that expects a tuple.
Choose a [frozen dataclass](12_Data_Classes_as_Types.md#immutability)
when a record should be a distinct type that equals nothing but its own kind.

## Exercises

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes
    (unlike a class attribute from [Class Attributes](09_Class_Attributes.md)).
2.  In `point_dataclass.py`, add a third field, `z: float`,
    to the `Point` dataclass,
    and update both `Point(...)` calls to pass three arguments.
3.  Add a `NamedTuple` called `Fraction` with fields `numerator: int` and `denominator: int` to `color_namedtuple.py`,
    following `Color`'s shape,
    and confirm an instance still unpacks and indexes like a tuple.
4.  In `display_namespace.py`,
    add a fourth attribute to `m` by passing it to the constructor,
    then add it by assignment instead.
    Confirm `vars(m)` reports the same four attributes, in the same order,
    either way.
5.  In `fetch_stats.py`,
    change `summarize()` to return a bare `tuple[float, int]`.
    Every caller still runs.
    What did the call sites lose,
    and which mistakes would the type checker still catch?
6.  In `still_a_tuple.py`, add `class Point3(NamedTuple)` with fields `x`, `y`,
    `z`.
    Predict `Color(1, 2, 3) == Point3(1, 2, 3)` before running it,
    then predict `FrozenColor(1, 2, 3) == (1, 2, 3)` and check that too.
