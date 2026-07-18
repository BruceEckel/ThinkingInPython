# Data Transfer Objects

The *Messenger* or *Data Transfer Object* is a way to pass a clump of information around.
The most typical place for this is in return values from functions,
where tuples or dictionaries often serve.
However, those rely on indexing.
A tuple requires the consumer to keep track of numerical order.
A `dict` requires the clumsier `d["name"]` syntax.

A Messenger is an object with attributes corresponding to the names of the data you pass or return:

```python
# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11
print(vars(m))
#: {'info': 'Some information', 'b': ['a', 'list'], 'more': 11}
```

The trick here is replacing the object's `__dict__`,
the dict where Python keeps an instance's attributes,
with the `dict` that the `**kwargs` argument automatically creates.
`vars(m)` returns that same `__dict__`,
and its output shows the attributes and the keyword arguments are one dict:
`m.more = 11` added a key,
just as passing `more=11` to the constructor would have.

The `m: Any` annotation is quiet but load-bearing.
Without it, the type checker rejects both `m.more = 11` and `m.info`,
since the `Messenger` class declares no attributes.
`Any` switches the checker off for `m`
(the bargain described in [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance)),
and that is the honest price of an ad-hoc attribute bag:
no checker knows your attribute names,
so a typo like `m.inof` is a runtime `AttributeError`, not a static error.
The typed alternatives below buy the checker back.

You could create a `Messenger` class and put it in a library to import,
but there is no need: the standard library already ships this idiom,
as the next section shows.

Testing confirms the `Messenger` turns keyword arguments into attributes and takes new ones afterward:

```python
# test_messenger_idiom.py
from typing import Any
from messenger_idiom import Messenger

def test_messenger_exposes_kwargs_as_attributes() -> None:
    m: Any = Messenger(info="hi", count=3)
    assert m.info == "hi"
    assert m.count == 3
    m.added = 9  # Attributes can be added afterward, too
    assert m.added == 9
```

## The Standard-Library Versions

Python ships with this idiom.
`types.SimpleNamespace` is a `Messenger`,
with keyword arguments becoming attributes.
When you want the fields named and type-checked,
a `@dataclass` gives you a typed mutable record with a generated `__init__()`,
`__repr__()`, and equality, and a `NamedTuple` gives you a typed immutable one:

```python
# messenger_modern.py
from dataclasses import dataclass
from types import SimpleNamespace
from typing import NamedTuple

# SimpleNamespace is the Messenger idiom, built in:
m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11

# A dataclass is the typed, mutable version:
@dataclass
class Point:
    x: float
    y: float

print(Point(1.0, 2.0))
#: Point(x=1.0, y=2.0)

# A NamedTuple is the typed, immutable version:
class Color(NamedTuple):
    r: int
    g: int
    b: int

print(Color(255, 0, 0))
#: Color(r=255, g=0, b=0)
```

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).

This verifies that the `@dataclass` carries fields and value equality,
and the `NamedTuple` is a named record you can still treat as a tuple:

```python
# test_messenger_modern.py
from messenger_modern import Color, Point

def test_dataclass_point_has_fields_and_equality() -> None:
    assert Point(1.0, 2.0).x == 1.0
    assert Point(1.0, 2.0) == Point(1.0, 2.0)
    assert Point(1.0, 2.0) != Point(1.0, 3.0)

def test_namedtuple_color_is_a_named_record() -> None:
    c = Color(255, 0, 0)
    assert c.r == 255
    assert (c.r, c.g, c.b) == tuple(c)
```

`display_object()` shows that a `SimpleNamespace` keeps each keyword argument as an attribute:

```python
# display_namespace.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
display_object(m)
#: [Attributes]
#:   • b = ['a', 'list']
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
```

## Returning Multiple Values

This chapter opened by claiming the most typical Messenger is a return value,
so here is that use.
A function computes several related things,
and a `NamedTuple` carries them back under their own names:

```python
# fetch_stats.py
from typing import NamedTuple

class Stats(NamedTuple):
    mean: float
    count: int

def summarize(data: list[float]) -> Stats:
    return Stats(sum(data) / len(data), len(data))

stats = summarize([2.0, 4.0, 6.0])
print(stats.mean, stats.count)
#: 4.0 3
mean, count = summarize([1.0, 3.0])  # Unpacks like a tuple
print(mean, count)
#: 2.0 2
```

The near-miss is annotating the return as `tuple[float, int]` and returning a bare tuple.
It runs, but every caller then owns the knowledge that position 0 is the mean and position 1 is the count,
knowledge the code no longer states anywhere.
`Stats` names the slots and documents itself at each call site,
and because a `NamedTuple` is a tuple,
the unpacking idiom callers already use keeps working.

Testing confirms both access styles see the same values:

```python
# test_fetch_stats.py
from fetch_stats import Stats, summarize

def test_summarize_returns_named_fields() -> None:
    s = summarize([2.0, 4.0, 6.0])
    assert s == Stats(4.0, 3)
    assert s == (4.0, 3)  # A NamedTuple is still a tuple
```

## A NamedTuple Is Still a Tuple

That last test line is the flip side of the convenience,
and it is worth seeing once.
A `NamedTuple` inherits its equality from `tuple`: positional and type-blind.
Any tuple-shaped value with the same contents compares equal,
including a different record type that happens to share the shape:

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

A color is not a box, but the first comparison cannot tell them apart.
The frozen data classes can,
because a dataclass's generated `__eq__()` checks the class before the fields.
This refines the selection rule.
Choose `NamedTuple` when tuple behavior is the point: unpacking,
multiple return values, compatibility with code that expects a tuple.
Choose a frozen dataclass
([Data Classes as Types](12_Data_Classes_as_Types.md#immutability))
when a record should be a distinct type that equals nothing but its own kind.

## Exercises

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes
    (unlike a class attribute from [Class Attributes](09_Class_Attributes.md)).
2.  In `messenger_modern.py`, add a third field, `z: float`,
    to the `Point` dataclass,
    and update the `print(Point(1.0, 2.0))` call to pass three arguments.
3.  Add a `NamedTuple` called `Fraction` with fields `numerator: int` and `denominator: int` to `messenger_modern.py`,
    following `Color`'s shape,
    and confirm an instance still unpacks and indexes like a tuple.
4.  In `display_namespace.py`,
    add a fourth keyword argument to `m` when it is constructed instead of assigning `m.more` afterward,
    and confirm `display_object()` shows all four attributes,
    sorted alphabetically either way.
5.  In `fetch_stats.py`,
    change `summarize()` to return a plain `tuple[float, int]`.
    Every caller still runs.
    What did the call sites lose,
    and which mistakes would the type checker still catch?
6.  In `still_a_tuple.py`, add `class Point3(NamedTuple)` with fields `x`, `y`,
    `z`.
    Predict `Color(1, 2, 3) == Point3(1, 2, 3)` before running it,
    then predict `FrozenColor(1, 2, 3) == (1, 2, 3)` and check that too.
