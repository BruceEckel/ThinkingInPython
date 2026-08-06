# Pattern Matching: Solutions

## 1. `classify()` over lists, a `Point`, and anything else

```python
# exercise_1.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def classify(value):
    match value:
        case []:
            return "empty list"
        case [_]:
            return "singleton"
        case [_, *_]:
            return "longer list"
        case Point():
            return "point"
        case _:
            return "other"

print(classify([]))
#: empty list
print(classify([1]))
#: singleton
print(classify([1, 2, 3]))
#: longer list
print(classify(Point(1, 2)))
#: point
print(classify("hi"))
#: other
```

`[]` matches only the empty list. `[_]` matches a list with exactly
one element (the `_` throws the value away without a name). `[_, *_]`
matches two or more elements: the first `_` matches the first element,
and `*_` collects everything after it, requiring the list to have at
least that first element plus more. Order matters here: the more
specific patterns (`[]`, `[_]`) must come before the more general one
(`[_, *_]`), or the general one matches first and the specific
cases never run. `Point()` matches any `Point` instance without
binding its fields at all, since `classify()` doesn't need `x` or `y`.

## 2. Adding `Rectangle` without its `case`

```python
@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

type Shape = Circle | Square | Rectangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius):
            return pi * radius ** 2
        case Square(side):
            return side ** 2
        case _:
            assert_never(shape)
```

Running `ty check` reports:

```
error[type-assertion-failure]: Argument does not have asserted type `Never`
  --> exhaustive.py:27:13
   |
27 |             assert_never(shape)
   |             ^^^^^^^^^^^^^-----^
   |                          |
   |                          Inferred type of argument is `Rectangle & ~Circle & ~Square`
   |
info: `Never` and `Rectangle & ~Circle & ~Square` are not equivalent types
```

Once `Rectangle` joins the `Shape` union, the checker can prove that a
`Rectangle` value falls through both `case`s and reaches `case _`.
`assert_never()` demands its argument have type `Never`, meaning "this
code is unreachable," but the checker now knows `shape` could
genuinely be a `Rectangle` at that point, so the two types disagree
and it reports an error. This is the safety net the chapter
describes: the missing case becomes a caught type error instead of a
silent gap that only shows up when an actual `Rectangle` reaches
`area()` at runtime.

## 3. Matching a nested shape

```python
# exercise_3.py
def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "at": {"x": x, "y": y}}:
            return f"Click at ({x}, {y})"
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"Key {key}"
        case {"type": kind}:
            return f"Other event: {kind}"
        case nonevent:
            return f"Not an event: {nonevent}"

print(handle({"type": "click", "at": {"x": 10, "y": 20}}))
#: Click at (10, 20)
print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
```

The new `case` nests a mapping pattern inside a mapping pattern:
`{"at": {"x": x, "y": y}}` matches when `"at"` maps to a dictionary
that itself has `"x"` and `"y"` keys, binding both in one step. Placing
it before the flat `{"type": "click", "x": x, "y": y}` case lets both
shapes of a click event share the same handling logic while keeping
each pattern focused on one shape; `match` tries cases top to bottom
and stops at the first one that fits, so the flat form still works
for events that were never nested to begin with.

## 4. A `Webhook` channel added to the union

```python
# exercise_4.py
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Email:
    subject: str

@dataclass(frozen=True)
class Webhook:
    url: str

type Notification = Email | Webhook

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Webhook(url):
            return f"POST for {recipient} to {url}"
        case _:
            assert_never(note)

print(render(Webhook("https://example.com/hook"), "Dana"))
#: POST for Dana to https://example.com/hook
```

Adding `Webhook` to the union and running `ty` before adding the
`case` reports, at each `assert_never()` call:

```
error[invalid-argument-type]: Argument to function `assert_never` is incorrect
  |
  |             assert_never(note)
  |                          ^^^^ Expected `Never`, found `Webhook`
```

The message names the type that has no case. `assert_never()` declares
its parameter as `Never`, the type no value has, so the call checks
only when every other case has already been eliminated. One unhandled
member leaves `Webhook` reaching that line, and the checker says so.
The same error appears once per function that matches on the union,
which is the cost the chapter describes: adding a type touches every
operation.

## 5. Quadrants with guards, and without them

```python
# exercise_5.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def quadrant(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "Origin"
        case Point(x, y) if x > 0 and y > 0:
            return "First quadrant"
        case Point(x, y) if x < 0 and y > 0:
            return "Second quadrant"
        case Point(x, y) if x < 0 and y < 0:
            return "Third quadrant"
        case Point(x, y) if x > 0 and y < 0:
            return "Fourth quadrant"
        case _:
            return "On an axis"

print(quadrant(Point(-3, -4)), quadrant(Point(3, -4)))
#: Third quadrant Fourth quadrant
print(quadrant(Point(0, 7)))
#: On an axis
```

The second version replaces every guard with a literal pattern, by
matching on the pair of signs rather than on the point:

```python
# exercise_5_signs.py
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def sign(n: int) -> int:
    return (n > 0) - (n < 0)

def quadrant(p: Point) -> str:
    match sign(p.x), sign(p.y):
        case 0, 0:
            return "Origin"
        case 1, 1:
            return "First quadrant"
        case -1, 1:
            return "Second quadrant"
        case -1, -1:
            return "Third quadrant"
        case 1, -1:
            return "Fourth quadrant"
        case (0, _) | (_, 0):
            return "On an axis"
        case _:
            return "unreachable"

print(quadrant(Point(-3, -4)), quadrant(Point(3, -4)))
#: Third quadrant Fourth quadrant
print(quadrant(Point(0, 7)))
#: On an axis
```

The second version reads better, and the reason is worth naming. A
guard hides the shape of the dispatch: five nearly identical `if`
clauses have to be read one at a time to see that they enumerate sign
combinations. Once the subject is `sign(p.x), sign(p.y)`, the cases
are literals in a two-column table, and a missing combination is
visible at a glance. The `|` alternation then handles both axis cases
in one line, which no guard arrangement does as briefly.

The cost is the `sign()` helper and one extra layer of indirection:
the `match` no longer mentions `Point` at all. That trade is usually
worth it when the guards are all testing the same handful of
derived facts, and not worth it when each guard asks a different
question.
