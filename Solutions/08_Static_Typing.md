# Static Typing: Solutions

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

The checker pinpoints the mistake the chapter describes: `"3"`
is a `str`, not an `int`, so it violates `width: int`, even though the
call runs without error at runtime (`"3" * 4` is valid string
repetition). The `# type: ignore` comment that was on this line in the
book existed only to let this deliberately-wrong example pass the
book's own build; removing it restores the error `ty` is meant to
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
whatever `list[T]` is passed in. Calling it on a `list[int]` makes `T`
`int` for that call, and on a `list[str]` makes `T` `str`, exactly as
`first()` does, so the checker knows `last([10, 20, 30])` returns an
`int` and `last(["a", "b", "c"])` returns a `str`.

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

`bump()` is declared on `Tally` with return type `Self`, which the
checker resolves to whatever class `bump()` was actually called on.
Called on a `LoudTally`, `Self` means `LoudTally`, so
`t.bump().bump()` type-checks as a `LoudTally`, and `.report()` is
available on it, resolving to `LoudTally.report()` since Python always
starts method lookup from the actual (most derived) class. If
`bump()` is declared to return the fixed type `Tally` instead of
`Self`, the checker rejects `.report()` on the chained result,
since plain `Tally` has no `report()` method.

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
`reveal_type(words.top())`. Remove the default and it reports
`Unknown`, and `ty` still finds no errors in the file. That is the
lesson: an unsolved type parameter does not fail the check, it
switches the check off for every expression downstream of it.
`words.top().upper()` passes either way, and so would
`words.top().no_such_method()`. A default converts a silently
unchecked annotation into a checked one, which is why it earns its
place on a class whose parameter has one common answer.

## 6. A `Literal` that does not admit `"purple"`

```python
# exercise_6.py
from typing import Literal

type Coord = tuple[int, int]
type Grid = dict[Coord, str]
type Color = Literal["red", "blue", "green", "yellow", "purple"]

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

The expected type is spelled out in full, which is the practical
argument for naming the union once as `Color` rather than repeating
the four strings in every signature: the error message stays readable
and the allowed set has one place to change. Adding `"purple"` to that
one alias silences the error everywhere, and `grid[cell] = color`
needed no change, since `Grid`'s values are plain `str` and every
`Color` is one.
