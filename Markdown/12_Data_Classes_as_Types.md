# Data Classes as Types

A *type* is a set of values.
The type `int` is the set of whole numbers.
A type you define, like a rating from one to ten, is a smaller set:
the allowed values.
We have historically been bad at keeping objects inside that set.
We let an object be constructed in an illegal state,
or we let later code mutate it into one,
and then we scatter checks everywhere to defend against the mess.

This chapter shows a better approach, built from frozen data classes.
You validate the value once, at construction,
and freeze it so it can never change.
Every object of the type is then guaranteed to be a legal value.
Code that receives one never has to check it again.
This material comes from my PyCon 2022 talk,
[Making Data Classes Work for You](https://www.youtube.com/watch?v=w77Kjs5dEko).

This function will be used throughout the chapter.
It raises a custom exception when a value is not legal:

```python
# validation.py
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())
```

## A Value That Must Be Checked Everywhere

Suppose a rating is an integer from one to ten.
If you represent it as a plain `int`,
nothing stops a caller from passing eleven, or minus one.
So every function that takes a rating must check it:

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

rating = 6
print(rating)
#: 6
print(f1(rating))
#: 11
print(f2(rating))
#: 30
```

The check is duplicated, it is easy to forget, and the type system is no help.
The `int` annotation says "any integer," which is not what we mean.

## A Class Is Not a Type

The object-oriented answer is to wrap the value in a class and validate it in the constructor.
That is better, but it does not finish the job.
The value is still mutable, so every method that changes it must re-validate,
and a method can leave the object in an illegal state between steps:

```python
# stars_class.py
from validation import check

class Stars:
    def __init__(self, number: int) -> None:
        self._number = number  # Private by convention
        self._validate()

    def _validate(self) -> None:
        check(1 <= self._number <= 10, f"Stars({self._number})")

    @property
    def number(self) -> int:  # No setter: blocks outside mutation
        return self._number

    def __str__(self) -> str:
        return f"Stars({self._number})"

    def f1(self, n: int) -> int:
        check(1 <= n <= 10, f"f1({n})")  # Precondition
        self._number = n + 5
        self._validate()                 # Postcondition
        return self._number

if __name__ == "__main__":
    rating = Stars(4)
    print(rating)
    print(rating.f1(3))
#: Stars(4)
#: 8
```

A read-only property keeps outsiders from assigning to `number`,
but the class itself still mutates `_number` and must guard it with a precondition and a postcondition.
Checking arguments on the way in and results on the way out is the practice known as *Design by Contract* (DbC).
The problem with DbC is that the contract is spread across every method that touches the value.
That is the same scattering of checks as before, but moved inside the class.
The class encapsulates the value.
It does not constrain it to a set of legal values.

## Data Classes

A *data class* writes the boilerplate for a class that holds data.
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

```python
# demo_messenger.py
from dataclasses import replace
from messenger import Messenger

m = Messenger("foo", 12, 3.14)
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(m.name, m.number, m.depth)
#: foo 12 3.14

# __eq__ is generated, so equal fields compare equal:
print(Messenger("xx", 1) == Messenger("xx", 1))
#: True
print(Messenger("xx", 1) == Messenger("xx", 2))
#: False

mc = replace(m, depth=9.9)  # Copy with one field changed
print(m)
#: Messenger(name='foo', number=12, depth=3.14)
print(mc)
#: Messenger(name='foo', number=12, depth=9.9)

m.name = "bar"  # A plain data class is mutable
print(m)
#: Messenger(name='bar', number=12, depth=3.14)
```

`replace()` returns a copy with some fields changed, leaving the original alone.
This copy-instead-of-mutate style reduces errors.
But notice the last two lines: a plain data class is still mutable,
so `m.name = "bar"` works.

A data class is a type defined by its fields. `display_object()`, the
inspection helper from [Metaprogramming](18_Metaprogramming.md#the-inspect-module),
shows those fields with the types they were declared with:

```python
# display_messenger.py
from display import display_object
from messenger import Messenger

display_object(Messenger("foo", 12, 3.14))
#: === Messenger ===
#: [Attributes]
#:   • depth: float = 3.14
#:   • name: str = 'foo'
#:   • number: int = 12
#: [Methods]
#:   None
```

The generated `__init__()`, `__repr__()`, and `__eq__()` are dunders,
which are not shown by the default `display_object()`.

## Immutability

Passing `frozen=True` makes the data class immutable.
Attempting to assign to a field raises `FrozenInstanceError`.
As a bonus, a frozen instance is hashable,
so you can use it as a dictionary key or put it in a set:

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

cache = {m: "value"}  # Frozen instances are hashable
print(cache[m])
#: value
```

If an object cannot change after it is built, then validating it once,
at construction, is enough for its whole life.

## A Type Is a Set of Values

If we make `Stars` a frozen data class,
we can guarantee that every `Stars` object is legal.
To validate it after the fields are filled in, we call `__post_init__()`,
which is one of the hooks the `dataclass` machinery generates code around:

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

`Stars` now names a set of values: the integers one through ten.
The only way to make a `Stars` is through the constructor,
and the constructor refuses anything outside the set.
So if you are holding a `Stars`, it is legal.
You know it without checking.

This changes how the functions are written.
`f1()` and `f2()` take a `Stars` and return a `Stars`.
They do not check their argument, because a `Stars` is already known to be good.
They do not test their result, because building the returned `Stars` runs the check.

The validation lives in exactly one place, the constructor (which makes it easy to change).
Immutability guarantees no one can damage the value after that.

This principle is often stated as *parse, don't validate*.
Instead of checking a changeable value everywhere and hoping you never miss a spot,
you parse it once into a precise type.
After that, holding the type is proof the check passed.
The check is not repeated because it cannot fail:
an illegal value can never produce a `Stars` in the first place.
Illegal values are unrepresentable.

The style here is functional: instead of mutating an object and re-guarding it,
you transform one legal value into a new legal value.
[Static Typing](08_Static_Typing.md#type-hints) argues for letting the type carry the meaning.
Here the type carries a guarantee.

Testing validates the claim that illegal values cannot exist.
`pytest.raises()` ensures that the constructor rejects every value outside the set:

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
It cannot be built from an illegal name or an illegal email,
because those values cannot exist.

The tests confirm that an illegal `FullName` or `EmailAddress` is rejected at construction:

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

## Enums Are Types Too

When the set of values is small and fixed, an `Enum` is the clearest type.
As an example, we'll create a `BirthDate` containing a month, day, and year.
There are exactly twelve months, so `Month` is an `Enum`.
Each month carries its length, and knows how to check a `Day` against it.
A `BirthDate` then validates across its fields: the day must fit the month.

```python
# birth_date.py
from dataclasses import dataclass
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
        check(1900 < self.n <= 2026, f"Year({self.n})")

class Month(Enum):
    JANUARY = (1, 31)
    FEBRUARY = (2, 28)   # Leap years are left as an exercise
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
        check(day.n <= self.max_days,
              f"{self.name} has no day {day.n}")

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

```python
# test_birth_date.py
import pytest
from birth_date import BirthDate, Day, Month, Year
from validation import TypeFailure

def test_valid_date() -> None:
    bd = BirthDate(Month.of(7), Day(8), Year(1957))
    assert bd.month is Month.JULY

@pytest.mark.parametrize("month_n, day_n", [
    (2, 31),   # February has 28 days
    (4, 31),   # April has 30
    (9, 31),   # September has 30
])
def test_day_out_of_range_for_month(month_n: int, day_n: int) -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(month_n), Day(day_n), Year(2020))

@pytest.mark.parametrize("bad", [0, 13, -1])
def test_bad_month_number(bad: int) -> None:
    with pytest.raises(TypeFailure):
        Month.of(bad)
```

## When a Data Class Is the Wrong Tool

You can build `Month` as a data class instead of an `Enum`.
It works, but it is more code for less safety.
You must construct the twelve months yourself and carry them around,
whereas the `Enum` *is* that set:

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
              f"max_days {self.max_days}")

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days,
              f"{self.name} has no day {day.n}")

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

Choose the tool that makes the legal set easiest to express.
For a small fixed set, that is an `Enum`.

When validation grows complicated, libraries make it lighter.
The [attrs](https://www.attrs.org) library predates and inspired data classes and offers richer validators and converters.
[Pydantic](https://docs.pydantic.dev) builds validation and parsing into the type itself,
which is especially useful at the edges of a program where untrusted data comes in.
The principle is the same:
make the type responsible for guaranteeing its own values.

## Inheritance and the Generated `__init__` {#dataclass-inheritance}

A data class builds its `__init__` from its fields and assigns them directly.
It does not call the base class `__init__`.
If you inherit from an ordinary class that does setup in its own constructor,
that setup is silently skipped:

```python
# dataclass_inherits_plain.py
from dataclasses import dataclass

class Connection:
    def __init__(self) -> None:
        self.open = True   # Setup the subclass needs

@dataclass
class Logged(Connection):
    name: str

c = Logged("db")
print(c.name)
#: db
# Connection.__init__ never ran, so 'open' was never set:
print(hasattr(c, "open"))
#: False
```

The generated `__init__` assigned `name` and stopped.
Nothing called `Connection.__init__`, so `open` does not exist.
This is easy to miss because the class still constructs without an error.

To run the base initializer, call it yourself from `__post_init__()`,
which runs after the generated `__init__` assigns the fields:

```python
# dataclass_super_init.py
from dataclasses import dataclass

class Connection:
    def __init__(self) -> None:
        self.open = True

@dataclass
class Logged(Connection):
    name: str

    def __post_init__(self) -> None:
        super().__init__()   # Run the base initializer explicitly

c = Logged("db")
print(c.name, c.open)
#: db True
```

When the base class is itself a data class, you do not need this.
The subclass generates one `__init__` covering the inherited fields and the new ones, in order:

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

The reason is that a data class assembles its `__init__` from a field list:
its own fields plus any inherited from data class bases.
It builds the body by assigning those fields, not by chaining to the base.
It has no way to know what arguments a non-data-class base constructor expects,
so it does not call it.

## More Data Class Tools

`asdict()` and `astuple()` convert an instance to a dictionary or tuple,
recursing into nested data classes.
`KW_ONLY` forces the fields after it to be passed by keyword:

```python
# dataclass_features.py
from dataclasses import KW_ONLY, asdict, astuple, dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

@dataclass(frozen=True)
class Line:
    points: list[Point]

@dataclass
class Config:
    source: str
    # Everything after this must be passed by keyword:
    _: KW_ONLY
    verbose: bool = False
    retries: int = 3

p = Point(10, 20)
print(asdict(p))   # Nested dict
#: {'x': 10, 'y': 20}
print(astuple(p))  # Nested tuple
#: (10, 20)
line = Line([Point(2, 7), Point(10, 4)])
print(asdict(line))  # Recurses into the list of Points
#: {'points': [{'x': 2, 'y': 7}, {'x': 10, 'y': 4}]}
print(Config("data.csv", retries=5))
#: Config(source='data.csv', verbose=False, retries=5)
```

## Serializing to JSON

A data class has no built-in JSON support.
Hand one to `json.dumps()` and it raises `TypeError: Object of type Person is not JSON serializable`.

`asdict()` turns the object into a nested dictionary,
and `json.dumps()` knows how to serialize dictionaries.
Decoding goes the other way: parse the JSON into a dictionary,
then hand its parts to the constructors.

```python
# json_round_trip.py
import json
from dataclasses import asdict
from person import EmailAddress, FullName, Person

def to_json(person: Person) -> str:
    return json.dumps(asdict(person), indent=2)

def from_json(text: str) -> Person:
    data = json.loads(text)
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
so malformed JSON is rejected at the boundary instead of leaking a bad object into the rest of the code.
The type guards itself.

When a data class is buried inside a larger structure you are dumping,
converting it by hand first is awkward.
A custom `JSONEncoder` serializes any data class it meets, even nested
inside other structures, by converting each one to a dict:

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
The encoder converts each data class to a dictionary and lets the base encoder take it from there,
recursing through lists and nested objects.

Encoding is mechanical, but decoding must know which type to rebuild,
and that is the part the standard library leaves to you.
For deep or evolving structures,
[Pydantic](https://docs.pydantic.dev) and [dataclasses-json](https://github.com/lidatong/dataclasses-json) automate the decode side,
reconstructing nested types from the parsed JSON and validating as they go.

## Exercises

1.  Add leap-year support to `Month`,
    so February allows 29 days when the `BirthDate`'s `Year` is a leap year.
    Write the tests first.
2.  Give `EmailAddress` a stricter check (a single `@`, with text on both sides).
    Add tests for the values that should now be rejected.
3.  Rewrite `stars_class.py`'s `Stars` as a frozen data class with a method that returns a new `Stars`,
    and show that the precondition and postcondition disappear.
4.  Feed `from_json()` a JSON string whose email has no `@`,
    and confirm that it raises `TypeFailure`.
    The validation you wrote once, in `EmailAddress`,
    now also guards your JSON input.
