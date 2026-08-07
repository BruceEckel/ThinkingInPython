# Pattern Matching

The `match` statement compares a value against a series of *patterns* and runs the first one that fits.
A `match` is far more than a `switch` because a pattern can test a value's shape,
look inside it, and pull out the parts you need, all in one step.

Pattern matching was briefly introduced in [Control Flow](04_Control_Flow.md#pattern-matching).

## Matching Values

The simplest patterns are literal values.
A `case _` at the end is the wildcard.
It matches anything, like a default.
Without one, a `match` that fits no pattern does nothing and raises no error.
Patterns are tried top to bottom and the first match wins:

```python
# http_status.py

def describe(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:  # Default
            return f"Status {status}"

print(describe(200))
#: OK
print(describe(404))
#: Not Found
print(describe(301))
#: Status 301
```

A literal pattern compares with `==`, not with `is`,
so `case 200:` also matches `200.0` and `case 1:` matches `True`.
`None`, `True`, and `False` are the exception: those three compare with `is`.

For a value-to-value lookup like this, a dictionary is often shorter
(see [When Not to Match](#when-not-to-match)).
`match` becomes valuable once the patterns do more than test equality.

## Alternatives and Capture

An alternative combines several patterns in one `case` with `|`.

A bare name is a *capture pattern*.
Like `_`, it matches any value unconditionally; unlike `_`,
it also binds the matched value to that name.
Here, `other` is the capture pattern:

```python
# step.py

def step(command: str) -> str:
    match command:
        case "up" | "u":
            return "y -= 1"
        case "down" | "d":
            return "y += 1"
        case other:
            return f"unknown command: {other}"

print(step("up"))
#: y -= 1
print(step("d"))
#: y += 1
print(step("jump"))
#: unknown command: jump
```

A bare name always binds.
It never compares against a variable of that name,
so a named constant in a `case` silently captures instead.
A *value pattern* is a dotted name, and it does compare:

```python
# value_patterns.py
from enum import Enum
from typing import Final

class Signal(Enum):
    STOP = "stop"
    GO = "go"

DEFAULT: Final[Signal] = Signal.STOP

def act(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case Signal.STOP:
            return "brake"

def broken(s: Signal) -> str:
    match s:
        case DEFAULT:
            return f"DEFAULT is now {DEFAULT}"
    return "unreachable"

print(act(Signal.GO), act(Signal.STOP))
#: accelerate brake
print(broken(Signal.GO))
#: DEFAULT is now Signal.GO
print(DEFAULT)
#: Signal.STOP
```

`case Signal.GO` compares.
`case DEFAULT` binds: it matches `Signal.GO`,
rebinds `DEFAULT` as a local name inside `broken()`,
and leaves the module-level constant untouched.
Python catches the mistake when a later `case` follows a bare-name capture,
refusing to compile with `SyntaxError: name capture 'DEFAULT' makes remaining patterns unreachable`.
When the capture is the last `case`, as here, nothing warns you.
`ruff` does notice, reporting `N806 Variable DEFAULT in function should be lowercase`,
which is the linter saying that `DEFAULT` here is a local variable rather than the constant you meant to compare against.

`act()` also shows why an enum is worth the trouble: `Signal` is a closed set,
so the checker sees that both members are covered and does not complain about the missing return.

## Sequence Patterns

A sequence pattern matches the shape of a list or tuple and binds the elements by position.
A starred name, as in `*rest`, captures the remaining elements:

```python
# sequence_patterns.py

def summarize(items: list[int]) -> str:
    match items:
        case []:
            return "Empty"
        case [only]:
            return f"One item: {only}"
        case [first, second]:
            return f"Two items: {first}, {second}"
        case [first, *rest]:
            return f"{first}, then {len(rest)} more"
        case _:
            return "Unreachable"

print(summarize([]))
#: Empty
print(summarize([5]))
#: One item: 5
print(summarize([3, 4]))
#: Two items: 3, 4
print(summarize([1, 2, 3, 4]))
#: 1, then 3 more
```

This shows the structural part of "structural pattern matching."
The pattern `[first, second]` matches only a two-element sequence and pulls both out at once.

A sequence pattern deliberately excludes `str`, `bytes`, and `bytearray`.
`case [a, b, c]` does not match `"abc"`,
even though a string is a sequence in every other context.
Iterating a string a character at a time is almost never what a pattern means,
so the language rules it out.
A tuple does match: `case [a, b, c]` accepts `(1, 2, 3)` as readily as `[1, 2, 3]`,
because the pattern describes a shape, not a concrete type.
The subject must be a sequence, though, not merely iterable:
`case [a, b]` matches a `range` but not a generator and not a `set`.

```python
# test_sequence_patterns.py
import pytest
from sequence_patterns import summarize

@pytest.mark.parametrize("items, expected", [
    ([], "Empty"),
    ([5], "One item: 5"),
    ([1, 2, 3], "1, then 2 more"),
])
def test_sequence_patterns(items: list[int], expected: str) -> None:
    assert summarize(items) == expected
```

## Class Patterns

A class pattern matches by type and extracts attributes.
With a data class you can match positionally or by keyword:

```python
# point.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

```python
# class_patterns.py
from point import Point

def locate(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "The origin"
        case Point(0, y):
            return f"On the y-axis at y={y}"
        case Point(x, 0):
            return f"On the x-axis at x={x}"
        case Point(x, y):
            return f"At ({x}, {y})"

print(locate(Point(0, 0)))
#: The origin
print(locate(Point(0, 5)))
#: On the y-axis at y=5
print(locate(Point(3, 0)))
#: On the x-axis at x=3
print(locate(Point(3, 4)))
#: At (3, 4)
```

`Point(0, 0)` matches a point whose fields are both zero.
`Point(0, y)` matches when `x` is zero and captures `y`.
The literal and the capture combine in one pattern.

Positional matching depends on `__match_args__`,
a class attribute listing field names in order.
`@dataclass` generates it automatically from the field order,
so `Point(0, y)` means "position 0 is `x`, position 1 is `y`."
`NamedTuple` generates it too; an ordinary class must assign it by hand.
Without a `__match_args__` long enough to cover the positions you supply,
a positional pattern raises a `TypeError`.

Keyword patterns work differently.
`Point(x=0, y=y)` matches by attribute name directly, through attribute access,
not through `__match_args__`.
They also work on any object with the named attributes, dataclass or not,
and let you match a subset of attributes while ignoring the rest:

```python
# keyword_patterns.py
from point import Point

def describe(p: Point) -> str:
    match p:
        case Point(x=0):
            return "Somewhere on the y-axis"
        case Point(y=0):
            return "Somewhere on the x-axis"
        case Point(x=x, y=y) if x == y:
            return f"On the diagonal at {x}"
        case Point():
            return "Just some point"

print(describe(Point(0, 5)))
#: Somewhere on the y-axis
print(describe(Point(3, 0)))
#: Somewhere on the x-axis
print(describe(Point(2, 2)))
#: On the diagonal at 2
print(describe(Point(3, 4)))
#: Just some point
```

The `if x == y` on the third case is a *guard*, covered in the next section.

`Point(x=0)` matches any point whose `x` attribute is zero, ignoring `y`.
A positional pattern can leave fields unchecked too:
`Point(0)` supplies fewer sub-patterns than `__match_args__` names,
so it ignores `y`, and `Point(_, 0)` uses the wildcard to skip `x`.
Naming the attribute is clearer,
and it survives a change to the field order that would silently redefine every position.
`Point()` with no arguments matches any `Point` instance, keyword or positional,
and works as a type-only check or a final catch-all.

The type test is `isinstance()`, which has consequences worth knowing:

```python
# type_patterns.py

def describe(value: object) -> str:
    match value:
        case bool(b):
            return f"bool {b}"
        case int(n):
            return f"int {n}"
        case str(s):
            return f"str of length {len(s)}"
        case _:
            return "something else"

print(describe(True))
#: bool True
print(describe(7))
#: int 7
print(describe("hello"))
#: str of length 5
print(describe(3.5))
#: something else
```

A subclass matches its base's pattern,
so the order of the cases decides which one wins.
`bool` is a subclass of `int`,
so moving `case bool(b)` below `case int(n)` makes it unreachable:
`describe(True)` would answer `int True`.

The single positional argument in `int(n)` does not name an attribute.
A handful of builtins
(`bool`, `int`, `float`, `str`, `bytes`, `bytearray`, `list`, `tuple`, `dict`, `set`, `frozenset`)
are special-cased so that one positional sub-pattern binds the whole value,
which is why `case str(s)` reads as "a string, call it `s`."

Matching on `isinstance()` is the opposite of the exact-type dispatch used by a `dict` keyed on `type(value)`,
which [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
relies on.
There a subclass finds no entry at all.

```python
# test_class_patterns.py
import pytest
from class_patterns import locate
from keyword_patterns import describe
from point import Point

@pytest.mark.parametrize("point, expected", [
    (Point(0, 0), "The origin"),
    (Point(3, 0), "On the x-axis at x=3"),
    (Point(3, 4), "At (3, 4)"),
])
def test_class_patterns(point: Point, expected: str) -> None:
    assert locate(point) == expected

@pytest.mark.parametrize("point, expected", [
    (Point(0, 5), "Somewhere on the y-axis"),
    (Point(3, 0), "Somewhere on the x-axis"),
    (Point(2, 2), "On the diagonal at 2"),
    (Point(3, 4), "Just some point"),
])
def test_keyword_patterns(point: Point, expected: str) -> None:
    assert describe(point) == expected
```

## Guards

A guard is an `if` attached to a `case`.
The case matches only when the pattern fits and the guard is true:

```python
# guards.py
from point import Point

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "Origin"
        case Point(x, y) if x > 0 and y > 0:
            return "First quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "Second quadrant"
        case _:
            return "Somewhere else"

print(quadrant(Point(0, 0)))
#: Origin
print(quadrant(Point(3, 4)))
#: First quadrant
print(quadrant(Point(-3, 4)))
#: Second quadrant
print(quadrant(Point(-1, -1)))
#: Somewhere else
```

The guard runs only after the pattern matches,
which is what lets it use the names the pattern bound.
A false guard moves on to the next `case`, but the names stay bound:
once `case Point(x, y) if x > 0 and y > 0` has failed,
`x` and `y` still hold the values it captured.
A pattern tests shape and equality and nothing else,
so everything beyond that belongs in the guard: an ordering test like `x > 0`,
a relation between two captures like `x == y`, or any call,
such as `len(items) > 3`.
A guard that only compares one capture to a constant is a literal pattern written the long way.

## Mapping Patterns

A mapping pattern matches keys in a dictionary and binds their values.
It ignores keys you do not mention,
which makes it a clean way to dispatch on JSON-shaped data.
That also makes `case {}` a catch-all for any mapping rather than a test for an empty one,
the opposite of `case []`, which matches only an empty sequence.
Test for an empty dictionary with a guard, `case {} if not event:`.
A `**rest` at the end binds whatever keys the pattern did not mention,
the mapping counterpart of `*rest` in a sequence pattern.

```python
# mapping_patterns.py

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"Key {key}"
        case {"type": kind}:
            return f"Other event: {kind}"
        case nonevent:
            return f"Not an event: {nonevent}"

print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
print(handle({"type": "scroll", "delta": 3}))
#: Other event: scroll
print(handle({"button": 1}))
#: Not an event: {'button': 1}
```

Testing verifies a matched event and the fall-through:

```python
# test_mapping_patterns.py
from mapping_patterns import handle

def test_mapping_patterns() -> None:
    assert handle({"type": "key", "key": "Esc"}) == "Key Esc"
    assert handle({"nope": 1}) == "Not an event: {'nope': 1}"
```

## Patterns Nest

Everything so far has been one pattern at a time.
A sub-pattern is itself a pattern,
so any of these forms can sit inside any other:

```python
# nested_patterns.py
from point import Point

def survey(points: list[Point]) -> str:
    match points:
        case [Point(0, 0) as start, *rest]:
            return f"{start} then {len(rest)} more"
        case [Point(0, n) | Point(n, 0)]:
            return f"one axis point, offset {n}"
        case [Point(), Point()]:
            return "two points, neither at an axis"
        case _:
            return "nothing to say"

print(survey([Point(0, 0), Point(1, 1), Point(2, 2)]))
#: Point(x=0, y=0) then 2 more
print(survey([Point(0, 5)]))
#: one axis point, offset 5
print(survey([Point(4, 0)]))
#: one axis point, offset 4
print(survey([Point(1, 2), Point(3, 4)]))
#: two points, neither at an axis
```

The first case is a sequence pattern holding a class pattern holding two literals,
with a starred capture beside it.
`as` binds whatever its sub-pattern matched,
so `start` is the whole `Point` while `0, 0` checks its fields.
Without `as` you would have to choose between testing the shape and keeping the object.

The second case alternates two class patterns and binds `n` from either.
Every branch of a `|` must bind the same set of names,
which the compiler enforces: adding a third alternative `| Point(1, 1)`,
which binds nothing,
fails with `SyntaxError: alternative patterns bind different names`.

## Exhaustive Matching

When a value is one of a fixed set of types,
define that set as a union using the [`type` statement](08_Static_Typing.md#the-type-statement).
Now you can `match` on that union.
When you end with `case _: assert_never(value)`,
the type checker will ensure the match is *exhaustive*.
Adding a type to the union and forgetting its `case` produces a type error.
The type checker reports it before the program runs,
instead of the value falling through at runtime.
That is the benefit of static typing applied to control flow:

```python
# exhaustive.py
from dataclasses import dataclass
from math import pi
from typing import assert_never

@dataclass(frozen=True)
class Circle:
    radius: float

@dataclass(frozen=True)
class Square:
    side: float

type Shape = Circle | Square

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius):
            return pi * radius ** 2
        case Square(side):
            return side ** 2
        case _:
            assert_never(shape)

print(round(area(Circle(1.0)), 4))
#: 3.1416
print(area(Square(2.0)))
#: 4.0
```

If you add a `Triangle` to `Shape` without adding the appropriate `case`,
the checker flags `assert_never(shape)`.

A `switch` in C, JavaScript, or traditional Java cannot do this.
Nothing forces you to add a case, and an unhandled value falls through silently.
Scala's `match`, Kotlin's `when`,
and Java's newer switch expressions do check this,
as long as the matched type is a sealed hierarchy the compiler can see in full.

Python has no `sealed` keyword.
`assert_never()` plus a type checker fills that role instead.
An `if`/`isinstance()` chain can also get there,
but only if you remember to end it with `assert_never()`.
A `match` makes the shape of the dispatch explicit.

This reframes the classic OOP "shapes" example as a closed type union instead of a class hierarchy.
[Dynamic Binding vs. Pattern Matching](#dynamic-binding-vs.-pattern-matching)
compares the two approaches directly.

```python
# test_exhaustive.py
from exhaustive import Circle, Square, area

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0
```

## When Not to Match

For a value-to-value lookup, a dictionary is shorter:

```python
# value_to_value_lookup.py
from typing import Final

STATUS: Final[dict[int, str]] = {
    200: "OK", 404: "Not Found", 500: "Server Error"}

def describe(status: int) -> str:
    return STATUS.get(status, f"Status {status}")

print(describe(200))
#: OK
print(describe(301))
#: Status 301
```

A literal `match` compiles to a chain of comparisons, one per `case`,
so its cost grows with the number of cases while a dictionary lookup's does not.
At three entries the difference does not matter;
the dictionary wins as the table grows,
and it is the only one of the two you can build or change at runtime.

When the set of types is *open* (anyone can add a new one),
inheritance and dynamic binding work better than `match`.
Each type carries its own behavior,
so adding a type needs no change to a central `match`.
Use `match` when the set of cases is closed and you want to handle them in one place,
especially when the cases need to look inside the value.
When that closed set is a set of constants rather than a set of shapes,
make it an `Enum` and `match` on its members, as `value_patterns.py` did.
The enum hands the checker the closed set for free,
so `assert_never()` works without a `type` union.

## Dynamic Binding vs. Pattern Matching

An alerting system sends a notification through one of three channels: email,
SMS, or push.
Every channel renders the notification into a message string for a recipient.
Every channel also has a rough cost to send a message.

The inheritance answer declares both operations as abstract methods on a base class.
Each channel is a subclass that implements them,
and dynamic binding picks the correct implementation at each call:

```python
# notifications_oo.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Notification(ABC):
    @abstractmethod
    def render(self, recipient: str) -> str: ...

    @abstractmethod
    def cost(self) -> float: ...

@dataclass(frozen=True)
class Email(Notification):
    subject: str

    @override
    def render(self, recipient: str) -> str:
        return f"Email to {recipient}: {self.subject}"

    @override
    def cost(self) -> float:
        return 0.001

@dataclass(frozen=True)
class Sms(Notification):
    body: str

    @override
    def render(self, recipient: str) -> str:
        return f"SMS to {recipient}: {self.body}"

    @override
    def cost(self) -> float:
        return 0.02

@dataclass(frozen=True)
class Push(Notification):
    title: str

    @override
    def render(self, recipient: str) -> str:
        return f"Push to {recipient}: {self.title}"

    @override
    def cost(self) -> float:
        return 0.0005

email = Email("Invoice ready")
sms = Sms("Code: 5821")
push = Push("New message")

print(email.render("Dana"))
#: Email to Dana: Invoice ready
print(sms.render("Dana"))
#: SMS to Dana: Code: 5821
print(push.render("Dana"))
#: Push to Dana: New message
print(round(email.cost() + sms.cost() + push.cost(), 4))
#: 0.0215
```

`Notification` names the shape every channel must have.
`@abstractmethod` forces `Email`, `Sms`,
and `Push` to define both `render()` and `cost()`.
If you forget one, the class stays abstract, so you cannot instantiate it.

A type union with `match` takes the opposite shape.
The channels become plain data,
and each operation is a free function that inspects the type:

```python
# notifications_match.py
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Email:
    subject: str

@dataclass(frozen=True)
class Sms:
    body: str

@dataclass(frozen=True)
class Push:
    title: str

type Notification = Email | Sms | Push

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Sms(body):
            return f"SMS to {recipient}: {body}"
        case Push(title):
            return f"Push to {recipient}: {title}"
        case _:
            assert_never(note)

def cost(note: Notification) -> float:
    match note:
        case Email():
            return 0.001
        case Sms():
            return 0.02
        case Push():
            return 0.0005
        case _:
            assert_never(note)

email = Email("Invoice ready")
sms = Sms("Code: 5821")
push = Push("New message")

print(render(email, "Dana"))
#: Email to Dana: Invoice ready
print(render(sms, "Dana"))
#: SMS to Dana: Code: 5821
print(render(push, "Dana"))
#: Push to Dana: New message
print(round(cost(email) + cost(sms) + cost(push), 4))
#: 0.0215
```

`render()` and `cost()` each `match` over `Notification` and end with `assert_never()`,
so the type checker confirms every case is handled.

```python
# test_notifications.py
import notifications_match as nm
import notifications_oo as no

def test_oo_and_match_agree() -> None:
    assert (no.Email("Hi").render("Dana")
            == nm.render(nm.Email("Hi"), "Dana"))
    assert no.Sms("Hi").cost() == nm.cost(nm.Sms("Hi"))
```

Try growing the system in each direction.
First, add a new type: a `Webhook` channel.
In the object version,
you write one new subclass with its own `render()` and `cost()`,
and nothing else changes.
In the match version, you add a `Webhook` dataclass to the `Notification` union,
and the type checker flags `assert_never()` in both `render()` and `cost()` until you add a `case Webhook(...)` to each.

Now try adding a new operation, `priority()`, that ranks channels by urgency.
In the object version, every existing subclass needs a new method.
In the match version, you write one new function with its own `match`,
and the existing classes and functions stay untouched.

Adding a type is cheaper with inheritance.
Adding an operation is cheaper with pattern matching.
That is the open-set-versus-closed-set tradeoff from [When Not to Match](#when-not-to-match),
worked out concretely.
It is also called the *expression problem*.
[Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance)
works through the same split with shapes,
and [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
and [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch)
explore it further.

## Exercises

1.  Write `classify(value)` that uses `match` to return `"empty list"`,
    `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
    and `"other"` for anything else.
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union without adding its `case`.
    Run `ty` and read the error it reports at `assert_never`.
3.  Rewrite `mapping_patterns.handle()` to also accept a nested shape,
    such as `{"type": "click", "at": {"x": x, "y": y}}`,
    binding `x` and `y` from the inner dictionary.
4.  Add a `Webhook` channel to `notifications_match.py`:
    a dataclass with a `url` field, added to the `Notification` union.
    Run `ty` before adding its `case` to `render()` and `cost()`,
    and read the errors.
    Then add both cases and confirm `ty` passes.
5.  Rewrite `guards.py`'s `quadrant()` so the third and fourth quadrants are handled too.
    Then write it a second time with one `case` per sign combination,
    using `|` alternations and no guards, and say which version reads better.
