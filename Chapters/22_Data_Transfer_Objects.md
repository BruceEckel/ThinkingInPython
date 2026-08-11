# Data Transfer Objects

The *Messenger* or *Data Transfer Object* is a way to pass a package of information around.
The most typical use is for function return values.
You often use tuples and dictionaries for that, but both rely on indexing.
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

The constructor replaces the object's `__dict__` with the `dict` that the `**kwargs` parameter automatically creates.
`vars(m)` returns that same `__dict__`,
and its output shows that the attributes and the keyword arguments are one dict:
`m.more = 11` adds a key, just as passing `more=11` to the constructor would.

Because `**kwargs` is the only parameter,
`Messenger` accepts only keyword arguments.
`Messenger("Spam")` raises a `TypeError`.
The `*` marker from [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters)
is unnecessary here, and `def __init__(self, *, **kwargs)` is a syntax error,
since a named parameter must follow a bare `*`.

The `m: Any` annotation is not decoration.
Without it, the type checker rejects both `m.more = 11` and `m.info`,
since the `Messenger` class declares no attributes.
`Any` switches the checker off for `m`.
You can move that `Any` into the class instead of repeating it at every use site,
by declaring a `__getattr__()` that returns `Any` and a `__setattr__()` that accepts one.
Declaring only the first leaves the write, `m.more = 11`, still rejected.
The standard library's stub for `SimpleNamespace` declares such a pair
(its read half is `__getattribute__()`, which intercepts every attribute access),
which is why the next listing needs no annotation.
The price of an ad-hoc attribute bag is that no checker knows your attribute names.
A typo like `m.inof` is a runtime `AttributeError`, not a static error.

## The Standard-Library Versions

In the standard Python library,
`types.SimpleNamespace` is a ready-made Messenger.
Here, too, keyword arguments become attributes in the instance's `__dict__`:

```python
# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(m)
#: namespace(info='Spam', b=['x', 'y'], more=11)
print(m == SimpleNamespace(info="Spam", b=["x", "y"], more=11))
#: True
```

The first `print()` shows the same instance `__dict__` the hand-rolled version had.
The rest is what `SimpleNamespace` adds:
a readable `repr()` and equality by contents.
`Messenger` prints as `<Messenger object at 0x...>`,
and two `Messenger`s with identical attributes compare unequal,
because it inherits `object`'s identity-based equality.

A `SimpleNamespace` also accepts any name you invent,
so no checker can know which names to expect.
Its type declaration says so: reading any attribute yields `Any`,
and `m.inof` goes unreported here as well.

When you want the fields named and checked, declare them.
A `@dataclass` generates `__init__()`, `__repr__()`,
and equality from those declarations, and produces a mutable record:

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
`typing.NamedTuple` is the class form of the `namedtuple()` in [Containers](03_Containers.md#namedtuple).
Both build a subclass of `tuple` whose positions also have names,
but the class form declares a type for each field,
so a checker knows a `Color`'s `r` is an `int` while the functional form leaves it unknown.
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
try:
    red.r = 9  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
print(red._replace(g=128))
#: Color(r=255, g=128, b=0)
print(red._asdict(), Color._fields)
#: {'r': 255, 'g': 0, 'b': 0} ('r', 'g', 'b')
```

Printing a `NamedTuple` gives the same readable output a data class gives.
A bare tuple prints `(255, 0, 0)` and leaves you counting positions.
Assigning to a field raises an `AttributeError`,
and `ty` reports it before the program runs.
The attribute bag caught nothing; a declared field catches this.
Since nothing can mutate the fields, `_replace()` produces an updated copy.
`copy.replace()` from [The General Form of `replace()`](12_Data_Classes_as_Types.md#the-general-form-of-replace)
does the same job for any immutable record, including a frozen data class.
Immutability also makes the record hashable,
so a `Color` can key a `dict` or join a `set`.

The immutability guarantee reaches the fields, not the objects they name.
A `NamedTuple` holding a list still lets that list change,
the same leak [`frozen=True` has](20_Rethinking_Objects.md#the-immutability-solution).
Nor can you hash such a record, whether or not anyone mutates the list,
because hashing a tuple hashes its contents.
An immutable record needs immutable fields.

The leading underscore on `_replace()`, `_asdict()`,
and `_fields` does not mean private.
`NamedTuple` marks its own members that way so they cannot collide with a field you name.
A record is free to declare a field called `replace` or `fields`.

## Returning Multiple Values

A function that computes two results can return them in a `NamedTuple`:

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

Without `Stats` you annotate the return as `tuple[float, int]` and return a bare tuple.
Every caller then owns the knowledge that position 0 is the mean and position 1 is the count,
knowledge the code no longer states anywhere.
`Stats` names the fields and documents itself at each call site,
and because a `NamedTuple` is a tuple, you can unpack it.

A data class cannot do that last part.
`mean, count = summarize(data)` against a `@dataclass` version of `Stats` raises a `TypeError`,
since a data class is not iterable.
`dataclasses.astuple()` converts one when you need the positional form.
It recurses, though: a nested data class comes back as a nested tuple,
and every other field is deep-copied rather than shared.

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
print(Color(1, 2, 3) < Dimensions(1, 2, 4))
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
try:
    FrozenColor(1, 2, 3) < FrozenColor(1, 2, 4)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

`Color` and `Dimensions` mean different things,
but the first comparison cannot tell them apart.
The frozen data classes can,
because a dataclass's generated `__eq__()` checks the class before the fields.

Ordering arrives by inheritance the same way, and is as type-blind as equality.
Sorting a list of `Color`s orders them by `r`, then `g`, then `b`,
with nothing in the code declaring that intent.
A frozen data class refuses the comparison instead.
`<` between two `FrozenColor`s raises a `TypeError` unless the decorator receives `order=True`,
and a comparison between two different frozen types raises one even then.

Tuple behavior shows up in serialization too.
`json.dumps(Color(1, 2, 3))` writes the array `[1, 2, 3]`,
since `json` sees a sequence and the field names never reach the output.
Converting first, `json.dumps(Color(1, 2, 3)._asdict())`,
writes `{"r": 1, "g": 2, "b": 3}`.
`json.dumps()` on a data class raises a `TypeError` instead.
That is the safer failure of the two,
because the array version loses the names without saying so.

## Which Should You Use?

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
The hand-rolled `Messenger` is worth writing only to show how `SimpleNamespace` works underneath.

Between the two typed records,
the deciding question is whether tuple behavior is a feature.
Choose `NamedTuple` when it is: unpacking, multiple return values,
compatibility with code that expects a tuple.
Choose a [frozen dataclass](12_Data_Classes_as_Types.md#immutability)
when a record should be a distinct type that equals only its own kind,
and when inherited ordering and array-shaped JSON would be wrong rather than convenient.

When the data must stay a dict,
because it arrives as JSON or goes back out as JSON,
a `TypedDict` from [Static Typing](08_Static_Typing.md#dictionary-and-record-shapes)
names the keys and their types for the checker while the value stays a real dict.
When it need only *become* a dict on the way out,
`_asdict()` on a `NamedTuple` and `dataclasses.asdict()` on a data class each produce one.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).

## Exercises

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes
    (unlike a class attribute from [Class Attributes](09_Class_Attributes.md)).
2.  In `point_dataclass.py`, add a third field, `z: float`,
    to the `Point` dataclass,
    and update the `Point(...)` call to pass three arguments.
3.  Add a `NamedTuple` called `Recipe` with fields `name: str` and `steps: list[str]` to `color_namedtuple.py`.
    Mutate the `steps` list of an instance and print the record.
    Then try to use the record as a `dict` key and explain the result.
4.  In `display_namespace.py`,
    add a fourth attribute to `m` by passing it to the constructor,
    then add it by assignment after the existing `m.more = 11` instead.
    Confirm `vars(m)` reports the same four attributes either way,
    and note whether they come out in the same order.
5.  In `fetch_stats.py`,
    change `summarize()` to return a bare `tuple[float, int]`.
    Every caller still runs.
    What did the call sites lose,
    and which mistakes would the type checker still catch?
6.  In `still_a_tuple.py`, add `class Point3(NamedTuple)` with fields `x`, `y`,
    `z`.
    Predict `Color(1, 2, 3) == Point3(1, 2, 3)` before running it,
    then predict `FrozenColor(1, 2, 3) == (1, 2, 3)` and check that too.
