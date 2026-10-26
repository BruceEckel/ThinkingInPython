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
Apart from `__slots__`, which comes up below,
no syntax in a Python class body allocates a per-object field.
Assigning through `self` inside a method creates that storage,
as `self.x = x` in a constructor does.

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
`vars()` returns an object's own attribute dictionary, its `__dict__`,
so inspecting the class with `vars(A)` and the instance with `vars(a)` shows the split:

```python
# inside_objects.py

class A:
    x = 100

a = A()
print(vars(a), a.x)  # Empty, so a.x comes from the class
#: {} 100
a.x = 1
print(vars(a), a.x)  # Assignment created it on the instance
#: {'x': 1} 1
print(vars(A)["x"])  # The class entry is unchanged
#: 100
```

The listing subscripts `vars(A)` instead of printing it whole,
because a class's dictionary also holds entries the compiler adds,
such as `__module__` and `__doc__`.
That dictionary is a read-only `mappingproxy`,
so writing to it raises a `TypeError`.
To change the entry, assign through the class name,
or call `setattr(A, "x", 5)` when the name arrives as a string.
The instance dictionary is a plain `dict` holding what the code assigned,
and that alone.

Slots can replace that instance dictionary.
A class gets them by declaring [`__slots__`](18_Techniques--Performance.md#slots),
and a data class gets them from `slots=True`.
Each instance then holds one slot per declared name in place of a `__dict__`,
provided every base class declares slots too.
An instance of such a class cannot shadow a class attribute.
Assigning to the class attribute's name on the instance raises an `AttributeError`,
because the instance has no dictionary to hold the new attribute.

A method is a class attribute like any other.
`def show(self):` in a class body stores a function object in the class dictionary,
and `a.show()` finds it by the same fallback that finds `a.x`:
the instance first, then the class.
Because the class dictionary holds the method,
assigning `a.show = something` shadows the method for `a` alone.
The inspection helper `display_object()` that [Classes](07_Foundations--Classes.md)
introduces reports attributes and methods separately,
but the same class dictionary holds both.

Some class attributes follow a different rule.
A [`@property`](07_Foundations--Classes.md#properties)
stored on the class takes precedence over the instance dictionary for its name,
so reading that name calls its getter and assigning to it calls its setter.
The setter stores its value in the instance dictionary under a different name,
as `Circle`'s `radius` setter stores `_radius`.

### The Bug Surfaces Far from Its Cause

A class attribute behaves like a default until someone assigns to an attribute of the same name on one instance.
After that, every other object reads the new value when the class attribute changes,
while the object that assigned keeps its own value.
The program reads the wrong value far from the line that caused it,
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

Someone debugging the stale `1` finds `rerate()` and `show()` both correct.
The cause is the assignment inside `sell()`,
which gave `a` its own `rating` before the class attribute changed.
Neither `rerate()` nor `show()` calls `sell()`,
so finding the assignment means tracing every earlier call that used a `Stars` instance.

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
a.items += ["pear"]  # Mutates, then assigns
print(a.items, b.items)
#: ['apple', 'pear'] ['apple', 'pear']
a.items = ["plum"]  # Rebinds a's own attribute
print(a.items, b.items)
#: ['plum'] ['apple', 'pear']
```

`a.items.append("apple")` reads `items`, finds `a`'s own dictionary empty,
falls back to the class, and mutates the one list stored there.
Shadowing starts with an assignment.
`.append()` leaves `a`'s dictionary empty,
so `b.items` reads the same list and holds the apple too.
The type checker also accepts the line,
since `a.items.append("apple")` is a correct call on a `list[str]`.

An augmented assignment both mutates and assigns.
`a.items += ["pear"]` mutates the shared list through `__iadd__()`,
so `b.items` holds the pear too.
The augmented assignment then stores that same list on `a`,
creating an instance attribute that shadows the class list.
Because both attributes refer to one list, the two printed values match.

A per-object list belongs in `__init__()`,
as [Real Per-Object Defaults](#real-per-object-defaults) shows,
or in a `@dataclass` field with a [`default_factory`](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared).

## Declaring Shared State with ClassVar

When you intend one shared value, say so with `ClassVar` from `typing`.
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

`display_object(Tally)` shows `total` on the class and no `label`.
`label` first appears in `display_object(a)`, on the instance.
An assignment in the class body creates a class attribute,
as `class_attribute_confusion.py` shows.
`total: ClassVar[int] = 0` has the `= 0`,
so it exists on `Tally` before any instance exists.
`label: str` has no `=`, so it stays a declaration.
The annotation goes into `Tally.__annotations__` beside `total`'s entry and records that a `Tally` will carry a `label`.
`display_object()` reports attributes that exist,
so the declaration stays out of its report.

Constructing `a` runs `self.label = label`,
which creates a real `label` attribute on `a`, not on `Tally`.
`display_object(a)` reports `total` too, by fallback.
Reading an attribute checks the instance first, then the class,
the rule `Stars` demonstrates in `class_attribute_confusion.py`.
The `total` that `a` reports is `Tally.total`.
The `[CV]` tag marks an attribute the class stores.
It stands for "class variable," another name for a class attribute.
`label`, stored on `a`, carries no `[CV]`, while `total`, found by fallback,
keeps it.

### A Bare Annotation Declares, It Does Not Create

A *bare annotation*, one with no assigned value,
is a declaration rather than a placeholder.
In `class_var.py`, `label: str` states that every `Tally` carries a `label` attribute of type `str` and leaves the assignment to other code.
If no method assigns `self.label`, no attribute exists,
on the instance or the class.
The type checker takes the annotation as the attribute's declaration.
It never checks whether some method sets the attribute,
so it accepts every read of `label`.
The first code that reads `label` raises an `AttributeError`.

The annotation on `label` is optional here.
If you delete it, the type checker still infers `label: str` correctly from `self.label = label`,
because the checker gives the attribute the type of the parameter assigned to it.
The annotation stays for symmetry with `total`,
so both names appear at the top of the class,
instead of `label` appearing first inside the constructor.
[Simulation](38_Patterns--Simulation.md#rooms-robots-and-the-item-factory)
shows the case that requires the annotation.
There, code outside the class makes the first assignment,
and the assignment inside `move()` reads the attribute it sets,
so the bare annotation is the type checker's one source for its type.

### A `ClassVar` With No Value Declares Too

`ClassVar` declares that the class holds an attribute,
and leaves creating it to an assignment.
A `ClassVar` with no value stays a declaration,
the same as `label` in `class_var.py`:

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

`count: ClassVar[int]` records that a count belongs to `Registry`.
No attribute exists until something assigns one,
so the first read raises an `AttributeError`.

The type checker (`ty`) accepts that first read,
for the reason it accepts a read of `label`.
It checks the declaration's type and ignores which code runs first.
Pyright accepts the read too.
Its optional `reportUninitializedInstanceVariable` rule checks instance variables,
not a `ClassVar`.

An annotation states the type, and `ClassVar` adds where the attribute belongs.
The assignment creates the attribute.
That holds for `label: str`,
which `self.label = label` creates on each instance,
for `total: ClassVar[int] = 0`,
and for the `count` that `Registry.count = 0` creates in `declared_classvar.py`.

### A Base Class Declares, a Subclass Supplies

A `ClassVar` with no value usually appears in a base class,
declaring what its subclasses must supply:

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

A [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
declares its attributes in the same form as `Shape`, a bare annotation,
since it describes what a class must have and leaves the value to the class.

`ty` 0.0.91 enforces what the declaration states about the value.
A subclass that writes `sides = "four"` draws `invalid-assignment` on that line,
since the checker compares the value with the declared `ClassVar[int]`.
A subclass that redeclares the attribute as `sides: ClassVar[str] = "four"` draws `invalid-attribute-override`.
A subclass that narrows the type, as `sides: ClassVar[bool] = True` does,
draws `invalid-mutable-override`.
A mutable attribute's type is [invariant](08_Foundations--Static_Types.md#variance),
so a subclass must keep the type it inherits.

One mistake passes the checker.
The checker accepts `Blob` as written,
because it trusts the declaration that `sides` exists.
Treat the base declaration as documentation that a checker reads,
not as a guarantee that the attribute exists.

### What `ClassVar` Catches

`ClassVar` is a hint for the type checker.
It records that `total` belongs to the class,
so the type checker reports an assignment to `total` through an instance as an error.
That assignment is the shadowing `class_attribute_confusion.py` performs unchecked on `Stars.rating`.
Python's attribute lookup ignores the hint.
`@dataclass` does read it at runtime,
and leaves a `ClassVar` out of the fields it generates.

At runtime an assignment through `self` creates an instance attribute with or without `ClassVar`:

```python
# self_increment.py
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
The write through `self` is why `class_var.py` increments through the class name,
`Tally.total += 1`.

With `ClassVar`, the type checker reports this mistake before the program runs.
The checker rejects the augmented form as it rejects a direct `self.total = 5`.
For a write like `a.total = 99`,
`ty` reports "Cannot assign to ClassVar `total` from an instance of type `Tally`".
Inside `__init__()` the message names the type of `self` in place of `Tally`.
The `# type: ignore` suppresses that report so the listing can show what the line does when it runs.

Shared storage is right when you intend the sharing.
The bug is not the class attribute.
It is writing one where you meant a per-object default.
Three kinds of value commonly belong in class attributes:
a count of every object created, a registry mapping names to classes,
and a constant that all instances read but none change.
Declare the sharing for each,
so the type checker reports an instance assignment that would shadow it.
`Tally.total` is the first of these.

For the third kind, a class-level constant,
[`Final[int]`](08_Foundations--Static_Types.md#constants-with-final)
says more than `ClassVar[int]`.
`Final[int]` declares the value both shared and constant.
Use `ClassVar` when you intend the shared value to change,
as `Tally.total` does.

## ClassVar and Inheritance

Subclasses inherit a `ClassVar` declared on a base class like any other class attribute.
A subclass reads through to the base's value,
via the normal [method resolution order](07_Foundations--Classes.md#method-resolution-order),
until it assigns its own.
That assignment creates a separate class attribute,
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

print(Base.shared, Left.shared, Right.shared)
#: 0 0 100
Base.shared = 9
print(Base.shared, Left.shared, Right.shared)
#: 9 9 100
Left.shared = 5
print(Base.shared, Left.shared, Right.shared)
#: 9 5 100
```

Attribute lookup on a subclass is the shadowing rule from `class_attribute_confusion.py`,
one level up.
`Left` reads through to `Base` until an assignment gives `Left` its own copy,
the way `a` reads through to `Stars` until `a.rating = 1`.

`ClassVar` leaves that lookup alone.
It tells the type checker that `shared` belongs to the class.
Attribute lookup alone decides whether subclasses share storage.
`Right` writes `shared = 100` and leaves the annotation to `Base`.
The override is still a `ClassVar`.
The type checker applies the base's declaration to it,
so the checker rejects `Right().shared = 5` as it rejects `Left().shared = 5`.

### `type(self)` Forks the Counter

The mistake in `self_increment.py` has a subclass form.
`class_var.py` increments `Tally.total` through the literal class name.
Methods often write `type(self)` to name the instance's class.
Writing the same increment through `type(self)` forks the counter when the base class has subclasses,
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
print(Base.total, Sub.total)
#: 1 1
Sub()  # [2]
print(Base.total, Sub.total)
#: 1 2
Sub()  # [3]
print(Base.total, Sub.total)
#: 1 3
```

`type(self)` is `Base` for the one `Base()` call and `Sub` for both `Sub()` calls.
`Base()` (`[1]`) increments `Base.total` to `1`.
`Sub.total` reads through to that `1`.
The first `Sub()` (`[2]`) reads the same `1` and adds one.
The assignment creates `Sub.total = 2` on `Sub` alone,
the same shadowing `Right` demonstrates in `class_var_inheritance.py`.
The second `Sub()` (`[3]`) increments that separate copy to `3`.

The type checker accepts every line.
The augmented assignment is a valid `ClassVar[int]` update either way,
and the annotation leaves open which class name should receive it.

Write the increment through the literal class name, as `class_var.py` does,
whenever a `ClassVar` must count across every subclass rather than fork one counter per subclass.
A [`@classmethod`](07_Foundations--Classes.md#static-and-class-methods)
that writes `cls.total += 1` forks the same way,
because `cls` is the class that received the call.
[Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#the-trash-hierarchy)'s registry avoids the fork by mutating one dictionary in place.
`Trash.registry[cls.__name__] = cls` assigns into the dictionary,
not to an attribute of `cls`, so every subclass shares the one registry.

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

print(vars(A()), A(7).x)  # Each instance holds x
#: {'x': 100} 7
print(B().x, B(7).x)
#: 100 7
print(vars(B)["x"], vars(B())["x"])
#: 100 100
```

`real_defaults.py`'s `A` and `inside_objects.py`'s `A` both start `x` at `100`.
The two behave in opposite ways.
In `inside_objects.py` the class holds the `100` and every instance reads it.
In `real_defaults.py` the `100` is a default argument,
`__init__(self, x: int = 100) -> None`.
`self.x = x` runs on every construction,
giving each object its own storage before anything can read it.
`vars(A())` prints `{'x': 100}`,
where `inside_objects.py`'s `vars(a)` prints `{}` until `a.x = 1` runs.

Python still builds the [default value](05_Foundations--Functions.md#the-mutable-default-trap)
once, at definition time,
so every construction that relies on a mutable default argument shares one object.
`100` is immutable, so this default is safe.

A `@dataclass` reads the annotated class-body declarations as a template and generates a constructor from them.
Without the decorator,
an annotated assignment such as `B`'s `x: int = 100` stays a shared class attribute,
as `Cart` shows.
The annotation marks a field.
If you write `x = 100` with no `x: int`, `@dataclass` creates no field:

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
so the generated `__init__()` is `__init__(self)`.
Neither Python nor the type checker reports an error.
An assignment through the class changes every instance that falls back to the class,
the hazard `Stars` demonstrates.

The annotated field in `real_defaults.py` also leaves a class attribute behind.
As its last line shows, `vars(B)` still holds `x = 100`.
The difference is the generated `__init__()`,
which runs `self.x = x` on every construction.
Each object therefore shadows the class attribute immediately and always reads its own value.
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#data-classes)
shows the `__init__()`, `__repr__()`,
and `__eq__()` that `@dataclass` generates.

## Which Dictionary?

Every attribute question in this chapter reduces to one:
which dictionary holds the value?
Assignment answers it.
Assigning through `self` writes the instance's dictionary,
and assigning through the class name writes the class's dictionary.
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
    add a third subclass `class Middle(Base): pass`
    (no shadowing `shared`, like `Left`)
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
7.  In `self_increment.py`,
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
    and use the three values to say which class's dictionary supplies each `Sub.total` the listing prints.
    Then change the increment to `Base.total += 1` and predict every line before running.
