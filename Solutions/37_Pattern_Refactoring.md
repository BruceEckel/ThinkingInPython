# Pattern Refactoring: Solutions

## 1. Adding `Plastic`

```python
# exercise_1.py
from collections import defaultdict
from typing import ClassVar

type Bins = dict[type[Trash], list[Trash]]

class Trash:
    value: ClassVar[float] = 0.0
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

class Plastic(Trash):
    value = 0.15

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

That is the entire change to Python code. `__init_subclass__()`
registers `Plastic` in `Trash.registry` automatically, the moment the
class is defined, so `Trash.create("Plastic", weight)` works with no
further wiring. `recycle_dict.py` needs no change because
`bins[type(t)].append(t)` keys on whatever type `t` actually is;
`type(t)` for a piece of `Plastic` is simply `Plastic`, a key the
dictionary has never seen before, which `defaultdict` handles the same
way it handles every other new key. `parse_trash.py` needs no change
because it only ever calls `Trash.create(name, weight)` with a name
string read from the file; it never names a concrete material itself.
The only files that change are the data (adding `Plastic:NN` lines)
and, if `Plastic` deserves special handling, one
`@recycling_note.register` function.

Accounting for the plastic in `plastic_dropped.py` is the other half.
It parses four pieces and bins two, so twenty and forty pounds of
plastic are missing from every total the report prints. No `case`
matches a `Plastic`, and the `match` has no `case _`, so the loop body
runs zero times for those pieces and the program continues. The plant
gets a report that balances against nothing.

`test_subclasses_self_register` is the test that fails, because it pins
the registry to exactly `{"Aluminum", "Paper", "Glass", "Cardboard"}`
and `Plastic` is now a fifth entry. That failure is correct behavior
for it. The test exists to prove that defining a subclass registers it,
so a new material *should* move the assertion; a test that passed here
would mean `__init_subclass__()` had stopped doing its job. Update the
expected set and the test goes back to guarding what it was written to
guard.

## 2. `price()` and `heaviest()`

```python
# exercise_2.py
from typing import ClassVar

class Trash:
    value: ClassVar[float] = 0.0
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

class Plastic(Trash):
    value = 0.15

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

Neither needs `singledispatch`. Both read only `t.weight` and
`t.value`, attributes every `Trash` subclass already carries through
ordinary polymorphism, so the same code runs unchanged for `Aluminum`,
`Glass`, `Plastic`, or any future material. This is exactly
`sum_value()`'s situation: `singledispatch` earns its place only when
the behavior genuinely differs *by type*, such as `recycling_note()`
giving `Aluminum` and `Glass` their own wording. A calculation that is
identical in shape for every type, varying only in the numbers each
type happens to carry, is a plain function, full stop.

## 3. `recycling_note()` as a `singledispatchmethod`

```python
# exercise_3.py
from functools import singledispatchmethod
from typing import ClassVar

class Trash:
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

class Aluminum(Trash):
    value = 1.67

class Paper(Trash):
    value = 0.10

class Glass(Trash):
    value = 0.23

class Cardboard(Trash):
    value = 0.79

class Plastic(Trash):
    value = 0.15

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
for t in [Aluminum(1), Paper(1), Glass(1), Cardboard(1), Plastic(1)]:
    print(sorter.recycling_note(t))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
#: Plastic: no special handling
```

The dispatch logic is identical to the plain-function version;
`singledispatchmethod` still routes on the type of the first argument
*after* `self`. What changes is where the operation lives:
`recycling_note()` is now a method you call as `sorter.recycling_note(t)`,
reading like it belongs to `Sorter` rather than to nothing in
particular, which matters if `Sorter` needs to hold its own state
(a log of notes issued, a configuration, statistics) alongside the
dispatch. When no such state exists, as here, the free-function
version from `recycling_note.py` is simpler and does the identical
job; use `singledispatchmethod` only once the operation needs a home
on an object.

## 4. Exact-type bins against MRO dispatch

```python
# exercise_4.py
from collections import defaultdict
from functools import singledispatch
from typing import ClassVar

class Trash:
    value: ClassVar[float] = 0.0
    bin: ClassVar[type[Trash]]

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "bin" not in cls.__dict__:
            cls.bin = cls

class Aluminum(Trash):
    value = 1.67

class CrushedAluminum(Aluminum):
    value = 1.67
    bin = Aluminum

class Glass(Trash):
    value = 0.23

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
behaviors are deliberate and neither is a fallback: the sorter wants to
know precisely what arrived, and the note wants the nearest answer
anyone has written.

Sharing a parent's bin without naming a material in the loop means
choosing your own key instead of accepting `type(t)`. A `bin` class
variable does it: `__init_subclass__()` defaults each class to itself,
so nothing changes for a material that does not opt in, and
`CrushedAluminum` sets `bin = Aluminum` to opt in. The sorting loop
becomes `shared[t.bin].append(t)` and still names nothing.

The lesson generalizes past this exercise. `type(t)` is a convenient
key, not an inevitable one, and a design that declares its key can
express groupings the type hierarchy does not.
