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
print(vars(m))
#: {'info': 'Some information', 'b': ['a', 'list']}
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11
print(vars(m))
#: {'info': 'Some information', 'b': ['a', 'list'], 'more': 11}
```

`class Messenger` replaces the object's `__dict__`,
the dict where Python keeps an instance's attributes,
with the `dict` that the `**kwargs` argument automatically creates.
`vars(m)` returns that same `__dict__`,
and its output shows the attributes and the keyword arguments are one dict:
`m.more = 11` added a key,
just as passing `more=11` to the constructor would have.

Because `**kwargs` is the only parameter,
`Messenger` accepts nothing but keyword arguments.
`Messenger("Some information")` raises a `TypeError`.
The `*` marker from [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters)
is unnecessary here, and `def __init__(self, *, **kwargs)` is a syntax error,
since a bare `*` must be followed by a named parameter.
The one name a caller cannot use is `self`.
Writing `def __init__(self, /, **kwargs)` makes `self` positional-only and frees the name,
so `Messenger(self="me")` becomes a legal attribute instead of a duplicate argument.

The `m: Any` annotation is quiet but load-bearing.
Without it, the type checker rejects both `m.more = 11` and `m.info`,
since the `Messenger` class declares no attributes.
`Any` switches the checker off for `m`,
the bargain described in [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance).
That is the price of an ad-hoc attribute bag:
no checker knows your attribute names,
so a typo like `m.inof` is a runtime `AttributeError`, not a static error.

## The Standard-Library Versions

In the standard Python library, `types.SimpleNamespace` is a `Messenger`,
with keyword arguments becoming attributes.
`display_object()` from [Metaprogramming](17_Metaprogramming.md#the-inspect-module)
confirms that each keyword argument lands in the instance's `__dict__`,
alongside anything assigned afterward:

```python
# display_namespace.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11
display_object(m)
#: [Attributes]
#:   • b = ['a', 'list']
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
```

A `SimpleNamespace` is as anonymous as the hand-rolled `Messenger`.
It accepts any name you invent, so no checker can know which names to expect.
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
```

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).

## Returning Multiple Values

The most common Messenger is a return value.
Here, a function computes several related things,
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
2.  In `point_dataclass.py`, add a third field, `z: float`,
    to the `Point` dataclass,
    and update both `Point(...)` calls to pass three arguments.
3.  Add a `NamedTuple` called `Fraction` with fields `numerator: int` and `denominator: int` to `color_namedtuple.py`,
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
