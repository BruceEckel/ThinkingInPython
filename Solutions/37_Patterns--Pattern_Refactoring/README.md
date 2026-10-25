# Pattern Refactoring: Solutions

## 1. Adding `Plastic`

> Add a `Plastic` material to `trash.py`,
> then point `recycle_dict.py` at `plastic.dat` and run it.
> Confirm that `sort_by_type()` and `parse_trash.py` need no changes,
> then account for every pound of plastic that `plastic_dropped.py` loses.
> Which test in `test_trash.py` fails, and why is that failure correct?

<details>
<summary>Where to look</summary>

[Let a Dictionary Do the Sorting](../../Chapters/37_Patterns--Pattern_Refactoring.md#let-a-dictionary-do-the-sorting)
shows the loop keying each bin on `type(piece)`.
[The First Cut: Checking Every Type](../../Chapters/37_Patterns--Pattern_Refactoring.md#the-first-cut-checking-every-type)
shows a `match` with no case for a new material.
A subclass of `Trash` registers itself when its `class` statement runs,
so compare what each script does with a new key.
For the failing test, read what `test_trash.py` asserts about the registry.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
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
        ...

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        ...

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Plastic(Trash):
    value: ClassVar[float] = 0.15

def sum_value(contents: list[Trash]) -> float:
    ...
```

<details>
<summary>Done when</summary>

`recycle_dict.py` on `plastic.dat` prints `Plastic: 9.00` beside the `Glass` and `Aluminum` totals,
with `dict_sorter.py` and `parse_trash.py` as they were,
and you can trace that 9.00 to the pieces `plastic_dropped.py` omits.
`uv run pytest test_trash.py` shows one failing test,
and you can say why its failure is correct.

<details>
<summary>Solution</summary>

The listing bins a two-piece sample.
On `plastic.dat`, the same binning yields the `Plastic: 9.00` total that `recycle_dict_plastic.py` prints.

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
        return cls.registry[name](weight)

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Plastic(Trash):
    value: ClassVar[float] = 0.15

def sum_value(contents: list[Trash]) -> float:
    return sum(piece.weight * piece.value
               for piece in contents)

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

**Register the new material.**
The `Plastic` class is the only new Python code.
`__init_subclass__()` registers it in `Trash.registry` the moment the `class` statement runs,
so `Trash.create("Plastic", weight)` finds the class with no further code.

**Bin each piece by its class.**
`sort_by_type()` needs no change because its loop,
`bins[type(piece)].append(piece)`, keys on the class of each piece.
`Plastic` is a new key for the dictionary,
so `defaultdict` creates its bin the way it creates every other.

The one edit to `recycle_dict.py` is the filename,
since the script hardcodes `parse("trash.dat")`.
`parse_trash.py` needs no change because it calls `Trash.create(name, weight)` with a name read from the file and specifies no material.
If `Plastic` needs special handling,
an optional `@recycling_note.register` function provides it.

`plastic_dropped.py` parses four pieces and bins two.
The `match` in `sort_by_match()` has no `case` for `Plastic` and no `case _`.
The twenty-pound and forty-pound pieces fall through it,
and the loop moves on to the next piece.
Sixty pounds at 0.15 a pound is the `Plastic: 9.00` that `recycle_dict_plastic.py` prints and `plastic_dropped.py` omits.
`plastic_dropped.py`'s report looks complete,
and the two totals it prints are correct for the pieces they cover.

`test_subclasses_self_register` fails,
because it asserts that the registry's keys are exactly `{"Aluminum", "Paper", "Glass", "Cardboard"}` and `Plastic` is now a fifth entry.
That failure is correct.
The test exists to prove that defining a subclass registers it,
so a new material changes the set the assertion compares.
With `Plastic` defined,
the test passes only if `__init_subclass__()` has stopped registering subclasses.
Once you update the expected set, the test checks registration again.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. `price()` and `heaviest()`

> Write a `price()` operation as a function over a list of `Trash`,
> and a `heaviest()` operation that returns the single heaviest piece.
> Decide for each whether it needs `singledispatch`.

<details>
<summary>Where to look</summary>

[One `singledispatch` Function per Operation](../../Chapters/37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
uses `singledispatch` where behavior differs by type,
and [Choosing the Lightest Construct](../../Chapters/37_Patterns--Pattern_Refactoring.md#choosing-the-lightest-construct)
compares the options.
Ask whether each operation reads anything that varies by class beyond the numbers every `Trash` carries.
When the form is the same for every type,
an ordinary function over the list is enough.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        ...

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        ...

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class Plastic(Trash):
    value: ClassVar[float] = 0.15

def price(items: list[Trash]) -> float:
    ...

def heaviest(items: list[Trash]) -> Trash:
    ...
```

<details>
<summary>Done when</summary>

for a 10-pound `Plastic` and a 2-pound `Aluminum`,
`price()` returns `4.84` and `heaviest()` returns the `Plastic` object,
not the number `10.0`.
`uv run ty check` passes on your file,
and you can say for each function whether its body reads anything that differs by class.

<details>
<summary>Solution</summary>

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
        return cls.registry[name](weight)

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

If you call `max(items)` without the `key=` argument,
`heaviest()` raises a `TypeError`:
`'>' not supported between instances of 'Aluminum' and 'Plastic'`.
`ty` reports the same call as an `invalid-argument-type`,
because a record defines no ordering for `max()` to use.

Neither `price()` nor `heaviest()` needs `singledispatch`.
Every `Trash` subclass carries `weight` and `value`,
so the same code runs for `Aluminum`, `Plastic`, or any future material.
Each is a single function, like `sum_value()`.

`singledispatch` is for behavior that differs by type,
such as `recycling_note()` giving `Aluminum` and `Glass` their own wording.
When a calculation has the same form for every type and varies only in the numbers each type carries,
write an ordinary function.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. `recycling_note()` as a `singledispatchmethod`

> Replace the `recycling_note()` single-dispatch function with a `singledispatchmethod` on a `Sorter` class,
> and explain what changed.

<details>
<summary>Where to look</summary>

[One `singledispatch` Function per Operation](../../Chapters/37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
shows `recycling_note()` as a registered function.
Move `recycling_note()` into a `Sorter` class with `functools.singledispatchmethod`,
and register each overload with the base method's `register` decorator.
Dispatch still keys on the first argument after `self`,
so consider what else the class now provides.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from functools import singledispatchmethod
from typing import ClassVar
from record import record

@record
class Trash:
    weight: float
    value: ClassVar[float] = 0.0
    registry: ClassVar[dict[str, type[Trash]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        ...

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
        ...

    @recycling_note.register
    def _(self, t: Aluminum) -> str:
        ...

    @recycling_note.register
    def _(self, t: Glass) -> str:
        ...

    @recycling_note.register
    def _(self, t: Cardboard) -> str:
        ...
```

<details>
<summary>Done when</summary>

looping over `Trash.registry` and calling your `Sorter`'s `recycling_note()` prints the four notes `recycling_note.py` prints,
plus `Plastic: no special handling` if you define `Plastic`.
If `Aluminum` gets `no special handling`,
your dispatch is keying on the `Sorter` instance.
You can say when the method form improves on the function.

<details>
<summary>Solution</summary>

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
        return "no special handling"

    @recycling_note.register
    def _(self, t: Aluminum) -> str:
        return "crush and bale"

    @recycling_note.register
    def _(self, t: Glass) -> str:
        return "sort by color, then crush"

    @recycling_note.register
    def _(self, t: Cardboard) -> str:
        return "flatten and bundle"

sorter = Sorter()
for cls in Trash.registry.values():
    note = sorter.recycling_note(cls(1.0))
    print(f"{cls.__name__}: {note}")
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
#: Plastic: no special handling
```

If you decorate the `Sorter` methods with `@singledispatch` instead of `@singledispatchmethod`,
the loop prints "no special handling" for all five materials,
`Aluminum` included, and the type checker accepts the class.
`singledispatch` dispatches on the first argument,
which in a method call is the `Sorter` instance.
The one registration that matches a `Sorter` is the base method's registration,
so the base method handles every call.

**Route each piece by its type.**
The dispatch is the same as in the function version.
`singledispatchmethod` routes on the type of the first argument after `self`.

**Move the operation onto an object.**
What changes is where you define the operation.

The method form matters if `Sorter` holds state of its own alongside the dispatch:
a log of notes issued, a configuration, statistics.
When `Sorter` holds only the dispatch, as here,
the function in `recycling_note.py` is simpler and does the same job.
Use `singledispatchmethod` when the operation needs to read or update an object's state.

The method form also brings the trap that [*Multiple Dispatching*](../../Chapters/32_Patterns--Multiple_Dispatching.md#the-singledispatchmethod-trap)
describes.
A subclass of `Sorter` shares this one dispatcher,
so a registration made through the subclass changes what `Sorter`'s method returns too.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Exact-type bins against MRO dispatch

> Derive `CrushedAluminum` from `Aluminum` in `trash.py`,
> add it to the data `recycle_dict.py` reads,
> then run `recycle_dict.py` and `recycling_note.py`.
> Explain why `CrushedAluminum` gets its own bin but not its own note.
> Then change `sort_by_type()` so a subclass shares its parent's bin,
> without naming any material class in the sorting loop.

<details>
<summary>Where to look</summary>

[Let a Dictionary Do the Sorting](../../Chapters/37_Patterns--Pattern_Refactoring.md#let-a-dictionary-do-the-sorting)
keys each bin on `type(piece)`, an exact-class lookup,
while `singledispatch` in [One `singledispatch` Function per Operation](../../Chapters/37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
walks the MRO.
To let a subclass share its parent's bin,
give `Trash` a class variable that holds the bin's key,
and have `__init_subclass__()` default that variable for each class.
A subclass that shares its parent's bin overrides the variable,
and the loop indexes by that attribute instead of `type(t)`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
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
        ...

class Aluminum(Trash):
    value: ClassVar[float] = 1.67

class CrushedAluminum(Aluminum):
    value: ClassVar[float] = 1.67
    bin: ClassVar[type[Trash]] = Aluminum

class Glass(Trash):
    value: ClassVar[float] = 0.23

@singledispatch
def recycling_note(t: Trash) -> str:
    ...

@recycling_note.register
def _(t: Aluminum) -> str:
    ...
```

<details>
<summary>Done when</summary>

`recycle_dict.py` reports a `CrushedAluminum:` total of its own while `recycling_note.py` prints `CrushedAluminum: crush and bale`,
and you can name the lookup behind each.
After your change, the `CrushedAluminum:` line is gone,
its weight adds to the `Aluminum` total, every other material keeps its own bin,
and the sorting loop specifies no material.

<details>
<summary>Solution</summary>

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
    return "no special handling"

@recycling_note.register
def _(t: Aluminum) -> str:
    return "crush and bale"

pieces: list[Trash] = [
    Aluminum(30.0), CrushedAluminum(20.0), Glass(10.0)]

exact: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    exact[type(t)].append(t)
print(sorted(k.__name__ for k in exact))
#: ['Aluminum', 'CrushedAluminum', 'Glass']

crushed = CrushedAluminum(1.0)
print(f"{type(crushed).__name__}: "
      f"{recycling_note(crushed)}")
#: CrushedAluminum: crush and bale

shared: dict[type[Trash], list[Trash]] = defaultdict(list)
for t in pieces:
    shared[t.bin].append(t)
print(sorted(k.__name__ for k in shared))
#: ['Aluminum', 'Glass']
```

If you set `cls.bin = cls` in `__init_subclass__()` without checking `cls.__dict__` first,
the shared sort still prints three bins,
`['Aluminum', 'CrushedAluminum', 'Glass']`.
`__init_subclass__()` runs after the class body,
so the assignment overwrites the `bin = Aluminum` that `CrushedAluminum` declares.

**Key the bins on the exact class.**
`exact[type(t)]` is a dictionary probe on the exact class,
so `CrushedAluminum` is a new key and gets a bin of its own.

**Resolve the note through the MRO.**
`singledispatch` resolves through the MRO instead.
It walks from `CrushedAluminum` to `Aluminum` and uses `Aluminum`'s registration.

Both behaviors are deliberate, and neither is a fallback.
The sorter must know the exact class that arrived.
The note uses the nearest registration along the MRO.

**Give each class a default bin.**
To share a parent's bin without specifying a material in the loop,
choose your own key instead of accepting `type(t)`.
A `bin` class variable supplies that key.
`__init_subclass__()` sets each class's `bin` to that class by default,
so every material keeps a bin of its own.

**Let a subclass share its parent's bin.**
`CrushedAluminum` restates the `ClassVar` annotation the way the chapter's subclasses restate `value`'s annotation.
The type checker treats that restatement as optional.

**Sort by the declared key.**
The sorting loop still specifies no material.

`type(t)` is a convenient key, not an inevitable one.
A design that declares its own key can group classes that `type(t)` keeps apart,
as `bin` puts `CrushedAluminum` in the `Aluminum` bin.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A base function that refuses to answer

> Define `Plastic`, whose disposal hazard is toxic fumes,
> and leave it out of `disposal_hazard.py`'s registrations.
> What does `hazard()` answer for a piece of plastic?
> Then write `strict_hazard()`,
> whose base function raises `NotImplementedError`,
> and call it on the same piece.
> What does the strict form require for the materials whose hazard is "none"?

<details>
<summary>Where to look</summary>

[One `singledispatch` Function per Operation](../../Chapters/37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
builds `hazard()` with a base function that answers for any unregistered type.
For `strict_hazard()`,
make the base function raise `NotImplementedError` with a message naming the type,
then register each material whose hazard you know,
including those whose answer is `"none"`.
When you forget a registration,
compare what goes wrong with a silent default and with a stopped program.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
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
    ...

@hazard.register
def _(t: Aluminum) -> str:
    ...

@singledispatch
def strict_hazard(t: Trash) -> str:
    ...

@strict_hazard.register
def _(t: Aluminum) -> str:
    ...

@strict_hazard.register
def _(t: Paper) -> str:
    ...
```

<details>
<summary>Done when</summary>

`hazard()` returns `none` for a `Plastic` piece,
and `strict_hazard()` on the same piece raises a `NotImplementedError` whose message names `Plastic`.
Your `strict_hazard()` returns `"none"` for `Paper` and `sharp edges` for `Aluminum`,
and you can say what your file needed for `Paper` that `hazard()` gets from its base function.

<details>
<summary>Solution</summary>

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

If you register `Aluminum` for `strict_hazard()` and skip `Paper`,
`strict_hazard(Paper(1.0))` raises a `NotImplementedError` reading `no hazard rule for Paper`.
The program stops before it reaches the plastic.
The strict base function raises an exception for every unregistered type,
including a harmless one like `Paper`, whose answer is `"none"`.

**Fall back to a default answer.**
`hazard()` returns `"none"` for the plastic, whose hazard is toxic fumes.
That wrong answer looks like every correct `"none"` beside it.
The forgotten registration produces no exception and no report from the type checker.

**Refuse an unregistered type.**
`strict_hazard()` raises a `NotImplementedError` that names the material at the first call.

**Register every material.**
The strict form requires one registration for every material,
including each one whose answer is `"none"`.
`Paper` needs three lines to return the `"none"` that `hazard()` gets from its base function.

Choose by which mistake does more harm.
A default is right when it is a true answer for most types and a forgotten registration does little harm.
A base function that raises an exception is right when a wrong answer is worse than a stopped program,
as it is for a safety report.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
