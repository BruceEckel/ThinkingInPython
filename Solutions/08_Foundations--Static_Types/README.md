# Static Types: Solutions

## 1. A third shape satisfying `Drawable`

> In `protocols.py`, add a class `Triangle` with its own `draw()`,
> and pass an instance to `render()` without changing `Drawable` or `render()`.

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
`Square`. It qualifies because it has a `draw() -> str` method, and
`Drawable` requires no more than that. Neither `Drawable` nor
`render()` needs to change to accept it.

## 2. Removing `# type: ignore` from `area.py`

> In `area.py`, remove the `# type: ignore` comment and run `ty check` on the file.
> Read the error, then restore the comment.

```python
def area(width: int, height: int) -> int:
    return width * height

print(area("3", 4))
```

That is the function and the call from the chapter's `area.py`,
without its comments. Running `ty check` on that file with the
`# type: ignore` comment removed reports:

```
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> area.py:6:12
  |
6 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
info: Function defined here
 --> area.py:2:5
  |
2 | def area(width: int, height: int) -> int:
  |     ^^^^ ---------- Parameter declared here
```

The type checker pinpoints the mistake the chapter describes: `"3"`
is a `str`, not an `int`, so it violates `width: int`. The call still
runs without error at runtime, because `"3" * 4` is valid string
repetition. In the book, the `# type: ignore` comment on this line
lets a deliberately wrong example pass the book's build. Removing
the comment restores the error.

## 3. A second generic function, `last()`

> In `generics.py`, write a second generic function,
> `last[T](items: list[T]) -> T`, that returns the final element,
> and call it on both a `list[int]` and a `list[str]` the way the listing calls `first()`.

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
the same as `first()` does. The type checker therefore knows that
`last([10, 20, 30])` returns an `int` and `last(["a", "b", "c"])`
returns a `str`.

## 4. A subclass of `NamedTally` still chains through `Self`

> In `self_type.py`, add a subclass of `NamedTally` called `LoudTally` whose `report()` returns the message in all capitals,
> calling `super().report()` first.
> Confirm `.bump().bump().report()` still chains correctly on a `LoudTally`.

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
checker resolves to the class on which the call is made. On
a `LoudTally`, `Self` means `LoudTally`, so `t.bump().bump()`
type-checks as a `LoudTally` and `.report()` is available on the
result. That call resolves to `LoudTally.report()`, because Python
starts method lookup at the object's own class. If `bump()`'s return
annotation is the fixed type `Tally` instead of `Self`, the type
checker rejects `.report()` on the chained result, since `Tally` has
no `report()` method.

## 5. What a missing type parameter default costs

> Add `reveal_type(words.top())` to `type_defaults.py` and run `ty check` on the file.
> Remove the `= str` default and run it again.
> The type checker reports no error either way.
> Say what that means for a bare `Stack` annotation.

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
`reveal_type(words.top())`. Without the default, `ty` reports
`Unknown` and still finds no errors in the file. An unsolved type
parameter does not fail the check. It switches the check off for
every expression built on it. `words.top().upper()` passes either
way. Without the default, so does `words.top().no_such_method()`.
A default turns a bare annotation that checks nothing into one that
checks, and that is the reason to give one to a class whose
parameter is usually the same type.

## 6. A `Literal` that does not admit `"purple"`

> In `type_aliases.py`,
> call `paint(grid, (2, 3), "purple")` and run `ty check`.
> Read the error, then widen `Color` to admit `"purple"` and confirm the error goes away.

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
  --> type_aliases.py:12:21
   |
12 | paint(grid, (2, 3), "purple")
   |                     ^^^^^^^^ Expected `Color`, found `Literal["purple"]`
info: Function defined here
 --> type_aliases.py:8:5
  |
8 | def paint(grid: Grid, cell: Coord, color: Color) -> None:
  |     ^^^^^                          ------------ Parameter declared here
```

The diagnostic names the alias rather than the union behind it, so
you read `Color` and find the four permitted strings in the `type`
statement. An alias makes that trade: a short message and one place
to change the allowed set, against following the name to see what
the set is. Adding `"purple"` to the alias removes the error at every
call. `grid[cell] = color` needs no change, since `Grid`'s values are
`str` and every `Color` is a `str`.

## 7. Widening `add_square()` to `Sequence[Shape]`

> In `variance.py`, change `add_square()`'s parameter annotation to `Sequence[Shape]` and uncomment the call.
> Explain why the type checker now accepts the call and why `shapes.append(...)` no longer type-checks.

```python
# exercise_7.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

class Square(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: Sequence[Shape]) -> None:
    # ty: "Sequence[Shape]" has no attribute "append":
    # shapes.append(Square())
    print("would add a square to", len(shapes), "shapes")

circles: list[Circle] = [Circle(), Circle()]
add_square(circles)  # Now accepted
#: would add a square to 2 shapes
print(count(circles))
#: 2
```

The type checker accepts the call because `Sequence` is covariant in its element
type. A `Sequence[Shape]` declares only that you can read `Shape`s out
of it, and every `Circle` you read out is a `Shape`, so a
`list[Circle]` meets that requirement. `list[Shape]` refuses the same
argument because `list` is invariant.

`shapes.append(...)` stops type-checking for the reason the widening
works. `Sequence` has no `append()`: it is the read-only abstract
shape, so the diagnostic is `unresolved-attribute` rather than an
argument-type error. The type checker is not saying "you may not
append a `Square` here." It is saying the type you declared has no
such operation.

The one edit shows both sides of variance. A container you can write
to is invariant, and giving up the writes makes it covariant. The
practical rule follows: annotate a parameter with the weakest shape
the body needs, because each capability you declare rejects the
callers whose argument lacks it.

## 8. Truthiness in place of `is not None`

> In `narrowing.py`, replace `if text is not None:` with `if text:` and run `ty check`.
> Explain why the empty string now takes the other branch even though the type checker accepts either version.

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

The type checker accepts either version, because truthiness narrows too. `None`
is falsy, so inside `if text:` the type checker rules out `None` the
same as `is not None` does, and `.upper()` is safe in both versions.

The change is in which values reach which branch. `is not None` asks
one question, whether the value is missing. `if text:` asks a
different one, whether the value is missing or empty, and answers
both with `"(nothing)"`. The function can no longer tell an empty
string a caller passed on purpose from no string.

Whether that matters depends on the caller. The type checker cannot
tell you, because both versions are type-correct. The truthiness test
is the same trap as `if not target:` on a mutable default in
[Functions](../../Chapters/05_Foundations--Functions.md), and the same
answer applies. Test for the condition you mean. Use `is None` when
you mean "was anything supplied," and truthiness when an empty value
belongs with the missing one.

## 9. Narrowing a local copy of an attribute

> In `narrowing_attribute.py`,
> copy `b.val` into a local variable before the `if` and use the local inside it.
> Replace the `expect()` call with `print(show(box))` for a `Box` named `box`,
> then print `box.val`.
> Explain why the `AttributeError` is gone although `reset()` still runs.

```python
# exercise_9.py

class Box:
    def __init__(self, val: str | None) -> None:
        self.val = val

    def reset(self) -> None:
        self.val = None

def show(b: Box) -> str:
    val = b.val
    if val is not None:
        b.reset()
        return val.upper()
    return "(nothing)"

box = Box("hi")
print(show(box))
#: HI
print(box.val)
#: None
```

`reset()` still runs and still sets the attribute to `None`, as the
second line of output shows. The call cannot change `val`, though.
`val` is a second name for the string `"hi"`, and `reset()` rebinds
`b.val`, not the local. The narrowing of `val` to `str` therefore
holds through the call, and the type checker's verdict matches what
the program does. In the chapter's version the verdict concerns
`b.val`, which the call changes after the test.
