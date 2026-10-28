# Pattern Matching

> Sometimes the shape of a value matters as much as its contents.
> `match` tests the shape, takes the value apart,
> and binds the parts in one statement.

The `match` statement compares a value, its *subject*,
against a series of *patterns* and runs the body of the first `case` whose pattern fits.
No C-style `switch` can express this case:

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        ...
```

That case matches only a mapping whose `"type"` is `"click"`,
and it binds `x` and `y` from that mapping as it matches.
`match` becomes valuable when the patterns do more than test equality.

Pattern matching first appears in [Control Flow](04_Foundations--Control_Flow.md#pattern-matching).

`match` and `case` are *soft keywords*:
they act as keywords only inside this statement,
so existing code that uses `match` as a variable name still runs.
Avoid naming a new variable `match`.
The name shadows no keyword, but it reads like the statement.

## Matching Values

The simplest patterns are literal values.
A `case _` at the end is the wildcard.
It matches anything, like a default.
Without one, the `match` skips every body silently when the value fits no pattern.

`match` tries the patterns top to bottom and ends after the first matching `case` body runs.
Cases do not fall through as they do in C's `switch`,
and `match` has no `break` to forget:

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
        case _:
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
`None`, `True`, and `False` compare with `is`,
so `case True:` does not match `1`.

For a value-to-value lookup like this,
a [dictionary is often shorter](#when-not-to-match).

## Alternatives and Capture

`|` joins several patterns in one `case`.
The case matches when any one of them fits.
Inside a pattern, `|` takes the place of `or`.
Writing `case "up" or "u":`, as you would in an `if` condition,
fails with a bare `SyntaxError: invalid syntax`.

A bare name is a *capture pattern*.
Like `_`, it matches any value unconditionally.
Unlike `_`, it also binds the matched value to that name.
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

The alternatives in `step()` are literals,
which compare the subject with a value.
When alternatives do capture, each one must bind the same set of names,
so the body can use those names whichever alternative matched.

## A Bare Name Captures, a Dotted Name Compares

A bare name always binds.
It ignores any variable of that name,
so a named constant in a `case` silently captures instead.
A *value pattern* is a dotted name, and it does compare.
`Signal` is an [`Enum`](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too):

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

print(act(Signal.GO), act(Signal.STOP))
#: accelerate brake
print(broken(Signal.GO))
#: DEFAULT is now Signal.GO
print(DEFAULT)
#: Signal.STOP
```

`case Signal.GO` compares.
`case DEFAULT` binds.
It matches `Signal.GO`,
binds that member to a local name `DEFAULT` inside `broken()`,
and leaves the module-level constant untouched.

When a later `case` follows a capture pattern,
Python refuses to compile the `match` and reports `SyntaxError: name capture 'DEFAULT' makes remaining patterns unreachable`.
When the capture is the last `case`, as here,
Python compiles the `match` silently, and the type checker accepts it.
The checker treats the capture as matching every value,
so it sees every path through `broken()` ending at the `return`.
`ruff` flags the line only when you enable its pep8-naming rules.
Then N806 reports `DEFAULT` as an uppercase variable inside a function.
That message is about naming style rather than the capture,
so `ruff` accepts the same capture when the constant has a lowercase name.
This book's `ruff` configuration turns N806 off for `value_patterns.py`,
since the capture is the mistake the listing exists to show.

`act()` also shows what an enum gives the type checker.
`Signal` is a closed set,
so the type checker verifies that the cases cover both members and accepts the function with no trailing `return`.

## Sequence Patterns

A sequence pattern matches the shape of a list or tuple and binds the elements by position.
A starred name, as in `*middle`, captures the elements the other names leave:

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
        case [first, *middle, last]:
            return (f"{first} to {last}, "
                    f"{len(middle)} between")
        case _:  # [1]
            return "Unreachable"

print(summarize([]))
#: Empty
print(summarize([5]))
#: One item: 5
print(summarize([3, 4]))
#: Two items: 3, 4
print(summarize([1, 2, 3, 4]))
#: 1 to 4, 2 between
```

`summarize()` shows the structural part of "structural pattern matching."
The pattern `[first, second]` matches only a two-element sequence and binds both elements in one step.

The `case _` at `[1]` is unreachable.
`[first, *middle, last]` matches every list of two or more elements,
`[only]` the one-element list, and `[]` the empty one.
The type checker cannot prove that,
so the wildcard stays to satisfy the declared return type.

A starred name can appear anywhere in a sequence pattern,
as long as the pattern has at most one.
`[*init, last]` puts it first and binds every element but the last to `init`.

A sequence pattern deliberately excludes `str`, `bytes`, and `bytearray`.
`case [a, b, c]` does not match `"abc"`,
although a string is a sequence in every other context.
You rarely want a pattern to take a string apart character by character,
so the language rules that out.

A tuple does match.
`case [a, b, c]` accepts `(1, 2, 3)` as readily as `[1, 2, 3]`,
because the pattern describes a shape, not a concrete type.
The subject must be a sequence, though.
`case [a, b]` matches a two-element `range`, but for a generator or a `set`,
`match` moves on to the next `case`.

Parentheses group a pattern rather than build a tuple.
`case (x)` is `case x`, an unconditional capture,
and `case (x,)` is a one-element sequence pattern.
The brackets are optional in a sequence pattern,
so `case 0, 0:` and `case [0, 0]:` are the same pattern.

The subject can be any expression, and a comma builds a tuple there too.
Given a `sign()` helper that returns `-1`, `0`, or `1`,
`match sign(x), sign(y):` matches on a pair computed inline.
Transforming the subject this way turns a set of comparisons into literal patterns.
A `case 1, -1:` then replaces the [guard](#guards) `if x > 0 and y < 0`.

## Class Patterns

A class pattern matches by type and extracts attributes.
With a data class you can match positionally or by keyword:

```python
# point.py
from dataclasses import dataclass

@dataclass(frozen=True)
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

A class pattern looks like a constructor call,
but it tests the subject's type and reads its attributes.

Positional matching depends on `__match_args__`,
a class attribute listing field names in order.
`@dataclass` generates it from the field order,
so `Point(0, y)` means "position 0 is `x`, position 1 is `y`."
`NamedTuple` generates it too.
An ordinary class assigns `__match_args__` in its body.
When `__match_args__` is too short to name every position you supply,
a positional pattern raises a `TypeError`.
For an ordinary class `R` that lacks `__match_args__`,
`case R(1)` reports `TypeError: R() accepts 0 positional sub-patterns (1 given)`.

### Keyword Patterns

A keyword pattern such as `Point(x=0, y=y)` matches by attribute name.
It reads each named attribute, so it works with any class,
whether or not the class defines `__match_args__`.
It also lets you match a subset of attributes while ignoring the rest:

```python
# keyword_patterns.py
from point import Point

def describe(p: Point) -> str:
    match p:
        case Point(x=0):
            return "Somewhere on the y-axis"
        case Point(y=0):
            return "Somewhere on the x-axis"
        case Point():
            return "Just some point"

print(describe(Point(0, 5)))
#: Somewhere on the y-axis
print(describe(Point(3, 0)))
#: Somewhere on the x-axis
print(describe(Point(3, 4)))
#: Just some point
```

A positional pattern can also check a subset of fields.
`Point(0)` supplies one sub-pattern, which goes to `x`,
the first name in `__match_args__`.
`Point(_, 0)` puts the wildcard in `x`'s position to check `y` alone.
Naming the attribute is clearer.
A keyword pattern matches the same attribute whatever the field order.
Reordering the fields rewrites `__match_args__`,
so every positional pattern silently starts matching a different field.

`Point()`, with empty parentheses, matches any `Point` instance.
Use it as a type-only check or a final catch-all.

### Built-in Types and Subclasses {#builtin-types-and-subclasses}

The type test is `isinstance()`, so a subclass matches its base's pattern:

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

Because a subclass matches, the order of the cases decides which body runs.
`bool` is a subclass of `int`,
so moving `case bool(b)` below `case int(n)` makes the `bool` case unreachable.
`describe(True)` then returns `int True`.

In `int(n)`, the positional sub-pattern binds the whole value rather than an attribute.
Python special-cases a handful of built-ins this way,
so `case str(s)` reads as "a string, call it `s`."
The full set is `bool`, `int`, `float`, `str`, `bytes`, `bytearray`, `list`,
`tuple`, `dict`, `frozendict`, `set`, and `frozenset`.

Dropping the parentheses changes the meaning.
`case str:` is a capture pattern, not a type test,
matching any value and binding it to a local named `str`.
`case str:` repeats the `DEFAULT` mistake from `value_patterns.py`.
Python rejects it the same way,
refusing to compile the `match` when another `case` follows:
`SyntaxError: name capture 'str' makes remaining patterns unreachable`.

Matching on `isinstance()` differs from the exact-type dispatch of a `dict` keyed on `type(value)`,
where a subclass needs an entry of its own.
[*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
relies on that exact-type dispatch.

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

def leaky(p: Point) -> int:
    match p:
        case Point(x, _) if x > 100:
            return 0
        case _:
            return x

print(quadrant(Point(0, 0)))
#: Origin
print(quadrant(Point(3, 4)))
#: First quadrant
print(quadrant(Point(-3, 4)))
#: Second quadrant
print(quadrant(Point(-1, -1)))
#: Somewhere else
print(leaky(Point(3, 4)))
#: 3
```

The guard runs after the pattern matches,
so it can use the names the pattern bound.
When a guard is false, `match` tries the next `case`, but the names stay bound.
Once `case Point(x, y) if x > 0 and y > 0` has failed,
`x` and `y` still hold the values it captured.
In `leaky()`, the `x` that `case _:` returns holds `3`,
left over from the failed guard in the case above it.
Any name a later case leaves alone keeps the value an earlier,
failed case bound.

A failed guard always leaves its bindings,
because the pattern matched and made them before the guard ran.
For a pattern that fails partway,
the language reference lets each implementation decide whether the captures made before the failure stay bound.
Use a captured name only in the `case` that captured it.

A pattern tests shape and equality,
so everything beyond that belongs in the guard: an ordering test like `x > 0`,
a relation between two captures like `x == y`,
or any call like `len(items) > 3`.
A repeated name is an error rather than an equality test.
`case [x, x]:` fails with `SyntaxError: multiple assignments to name 'x' in pattern`,
so an equal-elements test is also a guard, `case [x, y] if x == y:`.

A guard that compares one capture to a constant is a literal pattern written the long way.
The exception is a constant with a bare name,
such as `DEFAULT` in `value_patterns.py`.
A bare name in a pattern captures, so a `case` tests for it with a guard,
`case s if s == DEFAULT:`.

## Mapping Patterns

A mapping pattern matches keys in a dictionary and binds their values.
It checks the keys you specify and ignores the rest,
so it matches a JSON-shaped record that carries extra fields.
Ignoring the extra keys also makes `case {}` a catch-all for any mapping rather than a test for an empty one.
`case []` works the opposite way and matches only an empty sequence.
Test for an empty dictionary with a guard, `case {} if not event:`.

A `**rest` at the end binds the remaining key-value pairs as a `dict`,
the mapping counterpart of a starred name in a sequence pattern.
The `{"type": kind, **rest}` case in `handle()` reports those leftover pairs:

```python
# mapping_patterns.py

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"Key {key}"
        case {"type": kind, **rest}:
            return f"Other event: {kind} {rest}"
        case unknown:
            return f"Unrecognized event: {unknown}"

print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
print(handle({"type": "scroll", "delta": 3}))
#: Other event: scroll {'delta': 3}
print(handle({"button": 1}))
#: Unrecognized event: {'button': 1}
```

A `TypedDict` declares a value type for each key.
Here `handle()` takes a union of two `TypedDict` classes,
each with a `Literal` value for its `"type"` key:

```python
# typed_events.py
from typing import Literal, TypedDict

class Click(TypedDict):
    type: Literal["click"]
    x: int
    y: int

class Key(TypedDict):
    type: Literal["key"]
    key: str

type Event = Click | Key

def handle(event: Event) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y}), sum {x + y}"
        case {"type": "key", "key": key}:
            return f"Key {key.upper()}"
        case _:
            return "Unrecognized event"

print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20), sum 30
print(handle({"type": "key", "key": "Enter"}))
#: Key ENTER
```

`mapping_patterns.py` loses type information through its annotation,
not its patterns.
Its parameter is `event: dict[str, object]`,
so each binding takes the dictionary's one declared value type and comes out typed `object`.
If you add `{x + y}` to its first `case`, `ty` reports `unsupported-operator`,
because `object` defines no `+`.

In `typed_events.py` the `Literal` value of `"type"` does the narrowing.
The pattern `{"type": "click", ...}` matches that key against `"click"`,
a value `Click` alone can hold,
so the type checker narrows `Event` to `Click` and binds `x` and `y` as `int`.
The pattern `{"type": "key", ...}` narrows to `Key` the same way,
which makes `key` a `str` with an `upper()` method.

At runtime a `TypedDict` instance is a `dict`, so the event stays a dictionary.
That suits an event that arrives as JSON,
since `json.loads()` returns a `dict` that `handle()` matches directly.
The type checker enforces the declared keys and types;
at runtime `handle()` accepts any `dict`.
[Typing `**kwargs` with a `TypedDict`](08_Foundations--Static_Types.md#typed-kwargs)
introduces the construct.

[Which Should You Use?](28_Patterns--Data_Transfer_Objects.md#which-should-you-use)
describes when a `TypedDict` fits better than a data class.
For pattern matching,
the choice depends on what the program does with the data next.
`class_patterns.py`'s `Point(x, y)` binds `x` and `y` as `int`,
because `Point` declares its fields that way.
When the program must validate the data or goes on to compute with it,
parse it into a data class first, then match on the data class.
You keep the shape test and gain the field types.
When the data must stay a dict, a `TypedDict` gives the bindings their types.

## Patterns Nest

A sub-pattern is a pattern, so any kind of pattern can appear inside any other:

```python
# nested_patterns.py
from point import Point

def survey(points: list[Point]) -> str:
    match points:
        case [Point(0, 0) as start, *rest]:  # [1]
            return f"{start} then {len(rest)} more"
        case [Point(0, n) | Point(n, 0)]:  # [2]
            return f"one axis point, offset {n}"
        case [Point(), Point()]:
            return "two points"
        case _:
            return "nothing to say"

print(survey([Point(0, 0), Point(1, 1), Point(2, 2)]))
#: Point(x=0, y=0) then 2 more
print(survey([Point(0, 5)]))
#: one axis point, offset 5
print(survey([Point(4, 0)]))
#: one axis point, offset 4
print(survey([Point(1, 2), Point(3, 4)]))
#: two points
```

The case at `[1]` is a sequence pattern holding a class pattern holding two literals,
with a starred name beside the class pattern.
`as` binds the value its sub-pattern matched,
so `start` is the whole `Point` while `0, 0` checks its fields.
With `as`, one pattern both tests the shape and keeps the object.

The case at `[2]` is a one-element sequence pattern whose element alternates two class patterns.
Either alternative binds `n`.
The compiler enforces the [same-names rule](#alternatives-and-capture).
Adding a third alternative of literals alone, `| Point(1, 1)`,
fails with `SyntaxError: alternative patterns bind different names`.

Nesting has a set depth, the depth you write into the pattern.
A self-referential type such as a tree needs recursion:
a function whose `match` takes one level apart and calls the function again on the parts.
[*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md#evaluation-is-a-tree-walk)
walks an expression tree this way.
Each `case` matches one node type,
and its body recurses into that node's children.

## Exhaustive Matching

When a value is one of a known set of types,
define that set as a union using the [`type` statement](08_Foundations--Static_Types.md#the-type-statement).
Then `match` on that union.
When you end with `case _: assert_never(value)`,
the type checker ensures the match is *exhaustive*.
If you add a type to the union without its `case`,
the type checker reports an error at `assert_never()`.
That report comes before the program runs,
instead of as an `AssertionError` when the unhandled value arrives at runtime.

```python
# exhaustive.py
from dataclasses import dataclass
from math import pi
from typing import assert_never
from exceptions import expect

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
expect(AssertionError, area, "x")  # type: ignore
#: [AssertionError] Expected code to be unreachable, but
#: got: 'x'
```

`assert_never()` acts at runtime as well as at check time.
The string `"x"` is no `Shape`,
so the `expect()` line carries `# type: ignore` to get past the type checker.

`act()` in `value_patterns.py` gets its coverage check from the return type instead of from `assert_never()`.
If one `Signal` member lacked a `case`,
`act()` could reach its end and return `None`,
which breaks its `-> str` annotation.
In a function that returns `None`, reaching the end matches the declared type,
so the type checker accepts a missing `case` there.
`assert_never()` catches a missing `case` whatever the function returns.
It also reports the error inside the `match`, at the `assert_never()` call,
instead of at the function's return type.

A `switch` in C, JavaScript,
or traditional Java silently skips any value outside its cases.
Scala's `match`, Kotlin's `when`,
and Java's newer switch expressions check exhaustiveness,
as an error in Java and Kotlin and a warning in Scala.
The compiler can prove the cases complete without a default branch only when the declaration of the matched type lists every member:
a sealed hierarchy or an enum.

The Scala, Kotlin, and Java versions are also expressions,
producing a value you can assign.
Python's `match` is a statement, not an expression,
so a `match` that must produce a value goes inside a function that returns from each `case`.

Python has no `sealed` keyword.
`assert_never()` plus the type checker fills that role.

An `if`/`isinstance()` chain that ends with `assert_never()` gives the same exhaustiveness check,
but a `match` names the subject once and binds fields as it tests the type.
`case Circle(radius)` in `area()` tests the type and binds `radius` in one pattern,
where the chain tests `isinstance(shape, Circle)` and then reads `shape.radius`.

`Shape` turns the classic OOP "shapes" example into a closed type union instead of a class hierarchy.

`test_area_of_each_shape()` checks the area of one `Circle` and one `Square`,
so every member of the `Shape` union reaches its own `case`:

```python
# test_exhaustive.py
from exhaustive import Circle, Square, area

def test_area_of_each_shape() -> None:
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
    return STATUS.get(status) or f"Status {status}"

print(describe(200))
#: OK
print(describe(301))
#: Status 301
```

The `or` treats a falsy value from the table like the `None` of a missing key,
but every value in `STATUS` is a nonempty string.

A literal `match` compiles to a chain of comparisons, one per `case`,
so its running time grows with the number of cases.
A dictionary lookup takes about the same time at any size.
At three entries the difference is too small to matter,
but the dictionary is faster as the table grows.
You can also build or change a dictionary at runtime,
while a `match` stays as written.

When the set of types is *open* (anyone can add a new one),
inheritance and dynamic binding work better than `match`.
Each type defines its own methods, so adding a type touches only the new class.
Use `match` for a closed set of cases you want to handle in one place,
especially when the cases test the value's attributes or elements.

When a closed set holds constants rather than shapes,
make it an `Enum` and `match` on its members, as `value_patterns.py` does.
The enum declares the closed set for the type checker,
so `assert_never()` works without a `type` union.

## Dynamic Binding vs. Pattern Matching {#dynamic-binding-vs-pattern-matching}

An alerting system sends a notification through one of three channels: email,
SMS, or push.
Every channel renders the notification into a message string for a recipient.
Every channel also has a rough cost to send a message.

### The Inheritance Version

The inheritance answer declares both operations as abstract methods on an [abstract base class](20_Patterns--Rethinking_Objects.md#abstract-base-classes).
Each channel is a subclass that implements them,
and dynamic binding runs the method of the object's own class at each call:

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

notes: list[Notification] = [
    Email("Invoice ready"), Sms("Code: 5821"),
    Push("New message")]

for note in notes:
    print(note.render("Dana"))
#: Email to Dana: Invoice ready
#: SMS to Dana: Code: 5821
#: Push to Dana: New message
print(round(sum(n.cost() for n in notes), 4))
#: 0.0215
```

`Notification` describes the shape every channel must have.
`@abstractmethod` forces `Email`, `Sms`,
and `Push` to define both `render()` and `cost()`.
If a subclass leaves out either method, that subclass stays abstract.
Instantiating it raises a `TypeError`.

### The `match` Version

A type union with `match` takes the opposite shape from the class hierarchy.
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

notes: list[Notification] = [
    Email("Invoice ready"), Sms("Code: 5821"),
    Push("New message")]

for note in notes:
    print(render(note, "Dana"))
#: Email to Dana: Invoice ready
#: SMS to Dana: Code: 5821
#: Push to Dana: New message
print(round(sum(cost(n) for n in notes), 4))
#: 0.0215
```

`render()` and `cost()` each `match` over `Notification` and end with `assert_never()`,
so the type checker confirms each `match` handles every member of `Notification`.

`test_oo_and_match_agree()` confirms that `render()` and `cost()` return equal values in the two versions for each channel:

```python
# test_notifications.py
import notifications_match as nm
import notifications_oo as no
import pytest

@pytest.mark.parametrize("oo, data", [
    (no.Email("Hi"), nm.Email("Hi")),
    (no.Sms("Hi"), nm.Sms("Hi")),
    (no.Push("Hi"), nm.Push("Hi")),
])
def test_oo_and_match_agree(
    oo: no.Notification, data: nm.Notification
) -> None:
    assert oo.render("Dana") == nm.render(data, "Dana")
    assert oo.cost() == nm.cost(data)
```

### The Expression Problem

Try growing the system in each direction.
First, add a new type: a `Webhook` channel.
In the inheritance version,
you write one new subclass with its own `render()` and `cost()`.
The rest of the program stays as it was.
In the match version,
you add a `Webhook` data class to the `Notification` union.
The type checker then reports an error at `assert_never()` in both `render()` and `cost()`.
Each function needs a `Webhook` case to pass:
`case Webhook(url):` in `render()` and `case Webhook():` in `cost()`.

Second, add a new operation: `priority()`, which ranks channels by urgency.
In the inheritance version, every existing subclass needs a new method.
In the match version, you write one new function with its own `match`.
The existing classes and functions stay untouched.

Inheritance confines a new type to one new subclass.
Pattern matching confines a new operation to one new function.
A new operation touches every existing subclass,
and a new type touches every existing `match`.
[When Not to Match](#when-not-to-match)
weighs an open set of types against a closed one,
and the two notification versions show that tradeoff in code.
The tradeoff has a name: the *expression problem*.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
works through the same tradeoff with shapes,
and [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-type-or-many)
and [*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
explore it further.

## Exercises

Try each exercise before opening its [solution](../Solutions/13_Techniques--Pattern_Matching/).

1.  Write `classify(value)` that uses `match` to return `"empty list"`,
    `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
    and `"other"` for anything else.
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union without adding its `case`.
    Run `ty` and read the error it reports at `assert_never()`.
3.  Rewrite `mapping_patterns.handle()` to also accept a nested shape,
    such as `{"type": "click", "at": {"x": x, "y": y}}`,
    binding `x` and `y` from the inner dictionary.
4.  Add a `Webhook` channel to `notifications_match.py`:
    a data class with a `url` field, added to the `Notification` union.
    Run `ty` before adding its `case` to `render()` and `cost()`,
    and read the errors.
    Then add both cases and confirm `ty` passes.
5.  Rewrite `guards.py`'s `quadrant()` so it handles the third and fourth quadrants too.
    Then write it a second time matching on `sign(p.x), sign(p.y)`,
    with one `case` per quadrant, a `|` alternation for the axes, and no guards,
    and say which version reads better.
6.  Give `value_patterns.py`'s `Signal` a third member,
    and write `act()` so that it compares against a module-level `FALLBACK: Final[Signal]`.
    Run it and confirm that the constant captures instead of comparing.
    Then fix `act()` two ways, with a value pattern and with a guard.
