# Pattern Refactoring

This chapter follows one problem through several designs.
A first solution solves it, then we ask "what will change?" and reshape the design to absorb that change cheaply.
This is the spirit of Martin Fowler's *Refactoring*, applied to patterns rather than single statements.

It is also a Python lesson.
Many patterns in *GoF Design Patterns* work around the limitations of statically typed languages without multiple dispatch.
Python lacks those limitations, so some of those patterns become unnecessary.
We will point that out as it happens.

The example is a trash sorting simulation, and it evolves across the chapter:
an initial solution, then successive redesigns as new requirements appear.
Read that evolution as a template for your own designs,
which can start as an adequate fit for one problem and grow into a flexible fit for a class of problems.

## Simulating a Trash Recycler

Trash arrives at the recycling plant mixed together.
The program must sort it by material and report the total value of each kind.
The trash starts out as an undifferentiated pile,
and you must recover the type of each piece to sort it.

In the `Trash` hierarchy, each material carries a per-pound `value`.
The base class keeps a `registry` of its subclasses,
filled automatically by `__init_subclass__()`,
and a `create()` method builds an instance from a material name (this is a [Factory](28_Factory.md)):

![Each Trash subclass registers itself, and sorting keys the bins dict by type(t) instead of naming any material](_images/trash_sorter)

```python
# trash.py
from typing import ClassVar

type Bins = dict[type[Trash], list[Trash]]

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

Python implicitly makes `__init_subclass__` a classmethod, so `cls` doesn't need an `@classmethod` decorator.
It runs once per subclass, right after Python creates that subclass, so each one can register itself in `Trash.registry` automatically.

Each subclass's `value = ...` line creates its own class attribute, separate from `Trash.value`.
The `ClassVar` annotation just tells type checkers it belongs to the class rather than an instance. It doesn't share storage across subclasses.

None of the subclasses redeclare `value: ClassVar[float]`.
They don't need to because the checker resolves `value` through the MRO and finds it already declared `ClassVar[float]` on `Trash`.
It treats each subclass's assignment as filling in that same classvar rather than introducing a new one.

Adding a new recyclable type is a single class definition.
It registers itself, and `create()` can build it.
`sum_value()` is an ordinary function.
It relies on polymorphism (`t.value`, `t.weight`) and never asks what type each piece is.

We test that each subclass registers itself,
`create()` builds one by name, the per-pound values are right,
and `sum_value()` totals weight times value:

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

A data file describes the trash to process,
one `Name:weight` line per piece:

```text
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

Testing parses a small file written on the spot, so it does not depend on `trash.dat`:

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

The most obvious way to sort is to look at each piece and discover its type using `match`:

```python
# recycle_rtti.py
from collections import defaultdict
from parse_trash import parse
from trash import Aluminum, Bins, Cardboard, Glass, Paper, sum_value

bins: Bins = defaultdict(list)
for t in parse("trash.dat"):
    match t:
        case Aluminum():
            bins[Aluminum].append(t)
        case Paper():
            bins[Paper].append(t)
        case Glass():
            bins[Glass].append(t)
        case Cardboard():
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

This satisfies the requirement, but it has a classic flaw.
It tests for *every type in the system*.
When cardboard becomes valuable and you add it,
you must find any `case` statements that look for specific types.
Any you miss will silently drop trash on the floor.
Testing for one type, or a small subset that needs special handling, is fine.
Testing for all of them means you are doing polymorphism's job by hand.

## Let a Dictionary Do the Sorting

We can use a dictionary keyed by type:

```python
# recycle_dict.py
from collections import defaultdict
from parse_trash import parse
from trash import Bins, sum_value

bins: Bins = defaultdict(list)

for t in parse("trash.dat"):
    bins[type(t)].append(t)  # Bin chosen by the trash piece

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

`type(t)` is the perfect key because it adapts to new types,
even ones added at runtime.
There is nothing to maintain or forget.

## Adding Operations: Visitor, and Why Python Skips It

So far we have changed *types* cheaply.
The other axis of change is adding new *operations*.
Suppose the `Trash` hierarchy is fixed (maybe it ships from a vendor) and you want to add new behaviors to it without editing it:
price it, weigh it, print recycling instructions, and more later.

[Visitor](33_Visitor.md) solves this problem.
Visitor is elaborate:
a `Visitor` base class with one `visit()` overload per material,
an `accept()` method added to every element,
and *double dispatch* to route each piece to the right `visit()`.
It exists because languages like Java and C++ dispatch on only one type at a time and cannot add methods to a class from outside.
Python has neither limitation.
The standard library provides `functools.singledispatch` which dispatches on the type of its first argument,
with new types registered from anywhere.

In Python, a single-dispatch function implements *Visitor*:

```python
# recycling_note.py
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

Each implementation above is named `_`, a throwaway name
[Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch) explains.
`recycling_note()` is a new operation defined entirely outside the `Trash` hierarchy.
`Paper` has no registered note, so it falls through to the base function and performs the default behavior.
Adding a `price()` or `weight()` operation means writing another single-dispatch function.
Adding a `Plastic` material means defining the class and,
if it needs a special note, registering one line.

Compare this to a Visitor implementation.
There is no `Visitor` class, no `accept()` method bolted onto every material,
and no decorator gymnastics to fake overloading.

When the operation is the same for every type,
you do not even need single dispatch.
`sum_value()` earlier was a function.
Use `singledispatch` only when the behavior genuinely differs by type.
For operations that belong on the objects and vary by type,
`singledispatchmethod` does the same thing as a method.

## Choosing the Lightest Construct

Design patterns are about *separating things that change from things that stay the same*.
Polymorphism is one way to do that, but it is not the only one.
The deeper skill is spotting the *vector of change* in a problem (here, new types versus new operations) and choosing the lightest construct that isolates it.
In Python that construct is often a language feature, not a multi-class pattern.
The honest measure of a pattern is whether it is still useful once the language does part of the work for you.

## Exercises

1.  Add a `Plastic` material with a per-pound value.
    Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,
    and that only `trash.dat` and (optionally) a one-line `recycling_note()` registration do.
2.  Write a `price()` operation as a plain function over a list of `Trash`,
    and a `heaviest()` operation that returns the single heaviest piece.
    Decide for each whether it needs `singledispatch`.
3.  Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
    and explain what changed.
