# Data Transfer Objects: Solutions

## 1. Two `Messenger`s do not share attributes

```python
# exercise_1.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m1: Any = Messenger(info="hi", count=3)
m2: Any = Messenger(name="Bob", age=30)
print(m1.info, m1.count)
#: hi 3
print(m2.name, m2.age)
#: Bob 30
print(hasattr(m1, "name"), hasattr(m2, "info"))
#: False False
```

Each `Messenger()` call assigns a fresh `dict` to that instance's
`__dict__`: the one `**kwargs` built from that call's own arguments.
Every instance gets its own independent dictionary. A class attribute
from [Class Attributes](../Chapters/09_Foundations--Class_Attributes.md) works the other way:
one object shared by every instance until something shadows it. `m1`
and `m2` share nothing: `m1` has no `name`, and `m2` has no `info`.

## 2. A third field on `Point`

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

p = Point(1.0, 2.0, 3.0)
print(p)
#: Point(x=1.0, y=2.0, z=3.0)
p.x = 3.5
print(p == Point(3.5, 2.0, 3.0))
#: True
```

`@dataclass` reads whatever fields the class body declares and
generates `__init__()`, `__repr__()`, and `__eq__()` to match. Adding
`z: float` extends the constructor to three positional arguments, the
`repr()` to three fields, and the equality comparison to three values,
with no other code to update.

## 3. A `NamedTuple` holding a list

```python
# exercise_3.py
from typing import NamedTuple

class Recipe(NamedTuple):
    name: str
    steps: list[str]

toast = Recipe("Toast", ["slice", "heat"])
toast.steps.append("butter")
print(toast)
#: Recipe(name='Toast', steps=['slice', 'heat', 'butter'])
try:
    key = {toast: "breakfast"}
except TypeError as e:
    print(str(e).partition(" (")[0])
#: cannot use 'Recipe' as a dict key
```

The record changed, and nothing objected. `NamedTuple` refuses to
rebind `toast.steps`. It says nothing about the list that field
already refers to, so `append()` edits that list through the record.
Both `ty` and Python stay silent, because `append()` mutates the
list instead of assigning to a field.

Using the record as a `dict` key raises a `TypeError`, whose full message
names the cause: `cannot use 'Recipe' as a dict key (unhashable type:
'list')`. Hashing a tuple hashes each element, so a `Recipe` is
hashable only when every field is. The `list` has no hash, so the
record has none either.

The two results are one fact seen twice. The immutability a
`NamedTuple` gives you stops at the field, and a field pointing at a
mutable object hands that object's mutability back. `frozen=True` in
[Rethinking Objects](../Chapters/20_Patterns--Rethinking_Objects.md#the-immutability-solution)
is shallow the same way. Declaring `steps: tuple[str, ...]` fixes
both at once: the contents stop being editable and the record becomes
hashable. One declaration fixing both is the clue that they were
never two problems.

## 4. A fourth attribute supplied at construction

```python
# exercise_4.py
from types import SimpleNamespace

TAGS = ["urgent", "todo"]

built = SimpleNamespace(
    info="Spam", tags=TAGS, more=11, note=12)
print(list(vars(built)))
#: ['info', 'tags', 'more', 'note']

assigned = SimpleNamespace(
    info="Spam", tags=TAGS, more=11)
assigned.note = 12
print(list(vars(assigned)))
#: ['info', 'tags', 'more', 'note']

print(vars(built) == vars(assigned))
#: True
```

A keyword argument and a later assignment both add one entry to the
instance's `__dict__`. `vars()` reads that dict, and the two
namespaces are indistinguishable afterward. Even the order matches,
because a dict keeps insertion order and both routes add `note` last.
If you assign the attributes in a different sequence, the dicts still
compare equal, since dict equality ignores order.

## 5. Returning a bare `tuple[float, int]`

```python
# exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    return (sum(data) / len(data), len(data))

print(summarize([2.0, 4.0, 6.0]))
#: (4.0, 3)
mean, count = summarize([1.0, 3.0])
print(mean, count)
#: 2.0 2
```

Every caller still runs, because a `NamedTuple` was a tuple all along.
Unpacking works, indexing works, and printing works. What changed is
everything above the mechanics.

The call sites lost the names. `summarize([2.0, 4.0, 6.0])` now prints
`(4.0, 3)` instead of `Stats(mean=4.0, count=3)`, so the repr no longer
says which number is which. A reader of the call site has to open
`summarize()` to find out. They also lost attribute access:
`result.mean` becomes `result[0]`, which holds the same value and no
longer says what it is. And they lost the type as a name. Nothing can
carry a `Stats` annotation anymore, so a function accepting a summary
now advertises `tuple[float, int]`, which any pair of a `float` and an
`int` satisfies.

The type checker still catches a fair amount. Unpacking into the wrong
number of names fails, since the tuple's length is part of its type.
Passing `mean` to a parameter declared `int` fails, since the element
types are still known positionally. Indexing past the end fails, and
so does calling a `str` method on `count`.

What the checker cannot catch is the mistake this exercise is about:
swapping `mean` and `count`. `mean, count = summarize(data)` and
`count, mean = summarize(data)` destructure the same
`tuple[float, int]` into two names. The second type-checks cleanly and
misnames both values. With `Stats` you write `result.count`, so the
order never enters the code. A function annotated `Stats` also rejects
a reversed `tuple[int, float]`, because the two are different types.
Position is something the type checker can verify and a reader cannot.
A name is something both can.

## 6. Structural equality across three-field types

```python
# exercise_6.py
from dataclasses import dataclass
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Point3(NamedTuple):
    x: int
    y: int
    z: int

print(Color(1, 2, 3) == Point3(1, 2, 3))
#: True

@dataclass(frozen=True)
class FrozenColor:
    r: int
    g: int
    b: int

print(FrozenColor(1, 2, 3) == (1, 2, 3))
#: False
```

`Color(1, 2, 3) == Point3(1, 2, 3)` is `True`, the same answer
`Dimensions` gives, and for the same reason: a `NamedTuple` inherits
`tuple.__eq__`, which compares length and elements and consults neither
class. Adding a third `NamedTuple` adds a third type that compares
equal to the other two, so the family of things that equal `(1, 2, 3)`
grows with every three-integer `NamedTuple` in the program. The field names
are for you, not for `==`.

`FrozenColor(1, 2, 3) == (1, 2, 3)` is `False`. A frozen dataclass's
generated `__eq__()` first checks `other.__class__ is
self.__class__`, and returns `NotImplemented` for a plain tuple.
Python then tries the tuple's own comparison, which also returns
`NotImplemented`. With both sides declining, `==` falls back to
identity, which is `False` for two distinct objects. A dataclass is
not a tuple and never pretends to be one.

`NamedTuple` and the frozen dataclass offer a choice. A `NamedTuple`
is a tuple with labels, so it interoperates with everything expecting
a tuple and accepts equality with anything of the same shape. A frozen
dataclass is a distinct type, so it refuses those comparisons and
catches the mismatch instead. Which one is right depends on whether
you want your three numbers to travel as data or to mean something.
