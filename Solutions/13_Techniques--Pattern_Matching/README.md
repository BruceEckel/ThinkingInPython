# Pattern Matching: Solutions

## 1. `classify()` over lists, a `Point`, and anything else

> Write `classify(value)` that uses `match` to return `"empty list"`,
> `"singleton"`, or `"longer list"` for lists, `"point"` for a `Point`,
> and `"other"` for anything else.

<details>
<summary>Where to look</summary>

[Sequence Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#sequence-patterns) covers matching by shape, including a star pattern for the rest of a sequence.
Then [Class Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#class-patterns) shows how to test for a `Point` without binding its fields.
`match` tries cases top to bottom, so put the narrow list shapes before the wider one.

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
<summary>Solution</summary>

If you drop the parentheses and write `case Point:`, the script does not compile.
Without parentheses `Point` is a bare name, so the pattern captures any value,
and Python rejects the `case _` after it with `SyntaxError: name capture 'Point' makes remaining patterns unreachable`.
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

**Tell lists apart by length.** `[]` matches only an empty sequence.
`[_]` matches a list with exactly one element (the `_` throws the
element away without a name). `[_, *_]` matches one or more elements.
The first `_` matches the first element, and `*_` collects the rest,
including an empty rest. So `[_, *_]` also fits a singleton, and order
matters. `[_]` must come before `[_, *_]`, or the general pattern
claims the one-element list first and the "singleton" case is unreachable.

**Test the type alone.** `Point()` matches any `Point`
instance without binding its fields, since `classify()` doesn't need
`x` or `y`.

The string `"hi"` is a sequence of two characters, but a sequence
pattern excludes `str`, so `classify()` still returns "other" for it.
The tuple `(1,)` goes the other way. A sequence pattern tests the
shape, not the type, so a one-element tuple is a "singleton" here.
When the answer must hold for a `list` alone, wrap the pattern in a
class pattern. `case list([_]):` first tests for a `list`, then
matches the one-element shape.

</details>
</details>
</details>

## 2. Adding `Rectangle` without its `case`

> Add a `Rectangle` type to `exhaustive.py`'s `Shape` union without adding its `case`.
> Run `ty` and read the error it reports at `assert_never()`.

<details>
<summary>Where to look</summary>

[Exhaustive Matching](../../Chapters/13_Techniques--Pattern_Matching.md#exhaustive-matching) ends the `match` with `assert_never()`.
Add the new data class and include it in the `Shape` union, but leave `area()` alone.
The type checker's message shows the type that survives every `case` above `assert_never()`.

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
  --> exhaustive.py:28:13
   |
28 |             assert_never(shape)
   |             ^^^^^^^^^^^^^-----^
   |                          |
   |                          Inferred type of argument is `Rectangle & ~Circle & ~Square`
info: `Never` and `Rectangle & ~Circle & ~Square` are not equivalent types
```

Once `Rectangle` joins the `Shape` union, the type checker proves that a
`Rectangle` value falls through both `case`s and reaches `case _`.
`assert_never()` demands an argument of type `Never`, meaning "this
code is unreachable." The type checker now knows `shape` can be a
`Rectangle` at that point, so `Never` and the argument's type disagree and the checker
reports an error. That error is the check the chapter describes.
The missing case becomes a type error at check time instead of a
silent gap that shows up only when a `Rectangle` reaches `area()` at
runtime.

</details>
</details>

## 3. Matching a nested shape

> Rewrite `mapping_patterns.handle()` to also accept a nested shape,
> such as `{"type": "click", "at": {"x": x, "y": y}}`,
> binding `x` and `y` from the inner dictionary.

<details>
<summary>Where to look</summary>

[Mapping Patterns](../../Chapters/13_Techniques--Pattern_Matching.md#mapping-patterns) matches a dictionary by the keys it must contain.
A value inside a mapping pattern can itself be a pattern, as [Patterns Nest](../../Chapters/13_Techniques--Pattern_Matching.md#patterns-nest) shows.
Put a mapping pattern inside the `"at"` entry, and keep the flat click case so both shapes still work.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
def handle(event: dict[str, object]) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you replace the flat click case with the nested one, a flat click event matches no click case.
It falls through to `{"type": kind}`, and `handle()` returns `Other event: click`.
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

**Match the inner dictionary.** The new `case` nests a mapping pattern inside a mapping pattern.
`{"at": {"x": x, "y": y}}` matches when `"at"` maps to a dictionary
that has `"x"` and `"y"` keys, binding both in one step.

**Accept both click shapes.** The
nested case and the flat `{"type": "click", "x": x, "y": y}` case
each describe one shape of click event, and both return the same
string. The two cases do not compete. A flat event has no `"at"` key
and a nested one has no top-level `"x"`, so each event fits only one
of them.

**Try the specific cases first.** Order matters for `{"type": kind}`, which any event with a
`"type"` key satisfies. `match` tries cases top to bottom and stops
at the first one that fits, so `{"type": kind}` sits after the specific
click and key cases.

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

[The Match Version](../../Chapters/13_Techniques--Pattern_Matching.md#the-match-version) ends both `render()` and `cost()` with `assert_never()`.
Add the `Webhook` data class to the `Notification` union first and run the type checker before touching either function.
Each function that matches on the union reports its own error until it gains a `case`.

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

If you add `Webhook` to the union and run `ty` before adding either
`case`, the checker reports two diagnostics, one per function that
matches on the union:

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

The fence shows the first diagnostic, in `render()`. The second is identical, at
line 43 in `cost()`.

`assert_never()` declares its parameter as `Never`, the type with no
values, so the call checks only when the cases above it have
eliminated every member of the union. The inferred type spells out
what survives those cases: a `Webhook` that is none of the three
handled types. A `Webhook` can still reach the `assert_never()` call,
so the check fails. One new channel draws two diagnostics because, as
the chapter describes, adding a type touches every operation.

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

[Guards](../../Chapters/13_Techniques--Pattern_Matching.md#guards) adds an `if` condition to a `case`.
For the second version, change the subject of the `match` to a tuple of derived values.
Then write literal patterns for each combination, and use `|` from [Alternatives and Capture](../../Chapters/13_Techniques--Pattern_Matching.md#alternatives-and-capture) to join the axis cases.

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
<summary>Solution</summary>

If you write the second version without its final `case _`, the
script still prints the same two lines, but `ty` reports
`invalid-return-type`, since the function can implicitly return
`None`, which is not assignable to its return type `str`.
The six cases cover all nine
pairs of signs, but to the type checker `sign()` returns any `int`,
so a pair such as `(2, 5)` matches none of them. The solution keeps
an unreachable `case _` so every path returns a `str`.

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

The second version replaces every guard with a literal pattern, by
matching on the pair of signs rather than on the point:

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

The second version reads better. A guard hides the shape of the
dispatch. You must read four nearly identical `if` clauses one at a
time to see that they enumerate sign combinations. Once the subject is
`sign(p.x), sign(p.y)`, the cases are literals in a two-column table,
and a missing combination is visible at a glance. The `|` alternation
then handles both axis cases in one line, which no guard arrangement
does as briefly.

The second version adds the `sign()` helper and one layer of
indirection: the `match` no longer mentions `Point`. That trade is
usually worth it when the guards all test the same handful of derived
facts, and not worth it when each guard asks a different question.

**Give every path a return.** The final `case _` is unreachable, since the six cases above it cover
all nine pairs of signs. The type checker sees only that `sign()`
returns an `int`, so without that case it reports that `quadrant()`
can return `None`.

</details>
</details>
</details>

## 6. A constant that captures, and two ways to fix it

> Give `value_patterns.py`'s `Signal` a third member,
> and write `act()` so that it compares against a module-level `FALLBACK: Final[Signal]`.
> Run it and confirm that the constant captures instead of comparing.
> Then fix it two ways, with a dotted name and with a guard.

<details>
<summary>Where to look</summary>

[A Bare Name Captures, a Dotted Name Compares](../../Chapters/13_Techniques--Pattern_Matching.md#a-bare-name-captures-a-dotted-name-compares) explains why a module-level constant in a `case` binds instead of comparing.
For the first fix, put the constant in a namespace so the pattern is a dotted name.
For the second, bind any value and compare it to the constant in a guard, where the name is an ordinary expression.

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

**Demonstrate the accidental capture.** `act()` answers "fallback" for `Signal.STOP`, which is not the
fallback value. `case FALLBACK:` is a bare name, so it captures. It
matches `Signal.STOP`, binds it to a local named `FALLBACK` inside
`act()`, and compares nothing. The module-level constant
still holds `Signal.CAUTION` afterward, so the mistake is
easy to miss.

Python accepts `case FALLBACK:` only because it is the last case.
Python rejects another case after it with a `SyntaxError`.

**Compare through a dotted name.** The first fix gives the constant a dotted name by putting it in a
namespace. `Defaults.FALLBACK` is a value pattern, so `dotted()`
compares against it and answers "brake" for `Signal.STOP`. Any dotted
name works, including `Signal.CAUTION`.

In a program the constant would live in `Defaults` alone, one
definition for every use. The listing keeps the module-level copy
because `act()` and `guarded()` need the bare name.

**Compare in a guard.** The second fix keeps the bare constant and moves the comparison into a
guard, where `FALLBACK` is an ordinary expression rather than a
pattern. `case other if other is FALLBACK:` is more verbose than the
dotted name, but it is what you want when the test is more than
equality.

</details>
</details>
</details>
