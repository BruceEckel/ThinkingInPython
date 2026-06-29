# Pattern Refactoring

This chapter follows one problem through several designs.
A first solution solves it,
then we ask "what will change?" and reshape the design to absorb that change cheaply.
This is the spirit of Martin Fowler's *Refactoring*,
applied at the level of patterns rather than single statements.

This is also a Python lesson.
Several of the patterns that the original *Design Patterns* book needed are answers to limitations of statically typed languages without multiple dispatch.
Python removes some of those limitations,
so a few common patterns simply dissolve here.
We will call that out as it happens.

## Simulating a Trash Recycler

Trash arrives at the recycling plant mixed together.
The program must sort it by material and report the total value of each kind.
The trash starts out as an undifferentiated pile,
and the type of each piece must be recovered to sort it.

In the `Trash` hierarchy, each material carries a per-pound `value`.
The base class keeps a `registry` of its subclasses,
filled automatically by `__init_subclass__()`,
and a `create()` method builds an instance from a material name (this is a *factory*):

```python
# trash.py
# The Trash hierarchy, with self-registration and a per-pound value.
from typing import ClassVar

class Trash:
    value: ClassVar[float] = 0.0  # Dollars per pound (per subclass)
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return Trash.registry[name](weight)

class Aluminum(Trash):
    value = 1.67

class Paper(Trash):
    value = 0.10

class Glass(Trash):
    value = 0.23

class Cardboard(Trash):
    value = 0.79

def sum_value(items: list[Trash]) -> float:
    total = 0.0
    for t in items:
        print(f"weight of {type(t).__name__} = {t.weight}")
        total += t.weight * t.value
    print(f"Total value = {total:.2f}")
    return total
```

Adding a new recyclable type is now one class definition.
It registers itself, and `create()` can build it.
`sum_value()` is an ordinary function:
it relies on polymorphism (`t.value`, `t.weight`) and never asks what type each piece is.

These tests confirm each subclass registers itself, `create()` builds one by name, the per-pound values are right, and `sum_value()` totals weight times value:

```python
# test_trash.py
import pytest
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value

def test_subclasses_self_register() -> None:
    assert set(Trash.registry) == {
        "Aluminum", "Paper", "Glass", "Cardboard"}

def test_create_builds_by_name() -> None:
    t = Trash.create("Aluminum", 2.0)
    assert isinstance(t, Aluminum)
    assert t.weight == 2.0

def test_per_pound_values() -> None:
    assert Aluminum.value == 1.67
    assert Paper.value == 0.10
    assert Glass.value == 0.23
    assert Cardboard.value == 0.79

def test_sum_value_totals_weight_times_value() -> None:
    items: list[Trash] = [Aluminum(2.0), Paper(5.0)]
    assert sum_value(items) == pytest.approx(3.84)  # 2*1.67 + 5*0.10
```

The trash to process is described in a data file,
one `Name:weight` line per piece:

```python
# trash.dat
Glass:54
Paper:22
Paper:11
Glass:17
Aluminum:89
Paper:88
Aluminum:76
Cardboard:96
Aluminum:25
Aluminum:34
Glass:11
Glass:68
Glass:43
Aluminum:27
Cardboard:44
Aluminum:18
Paper:91
Glass:63
Glass:50
Glass:80
Aluminum:81
Cardboard:12
```

Parsing it into `Trash` objects goes through the registry,
so the parser never mentions a concrete material.
Add a new kind of trash and the parser keeps working unchanged:

```python
# parse_trash.py
# Read "Name:weight" lines into Trash objects through the registry.
from pathlib import Path
from trash import Trash

def parse(filename: str) -> list[Trash]:
    items: list[Trash] = []
    for line in Path(filename).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, weight = line.split(":")
        items.append(Trash.create(name.strip(), float(weight)))
    return items
```

A test parses a small file written on the spot, so it does not depend on `trash.dat`:

```python
# test_parse_trash.py
from pathlib import Path
from parse_trash import parse

def test_parse_reads_and_skips_comments(tmp_path: Path) -> None:
    data = tmp_path / "trash.dat"
    data.write_text("""\
# header
Aluminum:2.0

Glass:3.0
""")
    items = parse(str(data))
    assert [type(t).__name__ for t in items] == ["Aluminum", "Glass"]
    assert items[0].weight == 2.0
    assert items[1].weight == 3.0
```

## The First Cut: Checking Every Type

The most obvious way to sort is to look at each piece and test what it is using `isinstance()`:

```python
# recycle_rtti.py
# First cut: sort by testing each type. It works, but it checks for
# EVERY type. Add a new kind of Trash and you must find and edit
# this code, with no help from the tools if you miss a spot. That is
# the smell to watch for.
from collections import defaultdict
from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value

bins: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in parse("trash.dat"):
    if isinstance(t, Aluminum):
        bins[Aluminum].append(t)
    elif isinstance(t, Paper):
        bins[Paper].append(t)
    elif isinstance(t, Glass):
        bins[Glass].append(t)
    elif isinstance(t, Cardboard):
        bins[Cardboard].append(t)
for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
#: --- Glass ---
#: weight of Glass = 54.0
#: weight of Glass = 17.0
#: weight of Glass = 11.0
#: weight of Glass = 68.0
#: weight of Glass = 43.0
#: weight of Glass = 63.0
#: weight of Glass = 50.0
#: weight of Glass = 80.0
#: Total value = 88.78
#: --- Paper ---
#: weight of Paper = 22.0
#: weight of Paper = 11.0
#: weight of Paper = 88.0
#: weight of Paper = 91.0
#: Total value = 21.20
#: --- Aluminum ---
#: weight of Aluminum = 89.0
#: weight of Aluminum = 76.0
#: weight of Aluminum = 25.0
#: weight of Aluminum = 34.0
#: weight of Aluminum = 27.0
#: weight of Aluminum = 18.0
#: weight of Aluminum = 81.0
#: Total value = 584.50
#: --- Cardboard ---
#: weight of Cardboard = 96.0
#: weight of Cardboard = 44.0
#: weight of Cardboard = 12.0
#: Total value = 120.08
```

This satisfies the requirement, but it has a classic flaw:
it tests for *every type in the system*.
When cardboard becomes valuable and you add it,
you must hunt down this chain of `isinstance()` checks,
and any you miss will silently drop trash on the floor.
Testing for one type, or a small subset that needs special handling, is fine.
Testing for all of them means you are doing polymorphism's job by hand.

## Let a Dictionary Do the Sorting

Group the pieces in a dictionary keyed by their own type:

```python
# recycle_dict.py
# The Pythonic sort: the object's own type is the key. No type is
# named here, so this code never changes when you add a new kind of
# Trash.
from collections import defaultdict
from parse_trash import parse
from trash import Trash, sum_value

bins: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in parse("trash.dat"):
    bins[type(t)].append(t)  # Bin chosen by the piece itself
for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
#: --- Glass ---
#: weight of Glass = 54.0
#: weight of Glass = 17.0
#: weight of Glass = 11.0
#: weight of Glass = 68.0
#: weight of Glass = 43.0
#: weight of Glass = 63.0
#: weight of Glass = 50.0
#: weight of Glass = 80.0
#: Total value = 88.78
#: --- Paper ---
#: weight of Paper = 22.0
#: weight of Paper = 11.0
#: weight of Paper = 88.0
#: weight of Paper = 91.0
#: Total value = 21.20
#: --- Aluminum ---
#: weight of Aluminum = 89.0
#: weight of Aluminum = 76.0
#: weight of Aluminum = 25.0
#: weight of Aluminum = 34.0
#: weight of Aluminum = 27.0
#: weight of Aluminum = 18.0
#: weight of Aluminum = 81.0
#: Total value = 584.50
#: --- Cardboard ---
#: weight of Cardboard = 96.0
#: weight of Cardboard = 44.0
#: weight of Cardboard = 12.0
#: Total value = 120.08
```

`type(t)` is the perfect key: it adapts to whatever types show up,
even ones added at run time.
There is no chain to maintain and nothing to forget.

## Adding Operations: Visitor, and Why Python Skips It

So far we have changed *types* cheaply.
The other axis of change is adding new *operations*.
Suppose the `Trash` hierarchy is fixed (maybe it ships from a vendor) and you want to add new behaviors to it without editing it:
price it, weigh it, print recycling instructions, and more later.

This is exactly the problem the *Visitor* pattern was invented for.
Visitor is elaborate:
a `Visitor` base class with one `visit()` overload per material,
an `accept()` method added to every element,
and "double dispatch" to route each piece to the right `visit()`.
It exists because languages like Java and C++ dispatch on only one type at a time and cannot add methods to a class from outside.
Python has neither limitation;
the standard library provides `functools.singledispatch` which dispatches on the type of its first argument,
with new types registered from anywhere.

So you do not write Visitor in Python.
You write a single-dispatch function:

```python
# visitor_singledispatch.py
# Visitor's goal is to add operations to a fixed hierarchy from
# outside it. functools.singledispatch does that directly: a
# polymorphic function whose behavior is registered per type. Trash
# is never touched, new operations are independent functions, and
# new types register themselves.
from functools import singledispatch
from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Trash

@singledispatch
def recycling_note(t: Trash) -> str:
    return f"{type(t).__name__}: no special handling"

@recycling_note.register
def _(t: Aluminum) -> str:
    return "Aluminum: crush and bale"

@recycling_note.register
def _(t: Glass) -> str:
    return "Glass: sort by color, then crush"

@recycling_note.register
def _(t: Cardboard) -> str:
    return "Cardboard: flatten and bundle"

seen: set[type[Trash]] = set()
for t in parse("trash.dat"):
    if type(t) not in seen:
        seen.add(type(t))
        print(recycling_note(t))
#: Glass: sort by color, then crush
#: Paper: no special handling
#: Aluminum: crush and bale
#: Cardboard: flatten and bundle
```

`recycling_note()` is a new operation defined entirely outside the `Trash` hierarchy.
`Paper` has no registered note, so it falls through to the base function:
the default behavior, for free.
Adding a `price()` or `weight` operation means writing another single-dispatch function.
Adding a `Plastic` material means defining the class and,
if it needs a special note, registering one line.

Compare this to a Visitor implementation.
There is no `Visitor` class, no `accept()` method bolted onto every material,
and no decorator gymnastics to fake overloading.

When the operation is the *same* for every type,
you do not even need single dispatch.
`sum_value()` earlier was a function.
Use `singledispatch` only when the behavior genuinely differs by type.
For operations that belong on the objects and vary by type,
`singledispatchmethod` does the same thing as a method.

## Summary

Design patterns are about *separating what changes from what stays the same*.
Polymorphism is one way to do that, but it is not the only one.
The deeper skill is spotting the "vector of change" in a problem (here, new types versus new operations) and choosing the lightest construct that isolates it.
In Python that construct is often a language feature, not a multi-class pattern.
The honest measure of a pattern is whether it still earns its keep once the language does part of the work for you.

## Exercises

1.  Add a `Plastic` material with a per-pound value.
    Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,
    and that only `trash.dat` and (optionally) a one-line `recycling_note()` registration do.
2.  Write a `price()` operation as a plain function over a list of `Trash`,
    and a `heaviest()` operation that returns the single heaviest piece.
    Decide for each whether it needs `singledispatch`.
3.  Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
    and explain what changed.
