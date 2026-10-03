# Data Classes as Types: Solutions

## 1. Leap-year support for `Month`, tests written first

> Add leap-year support to `Month`,
> so February allows 29 days when the `BirthDate`'s `Year` is a leap year.
> Write the tests first.

<details>
<summary>Where to look</summary>

[Enums Are Types Too](../../Chapters/12_Techniques--Data_Classes_as_Types.md#enums-are-types-too) shows `Month` checking a day against its own cap.
The cap now depends on a second value, so `check_day()` needs the `Year` as well, and `Year` needs a method that applies the leap rule.
Write the `pytest` tests first, covering a leap year, a year that is not leap, the leap century 2000, and a day that fails in every year.
`Year` accepts 1901 through the current year, so it rejects 1900 and 2100, the century years that are not leap.

<details>
<summary>Solution</summary>

If you drop the `% 400` clause from `is_leap()`,
every century year counts as common,
and `test_feb_29_allowed_in_2000` fails when `check_day()` raises a `TypeFailure` for `Day(29)`.
A test for divisibility by 4 alone passes all four tests,
because 2000 is the one century year `Year` accepts.
The solution still writes the full rule,
because `Year`'s upper bound follows `date.today()`,
and 2100 is not a leap year.

`Year` gains an `is_leap()` method using the standard rule (divisible
by 4, and not by 100 unless also by 400). `Month.check_day()` takes
the `Year` as a second argument so it can raise February's cap to 29
only when the year is leap:

```python
# test_ch12_leap_year.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
import pytest

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

    def is_leap(self) -> bool:
        return self.n % 4 == 0 and (
            self.n % 100 != 0 or self.n % 400 == 0)

class Month(Enum):
    JANUARY = (1, 31)
    FEBRUARY = (2, 28)
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
        check(1 <= month_number <= 12,
              f"Month({month_number})")
        return list(Month)[month_number - 1]

    @property
    def max_days(self) -> int:
        return self.value[1]

    def check_day(self, day: Day, year: Year) -> None:
        max_days = self.max_days
        if self is Month.FEBRUARY and year.is_leap():
            max_days = 29
        check(day.n <= max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day, self.year)

def test_feb_29_allowed_in_leap_year() -> None:
    bd = BirthDate(Month.of(2), Day(29), Year(2020))
    assert bd.day.n == 29

def test_feb_29_allowed_in_2000() -> None:
    bd = BirthDate(Month.of(2), Day(29), Year(2000))
    assert bd.day.n == 29

def test_feb_29_rejected_in_non_leap_year() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(29), Year(2021))

def test_feb_30_always_rejected() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(30), Year(2020))
```

**Accept both kinds of leap year.**
`BirthDate(Month.of(2), Day(29), Year(2020))` succeeds because 2020 is
divisible by 4 and not by 100. 2000 is divisible by 100 and also by
400, so it is a leap year too, and it is the one century year `Year`
accepts.

**Reject a day past the cap.** `Year(2021)` is not leap, so
`check_day()` rejects the same day. `check_day()` rejects February 30
regardless of the year, because `max_days` is 29 at most, even in a
leap year.

</details>
</details>

## 2. A stricter `EmailAddress`

> Give `EmailAddress` a stricter check
> (a single `@`, with text on both sides).
> Add tests for the values the check should now reject.

<details>
<summary>Where to look</summary>

[Composing Types from Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#composing-types-from-types) puts the check for `EmailAddress` in `__post_init__()`.
Strengthen it there with two calls to `check()`: one that counts the `@` characters, and one that splits the text with `str.partition()` and tests both halves.
The tests feed it each shape the new check should reject.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you keep only the `partition()` check, `"b@@x.com"` passes:
`partition()` splits at the first `@`,
and the domain half, `"@x.com"`, is not empty.
The demo loop stops there with an `AssertionError`,
because `expect()` finds no exception to report.
Counting the `@` characters closes that gap,
so the solution makes two calls to `check()`.

```python
# exercise_2.py
from dataclasses import dataclass
from exceptions import expect

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

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check(self.text.count("@") == 1,
              f"EmailAddress({self.text!r})",
              "needs exactly one @")
        local, _, domain = self.text.partition("@")
        check(len(local) > 0 and len(domain) > 0,
              f"EmailAddress({self.text!r})",
              "needs text on both sides")

for bad in ["grace", "b@@x.com", "@x.com", "b@", ""]:
    expect(TypeFailure, EmailAddress, bad)
#: [TypeFailure] EmailAddress('grace') needs exactly one @
#: [TypeFailure] EmailAddress('b@@x.com') needs exactly one
#: @
#: [TypeFailure] EmailAddress('@x.com') needs text on both
#: sides
#: [TypeFailure] EmailAddress('b@') needs text on both sides
#: [TypeFailure] EmailAddress('') needs exactly one @

print(EmailAddress("grace@example.com"))
#: EmailAddress(text='grace@example.com')
```

**Require a single `@`.**
The original check, `"@" in self.text`, only confirms an `@` appears
somewhere. `count("@") == 1` additionally rejects two-`@` strings like
`"b@@x.com"`.

**Require text on both halves.** The second check splits on `@` and requires text on both
sides, so it rejects `"@x.com"` and `"b@"`.

</details>
</details>
</details>

## 3. The `NamedTuple` subclass workaround, and the hole it leaves

> Take `test_namedtuple_no_hook.py`'s `Stars` and build the subclass workaround:
> a `_Stars(NamedTuple)` holding the field,
> and a `Stars(_Stars)` whose `__new__()` runs the check.
> Show that `Stars(11)` now raises a `TypeFailure` while `copy.replace(Stars(5), number=99)` does not,
> and explain why a frozen data class has no equivalent hole.

<details>
<summary>Where to look</summary>

[A `NamedTuple` Cannot Validate Itself](../../Chapters/12_Techniques--Data_Classes_as_Types.md#namedtuple-cannot-validate) explains why the class body of a `NamedTuple` refuses a `__new__()`.
A subclass is free to define one, so put the check there and call `super().__new__()` afterward.
For the hole, find which method `copy.replace()` calls on a `NamedTuple` and whether it passes through your `__new__()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import copy
from dataclasses import dataclass
from typing import NamedTuple
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

class _Stars(NamedTuple):
    number: int

class Stars(_Stars):
    def __new__(cls, number: int) -> Stars:
        ...
```

<details>
<summary>Solution</summary>

If you define `__new__()` in the `NamedTuple` class body,
the `class` statement raises an `AttributeError`
(`Cannot overwrite NamedTuple attribute __new__`),
and `Stars` stays undefined.
[A `NamedTuple` Cannot Validate Itself](../../Chapters/12_Techniques--Data_Classes_as_Types.md#namedtuple-cannot-validate) shows the same failure in its third test.
The prohibition covers only the body that `NamedTuple` processes,
so the solution defines `__new__()` in a subclass.

```python
# exercise_3.py
import copy
from dataclasses import dataclass
from typing import NamedTuple
from exceptions import expect

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

class _Stars(NamedTuple):
    number: int

class Stars(_Stars):
    def __new__(cls, number: int) -> Stars:
        check(1 <= number <= 10, f"Stars({number})")
        return super().__new__(cls, number)

print(Stars(5))
#: Stars(number=5)
expect(TypeFailure, Stars, 11)
#: [TypeFailure] Stars(11)

print(Stars(5)._replace(number=99))
#: Stars(number=99)
print(copy.replace(Stars(5), number=99))
#: Stars(number=99)
```

**Validate in a subclass.**
`typing.NamedTuple` refuses a `__new__()` in its own class body but
accepts one in a subclass, so `Stars(11)` now raises a `TypeFailure`.
The chapter's factory function can only advise against that call.

**Test the replacement path.** The guarantee still leaks. `_replace()` builds the new tuple through
`tuple.__new__()` rather than through `cls.__new__()`, so it skips
the check. `copy.replace()` calls `_replace()` and inherits the hole.
A validated `Stars` therefore produces an unvalidated one.
That leak is worse than no check: the type now looks like it guarantees its values.

A frozen data class has no equivalent hole because its replacement
goes through the constructor. `copy.replace()` calls the constructor,
the constructor calls `__post_init__()`, and the check runs.

</details>
</details>
</details>

## 4. `from_json()` rejects a bad email

> Feed `from_json()` a JSON string whose email has no `@`,
> and confirm that it raises `TypeFailure`.
> The validation you wrote once, in `EmailAddress`,
> now also guards your JSON input.

<details>
<summary>Where to look</summary>

[Serializing to JSON](../../Chapters/12_Techniques--Data_Classes_as_Types.md#serializing-to-json) rebuilds a `Person` from parsed JSON by calling the field classes.
Build a JSON string whose email lacks an `@` with `json.dumps()`, and pass it to `from_json()`.
Watch which code raises the `TypeFailure`: the constructor of `EmailAddress`, not `from_json()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import json
from dataclasses import dataclass
from typing import Any
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

@dataclass(frozen=True)
class FullName:
    text: str

    def __post_init__(self) -> None:
        ...

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        ...

@dataclass(frozen=True)
class Person:
    name: FullName
    email: EmailAddress

def from_json(text: str) -> Person:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
import json
from dataclasses import dataclass
from typing import Any
from exceptions import expect

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

def from_json(text: str) -> Person:
    data: dict[str, Any] = json.loads(text)
    return Person(
        FullName(data["name"]["text"]),
        EmailAddress(data["email"]["text"]),
    )

bad_json = json.dumps(
    {"name": {"text": "Grace Hopper"},
     "email": {"text": "no-at-sign"}})
expect(TypeFailure, from_json, bad_json)
#: [TypeFailure] EmailAddress('no-at-sign') needs an @
```

**Let the field types validate.**
`from_json()` does not validate the email string. It hands the raw
JSON value straight to `EmailAddress(...)`, and `EmailAddress`'s own
`__post_init__()` runs the same check it runs for any other caller.
One check, inside `EmailAddress`, protects every path that constructs
a `Person`. The path from untrusted JSON input is one of those, with
no additional code in `from_json()`.

</details>
</details>
</details>

## 5. `__replace__()` on an ordinary class

> Make `copy.replace()` work on a `Stars` that is not a data class:
> write an ordinary class holding the rating, validate in `__init__()`,
> define `__replace__()`,
> and confirm that `copy.replace()` still runs your validation.

<details>
<summary>Where to look</summary>

[Defining `__replace__()`](../../Chapters/12_Techniques--Data_Classes_as_Types.md#defining-replace) shows the method that `copy.replace()` calls.
In an ordinary class, write `__replace__()` so it merges the current field values with the keyword changes and calls the class constructor.
Because the rebuild goes through `__init__()`, the check runs on the replacement.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import copy
from dataclasses import dataclass
from typing import Self
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

class Stars:
    def __init__(self, number: int) -> None:
        ...

    def __repr__(self) -> str:
        ...

    def __replace__(self, **changes: int) -> Self:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
import copy
from dataclasses import dataclass
from typing import Self
from exceptions import expect

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

class Stars:
    def __init__(self, number: int) -> None:
        check(1 <= number <= 10, f"Stars({number})")
        self.number = number

    def __repr__(self) -> str:
        return f"Stars({self.number})"

    def __replace__(self, **changes: int) -> Self:
        return type(self)(
            **({"number": self.number} | changes))

s = Stars(4)
print(copy.replace(s, number=9))
#: Stars(9)
expect(TypeFailure, copy.replace, s, number=99)
#: [TypeFailure] Stars(99)
```

**Merge the changes into the arguments.**
`copy.replace()` looks for `__replace__()` and calls it with the
keyword changes. This implementation recovers the constructor
arguments (`{"number": self.number}`), uses `|` to override the
arguments the changes name, and rebuilds through `type(self)(...)`.

**Validate the replacement.** The validation runs
because the rebuild goes through `__init__()`. A frozen data class
stays validated across a replacement for the same reason. Any
`__replace__()` that restores the state directly, the way
`copy.copy()` does, skips the check.

</details>
</details>
</details>

## 6. A `ClassVar` counter on a frozen `Stars`

> Add a `ClassVar[int]` counter to `Stars` that counts every `Stars` created.
> Predict whether it appears in the generated `__init__()`'s parameter list before you run it,
> then check by printing `inspect.signature(Stars.__init__)`.
> Incrementing the counter as `Stars.built += 1` from `__post_init__()` works on a frozen class,
> while `self.built += 1` does not.
> Explain why.

<details>
<summary>Where to look</summary>

[A Real `ClassVar`](../../Chapters/12_Techniques--Data_Classes_as_Types.md#d-a-real-classvar) shows how `@dataclass` treats an annotation marked `ClassVar`.
It skips that name when it builds the fields and the `__init__()` parameters, so check `fields()` and `inspect.signature()`.
For the frozen question, compare the target of `Stars.built += 1` with the target of `self.built += 1`, and which of the two `frozen=True` guards (see [Immutability](../../Chapters/12_Techniques--Data_Classes_as_Types.md#immutability)).

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
import inspect
from dataclasses import dataclass, fields
from typing import ClassVar
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

@dataclass(frozen=True)
class Stars:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        ...

@dataclass(frozen=True)
class Wrong:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
import inspect
from dataclasses import dataclass, fields
from typing import ClassVar
from exceptions import expect

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

@dataclass(frozen=True)
class Stars:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10,
              f"Stars({self.number})")
        Stars.built += 1

print([f.name for f in fields(Stars)])
#: ['number']
print(inspect.signature(Stars.__init__))
#: (self, number: int) -> None

for n in (3, 4, 5):
    Stars(n)
print(Stars.built)
#: 3

@dataclass(frozen=True)
class Wrong:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        self.built += 1  # type: ignore

expect(Exception, Wrong, 1)
#: [FrozenInstanceError] cannot assign to field 'built'
```

**Keep the counter out of the fields.**
`@dataclass` reads the annotation, sees `ClassVar`, and leaves `built`
alone as an ordinary class attribute, so `built` stays out of
`__init__()`. `dataclasses.fields()` reports only `number`, and the
generated signature takes only `number`.

**Count on the class.**
`frozen=True` installs a `__setattr__()` that rejects assignment to
an instance. `Stars.built += 1` assigns to the class instead, so it
works.

**Show the instance store failing.** `Wrong` writes the same intent a different way, and fails:
`self.built += 1` reads the class attribute, adds one, and then tries
to store the result on the instance. That store is the assignment
`frozen=True` refuses. The type checker rejects the line before the program runs,
reporting `built` as read-only on a frozen instance, so the listing
carries a `# type: ignore` to demonstrate the runtime failure.

</details>
</details>
</details>

## 7. A `dict` field default, three ways

> Give `Months` a second field,
> a `dict[str, Month]` index written with a `= {}` default,
> and read the error `@dataclass` reports.
> Then fix it two ways,
> with `default_factory=dict` and with `default_factory=dict[str, Month]`,
> and say which one a type checker can verify.

<details>
<summary>Where to look</summary>

[Defaults Built Fresh, Not Shared](../../Chapters/12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared) shows `@dataclass` rejecting a mutable default and `field(default_factory=...)` as the fix.
Wrap the class definition that has the `= {}` default in `expected(ValueError)` to capture the message.
Then write the two fixed classes, and ask what return type a type checker can read from `dict` and from `dict[str, Month]`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass(frozen=True)
class Month:
    name: str
    n: int

def make_months() -> list[Month]:
    ...

@dataclass(frozen=True)
class Bare:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict)

@dataclass(frozen=True)
class Subscripted:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(
        default_factory=dict[str, Month])
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from dataclasses import dataclass, field
from exceptions import expected

@dataclass(frozen=True)
class Month:
    name: str
    n: int

def make_months() -> list[Month]:
    return [Month("January", 1), Month("February", 2)]

with expected(ValueError):
    @dataclass(frozen=True)
    class Broken:
        months: list[Month] = field(
            default_factory=make_months)
        index: dict[str, Month] = {}
#: [ValueError] mutable default <class 'dict'> for field
#: index is not allowed: use default_factory

@dataclass(frozen=True)
class Bare:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict)

@dataclass(frozen=True)
class Subscripted:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(
        default_factory=dict[str, Month])

print(Bare().index, Subscripted().index)
#: {} {}
```

**Provoke the decorator's error.**
`= {}` fails at the class definition, before any instance exists.
`@dataclass` inspects the default as the decorator runs, finds an
unhashable object, and raises a `ValueError` naming the fix.

**Fix it with a bare factory.**
`Bare` and `Subscripted` both work, and they differ in what `ty`
sees. For `field(default_factory=dict)` `ty` infers `Unknown`, a type
that satisfies any annotation, so `ty` does not compare the factory
against the field. Checkers differ here: Pyright and mypy
both compare the bare factory and reject a mismatched one.

**Give the checker a return type.**
`dict[str, Month]` is callable too, and its return type is concrete, so
`field(default_factory=dict[int, int])` on this field draws a type
error before the program runs. The bare form is fine where a reader
can see that the factory and the annotation agree. Subscript the
factory when you want the checker to confirm the agreement.

</details>
</details>
</details>

## 8. A type test in the check

> `stars_float.py` builds a `Stars` holding `5.5`.
> Add a type test to the check in `__post_init__()` so that `Stars(5.5)` raises `TypeFailure`.
> `Stars(True)` also passes the range check.
> Explain why an `isinstance()` test accepts it,
> and write the test so that it rejects `True` as well.

<details>
<summary>Where to look</summary>

[The Annotation and the Check](../../Chapters/12_Techniques--Data_Classes_as_Types.md#the-annotation-and-the-check) shows `Stars(5.5)` passing because Python does not enforce the annotation at runtime.
Add a type test as the first call to `check()` in `__post_init__()`, before the range comparison.
For `True`, consider how `bool` relates to `int`, and compare the class of the value directly instead of using `isinstance()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from dataclasses import dataclass
from exceptions import expect

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        ...

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    ...

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you write the type test as `isinstance(self.number, int)`,
the test [The Annotation and the Check](../../Chapters/12_Techniques--Data_Classes_as_Types.md#the-annotation-and-the-check) shows for a type built at a JSON boundary,
`Stars(5.5)` and `Stars("five")` raise a `TypeFailure`,
but `Stars(True)` builds `Stars(number=True)`.
The demo loop then stops with an `AssertionError`,
because `expect()` finds no exception to report.
The solution compares the class of the value with `int`,
a test that a `bool` fails.

```python
# exercise_8.py
from dataclasses import dataclass
from exceptions import expect

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

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(type(self.number) is int,
              f"Stars({self.number!r})", "needs an int")
        check(1 <= self.number <= 10,
              f"Stars({self.number})")

print(Stars(5))
#: Stars(number=5)
for bad in (5.5, True, "five"):
    expect(TypeFailure, Stars, bad)  # type: ignore
#: [TypeFailure] Stars(5.5) needs an int
#: [TypeFailure] Stars(True) needs an int
#: [TypeFailure] Stars('five') needs an int

print(issubclass(bool, int), isinstance(True, int))
#: True True
```

**Test the exact class.**
`bool` is a subclass of `int`, so `isinstance(True, int)` is `True`
and an `isinstance()` test admits `True` as the rating 1.
`type(self.number) is int` compares the class of the value with `int`
and rejects a `bool` along with a `float` and a `str`.

**Test the type before the range.** The type test runs first. Comparing `"five"` with `1` raises a
`TypeError`, so with the range check first a `str` ends in that
`TypeError` instead of a `TypeFailure`.

**Feed values the checker refuses.** The type checker rejects `5.5`
and `"five"` as arguments before the program runs, and the
`# type: ignore` silences that report so the listing can show what the
constructor does with each value at runtime. The type checker accepts
`Stars(True)`: a `bool` is an `int` to it for the same subclass
reason, so the runtime test is the one check that rejects `True`.

</details>
</details>
</details>
