# Data Classes as Types: Solutions

## 1. Leap-year support for `Month`, tests written first

`Year` gains an `is_leap()` method using the standard rule (divisible
by 4, and not by 100 unless also by 400), and `Month.check_day()`
takes the `Year` as a second argument so it can raise February's cap
to 29 only when the year is leap:

```python
# test_ch12_leap_year.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum
import pytest

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
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
        check(1900 < self.n <= date.today().year, f"Year({self.n})")

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
        check(1 <= month_number <= 12, f"Month({month_number})")
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

def test_feb_29_rejected_in_non_leap_year() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(29), Year(2021))

def test_feb_30_always_rejected() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(30), Year(2020))
```

`BirthDate(Month.of(2), Day(29), Year(2020))` succeeds because 2020 is
divisible by 4 and not by 100. `Year(2021)` is not leap, so the same
day is rejected. February 30 is rejected regardless of the year,
because `max_days` never exceeds 29 even in a leap year.

## 2. A stricter `EmailAddress`

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

@dataclass(frozen=True)
class EmailAddress:
    text: str

    def __post_init__(self) -> None:
        check(self.text.count("@") == 1,
              f"EmailAddress({self.text!r})", "needs exactly one @")
        local, _, domain = self.text.partition("@")
        check(len(local) > 0 and len(domain) > 0,
              f"EmailAddress({self.text!r})",
              "needs text on both sides")

for bad in ["bruce", "b@@x.com", "@x.com", "b@", ""]:
    try:
        EmailAddress(bad)
    except TypeFailure as e:
        print("rejected:", bad, "->", e)
#: rejected: bruce -> EmailAddress('bruce') needs exactly one @
#: rejected: b@@x.com -> EmailAddress('b@@x.com') needs exactly one @
#: rejected: @x.com -> EmailAddress('@x.com') needs text on both sides
#: rejected: b@ -> EmailAddress('b@') needs text on both sides
#: rejected:  -> EmailAddress('') needs exactly one @

print(EmailAddress("bruce@example.com"))
#: EmailAddress(text='bruce@example.com')
```

The original check, `"@" in self.text`, only confirms an `@` appears
somewhere. `count("@") == 1` additionally rejects two-`@` strings like
`"b@@x.com"`, and splitting on `@` and checking both halves are
non-empty rejects an `@` with nothing before or after it.

## 3. The `NamedTuple` subclass workaround, and the hole it leaves

```python
# exercise_3.py
import copy
from dataclasses import dataclass
from typing import NamedTuple

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
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
try:
    Stars(11)
except TypeFailure as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(11)

print(Stars(5)._replace(number=99))
#: Stars(number=99)
print(copy.replace(Stars(5), number=99))
#: Stars(number=99)
```

`typing.NamedTuple` refuses a `__new__()` in its own class body, but it
does not refuse one in a subclass, so `Stars(11)` now raises a
`TypeFailure` the factory function could only advise against.

The guarantee still leaks. `_replace()` builds the new tuple through
`tuple.__new__()` rather than through `cls.__new__()`, so it never sees
the check, and `copy.replace()` calls `_replace()`. A validated `Stars`
therefore produces an unvalidated one, which is worse than no check at
all: the type now looks like it guarantees its values.

A frozen data class has no equivalent hole because there is only one
construction path. `copy.replace()` calls the constructor, the
constructor calls `__post_init__()`, and the check runs.

## 4. `from_json()` rejects a bad email

```python
# exercise_4.py
import json
from dataclasses import dataclass

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

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

def from_json(text: str) -> Person:
    data = json.loads(text)
    return Person(FullName(data["name"]), EmailAddress(data["email"]))

bad_json = json.dumps({"name": "Bruce Eckel", "email": "no-at-sign"})
try:
    from_json(bad_json)
except TypeFailure as e:
    print("from_json rejected bad email:", e)
#: from_json rejected bad email: EmailAddress('no-at-sign') needs an @
```

`from_json()` never validates the email string itself. It hands the
raw JSON value straight to `EmailAddress(...)`, and `EmailAddress`'s
own `__post_init__()` runs the same check it runs for any other
caller. The validation written once, inside `EmailAddress`, protects
every path that constructs a `Person`, including this one from
untrusted JSON input, with no additional code in `from_json()` itself.

## 5. `__replace__()` on an ordinary class

```python
# exercise_5.py
import copy
from dataclasses import dataclass
from typing import Self

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

class Stars:
    def __init__(self, number: int) -> None:
        check(1 <= number <= 10, f"Stars({number})")
        self.number = number

    def __repr__(self) -> str:
        return f"Stars({self.number})"

    def __replace__(self, **changes: int) -> Self:
        return type(self)(**({"number": self.number} | changes))

s = Stars(4)
print(copy.replace(s, number=9))
#: Stars(9)
try:
    copy.replace(s, number=99)
except TypeFailure as e:
    print(f"{type(e).__name__}: {e}")
#: TypeFailure: Stars(99)
```

`copy.replace()` looks for `__replace__()` and calls it with the
keyword changes. This implementation recovers the constructor
arguments (`{"number": self.number}`), overrides the named ones with
`|`, and rebuilds through `type(self)(...)`. The validation runs
because the rebuild goes through `__init__()`, which is the same
reason a frozen data class stays validated across a replacement. Any
`__replace__()` that restored the state directly, the way
`copy.copy()` does, would skip the check.

## 6. A `ClassVar` counter on a frozen `Stars`

```python
# exercise_6.py
import inspect
from dataclasses import dataclass, fields
from typing import ClassVar

@dataclass(eq=False)
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str, reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

@dataclass(frozen=True)
class Stars:
    number: int
    built: ClassVar[int] = 0

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")
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

try:
    Wrong(1)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
#: FrozenInstanceError: cannot assign to field 'built'
```

`built` never reaches `__init__()`. `dataclasses.fields()` reports
only `number`, and the generated signature takes only `number`, so a
`ClassVar` is invisible to construction: `@dataclass` reads the
annotation, sees `ClassVar`, and leaves the name alone as an ordinary
class attribute.

`Stars.built += 1` works on a frozen class because it assigns to the
class, and `frozen=True` installs its rejecting `__setattr__()` on
instances. `Wrong` writes the same intent a different way, and fails.
`self.built += 1` reads the class attribute, adds one, and then tries
to store the result on the instance, which is the assignment
`frozen=True` refuses. `ty` rejects the line before it ever runs
(fields of a frozen class are read-only to the type checker), so the
listing carries a `# type: ignore` to demonstrate the runtime failure.

## 7. A `dict` field default, three ways

```python
# exercise_7.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Month:
    name: str
    n: int

def make_months() -> list[Month]:
    return [Month("January", 1), Month("February", 2)]

try:
    @dataclass(frozen=True)
    class Broken:
        months: list[Month] = field(default_factory=make_months)
        index: dict[str, Month] = {}
except ValueError as e:
    print(f"{type(e).__name__}: {str(e).split(': ')[-1]}")
#: ValueError: use default_factory

@dataclass(frozen=True)
class Bare:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict)

@dataclass(frozen=True)
class Subscripted:
    months: list[Month] = field(default_factory=make_months)
    index: dict[str, Month] = field(default_factory=dict[str, Month])

print(Bare().index, Subscripted().index)
#: {} {}
```

`= {}` never reaches a running program. `@dataclass` inspects the
default while the class is being created, finds an unhashable object,
and raises a `ValueError` naming the fix. The full message is `mutable
default <class 'dict'> for field index is not allowed: use
default_factory`.

`Bare` and `Subscripted` both work, and they differ in what a type checker
can see. `dict` is a class whose call returns `dict[Unknown, Unknown]`,
loose enough to satisfy any `dict` annotation, so a type checker cannot
compare the factory against the field. `dict[str, Month]` is callable
too, and its return type is concrete, so writing
`field(default_factory=dict[int, int])` on this field is an error
before the program runs. The bare form is fine where the factory and
the annotation obviously agree; subscript it when you want the
agreement checked.
