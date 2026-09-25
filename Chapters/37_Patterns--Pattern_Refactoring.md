# Pattern Refactoring

This chapter follows one problem through several designs.
A first solution solves it,
then you ask "what will change?" and reshape the design so that kind of change touches one place.
This is Martin Fowler's *Refactoring*,
applied to patterns rather than single statements.

It is also a Python lesson.
Many patterns in *GoF Design Patterns* work around the limitations of statically typed languages:
single dispatch, closed classes, and types that are not values.
Python's classes stay open, its types are values,
and `functools.singledispatch` adds an operation from outside a class,
so some of those patterns become unnecessary.
This chapter names each one at the point where the example would otherwise need it.

The example is a trash sorting simulation, and it evolves across the chapter:
one design, then a requirement that makes it report wrong totals,
then a reshaping that absorbs the change,
then a second axis of change that the reshaped design leaves unsolved.
Read that evolution as a template for your own designs,
which can start as an adequate fit for one problem and become a flexible fit for a class of problems.

## Simulating a Trash Recycler

Trash arrives at the recycling plant mixed together.
The program must sort it by material and report the total value of each kind.
The trash starts out as an undifferentiated pile,
and you must recover the type of each piece to sort it.

### The `Trash` Hierarchy

In the `Trash` hierarchy, each material class declares a per-pound `value`.
The base class keeps a `registry` of its subclasses,
which `__init_subclass__()` fills automatically.
Its `create()` method is the [dictionary factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary):
it builds an instance from a material name.

![Each Trash subclass registers itself, and each bin takes a class as its key](_images/trash_sorter)

```python
# trash.py
from typing import ClassVar
from record import record

type Bins = dict[type[Trash], list[Trash]]

@record
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
    total = sum(t.weight * t.value for t in items)
    print(f"Total value = {total:.2f}")
    return total
```

`Bins` names the shape the sorting sections use,
a dictionary from a material's class to the pieces made of that material.
[The `type` Statement](08_Foundations--Static_Types.md#the-type-statement)
introduces this alias form.
A `type` statement's right side evaluates lazily,
so the alias can name `Trash` several lines before the `class` statement that defines it.

Python implicitly makes [`__init_subclass__()`](17_Techniques--Metaprogramming.md#self-registration-of-subclasses)
a classmethod, so it needs no `@classmethod` decorator and its first parameter is the new subclass.
It runs once per subclass, immediately after Python creates that subclass,
so each one can register itself in `Trash.registry` automatically.
`create()` is a class method reading `cls.registry`.
[Factory](27_Patterns--Factory.md#hazards-of-self-registration)
warns that this form can mislead:
`Aluminum.create("Paper", 1.0)` is legal and returns a `Paper`.
The lookup is safe here.
Every subclass writes to `Trash.registry` and none defines a `registry` of its own,
so `cls.registry` always resolves to that one table.
Call it as `Trash.create()`.

`@record` builds `__init__()` from the bare `weight: float` annotation alone:
the two [`ClassVar` attributes](12_Techniques--Data_Classes_as_Types.md#d-a-real-classvar)
belong to the class, so they stay out of it.
Each subclass's `value = ...` line creates a class attribute of its own,
separate from `Trash.value` and from its siblings'.
A subclass's bare `value = 1.67` inherits the name and its type from the base declaration,
but not the type checker's guard:
`ty` rejects `Trash(1.0).value = 2.0` and accepts `Aluminum(1.0).value = 2.0`.
Restating `ClassVar[float]` on the override [keeps that check](09_Foundations--Class_Attributes.md#classvar-and-inheritance).

A new recyclable type costs one class definition.
It registers itself, and `create()` builds it.
`sum_value()` is an ordinary function.
It reads `t.value` and `t.weight` polymorphically,
and never checks what type a piece is.

Testing confirms that each subclass registers itself,
`create()` builds one by name,
and `sum_value()` totals weight times the per-pound value:

```python
# test_trash.py
import pytest
from trash import Aluminum, Paper, Trash, sum_value

def test_subclasses_self_register() -> None:
    assert set(Trash.registry) == {
        "Aluminum", "Paper", "Glass", "Cardboard"}

def test_create_builds_by_name() -> None:
    t = Trash.create("Aluminum", 2.0)
    assert isinstance(t, Aluminum)
    assert t.weight == 2.0

def test_sum_value_totals_weight_times_value() -> None:
    items: list[Trash] = [Aluminum(2.0), Paper(5.0)]
    # 2*1.67 + 5*0.10
    assert sum_value(items) == pytest.approx(3.84)
```

### The Data File and Its Parser

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

The parser builds `Trash` objects through the registry,
so it never names a concrete material.
A new kind of trash leaves the parser unchanged:

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

The test parses a small temporary file, so it runs without `trash.dat`:

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

The most obvious way to sort is to test each piece for its type using `match`
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
#: Total value = 88.78
#: --- Paper ---
#: Total value = 21.20
#: --- Aluminum ---
#: Total value = 584.50
#: --- Cardboard ---
#: Total value = 120.08
```

`recycle_rtti.py` satisfies the requirement, but it has a classic flaw.
It tests for every type in the system.
When a new material joins the system, say `Plastic`,
you must find every `case` statement that enumerates specific types.
Each one you miss silently drops trash on the floor.
Readers of [*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md)
may expect `assert_never()` to make the type checker report the missed case.
Exhaustiveness checking needs a *closed* union to compare the cases against,
but `Trash` is deliberately open.
The registry exists to accept new subclasses.
This `match` runs over an open set,
which [Pattern Matching](13_Techniques--Pattern_Matching.md#when-not-to-match)
warns against.
A sorter over an open set must let each piece choose its own bin.
The next section builds one.
Testing for one type, or a small subset that needs special handling, is fine.
Testing for all of them means you write the type-to-bin lookup by hand.
A `case _:` wildcard could catch a new material:
`case _: raise ValueError(f"unsorted {type(t).__name__}")` turns the silent drop into a `ValueError`.
The wildcard is worth adding, and the flaw remains.
Every new material means editing this `match`,
where the next section's `bins[type(t)]` needs no edit at all.

That is the argument.
Here is the requirement that makes it concrete.
The plant starts accepting plastic,
which means a new material class and some new lines in the data:

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
#: Total value = 2.30
#: --- Aluminum ---
#: Total value = 50.10
#: parsed 4, binned 2
```

Nothing fails.
The parser builds two `Plastic` objects, the `match` lets both fall through,
and the report totals the trash it recognized.
The loop appends two of the four pieces to a bin,
so the sixty pounds of plastic vanish from the totals the plant uses.
"Silently drop trash on the floor" means a number that is wrong and looks right,
not an exception to debug.
The `match` is the statement that loses them.
`__init_subclass__()` registers `Plastic` the moment its `class` statement runs.
Without that `class` statement,
`create()` raises a `KeyError` at the first `Plastic:` line, loudly,
at parse time.
The `match` alone loses trash silently.

## Let a Dictionary Do the Sorting

A dictionary keyed by type replaces the `match`:

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
#: Total value = 88.78
#: --- Paper ---
#: Total value = 21.20
#: --- Aluminum ---
#: Total value = 584.50
#: --- Cardboard ---
#: Total value = 120.08
```

`type(t)` is the right key because every new class is a new key,
including one defined at runtime.
The loop has no list of materials to maintain and no case to forget.
The key is the *exact* class.
That is the same dictionary-probe dispatch as the tables in [State Machines](31_Patterns--State_Machines.md#the-engine)
and [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table).
It first appeared in the event bus in [Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type).
If you derive `CrushedAluminum` from `Aluminum`,
it sorts into its own bin rather than its parent's.
That is usually what a sorter needs,
but keep it in mind before you subclass a material.
Subclasses are another place where the two sorters differ:
`case Aluminum()` matches any subclass,
so `recycle_rtti.py` puts a `CrushedAluminum` in the `Aluminum` bin.
Swapping the `match` for the dictionary is a redesign, not a rename.

The `defaultdict(list)` creates a bin the first time the loop reads a piece of that material.
`Bins` is an alias for a plain `dict`,
so a type checker accepts `bins: Bins = {}` too.
That version raises a `KeyError` on the first piece of trash.

Point this sorter at `plastic.dat`,
the file whose plastic `plastic_dropped.py` drops.
The listing defines `Plastic` the same way `plastic_dropped.py` does:

```python
# recycle_dict_plastic.py
from collections import defaultdict
from parse_trash import parse
from trash import Bins, Trash, sum_value

class Plastic(Trash):
    value = 0.15

pieces = parse("plastic.dat")
bins: Bins = defaultdict(list)
for t in pieces:
    bins[type(t)].append(t)  # Bin chosen by the trash piece

for kind, items in bins.items():
    print(f"--- {kind.__name__} ---")
    sum_value(items)
binned = sum(len(v) for v in bins.values())
print(f"parsed {len(pieces)}, binned {binned}")
#: --- Glass ---
#: Total value = 2.30
#: --- Plastic ---
#: Total value = 9.00
#: --- Aluminum ---
#: Total value = 50.10
#: parsed 4, binned 4
```

The loop bins every piece, plastic included: `parsed 4, binned 4`.
The program changed in two places:
the `Plastic` definition and the data file's name.
The sorting line, `bins[type(t)].append(t)`,
reads the same as in `recycle_dict.py`,
while the `match` in `recycle_rtti.py` and `plastic_dropped.py` would need a new `case`.

## Adding Operations: Visitor, and Why Python Skips It

So far a new *type* has cost one class definition and no other edit.
The other axis of change is adding new *operations*.
A design that adds a type without editing existing code ordinarily adds an operation only by editing every type.
That trade is the [expression problem](13_Techniques--Pattern_Matching.md#the-expression-problem).

### A Method on Every Material

Here is the requirement that makes the second axis concrete.
The plant already prints a recycling instruction for each material.
Now the safety officer wants a disposal hazard printed beside it.
That is a second operation that varies by material.
The obvious place for it is a method on each material class:

```python
# note_methods.py
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0

    def note(self) -> str:
        return f"{type(self).__name__}: nothing special"

    # New requirement, so a new method here
    def hazard(self) -> str:
        return "none"

class Aluminum(Trash):
    value = 1.67

    def note(self) -> str:
        return "Aluminum: crush and bale"

    def hazard(self) -> str:
        return "sharp edges"

class Glass(Trash):
    value = 0.23

    def note(self) -> str:
        return "Glass: sort by color, then crush"

    def hazard(self) -> str:
        return "sharp edges"

class Cardboard(Trash):
    value = 0.79

    def note(self) -> str:
        return "Cardboard: flatten and bundle"

    def hazard(self) -> str:
        return "none"

materials = [Aluminum, Glass, Cardboard]
for cls in materials:
    t = cls(1.0)
    print(f"{t.note()} | hazard: {t.hazard()}")
edited = [c for c in materials if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: Aluminum: crush and bale | hazard: sharp edges
#: Glass: sort by color, then crush | hazard: sharp edges
#: Cardboard: flatten and bundle | hazard: none
#: classes edited for one operation: 3
```

Both operations answer correctly, and the last line counts the edits.
One new question is an edit to all three material classes,
and the question after it is three more edits.
Those edits sit in each class body, as `note_methods.py` shows;
in the real program they go in `trash.py`.
A method belongs in the body of its own class by design.
You can assign a function onto a class from outside,
but a reader of the class then has to search every module for the behavior assigned onto it.
A plant that buys its material classes from a supplier has no class body to edit.

The method form is a real option, not an example built to fail.
This hierarchy is small and the book owns every subclass,
so `note()` on each material is a fair choice here.
The method is the better choice while you own the hierarchy and the operations stay few:
each subclass defines its own answer,
with no separate table to keep in step with the class list.
It is the worse choice once the hierarchy belongs to someone else,
or once operations start to outnumber materials.

### One `singledispatch` Function per Operation

[*Visitor*](33_Patterns--Visitor.md)
is the classic way to add an operation without editing the classes.
It is elaborate: a visitor class, an `accept()` method on every element,
and double dispatch to select the right overload,
all to work around a language that cannot add a method to a class from outside.
`functools.singledispatch` selects the same implementation in one call.
Any module can register an implementation for a new type.

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
[*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
explains that placeholder.
`recycling_note()` is a new operation defined outside the `Trash` hierarchy.
Three materials register a note, and `Paper`, the fourth,
falls through to the base function.
That fallback is also the risk: a forgotten material gets the default answer,
with no exception at runtime and no report from the type checker.
Here "no special handling" is a genuine answer for `Paper`,
so the fallback is correct.
When every material needs an answer of its own,
the *Visitor* chapter advises making the base function raise `NotImplementedError`,
so a forgotten registration fails at the first call.

Now write the safety officer's question the same way.
It goes in its own file, and edits no material class:

```python
# disposal_hazard.py
from functools import singledispatch
from trash import Aluminum, Glass, Trash

@singledispatch
def hazard(t: Trash) -> str:
    return "none"

@hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

@hazard.register
def _(t: Glass) -> str:
    return "sharp edges"

for cls in Trash.registry.values():
    print(f"{cls.__name__}: {hazard(cls(1.0))}")
edited = [c for c in Trash.registry.values()
          if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: Aluminum: sharp edges
#: Paper: none
#: Glass: sharp edges
#: Cardboard: none
#: classes edited for one operation: 0
```

The counter reads zero.
The loop reads every material from the registry, `hazard()` answers for each,
and `trash.py` stays untouched.
A third question and a fourth are one more file each,
where `note_methods.py` needs one edit per material every time.
Adding a `Plastic` material means defining the class,
plus one registration for each operation that must answer differently for plastic.
Python still has the expression problem,
but each side is now one line instead of an edit spread across classes.

`singledispatch` is for behavior that differs by type.
The earlier `sum_value()` does the same thing for every type,
so it stays an ordinary function.
For an operation that belongs on an object and still varies by type,
[`functools.singledispatchmethod`](41_Functional--Toolkits.md#singledispatchmethod)
provides the same dispatch in method form.

The chapter now holds two kinds of dispatch that treat subclasses differently.
`bins[type(t)]` keys on the exact class,
so a `CrushedAluminum` derived from `Aluminum` gets a bin of its own.
`singledispatch` resolves through the [MRO](07_Foundations--Classes.md#method-resolution-order),
so `recycling_note()` returns `Aluminum`'s note for that same piece.
Each is right for its job.
[*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-type-or-many)
draws the same distinction between a table keyed by class and dispatch that follows inheritance.

## Choosing the Lightest Construct

Design patterns are about separating things that change from things that stay the same.
Polymorphism is one way to do that;
this chapter used a dictionary keyed by type and a `singledispatch` function.
The deeper skill is spotting the [*vector of change*](21_Patterns--Design_Patterns.md#the-vector-of-change)
and choosing the lightest construct that isolates it.
This chapter met two vectors through a concrete requirement each:
plastic for new types, and the disposal hazard for new operations.
Each vector now lands in one place: `bins[type(t)]` absorbs a new material,
one `@recycling_note.register` adds that material's answer to an existing operation,
and a new operation is one `singledispatch` function in its own file.
None of the three is a pattern in the GoF sense.
In Python the lightest construct is often a language feature,
not a multi-class pattern.
Keep a pattern where it does more than a language feature does.

## Exercises

1.  Add a `Plastic` material to `trash.py`,
    then point `recycle_dict.py` at `plastic.dat` and run it.
    Confirm that its sorting loop and `parse_trash.py` need no other changes,
    then account for every pound of plastic that `plastic_dropped.py` loses.
    Which test in `test_trash.py` fails, and why is that failure correct?
2.  Write a `price()` operation as a function over a list of `Trash`,
    and a `heaviest()` operation that returns the single heaviest piece.
    Decide for each whether it needs `singledispatch`.
3.  Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
    and explain what changed.
4.  Derive `CrushedAluminum` from `Aluminum`,
    add it to the data `recycle_dict.py` reads,
    then run that and `recycling_note.py`.
    Explain why it gets its own bin but not its own note.
    Then change `recycle_dict.py` so a subclass shares its parent's bin,
    without naming any material in the sorting loop.
