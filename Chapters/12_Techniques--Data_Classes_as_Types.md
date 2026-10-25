# Data Classes as Types

> A value can be wrong, and every function that receives it checks again.
> A data class that refuses illegal values moves that check into the type.

A *type* is a set of values.
The type `int` is the set of whole numbers.
A type you define, like a rating from one to ten, is a smaller set:
the allowed values.
Programmers have historically been bad at keeping objects inside that set.
Constructing or mutating an object in an illegal state is too easy.
Defensive checks then spread through your code.

Frozen data classes offer a better approach.
You validate the value once, at construction, and freeze it so it cannot change.
The type then guarantees that every object is a legal value.
Code that receives one need not check it again.
This material comes from my PyCon 2022 talk,
[Making Data Classes Work for You](https://www.youtube.com/watch?v=w77Kjs5dEko).

## `check()` and `TypeFailure`

`check()` raises `TypeFailure` when its condition is false.
`TypeFailure` is a custom exception meaning a value falls outside the type's allowed set:

```python
# validation.py
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)
```

An exception is a value like any other, and the values it carries deserve names.
[`@dataclass`](#data-classes) generates the constructor that stores them,
`__init__(self, subject: str, reason: str = "")`.
`subject` is the rejected value as the caller rendered it, such as `Stars(11)`.
`reason` explains the rejection when the name alone does not,
such as `needs an @`.
A handler can read `e.subject` and `e.reason` rather than parsing them from the exception text.

`check()` uses a `raise` statement instead of `assert 1 <= stars <= 10`.
Python strips every `assert` when you run with `-O` or `-OO`.
`assert` is a debugging aid for an invariant the program's own logic guarantees,
so the optimizer may remove it.
Under those flags, validation written with `assert` disappears silently and lets in the illegal values this chapter exists to keep out.
A value that arrives from outside the program needs a check that stays.
No flag removes a `raise`.

`eq=False` turns off the generated `__eq__()`, for two reasons.
A mutable data class that defines `__eq__()` [sets `__hash__` to `None`](#data-classes).
Putting an unhashable exception in a set raises a `TypeError`.
Identity is the correct comparison for an exception.
Two failures carrying the same text are still two separate failures.

## A Value to Check Everywhere

Suppose a "stars" rating is an integer from one to ten.
If you represent it as an `int`, a caller can pass eleven, or minus one.
To prevent that, every function that takes a rating must check it:

```python
# stars_unchecked.py
from validation import check

def f1(stars: int) -> int:
    # Check the argument here...
    check(1 <= stars <= 10, f"f1({stars})")
    return stars + 5

def f2(stars: int) -> int:
    # ...and again in every other function
    check(1 <= stars <= 10, f"f2({stars})")
    return stars * 5

def f3(stars: int) -> int:  # The check is missing here
    return stars * 100

rating = 6
print(f1(rating))
#: 11
print(f2(rating))
#: 30
print(f3(11))
#: 1100
```

Each function duplicates the check, the check is easy to forget,
and the type system is no help.
The `int` annotation says "any integer,"
a far larger set than the ratings you mean.
`f3()` shows a forgotten check.
`11` lies outside the legal range.
Nothing objects: not the annotation, not the type checker,
not the running program.
`f3(11)` returns 1100, beyond anything a legal rating produces,
and the caller receives it as if it were fine.

A check that is present still tests only the argument and leaves the result unchecked.
`f1(6)` returns 11, outside the range of a rating.

## A Class Is Not a Type

The object-oriented answer is to wrap the value in a class and validate it in the constructor.
The constructor then rejects an illegal starting value,
but the value is still mutable.
Every method that changes it must re-validate,
and a method can leave the object in an illegal state between steps:

```python
# stars_class.py
from exceptions import expect
from validation import TypeFailure, check

class Stars:
    def __init__(self, number: int) -> None:
        self._number = number  # Private by convention
        self._validate()

    def _validate(self) -> None:
        check(1 <= self._number <= 10,
              f"Stars({self._number})")

    @property
    # No setter: blocks external mutation
    def number(self) -> int:
        return self._number

    def __str__(self) -> str:
        return f"Stars({self._number})"

    def f1(self) -> int:
        self._number = self._number + 5
        self._validate()  # Postcondition
        return self._number

damaged = Stars(8)
print(damaged)
#: Stars(8)
expect(TypeFailure, damaged.f1)
#: [TypeFailure] Stars(13)
print(damaged)
#: Stars(13)
```

A read-only `@property` keeps users from assigning to `number`.
The object's own methods still mutate `_number`,
so `f1()` must re-check the result before returning it.
That check runs after the mutation,
so it reports the illegal value instead of preventing it.
After the caller catches the `TypeFailure`,
the object still holds that illegal value.

The order is a choice, not something mutation forces.
`f1()` could check the sum before assigning it,
and then `damaged` stays `Stars(8)` instead of holding a corrupted `13`.
With mutation, every method must check before it assigns,
every time it changes the value.
`f1()` here gets that order wrong.

*Design by Contract* (DbC)
is the practice of checking arguments on entry and results on exit,
with a class invariant that must hold between calls.
`f1()` takes no argument, so only the postcondition appears here.
A method that accepts a second rating needs a precondition for it as well.

DbC spreads the contract across every method that touches the value.
The invariant is the part this chapter replaces.
`_validate()` states it, and every mutating method must remember to call it.
Those calls are the same scattering of checks as before,
but moved inside the class.
The class encapsulates the value, but `_number` can still hold any `int`,
legal or not.

Some values must change in place over their lifetime: a counter,
a connection's open-or-closed state, a running total.
You cannot always replace one with a fresh instance on every change.
For those, accept DbC's scattered checks, because the value must stay mutable.
The accepted answer is a validating setter that checks before it assigns,
whereas `stars_class.py`'s `f1()` assigns first.
The rest of this chapter prefers the other case, where a fresh,
validated instance can replace the old one.
[Immutability](#immutability) begins that approach.

## Data Classes

A *data class* removes the boilerplate from a class that holds data.
The `@dataclass` decorator generates `__init__()`, `__repr__()`,
and `__eq__()` from the fields you declare:

```python
# messenger.py
from dataclasses import dataclass

@dataclass
class Messenger:
    name: str
    number: int
    depth: float = 0.0
```

[`display_object()`](17_Techniques--Metaprogramming.md#building-display_object),
the inspection helper, shows what `@dataclass` generates:

```python
# display_messenger_class.py
from display import INTERESTING_DUNDERS, display_object
from messenger import Messenger

display_object(Messenger, INTERESTING_DUNDERS)
#: [Attributes]
#:   • __hash__ = None [CV]
#:   • depth: float = 0.0 [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, name: str, number: int, depth: floa...
#:   • __repr__(self)
```

The trailing `...` is `display_object()` trimming that line to its report width.

`__hash__` is `None`.
A mutable `@dataclass` compares by value with `__eq__()`,
so a hash that agreed with that comparison would change whenever a field changed.
`@dataclass` sets `__hash__` to `None` instead,
which makes the instances unhashable.
An unhashable instance cannot go in a `set` or serve as a `dict` key.

As [Class Attributes](09_Foundations--Class_Attributes.md) explains,
`depth` is the one field of the three that appears as an attribute,
because it has an initialization value.
`name` and `number` declare a type alone.

```python
# demo_messenger.py
from dataclasses import replace
from messenger import Messenger

m = Messenger("iris", 12, 3.14)
print(m)
#: Messenger(name='iris', number=12, depth=3.14)

# The generated __eq__ compares by field value:
print(Messenger("iris", 1) == Messenger("iris", 1))
#: True
print(Messenger("iris", 1) == Messenger("iris", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='iris', number=12, depth=3.14)
print(mc)
#: Messenger(name='iris', number=12, depth=9.9)

m.name = "hermes"  # Data classes are mutable by default
print(m)
#: Messenger(name='hermes', number=12, depth=3.14)
```

`print(m)` uses the generated `__repr__()`.

`replace()` returns a copy with some fields changed, leaving the original alone.
Copying instead of mutating reduces errors.
[`copy.replace()`](#the-general-form-of-replace)
does the same for any object that defines `__replace__()`,
data classes included.

`display_object()` shows the attributes with their declared types:

```python
# display_messenger.py
from display import display_object
from messenger import Messenger

display_object(Messenger("iris", 12, 3.14))
#: [Attributes]
#:   • depth: float = 3.14
#:   • name: str = 'iris'
#:   • number: int = 12
#: [Methods]
#:   None
```

With its default, an empty `dunder` list,
`display_object()` leaves out every dunder,
including the generated `__init__()`, `__repr__()`, and `__eq__()`.

## Comparing Ordinary Classes and Data Classes

`Messenger` shows what `@dataclass` produces,
but not what adding the decorator changes.
Four small classes isolate that change, one step at a time:

- `A` is an ordinary class with bare annotations.
- `B` adds default values but no constructor.
- `C` is a `@dataclass`.
- `D` adds a `ClassVar` field alongside an ordinary one.

The same helper inspects each one:

```python
# comparison.py
from display import REDEFINED_DUNDERS, display_object

def show(obj: object) -> None:
    display_object(obj, REDEFINED_DUNDERS,
                   exclude=("__hash__",))
```

`show()` calls `display_object()` with `REDEFINED_DUNDERS`,
so each report lists which of `__init__()`, `__repr__()`, `__eq__()`,
and `__hash__` differ from `object`'s versions.
For clarity, `show()` also excludes [`__hash__`](#data-classes)
from these reports.

### `A`: Annotations Only

`A` is the simplest case, with no defaults and no constructor,
but with field declarations that look like class variables:

```python
# ordinary_class.py
from comparison import show
from exceptions import expect

class A:
    x: int
    s: str

show(A())
#: [Attributes]
#:   None
#: [Methods]
#:   None

print(A.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
expect(AttributeError, getattr, A(), "x")
#: [AttributeError] 'A' object has no attribute 'x'
```

`A` inherits `__init__()`, `__repr__()`, `__eq__()`,
and `__hash__()` from `object`,
so `show(A())` reports none of them as redefined.

`x` and `s` in `A` are *bare annotations*: declared, but not assigned a value.
A [bare annotation](09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create)
is a declaration rather than a placeholder.
The two annotations record in `A.__annotations__` that some future `A` will carry an `x` and an `s`.
Python allocates the storage when code assigns a value.
`A` has no `__init__()` to assign them,
so neither the class nor the instance holds an `x` or an `s`.

### `B`: Class-Level Defaults

`B` adds default values to `x` and `s`.
The assignments allocate storage,
so the two turn from bare annotations into class variables:

```python
# class_with_defaults.py
from comparison import show

class B:
    x: int = 42
    s: str = "Answer"

show(B())
#: [Attributes]
#:   • s: str = 'Answer' [CV]
#:   • x: int = 42 [CV]
#: [Methods]
#:   None
```

The `[CV]` tags in `show(B())` mark both as class variables.
`B` has no `__init__()` to copy them onto each instance,
so every `B` object reads the same two values straight from the class attributes.

### `C`: The Same Annotations, Decorated

`C` is `A` decorated with `@dataclass`:

```python
# plain_dataclass.py
from dataclasses import dataclass, fields
from comparison import show

@dataclass
class C:
    x: int
    s: str

show(C(11, "this is C"))
#: [Attributes]
#:   • s: str = 'this is C'
#:   • x: int = 11
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, s: str) -> None
#:   • __repr__(self)

print("x" in C.__dict__, [f.name for f in fields(C)])
#: False ['x', 's']
```

`show(C(11, "this is C"))` finds the same two names as `show(B())`.
Neither `x` nor `s` carries `[CV]` this time.
Because `C` is a `@dataclass`,
its generated `__init__(self, x: int, s: str) -> None` runs `self.x = x` and `self.s = s` for every new `C`.
Each `C` instance owns its own copies from the moment of construction.
`B` has no `__init__()`, so `show(B())` finds `x` and `s` on the class,
tagged `[CV]`, no matter how many `B` instances exist.

`C` starts from the same bare annotations as `A`.
`@dataclass` reads them, in order, and writes one parameter (`x: int`)
and one assignment (`self.x = x`) per field.
`dataclasses.fields()` reports the field list `@dataclass` recorded.
`@dataclass` leaves a field with no default off the class,
so `x` is still absent from `C.__dict__` after decoration, as it was before.
`@dataclass` leaves the annotations as they were and adds an `__init__()` that acts on them.

### `D`: A Real `ClassVar`

`D` adds a real `ClassVar` alongside an ordinary field:

```python
# classvar_dataclass.py
from dataclasses import dataclass
from typing import ClassVar
from comparison import show
from exceptions import expect

@dataclass
class D:
    x: int = 99
    s: ClassVar[str] = "Initializer"
    f: ClassVar[float]  # No initializer

show(D)
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'Initializer' [CV]
#:   • x: int = 99 [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)

print(vars(D()))
#: {'x': 99}

for k, v in D.__annotations__.items():
    print(f"'{k}': {v}")
#: 'x': <class 'int'>
#: 's': typing.ClassVar[str]
#: 'f': typing.ClassVar[float]
expect(AttributeError, getattr, D, "f")
#: [AttributeError] type object 'D' has no attribute 'f'
```

`show(D)` tags both attributes `[CV]`, since it inspects the class,
where both live.
`vars(D())` returns an instance's own `__dict__`, which holds `x` alone.
The `__init__()` that `@dataclass` generates decides which attributes the instance receives.

`x` is an ordinary field,
so the generated `__init__()` assigns it to each instance.
That assignment puts `'x': 99` in the instance's `__dict__`.

`s`, declared `ClassVar[str]`, behaves differently.
`__init__(self, x: int = 99) -> None` takes `x` and leaves `s` out,
so `s` stays on `D`, and every `D` object reads it from the class.

`f: ClassVar[float]` appears in neither `show(D)` nor `vars(D())`.
It has no initializer, so it is a bare annotation, like `x` and `s` in `A`.
The declaration lives in `D.__annotations__` alone.
`expect()` shows that `D.f` raises an `AttributeError`,
for the same reason `A().x` does.
Assigning a value creates the attribute.
Declaring it `ClassVar` does not.

## Immutability

Passing `frozen=True` makes the data class immutable.
Assigning to a field raises `FrozenInstanceError`.
A frozen instance is also hashable,
so it can serve as a dictionary key or go in a set.
`frozen=True` removes the mutability that left `Messenger`'s `__hash__` as `None`,
so `@dataclass` generates one from the fields:

```python
# frozen_messenger.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(frozen=True)
class Messenger:
    name: str
    number: int
    depth: float = 0.0

m = Messenger("iris", 12, 3.14)
print(m)
#: Messenger(name='iris', number=12, depth=3.14)

expect(Exception, setattr, m, "name", "hermes")
#: [FrozenInstanceError] cannot assign to field 'name'

cache = {m: "Ni!"}  # Frozen instances are hashable
print(cache[m])
#: Ni!
```

Two defenses guard a frozen field.
The type checker rejects `m.name = "hermes"` before the program runs.
`frozen=True` rejects the assignment at runtime,
including in code that bypasses the type checker,
as the listing does by going through `setattr()`.

`frozen=True` guards the binding, not the object behind it.
You can still mutate a field's `list` in place.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
demonstrates that leak.
A frozen instance is hashable only when every field it holds is.
The types this chapter validates hold `int`s and `str`s,
so every field of theirs keeps its constructed value,
and every instance is hashable.
`Months` and `Line`, both later in this chapter, each hold a `list`.
Both are unhashable, and code can change either one through that list.

A frozen data class still carries a per-instance `__dict__`.
Adding `slots=True` drops it, for less memory and faster attribute access.
[Performance](18_Techniques--Performance.md#slots)
measures the memory difference.

The standard library has a second immutable type, `typing.NamedTuple`,
which also rejects assignment and hashes under the same rule.
Every field it holds must be hashable.
The two differ in equality.
A frozen data class equals another instance of its own class,
while a `NamedTuple` [equals any tuple holding the same values](28_Patterns--Data_Transfer_Objects.md#a-namedtuple-is-still-a-tuple).
They also [differ in validation](#namedtuple-cannot-validate).

If every part of an object stays as construction left it,
then validating it at construction makes it legal for its lifetime.

## A Type Is a Set of Values

If you make `Stars` a frozen data class,
you can guarantee that every `Stars` object is legal.
The generated `__init__()` calls `__post_init__()` automatically:

```python
# stars.py
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10,
              f"Stars({self.number})")

def f1(s: Stars) -> Stars:
    return Stars(s.number + 5)

def f2(s: Stars) -> Stars:
    return Stars(s.number * 5)
```

`Stars` now constrains `number` to a set of values:
the integers one through ten.
Your code makes a `Stars` by calling the constructor,
and the constructor refuses anything outside that set.
(Copying and unpickling [skip the constructor](#copy-skips-the-constructor).)
If you hold a `Stars`, it is legal.
You know it without checking.

That guarantee changes how you write the functions.
`f1()` and `f2()` both declare `(s: Stars) -> Stars`,
and their bodies hold the arithmetic alone.
Every `Stars` argument is legal,
and building the returned `Stars` runs the check on the result.

The validation lives in one place, the constructor, so it is easy to change.
Immutability keeps the fields bound to their constructed values.
When the objects in those fields are immutable too,
the whole value stays as the constructor checked it.

### The Annotation and the Check

Two checks define the set, and they run at different times.
The annotation `number: int` belongs to the type checker,
which rejects `Stars(5.5)` and `Stars("five")` before the program runs.
`__post_init__()` holds the range and runs at construction.
`@dataclass` uses an annotation to find a field and leaves enforcement to the type checker.
At runtime the range check alone tests a `float`, and `5.5` passes it:

```python
# stars_float.py
from stars import Stars

print(Stars(5.5))  # type: ignore
#: Stars(number=5.5)
```

The `# type: ignore` silences the type checker so the listing can reach the runtime result.
Because the type checker rejects a `float` argument in annotated code before the program runs,
`__post_init__()` need not repeat the annotation.
A value from outside the program is different.
Parsed JSON arrives as `Any`,
which the type checker accepts for every parameter.
A type built at that boundary therefore tests the field's type in the check as well:
`check(isinstance(self.number, int) and 1 <= self.number <= 10, ...)`.

### Normalizing a Frozen Field

`__post_init__()` can check a field but cannot assign to one.
`frozen=True` works by installing a `__setattr__()` that rejects every assignment,
including assignments in the class's own methods.
Normalizing a field in `__post_init__()` therefore raises `FrozenInstanceError`:

```python
# post_init_normalize.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(frozen=True)
class Email:
    text: str

    def __post_init__(self) -> None:
        self.text = self.text.lower()  # type: ignore

expect(Exception, Email, "Grace@Example.com")
#: [FrozenInstanceError] cannot assign to field 'text'

@dataclass(frozen=True)
class Normalized:
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.lower())

print(Normalized("Grace@Example.com"))
#: Normalized(text='grace@example.com')
```

Both defenses reject the assignment here, as they do for `frozen_messenger.py`.
The type checker reports the assignment,
and the `# type: ignore` silences it so the listing can reach the runtime failure.

`object.__setattr__()` skips the rejecting `__setattr__()` and writes the field into the instance's `__dict__`.
It works, and it says what it does.
The same call works from outside the class,
so `frozen=True` stops an accidental assignment,
not a caller determined to change the value.

The alternative is to refuse the unnormalized value and normalize before construction.
Which to choose depends on the type.
Normalizing inside makes `Normalized("A@b.com")` and `Normalized("a@b.com")` the same value,
which is usually what an email address should mean.
Refusing means the constructor stores what it receives or raises an exception,
and the caller does the cleanup.

### Parse, Don't Validate

Validating once, at construction, often goes by the name *parse,
don't validate*.^[Coined by Alexis King in her 2019 essay ["Parse, don't validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/).]
Instead of checking a changeable value everywhere and hoping you cover every spot,
you parse it once into a precise type.
After that, holding the type is proof the check passed.
No other code repeats the check, because it cannot fail.
Illegal values are unrepresentable.

Parsing once into a precise type is one aspect of [functional programming](40_Functional--Foundations.md#immutability).
Instead of mutating an object and re-guarding it,
you transform one legal value into a new legal value.
A parameter [annotated](08_Foundations--Static_Types.md#how-much-to-annotate)
`Stars` states more than a type: the value passed the check.

Four tests show that illegal values cannot exist:

- `Stars(1)` and `Stars(10)`, the ends of the range, are legal.
- The constructor rejects values outside the set.
- `f1()` and `f2()` return legal `Stars`.
- A result outside the set raises `TypeFailure` when `f2()` builds it.

```python
# test_stars.py
import pytest
from stars import Stars, f1, f2
from validation import TypeFailure

def test_legal_stars() -> None:
    assert Stars(1).number == 1
    assert Stars(10).number == 10

@pytest.mark.parametrize("n", [0, 11, -1, 100])
def test_illegal_stars_rejected(n: int) -> None:
    with pytest.raises(TypeFailure):
        Stars(n)

def test_transformations_return_legal_values() -> None:
    assert f1(Stars(2)) == Stars(7)
    assert f2(Stars(2)) == Stars(10)

def test_illegal_result_is_rejected() -> None:
    with pytest.raises(TypeFailure, match=r"Stars\(20\)"):
        f2(Stars(4))
```

## Composing Types from Types

When each small type guarantees its own values,
you can safely build larger types out of them.
A `Person` made of a legal `FullName` and a legal `EmailAddress` is legal by construction:

```python
# person.py
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class FullName:
    text: str

    def __post_init__(self) -> None:
        check(len(self.text.split()) >= 2,
              f"FullName({self.text!r})",
              "needs a first and last name")

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check("@" in self.text,
              f"EmailAddress({self.text!r})",
              "needs an @")

@dataclass(frozen=True)
class Person:
    name: FullName
    email: EmailAddress
```

`Person` declares no checks of its own.
Its annotations require a `FullName` and an `EmailAddress`,
which the type checker enforces.
Every `FullName` and `EmailAddress` is legal from construction.

`test_person_composes_validated_parts()` builds a `Person` from legal parts and reads them back.
`test_full_name_needs_first_and_last()` and `test_email_needs_at_sign()` show that the constructors reject an illegal name or email,
so every `Person` holds legal parts:

```python
# test_person.py
import pytest
from person import EmailAddress, FullName, Person
from validation import TypeFailure

def test_person_composes_validated_parts() -> None:
    person = Person(FullName("Grace Hopper"),
                    EmailAddress("grace@example.com"))
    assert person.name.text == "Grace Hopper"
    assert person.email.text == "grace@example.com"

@pytest.mark.parametrize("bad", ["Grace", "", "   "])
def test_full_name_needs_first_and_last(bad: str) -> None:
    with pytest.raises(TypeFailure):
        FullName(bad)

@pytest.mark.parametrize(
    "bad", ["grace", "example.com", ""])
def test_email_needs_at_sign(bad: str) -> None:
    with pytest.raises(TypeFailure):
        EmailAddress(bad)
```

When validation grows complicated,
libraries supply checks you would otherwise write.
The [attrs](https://www.attrs.org) library predates and inspired data classes.
It offers richer validators and converters.
[Pydantic](https://docs.pydantic.dev)
validates and parses each field according to its annotation,
which is especially useful at the edges of a program where untrusted data can enter.
The principle is the same: make the type guarantee its own values.

## Enums Are Types Too

When the set of values is small and known, the clearest type is an `Enum`.
An *enumeration* lists its members by name in the class body,
and those members are the only values the type has.

As an example, a `BirthDate` contains a month, day, and year.
`Month` is an `Enum`, because a year has a known set of twelve months.
Each month carries its length and has a method that checks a `Day` against that length.
A `BirthDate` then validates across its fields.
The day must fit the month.

```python
# birth_date.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Final
from validation import check

@dataclass(frozen=True)
class Day:
    n: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 31, f"Day({self.n})")

@dataclass(frozen=True)
class Year:
    n: int

    def __post_init__(self) -> None:
        check(1900 < self.n <= date.today().year,
              f"Year({self.n})")

DAYS: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30,
                                31, 31, 30, 31, 30, 31)

class Month(Enum):
    JANUARY = 1
    FEBRUARY = 2  # Leap years are left as an exercise
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    @property
    def max_days(self) -> int:
        return DAYS[self.value - 1]

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day)
```

The `Enum` creates the constrained set of `Month`s.
No thirteenth month can exist, because `Month` defines no such value.

Each member's value is its month number, so `Month(7)` looks up `JULY` by value.
`Month(13)` raises a `ValueError`, because no member holds 13.
The `Enum`'s lookup performs the range check, so `Month` writes none.

A day count cannot serve as the member's value,
because `Enum` treats members with equal values as aliases of one another.
Writing `APRIL = 30` and `JUNE = 30` makes `JUNE` a second name for `APRIL`.

`Enum` accepts that alias silently.
The `verify()` decorator checks the finished class against the constraints you pass it,
and raises a `ValueError` at class creation when one fails.
`UNIQUE` rejects an alias.
`CONTINUOUS` rejects a gap in the integer values.
Decorating `Month` with `@verify(UNIQUE, CONTINUOUS)` catches a repeated or skipped month number.

`DAYS` sits outside the class for a related reason.
Inside the class body,
`DAYS = (31, 28, ...)` makes the tuple a thirteenth member,
because `Enum` treats a value assigned there as one more member.
Wrapping the tuple in `nonmember()` keeps it an ordinary class attribute,
so `DAYS = nonmember((31, 28, ...))` puts the table inside `Month` and leaves twelve members.

The tests confirm that `Month(7)` finds `JULY` in a legal date,
that a day past the end of its month raises `TypeFailure`,
and that a month number outside the twelve makes `Month()` raise `ValueError`:

```python
# test_birth_date.py
import pytest
from birth_date import BirthDate, Day, Month, Year
from validation import TypeFailure

def test_lookup_finds_the_month() -> None:
    bd = BirthDate(Month(7), Day(8), Year(1957))
    assert bd.month is Month.JULY

@pytest.mark.parametrize("month_n, day_n", [
    (2, 31),
    (4, 31),
    (9, 31),
])
def test_day_past_end_of_month(month_n: int,
                               day_n: int) -> None:
    assert Month(month_n).max_days < day_n
    with pytest.raises(TypeFailure):
        BirthDate(Month(month_n), Day(day_n), Year(2020))

@pytest.mark.parametrize("bad", [0, 13, -1])
def test_month_number_outside_twelve(bad: int) -> None:
    with pytest.raises(ValueError):
        Month(bad)
```

### Mixing a Type into an Enum {#enum-mix-ins}

A `Month` member carries a number as its value.
The number is not the month.
Sometimes the member is a value of some type: a direction is a pair of offsets,
a log level is a string.
A class listed before `Enum` in the bases is a *mix-in*,
and every member becomes an instance of it.
`Enum` builds each member by calling the mix-in's constructor with the assigned value,
so `UP = (0, 1)` makes `Direction.UP` the tuple `(0, 1)` as well as an enum member:

```python
# enum_mixins.py
from enum import Enum, StrEnum

class Direction(tuple, Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def step(self, x: int, y: int) -> tuple[int, int]:
        dx, dy = self
        return x + dx, y + dy

print(Direction.UP.step(3, 3))
#: (3, 4)
print(Direction((0, -1)), Direction.LEFT.value)
#: Direction.DOWN (-1, 0)
print(isinstance(Direction.RIGHT, tuple), len(Direction))
#: True 4

class Level(StrEnum):
    INFO = "info"
    WARNING = "warning"

print(f"{Level.INFO}: ready", Level.WARNING.upper())
#: info: ready WARNING
```

`step()` unpacks `self`, because a `Direction` is a tuple.
The member keeps everything an enum member has.
A member passes wherever code expects the mix-in type,
and carries its name with it.

The standard library mixes `str` into `StrEnum`,
so a member answers every `str` method.
Its `__str__()` is `str.__str__()`,
so an f-string shows `info` rather than `Level.INFO`.
A class that lists `(str, Enum)` as its bases keeps `Enum`'s `__str__()` and prints `Level.INFO`;
ruff's `UP042` rewrites that form to `StrEnum`.
`IntEnum` mixes `int` into `Enum`, so each member is an `int`.

Mix in a type when the member is one of that type.
`Month` stays a bare `Enum`,
because a month carries an `int` rather than being one.
`max_days` reads that number through `.value`.
A class of your own can be the mix-in too.
`Enum` passes the assigned value to the mix-in's `__init__()`,
unpacking a tuple into separate arguments,
so `Enum` builds each member the way a constructor call builds an ordinary instance.
[State Machines](31_Patterns--State_Machines.md#mousetrap-states)
mixes its `State` data class into `Enum` this way,
so each `TrapState` member is also a `State` with `message` and `next` fields.

An `Enum` member is one value from the set.
A `Flag` value holds any combination of its members,
the way a file's permissions combine read, write, and execute.
The `|` operator combines members into one `Flag` value.
The `in` operator tests whether a member belongs to that value:

```python
# enum_flags.py
from enum import Flag, IntFlag, auto

class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

rw = Perm.READ | Perm.WRITE
print(repr(rw))
#: <Perm.READ|WRITE: 3>
print(Perm.WRITE in rw, Perm.EXECUTE in rw)
#: True False
print(list(rw))
#: [<Perm.READ: 1>, <Perm.WRITE: 2>]

class Mode(IntFlag):
    R = 4
    W = 2
    X = 1

print(repr(Mode(6)), Mode(6) == 6, Mode.W in Mode(6))
#: <Mode.R|W: 6> True True
print(repr(Mode(9)))
#: <Mode.X|8: 9>
```

`auto()` gives each `Perm` member its own bit, so `READ` is 1, `WRITE` is 2,
and `EXECUTE` is 4.
Iterating over a combined value yields the members it contains,
in definition order.
A `Flag` is still a closed set.
`Perm(8)` raises a `ValueError`, because no member holds that bit.

`IntFlag` mixes in `int`, the way `IntEnum` does,
so a member is an `int` and compares equal to its number.
That suits the bit patterns a library or an operating system returns as integers.
`IntFlag` also keeps unnamed bits,
so `Mode(9)` holds `X` plus a bare 8 where `Perm(8)` raises an exception.

## When an `Enum` Beats a Data Class

You can build `Month` as a data class instead of an `Enum`.
A data-class `Month` works, but it is more code for less safety.
You must construct the twelve months yourself and store them in a container,
whereas the `Enum` is that set:

```python
# month_dataclass.py
from dataclasses import dataclass, field
from birth_date import Day
from validation import check

@dataclass(frozen=True)
class Month:
    name: str
    n: int
    max_days: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 12, f"Month({self.n})")
        check(self.max_days in (28, 30, 31),
              f"Month(max_days={self.max_days})",
              "is not a month length")

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

def make_months() -> list[Month]:
    return [Month(name, n, days)
            for n, (name, days) in enumerate([
        ("January", 31), ("February", 28), ("March", 31),
        ("April", 30), ("May", 31), ("June", 30),
        ("July", 31), ("August", 31), ("September", 30),
        ("October", 31), ("November", 30), ("December", 31),
    ], start=1)]

@dataclass(frozen=True)
class Months:
    months: list[Month] = field(default_factory=make_months)

    def of(self, month_number: int) -> Month:
        check(1 <= month_number <= 12,
              f"Month({month_number})")
        return self.months[month_number - 1]

months = Months()
print(months.of(7))
#: Month(name='July', n=7, max_days=31)
print(Month("Smarch", 7, 30))
#: Month(name='Smarch', n=7, max_days=30)
```

`Month("Smarch", 7, 30)` passes every `check()`,
so the data class accepts an invented month and a second July.
The `Enum` defines no such value.
`Months.of()` also writes out the range check that the `Enum`'s lookup performs for `Month(7)`.

`Months` carries a list of its twelve `Month`s,
so its `months` field needs `field(default_factory=make_months)` rather than a default value.

Choose the tool that makes the legal set easiest to express.
For a small known set, that is an `Enum`.

## Defaults Built Fresh, Not Shared {#defaults-built-not-shared}

`Months` declares `months: list[Month] = field(default_factory=make_months)`.
`@dataclass` rejects `= make_months()` at class-definition time,
with `ValueError: mutable default <class 'list'> for field months is not allowed: use default_factory`.
The rejection prevents shared storage.
Python evaluates a default value once, at class definition,
so with that default every `Months` reads and writes one list,
the [mutable-default trap](05_Foundations--Functions.md#the-mutable-default-trap).
`field(default_factory=make_months)` supplies a function instead of a value.
Each new `Months` calls it and gets its own fresh list.

`@dataclass` refuses a default it recognizes as shared storage,
which covers `list`, `dict`, and `set`.
The test is hashability, not mutability.
An instance of an ordinary class you wrote is hashable by default,
so it passes as a default.
Every data class instance then shares the same default object.
That sharing is the same bug the check exists to prevent.
Use `default_factory` for any mutable default.

`field()` types its parameter as `default_factory: Callable[[], _T]`,
so it accepts any callable that takes no arguments.
A named function like `make_months()` is one.
A type is another, which is why `field(default_factory=list)` appears throughout this book.
Calling `list` builds an empty list.
A subscripted generic is callable too,
so `field(default_factory=dict[str, str])` is legal and produces an empty dict.
That form seems redundant, because the annotation on the left names the type,
and the subscript vanishes at runtime.
It gains one thing, a check that the factory builds the type the annotation names:

```python
# factory_checking.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass
class Unchecked:
    # A set
    data: dict[str, str] = field(default_factory=set)

@dataclass
class Checked:
    data: dict[str, str] = field(
        default_factory=dict[str, str])

print(type(Unchecked().data).__name__)
#: set
with expected(TypeError):
    Unchecked().data["theme"] = "dark"
#: [TypeError] 'set' object does not support item assignment
print(Checked().data)
#: {}
```

`Unchecked` passes every check.
`ty` accepts it, the linter (`ruff`) accepts it,
and the declaration says `dict[str, str]`, so every reader expects a dict.
What arrives is a `set`.
Python reports the mistake at the first item assignment,
which can be far from the declaration that caused it.

For a bare `list`, `dict`, or `set` factory,
`ty` infers `Unknown` for the `field()` call.
`Unknown` satisfies any annotation,
so `ty` accepts any bare factory for the field.
Checkers differ here.
Pyright infers `set[Unknown]` for this factory and rejects it against `dict[str, str]`.

Subscripting makes the factory's return type concrete.
`field(default_factory=dict[int, int])` on this field then draws a type error.
Use the bare form when the factory and the annotation agree,
which is most of the time.
Subscript the factory when you want that agreement checked.

## A `NamedTuple` Cannot Validate Itself {#namedtuple-cannot-validate}

A `NamedTuple` is the other immutable type,
and it is tempting for a small type like `Stars`.
`typing.NamedTuple` forbids overriding the methods that build an instance,
so validation must live in a factory function beside the type.
A caller can skip the check by calling the type instead of the factory:

```python
# test_namedtuple_no_hook.py
from typing import NamedTuple
import pytest
from validation import TypeFailure, check

class Stars(NamedTuple):
    number: int

# Validation lives outside
def make_stars(number: int) -> Stars:
    check(1 <= number <= 10, f"Stars({number})")
    return Stars(number)

def test_the_factory_rejects_illegal_values() -> None:
    assert make_stars(10).number == 10
    with pytest.raises(TypeFailure):
        make_stars(11)

def test_calling_the_type_skips_the_check() -> None:
    assert Stars(11).number == 11

def test_the_check_cannot_move_inside() -> None:
    with pytest.raises(AttributeError,
                       match="Cannot overwrite"):
        class Validated(NamedTuple):
            number: int

            def __new__(cls, number: int) -> Validated:  # type: ignore
                check(1 <= number <= 10, f"Stars({number})")
                return tuple.__new__(cls, (number,))
```

`test_the_factory_rejects_illegal_values()` and `test_calling_the_type_skips_the_check()` are `test_stars.py` inverted.
There, no illegal `Stars` can exist.
Here, `Stars(11)` builds one,
because a caller can call `Stars()` instead of the factory function.
Every factory in [Factory](26_Patterns--Factory.md#hiding-the-concrete-classes)
shares that limit.

`test_the_check_cannot_move_inside()` shows why the check cannot move inside the type.
`NamedTuple` refuses `__new__()`,
and it refuses `__init__()` with the same `AttributeError`.
Python raises `AttributeError` while it is still executing the `class` statement,
before the class exists.

`ty` reports the `__new__()` override as `invalid-named-tuple`,
which the `# type: ignore` silences.
Pyright accepts the `__new__()` without comment.

A subclass of the `NamedTuple` may define `__new__()`.
That avoids the prohibition, but one path still bypasses the check.
`copy.replace()` calls the named tuple's `_replace()`,
which rebuilds through `tuple.__new__()`, not through your `__new__()`,
so `copy.replace()` on a validated instance quietly produces an unvalidated one.

A frozen data class runs `__post_init__()` on every construction,
including the ones you did not anticipate.
[`copy.replace()`](#the-general-form-of-replace) is one of them,
because it builds the copy through the constructor.
Running the check on every construction is the deciding difference whenever a type must guarantee its own values.
When every value of the field types is legal,
a `NamedTuple` is a fine [immutable type](28_Patterns--Data_Transfer_Objects.md#the-standard-library-versions).

## Inheritance and the Generated `__init__()` {#dataclass-inheritance}

A data class generates an `__init__()` with one parameter per field,
and its body assigns each one (`self.name = name`).
The generated `__init__()` does not call the base class `__init__()`,
because `@dataclass` cannot know what arguments that constructor expects.
If you inherit from an ordinary class that sets up state in its own constructor,
the data class silently skips that setup:

```python
# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class NamedConnection(Connection):
    name: str

c = NamedConnection("db")
print(c.name)
#: db
# Connection.__init__ never ran, so host and url are unset:
print(hasattr(c, "host"), hasattr(c, "url"))
#: False False
```

The omission is easy to miss because `NamedConnection("db")` still succeeds.

To run the base initializer, call it yourself from `__post_init__()`,
which runs after the generated `__init__()` assigns the fields:

```python
# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class NamedConnection(Connection):
    host: str
    name: str

    def __post_init__(self) -> None:
        super().__init__(self.host)

c = NamedConnection("localhost", "db")
print(c.url, c.name)
#: tcp://localhost:5432 db
```

No field declaration produces `url`.
If you delete `__post_init__()`,
`print(c.url, c.name)` raises an `AttributeError`.

If a base `__init__()` instead replaces `self.__dict__`,
calling it from `__post_init__()` discards the fields the data class just assigned.
The [*Borg* singleton](23_Patterns--Singleton.md#borg-singleton-by-inheritance)
is that case.

When the base class is also a data class, you need no `__post_init__()`.
The subclass generates one `__init__()` covering the inherited fields and the new ones,
in order:

```python
# dataclass_inherits_dataclass.py
from dataclasses import dataclass

@dataclass
class Connection:
    host: str

@dataclass
class NamedConnection(Connection):
    name: str

c = NamedConnection("localhost", "db")
print(c.host, c.name)
#: localhost db
```

A default in the base class is the one snag.
If `host` has a default, `name` follows it with none,
and `@dataclass` refuses that order under its [field-ordering rule](#more-data-class-tools).
The rule governs positional fields alone,
so `kw_only=True` on `NamedConnection` avoids it by making `name` keyword-only.

## Frozen and Plain Data Classes Do Not Mix

Two data classes in one hierarchy must agree about `frozen`.
Mixing the settings fails in either direction:

```python
# frozen_inheritance.py
from dataclasses import dataclass
from exceptions import expected

@dataclass(frozen=True)
class Frozen:
    a: int

@dataclass
class Plain:
    a: int

with expected(TypeError):
    @dataclass
    class Thawed(Frozen):  # type: ignore
        b: int
#: [TypeError] cannot inherit non-frozen dataclass from a
#: frozen one

with expected(TypeError):
    @dataclass(frozen=True)
    class Chilled(Plain):  # type: ignore
        b: int
#: [TypeError] cannot inherit frozen dataclass from a non-
#: frozen one
```

Both defenses reject these classes.
The type checker reports an `invalid-frozen-dataclass-subclass` error for each class,
which the `# type: ignore` silences so the listing can reach the runtime failure.

`frozen=True` works by installing a `__setattr__()` that rejects an assignment to any field of the frozen class,
and a subclass inherits that method.
A plain subclass of a frozen class is half writable,
its own fields assignable and the inherited ones not.
A frozen subclass of a plain base is the opposite,
freezing every attribute that the mutable base's methods assign.
So `@dataclass` refuses the combination at class-definition time,
before the first surprising assignment.
Every validated type in this chapter carries `frozen=True`,
so anything you derive from one must carry it too.

## More Data Class Tools

`asdict()` and `astuple()` convert an instance to a dictionary or tuple,
recursing into nested data classes:

```python
# asdict_astuple.py
from dataclasses import asdict, astuple, dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(10, 20)
print(asdict(p))
#: {'x': 10, 'y': 20}
print(astuple(p))
#: (10, 20)

@dataclass(frozen=True)
class Line:
    points: list[Point]

line = Line([Point(2, 7), Point(10, 4)])
print(asdict(line))  # Recurses into the list of Points
#: {'points': [{'x': 2, 'y': 7}, {'x': 10, 'y': 4}]}
```

`asdict()` and `astuple()` copy as they go,
so every list and dict in the result is a new object rather than the one inside the instance.
Changing the result leaves the original as it was.

`KW_ONLY` forces callers to pass the fields after it by keyword:

```python
# kw_only_config.py
from dataclasses import KW_ONLY, dataclass

@dataclass
class Config:
    source: str
    # Everything after this must be passed by keyword:
    _: KW_ONLY
    verbose: bool = False
    retries: int = 3

print(Config("data.csv", retries=5))
#: Config(source='data.csv', verbose=False, retries=5)
```

Passing `kw_only=True` to `@dataclass` makes every field keyword-only.
The `_: KW_ONLY` marker limits that to the fields after it,
leaving `source` positional.

`KW_ONLY` also exempts the fields after it from the ordering rule.
A field with no default normally cannot follow one that has a default,
because the generated `__init__()` then needs a required parameter after an optional one.
`@dataclass` refuses that with `TypeError: non-default argument 'b' follows default argument 'a'`.
Because fields after `_: KW_ONLY` are keyword-only, they can come in any order.

## The General Form of `replace()` {#the-general-form-of-replace}

`dataclasses.replace()` works only on data classes, but "same object,
one field different" is what you do with any immutable value.
`copy.replace()` is the general version, and it works on a frozen data class,
a `NamedTuple`, a `date` or `datetime`, a `SimpleNamespace`,
and anything else that defines `__replace__()`:

```python
# copy_replace.py
import copy
from datetime import date
from typing import NamedTuple
from exceptions import expect
from stars import Stars

class Size(NamedTuple):
    width: int
    height: int

print(copy.replace(Stars(4), number=9))
#: Stars(number=9)
print(copy.replace(Size(4, 3), height=9))
#: Size(width=4, height=9)
print(copy.replace(date(2026, 8, 4), day=1))
#: 2026-08-01

expect(Exception, copy.replace, Stars(4), number=99)
#: [TypeFailure] Stars(99)
```

For a data class, `copy.replace()` builds the new object through the constructor,
so `Stars.__post_init__()` runs on the copy.
A validated type stays validated across a replacement,
so `copy.replace()` transforms one legal value into a new legal value.

### `copy()` and `deepcopy()` Skip the Constructor {#copy-skips-the-constructor}

`copy.copy()` and `copy.deepcopy()` copy without calling the constructor.

```python
# replace_vs_copy.py
import copy
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        print(f"checking {self.number}")
        check(1 <= self.number <= 10,
              f"Stars({self.number})")

s = Stars(4)
#: checking 4
print(copy.replace(s, number=2))
#: checking 2
#: Stars(number=2)
print(copy.copy(s))
#: Stars(number=4)
print(copy.deepcopy(s))
#: Stars(number=4)
```

`copy.copy()` and `copy.deepcopy()` create the copy with `__new__()` and write the saved state into its `__dict__`,
and so does `pickle`.
Because none of the three runs `__init__()` or `__post_init__()`,
each can produce a `Stars` holding a number that no check saw.
That is harmless while the copy comes from a legal original.
It is dangerous when the state comes from a file that an older version of the class wrote.
[*Memento*](36_Patterns--Memento.md) revisits that case.
`copy.replace()` alone keeps the guarantee,
because rebuilding through the constructor is the only way to run the check again.

### Defining `__replace__()` {#defining-replace}

`__replace__()` is a dunder like any other,
so an ordinary class can support `copy.replace()` by defining it:

```python
# copy_replace_protocol.py
import copy
from typing import Self

class Color:
    def __init__(self, red: int, green: int,
                 blue: int) -> None:
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self) -> str:
        return (f"Color({self.red}, {self.green}, "
                f"{self.blue})")

    def __replace__(self, **changes: int) -> Self:
        current = {"red": self.red, "green": self.green,
                   "blue": self.blue}
        return type(self)(**(current | changes))

teal = Color(0, 128, 128)
print(teal)
#: Color(0, 128, 128)
lighter = copy.replace(teal, red=64)
print(lighter)
#: Color(64, 128, 128)
```

`Color` is an ordinary class,
so `dataclasses.replace()` rejects it with a `TypeError`.
Every implementation takes the same shape: recover the constructor arguments,
override the named ones, rebuild.
Calling `type(self)(...)` rather than `Color(...)` gives a subclass a copy of its own class,
and the `Self` return annotation tells the type checker so.

Define `__replace__()` when your type is immutable and callers need variants of it.
For a mutable type, the caller assigns to the attribute.

## Serializing to JSON

A data class has no built-in JSON support.
Handed a data class instance,
`json.dumps()` raises `TypeError: Object of type Person is not JSON serializable`.

`asdict()` turns the object into a nested dictionary,
and `json.dumps()` serializes dictionaries.

```python
# json_round_trip.py
import json
from dataclasses import asdict
from typing import Any
from person import EmailAddress, FullName, Person

def to_json(person: Person) -> str:
    return json.dumps(asdict(person), indent=2)

def from_json(text: str) -> Person:
    data: dict[str, Any] = json.loads(text)
    return Person(
        FullName(data["name"]["text"]),
        EmailAddress(data["email"]["text"]),
    )

original = Person(FullName("Grace Hopper"),
                  EmailAddress("grace@example.com"))
text = to_json(original)
print(text)
#: {
#:   "name": {
#:     "text": "Grace Hopper"
#:   },
#:   "email": {
#:     "text": "grace@example.com"
#:   }
#: }
print(from_json(text) == original)  # Round-trip
#: True
```

JSON data typically arrives from outside the program,
so the program treats it as untrusted.
Rebuilding the value through `Person`, `FullName`,
and `EmailAddress` runs each constructor's validation,
so the boundary rejects an illegal value instead of passing it to the rest of the code.

A custom `JSONEncoder` converts each data class that `json.dumps()` hands it into a dict,
including one nested inside other structures:

```python
# json_encoder.py
import json
from dataclasses import asdict, is_dataclass
from typing import Any, override
from person import EmailAddress, FullName, Person

class DataClassEncoder(json.JSONEncoder):
    @override
    def default(self, o: Any) -> Any:
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        return super().default(o)

people = [Person(FullName("Ada Lovelace"),
                 EmailAddress("ada@example.com"))]
print(json.dumps(people, cls=DataClassEncoder, indent=2))
#: [
#:   {
#:     "name": {
#:       "text": "Ada Lovelace"
#:     },
#:     "email": {
#:       "text": "ada@example.com"
#:     }
#:   }
#: ]
```

`json.dumps()` calls `default()` for any object it cannot serialize on its own.
The encoder converts each data class to a dictionary,
and the base encoder serializes that dictionary,
recursing through lists and nested objects.

`is_dataclass()` answers `True` for the class object as well as for an instance,
but `asdict()` requires an instance.
The `not isinstance(o, type)` test passes a class object on to the base encoder instead of `asdict()`.

Encoding is mechanical, but a decoder must name the type to rebuild.
The standard library leaves that code to you.
For deep or evolving structures, [Pydantic](https://docs.pydantic.dev)
and [dataclasses-json](https://github.com/lidatong/dataclasses-json)
automate the decode side,
reconstructing nested types from the parsed JSON and validating as they go.

## Where the Checks Go

`stars_unchecked.py` spreads the checks across every function that takes a rating,
and `stars_class.py` spreads them across every method that changes one.
`stars.py` puts them in the constructor, where they run once,
for every value the program constructs.

Checking in the constructor moves work to the edges of the program.
Every place data enters your program now needs a constructor call:
the parsed JSON, the database row, the form field, the command-line argument.
`from_json()` is that boundary written out.
It reads untrusted text and hands the pieces to `FullName` and `EmailAddress`.
That boundary is the last point where you can reject a bad value before the rest of the program receives it.
After those constructor calls your code holds types rather than raw data.
A function receiving a `FullName` or an `EmailAddress` uses the value without checking it again.

Away from the boundaries, the types also use more memory and time.
Every value is now an object.
Creating one calls a constructor and reading it goes through attribute access,
where a bare `int` or `str` needs neither.
`copy.replace()` re-runs every check in `__post_init__()` on every change,
including the checks on fields it copied unchanged.
For a hot path, or a structure nesting many values
(many `Point`s inside a `Line`),
[measure the overhead](18_Techniques--Performance.md)
before you adopt the types everywhere.

## Exercises

Try each exercise before opening its [solution](../Solutions/12_Techniques--Data_Classes_as_Types/).

1.  Add leap-year support to `Month`,
    so February allows 29 days when the `BirthDate`'s `Year` is a leap year.
    Write the tests first.
2.  Give `EmailAddress` a stricter check
    (a single `@`, with text on both sides).
    Show the values the check now rejects.
3.  Take `test_namedtuple_no_hook.py`'s `Stars` and build the subclass workaround:
    a `_Stars(NamedTuple)` holding the field,
    and a `Stars(_Stars)` whose `__new__()` runs the check.
    Show that `Stars(11)` now raises a `TypeFailure` while `copy.replace(Stars(5), number=99)` does not,
    and explain why `copy.replace()` on a frozen data class runs the check.
4.  Feed `from_json()` a JSON string whose email has no `@`,
    and confirm that it raises `TypeFailure`.
    The validation you wrote once, in `EmailAddress`,
    now also guards your JSON input.
5.  Make `copy.replace()` work on a `Stars` that is not a data class:
    write an ordinary class holding the rating, validate in `__init__()`,
    define `__replace__()`,
    and confirm that `copy.replace()` still runs your validation.
6.  Add a `ClassVar[int]` counter to `Stars` that counts every `Stars` created.
    Predict whether the counter appears in the generated `__init__()`'s parameter list,
    then check by printing `inspect.signature(Stars.__init__)`.
    Incrementing the counter as `Stars.built += 1` from `__post_init__()` works on a frozen class,
    while `self.built += 1` does not.
    Explain why.
7.  Give `Months` a second field,
    a `dict[str, Month]` index written with a `= {}` default,
    and read the error `@dataclass` reports.
    Then fix it two ways,
    with `default_factory=dict` and with `default_factory=dict[str, Month]`,
    and say which one a type checker can verify.
8.  `stars_float.py` builds a `Stars` holding `5.5`.
    Add a type test to the check in `__post_init__()` so that `Stars(5.5)` raises `TypeFailure`.
    `Stars(True)` also passes the range check.
    Explain why an `isinstance()` test accepts it,
    and write the test so that it rejects `True` as well.
