# Data Classes as Types

A *type* is a set of values.
The type `int` is the set of whole numbers.
A type you define, like a rating from one to ten, is a smaller set:
the allowed values.
Programmers have historically been bad at keeping objects inside that set.
It's too easy to construct or mutate an object in an illegal state.
Defensive checks then spread through your code.

This chapter shows a better approach, built from frozen data classes.
You validate the value once, at construction, and freeze it so it cannot change.
The type then guarantees that every object is a legal value.
Code that receives one need not check it again.
This material comes from my PyCon 2022 talk,
[Making Data Classes Work for You](https://www.youtube.com/watch?v=w77Kjs5dEko).

The following `check()` function appears throughout the chapter.
It raises `TypeFailure`,
a custom exception meaning a value falls outside the type's allowed set:

```python
# validation.py
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)
```

An exception is a value like any other, and the values it carries deserve names.
`subject` is the rejected value as the caller rendered it, such as `Stars(11)`.
`reason` explains the rejection when the name alone does not,
such as `needs an @`.
A handler can read `e.subject` and `e.reason` rather than parsing them from the exception text.

`eq=False` turns off the generated `__eq__()`, for two reasons.
A data class that defines `__eq__()` sets `__hash__` to `None`
(shown for `Messenger` in [Data Classes](#data-classes)),
and an unhashable exception is a trap if you put it in a set.
Identity is the correct comparison for an exception.
Two failures carrying the same text are still two separate failures.

## A Value to Check Everywhere

Suppose a "stars" rating is an integer from one to ten.
If you represent it as an `int`, nothing stops a caller from passing eleven,
or minus one.
To prevent that, every function that takes a rating must check it:

```python
# stars_unchecked.py
# An int as a 1-10 rating must be re-checked everywhere
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
The `int` annotation says "any integer," which is not what you mean.
Checking the argument also says nothing about the result: `f1(6)` returns 11,
which no rating may be.
`f3()` is what forgetting looks like.
`11` was never a legal rating, and nothing objected: not the annotation,
not the type checker, not the running program.
The result is a number that no rating can produce,
passed along as if it were fine.

## A Class Is Not a Type

The object-oriented answer is to wrap the value in a class and validate it in the constructor.
That is better, but it does not finish the job.
The value is still mutable, so every method that changes it must re-validate,
and a method can leave the object in an illegal state between steps:

```python
# stars_class.py
from validation import TypeFailure, check

class Stars:
    def __init__(self, number: int) -> None:
        self._number = number  # Private by convention
        self._validate()

    def _validate(self) -> None:
        check(1 <= self._number <= 10, f"Stars({self._number})")

    @property
    def number(self) -> int:  # No setter: blocks external mutation
        return self._number

    def __str__(self) -> str:
        return f"Stars({self._number})"

    def f1(self) -> int:
        self._number = self._number + 5
        self._validate()  # Postcondition
        return self._number

if __name__ == "__main__":
    rating = Stars(4)
    print(rating)
    print(rating.f1())
    damaged = Stars(8)
    try:
        damaged.f1()
    except TypeFailure as e:
        print(f"TypeFailure: {e}")
    print(damaged)
#: Stars(4)
#: 9
#: TypeFailure: Stars(13)
#: Stars(13)
```

A read-only `@property` keeps users from assigning to `number`,
but the object still mutates `_number`,
so `f1()` must re-check the result before returning it.
That check runs after the mutation, not instead of it:
`Stars(8).f1()` sets `_number` to 13, then raises `TypeFailure`,
and the object goes on holding that illegal value.
Catching the exception does not undo the damage.
Checking arguments on the way in and results on the way out,
with a class invariant that must hold between calls,
is the practice known as *Design by Contract* (DbC).
`f1()` takes no argument, so only the postcondition appears here.
A method that accepted a second rating would need a precondition for it as well.
The problem with DbC is that the contract spreads across every method that touches the value.
The invariant is the part this chapter replaces.
`_validate()` states it, and every mutating method must remember to call it.
That is the same scattering of checks as before, but moved inside the class.
The class encapsulates the value.
It does not constrain it to a set of legal values.

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
    depth: float = 0.0  # Default value
```

`display_object()`, the inspection helper from [Metaprogramming](17_Metaprogramming.md#building-display_object),
shows what `@dataclass` generates:

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
#:   • __init__(self, name: str, number: int, depth: float = 0.0)...
#:   • __repr__(self)
```

`@dataclass` did generate the dunder methods,
and the constructor arguments cover all the fields in `Messenger`.
The trailing `...` is `display_object()` trimming that line to its report width.
`__hash__` is `None`: a `@dataclass` compares by value with `__eq__`,
so it gives up hashability rather than let you put a mutable instance in a `set` or use it as a `dict` key.
As described in [Class Attributes](09_Class_Attributes.md),
of the three fields only `depth` appears as an attribute,
because it has an initialization value.

```python
# demo_messenger.py
from dataclasses import replace
from messenger import Messenger

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(m.name, m.number, m.depth)
#: foo 12 3.14

# The generated __eq__ compares by field value:
print(Messenger("xx", 1) == Messenger("xx", 1))
#: True
print(Messenger("xx", 1) == Messenger("xx", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(mc)
#: Messenger(name='foo', number=12, depth=9.9)

m.name = "bar"  # Data classes are mutable by default
print(m)
#: Messenger(name='bar', number=12, depth=3.14)
```

`print(m)` uses the generated `__repr__()`,
which produces the class name and the named argument values.

`replace()` returns a copy with some fields changed, leaving the original alone.
This copy-instead-of-mutate style reduces errors.
`copy.replace()`, in [The General Form of `replace()`](#the-general-form-of-replace),
does the same for anything immutable, not only for data classes.

The last two lines show that a data class is mutable, so `m.name = "bar"` works.

`display_object()` shows the attributes with their declared types:

```python
# display_messenger.py
from display import display_object
from messenger import Messenger

display_object(Messenger("foo", 12, 3.14))
#: [Attributes]
#:   • depth: float = 3.14
#:   • name: str = 'foo'
#:   • number: int = 12
#: [Methods]
#:   None
```

The default `display_object()` does not show the generated `__init__()`,
`__repr__()`, and `__eq__()`.

## Immutability

Passing `frozen=True` makes the data class immutable.
Attempting to assign to a field raises `FrozenInstanceError`.
As a bonus, a frozen instance is hashable,
so you can use it as a dictionary key or put it in a set.
The mutability that cost `Messenger` its `__hash__` is gone,
so `@dataclass` generates one from the fields:

```python
# frozen_messenger.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Messenger:
    name: str
    number: int
    depth: float = 0.0

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)

try:
    setattr(m, "name", "bar")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'name'

cache = {m: "Ni!"}  # Frozen instances are hashable
print(cache[m])
#: Ni!
```

The listing goes through `setattr()` because the type checker rejects `m.name = "bar"` before the program runs,
which is the earlier of the two defenses.
`frozen=True` is the one that holds at runtime,
against code the checker never saw.

`frozen=True` guards the binding, not the object behind it.
You can still mutate a field's `list` in place,
and a frozen instance is hashable only when every field it holds is.
[Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)
demonstrates that leak.
The types this chapter validates hold `int`s and `str`s,
so for them the guarantee is total.
`Months` and `Line`, both later in this chapter, each hold a `list`:
neither is hashable, and neither is safe from a change made through that list.

A frozen data class still carries a per-instance `__dict__`.
Adding `slots=True` drops it, for less memory and faster attribute access;
[Performance](18_Performance.md#slots) measures the difference.

A frozen data class is not the only immutable record in the standard library.
A `typing.NamedTuple` also rejects assignment and is also hashable.
The two differ in equality.
A frozen data class equals only another instance of its own class,
while a `NamedTuple` equals any tuple holding the same values,
a difference [Data Transfer Objects](22_Data_Transfer_Objects.md#a-namedtuple-is-still-a-tuple)
covers.
They differ again in what this chapter cares about most,
shown in [A `NamedTuple` Cannot Validate Itself](#namedtuple-cannot-validate).

If nothing about an object can change after construction,
then validating it at construction makes it valid for its lifetime.

## A Type Is a Set of Values

If you make `Stars` a frozen data class,
you can guarantee that every `Stars` object is legal.
To validate it after the fields receive their values, define `__post_init__()`.
The generated `__init__()` calls this automatically:

```python
# stars.py
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")

def f1(s: Stars) -> Stars:
    return Stars(s.number + 5)

def f2(s: Stars) -> Stars:
    return Stars(s.number * 5)

if __name__ == "__main__":
    print(Stars(4))
    print(f1(Stars(2)))
    print(f2(Stars(2)))
#: Stars(number=4)
#: Stars(number=7)
#: Stars(number=10)
```

The `number` in `Stars` is now constrained to a set of values:
the integers one through ten.
The only way to make a `Stars` is through the constructor,
and the constructor refuses anything outside that set.
If you are holding a `Stars`, it is legal.
You know it without checking.

This changes how you write the functions.
`f1()` and `f2()` take a `Stars` and return a `Stars`.
They do not check their argument, because every `Stars` is legal.
They do not test their result,
because building the returned `Stars` runs the check.

The validation lives in one place, the constructor, so it is easy to change.
Immutability guarantees no one can rebind the fields after construction,
and when the fields are immutable too, no one can damage the value.

`__post_init__()` can check a field but cannot change one.
`frozen=True` works by installing a `__setattr__()` that rejects every assignment,
including the ones arriving from inside the class,
so normalizing a value there raises `FrozenInstanceError`:

```python
# post_init_normalize.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    text: str

    def __post_init__(self) -> None:
        self.text = self.text.lower()  # type: ignore

try:
    Email("Bruce@Example.com")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'text'

@dataclass(frozen=True)
class Normalized:
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.lower())

print(Normalized("Bruce@Example.com"))
#: Normalized(text='bruce@example.com')
```

Both defenses fire here, as they did for `frozen_messenger.py`.
The checker reports the assignment before the program runs,
which the `# type: ignore` silences so the listing can reach the runtime failure.

`object.__setattr__()` skips the rejecting `__setattr__()` and writes the field directly.
It works, and it says what it is doing.
The alternative is to refuse the unnormalized value and normalize before construction.
Which to choose depends on the type.
Normalizing inside makes `Normalized("A@b.com")` and `Normalized("a@b.com")` the same value,
which is usually what an email address should mean.
Refusing instead keeps the constructor a gate and leaves the cleanup to the caller.

Validating once, at construction, often goes by the name *parse,
don't validate*.^[Coined by Alexis King in her 2019 essay ["Parse, don't validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/).]
Instead of checking a changeable value everywhere and hoping you never miss a spot,
you parse it once into a precise type.
After that, holding the type is proof the check passed.
No other code repeats the check, because it cannot fail.
Illegal values are unrepresentable.

This is one aspect of functional programming
(see [Functional Foundations](40_Functional_Foundations.md#immutability)).
Instead of mutating an object and re-guarding it,
you transform one legal value into a new legal value.
[Static Typing](08_Static_Typing.md#type-hints)
argues for letting the type carry the meaning.
Here the type carries a guarantee.

Testing demonstrates that illegal values cannot exist.
`pytest.raises()` confirms that the constructor rejects values outside the set:

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

def test_transformation_can_produce_illegal_value() -> None:
    # f2 multiplies, so its result can be outside the legal set.
    # Construction of the returned Stars catches it: no illegal
    # Stars can ever exist.
    with pytest.raises(TypeFailure):
        f2(Stars(4))  # 4 * 5 = 20
```

## Composing Types from Types

Once each small type guarantees its own values,
you can safely build larger types out of them.
A `Person` made of a valid `FullName` and a valid `EmailAddress` is valid by construction,
with no extra work:

```python
# person.py
from dataclasses import dataclass
from validation import check

@dataclass(frozen=True)
class FullName:
    text: str

    def __post_init__(self) -> None:
        check(len(self.text.split()) >= 2, f"FullName({self.text!r})",
              "needs a first and last name")

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check("@" in self.text, f"EmailAddress({self.text!r})",
              "needs an @")

@dataclass(frozen=True)
class Person:
    name: FullName
    email: EmailAddress

if __name__ == "__main__":
    person = Person(
        FullName("Bruce Eckel"),
        EmailAddress("bruce@example.com"),
    )
    print(person.name)
    print(person.email)
#: FullName(text='Bruce Eckel')
#: EmailAddress(text='bruce@example.com')
```

`Person` declares no checks of its own.
You cannot build it from an illegal name or an illegal email,
because those values cannot exist:

```python
# test_person.py
import pytest
from person import EmailAddress, FullName
from validation import TypeFailure

@pytest.mark.parametrize("bad", ["Bruce", "", "   "])
def test_full_name_needs_two_parts(bad: str) -> None:
    with pytest.raises(TypeFailure):
        FullName(bad)

@pytest.mark.parametrize("bad", ["bruce", "example.com", ""])
def test_email_needs_at_sign(bad: str) -> None:
    with pytest.raises(TypeFailure):
        EmailAddress(bad)
```

When validation grows complicated, libraries make it lighter.
The [attrs](https://www.attrs.org)
library predates and inspired data classes and offers richer validators and converters.
[Pydantic](https://docs.pydantic.dev)
builds validation and parsing into the type,
which is especially useful at the edges of a program where untrusted data can enter.
The principle is the same.
Make the type responsible for guaranteeing its own values.

## Comparing Ordinary Classes and Data Classes

So far this chapter has used `@dataclass` without opening it up:
you declare fields and a constructor appears.
Four small classes show the difference between a class body that declares fields and one that stores them,
and go further than [Class Attributes](09_Class_Attributes.md) did:

- `A` is an ordinary class with bare annotations.
- `B` adds default values but no constructor.
- `C` is a `@dataclass`.
- `D` adds a `ClassVar` field alongside an ordinary one.

The same helper inspects each one:

```python
# comparison.py
from display import REDEFINED_DUNDERS, display_object

def show(obj: object) -> None:
    display_object(obj, REDEFINED_DUNDERS, exclude=("__hash__",))
```

`show()` calls `display_object()` with `REDEFINED_DUNDERS`,
so each report lists only the dunders a class customizes,
not the standard machinery every object inherits from `object`.
For clarity, `show()` also excludes `__hash__` from these reports
(`@dataclass` disabling `__hash__` was [demonstrated for `Messenger`](#data-classes)).

### `A`: Annotations Only

`A` is the simplest case, with no defaults and no constructor,
but with field declarations that look like class variables:

```python
# ordinary_class.py
from comparison import show

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
```

`A` does not override `__init__`, `__repr__`, `__eq__`, or `__hash__`,
so every one of them is `object`'s generic version,
and `show(A())` reports none as redefined.

`x` and `s` in `A` are *bare annotations*: declared, but never assigned a value.
As [Class Attributes](09_Class_Attributes.md#a-bare-annotation-declares-it-does-not-create)
puts it, a bare annotation is a declaration rather than a placeholder.
It records, in `A.__annotations__`,
that some future `A` will carry an `x` and an `s`,
but stores nothing until code assigns a value.
`A` has no `__init__()` to make that assignment,
so the declaration goes unfulfilled.
That is why `show(A())` finds nothing: there is no `x` and no `s` to report,
on the class or on the instance.

### `B`: Class-Level Defaults

`B` adds default values to `x` and `s`,
which turn them from bare annotations into class variables,
because the assignments allocate storage:

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

print(B.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
```

`show(B())` indicates that both are class variables by tagging them as `[CV]`.
`B` has no `__init__()` to copy them onto each instance,
so every `B` object reads the same two values straight from the class attributes.

### `C`: The Same Annotations, Decorated

`C` is `A` decorated with `@dataclass`:

```python
# plain_dataclass.py
from dataclasses import dataclass
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

print(C.__annotations__)
#: {'x': <class 'int'>, 's': <class 'str'>}
```

`show(C(11, "this is C"))` finds the same two names as `show(B())`.
Neither `x` nor `s` carries `[CV]` this time.
As a `@dataclass`, `C`'s generated `__init__(self, x: int, s: str) -> None` runs `self.x = x` and `self.s = s` for every new `C`.
Each `C` instance owns its own copies from the moment of construction.
`B` runs nothing like that.
With no `__init__()`, `show(B())` keeps finding `x` and `s` on the class,
tagged `[CV]`, no matter how many `B` instances exist.

`C` starts from the same bare annotations as `A`.
`@dataclass` reads them to learn what fields exist and in what order,
then uses that to write `__init__`'s parameter list and the assignments inside it;
`dataclasses.fields()` reports the field list it recorded.
`@dataclass` stores nothing on the class:
`x` is still absent from `C.__dict__` after decoration, as it was before.
The declaration is only fulfilled per instance,
when the generated `__init__()` runs.
That is the difference from `A`: not that `@dataclass` changes the annotations,
but that it builds something to act on them.

### `D`: A Real `ClassVar`

`D` adds a real `ClassVar` alongside an ordinary field:

```python
# classvar_dataclass.py
from dataclasses import dataclass
from typing import ClassVar
from comparison import show

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

show(D())
#: [Attributes]
#:   • s: typing.ClassVar[str] = 'Initializer' [CV]
#:   • x: int = 99
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int = 99) -> None
#:   • __repr__(self)

for k, v in D.__annotations__.items():
    print(f"'{k}': {v}")
#: 'x': <class 'int'>
#: 's': typing.ClassVar[str]
#: 'f': typing.ClassVar[float]
```

`show(D)` tags both attributes `[CV]`,
since no instance owns either of them yet.
The difference comes from what `@dataclass` generates for each field.

`x` is an ordinary field.
`__init__()` takes it as a parameter and runs `self.x = x`,
so each new `D` gets its own copy at construction.
That is why `show(D())`'s `x: int = 99` carries no tag.
It now lives in that instance's own `__dict__`, not on the class.

`s`, declared `ClassVar[str]`, behaves differently.
`@dataclass` treats a `ClassVar` field as belonging to the class,
not to any instance, and leaves it out of `__init__()`.
`__init__(self, x: int = 99) -> None` has no `s` parameter,
so no constructor call can assign one.
`s` stays on `D` and keeps its `[CV]` tag no matter how many `D` objects exist.

`f: ClassVar[float]` appears in neither report.
It has no initializer, so it is a bare annotation,
as `x` and `s` were back in `A`: a declaration recorded in `D.__annotations__`,
with no value stored anywhere to report.
`D.f` raises `AttributeError`, for the same reason `A().x` would.
Declaring a field `ClassVar` does not, on its own, create anything.
Only assigning it a value does.

## Enums Are Types Too

When the set of values is small and fixed, an `Enum` is the clearest type.
As an example, a `BirthDate` contains a month, day, and year.
A year has twelve months, so `Month` is an `Enum`.
Each month carries its length, and knows how to check a `Day` against it.
A `BirthDate` then validates across its fields.
The day must fit the month.

```python
# birth_date.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
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
        check(1900 < self.n <= date.today().year, f"Year({self.n})")

class Month(Enum):
    JANUARY = (1, 31)
    FEBRUARY = (2, 28)  # Leap years are left as an exercise
    MARCH = (3, 31)
    APRIL = (4, 30)
    MAY = (5, 31)
    JUNE = (6, 30)
    JULY = (7, 31)
    AUGUST = (8, 31)
    SEPTEMBER = (9, 30)
    OCTOBER = (10, 31)
    NOVEMBER = (11, 30)
    DECEMBER = (12, 31)

    @staticmethod
    def of(month_number: int) -> Month:
        check(1 <= month_number <= 12, f"Month({month_number})")
        return list(Month)[month_number - 1]

    @property
    def max_days(self) -> int:
        return self.value[1]

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day)

if __name__ == "__main__":
    print(BirthDate(Month.of(7), Day(8), Year(1957)))
#: BirthDate(month=JULY, day=Day(n=8), year=Year(n=1957))
```

The `Enum` creates the constrained set of `Month`s.
There cannot be a thirteenth month because that value doesn't exist.

Each member is a pair rather than a bare day count because `Enum` treats members with equal values as aliases of one another.
Writing `APRIL = 30` and `JUNE = 30` makes `JUNE` a second name for `APRIL`,
and only three day counts are distinct,
so `list(Month)` would return three members instead of twelve.
Pairing each month with its number keeps all twelve values distinct,
which `of()` relies on when it indexes `list(Month)`.
The cost is that the member's value is no longer the month number,
so `Month(7)` raises a `ValueError`.
`of()` is the replacement lookup.

```python
# test_birth_date.py
import pytest
from birth_date import BirthDate, Day, Month, Year
from validation import TypeFailure

def test_valid_date() -> None:
    bd = BirthDate(Month.of(7), Day(8), Year(1957))
    assert bd.month is Month.JULY

@pytest.mark.parametrize("month_n, day_n", [
    (2, 31),  # February has 28 days
    (4, 31),  # April has 30
    (9, 31),  # September has 30
])
def test_day_out_of_range_for_month(month_n: int, day_n: int) -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(month_n), Day(day_n), Year(2020))

@pytest.mark.parametrize("bad", [0, 13, -1])
def test_bad_month_number(bad: int) -> None:
    with pytest.raises(TypeFailure):
        Month.of(bad)
```

## When an `Enum` Beats a Data Class

You can build `Month` as a data class instead of an `Enum`.
It works, but it is more code for less safety.
You must construct the twelve months yourself and carry them around,
whereas the `Enum` is that set:

```python
# month_dataclass.py
from dataclasses import dataclass, field
from validation import check

@dataclass(frozen=True)
class Day:
    n: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 31, f"Day({self.n})")

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
    return [Month(name, n, days) for n, (name, days) in enumerate([
        ("January", 31), ("February", 28), ("March", 31),
        ("April", 30), ("May", 31), ("June", 30),
        ("July", 31), ("August", 31), ("September", 30),
        ("October", 31), ("November", 30), ("December", 31),
    ], start=1)]

@dataclass(frozen=True)
class Months:
    months: list[Month] = field(default_factory=make_months)

    def of(self, month_number: int) -> Month:
        check(1 <= month_number <= 12, f"Month({month_number})")
        return self.months[month_number - 1]

if __name__ == "__main__":
    months = Months()
    print(months.of(7))
#: Month(name='July', n=7, max_days=31)
```

`Months` carries a list of its twelve `Month`s,
so its `months` field needs `field(default_factory=make_months)` rather than a default value.

Choose the tool that makes the legal set easiest to express.
For a small fixed set, that is an `Enum`.

## Defaults Built Fresh, Not Shared {#defaults-built-not-shared}

`Months` declares `months: list[Month] = field(default_factory=make_months)`.
`@dataclass` rejects `= make_months()` at class-definition time,
with `ValueError: mutable default <class 'list'> for field months is not allowed: use default_factory`.
Python evaluates a default value once, at class definition,
so every `Months` would read and write that one list,
the trap shown in [Functions](05_Functions.md#default-and-keyword-arguments).
`field(default_factory=make_months)` supplies a function instead of a value,
and each new `Months` calls it and gets its own fresh list.

That rejection is narrower than it looks.
`@dataclass` refuses a default it can tell is shared storage,
which covers `list`, `dict`, and `set`.
The test is hashability, not mutability,
so a mutable object of a class you wrote passes as a default and every instance shares it,
which is the same bug the check exists to prevent.
Use `default_factory` for anything that is not obviously a constant.

`default_factory` accepts any callable that takes no arguments.
A named function like `make_months` is one.
A type is another, which is why `field(default_factory=list)` appears throughout this book:
calling `list` builds an empty one.
A subscripted generic is callable too,
so `field(default_factory=dict[str, str])` is legal and does what it looks like.
That form seems redundant,
because the annotation on the left already names the type,
and the subscript vanishes at runtime.
It gains one thing:

```python
# factory_checking.py
from dataclasses import dataclass, field

@dataclass
class Unchecked:
    data: dict[str, str] = field(default_factory=set)  # A set

@dataclass
class Checked:
    data: dict[str, str] = field(default_factory=dict[str, str])

print(type(Unchecked().data).__name__)
#: set
try:
    Unchecked().data["theme"] = "dark"
except TypeError as e:
    print(type(e).__name__)
#: TypeError
print(Checked().data)
#: {}
```

Nothing objects to `Unchecked`.
The type checker accepts it, the linter accepts it,
and the declaration says `dict[str, str]`, so every reader expects a dict.
What arrives is a `set`, and the mistake surfaces at the first item assignment,
which can be far from the declaration that caused it.
A bare `list`, `dict`,
or `set` produces a type loose enough that a checker accepts it against any annotation,
so it never compares the factory with the field.
Subscripting makes the factory's return type concrete,
and `field(default_factory=dict[int, int])` on this field is then a type error before the program runs.
Use the bare form when the factory and the annotation obviously agree,
which is most of the time.
Subscript it when you want that agreement checked.

## A `NamedTuple` Cannot Validate Itself {#namedtuple-cannot-validate}

A `NamedTuple` is the other immutable record,
and it is tempting for a small type like `Stars`.
`typing.NamedTuple` forbids overriding the methods that build an instance,
so validation must live in a factory function beside the type,
where a caller can go around it:

```python
# test_namedtuple_no_hook.py
from typing import NamedTuple
import pytest
from validation import TypeFailure, check

class Stars(NamedTuple):
    number: int

def make_stars(number: int) -> Stars:  # Validation lives outside
    check(1 <= number <= 10, f"Stars({number})")
    return Stars(number)

def test_the_factory_rejects_illegal_values() -> None:
    assert make_stars(10).number == 10
    with pytest.raises(TypeFailure):
        make_stars(11)

def test_the_type_accepts_them_anyway() -> None:
    assert Stars(11).number == 11  # Calling the type skips the check

def test_the_check_cannot_move_inside() -> None:
    with pytest.raises(AttributeError, match="Cannot overwrite"):
        class Validated(NamedTuple):
            number: int

            def __new__(cls, number: int) -> Validated:  # type: ignore
                check(1 <= number <= 10, f"Stars({number})")
                return tuple.__new__(cls, (number,))
```

The first two tests are `test_stars.py` inverted.
There, no illegal `Stars` could exist.
Here, `Stars(11)` builds one,
because a factory function is advice rather than a gate.
The third test shows why the check cannot move inside the type.
`NamedTuple` refuses `__new__()`, refuses `__init__()` the same way,
and the class never comes into existence:
the error arrives while Python is still executing the `class` statement.
A checker reports it as `invalid-named-tuple` before the program runs,
which the `# type: ignore` silences.

Subclassing the `NamedTuple` and defining `__new__()` on the subclass gets past the prohibition,
and moves the hole rather than closing it.
`_replace()` rebuilds through `tuple.__new__()`, not through your `__new__()`,
so `copy.replace()` on a validated instance quietly produces an unvalidated one.

A frozen data class runs `__post_init__()` on every construction,
including the ones you did not anticipate, and it has no such back door:
`copy.replace()` goes through the constructor,
as [The General Form of `replace()`](#the-general-form-of-replace) shows.
That is the deciding difference whenever a type must guarantee its own values.
When it need not, a `NamedTuple` is a fine immutable record,
as [Data Transfer Objects](22_Data_Transfer_Objects.md#the-standard-library-versions)
shows.

## Inheritance and the Generated `__init__` {#dataclass-inheritance}

A data class builds its `__init__` from its fields and assigns them directly.
It does not call the base class `__init__`.
If you inherit from an ordinary class that does setup in its own constructor,
the data class silently skips that setup:

```python
# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class Logged(Connection):
    name: str

c = Logged("db")
print(c.name)
#: db
# Connection.__init__ never ran, so 'host' and 'url' were never set:
print(hasattr(c, "host"), hasattr(c, "url"))
#: False False
```

The generated `__init__` assigned `name` and stopped.
Nothing called `Connection.__init__`, so neither `host` nor `url` exists.
This is easy to miss because the class still constructs without an error.

To run the base initializer, call it yourself from `__post_init__()`,
which runs after the generated `__init__` assigns the fields:

```python
# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"

@dataclass
class Logged(Connection):
    host: str
    name: str

    def __post_init__(self) -> None:
        super().__init__(self.host)  # Run the base initializer

c = Logged("localhost", "db")
print(c.url, c.name)
#: tcp://localhost:5432 db
```

`url` is derived state that no field declaration produces,
so printing it is proof that `Connection.__init__` ran.
If you delete `__post_init__()`, the same line raises an `AttributeError`.

If a base `__init__` instead replaces `self.__dict__`,
calling it from `__post_init__()` discards the fields the data class just assigned.
The [Borg singleton](24_Singleton.md#borg-singleton-by-inheritance)
is that case.

When the base class is also a data class, you do not need this.
The subclass generates one `__init__` covering the inherited fields and the new ones,
in order:

```python
# dataclass_inherits_dataclass.py
from dataclasses import dataclass

@dataclass
class Connection:
    host: str

@dataclass
class Logged(Connection):
    name: str

c = Logged("localhost", "db")
print(c.host, c.name)
#: localhost db
```

A data class has no way to know what arguments a non-data-class base constructor expects,
so it does not call it.
Its field list covers its own fields plus any inherited from data class bases,
and it builds the body by assigning those fields.

Two data classes in one hierarchy must agree about `frozen`.
Mixing the settings fails in either direction:

```python
# frozen_inheritance.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Frozen:
    a: int

@dataclass
class Plain:
    a: int

try:
    @dataclass
    class Thawed(Frozen):  # type: ignore
        b: int
except TypeError as e:
    print(e)
#: cannot inherit non-frozen dataclass from a frozen one

try:
    @dataclass(frozen=True)
    class Chilled(Plain):  # type: ignore
        b: int
except TypeError as e:
    print(e)
#: cannot inherit frozen dataclass from a non-frozen one
```

Both defenses fire again.
The checker reports each class as an invalid frozen-dataclass subclass,
which the `# type: ignore` silences so the listing can reach the runtime failure.

`frozen=True` works by installing a `__setattr__()` that rejects every assignment,
and a subclass inherits that method.
Either mix would produce a class whose fields are half writable,
so `@dataclass` refuses at class-definition time rather than at the first surprising assignment.
Every validated type in this chapter is frozen,
so anything you derive from one must be frozen too.

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
Changing the result cannot reach back into the original.

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

Passing `kw_only=True` to `@dataclass` makes every field keyword-only;
the `_: KW_ONLY` marker limits that to the fields after it,
leaving `source` positional.

`KW_ONLY` also lifts the ordering rule.
A field with no default normally cannot follow one that has a default,
because the generated `__init__()` would then need a required parameter after an optional one,
which Python refuses with `TypeError: non-default argument 'b' follows default argument 'a'`.
Fields after `_: KW_ONLY` are keyword-only,
so their order no longer matters and the rule stops applying.

## The General Form of `replace()` {#the-general-form-of-replace}

`dataclasses.replace()` only works on data classes, but "same object,
one field different" is not a data class idea.
It is what you do with any immutable value.
`copy.replace()` is the general version, and it works on a frozen data class,
a `NamedTuple`, a `datetime`, a `SimpleNamespace`,
and anything else that defines `__replace__()`:

```python
# copy_replace.py
import copy
from datetime import date
from typing import NamedTuple
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

try:
    copy.replace(Stars(4), number=99)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(99)
```

`copy.replace()` builds the new object through the constructor,
so `Stars.__post_init__()` runs on the copy.
A validated type stays validated across a replacement,
which makes "transform one legal value into a new legal value" a safe thing to say.

The `copy` module also holds copies that skip the constructor.
Printing from `__post_init__()` shows which calls run it:

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
        check(1 <= self.number <= 10, f"Stars({self.number})")

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

`copy.copy()` and `copy.deepcopy()` restore the object's state directly,
and so does `pickle`.
None of the three runs `__init__()` or `__post_init__()`,
so each can produce a `Stars` holding a number that no check saw.
That does not matter while the copy comes from a legal original,
and it matters a great deal when the state comes from a file written by an older version of the class,
which [Memento](36_Memento.md) revisits.
`copy.replace()` is the one that keeps the guarantee,
because rebuilding through the constructor is the only way to get the check back.

`__replace__()` is a dunder like any other,
so a class that is not a data class can join by defining it:

```python
# copy_replace_protocol.py
import copy
from typing import Final, Self

SHIFTS: Final[dict[str, int]] = {"red": 16, "green": 8, "blue": 0}
MASK: Final[int] = 0xFF

class Color:
    def __init__(self, red: int, green: int, blue: int) -> None:
        channels = {"red": red, "green": green, "blue": blue}
        self.packed = sum(v << SHIFTS[k] for k, v in channels.items())

    @property
    def channels(self) -> dict[str, int]:
        return {n: self.packed >> s & MASK for n, s in SHIFTS.items()}

    def __repr__(self) -> str:
        return f"Color({', '.join(map(str, self.channels.values()))})"

    def __replace__(self, **changes: int) -> Self:
        return type(self)(**(self.channels | changes))

teal = Color(0, 128, 128)
print(teal, hex(teal.packed))
#: Color(0, 128, 128) 0x8080
lighter = copy.replace(teal, red=64)
print(lighter, hex(lighter.packed))
#: Color(64, 128, 128) 0x408080
```

`Color` stores no separate fields,
so `dataclasses.replace()` has nothing to work with.
`__replace__()` unpacks the channels, applies the changes,
and hands the result back through the constructor,
which is the same shape every implementation takes:
recover the constructor arguments, override the named ones, rebuild.
`__init__()` packs a channel dictionary using `SHIFTS`,
and `channels` unpacks one with the same table, so the two are inverses.
Returning `Self` from `type(self)(...)` means a subclass gets a copy of its own class.

Define `__replace__()` when your type is immutable and callers will need variants of it.
Skip it when the type is mutable,
because the caller can assign to the attribute.

## Serializing to JSON

A data class has no built-in JSON support.
If you hand one to `json.dumps()`,
it raises `TypeError: Object of type Person is not JSON serializable`.

`asdict()` turns the object into a nested dictionary,
and `json.dumps()` knows how to serialize dictionaries.
Decoding goes the other way.
Parse the JSON into a dictionary, then hand its parts to the constructors.

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

original = Person(FullName("Bruce Eckel"),
                  EmailAddress("bruce@example.com"))
text = to_json(original)
print(text)
#: {
#:   "name": {
#:     "text": "Bruce Eckel"
#:   },
#:   "email": {
#:     "text": "bruce@example.com"
#:   }
#: }
print(from_json(text) == original)  # Round-trip
#: True
```

JSON data typically arrives from outside the program, untrusted.
Rebuilding the value through `Person`, `FullName`,
and `EmailAddress` runs each constructor's validation,
so the boundary rejects an illegal value instead of leaking it into the rest of the code.
The type guards itself.

A custom `JSONEncoder` serializes any data class it meets,
even nested inside other structures, by converting each one to a dict:

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

people = [
    Person(FullName("Ada Lovelace"),
           EmailAddress("ada@example.com")),
    Person(FullName("Alan Turing"),
           EmailAddress("alan@example.com")),
]
print(json.dumps(people, cls=DataClassEncoder, indent=2))
#: [
#:   {
#:     "name": {
#:       "text": "Ada Lovelace"
#:     },
#:     "email": {
#:       "text": "ada@example.com"
#:     }
#:   },
#:   {
#:     "name": {
#:       "text": "Alan Turing"
#:     },
#:     "email": {
#:       "text": "alan@example.com"
#:     }
#:   }
#: ]
```

`json.dumps()` calls `default()` for any object it cannot serialize on its own.
The encoder converts each data class to a dictionary and the base encoder handles it from there,
recursing through lists and nested objects.
`is_dataclass()` answers `True` for the class object as well as for an instance,
and `asdict()` accepts only instances,
so `not isinstance(o, type)` keeps a bare class object from reaching it.

Encoding is mechanical, but decoding must know which type to rebuild,
and that part the standard library leaves to you.
For deep or evolving structures, [Pydantic](https://docs.pydantic.dev)
and [dataclasses-json](https://github.com/lidatong/dataclasses-json)
automate the decode side,
reconstructing nested types from the parsed JSON and validating as they go.

## Where the Checks Went

The checks did not disappear.
They moved.
`stars_unchecked.py` spread them across every function that took a rating,
and `stars_class.py` spread them across every method that changed one.
`stars.py` put them in the constructor,
where they run once and nothing can skip them,
because the constructor is the only way to make the value.

That trade has a price, and the price is at the edges.
Every place data enters your program now needs a constructor call:
the parsed JSON, the database row, the form field, the command-line argument.
`from_json()` is that boundary written out.
It reads untrusted text and hands the pieces to `FullName` and `EmailAddress`,
which is the last point where a bad value is cheap to reject.
Past that line your code holds types rather than raw data,
and a function receiving one does its work without asking whether the value makes sense.

## Exercises

1.  Add leap-year support to `Month`,
    so February allows 29 days when the `BirthDate`'s `Year` is a leap year.
    Write the tests first.
2.  Give `EmailAddress` a stricter check
    (a single `@`, with text on both sides).
    Add tests for the values the check should now reject.
3.  Take `test_namedtuple_no_hook.py`'s `Stars` and build the subclass workaround:
    a `_Stars(NamedTuple)` holding the field,
    and a `Stars(_Stars)` whose `__new__()` runs the check.
    Show that `Stars(11)` now raises a `TypeFailure` while `copy.replace(Stars(5), number=99)` does not,
    and explain why a frozen data class has no equivalent hole.
4.  Feed `from_json()` a JSON string whose email has no `@`,
    and confirm that it raises `TypeFailure`.
    The validation you wrote once, in `EmailAddress`,
    now also guards your JSON input.
5.  Give `Stars` a `copy.replace()`-based variant helper without using a data class:
    write an ordinary class holding the rating, define `__replace__()`,
    and confirm that `copy.replace()` still runs your validation.
6.  Add a `ClassVar[int]` counter to `Stars` that counts every `Stars` created.
    Predict whether it appears in the generated `__init__()`'s parameter list before you run it,
    then check with `display_object()`.
    Incrementing the counter from `__post_init__()` works on a frozen class.
    Explain why.
7.  Give `Months` a second field,
    a `dict[str, Month]` index written with a `= {}` default,
    and read the error `@dataclass` reports.
    Then fix it two ways,
    with `default_factory=dict` and with `default_factory=dict[str, Month]`,
    and say which one a checker can verify.
