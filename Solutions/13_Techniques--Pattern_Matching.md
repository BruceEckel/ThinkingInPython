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
matches one or more elements: the first `_` matches the first element,
and `*_` collects the rest, even when the rest is empty. So
`[_, *_]` also fits a singleton, and order matters: `[_]` must come
before `[_, *_]`, or the general pattern claims `[1]` first and
"singleton" never runs. `Point()` matches any `Point` instance without
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

Once `Rectangle` joins the `Shape` union, the type checker can prove that a
`Rectangle` value falls through both `case`s and reaches `case _`.
`assert_never()` demands an argument of type `Never`, meaning "this
code is unreachable." The type checker now knows `shape` can be a
`Rectangle` at that point, so the two types disagree and the checker
reports an error. That error is the safety net the chapter describes:
the missing case becomes a type error at check time instead of a
silent gap that shows up only when an actual `Rectangle` reaches
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
        case unknown:
            return f"Unrecognized event: {unknown}"

print(handle({"type": "click", "at": {"x": 10, "y": 20}}))
#: Click at (10, 20)
print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
```

The new `case` nests a mapping pattern inside a mapping pattern:
`{"at": {"x": x, "y": y}}` matches when `"at"` maps to a dictionary
that itself has `"x"` and `"y"` keys, binding both in one step. The
nested case and the flat `{"type": "click", "x": x, "y": y}` case
each describe one shape of click event, and both return the same
string. The two cases never compete: a flat event has no `"at"` key
and a nested one has no top-level `"x"`, so each event fits only one
of them. Order matters for `{"type": kind}`, which any event with a
`"type"` key satisfies. `match` tries cases top to bottom and stops
at the first one that fits, so that catchall sits after the specific
click and key cases.

## 4. A `Webhook` channel added to the union

```python
# exercise_4.py
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

@dataclass(frozen=True)
class Webhook:
    url: str

type Notification = Email | Sms | Push | Webhook

def render(note: Notification, recipient: str) -> str:
    match note:
        case Email(subject):
            return f"Email to {recipient}: {subject}"
        case Sms(body):
            return f"SMS to {recipient}: {body}"
        case Push(title):
            return f"Push to {recipient}: {title}"
        case Webhook(url):
            return f"POST for {recipient} to {url}"
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
        case Webhook():
            return 0.0
        case _:
            assert_never(note)

hook = Webhook("https://example.com/hook")
print(render(hook, "Dana"))
#: POST for Dana to https://example.com/hook
print(cost(hook))
#: 0.0
```

Add `Webhook` to the union and run `ty` before adding either `case`.
The checker reports two diagnostics, one per function that matches on
the union:

```
error[type-assertion-failure]: Argument does not have asserted type `Never`
  --> notifications_match.py:32:13
   |
32 |             assert_never(note)
   |             ^^^^^^^^^^^^^----^
   |                          |
   |                          Inferred type of argument is `Webhook & ~Email & ~Sms & ~Push`
info: `Never` and `Webhook & ~Email & ~Sms & ~Push` are not equivalent types
```

`assert_never()` declares its parameter as `Never`, the type no value
has, so the call checks only when the cases above it have already
eliminated every member of the union. The inferred type spells out
what survived those cases: a `Webhook` that is none of the three
handled types. That is the value which can reach the line, so the
check fails. Two diagnostics for one new channel is the cost the
chapter describes: adding a type touches every operation.

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
guard hides the shape of the dispatch: you have to read five nearly
identical `if` clauses one at a time to see that they enumerate sign
combinations. Once the subject is `sign(p.x), sign(p.y)`, the cases
are literals in a two-column table, and a missing combination is
visible at a glance. The `|` alternation then handles both axis cases
in one line, which no guard arrangement does as briefly.

The cost is the `sign()` helper and one extra layer of indirection:
the `match` no longer mentions `Point` at all. That trade is usually
worth it when the guards are all testing the same handful of
derived facts, and not worth it when each guard asks a different
question.

## 6. A constant that captures, and two ways to fix it

```python
# ch13_fallback_capture.py
from enum import Enum
from typing import Final

class Signal(Enum):
    STOP = "stop"
    GO = "go"
    CAUTION = "caution"

FALLBACK: Final[Signal] = Signal.CAUTION

class Defaults:
    FALLBACK: Final[Signal] = Signal.CAUTION

def act(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case FALLBACK:
            return f"fallback, FALLBACK is now {FALLBACK}"
    return "unreachable"

def dotted(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case Defaults.FALLBACK:
            return "fallback"
        case _:
            return "brake"

def guarded(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case other if other is FALLBACK:
            return "fallback"
        case _:
            return "brake"

print(act(Signal.STOP))
#: fallback, FALLBACK is now Signal.STOP
print(FALLBACK)
#: Signal.CAUTION
print(dotted(Signal.STOP), dotted(Signal.CAUTION))
#: brake fallback
print(guarded(Signal.STOP), guarded(Signal.CAUTION))
#: brake fallback
```

`act()` answers "fallback" for `Signal.STOP`, which is not the
fallback value. `case FALLBACK:` is a bare name, so it captures: it
matches `Signal.STOP`, binds it to a local named `FALLBACK` inside
`act()`, and never compares anything. The module-level constant
still holds `Signal.CAUTION` afterward, which is why the mistake is
easy to miss. Python accepts `case FALLBACK:` only because it is the
last case. Another case after it fails to compile.

The first fix gives the constant a dotted name by putting it in a
namespace. `Defaults.FALLBACK` is a value pattern, so `dotted()`
compares against it and answers "brake" for `Signal.STOP`. Any dotted
name works, including `Signal.CAUTION` itself. Moving the constant
into a class keeps one definition for the rest of the program to use.

The second fix keeps the bare constant and moves the comparison into a
guard, where `FALLBACK` is an ordinary expression rather than a
pattern. `case other if other is FALLBACK:` is more verbose than the
dotted name, but it is what you want when the test is more than
equality.
