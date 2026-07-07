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

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

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
        check(day.n <= max_days, f"{self.name} has no day {day.n}")

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

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

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

## 3. `Stars` as a frozen data class, guarantees replace checks

```python
# exercise_3.py
from dataclasses import dataclass

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

@dataclass(frozen=True)
class Stars:
    number: int

    def __post_init__(self) -> None:
        check(1 <= self.number <= 10, f"Stars({self.number})")

    def f1(self) -> Stars:
        return Stars(self.number + 5)

print(Stars(2).f1())
#: Stars(number=7)
try:
    Stars(4).f1().f1()  # 4+5=9 legal, then 9+5=14 illegal
except TypeFailure as e:
    print("caught postcondition failure:", e)
#: caught postcondition failure: Stars(14)
```

Compare this to `stars_class.py`'s mutable `f1()`, which needs an
explicit `self._validate()` call after mutating `self._number`, its
postcondition written out by hand. Here `f1()` just returns
`Stars(self.number + 5)`. Building that new `Stars` runs
`__post_init__()` automatically, so the postcondition is enforced by
construction rather than a separate call, and there is no precondition
to write either: any `Stars` passed in is already known legal, since
it could not exist otherwise. The check moves from "written in every
method, easy to forget" to "run once, in the constructor, impossible
to skip."

## 4. `from_json()` rejects a bad email

```python
# exercise_4.py
import json
from dataclasses import dataclass

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

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
own `__post_init__()` runs the same check it would run for any other
caller. The validation written once, inside `EmailAddress`, protects
every path that constructs a `Person`, including this one from
untrusted JSON input, with no additional code in `from_json()` itself.
