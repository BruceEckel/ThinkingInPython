# Class Attributes: Solutions

## 1. A third instance created after the class attribute changes

> In `class_attribute_confusion.py`,
> add a third instance `c = Stars()` after the `Stars.rating = 9` line,
> and print `c.rating`.
> Predict its value before running,
> then explain why it differs from `a.rating`.

<details>
<summary>Where to look</summary>

[Two Dictionaries, One Lookup](../../Chapters/09_Foundations--Class_Attributes.md#two-dictionaries-one-lookup)
shows a read searching the instance dictionary and then the class.
A new instance starts with an empty dictionary,
so its read falls through to the value the class holds at that moment.
Compare the order of the three steps: shadow on `a`, change the class,
create `c`.

<details>
<summary>Done when</summary>

printing `c.rating` gives `9` while `a.rating` still gives `1`,
and you can name the dictionary in which each of the two reads finds `rating`.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
class Stars:
    rating = 5

a = Stars()
b = Stars()
a.rating = 1  # Shadows the class attribute on 'a' only
Stars.rating = 9  # Changes the shared class attribute
c = Stars()
print(c.rating)
#: 9
```

`c` is a brand-new instance with an empty instance dictionary,
so reading `c.rating` falls back to the class attribute, which is now `9`.
`c.rating` differs from `a.rating`, which is still `1`.
The line `a.rating = 1` gave `a` its own instance attribute,
and that attribute shadows the class attribute when you read `a.rating`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. A third subclass with no override

> In `class_var_inheritance.py`,
> add a third subclass `class Middle(Base): pass`
> (no shadowing `shared`, like `Left`)
> and print `Middle.shared` alongside the others at each step.
> Confirm `Middle` tracks `Base` the way `Left` does.

<details>
<summary>Where to look</summary>

[ClassVar and Inheritance](../../Chapters/09_Foundations--Class_Attributes.md#classvar-and-inheritance)
walks one class attribute down a hierarchy.
A subclass that inherits `shared` unchanged reads through to its base.
Add `Middle` as a second subclass like `Left`,
print `Middle.shared` beside the others at each step,
and check which classes move together.

<details>
<summary>Done when</summary>

at each step `Middle.shared` prints the same value as `Left.shared` until `Left.shared = 5`,
and your last line reads `9 5 9 100` for `Base`, `Left`, `Middle`, and `Right`.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Middle(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Base.shared, Left.shared, Middle.shared, Right.shared)
#: 0 0 0 100
Base.shared = 9
print(Base.shared, Left.shared, Middle.shared, Right.shared)
#: 9 9 9 100
Left.shared = 5
print(Base.shared, Left.shared, Middle.shared, Right.shared)
#: 9 5 9 100
```

`Middle` and `Left` both inherit `shared` from `Base`,
so both track `Base.shared` through attribute lookup until something assigns to `Left.shared` or `Middle.shared`.
In the last step, `Left.shared = 5` gives `Left` its own entry,
and `Middle` still reads `Base`'s `9`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. Each `B()` instance keeps its own `x`

> In `real_defaults.py`, create `b = B()` and assign `b.x = -1`.
> Then create a second instance, `b2 = B()`,
> and confirm `b2.x` is still `100`.

<details>
<summary>Where to look</summary>

[Real Per-Object Defaults](../../Chapters/09_Foundations--Class_Attributes.md#real-per-object-defaults)
shows a constructor default giving each instance its own value.
For a `@dataclass` field with a default,
the generated `__init__()` assigns `self.x` on every call.
Assign to `b.x`, build `b2`, and print both.

<details>
<summary>Done when</summary>

printing `b.x` and `b2.x` together shows `-1 100`,
so the assignment to `b.x` leaves the second instance's `x` at the constructor default.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
from dataclasses import dataclass

@dataclass
class B:
    x: int = 100  # Constructor default, not class attribute

b = B()
b.x = -1
b2 = B()
print(b.x, b2.x)
#: -1 100
```

Each call to `B()` runs the generated `__init__()`,
which assigns `100` to `self.x` as a fresh instance attribute for that object.
A constructor default creates one value per instance,
unlike a plain class attribute,
which creates one value shared by all instances until something shadows it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. A plain class attribute masquerading as shared state

> Rewrite `Tally` from `class_var.py` so `total` is a plain (non-`ClassVar`)
> class attribute instead, then assign `a.total = 99` through an instance.
> Using `vars()` as in `inside_objects.py`,
> explain what that assignment creates, and where.

<details>
<summary>Where to look</summary>

[Declaring Shared State with ClassVar](../../Chapters/09_Foundations--Class_Attributes.md#declaring-shared-state-with-classvar)
pairs the shared counter with the error the type checker reports for an instance write.
Use a plain class attribute for `total`,
then call `vars()` on the instance as in [Two Dictionaries, One Lookup](../../Chapters/09_Foundations--Class_Attributes.md#two-dictionaries-one-lookup).
The instance and class dictionaries show which one receives an assignment made through the instance.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
class Tally:
    total = 0  # Plain class attribute, no ClassVar
    label: str

    def __init__(self, label: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

after `a.total = 99`, `vars(a)` shows a `total` entry of `99` beside `label`,
while `Tally.total` still prints `2`.
Restoring `ClassVar[int]` on `total` makes `uv run ty check` report `invalid-attribute-access` on the `a.total = 99` line.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
class Tally:
    total = 0  # Plain class attribute, no ClassVar
    label: str

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

a = Tally("a")
b = Tally("b")
print(Tally.total)
#: 2
a.total = 99  # Does not touch Tally.total
print(vars(a))
#: {'label': 'a', 'total': 99}
print(Tally.total)
#: 2
```

**Shadow the class attribute.**
`a.total = 99` looks like it should update the shared count,
but assignment through an instance writes to the instance, not the class.
That assignment creates a brand-new instance attribute named `total` on `a`,
which then shadows `Tally.total` for `a`.

**Check where the write went.**
`vars(a)` shows the shadow: a `total` entry in `a`'s own dictionary.

This shadow is the bug `ClassVar` exists to catch.
With `total: ClassVar[int] = 0` declared instead,
the type checker reports `a.total = 99` as an error before the line runs,
because the assignment writes to a `ClassVar` through an instance.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A per-instance list, via `default_factory`

> Rewrite `Cart` from `shared_mutable.py` as a `@dataclass` with `items: list[str] = field(default_factory=list)`,
> importing `field` from `dataclasses`.
> [Data Classes as Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared)
> covers `default_factory`.
> This exercise needs only the one expression given here.
> Repeat the `append` and confirm `b.items` stays empty.
> Then try the same class with `items: list[str] = []` and report what `@dataclass` does about it.

<details>
<summary>Where to look</summary>

[A Shared Mutable Value](../../Chapters/09_Foundations--Class_Attributes.md#a-shared-mutable-value)
shows two `Cart` objects sharing one list,
so an append through one object changes the list both objects hold.
The fix builds the list per instance with `field(default_factory=list)` from `dataclasses`.
For the second half,
write the `[]` default and see whether the `class` statement finishes, and when.

<details>
<summary>Done when</summary>

after the `append()` through `a`, printing both lists shows `['apple'] []`.
With the `[]` default, the `class` statement fails before any `Cart` exists,
raising a `ValueError` whose message ends with `use default_factory`.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

a, b = Cart(), Cart()
a.items.append("apple")
print(a.items, b.items)
#: ['apple'] []
```

**Build a list per instance.**
`default_factory=list` calls `list()` once per construction,
so the generated `__init__()` assigns a brand-new list to `self.items` on every `Cart`.

For the same class written with `items: list[str] = []`,
`@dataclass` raises a `ValueError`,
which turns the shared-list bug into an immediate error:

```python
# exercise_5_rejected.py
from dataclasses import dataclass
from exceptions import expected

with expected(ValueError):
    @dataclass
    class Cart:
        items: list[str] = []
#: [ValueError] mutable default <class 'list'> for field
#: items is not allowed: use default_factory
```

**Fail at class definition.**
`@dataclass` raises `ValueError` at class-definition time, not at first use,
because it inspects every default before generating the constructor.
`shared_mutable.py`'s `Cart` has no decorator to inspect its defaults,
so `Cart` gets its shared list silently.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 6. `del` unshadows, once

> In `inside_objects.py`, add `del a.x` after the final `print`,
> then print `vars(a)` and `a.x` again.
> Predict both before running.
> Then run `del a.x` a second time and explain the exception,
> given what `vars(A)` still holds.

<details>
<summary>Where to look</summary>

[Two Dictionaries, One Lookup](../../Chapters/09_Foundations--Class_Attributes.md#two-dictionaries-one-lookup)
shows that assignment writes to the instance dictionary and a read falls back to the class.
Use `del a.x` on that same dictionary and print `vars(a)` and `a.x` afterward.
For the second `del`, compare what `vars(a)` and `vars(A)` each hold.

<details>
<summary>Done when</summary>

after the first `del a.x`, `vars(a)` prints `{}` and `a.x` prints `100`.
The second `del a.x` raises an `AttributeError`
(`'A' object has no attribute 'x'`),
and `vars(A)["x"]` still prints `100` afterward.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from exceptions import expected

class A:
    x = 100

a = A()
a.x = 1
print(vars(a), a.x)
#: {'x': 1} 1
print(vars(A)["x"])
#: 100
del a.x  # [1]
print(vars(a), a.x)
#: {} 100
with expected(AttributeError):
    del a.x  # [2]
#: [AttributeError] 'A' object has no attribute 'x'
print(vars(A)["x"])
#: 100
```

**Remove the shadow.**
`del a.x` (`[1]`) removes the entry from the instance dictionary,
which is where assignment writes.
`a.x` reads `100` again,
because the lookup falls back to the class the way it did before any assignment.

**Show that deletes stop at the instance.**
`del` acts on the instance dictionary alone, the way assignment does,
so `vars(A)["x"]` keeps its `100`.
The second `del a.x` (`[2]`)
finds the instance dictionary empty and raises an `AttributeError`.
Deleting the class attribute takes `del A.x`, naming the class.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Why `self.total += 1` leaves the class counter at zero

> In `self_increment.py`,
> print `vars(a)` and `vars(Tally)["total"]` after constructing both instances,
> and use them to explain the `1 1 0` output.
> Then fix the class so the shared counter moves,
> without changing the `ClassVar` declaration,
> and explain what the type checker reports when you remove the `# type: ignore` from the broken version.

<details>
<summary>Where to look</summary>

[What ClassVar Catches](../../Chapters/09_Foundations--Class_Attributes.md#what-classvar-catches)
shows `self.total += 1` leaving the class counter at zero.
The augmented assignment reads through the class but writes to the instance,
and `vars()` makes that write visible.
The fix names the class on the left of `+=`,
and removing the `# type: ignore` shows what the checker reports about the write.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        ...

class Counting:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        ...
```

<details>
<summary>Done when</summary>

`vars(a)` shows `{'total': 1}` while `vars(Tally)["total"]` shows `0`,
and your fixed class prints `2 2 2` for two instances and the class.
Removing the `# type: ignore` makes `uv run ty check` report `invalid-attribute-access` on `self.total += 1`.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1  # type: ignore

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
print(vars(a), vars(Tally)["total"])
#: {'total': 1} 0

class Counting:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        Counting.total += 1  # Name the class, not self

c, d = Counting(), Counting()
print(c.total, d.total, Counting.total)
#: 2 2 2
print(vars(c), vars(Counting)["total"])
#: {} 2
```

**Show where each write went.**
`self.total += 1` expands to `self.total = self.total + 1`.
The read finds the instance dictionary empty, falls back to the class,
and gets `0`.
The write then stores `1` in the instance dictionary,
where every write through an instance goes.
Each object ends up with its own `total` of `1`,
shadowing a class attribute that still holds `0`.

**Read the checker's report.**
With the `# type: ignore` removed, the type checker (`ty`)
reports `invalid-attribute-access`, naming the type of `self`.
The augmented form expands to an assignment through `self`.
The type checker treats that assignment as a write to a `ClassVar` through an instance,
the same as `a.total = 99`, the commented-out line in `class_var.py`.
For the line in `__init__()` it reports "Cannot assign to ClassVar `total` from an instance of type `Self@__init__`",
where `Self@__init__` is its name for the type of `self` inside that method.
For `a.total = 99` the message names `Tally`, the type of `a`.
The `ClassVar` declaration catches the mistake at check time.
The listing suppresses the report so it can demonstrate what the write does at runtime.

**Send the write to the class.**
`Counting.total += 1` reads and writes the same class dictionary,
so both instances report `2`.
`vars(c)` is empty because the constructor writes to the class.
Reading `c.total` falls back to that shared value.

Writing the fix as `type(self).total += 1` also prints `2 2 2` here,
because `type(self)` is `Counting` for both `c` and `d`.
With a subclass, the subclass's first construction forks the counter the way `classvar_fork.py` forks it for `Sub`.
Constructing an empty subclass twice after `c` and `d` leaves `Counting.total` at `2` and gives the subclass its own `total` of `4`.
Naming the class sends every write to one dictionary.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. A mutable `ClassVar` shared down the hierarchy

> Change `class_var_inheritance.py` so `shared` is `ClassVar[list[int]] = []`,
> delete `Right`'s `shared = 100`,
> and have `Left` and `Right` both call `.append()` on it.
> Predict what `Base.shared` holds afterwards, then check.
> Give `Right` its own list with `shared = []` in its body and repeat.

<details>
<summary>Where to look</summary>

[A Shared Mutable Value](../../Chapters/09_Foundations--Class_Attributes.md#a-shared-mutable-value)
and [ClassVar and Inheritance](../../Chapters/09_Foundations--Class_Attributes.md#classvar-and-inheritance)
each cover half of this exercise.
A mutable `ClassVar` on the base is a single object that every subclass reaches by lookup,
so `.append()` changes that object for every subclass.
An assignment in a subclass body makes a new entry in that subclass's dictionary.
Compare the two runs with `is`.

<details>
<summary>Done when</summary>

the first run prints `[1, 2]` for `Base.shared` and both subclasses,
and `Right.shared is Base.shared` prints `True`.
After you give `Right` its own `shared = []`,
the same appends print `[1] [1] [2]` for `Base`, `Left`, and `Right`,
and the `is` test prints `False`.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from typing import ClassVar

class Base:
    shared: ClassVar[list[int]] = []

class Left(Base):
    pass

class Right(Base):
    pass

Left.shared.append(1)
Right.shared.append(2)
print(Base.shared, Left.shared, Right.shared)
#: [1, 2] [1, 2] [1, 2]
print(Left.shared is Base.shared)
#: True
print(Right.shared is Base.shared)
#: True

class Base2:
    shared: ClassVar[list[int]] = []

class Left2(Base2):
    pass

class Right2(Base2):
    shared = []  # Its own list, separate from Base2's

Left2.shared.append(1)
Right2.shared.append(2)
print(Base2.shared, Left2.shared, Right2.shared)
#: [1] [1] [2]
print(Right2.shared is Base2.shared)
#: False
```

**Share one list across the hierarchy.**
`Left` and `Right` both inherit `shared`, so both names read through to `Base`,
and `.append()` mutates the list stored there.
`Left.shared is Base.shared` and `Right.shared is Base.shared` together prove that the three names share one object,
not three equal lists.

This listing combines the shared mutable value of `shared_mutable.py` with the inheritance lookup of `class_var_inheritance.py`.
Each one alone keeps a change where you can see it.
In a single class, a mutable `ClassVar` declares its sharing in the class body,
so the sharing stays visible.
A subclass changes an inherited immutable `ClassVar` by assignment,
which creates the subclass's own entry.
Combined, the mutable value and the inheritance lookup produce one list,
declared on the base class, that every subclass mutates under its own name.

**Give one subclass its own list.**
The assignment `shared = []` in `Right2`'s class body creates a new entry in `Right2`'s own dictionary,
so `Right2.shared` reads that entry.
`Left2` still shares `Base2`'s list.
The result, `[1] [1] [2]`,
follows the same rule the integer `shared` in exercise 2 shows:
one value per class that declares it.

The listing models a bug in which every subclass treats the single list on the base class as its own.
When one shared table is the intent, as in a registry of subclasses,
the same code is correct.
When each owner needs its own list,
build the mutable value per owner rather than once in the class body.
A `default_factory` field gives each instance its own list,
and `__init_subclass__()`,
which [Metaprogramming](../../Chapters/17_Techniques--Metaprogramming.md#self-registration-of-subclasses)
introduces, gives each subclass its own.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 9. A declared attribute that no method assigns

> Write a class `Ticket` with a bare annotation `seat: str` and an `__init__()` that stores a `holder` and leaves `seat` unassigned.
> Run `ty` on it, then read `seat` on an instance inside `expected(AttributeError)`.
> Assign `seat` from outside the class and print `vars()` of the instance before and after.

<details>
<summary>Where to look</summary>

[A Bare Annotation Declares, It Does Not Create](../../Chapters/09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create)
explains the difference between declaring `seat` and creating it.
The annotation informs the type checker.
An assignment creates the attribute,
so `vars()` on the instance shows what exists.
Read the attribute inside `expected(AttributeError)`, assign it from outside,
and print `vars()` again.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from exceptions import expected

class Ticket:
    seat: str  # Declared, assigned by no method

    def __init__(self, holder: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your file, the first `vars()` shows `holder` alone,
and the read inside `expected(AttributeError)` reports `'Ticket' object has no attribute 'seat'`.
After the outside assignment, `vars()` shows both `holder` and `seat`.

<details>
<summary>Solution</summary>

```python
# exercise_9.py
from exceptions import expected

class Ticket:
    seat: str  # Declared, assigned by no method

    def __init__(self, holder: str) -> None:
        self.holder = holder

t = Ticket("Ada")
print(vars(t))
#: {'holder': 'Ada'}
with expected(AttributeError):
    print(t.seat)
#: [AttributeError] 'Ticket' object has no attribute 'seat'
t.seat = "14C"
print(vars(t), t.seat)
#: {'holder': 'Ada', 'seat': '14C'} 14C
```

**Declare the attribute without creating it.**
The type checker passes this file.
The checker accepts the declaration `seat: str` and never checks that a method assigns `seat`.
At runtime the declaration becomes an entry in the class's annotations alone.

**Create the attribute from outside.**
The type checker verifies `t.seat = "14C"` against the declared `str`.

A bare annotation is safe when the code that assigns the attribute runs before any code that reads it.
The type checker cannot confirm that order,
so the class depends on its callers to keep it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. Watching `Sub` get its own counter

> In `classvar_fork.py`,
> print `vars(Sub).get("total")` before the first `Sub()` call and after each one,
> and use the three values to say which class's dictionary supplies each `Sub.total` the listing prints.
> Then change the increment to `Base.total += 1` and predict every line before running.

<details>
<summary>Where to look</summary>

[`type(self)` Forks the Counter](../../Chapters/09_Foundations--Class_Attributes.md#typeself-forks-the-counter)
shows the first `Sub()` writing a new `total` into `Sub`'s own dictionary.
Print `vars(Sub).get("total")` at each step and watch when the entry appears.
For the second half,
naming `Base` in the increment sends every write to `Base`'s dictionary,
so predict whether `Sub` gets an entry.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from typing import ClassVar

class Base:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        ...

class Sub(Base):
    pass

class Counted:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        ...

class SubCounted(Counted):
    pass
```

<details>
<summary>Done when</summary>

`vars(Sub).get("total")` prints `None` before the first `Sub()`,
then `2` and `3` after each call, while `Base.total` stays at `1`.
With `Base.total += 1` as the increment,
every `vars(Sub).get("total")` prints `None` and the two counts move together.

<details>
<summary>Solution</summary>

```python
# exercise_10.py
from typing import ClassVar

class Base:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        type(self).total += 1

class Sub(Base):
    pass

Base()
print(Base.total, Sub.total)
#: 1 1
print(vars(Sub).get("total"))
#: None
Sub()  # [1]
print(Base.total, Sub.total)
#: 1 2
print(vars(Sub).get("total"))
#: 2
Sub()  # [2]
print(Base.total, Sub.total)
#: 1 3
print(vars(Sub).get("total"))
#: 3

class Counted:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        Counted.total += 1  # Name the class

class SubCounted(Counted):
    pass

Counted()
print(Counted.total, SubCounted.total)
#: 1 1
print(vars(SubCounted).get("total"))
#: None
SubCounted()
print(Counted.total, SubCounted.total)
#: 2 2
print(vars(SubCounted).get("total"))
#: None
SubCounted()
print(Counted.total, SubCounted.total)
#: 3 3
print(vars(SubCounted).get("total"))
#: None
```

**Watch the subclass fork the counter.**
Before the first `Sub()` (`[1]`), `vars(Sub)` has no `total`,
so `Sub` reads `Base`'s `total`.
The `Sub()` at `[1]` runs `type(self).total += 1` with `type(self)` as `Sub`.
The read falls back to `Base.total`, which is `1`,
and the write stores `2` in `Sub`'s own dictionary.
From then on `Sub` has its own counter, and the second `Sub()` (`[2]`)
moves it to `3` while `Base.total` stays at `1`.

**Keep one counter for the hierarchy.**
`Counted` names the class on the left,
so every construction reads and writes `Counted`'s dictionary.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
