# Pattern Matching: Solutions

## 1. `classify()` over lists, a `Point`, and anything else

> Write `classify(value)` that uses `match` to return `"empty list"`,
> `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
> and `"other"` for anything else.

<details>
<summary>Where to look</summary>

[Sequence Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#sequence-patterns)
covers matching by shape, including a starred name for the rest of a sequence.
Then [Class Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#class-patterns)
shows how to test a value for the `Point` type alone.
`match` tries cases top to bottom,
so put the narrow list shapes before the wider one.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

def classify(value: object) -> str:
    ...
```

<details>
<summary>Done when</summary>

your `classify()` returns `"empty list"` for `[]`,
`"singleton"` for a one-element list, `"longer list"` for `[1, 2, 3]`,
`"point"` for `Point(1, 2)`, and `"other"` for `"hi"`.
If `classify([1])` returns `"longer list"`,
a wider case sits above a narrower one.

<details>
<summary>Solution</summary>

If you drop the parentheses and write `case Point:`,
the script stops at compile time.
A bare `Point` is a capture pattern that matches any value,
so Python rejects the `case _` after it with `SyntaxError: name capture 'Point' makes remaining patterns unreachable`.
The solution writes `case Point():`, a class pattern that tests the type.

```python
# exercise_1.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

def classify(value: object) -> str:
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
print(classify((1,)))
#: singleton
```

**Tell lists apart by length.**
`[_, *_]` matches one or more elements.
Its `*_` collects the rest, including an empty rest.
So `[_, *_]` also fits a singleton.
`[_]` must come before it, or `[_, *_]` matches the one-element list first,
leaving the "singleton" case unreachable.

**Test the type alone.**
`Point()` matches any `Point` instance.
That suits `classify()`,
which returns the same string whatever `x` and `y` hold.

The string `"hi"` is a sequence of two characters,
but a sequence pattern excludes `str`, so `classify()` returns "other" for it.
The tuple `(1,)` does match a sequence pattern.
A sequence pattern tests the shape, not the type,
so a one-element tuple is a "singleton" here.

When "singleton" must mean a `list` alone, wrap the pattern in a class pattern.
`case list([_]):` first tests for a `list`, then matches the one-element shape.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Adding `Rectangle` without its `case`

> Add a `Rectangle` type to `exhaustive.py`'s `Shape` union without adding its `case`.
> Run `ty` and read the error it reports at `assert_never()`.

<details>
<summary>Where to look</summary>

[Exhaustive Matching](../../Chapters/13_Techniques--Pattern_Matching.md#exhaustive-matching)
ends the `match` with `assert_never()`.
Add the new data class and include it in the `Shape` union,
but leave `area()` alone.
The type checker's message shows the type left after the `case`s above `assert_never()` narrow `shape`.

<details>
<summary>Done when</summary>

`uv run ty check` on your edited `exhaustive.py` reports a `type-assertion-failure` at the `assert_never()` call,
with the inferred type `Rectangle & ~Circle & ~Square`,
and you can say why that type reaches the call.

<details>
<summary>Solution</summary>

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
  --> exhaustive.py:29:13
   |
29 |             assert_never(shape)
   |             ^^^^^^^^^^^^^-----^
   |                          |
   |                          Inferred type of argument is `Rectangle & ~Circle & ~Square`
info: `Never` and `Rectangle & ~Circle & ~Square` are not equivalent types
```

Once `Rectangle` joins the `Shape` union,
the type checker finds that a `Rectangle` value falls through both `case`s and reaches `case _`,
so `shape` can be a `Rectangle` at the `assert_never()` call.
`assert_never()` requires an argument of type `Never`,
meaning "this code is unreachable."

The `type-assertion-failure` is the check the chapter describes.
The missing case becomes a type error at check time,
instead of an `AssertionError` that `assert_never()` raises when a `Rectangle` reaches `area()` at runtime.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. Matching a nested shape

> Rewrite `mapping_patterns.handle()` to also accept a nested shape,
> such as `{"type": "click", "at": {"x": x, "y": y}}`,
> binding `x` and `y` from the inner dictionary.

<details>
<summary>Where to look</summary>

[Mapping Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#mapping-patterns)
matches a dictionary by the keys it must contain.
The value position in a mapping pattern holds a pattern,
so it can hold another mapping pattern,
as [Patterns Nest](../../Chapters/13_Techniques--Pattern_Matching.md#patterns-nest)
shows.
Put a mapping pattern inside the `"at"` entry,
and keep the flat click case so both shapes still work.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
def handle(event: dict[str, object]) -> str:
    ...
```

<details>
<summary>Done when</summary>

your `handle()` returns `Click at (10, 20)` for both `{"type": "click", "at": {"x": 10, "y": 20}}` and `{"type": "click", "x": 10, "y": 20}`,
and the four calls in `mapping_patterns.py` still print their original lines.

<details>
<summary>Solution</summary>

If you replace the flat click case with the nested one,
a flat click event falls through to `{"type": kind, **rest}`,
and `handle()` returns `Other event: click {'x': 10, 'y': 20}`.
The exercise asks for the nested shape in addition to the flat one,
so the solution keeps both cases.

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
        case {"type": kind, **rest}:
            return f"Other event: {kind} {rest}"
        case unknown:
            return f"Unrecognized event: {unknown}"

print(handle({"type": "click", "at": {"x": 10, "y": 20}}))
#: Click at (10, 20)
print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
```

**Match the inner dictionary.**
The new `case` nests a mapping pattern inside a mapping pattern.

**Try the specific cases first.**
Any event with a `"type"` key satisfies `{"type": kind, **rest}`,
so the order of the cases matters.
`match` tries cases top to bottom and stops at the first one that fits,
so `{"type": kind, **rest}` sits after the specific click and key cases.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A `Webhook` channel added to the union

> Add a `Webhook` channel to `notifications_match.py`:
> a data class with a `url` field, added to the `Notification` union.
> Run `ty` before adding its `case` to `render()` and `cost()`,
> and read the errors.
> Then add both cases and confirm `ty` passes.

<details>
<summary>Where to look</summary>

[The Match Version](../../Chapters/13_Techniques--Pattern_Matching.md#the-match-version)
ends both `render()` and `cost()` with `assert_never()`.
Add the `Webhook` data class to the `Notification` union first and run the type checker before touching either function.
The type checker reports one error for each function that matches on the union,
until that function gains a `case`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
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
    ...

def cost(note: Notification) -> float:
    ...
```

<details>
<summary>Done when</summary>

before you add the cases,
`uv run ty check` reports two `type-assertion-failure` diagnostics,
one at the `assert_never()` in `render()` and one in `cost()`,
each naming `Webhook & ~Email & ~Sms & ~Push`.
After you add both cases,
it prints `All checks passed!` and `render()` and `cost()` accept a `Webhook`.

<details>
<summary>Solution</summary>

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

If you add `Webhook` to the union and run `ty` before adding either `case`,
the checker reports two diagnostics, one per function that matches on the union:

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

The output above shows the first diagnostic, in `render()`.
The second is the same diagnostic at line 43, in `cost()`.
With both cases added, as in `exercise_4.py`,
`ty check` reports `All checks passed!`.

`assert_never()` declares its parameter as `Never`, the type with no values,
so the call type-checks only when the cases above it have eliminated every member of the union.
The inferred type is what remains after those cases narrow `note`:
a `Webhook` that is none of the three handled types.

One new channel produces two diagnostics because adding a type to the match version requires a new `case` in every function that matches on the union,
as the chapter describes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Quadrants with guards, and without them

> Rewrite `guards.py`'s `quadrant()` so it handles the third and fourth quadrants too.
> Then write it a second time matching on `sign(p.x), sign(p.y)`,
> with one `case` per quadrant, a `|` alternation for the axes, and no guards,
> and say which version reads better.

<details>
<summary>Where to look</summary>

[Guards](../../Chapters/13_Techniques--Pattern_Matching.md#guards)
adds an `if` condition to a `case`.
For the second version,
change the subject of the `match` to a tuple of derived values.
Then write literal patterns for each combination,
and use `|` from [Alternatives and Capture](../../Chapters/13_Techniques--Pattern_Matching.md#alternatives-and-capture)
to join the axis cases.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

def quadrant(p: Point) -> str:
    ...
```

```python
# The shape of exercise_5_signs.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

def sign(n: int) -> int:
    ...

def quadrant(p: Point) -> str:
    ...
```

<details>
<summary>Done when</summary>

both versions print `Third quadrant Fourth quadrant` for `Point(-3, -4)` and `Point(3, -4)`,
and `On an axis` for `Point(0, 7)`.
`uv run ty check` passes on the version that matches on `sign(p.x), sign(p.y)`,
and you can say which version reads better and why.

<details>
<summary>Solution</summary>

The first version adds a guarded `case` for each of the third and fourth quadrants:

```python
# exercise_5.py
from dataclasses import dataclass

@dataclass(frozen=True)
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

The second version replaces every guard with a literal pattern,
by matching on the pair of signs rather than on the point:

```python
# exercise_5_signs.py
from dataclasses import dataclass

@dataclass(frozen=True)
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

If you delete the final `case _` from the second version,
the script prints the same two lines, but `ty` reports `invalid-return-type`.
The type checker finds a path that falls off the end of the function and returns `None`,
which conflicts with the declared return type, `str`.
The six cases cover all nine pairs of signs,
but the type checker knows `sign()` by its declared return type, `int`,
so it allows a pair such as `(2, 5)`.
That pair falls through all six cases.
The solution keeps an unreachable `case _` so every path returns a `str`.

The second version reads better.
A guard hides the shape of the dispatch.
You must read four nearly identical `if` clauses one at a time to see that they enumerate sign combinations.
When the subject is `sign(p.x), sign(p.y)`,
the cases are literals in a two-column table.
A missing combination is visible at a glance.
The `|` alternation then handles both axis cases in one line,
more briefly than any arrangement of guards.

The second version adds the `sign()` helper and one layer of indirection.
The `match` tests two derived signs in place of the `Point`.
Matching on the signs helps when the guards all test the same handful of derived facts.
When each guard tests a different condition, keep the guards.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A constant that captures, and two ways to fix it

> Give `value_patterns.py`'s `Signal` a third member,
> and write `act()` so that it compares against a module-level `FALLBACK: Final[Signal]`.
> Run it and confirm that the constant captures instead of comparing.
> Then fix `act()` two ways, with a value pattern and with a guard.

<details>
<summary>Where to look</summary>

[A Bare Name Captures, a Dotted Name Compares](../../Chapters/13_Techniques--Pattern_Matching.md#a-bare-name-captures-a-dotted-name-compares)
explains why a module-level constant in a `case` binds instead of comparing.
For the first fix, put the constant in a namespace so the pattern is a dotted name.
For the second, bind any value and compare it to the constant in a guard,
where `FALLBACK` is an ordinary expression.

<details>
<summary>The shape</summary>

```python
# The shape of ch13_fallback_capture.py
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
    ...

def dotted(s: Signal) -> str:
    ...

def guarded(s: Signal) -> str:
    ...
```

<details>
<summary>Done when</summary>

`act(Signal.STOP)` takes your `FALLBACK` case while `print(FALLBACK)` afterward still shows the third member.
Each fixed version takes the fallback case for the third member and sends `Signal.STOP` to a different case.

<details>
<summary>Solution</summary>

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

**Demonstrate the accidental capture.**
`act()` takes the fallback case for `Signal.STOP`,
although the fallback value is `Signal.CAUTION`.
`case FALLBACK:` holds a bare name, so the pattern captures.
The pattern matches `Signal.STOP` as it matches any value,
and binds that value to a local named `FALLBACK` inside `act()`.
The module-level constant holds `Signal.CAUTION` before and after the call,
so printing `FALLBACK` shows the expected value and hides the mistake.

Python accepts `case FALLBACK:` because it is the last case,
and rejects any case after it with a `SyntaxError`.

**Compare through a dotted name.**
The first fix gives the constant a dotted name by putting it in a namespace.
`Defaults.FALLBACK` is a value pattern, so `dotted()` compares against it.
Any dotted name works, including `Signal.CAUTION`.

In a program the constant would live in `Defaults` alone,
so every use reads that one definition.
The listing keeps the module-level copy because `act()` and `guarded()` need the bare name.

**Compare in a guard.**
The second fix keeps the bare constant and moves the comparison into a guard,
where `FALLBACK` is an ordinary expression rather than a pattern.
`case other if other is FALLBACK:` is longer than `case Defaults.FALLBACK:`,
and more flexible.
A value pattern always compares with `==`, while a guard holds any expression:
an `is` test like this one, a membership test, or a call.
Choose the guard when the test needs one of those.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
