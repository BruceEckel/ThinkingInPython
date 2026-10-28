# Data Transfer Objects

> A function computes several results, and the caller needs all of them.
> A *Data Transfer Object* carries them back under names instead of positions.

The *Messenger* passes a package of information around.
Martin Fowler's *Patterns of Enterprise Application Architecture* calls it a *Data Transfer Object*
(DTO).
Most often it carries a function's return values.
Tuples and dictionaries can carry them too, but both rely on indexing.
A tuple requires the consumer to keep track of numerical order.
A `dict` requires the clumsier `d["name"]` syntax.

Fowler's DTO crosses a process or network boundary,
batching several values into one object to cut round trips.
The objects in this chapter also hold several named values in one object,
whether or not your program sends them to another process.
To send one to a worker process,
a [process pool pickles it](19_Techniques--Concurrency.md#what-a-process-pool-requires).
For a network call, [Serializing to JSON](12_Techniques--Data_Classes_as_Types.md#serializing-to-json)
turns a data class into the wire format.

## A Hand-Rolled Messenger

A *Messenger* is an object whose attribute names match the data you pass or return:

```python
# messenger_idiom.py
from typing import Any
from exceptions import expected

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Spam", tags=["urgent", "todo"])
m.more = 11
print(m.info, m.tags, m.more)
#: Spam ['urgent', 'todo'] 11
print(vars(m))
#: {'info': 'Spam', 'tags': ['urgent', 'todo'], 'more': 11}
with expected(AttributeError):
    m.inof
#: [AttributeError] 'Messenger' object has no attribute
#: 'inof'
```

The constructor replaces the object's `__dict__` with the `dict` that the `**kwargs` parameter automatically creates.
`m.more = 11` adds a key to that `dict`,
as passing `more=11` to the constructor does.
`vars(m)` returns that same `__dict__`.

Because `**kwargs` is the only parameter after `self`,
`Messenger` accepts keyword arguments alone.
`Messenger("Spam")` raises a `TypeError`,
so `**kwargs` does the job of the [keyword-only `*` marker](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters).
Writing `def __init__(self, *, **kwargs)` is a syntax error,
since a named parameter must follow a bare `*`.

The listing needs the `m: Any` annotation to pass the type checker.
`Messenger` creates its attributes at runtime,
from the keyword arguments a caller passes.
If `m` keeps its inferred type, `Messenger`,
the type checker rejects the write `m.more = 11` and every read,
such as `m.info`.
With `Any`, the type checker accepts every operation on `m`.

An ad-hoc attribute bag's class is silent about your attribute names,
so the type checker cannot verify them.
The type checker accepts the typo `m.inof` because `m` is `Any`.
At runtime the read raises an `AttributeError`.

Instead of annotating every variable that holds a `Messenger`,
you can move that `Any` into the class.
Declare a [`__getattr__()`](25_Patterns--Surrogate.md#forwarding-with-getattr)
that returns `Any` and a `__setattr__()` that accepts an `Any` value.
The `__getattr__()` covers reads.
The `__setattr__()` covers writes such as `m.more = 11`.
The standard library's type declaration for `SimpleNamespace` has such a pair.
In place of `__getattr__()`, its read half is `__getattribute__()`,
which intercepts every attribute access.
Because of that pair,
the type checker accepts the next listing's `m` at its inferred type,
`SimpleNamespace`.

## The Standard-Library Versions

### `SimpleNamespace`

The standard library's `types.SimpleNamespace` is a ready-made *Messenger*.
Here, too, keyword arguments become attributes in the instance's `__dict__`:

```python
# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", tags=["urgent", "todo"])
print(vars(m))  # [1]
#: {'info': 'Spam', 'tags': ['urgent', 'todo']}
m.more = 11
print(m)
#: namespace(info='Spam', tags=['urgent', 'todo'], more=11)
print(m == SimpleNamespace(info="Spam",
                           tags=["urgent", "todo"],
                           more=11))
#: True
```

The `print()` at `[1]` shows the keyword arguments stored in the instance `__dict__`,
as in the hand-rolled version.
`SimpleNamespace` adds a readable `repr()` and equality by contents.
`Messenger` prints as `<__main__.Messenger object at 0x...>`.
Two `Messenger`s with identical attributes compare unequal,
because `Messenger` inherits `object`'s identity-based equality.

A `SimpleNamespace` also accepts any name you invent.
Its type declaration gives every attribute read the type `Any`,
so a typo such as `m.inof` passes the type checker here too.

### `@dataclass`

When you want the fields named and checked, declare them.
A `@dataclass` generates `__init__()`, `__repr__()`,
and equality from those declarations.
Its fields stay assignable:

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

`p.x = 3.5` succeeds because a data class is mutable by default.
[A NamedTuple Is Still a Tuple](#a-namedtuple-is-still-a-tuple)
compares the frozen form with a `NamedTuple`.
This book's listings write the frozen form as [`@record`](18_Techniques--Performance.md#record).

### `NamedTuple`

A `NamedTuple` declares its fields as annotations in the class body,
as a data class does, but produces immutable instances.
`typing.NamedTuple` is the class form of [`namedtuple()`](03_Foundations--Containers.md#namedtuple).
Both build a subclass of `tuple` whose positions also have names.
The class form adds a type for each field,
so the type checker infers `int` for a `Color`'s `r`.
Because a `Color` is a tuple underneath,
you can read each field by name or by position:

```python
# color_namedtuple.py
from typing import NamedTuple
from exceptions import expected

class Color(NamedTuple):
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
print(red)
#: Color(r=255, g=0, b=0)
print(red.r, red[0])
#: 255 255
with expected(AttributeError):
    red.r = 9  # type: ignore
#: [AttributeError] can't set attribute
print(red._replace(g=128))
#: Color(r=255, g=128, b=0)
print(red._asdict(), Color._fields)
#: {'r': 255, 'g': 0, 'b': 0} ('r', 'g', 'b')
```

Printing a `NamedTuple` shows the class name and each field by name,
`Color(r=255, g=0, b=0)`, as printing a data class does.
A bare tuple prints `(255, 0, 0)` and leaves you counting positions.

An attribute bag accepts every write.
A `NamedTuple` rejects a write to a field twice:
the type checker reports `red.r = 9` before the script runs,
and at runtime the assignment raises an `AttributeError`.

Because the constructor sets every field once,
`_replace()` builds an updated copy with new values for the fields you name.
[`copy.replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
does the same job for a `NamedTuple`, a frozen data class,
and any other type that defines `__replace__()`.
Immutability also makes a `NamedTuple` hashable,
so a `Color` can be a `dict` key or a `set` element.

Immutability applies to the fields, not to the objects they name.
A `NamedTuple` holding a list lets that list change,
the same leak [`frozen=True` has](20_Patterns--Rethinking_Objects.md#the-immutability-solution).
Such a `NamedTuple` is also unhashable, mutated or not,
because hashing a tuple hashes its contents,
and `hash()` on a list raises a `TypeError`.
An immutable type needs immutable fields.

The leading underscore on `_replace()`, `_asdict()`,
and `_fields` keeps the ordinary names free for your fields.
A `NamedTuple` can declare a field called `replace` or `fields`.
The underscore marks `NamedTuple`'s own members, not private ones.

## Returning Multiple Values

A function that computes two results can return them in a `NamedTuple`:

```python
# summarize_stats.py
from typing import NamedTuple

class Stats(NamedTuple):
    mean: float
    count: int

def summarize(data: list[float]) -> Stats:
    return Stats(sum(data) / len(data), len(data))

result = summarize([2.0, 4.0, 6.0])
print(result)
#: Stats(mean=4.0, count=3)
print(result.mean, result.count)
#: 4.0 3
mean, count = summarize([1.0, 5.0])  # Unpacks like a tuple
print(f"{mean=} {count=}")
#: mean=3.0 count=2
count, mean = summarize([1.0, 5.0])
print(f"{mean=} {count=}")
#: mean=2 count=3.0
```

A tuple version of `summarize()` annotates its return as `tuple[float, int]` and returns a bare tuple.
Every caller must then remember that position 0 is the mean and position 1 is the count.
No name in the code records that order.
`Stats` names the fields,
so a call site reads `result.mean` instead of `result[0]`.

Because a `NamedTuple` is a tuple, you can also unpack it.
Unpacking assigns by position,
so a caller can still swap the mean and the count.
`count, mean = summarize([1.0, 5.0])` runs and passes the type checker.
Reading `result.mean` picks the field by name, whatever its position.

Unpacking sets a `NamedTuple` apart from a data class.
If `Stats` is a `@dataclass`,
`mean, count = summarize(data)` raises a `TypeError`,
since a data class is not iterable.
`dataclasses.astuple()` converts a data class when you need the positional form.
[More Data Class Tools](12_Techniques--Data_Classes_as_Types.md#more-data-class-tools)
shows that `astuple()` also converts nested data classes and builds a new copy of every list and dict it returns.

## A NamedTuple Is Still a Tuple

A `NamedTuple` inherits its equality from `tuple`,
which compares elements by position and ignores the class.
Any tuple-shaped value with the same contents compares equal,
including a different `NamedTuple` class with the same shape:

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
print(Dimensions(1, 2, 3) in {Color(1, 2, 3)})
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
yet `Color(1, 2, 3) == Dimensions(1, 2, 3)` is `True`.
Equal tuples hash alike,
so the two are also the same `set` element or `dict` key.
The frozen data classes compare unequal,
because a data class's generated `__eq__()` tests `other.__class__ is self.__class__` before it compares the fields.

A `NamedTuple` inherits ordering from `tuple` the same way.
The listing below repeats `Color`, `Dimensions`,
and `FrozenColor` beside two data classes that pass `order=True`:

```python
# tuple_ordering.py
from dataclasses import dataclass
from typing import NamedTuple
from exceptions import expected

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Dimensions(NamedTuple):
    width: int
    height: int
    depth: int

print(Color(1, 2, 3) < Dimensions(1, 2, 4))
#: True

@dataclass(frozen=True)
class FrozenColor:
    r: int
    g: int
    b: int

with expected(TypeError):
    FrozenColor(1, 2, 3) < FrozenColor(1, 2, 4)  # type: ignore
#: [TypeError] '<' not supported between instances of
#: 'FrozenColor' and 'FrozenColor'

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

print(OrderedColor(1, 2, 3) < OrderedColor(1, 2, 4))
#: True
with expected(TypeError):
    OrderedColor(1, 2, 3) < OrderedDimensions(1, 2, 4)  # type: ignore
#: [TypeError] '<' not supported between instances of
#: 'OrderedColor' and 'OrderedDimensions'
```

Tuple ordering also crosses `NamedTuple` classes,
as `Color(1, 2, 3) < Dimensions(1, 2, 4)` shows.
Sorting a list of `Color`s orders them by `r`, then `g`, then `b`.
The sequence of the field declarations sets that order implicitly.
A frozen data class generates ordering methods only when the decorator receives `order=True`.
The generated `__lt__()` runs the same class test as `__eq__()`,
so comparing an `OrderedColor` with an `OrderedDimensions` raises a `TypeError`.

Both listings write `@dataclass(frozen=True)` in full instead of `@record`,
so that `FrozenColor` reads the same in each,
and `order=True` is the one difference between `FrozenColor` and its twin `OrderedColor`.

Tuple behavior affects serialization too.
`json.dumps(Color(1, 2, 3))` writes the array `[1, 2, 3]`,
since `json` encodes every tuple as an array of its values,
and a `NamedTuple` is a tuple.
Converting first, with `json.dumps(Color(1, 2, 3)._asdict())`,
writes `{"r": 1, "g": 2, "b": 3}`.
`json.dumps()` on a data class raises a `TypeError`.
The `TypeError` is the safer failure of the two,
because the array version drops the names silently.

## Subclassing `tuple` Directly

`NamedTuple` generates a `tuple` subclass.
You can also subclass `tuple` directly when you need the tuple protocol together with your own construction or methods.
A tuple takes its contents at creation,
so `__init__()` runs too late to assign them.
A custom `tuple` subclass overrides `__new__()` and hands the items to `tuple.__new__()`:

```python
# point_tuple.py
from typing import Self

class Point(tuple[float, float]):
    __slots__ = ()

    def __new__(cls, x: float, y: float) -> Self:
        return super().__new__(cls, (x, y))

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

p = Point(1.0, 2.0)
print(p, p.x, p.y)
#: (1.0, 2.0) 1.0 2.0
print(isinstance(p, tuple), p == (1.0, 2.0))
#: True True
print(type(p + (3.0,)).__name__, type(p[:1]).__name__)
#: tuple tuple
print(hasattr(p, "__dict__"))
#: False
```

Indexing, slicing, unpacking, hashing, and equality all come from `tuple`,
so a `Point` works anywhere code expects a tuple.
A `Point` also equals the bare `(1.0, 2.0)`,
the same structural equality that `still_a_tuple.py` shows.

Tuple operations return plain tuples.
A subclass whose `+` and slicing must return its own type overrides `__add__()` and `__getitem__()`.
The empty `__slots__ = ()` keeps a `Point` as small as a tuple.
A subclass that declares no `__slots__` gives each instance a `__dict__`,
and with it the ability to grow attributes beyond the ones the class declares.

## Which Should You Use?

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for typed fields you reassign,
and a `NamedTuple` for typed fields set once.
The hand-rolled `Messenger` is worth writing only to show that `SimpleNamespace` stores its keyword arguments in the instance `__dict__`.

The frozen data class, which this book writes as `@record`,
is another immutable type with typed fields.
Between it and a `NamedTuple`,
the deciding question is whether tuple behavior is a feature.
Choose `NamedTuple` when it is: unpacking, multiple return values,
compatibility with code that expects a tuple.
Subclass `tuple` yourself, as `point_tuple.py` does,
when that tuple behavior must come with your own construction or methods.
Choose a [record](12_Techniques--Data_Classes_as_Types.md#immutability)
when the value should be a distinct type that equals instances of its own class alone.
Choose the record too when inherited ordering and array-shaped JSON are wrong rather than convenient,
or when the type must check its own values.
A record runs [`__post_init__()`](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
on every construction, so its values are legal as well as typed.
By contrast, [a `NamedTuple` cannot validate itself](12_Techniques--Data_Classes_as_Types.md#namedtuple-cannot-validate).

When the data must stay a dict,
because it arrives as JSON or goes back out as JSON,
a [`TypedDict`](08_Foundations--Static_Types.md#dictionary-and-record-shapes)
specifies the keys and their types for the type checker while the data stays a real dict.
When the data becomes a dict for output alone,
`_asdict()` on a `NamedTuple` and `dataclasses.asdict()` on a data class each produce one.

## Exercises

Try each exercise before opening its [solution](../Solutions/28_Patterns--Data_Transfer_Objects/).

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm each instance keeps its own attributes
    (unlike a [class attribute](09_Foundations--Class_Attributes.md)).
2.  In `point_dataclass.py`, add a third field, `z: float`,
    to the `Point` data class,
    and update the `Point(...)` call to pass three arguments.
3.  Add a `NamedTuple` called `Recipe` with fields `name: str` and `steps: list[str]` to `color_namedtuple.py`.
    Mutate the `steps` list of an instance and print the `Recipe`.
    Then try to use the `Recipe` as a `dict` key and explain the result.
4.  In `display_namespace.py`,
    add a fourth attribute to `m` by passing it to the constructor,
    then add it by assignment after the existing `m.more = 11` instead.
    Confirm `vars(m)` reports the same four attributes either way,
    and note whether they come out in the same order.
5.  In `summarize_stats.py`,
    change `summarize()` to return a bare `tuple[float, int]`,
    and repair the one line that breaks.
    What do the call sites lose,
    and which mistakes does the type checker still catch?
6.  In `still_a_tuple.py`, add `class Point3(NamedTuple)` with fields `x`, `y`,
    `z`.
    Predict `Color(1, 2, 3) == Point3(1, 2, 3)` before running it,
    then predict `FrozenColor(1, 2, 3) == (1, 2, 3)` and check that too.
7.  For each scenario, name the type from "Which Should You Use?" that fits,
    and say why the others do not:
    a configuration bag whose keys first appear at runtime;
    a 2D grid coordinate that must work as a `dict` key;
    an object decoded from a JSON API response whose fields you also validate.
8.  Give `point_tuple.py`'s `Point` an `__add__()` that returns a `Point`,
    and a `__repr__()` that prints `Point(1.0, 2.0)`.
    Check that slicing still returns a plain tuple.
