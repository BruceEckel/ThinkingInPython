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

For a plain value-to-value lookup like this,
a dictionary is often shorter (see [the end of this chapter](#when-not-to-match)).
`match` becomes valuable once the patterns do more than test equality.

## Alternatives and Capture

Combine several patterns in one `case` with `|`.
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
from sequence_patterns import summarize

def test_sequence_patterns() -> None:
    assert summarize([]) == "Empty"
    assert summarize([5]) == "One item: 5"
    assert summarize([1, 2, 3]) == "1, then 2 more"
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
from class_patterns import locate
from keyword_patterns import describe
from point import Point

def test_class_patterns() -> None:
    assert locate(Point(0, 0)) == "The origin"
    assert locate(Point(3, 0)) == "On the x-axis at x=3"
    assert locate(Point(3, 4)) == "At (3, 4)"

def test_keyword_patterns() -> None:
    assert describe(Point(0, 5)) == "Somewhere on the y-axis"
    assert describe(Point(3, 0)) == "Somewhere on the x-axis"
    assert describe(Point(2, 2)) == "On the diagonal at 2"
    assert describe(Point(3, 4)) == "Just some point"
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
If you add a type to the union and forget its case,
that becomes a type error caught before the program runs,
not a silent fall-through.
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
`shape` could now be a `Triangle` that no `case` handles.

A plain `switch`, in C, JavaScript, or traditional Java, cannot do this.
Nothing forces you to add a case, and an unhandled value falls through silently.
Scala's `match`, Kotlin's `when`,
and Java's newer switch expressions do check this,
as long as the matched type is a sealed hierarchy the compiler can see in full.

Python has no `sealed` keyword.
`assert_never()` plus a type checker fills that role instead.
An `if`/`isinstance()` chain can also get there,
but only if you remember to end it with `assert_never()`.
A `match` makes the shape of the dispatch explicit.

Note that this example reframes the classic OOP "shapes" example without inheritance and dynamic binding.
Dynamic binding discovers an object's actual type at runtime.
Pattern matching does the same, but is a better solution by centralizing type-dependent behavior in a single place.
[Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance) uses this technique to add operations to a closed set of types without inheritance.

```python
# test_exhaustive.py
from exhaustive import Circle, Square, area

def test_exhaustive_area() -> None:
    assert round(area(Circle(1.0)), 4) == 3.1416
    assert area(Square(2.0)) == 4.0
```

## When Not to Match

`match` is not a replacement for everything.

For a plain value-to-value lookup, a dictionary is shorter and faster:

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

## Exercises

1.  Write `classify(value)` that uses `match` to return `"empty list"`,
    `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
    and `"other"` for anything else.
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union *without* adding its `case`.
    Run `ty` and read the error it reports at `assert_never`.
3.  Rewrite `mapping_patterns.handle()` to also accept a nested shape,
    such as `{"type": "click", "at": {"x": x, "y": y}}`,
    binding `x` and `y` from the inner dictionary.
