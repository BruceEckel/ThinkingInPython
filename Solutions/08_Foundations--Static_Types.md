# Static Types: Solutions

## 1. A third shape satisfying `Drawable`

```python
# exercise_1.py
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "circle"

class Square:
    def draw(self) -> str:
        return "square"

class Triangle:
    def draw(self) -> str:
        return "triangle"

def render(shape: Drawable) -> str:
    return shape.draw()

print(render(Circle()))
#: circle
print(render(Square()))
#: square
print(render(Triangle()))
#: triangle
```

`Triangle` never mentions `Drawable`, the same as `Circle` and
`Square`. It qualifies purely because it has a `draw() -> str` method,
which is the whole of `Drawable`'s required shape. Neither `Drawable`
nor `render()` needed to change to accept it.

## 2. Removing `# type: ignore` from `area.py`

```python
def area(width: int, height: int) -> int:
    return width * height

print(area("3", 4))
```

Running `ty check` on this without the `# type: ignore` comment
reports:

```
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> area.py:4:12
  |
4 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
  |
info: Function defined here
 --> area.py:1:5
  |
1 | def area(width: int, height: int) -> int:
  |     ^^^^ ---------- Parameter declared here
```

The type checker pinpoints the mistake the chapter describes: `"3"`
is a `str`, not an `int`, so it violates `width: int`. The call still
runs without error at runtime, because `"3" * 4` is valid string
repetition. In the book, the `# type: ignore` comment on this line
existed only to let this deliberately-wrong example pass the book's
own build. Removing the comment restores the error `ty` exists to
catch.

## 3. A second generic function, `last()`

```python
# exercise_3.py
def first[T](items: list[T]) -> T:
    return items[0]

def last[T](items: list[T]) -> T:
    return items[-1]

print(last([10, 20, 30]))
#: 30
print(last(["a", "b", "c"]))
#: c
```

`last()` mirrors `first()`: one type parameter `T`, inferred from
whatever `list[T]` the caller passes. Calling `last()` on a `list[int]`
makes `T` `int` for that call, and on a `list[str]` makes `T` `str`,
exactly as `first()` does. The type checker therefore knows that
`last([10, 20, 30])` returns an `int` and `last(["a", "b", "c"])`
returns a `str`.

## 4. A subclass of `NamedTally` still chains through `Self`

```python
# exercise_4.py
from typing import Self

class Tally:
    def __init__(self) -> None:
        self.count = 0

    def bump(self) -> Self:
        self.count += 1
        return self

class NamedTally(Tally):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def report(self) -> str:
        return f"{self.name}: {self.count}"

class LoudTally(NamedTally):
    def report(self) -> str:
        return super().report().upper()

t = LoudTally("clicks")
print(t.bump().bump().report())
#: CLICKS: 2
```

`Tally` declares `bump()` with return type `Self`, which the type
checker resolves to whatever class `bump()` was actually called on. On
a `LoudTally`, `Self` means `LoudTally`, so `t.bump().bump()`
type-checks as a `LoudTally` and `.report()` is available on the
result. That call resolves to `LoudTally.report()`, because Python
always starts method lookup from the actual (most derived) class. If
`bump()`'s return annotation were the fixed type `Tally` instead of
`Self`, the type checker would reject `.report()` on the chained
result, since plain `Tally` has no `report()` method.

## 5. What a missing type parameter default costs

```python
# exercise_5.py
from typing import reveal_type

class Stack[T = str]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

words: Stack = Stack()
words.push("beta")
reveal_type(words.top())  # ty: str
print(words.top().upper())
#: BETA
```

With `= str` in place, `ty check` reports `str` for
`reveal_type(words.top())`. Remove the default and `ty` reports
`Unknown` while still finding no errors in the file. That is the
lesson: an unsolved type parameter does not fail the check, it
switches the check off for every expression downstream of it.
`words.top().upper()` passes either way, and so would
`words.top().no_such_method()`. A default converts a silently
unchecked annotation into a checked one. That conversion is why a
default earns its place on a class whose parameter has one common
answer.

## 6. A `Literal` that does not admit `"purple"`

```python
# exercise_6.py
from typing import Literal

type Coord = tuple[int, int]
type Grid = dict[Coord, str]
type Color = Literal[
    "red", "blue", "green", "yellow", "purple"]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "purple")
print(grid)
#: {(2, 3): 'purple'}
```

Before `"purple"` joins `Color`, the call runs and stores the string,
because a `Literal` constrains nothing at run time. `ty check`
reports:

```
error[invalid-argument-type]: Argument to function `paint` is incorrect
  --> type_aliases.py:14:21
   |
14 | paint(grid, (2, 3), "purple")
   |                     ^^^^^^^^ Expected `Literal["red", "blue", "green", "yellow"]`,
   |                              found `Literal["purple"]`
```

The diagnostic spells out the expected type in full even though
`paint()` names it as `Color`. That is the practical argument for
naming the union once rather than repeating the four strings in every
signature: the alias costs nothing in the error message, and the
allowed set has one place to change. Adding `"purple"` to that one
alias silences the error everywhere. `grid[cell] = color` needs no
change, since `Grid`'s values are plain `str` and every `Color` is one.

## 7. Widening `add_square()` to `Sequence[Shape]`

```python
# exercise_7.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: Sequence[Shape]) -> None:
    # ty: "Sequence[Shape]" has no attribute "append":
    # shapes.append(Shape())
    print("would add a square to", len(shapes), "shapes")

circles: list[Circle] = [Circle(), Circle()]
add_square(circles)  # Now accepted
#: would add a square to 2 shapes
print(count(circles))
#: 2
```

`ty` accepts the call because `Sequence` is covariant in its element
type. A `Sequence[Shape]` promises only that you can read `Shape`s out
of it, and every `Circle` you read out is a `Shape`, so a
`list[Circle]` satisfies that promise. `list[Shape]` refused the same
argument because `list` is invariant.

`shapes.append(...)` stops type-checking for the reason the widening
worked. `Sequence` has no `append()` at all: it is the read-only
abstract shape, so the diagnostic is `unresolved-attribute` rather
than an argument-type error. The type checker is not saying "you may not
append a `Shape` here," it is saying there is no such operation on
what you declared.

That pairing is the whole of variance in one edit. Invariance is the
price of being able to write. Covariance is what you get when you give
that up. The practical rule follows: annotate a parameter with the
weakest shape the body actually needs, because every capability you
declare is a caller you turn away.

## 8. Truthiness in place of `is not None`

```python
# exercise_8.py

def shout(text: str | None) -> str:
    if text:
        return text.upper()
    return "(nothing)"

print(shout("hi"))
#: HI
print(shout(None))
#: (nothing)
print(shout(""))  # The empty string is falsy
#: (nothing)
```

`ty` accepts either version, and for a good reason: truthiness
narrows too. `None` is falsy, so inside `if text:` the type checker
rules out `None` exactly as `is not None` did, and `.upper()` is safe
under both spellings.

What changed is which values reach which branch. `is not None` asks
one question, whether the value is missing. `if text:` asks a
different one, whether the value is missing *or* empty, and answers
both with `"(nothing)"`. An empty string that a caller passed on
purpose is now indistinguishable from no string at all.

Whether that matters depends on the caller, and that is the point of
the exercise: the type checker cannot tell you, because both versions are
type-correct. The truthiness test is the same trap as `if not target:`
on a mutable default in
[Functions](../Chapters/05_Foundations--Functions.md), and the same
answer applies. Test for the condition you mean. Use `is None` when
you mean "was anything supplied," and truthiness only when an empty
value genuinely belongs with the missing one.
