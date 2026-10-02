# Pattern Refactoring: Solutions

## 1. Adding `Plastic`

> Add a `Plastic` material to `trash.py`,
> then point `recycle_dict.py` at `plastic.dat` and run it.
> Confirm that its sorting loop and `parse_trash.py` need no other changes,
> then account for every pound of plastic that `plastic_dropped.py` loses.
> Which test in `test_trash.py` fails, and why is that failure correct?

```python
# exercise_1.py
from collections import defaultdict
from typing import ClassVar
from record import record

type Bins = dict[type[Trash], list[Trash]]

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return Trash.registry[name](weight)

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Plastic(Trash):
    value: ClassVar[float] = 0.15

def sum_value(items: list[Trash]) -> float:
    return sum(t.weight * t.value for t in items)

items = [Trash.create("Plastic", 10.0),
         Trash.create("Aluminum", 2.0)]
bins: Bins = defaultdict(list)
for t in items:
    bins[type(t)].append(t)
for kind, group in bins.items():
    print(kind.__name__, sum_value(group))
#: Plastic 1.5
#: Aluminum 3.34
```

The `Plastic` class is the only new Python code.
`__init_subclass__()` registers it in `Trash.registry` the moment the
`class` statement runs, so `Trash.create("Plastic", weight)` works
with no further wiring. `recycle_dict.py`'s sorting loop needs no
change because `bins[type(t)].append(t)` keys on the class of each
piece. `Plastic` is a key the dictionary has not seen, and
`defaultdict` creates its bin the way it creates every other. The one
edit to `recycle_dict.py` is the filename, since the script hardcodes
`parse("trash.dat")`. `parse_trash.py` needs no change because it
calls `Trash.create(name, weight)` with a name read from the file and
names no material. One optional step remains: `Plastic` gets a
`@recycling_note.register` function if it needs special handling.

`plastic_dropped.py` parses four pieces and bins two. Its `match` has
no `case` for `Plastic` and no `case _`, so the twenty-pound and
forty-pound pieces fall through and the loop moves on. Sixty pounds
at 0.15 a pound is the `Total value = 9.00` that
`recycle_dict_plastic.py` prints and `plastic_dropped.py` omits. The
report shows no sign of the loss: the two totals it prints are correct
for the pieces they cover.

`test_subclasses_self_register` fails, because it pins the registry to
exactly `{"Aluminum", "Paper", "Glass", "Cardboard"}` and `Plastic` is
now a fifth entry. That failure is correct. The test exists to prove
that defining a subclass registers it, so a new material changes the
set the assertion compares. If the test still passed,
`__init_subclass__()` would have stopped registering subclasses. Once
you update the expected set, the test guards registration again.

## 2. `price()` and `heaviest()`

> Write a `price()` operation as a function over a list of `Trash`,
> and a `heaviest()` operation that returns the single heaviest piece.
> Decide for each whether it needs `singledispatch`.

```python
# exercise_2.py
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return Trash.registry[name](weight)

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Plastic(Trash):
    value: ClassVar[float] = 0.15

items = [Trash.create("Plastic", 10.0),
         Trash.create("Aluminum", 2.0)]

def price(items: list[Trash]) -> float:
    return sum(t.weight * t.value for t in items)

def heaviest(items: list[Trash]) -> Trash:
    return max(items, key=lambda t: t.weight)

print(price(items))
#: 4.84
h = heaviest(items)
print(type(h).__name__, h.weight)
#: Plastic 10.0
```

Neither `price()` nor `heaviest()` needs `singledispatch`. `price()`
reads `t.weight` and `t.value`, and `heaviest()` reads `t.weight`
alone. Every `Trash` subclass carries both attributes, so the same
code runs for `Aluminum`, `Plastic`, or any future material. Both are
in `sum_value()`'s situation: `singledispatch` is for behavior that
differs by type, such as `recycling_note()` giving `Aluminum` and
`Glass` their own wording. When a calculation has the same form for
every type and varies only in the numbers each type carries, write an
ordinary function.

## 3. `recycling_note()` as a `singledispatchmethod`

> Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
> and explain what changed.

```python
# exercise_3.py
from functools import singledispatchmethod
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Paper(Trash):
    value: ClassVar[float] = 0.10

class Glass(Trash):
    value: ClassVar[float] = 0.23

class Cardboard(Trash):
    value: ClassVar[float] = 0.79

class Plastic(Trash):
    value: ClassVar[float] = 0.15

class Sorter:
    @singledispatchmethod
    def recycling_note(self, t: Trash) -> str:
        return f"{type(t).__name__}: no special handling"

    @recycling_note.register
    def _(self, t: Aluminum) -> str:
        return "Aluminum: crush and bale"

    @recycling_note.register
    def _(self, t: Glass) -> str:
        return "Glass: sort by color, then crush"

    @recycling_note.register
    def _(self, t: Cardboard) -> str:
        return "Cardboard: flatten and bundle"

sorter = Sorter()
for cls in Trash.registry.values():
    print(sorter.recycling_note(cls(1.0)))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
#: Plastic: no special handling
```

The dispatch is the same as in the function version:
`singledispatchmethod` routes on the type of the first argument after
`self`. What changes is where the operation lives. `recycling_note()`
is now a method you call as `sorter.recycling_note(t)`. That matters
if `Sorter` holds state of its own (a log of notes issued, a
configuration, statistics) alongside the dispatch. When `Sorter`
carries no such state, as here, the function in `recycling_note.py`
is simpler and does the same job. Use `singledispatchmethod` once the
operation needs a home on an object.

The method form also brings the trap that *Multiple Dispatching*
describes. A subclass of `Sorter` shares this one dispatcher, so a
registration made through the subclass changes `Sorter`'s answers
too.

## 4. Exact-type bins against MRO dispatch

> Derive `CrushedAluminum` from `Aluminum`,
> add it to the data `recycle_dict.py` reads,
> then run `recycle_dict.py` and `recycling_note.py`.
> Explain why `CrushedAluminum` gets its own bin but not its own note.
> Then change `recycle_dict.py` so a subclass shares its parent's bin,
> without naming any material in the sorting loop.

```python
# exercise_4.py
from collections import defaultdict
from functools import singledispatch
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    bin: ClassVar[type[Trash]]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "bin" not in cls.__dict__:
            cls.bin = cls

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class CrushedAluminum(Aluminum):
    value: ClassVar[float] = 1.67
    bin: ClassVar[type[Trash]] = Aluminum

class Glass(Trash):
    value: ClassVar[float] = 0.23

@singledispatch
def recycling_note(t: Trash) -> str:
    return f"{type(t).__name__}: no special handling"

@recycling_note.register
def _(t: Aluminum) -> str:
    return "Aluminum: crush and bale"

pieces: list[Trash] = [
    Aluminum(30.0), CrushedAluminum(20.0), Glass(10.0)]

exact: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    exact[type(t)].append(t)
print(sorted(k.__name__ for k in exact))
#: ['Aluminum', 'CrushedAluminum', 'Glass']

print(recycling_note(CrushedAluminum(1.0)))
#: Aluminum: crush and bale

shared: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    shared[t.bin].append(t)
print(sorted(k.__name__ for k in shared))
#: ['Aluminum', 'Glass']
```

`bins[type(t)]` is a dictionary probe on the exact class, so
`CrushedAluminum` is a key the dictionary has never seen and gets a bin
of its own. `singledispatch` resolves through the MRO instead, finds no
registration for `CrushedAluminum`, and takes `Aluminum`'s. Both
behaviors are deliberate, and neither is a fallback. The sorter must
know exactly what arrived, and the note takes the nearest answer
anyone has written.

To share a parent's bin without naming a material in the loop, choose
your own key instead of accepting `type(t)`. A `bin` class variable
supplies that key: `__init_subclass__()` defaults each class to
itself, so a material that sets no `bin` keeps a bin of its own.
`CrushedAluminum` opts in by setting `bin` to `Aluminum`, and it
restates the `ClassVar` annotation for the reason the chapter's
subclasses restate `value`'s. The sorting loop becomes
`shared[t.bin].append(t)` and still names no material.

`type(t)` is a convenient key, not an inevitable one. A design that
declares its own key can express groupings the type hierarchy leaves
out.

## 5. A base function that refuses to answer

> Define `Plastic`, whose disposal hazard is toxic fumes,
> and leave it out of `disposal_hazard.py`'s registrations.
> What does `hazard()` answer for a piece of plastic?
> Then write `strict_hazard()`,
> whose base function raises `NotImplementedError`,
> and call it on the same piece.
> What does the strict form cost the materials whose hazard is "none"?

```python
# exercise_5.py
from functools import singledispatch
from typing import ClassVar
from exceptions import expect
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Paper(Trash):
    value: ClassVar[float] = 0.10

class Plastic(Trash):
    value: ClassVar[float] = 0.15

@singledispatch
def hazard(t: Trash) -> str:
    return "none"

@hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

print(hazard(Plastic(1.0)))
#: none

@singledispatch
def strict_hazard(t: Trash) -> str:
    raise NotImplementedError(
        f"no hazard rule for {type(t).__name__}")

@strict_hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

@strict_hazard.register
def _(t: Paper) -> str:
    return "none"

print(strict_hazard(Paper(1.0)))
#: none
expect(NotImplementedError, strict_hazard, Plastic(1.0))
#: [NotImplementedError] no hazard rule for Plastic
```

`hazard()` answers "none" for the plastic. That answer is wrong and
looks like every correct "none" beside it. The forgotten registration
produces no exception and no report from the type checker.
`strict_hazard()` raises a `NotImplementedError` that names the
material at the first call.

The strict form costs one registration for every material, including
each one whose answer is "none": `Paper` needs three lines to say what
`hazard()`'s base function answered without a registration. Choose by which mistake costs more. A
default is right when it is a true answer for most types and a
forgotten registration does little harm. A base function that raises
an exception is right when a wrong answer is worse than a stopped
program, as it is for a safety report.
