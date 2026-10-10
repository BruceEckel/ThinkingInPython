# Class Attributes

> A field in the class body looks, to a C++ or Java programmer,
> like storage in each object.
> In Python it is one variable the class holds,
> and an object's own fields come from assignments through `self`.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*.
A class attribute is easy to misread as a per-object default value.
It is not one.

> A class attribute creates a single shared variable across all instances of the class.

If you then create an instance attribute of the same name,
that instance attribute *shadows* the class attribute.

In C++ or Java, the language allocates storage for such a field in each object before the constructor runs,
so a programmer from those languages expects per-object storage here too.
A Python class attribute corresponds to a C++ or Java `static` field.
No syntax in a Python class body allocates a per-object field.
Assigning through `self` inside a method creates that storage instead.

```python
# class_attribute_confusion.py

class Stars:
    rating = 5  # Shared across all instances

a, b = Stars(), Stars()
print(a.rating, b.rating)  # Both read the same storage
#: 5 5
a.rating = 1  # Assigning makes an instance attribute on 'a'
# 'a' shadows it, 'b' sees the class
print(a.rating, b.rating)
#: 1 5
Stars.rating = 9  # Change the shared storage
print(a.rating, b.rating)  # 'b' reads the class attribute
#: 1 9
```

### Two Dictionaries, One Lookup

An instance and its class each have their own attribute dictionary.
Reading an attribute checks the instance first, then falls back to the class.
Assigning through an instance writes to the instance,
creating the instance attribute on first assignment.
Assigning through the class name, as `Stars.rating = 9` does,
changes the shared value.
`vars()` returns an object's own attribute dictionary,
so inspecting the class with `vars(A)` and the instance with `vars(a)` shows the split:

```python
# inside_objects.py

class A:
    x = 100

a = A()
print(vars(A)["x"])  # The attribute lives in the class dict
#: 100
print(vars(a))  # The instance has no attributes yet
#: {}
a.x = 1
print(vars(a))  # Assignment created it on the instance
#: {'x': 1}
print(vars(A)["x"])
#: 100
```

The listing subscripts `vars(A)` instead of printing it whole,
because a class's dictionary is a read-only `mappingproxy` that carries the compiler's own bookkeeping alongside `x`.
Assigning through the class name changes the entry, as `Stars.rating = 9` does,
and `setattr(A, "x", 5)` does the same when the name arrives as a string;
writing to the proxy raises a `TypeError`.
The instance dictionary is a plain `dict` holding what the code assigned,
and that alone.

That instance dictionary is not guaranteed.
A class that declares [`__slots__`](18_Techniques--Performance.md#slots),
or a data class built with `slots=True`, has no instance `__dict__`,
provided every base class is slotted too.
An instance of such a class cannot shadow a class attribute.
Assigning to that name on the instance raises an `AttributeError`,
because the instance has no dictionary to hold the new attribute.

A method is a class attribute like any other.
`def show(self):` in a class body stores a function object in the class dictionary,
and `a.show()` finds it by the same fallback that finds `a.x`:
nothing on the instance, so look at the class.
`display_object()`, the inspection helper first used in [Classes](07_Foundations--Classes.md),
reports attributes and methods separately,
but both live in the same class dictionary.
Because the method lives in the class dictionary,
assigning `a.show = something` shadows the method for `a` alone.

One kind of class attribute follows a different rule.
A [`@property`](07_Foundations--Classes.md#properties)
owns its name on the class,
so for that name reading calls its getter and assigning calls its setter in place of the instance dictionary.
Whatever the setter stores, such as the `_radius` behind `Circle`'s `radius`,
goes into that dictionary under its own name.

### The Bug Surfaces Far from Its Cause

A class attribute reads like a default right up until someone assigns to an attribute of the same name on one instance.
After that, a change to the class attribute reaches every other object,
while the object that assigned keeps its own value.
The bug surfaces far from the line that caused it,
often in a different function that does not mention the assignment:

```python
# far_from_the_cause.py

class Stars:
    rating = 5  # Shared across all instances

def sell(star: Stars) -> None:
    star.rating = 1  # Shadows, buried in a helper

def rerate(rating: int) -> None:
    Stars.rating = rating  # Meant for every Stars

def show(star: Stars) -> None:
    print(star.rating)  # Reads far from where it shadowed

a, b = Stars(), Stars()
sell(a)
rerate(9)
show(a)  # The new rating does not reach a
#: 1
show(b)
#: 9
```

`rerate(9)` changes the rating for every `Stars`,
and `show(a)` still prints `1`.
Someone debugging that stale `1` finds nothing wrong in `rerate()` or in `show()`.
The cause is the assignment inside `sell()`,
which gave `a` its own `rating` before the class attribute changed.
Neither `rerate()` nor `show()` calls `sell()`,
so finding the assignment means tracing every earlier call that touched a `Stars` instance.

### A Shared Mutable Value

The shadowing rule confines a change to one object only while the shared value is immutable:

```python
# shared_mutable.py

class Cart:
    items: list[str] = []  # One list, shared by every Cart

a, b = Cart(), Cart()
a.items.append("apple")  # Mutates, does not assign
print(a.items, b.items)
#: ['apple'] ['apple']
a.items = ["pear"]  # Assignment shadows, as before
print(a.items, b.items)
#: ['pear'] ['apple']
```

`a.items.append("apple")` does not assign to `a.items`.
It reads `items`, finds nothing on `a`, falls back to the class,
and mutates the one list stored there.
The mutation creates no instance attribute, so `b` sees the apple too.
`a.items = ["pear"]` does assign,
and that assignment creates `a.items` on the instance and shadows the class list,
leaving `b` still reading the shared one.
Because shadowing starts with an assignment and `.append()` makes none,
a read followed by a mutation slips past the rule.
An augmented assignment does both:
`a.items += ["pear"]` mutates the shared list through `__iadd__()` and then assigns that same list to `a`,
so `b` sees the pear too.
A type checker accepts the line too.
`a.items.append("apple")` is a correct call on a `list[str]`.

A per-object list belongs in `__init__()`,
as [Real Per-Object Defaults](#real-per-object-defaults) shows,
or in a `@dataclass` field with a [`default_factory`](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared).

## Declaring Shared State with ClassVar

When you genuinely want one shared value, say so with `ClassVar` from `typing`.
The type checker then treats the attribute as class-wide,
and rejects the instance assignment that shadows it:

```python
# class_var.py
from typing import ClassVar
from display import display_object

class Tally:
    total: ClassVar[int] = 0  # A single shared value
    label: str  # Declared, not yet assigned

    def __init__(self, label: str) -> None:
        self.label = label
        Tally.total += 1

display_object(Tally)
#: [Attributes]
#:   • total: typing.ClassVar[int] = 0 [CV]
#: [Methods]
#:   None
a = Tally("a")
display_object(a)
#: [Attributes]
#:   • label: str = 'a'
#:   • total: typing.ClassVar[int] = 1 [CV]
#: [Methods]
#:   None
b = Tally("b")
print(Tally.total)
#: 2
# a.total = 99  # ty: Cannot assign to ClassVar `total`
```

`display_object(Tally)` shows what the class holds: `total`,
and nothing called `label`.
The `[CV]` tag, for *class variable*, marks an attribute the class stores.
An assignment in the class body creates a class attribute,
as `class_attribute_confusion.py` shows.
`total: ClassVar[int] = 0` has the `= 0`,
so it exists on `Tally` before any instance exists.
`label: str` has no `=`, so the class stores nothing under that name.
The annotation records, in `Tally.__annotations__`,
that a `Tally` will carry a `label`.
`display_object()` reports attributes that exist,
so the declaration stays out of its report.

Once an instance exists, `display_object(a)` reports both names:
`label: str = 'a'` and `total: typing.ClassVar[int] = 1`.
Constructing `a` runs `self.label = label`,
which creates a real `label` attribute on `a`, not on `Tally`.
`total` shows up too, by fallback.
Reading an attribute checks the instance first, then the class,
the rule `Stars` demonstrates in `class_attribute_confusion.py`.
`a` holds no copy of its own.
The tags agree.
`label`, stored on `a`, carries no `[CV]`, while `total`, found by fallback,
keeps it.

### A Bare Annotation Declares, It Does Not Create

A *bare annotation*, one with no assigned value,
is a declaration rather than a placeholder.
It states that instances of this class carry a `label` attribute of type `str`,
set somewhere.
Here that somewhere is `__init__()`,
and its `self.label = label` produces the attribute `display_object(a)` finds.
If you leave that assignment out of `__init__()`, no attribute exists,
on the instance or the class.
The type checker trusts the annotation rather than checking that some method sets the attribute,
so the check passes.
The first code that reads `label` raises an `AttributeError`.

The annotation on `label` is optional here.
If you delete it, the type checker still infers `label: str` correctly from `self.label = label`,
because the parameter's own type carries through to the attribute it initializes.
The annotation stays for symmetry with `total`,
so both names read together at the top instead of one hiding inside the constructor.
[Simulation](38_Patterns--Simulation.md#rooms-robots-and-the-item-factory)
shows the case that requires the annotation.
There, code outside the class sets the attribute,
and the bare annotation is the type checker's one source for its type.

### A `ClassVar` With No Value Declares Too

`ClassVar` says where an attribute lives, not that it exists.
Without a value the class stores nothing,
the same as for `label` in `class_var.py`:

```python
# declared_classvar.py
from typing import ClassVar
from exceptions import expected

class Registry:
    count: ClassVar[int]  # Declared, no value

with expected(AttributeError):
    print(Registry.count)
#: [AttributeError] type object 'Registry' has no attribute
#: 'count'

Registry.count = 0  # The assignment creates it
print(Registry.count)
#: 0
print(Registry().count)  # Found by fallback
#: 0
```

`count: ClassVar[int]` records that a count belongs to `Registry`,
and no attribute exists until something assigns one,
so the first read raises an `AttributeError`.
The type checker (`ty`) reports nothing here,
for the reason it reports nothing for `label`.
It trusts the declaration rather than tracking which code runs first.
Pyright agrees: its optional `reportUninitializedInstanceVariable` rule checks instance variables,
not a `ClassVar`, so neither checker catches this read.
`Registry.count = 0` creates the attribute on the class,
and an instance finds it by fallback.

In every case the value creates the attribute.
An annotation states the type, and `ClassVar` adds where the attribute belongs,
while the `= 0` brings it into existence.
That holds for `label: str`, for `total: ClassVar[int] = 0`,
and for the `count` in `declared_classvar.py`.

### A Base Class Declares, a Subclass Supplies

Declaring a `ClassVar` and leaving the value elsewhere is deliberate,
and the common case is a base class naming what its subclasses must supply:

```python
# required_classvar.py
from typing import ClassVar
from exceptions import expected

class Shape:
    sides: ClassVar[int]  # Subclasses supply it

class Square(Shape):
    sides = 4

class Blob(Shape):
    pass

print(Square.sides)
#: 4
with expected(AttributeError):
    print(Blob.sides)
#: [AttributeError] type object 'Blob' has no attribute
#: 'sides'
```

`Shape` states that every shape carries a `sides`, `Square` supplies one,
and `Blob` forgets.
A [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
declares its attributes in the same form, an annotation with no value,
since it describes what a class must have and leaves the value to the class.

`ty` 0.0.84 enforces less than the declaration states.
Nothing requires `Blob` to supply a `sides`,
and a subclass `Bad` that writes `sides = "four"` draws no report.
`ty` reads that assignment as a fresh declaration and types `Bad.sides` as `str`,
so the error surfaces later, wherever the code requires an `int`.
Pyright rejects the assignment where it sits,
and the typing specification agrees with Pyright.
A mutable attribute's type is [invariant](08_Foundations--Static_Types.md#variance),
so a subclass may neither widen nor narrow it.
The gap is `ty`'s, and a known one.
`ty` tracks the check under "Enforce the Liskov Substitution Principle for non-methods"
(`astral-sh/ty` issue 2158).
Treat the base declaration as documentation that a checker reads,
not as a guarantee that the attribute exists.

### What `ClassVar` Catches

`ClassVar` is a hint for the type checker.
It records that `total` belongs to the class,
and turns the accidental shadowing from `class_attribute_confusion.py` into a check-time error.
Python's own attribute lookup ignores the hint.
`@dataclass` does read it at runtime.
It [leaves a `ClassVar` field out](12_Techniques--Data_Classes_as_Types.md#d-a-real-classvar)
of the constructor it generates.

At runtime an assignment does the same thing with or without `ClassVar`:

```python
# counter_near_miss.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1  # type: ignore

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
```

`self.total += 1` expands to `self.total = self.total + 1`.
The read falls back to the class and finds `0`.
The write creates a fresh `total` on the instance.
Every `Tally` counts itself once and the shared counter stays at `0`.
The write through `self` is why `class_var.py` increments through the class name,
`Tally.total += 1`.

`ClassVar` does catch this mistake, at check time.
`ty` rejects the augmented form as it rejects a direct `self.total = 5`,
reporting "Cannot assign to ClassVar `total` from an instance of type `Tally`" for a write like `a.total = 99`,
and naming the type of `self` where the write sits inside `__init__()`.
The `# type: ignore` suppresses that report so the listing can show what the line does when it runs.

Shared storage is right when you intend the sharing.
A count of every object created, a registry mapping names to classes,
and a constant that all instances read but none change are all class attributes,
and each reads better when you declare the sharing.
`Tally.total` is the first of these.
For the third, a class-level constant,
[`Final[int]`](08_Foundations--Static_Types.md#constants-with-final)
says more than `ClassVar[int]`.
`Final[int]` declares the value both shared and not reassignable.
Use `ClassVar` when you intend the shared value to change,
as `Tally.total` does.
The bug is not the class attribute.
It is writing one where you meant a per-object default.

## ClassVar and Inheritance

Subclasses inherit a `ClassVar` declared on a base class like any other class attribute.
A subclass that doesn't declare its own copy reads through to the base's value,
via the normal [method resolution order](07_Foundations--Classes.md#method-resolution-order).
A subclass that assigns its own value creates a separate class attribute,
independent of the base and of sibling subclasses:

```python
# class_var_inheritance.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Left.shared, Right.shared)
#: 0 100
# Only affects subclasses that haven't overridden
Base.shared = 9
print(Left.shared, Right.shared)
#: 9 100
# Creates Left's own attribute, doesn't touch Base
Left.shared = 5
print(Base.shared, Left.shared, Right.shared)
#: 9 5 100
```

`Left` has no `shared` of its own,
so it tracks `Base.shared` until something assigns to `Left.shared`.
`Right` overrides `shared` at class-definition time,
so it keeps `100` when `Base.shared` changes.
`ClassVar` leaves all of that alone.
It tells the type checker that `shared` belongs to the class,
and says nothing about whether subclasses share storage.
Attribute lookup on a subclass is the shadowing rule from `class_attribute_confusion.py`,
one level up.
`Left` reads through to `Base` until an assignment gives `Left` its own copy,
the way `a` reads through to `Stars` until `a.rating = 1`.

`Right` writes `shared = 100` without repeating the annotation.
Under `ty`, that bare override loses the guard against instance assignment.
`ty` rejects `Left().shared = 5` and accepts `Right().shared = 5`.
Pyright carries the base's declaration to the override and rejects both.
Restating `ClassVar[int]` on an override keeps the check under either checker.

### `type(self)` Forks the Counter

The mistake in `counter_near_miss.py` has a subclass form.
`class_var.py` increments `Tally.total` through the literal class name.
Writing that same increment through `type(self)`,
a common idiom for naming the instance's class from a method,
forks the counter once the base class has subclasses,
the same way `Right` forks `shared`:

```python
# classvar_fork.py
from typing import ClassVar

class Base:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        type(self).total += 1  # Looks like Base.total += 1

class Sub(Base):
    pass

Base()  # [1]
Sub()  # [2]
Sub()  # [3]
print(Base.total, Sub.total)
#: 1 3
```

`type(self)` is `Base` for the one `Base()` call and `Sub` for both `Sub()` calls.
`Base()` (`[1]`) increments `Base.total` to `1`.
The first `Sub()` (`[2]`) reads through to that `1`, adds one,
and the assignment creates `Sub.total = 2` on `Sub` alone,
the same shadowing `Right` demonstrates in `class_var_inheritance.py`.
The second `Sub()` (`[3]`) increments that separate copy to `3`.
`Base.total` stays at `1`, and the type checker reports no diagnostic.
The augmented assignment is a valid `ClassVar[int]` update either way,
and nothing in the annotation says which class name should receive it.

Write the increment through the literal class name, as `class_var.py` does,
whenever a `ClassVar` must count across every subclass rather than fork one counter per subclass.
A [`@classmethod`](07_Foundations--Classes.md#static-and-class-methods)
that writes `cls.total += 1` forks the same way,
because `cls` is the class that received the call.
[Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#the-trash-hierarchy)'s registry sidesteps the fork by mutating `Trash.registry` in place,
instead of reassigning it through `cls`.

## Real Per-Object Defaults

For real per-object defaults, write a constructor with default arguments,
or use a `@dataclass`,
which turns the class-attribute syntax into instance attribute defaults.
Each object then gets its own storage:

```python
# real_defaults.py
from dataclasses import dataclass

class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # An instance attribute, one per object

@dataclass
class B:
    x: int = 100  # Becomes a constructor default

a = A()
a.x = -1
print(a.x, A().x)  # The change in a does not leak
#: -1 100
print(B().x, B(7).x)
#: 100 7
print(vars(B)["x"], vars(B())["x"])
#: 100 100
```

`real_defaults.py`'s `A` and `inside_objects.py`'s `A` both start `x` at `100`,
and the two behave in opposite ways.
In `inside_objects.py` the `100` lives on the class and every instance reads it.
In `real_defaults.py` it is a default argument,
and `self.x = x` runs on every construction,
giving each object its own storage before anything can read it.

Python still builds the [default value](05_Foundations--Functions.md#the-mutable-default-trap)
once, at definition time, so a mutable default argument brings the sharing back.
`100` is immutable, so this default is safe.

A `@dataclass` reads the annotated class-body declarations as a template and generates a constructor from them.
The annotation marks a field.
Without the decorator,
the same annotated assignment stays a shared class attribute, as `Cart` shows.
If you write `x = 100` with no `x: int`, `@dataclass` sees no field:

```python
# dataclass_no_annotation.py
from dataclasses import dataclass, fields

@dataclass
class B:
    x = 100  # No annotation, so not a field

print(fields(B))
#: ()
b = B()
print(vars(b), b.x)
#: {} 100
b.x = -1
print(vars(b), B().x)  # The same shadowing as Stars
#: {'x': -1} 100
```

The name stays an ordinary shared class attribute,
the generated `__init__()` takes no `x`,
and neither the runtime nor the type checker complains.
`b.x = -1` shadows the class attribute for that one instance,
and an assignment through the class still changes every instance that has not shadowed it,
the hazard `Stars` demonstrates.

The annotated field in `real_defaults.py` also leaves a class attribute behind.
As its last line shows, `vars(B)` still holds `x = 100`.
The difference is the generated `__init__()`,
which assigns `self.x` on every construction,
so each object shadows the class attribute immediately and never reads the shared one.
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#data-classes)
covers the details.

## Which Dictionary?

Every attribute question in this chapter reduces to one:
which dictionary holds the value?
Assignment answers it,
and the answer depends on whether you assign through `self` or through the class name.
Decide which you want, then write the declaration that says so:
`ClassVar` for shared,
a constructor default or a `@dataclass` field for per-object.

## Exercises

Try each exercise before opening its [solution](../Solutions/09_Foundations--Class_Attributes/).

1.  In `class_attribute_confusion.py`,
    add a third instance `c = Stars()` after the `Stars.rating = 9` line,
    and print `c.rating`.
    Predict its value before running,
    then explain why it differs from `a.rating`.
2.  In `class_var_inheritance.py`,
    add a third subclass `class Middle(Base): pass` (no override, like `Left`)
    and print `Middle.shared` alongside the others at each step.
    Confirm `Middle` tracks `Base` the way `Left` does.
3.  In `real_defaults.py`, create `b = B()` and assign `b.x = -1`.
    Then create a second instance, `b2 = B()`,
    and confirm `b2.x` is still `100`.
4.  Rewrite `Tally` from `class_var.py` so `total` is a plain (non-`ClassVar`)
    class attribute instead, then assign `a.total = 99` through an instance.
    Using `vars()` as in `inside_objects.py`,
    explain what that assignment creates, and where.
5.  Rewrite `Cart` from `shared_mutable.py` as a `@dataclass` with `items: list[str] = field(default_factory=list)`,
    importing `field` from `dataclasses`.
    [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared)
    covers `default_factory`.
    This exercise needs only the one expression given here.
    Repeat the `append` and confirm `b.items` stays empty.
    Then try the same class with `items: list[str] = []` and report what `@dataclass` does about it.
6.  In `inside_objects.py`, add `del a.x` after the final `print`,
    then print `vars(a)` and `a.x` again.
    Predict both before running.
    Then run `del a.x` a second time and explain the exception,
    given what `vars(A)` still holds.
7.  In `counter_near_miss.py`,
    print `vars(a)` and `vars(Tally)["total"]` after constructing both instances,
    and use them to explain the `1 1 0` output.
    Then fix the class so the shared counter moves,
    without changing the `ClassVar` declaration,
    and explain what the type checker reports when you remove the `# type: ignore` from the broken version.
8.  Change `class_var_inheritance.py` so `shared` is `ClassVar[list[int]] = []`,
    delete `Right`'s `shared = 100`,
    and have `Left` and `Right` both call `.append()` on it.
    Predict what `Base.shared` holds afterwards, then check.
    Give `Right` its own list with `shared = []` in its body and repeat.
9.  Write a class `Ticket` with a bare annotation `seat: str` and an `__init__()` that stores a `holder` and leaves `seat` unassigned.
    Run `ty` on it, then read `seat` on an instance inside `expected(AttributeError)`.
    Assign `seat` from outside the class and print `vars()` of the instance before and after.
10. In `classvar_fork.py`,
    print `vars(Sub).get("total")` before the first `Sub()` call and after each one,
    and use the three values to explain the `1 3` output.
    Then change the increment to `Base.total += 1` and predict all four lines before running.
