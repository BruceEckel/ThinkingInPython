# Pattern Matching

The `match` statement compares a value against a series of *patterns* and runs the first one that fits.
A `match` is far more than a `switch` because a pattern can test a value's shape,
look inside it, and pull out the parts you need, all in one step.

Pattern matching was briefly introduced in [Control Flow](04_Control_Flow.md#pattern-matching).

## Matching Values

The simplest patterns are literal values.
A `case _` at the end is the wildcard.
It matches anything, like a default.
Each `case` body runs only when its pattern matches, and the first match wins:

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

For a value-to-value lookup like this, a dictionary is often shorter
(see [the end of this chapter](#when-not-to-match)).
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
`Point(0, y)` matches when `x` is zero and *captures* `y`.
The literal and the capture combine in one pattern.

Positional matching depends on `__match_args__`,
a class attribute listing field names in order.
`@dataclass` generates it automatically from the field order,
so `Point(0, y)` means "position 0 is `x`, position 1 is `y`."
Without a `__match_args__` long enough to cover the positions you supply,
a positional pattern raises a `TypeError`.

Keyword patterns work differently.
`Point(x=0, y=y)` matches by attribute name directly, through attribute access,
not through `__match_args__`.
Keyword patterns work on any object with the named attributes, dataclass or not,
and they let you match a subset of attributes while ignoring the rest:

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

`Point(x=0)` matches any point whose `x` attribute is zero,
ignoring `y` entirely.
A positional pattern cannot do this:
it must supply a sub-pattern for every position that `__match_args__` defines.
`Point()` with no arguments matches any `Point` instance, keyword or positional,
and works as a type-only check or a final catch-all.

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

## Mapping Patterns

A mapping pattern matches keys in a dictionary and binds their values.
It ignores keys you do not mention,
which makes it a clean way to dispatch on JSON-shaped data:

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

## Exhaustive Matching

When a value is one of a fixed set of types,
define that set as a union using the [`type` statement](08_Static_Typing.md#the-type-statement).
Now you can perform a match on that union.
When you end with `case _: assert_never(value)`,
the type checker will ensure the match is *exhaustive*.
Adding a type to the union and forgeting its `case` produces a type error.
This error is caught during type checking rather than silently falling through.
This is the static-typing payoff applied to control flow:

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

Add a `Triangle` to `Shape` without adding the appropriate `case`,
and the checker flags `assert_never(shape)`.

A `switch` in C, JavaScript, or traditional Java, cannot do this.
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

`match` is not a replacement for everything.

For a value-to-value lookup, a dictionary is shorter and faster:

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

When the set of types is *open* (anyone can add a new one),
inheritance and dynamic binding works better than `match`.
Each type carries its own behavior,
so adding a type needs no change to a central `match`.
Use `match` when the set of cases is closed and you want to handle them in one place,
especially when the cases need to look inside the value.
(Note that `Enum` is also worth considering here.)

## Dynamic Binding vs. Pattern Matching

An alerting system sends a notification through one of three channels: email,
SMS, or push.
Every channel renders the notification into a message string for a recipient.
Every channel also has a rough cost to send a message.

The inheritance answer declares both operations as abstract methods on a base class.
Each channel is a subclass that implements them,
and dynamic binding picks the right implementation at each call:

```python
# notifications_oo.py
from abc import ABC, abstractmethod
from typing import override

class Notification(ABC):
    @abstractmethod
    def render(self, recipient: str) -> str: ...

    @abstractmethod
    def cost(self) -> float: ...

class Email(Notification):
    def __init__(self, subject: str) -> None:
        self.subject = subject

    @override
    def render(self, recipient: str) -> str:
        return f"Email to {recipient}: {self.subject}"

    @override
    def cost(self) -> float:
        return 0.001

class Sms(Notification):
    def __init__(self, body: str) -> None:
        self.body = body

    @override
    def render(self, recipient: str) -> str:
        return f"SMS to {recipient}: {self.body}"

    @override
    def cost(self) -> float:
        return 0.02

class Push(Notification):
    def __init__(self, title: str) -> None:
        self.title = title

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
Forget one and the class stays abstract, so you cannot instantiate it.

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
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union *without* adding its `case`.
    Run `ty` and read the error it reports at `assert_never`.
3.  Rewrite `mapping_patterns.handle()` to also accept a nested shape,
    such as `{"type": "click", "at": {"x": x, "y": y}}`,
    binding `x` and `y` from the inner dictionary.
4.  Add a `Webhook` channel to `notifications_match.py`:
    a dataclass with a `url` field, added to the `Notification` union.
    Run `ty` before adding its `case` to `render()` and `cost()`,
    and read the errors.
    Then add both cases and confirm `ty` passes.
