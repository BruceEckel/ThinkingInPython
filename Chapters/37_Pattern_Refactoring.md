# Pattern Refactoring

This chapter follows one problem through several designs.
A first solution solves it,
then you ask "what will change?" and reshape the design to absorb that change cheaply.
This is the spirit of Martin Fowler's *Refactoring*,
applied to patterns rather than single statements.

It is also a Python lesson.
Many patterns in *GoF Design Patterns* work around the limitations of statically typed languages:
single dispatch, closed classes, and types that are not values.
Python lacks those limitations, so some of those patterns become unnecessary.
This chapter points out each one as the example reaches it.

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
which `__init_subclass__()` fills automatically,
and a `create()` method builds an instance from a material name
(this is a [Factory](27_Factory.md#the-pythonic-factory-a-dictionary)):

![Each Trash subclass registers itself, and sorting keys the bins dict by type(t) instead of naming any material](_images/trash_sorter)

```python
# trash.py
from dataclasses import dataclass
from typing import ClassVar

type Bins = dict[type[Trash], list[Trash]]

@dataclass(frozen=True)
class Trash:
    weight: float
    # Dollars per pound (per subclass)
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return cls.registry[name](weight)

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

`Bins` names the shape the sorting sections use,
a dictionary from a material's class to the pieces made of that material.
A `type` statement's right side evaluates lazily,
so the alias can name `Trash` several lines before the `class` statement that defines it
(see [The `type` Statement](08_Static_Typing.md#the-type-statement)).

Python implicitly makes `__init_subclass__()` a classmethod,
so it needs no `@classmethod` decorator and its first parameter is the new subclass.
It runs once per subclass, immediately after Python creates that subclass,
so each one can register itself in `Trash.registry` automatically.

`@dataclass` builds `__init__()` from the bare `weight: float` annotation alone:
the two `ClassVar` attributes belong to the class, so they stay out of it
([Data Classes as Types](12_Data_Classes_as_Types.md#d-a-real-classvar)).
Each subclass's `value = ...` line creates its own class attribute,
separate from `Trash.value`, sharing no storage with its siblings,
and none of them restates the annotation:
a subclass inherits the declaration along with the name
([Class Attributes](09_Class_Attributes.md#classvar-and-inheritance)).

Adding a new recyclable type is a single class definition.
It registers itself, and `create()` builds it.
`sum_value()` is an ordinary function.
It reads `t.value` and `t.weight` polymorphically,
and uses the type only to label the printed line, never to decide what to do.

The tests confirm that each subclass registers itself,
`create()` builds one by name, the per-pound values are correct,
and `sum_value()` totals weight times value:

```python
# test_trash.py
import pytest
from trash import (Aluminum, Cardboard, Glass, Paper,
                   Trash, sum_value)

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
    # 2*1.67 + 5*0.10
    assert sum_value(items) == pytest.approx(3.84)
```

A data file describes the trash to process, one `Name:weight` line per piece:

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
If you add a new kind of trash, the parser keeps working unchanged:

```python
# parse_trash.py
from pathlib import Path
from trash import Trash

def parse(filename: str | Path) -> list[Trash]:
    items: list[Trash] = []
    for line in Path(filename).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, weight = line.split(":")
        items.append(
            Trash.create(name.strip(), float(weight)))
    return items
```

The test parses a small in-memory file, so it does not depend on `trash.dat`:

```python
# test_parse_trash.py
from pathlib import Path
from parse_trash import parse

def test_parse_reads_and_skips_comments(
    tmp_path: Path,
) -> None:
    data = tmp_path / "trash.dat"
    data.write_text("""\
# header
Aluminum:2.0

Glass:3.0
""")
    items = parse(data)
    assert [type(t).__name__ for t in items] == [
        "Aluminum", "Glass"]
    assert items[0].weight == 2.0
    assert items[1].weight == 3.0
```

## The First Cut: Checking Every Type

The most obvious way to sort is to look at each piece and discover its type using `match`
(the `rtti` in the file name is *run-time type identification*, the C++ name for discovering a type at runtime):

```python
# recycle_rtti.py
from collections import defaultdict
from parse_trash import parse
from trash import (Aluminum, Bins, Cardboard, Glass,
                   Paper, sum_value)

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

`recycle_rtti.py` satisfies the requirement, but it has a classic flaw.
It tests for every type in the system.
When a new material joins the system, say `Plastic`,
you must find every `case` statement that enumerates specific types.
Each one you miss silently drops trash on the floor.
Readers of [Composite and Interpreter](34_Composite_and_Interpreter.md)
may expect `assert_never()` to make the type checker catch the missed case,
and here it cannot help: exhaustiveness checking needs a *closed* union,
and `Trash` is deliberately open, which is the point of the registry,
so no type checker can know the set is complete.
This is a `match` over an open set,
which [Pattern Matching](13_Pattern_Matching.md#when-not-to-match)
warns against.
When the set is open, sorting must not enumerate it,
and the next section shows a sorter that doesn't.
Testing for one type, or a small subset that needs special handling, is fine.
Testing for all of them means you do dispatch's job by hand.

That is the argument.
Here is the requirement that makes it concrete.
The plant starts accepting plastic,
which arrives as a new material class and some new lines in the data:

```text
# plastic.dat
Glass:10
Plastic:20
Aluminum:30
Plastic:40
```

```python
# plastic_dropped.py
from collections import defaultdict
from parse_trash import parse
from trash import (
    Aluminum,
    Bins,
    Cardboard,
    Glass,
    Paper,
    Trash,
    sum_value,
)

class Plastic(Trash):
    value = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for t in pieces:
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
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: --- Glass ---
#: weight of Glass = 10.0
#: Total value = 2.30
#: --- Aluminum ---
#: weight of Aluminum = 30.0
#: Total value = 50.10
#: parsed 4, binned 2
```

Nothing failed.
The parser built two `Plastic` objects, the sorter matched neither,
and the report totals the trash it recognized.
Two of four pieces reached a bin,
and the sixty pounds of plastic left no trace in any total on which the plant acts.
"Silently drop trash on the floor" means a number that is wrong and looks right,
not an exception to debug.
The registry is not the leak:
it accepted `Plastic` the moment the `class` statement ran,
and had the class been missing,
`create()` would have raised a `KeyError` at the first `Plastic:` line,
a loud failure at parse time.
Only the `match` loses trash silently.

## Let a Dictionary Do the Sorting

You can use a dictionary keyed by type:

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
including ones added at runtime.
Nothing needs maintaining, and nothing gets forgotten.
The key is the *exact* class,
the same dictionary-probe dispatch as the tables in [State Machines](31_State_Machines.md#the-engine)
and [Multiple Dispatching](32_Multiple_Dispatching.md),
and it first appeared in [Function Objects](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type)'s event bus.
If you derive `CrushedAluminum` from `Aluminum`,
it sorts into its own bin rather than its parent's: usually what a sorter needs,
but keep it in mind before you subclass a material.
This is the one place where the two versions disagree:
`case Aluminum()` matches any subclass,
so `recycle_rtti.py` files a `CrushedAluminum` under `Aluminum`.
Swapping the `match` for the dictionary is a redesign, not a rename.

The `defaultdict(list)` creates a bin the first time a material turns up.
`Bins` is an alias for a plain `dict`,
so a type checker accepts `bins: Bins = {}` just as happily,
and that version raises `KeyError` on the first piece of trash.

## Adding Operations: Visitor, and Why Python Skips It

So far the chapter has made new *types* cheap.
The other axis of change is adding new *operations*,
and the two ordinarily pull against each other:
that trade is the expression problem from [Pattern Matching](13_Pattern_Matching.md#dynamic-binding-vs.-pattern-matching).
`Trash` should not grow a method for every question the plant learns to ask.
Recycling instructions, disposal hazards,
and transport volume are all operations that vary by material,
and none of them belongs in `trash.py`.
[Visitor](33_Visitor.md) is the classic way to add them from outside,
and it is elaborate.
In its C++ and Java form a `Visitor` base class declares one overload per material,
every element grows an `accept()` method,
and *double dispatch* routes each piece to the correct overload.
Python has no method overloading, so even writing that down takes work
(that chapter shows the shape on which the book's version settles).
Visitor exists because languages like Java and C++ dispatch on only one type at a time and cannot add methods to a class from outside.
Python has neither limitation.
The standard library provides `functools.singledispatch`,
which dispatches on the type of its first argument,
and any module can register a new type.

In Python, a single-dispatch function implements *Visitor*:

```python
# recycling_note.py
from functools import singledispatch
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

for cls in Trash.registry.values():
    print(recycling_note(cls(1.0)))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
```

Each implementation above takes the name `_`.
[Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch)
explains that placeholder.
`recycling_note()` is a new operation that lives outside the `Trash` hierarchy.
`Paper` has no registered note, so it falls through to the base function.
That fallback is also the risk:
a material nobody registers gets the default answer,
with no exception at runtime and no complaint from the type checker.
Here "no special handling" is a genuine answer, so the fallback earns its keep;
when no default makes sense,
that chapter advises making the base function raise `NotImplementedError`,
so a forgotten registration fails at the first call.
Adding another operation that varies by material means writing another single-dispatch function.
Adding a `Plastic` material means defining the class,
plus one registration for each operation that must answer differently for plastic.
Python does not escape the expression problem.
It makes both sides of it cost a line instead of an edit spread across classes.

Compare this to that classic form: no `Visitor` class exists,
no `accept()` method bolted onto every material,
and no second dispatch to arrange.

The chapter now holds two kinds of dispatch that disagree about subclasses.
`bins[type(t)]` keys on the exact class,
so a `CrushedAluminum` derived from `Aluminum` gets a bin of its own.
`singledispatch` resolves through the MRO,
so that same piece answers with `Aluminum`'s note.
Neither is wrong for its job,
and the difference is the one [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
draws between a table keyed by class and dispatch that follows inheritance.

When the operation is the same for every type, you do not need single dispatch.
The earlier `sum_value()` is an ordinary function.
Use `singledispatch` only when the behavior differs by type.
For an operation that belongs on an object and still varies by type,
`functools.singledispatchmethod` provides the same dispatch in method form.

## Choosing the Lightest Construct

Design patterns are about separating things that change from things that stay the same.
Polymorphism is one way to do that, but it is not the only one.
The deeper skill is spotting the *vector of change*
([The Pattern Concept](21_The_Pattern_Concept.md#what-is-a-pattern))
in a problem (here, new types versus new operations)
and choosing the lightest construct that isolates it.
This chapter discovered its two vectors one requirement at a time,
rather than predicting them up front,
and each ended up costing a single line at the point of use:
`bins[type(t)]` absorbs a new material,
and one `@recycling_note.register` absorbs a new operation.
Neither is a pattern in the *GoF* sense.
In Python the lightest construct is often a language feature,
not a multi-class pattern,
and a pattern is worth keeping only when it is still useful once the language does part of the work.

## Exercises

1.  Add the `Plastic` material and its `plastic.dat` lines to `recycle_dict.py`.
    Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,
    then account for every pound of plastic that `plastic_dropped.py` loses.
    Which test in `test_trash.py` fails, and why is that failure correct?
2.  Write a `price()` operation as a function over a list of `Trash`,
    and a `heaviest()` operation that returns the single heaviest piece.
    Decide for each whether it needs `singledispatch`.
3.  Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
    and explain what changed.
4.  Derive `CrushedAluminum` from `Aluminum` and run both `recycle_dict.py` and `recycling_note.py` over data containing it.
    Explain why it gets its own bin but not its own note.
    Then change `recycle_dict.py` so a subclass shares its parent's bin,
    without naming any material in the sorting loop.
