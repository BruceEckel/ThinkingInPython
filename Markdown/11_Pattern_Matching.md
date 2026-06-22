# Pattern Matching

The `match` statement compares a value against a series of *patterns* and runs the first one that fits.
A `match` is far more than a `switch` because a pattern can test a value's shape,
look inside it, and pull out the parts you need, all in one step.

[Containers and Control Flow](03_Containers_and_Control_Flow.md) gave a taste.
This chapter covers the rest.

## Matching Values

The simplest patterns are literal values.
A `case _` at the end is the wildcard: it matches anything, like a default.
Each `case` body runs only when its pattern matches, and the first match wins:

```python
# http_status.py
# Literal patterns match exact values.

def describe(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:  # Default
            return f"status {status}"

print(describe(200))
print(describe(404))
print(describe(301))
```

The output is:

    OK
    Not Found
    status 301

For a plain value-to-value lookup like this,
a dictionary is often shorter (see the end of the chapter).
`match` earns its keep once the patterns do more than test equality.

## Alternatives and Capture

Combine several patterns in one `case` with `|`.
A bare name is a *capture pattern*:
it always matches and binds the value to that name,
which is the wildcard with a name attached:

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
print(step("d"))
print(step("jump"))
```

The output is:

    y -= 1
    y += 1
    unknown command: jump

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
print(summarize([5]))
print(summarize([3, 4]))
print(summarize([1, 2, 3, 4]))
```

The output is:

    Empty
    One item: 5
    Two items: 3, 4
    1, then 3 more

This shows the structural part of "structural pattern matching".
The pattern `[first, second]` matches only a two-element sequence and pulls both out at once.

## Class Patterns

A class pattern matches by type and extracts attributes.
With a data class you can match positionally,
because `@dataclass` fills in the `__match_args__` the pattern uses,
or by keyword:

```python
# class_patterns.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

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
print(locate(Point(0, 5)))
print(locate(Point(3, 0)))
print(locate(Point(3, 4)))
```

The output is:

    The origin
    On the y-axis at y=5
    On the x-axis at x=3
    At (3, 4)

`Point(0, 0)` matches a point whose fields are both zero.
`Point(0, y)` matches when `x` is zero and *captures* `y`.
The literal and the capture combine in one pattern.

## Guards

A guard is an `if` attached to a `case`.
The case matches only when the pattern fits *and* the guard is true:

```python
# guards.py
# A guard adds a condition to a case.
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "origin"
        case Point(x, y) if x > 0 and y > 0:
            return "first quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "second quadrant"
        case _:
            return "somewhere else"

print(quadrant(Point(0, 0)))
print(quadrant(Point(3, 4)))
print(quadrant(Point(-3, 4)))
print(quadrant(Point(-1, -1)))
```

The output is:

    origin
    first quadrant
    second quadrant
    somewhere else

## Mapping Patterns

A mapping pattern matches keys in a dictionary and binds their values.
Keys you do not mention are ignored,
which makes it a clean way to dispatch on JSON-shaped data:

```python
# mapping_patterns.py
# A mapping pattern matches the keys it names and binds their values.

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"key {key}"
        case {"type": kind}:
            return f"other event: {kind}"
        case _:
            return "not an event"

print(handle({"type": "click", "x": 10, "y": 20}))
print(handle({"type": "key", "key": "Enter"}))
print(handle({"type": "scroll", "delta": 3}))
print(handle({"button": 1}))
```

The output is:

    click at (10, 20)
    key Enter
    other event: scroll
    not an event

## Exhaustive Matching

When a value is one of a fixed set of types,
declare that set as a union with the `type` statement and match on it.
End with `case _: assert_never(value)`.
The type checker then proves the match is *exhaustive*:
if you add a type to the union and forget its case,
it reports the gap before the program runs.
This is the static-typing payoff from the [Static Typing](07_Static_Typing.md) chapter applied to control flow:

```python
# exhaustive.py
# A closed union plus assert_never makes match exhaustive: forgetting
# a case becomes a type error, not a silent fall-through.
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
print(area(Square(2.0)))
```

The output is:

    3.1416
    4.0

Add a `Triangle` to `Shape` and the checker flags `assert_never(shape)`,
because `shape` could now be a `Triangle` that no `case` handles.
A `switch` cannot do this; neither can a chain of `if`/`isinstance`.
The [Rethinking Objects](16_Rethinking_Objects.md) chapter uses exactly this technique to add operations to a closed set of types without inheritance.

## When Not to Match

`match` is not a replacement for everything.

For a plain value-to-value lookup, a dictionary is shorter and faster:

```python
# not_match.py
# A dict is the right tool for a value-to-value lookup; reserve match
# for patterns that destructure.
STATUS = {200: "OK", 404: "Not Found", 500: "Server Error"}

def describe(status: int) -> str:
    return STATUS.get(status, f"status {status}")

print(describe(200))
print(describe(301))
```

The output is:

    OK
    status 301

And when the set of types is *open* (anyone can add a new one),
polymorphism is better than a `match`: each type carries its own behavior,
so adding a type needs no change to a central `match`.
Use `match` when the set of cases is closed and you want to handle them in one place,
especially when the cases need to look inside the value.
(Note that `Enum` is also worth considering here).

## Testing the Matchers

Each matcher is an ordinary function, so a test calls it and checks the result.
The cases worth pinning down are the structural ones and the fall-through:

```python
# test_pattern_matching.py
from class_patterns import Point, locate
from exhaustive import Circle, Square, area
from mapping_patterns import handle
from sequence_patterns import summarize

def test_sequence_patterns() -> None:
    assert summarize([]) == "Empty"
    assert summarize([5]) == "One item: 5"
    assert summarize([1, 2, 3]) == "1, then 2 more"

def test_class_patterns() -> None:
    assert locate(Point(0, 0)) == "The origin"
    assert locate(Point(3, 0)) == "On the x-axis at x=3"
    assert locate(Point(3, 4)) == "At (3, 4)"

def test_mapping_patterns() -> None:
    assert handle({"type": "key", "key": "Esc"}) == "key Esc"
    assert handle({"nope": 1}) == "not an event"

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0
```

## Exercises

1.  Write `classify(value)` that uses `match` to return `"empty list"`,
    `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
    and `"other"` for anything else.
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union *without* adding its `case`.
    Run `ty` and read the error it reports at `assert_never`.
3.  Rewrite `mapping_patterns.handle` to also accept a nested shape,
    such as `{"type": "click", "at": {"x": x, "y": y}}`,
    binding `x` and `y` from the inner dictionary.
