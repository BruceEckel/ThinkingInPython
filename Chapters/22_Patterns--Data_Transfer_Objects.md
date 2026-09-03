# Data Transfer Objects

The *Messenger*, called a *Data Transfer Object* in Martin Fowler's *Patterns of Enterprise Application Architecture*,
passes a package of information around.
Most often it carries a function's return values.
You use tuples and dictionaries for that, but both rely on indexing.
A tuple requires the consumer to keep track of numerical order.
A `dict` requires the clumsier `d["name"]` syntax.

Fowler's DTO crosses a process or network boundary,
batching several values into one object to cut round trips.
The object shape below is the same one,
whether or not it ever leaves the process:
[Parallelism](19_Techniques--Concurrency.md#parallelism)
pickles arguments and return values across a process boundary the same way,
and [Serializing to JSON](12_Techniques--Data_Classes_as_Types.md#serializing-to-json)
turns one into the wire format for a network call.
This chapter teaches the object, not the crossing.

A Messenger is an object with attributes corresponding to the names of the data you pass or return:

```python
# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Spam", tags=["urgent", "todo"])
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo']}
m.more = 11
print(m.info, m.tags, m.more)
#: Spam ['urgent', 'todo'] 11
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo'], 'more': 11}
```

The constructor replaces the object's `__dict__` with the `dict` that the `**kwargs` parameter automatically creates.
`vars(m)` returns that same `__dict__`,
and its output shows that the attributes and the keyword arguments are one dict:
`m.more = 11` adds a key, just as passing `more=11` to the constructor would.

Because `**kwargs` is the only parameter,
`Messenger` accepts keyword arguments alone:
`Messenger("Spam")` raises a `TypeError`,
with no `*` marker from [Positional-Only and Keyword-Only Parameters](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)
needed.
Writing `def __init__(self, *, **kwargs)` anyway is a syntax error,
since a named parameter must follow a bare `*`.

The `m: Any` annotation does real work.
The `Messenger` class declares no attributes,
so without that annotation the type checker rejects both `m.more = 11` and `m.info`.
`Any` switches the type checker off for `m`.
You can move that `Any` into the class instead of repeating it at every use site,
by declaring a `__getattr__()` that returns `Any` and a `__setattr__()` that accepts one
([Surrogate](26_Patterns--Surrogate.md#forwarding-with-getattr) explains the `__getattr__()` fallback hook).
With `__getattr__()` alone, the type checker still rejects the write,
`m.more = 11`.
The standard library's stub for `SimpleNamespace` declares such a pair
(its read half is `__getattribute__()`, which intercepts every attribute access),
so the next listing needs no annotation.
The price of an ad-hoc attribute bag is that no type checker knows your attribute names.
A typo like `m.inof` is a runtime `AttributeError`, not a static error.

## The Standard-Library Versions

### `SimpleNamespace`

In the standard Python library,
`types.SimpleNamespace` is a ready-made Messenger.
Here, too, keyword arguments become attributes in the instance's `__dict__`:

```python
# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", tags=["urgent", "todo"])
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo']}
m.more = 11
print(m)
#: namespace(info='Spam', tags=['urgent', 'todo'], more=11)
print(m == SimpleNamespace(info="Spam",
                           tags=["urgent", "todo"],
                           more=11))
#: True
```

The first `print()` shows the same instance `__dict__` the hand-rolled version has.
`SimpleNamespace` adds the rest: a readable `repr()` and equality by contents.
`Messenger` prints as `<Messenger object at 0x...>`,
and two `Messenger`s with identical attributes compare unequal,
because `Messenger` inherits `object`'s identity-based equality.

A `SimpleNamespace` also accepts any name you invent,
so no type checker can know which names to expect.
Its type declaration says so: reading any attribute yields `Any`,
so `m.inof` passes the type checker here too.

### `@dataclass`

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

### `NamedTuple`

A `NamedTuple` declares its fields the same way but produces an immutable record.
`typing.NamedTuple` is the class form of the `namedtuple()` in [Containers](03_Foundations--Containers.md#namedtuple).
Both build a subclass of `tuple` whose positions also have names,
but the class form declares a type for each field,
so a type checker knows a `Color`'s `r` is an `int`,
where the functional form declares none.
Because a `Color` is a tuple underneath,
you can read each field by name or by position:

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
    print(e)
#: can't set attribute
print(red._replace(g=128))
#: Color(r=255, g=128, b=0)
print(red._asdict(), Color._fields)
#: {'r': 255, 'g': 0, 'b': 0} ('r', 'g', 'b')
```

Printing a `NamedTuple` gives the same readable output as a data class.
A bare tuple prints `(255, 0, 0)` and leaves you counting positions.
Assigning to a field raises an `AttributeError`,
and `ty` reports the assignment as well.
An attribute bag accepts every write; a declared field rejects this one,
at runtime and in the checker.
Because no field can change, `_replace()` is the way to change one:
it produces an updated copy.
`copy.replace()` from [The General Form of `replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
does the same job for any immutable record, including a frozen data class.
Immutability also makes the record hashable,
so a `Color` can key a `dict` or join a `set`.

The immutability guarantee reaches the fields, not the objects they name.
A `NamedTuple` holding a list still lets that list change,
the same leak [`frozen=True` has](20_Patterns--Rethinking_Objects.md#the-immutability-solution).
Such a record is also unhashable, mutated or not,
because hashing a tuple hashes its contents.
An immutable record needs immutable fields.

The leading underscore on `_replace()`, `_asdict()`,
and `_fields` keeps every unprefixed name free for your fields:
a record can declare a field called `replace` or `fields`.
The underscore marks `NamedTuple`'s own members, and says nothing about privacy.

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

Unpacking is the part a data class lacks.
`mean, count = summarize(data)` against a `@dataclass` version of `Stats` raises a `TypeError`,
since a data class is not iterable.
`dataclasses.astuple()` converts a data class when you need the positional form.
[More Data Class Tools](12_Techniques--Data_Classes_as_Types.md#more-data-class-tools)
covers its recursive, copying behavior.

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
    print(str(e).partition(" and")[0])
#: '<' not supported between instances of 'FrozenColor'

@dataclass(frozen=True, order=True)
class OrderedColor:
    r: int
    g: int
    b: int

@dataclass(frozen=True, order=True)
class OrderedDimensions:
    width: int
    height: int
    depth: int

try:
    OrderedColor(1, 2, 3) < OrderedDimensions(1, 2, 4)  # type: ignore
except TypeError as e:
    print(str(e).partition(" and")[0])
#: '<' not supported between instances of 'OrderedColor'
```

`Color` and `Dimensions` mean different things,
yet `Color(1, 2, 3) == Dimensions(1, 2, 3)` is `True`.
The frozen data classes tell the two apart,
because a dataclass's generated `__eq__()` checks the class before the fields.

A `NamedTuple` inherits ordering from `tuple` the same way,
and that ordering is as type-blind as equality.
Sorting a list of `Color`s orders them by `r`, then `g`, then `b`,
with nothing in the code declaring that intent.
A frozen data class refuses the comparison instead.
`<` between two `FrozenColor`s raises a `TypeError` unless the decorator receives `order=True`,
and a comparison between two different frozen types raises one even then.

Tuple behavior shows up in serialization too.
`json.dumps(Color(1, 2, 3))` writes the array `[1, 2, 3]`,
since `json` sees a sequence and the field names never reach the output.
Convert first, `json.dumps(Color(1, 2, 3)._asdict())`,
and the output is `{"r": 1, "g": 2, "b": 3}`.
`json.dumps()` on a data class raises a `TypeError` instead.
That is the safer failure of the two,
because the array version drops the names silently.

## Which Should You Use?

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
The hand-rolled `Messenger` is worth writing only to show how `SimpleNamespace` works underneath.

Between the two typed records,
the deciding question is whether tuple behavior is a feature.
Choose `NamedTuple` when it is: unpacking, multiple return values,
compatibility with code that expects a tuple.
Choose a [frozen dataclass](12_Techniques--Data_Classes_as_Types.md#immutability)
when a record should be a distinct type that equals only its own kind,
and when inherited ordering and array-shaped JSON would be wrong rather than convenient.

When the data must stay a dict,
because it arrives as JSON or goes back out as JSON,
a `TypedDict` from [Static Types](08_Foundations--Static_Types.md#dictionary-and-record-shapes)
names the keys and their types for the type checker while the value stays a real dict.
When the data need only *become* a dict on the way out,
`_asdict()` on a `NamedTuple` and `dataclasses.asdict()` on a data class each produce one.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values).

## Exercises

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes
    (unlike a class attribute from [Class Attributes](09_Foundations--Class_Attributes.md)).
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
7.  For each scenario, name the type from "Which Should You Use?" that fits,
    and say why the others do not:
    a configuration bag whose keys arrive at runtime and are not known in advance;
    a 2D grid coordinate that must work as a `dict` key;
    a record decoded from a JSON API response whose fields you also validate.
