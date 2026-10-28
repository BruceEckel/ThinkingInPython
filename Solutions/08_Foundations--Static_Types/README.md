# Static Types: Solutions

## 1. A third shape satisfying `Drawable`

> In `protocols.py`, add a class `Triangle` with its own `draw()`,
> and pass an instance to `render()` without changing `Drawable` or `render()`.

<details>
<summary>Where to look</summary>

[Structural Typing with Protocols](../../Chapters/08_Foundations--Static_Types.md#structural-typing-with-protocols)
shows `Circle` and `Square` passing as `Drawable` without naming it.
A class qualifies by having the members the `Protocol` declares.
Write `Triangle` with a `draw()` that has the same signature,
and leave `Drawable` and `render()` as they are.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        ...

class Square:
    def draw(self) -> str:
        ...

class Triangle:
    def draw(self) -> str:
        ...

def render(shape: Drawable) -> str:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your `protocols.py` with `render(Triangle())` in it,
and the program prints your triangle's string as a third line.
Renaming `Triangle`'s method to `paint()`, as `Blob` names its method,
makes the check report `invalid-argument-type` on that call.

<details>
<summary>Solution</summary>

If you name `Triangle`'s method `paint()`, as the chapter's `Blob` does,
`ty check` rejects `render(Triangle())` with an `invalid-argument-type`,
reporting that protocol member `draw` is not defined on type `Triangle`.
The call also fails at run time with an `AttributeError`,
because `render()` calls `shape.draw()`.
A protocol matches on names and signatures,
so the solution's method is the `draw() -> str` that `Drawable` declares.

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

Like `Circle` and `Square`, `Triangle` doesn't mention `Drawable`.
It qualifies because it has a `draw() -> str` method,
and that method is all `Drawable` requires.
`Drawable` and `render()` accept a `Triangle` as written.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Removing `# type: ignore` from `area.py`

> In `area.py`, remove the `# type: ignore` comment and run `ty check` on the file.
> Read the error, then restore the comment.

<details>
<summary>Where to look</summary>

[Catching Mistakes](../../Chapters/08_Foundations--Static_Types.md#catching-mistakes)
shows the comment silencing the error on a call that passes `area()` a `str`.
Remove the comment, run `ty check` on the file,
and read which argument and which parameter the diagnostic marks.
Then consider what Python does with the call at run time.

<details>
<summary>Done when</summary>

with the comment removed,
`ty check` reports `invalid-argument-type` on `area.py`,
marking `"3"` with ``Expected `int`, found `Literal["3"]` ``,
and you can say what `area("3", 4)` returns at run time.
With the comment restored, the check passes again.

<details>
<summary>Solution</summary>

```python
def area(width: int, height: int) -> int:
    return width * height

print(area("3", 4))
```

The listing repeats the function and the call from the chapter's `area.py`,
minus its comments.
With the `# type: ignore` comment removed, `ty check` on `area.py` reports:

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

The diagnostic marks the mistake the chapter describes.
At run time the call returns `"3333"`,
because `"3" * 4` is valid string repetition.

In the book, the `# type: ignore` comment on the `area("3", 4)` line lets a deliberately wrong example pass the book's build.
Removing the comment restores the error.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. A second generic function, `last()`

> In `generics.py`, write a second generic function,
> `last[T](items: list[T]) -> T`, that returns the final element,
> and call it on both a `list[int]` and a `list[str]` the way the listing calls `first()`.

<details>
<summary>Where to look</summary>

[Type Parameters](../../Chapters/08_Foundations--Static_Types.md#type-parameters)
shows `first()` with one type parameter `T` shared by the argument and the return type.
Give `last()` the same signature, index from the other end of the list,
and call it on a `list[int]` and a `list[str]`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
def first[T](items: list[T]) -> T:
    ...

def last[T](items: list[T]) -> T:
    ...
```

<details>
<summary>Done when</summary>

your `generics.py` prints the final element of each list and `uv run ty check` passes.
Adding `.upper()` to the `last()` call on the `list[int]` makes the check report `unresolved-attribute`,
as `n.upper()` does for `first()`.

<details>
<summary>Solution</summary>

If you annotate `last()` the way the chapter annotates `first_any()`,
with a bare `list` parameter and an `Any` return,
`ty check` accepts `.upper()` on the result of `last([10, 20, 30])`.
The `.upper()` call then fails at run time with an `AttributeError`:
`'int' object has no attribute 'upper'`.
The solution shares one type parameter `T` between the argument and the return type,
so each call's result keeps the list's element type.

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

A call on a `list[int]` binds `T` to `int` for that call,
and a call on a `list[str]` binds `T` to `str`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A subclass of `NamedTally` still chains through `Self`

> In `self_type.py`, add a subclass of `NamedTally` called `LoudTally` whose `report()` returns the message in all capitals,
> calling `super().report()` first.
> Confirm that `ty check` accepts `.bump().bump().report()` on a `LoudTally` and that the call prints the message in capitals.

<details>
<summary>Where to look</summary>

[The `Self` Return Type](../../Chapters/08_Foundations--Static_Types.md#the-self-type)
explains why `bump()` declares its return type as `Self` instead of a class name.
Subclass `NamedTally`, override `report()` to build on `super().report()`,
and chain `bump()` twice before calling `report()` on the `LoudTally`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import Self

class Tally:
    def __init__(self) -> None:
        ...

    def bump(self) -> Self:
        ...

class NamedTally(Tally):
    def __init__(self, name: str) -> None:
        ...

    def report(self) -> str:
        ...

class LoudTally(NamedTally):
    def report(self) -> str:
        ...
```

<details>
<summary>Done when</summary>

with `t = LoudTally("clicks")`,
`print(t.bump().bump().report())` prints `CLICKS: 2` and `uv run ty check` passes.
Changing `bump()`'s return annotation from `Self` to `Tally` makes the check report `unresolved-attribute` for `report` on the chained call.

<details>
<summary>Solution</summary>

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

**Keep the subclass type through the chain.**
`Tally` declares `bump()` with return type `Self`,
which the type checker resolves to the class of the object receiving the call.
On a `LoudTally`, `Self` means `LoudTally`,
so `t.bump().bump()` type-checks as a `LoudTally`.
The checker therefore accepts `.report()` on the result.
If `bump()`'s return annotation is the concrete type `Tally` instead of `Self`,
the type checker rejects `.report()` on the chained result,
since `report()` first appears on `NamedTally`.

At run time, the `.report()` call resolves to `LoudTally.report()`,
because Python starts method lookup at the object's own class.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. What a missing type parameter default loses

> Run `ty check` on `type_defaults.py` and read what it reports for `reveal_type(words.top())`.
> Remove the `= str` default and run it again.
> The type checker accepts the file either way.
> Say what that means for a bare `Stack` annotation.

<details>
<summary>Where to look</summary>

[Type Parameter Defaults](../../Chapters/08_Foundations--Static_Types.md#type-parameter-defaults)
gives `Stack` a default for `T` so a bare `Stack` annotation means `Stack[str]`.
Use `reveal_type()` from `typing` on `words.top()` with and without the default,
and compare what the checker reports.
Work out what type the checker infers for an expression whose type parameter stays unsolved.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import reveal_type

class Stack[T = str]:
    def __init__(self) -> None:
        ...

    def push(self, item: T) -> None:
        ...

    def top(self) -> T:
        ...
```

<details>
<summary>Done when</summary>

you can name the type that the type checker (`ty`)
reveals for `words.top()` with and without `= str`, and you predict,
before running it, whether `ty check` flags `words.top().no_such_method()` in each version.
Run both versions to confirm your prediction;
your statement about a bare `Stack` follows from the result.

<details>
<summary>Solution</summary>

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

Without the default, `ty` reports `Unknown` and accepts the file.
An unsolved type parameter becomes `Unknown`.
The checker accepts any operation on an `Unknown` value,
so every expression built on that value passes.
`words.top().upper()` passes either way.
With the default removed, so does `words.top().no_such_method()`.

A default turns a bare annotation that accepts every operation into one that checks each operation against `str`.
So give a default to a class whose parameter is usually the same type.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A `Literal` that does not admit `"purple"`

> In `type_aliases.py`,
> call `paint(grid, (2, 3), "purple")` and run `ty check`.
> Read the error, then widen `Color` to admit `"purple"` and confirm the error goes away.

<details>
<summary>Where to look</summary>

In [Naming Types: The `type` Statement](../../Chapters/08_Foundations--Static_Types.md#the-type-statement),
`Color` is an alias for a `Literal` union of strings.
Call `paint()` with `"purple"` and read how the diagnostic names the parameter's type.
Then add the string to the one `type` statement that defines the alias and run the check again.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import Literal

type Coord = tuple[int, int]
type Color = Literal[
    "red", "blue", "green", "yellow", "purple"]
type Grid = dict[Coord, Color]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    ...
```

<details>
<summary>Done when</summary>

before the widening,
`ty check` reports `invalid-argument-type` on the `paint()` call with ``Expected `Color`,
found `Literal["purple"]` ``.
After you add `"purple"` to `Color`,
the check passes and `print(grid)` shows `{(2, 3): 'purple'}`.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from typing import Literal

type Coord = tuple[int, int]
type Color = Literal[
    "red", "blue", "green", "yellow", "purple"]
type Grid = dict[Coord, Color]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "purple")
print(grid)
#: {(2, 3): 'purple'}
```

Before you add `"purple"` to `Color`, the call runs and stores the string,
because the interpreter lets any value through a `Literal` annotation at run time.
`ty check` reports:

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

The diagnostic names the alias rather than the union behind it,
so you follow `Color` to its `type` statement to find the four permitted strings.
The alias also keeps the message short and puts the allowed set in one place to change.

**Widen the set at its definition.**
Adding `"purple"` to the alias removes the error at every call.
`grid[cell] = color` works as written.
`Grid`'s values are `Color`s,
so the widened alias admits `"purple"` in the grid as well as in the parameter.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. Widening `add_square()` to `Sequence[Shape]`

> In `variance.py`, change `add_square()`'s parameter annotation to `Sequence[Shape]` and uncomment the call.
> Explain why the type checker now accepts the call and why `shapes.append(...)` no longer type-checks.

<details>
<summary>Where to look</summary>

[Variance](../../Chapters/08_Foundations--Static_Types.md#variance)
shows the checker refusing a `list[Circle]` where the parameter requires a `list[Shape]`.
`variance.py` imports `Sequence` from `collections.abc` for `count()`.
Compare which operations `Sequence` offers with those of `list`.
The answer to both questions follows from whether you can write to the container.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

class Square(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    ...

def add_square(shapes: Sequence[Shape]) -> None:
    # ty: "Sequence[Shape]" has no attribute "append":
    # shapes.append(Square())
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on `variance.py` with `add_square(circles)` uncommented,
and a body that still calls `shapes.append(Square())` makes it report `unresolved-attribute` on `Sequence[Shape]`.
Your explanation names the variance of `Sequence` and of `list`.

<details>
<summary>Solution</summary>

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

**Widen what the parameter accepts.**
The type checker accepts the call because `Sequence` is covariant in its element type.
A `Sequence[Shape]` declares that you can read `Shape`s out of it,
not that you can put them in.
Every `Circle` is a `Shape`, so a `list[Circle]` meets that requirement.
A `list[Shape]` parameter refuses the same argument because `list` is invariant.

**Give up the write operations.**
`shapes.append(...)` draws a diagnostic for the reason the widening works.
`Sequence` is a read-only container type, so it has no `append()`.
The diagnostic is therefore `unresolved-attribute` rather than an argument-type error.
The type checker does not say "you may not append a `Square` here."
It says the type you declared has no such operation.

The one edit shows both sides of variance.
A writable container is invariant.
A read-only type is covariant.
The practical rule follows:
annotate a parameter with the weakest type the body needs,
because each caller's argument must supply every capability you declare.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Truthiness in place of `is not None`

> In `narrowing.py`, replace `if text is not None:` with `if text:` and run `ty check`.
> Explain why the empty string now takes the other branch even though the type checker accepts either version.

<details>
<summary>Where to look</summary>

[Narrowing](../../Chapters/08_Foundations--Static_Types.md#narrowing)
shows `is not None` removing `None` from a `str | None` before `shout()` calls `.upper()`.
A truthiness test narrows the same way, so the checker accepts it.
Call the function with `None`, a normal string, and the empty string,
and compare which values each test sends to which branch.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
def shout(text: str | None) -> str:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on both versions of `narrowing.py`,
and `shout("")` prints `(nothing)` with `if text:` and an empty line with `is not None`,
while `shout("hi")` and `shout(None)` print the same in both.
You can name the values each test sends to the fallback.

<details>
<summary>Solution</summary>

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

**Narrow out the missing value.**
The type checker accepts either version, because truthiness narrows too.
`None` is falsy, so inside `if text:` the type checker rules out `None` the same as `is not None` does.
`.upper()` is therefore safe in both versions.

**Send empty values to the fallback.**
The change is in which values reach which branch.
`is not None` tests one condition, whether the value is missing.
`if text:` tests whether the value is missing or empty.
The function now treats an empty string the same as a missing value,
including one a caller passed on purpose.

Whether that matters depends on the caller.
The type checker cannot tell you, because both versions are type-correct.
The truthiness test is the same trap as [`if not target:` on a mutable default](../../Chapters/05_Foundations--Functions.md#sentinel-values).
The same answer applies: test for the condition you mean.
Use `is None` when you mean "was anything supplied,"
and truthiness when an empty value belongs with the missing one.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Narrowing a local copy of an attribute

> In `narrowing_attribute.py`,
> copy `b.val` into a local variable before the `if` and use the local inside it.
> Replace the `expect()` call with `print(show(box))` for a `Box` named `box`,
> then print `box.val`.
> Explain why the `AttributeError` disappears although `reset()` still runs.

<details>
<summary>Where to look</summary>

[Narrowing](../../Chapters/08_Foundations--Static_Types.md#narrowing)
shows the checker keeping a narrowing of `b.val` although `reset()` can change that attribute.
Bind `b.val` to a local name before the `if`,
so the narrowed expression is a variable instead of an attribute.
Then consider which name `reset()` can rebind.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
class Box:
    def __init__(self, val: str | None) -> None:
        ...

    def reset(self) -> None:
        ...

def show(b: Box) -> str:
    ...
```

<details>
<summary>Done when</summary>

for `box = Box("hi")`, `print(show(box))` prints `HI`,
`print(box.val)` prints `None`,
and `uv run ty check` passes on `narrowing_attribute.py`.
Calling `upper()` on `b.val` inside the `if` instead makes the check report `unresolved-attribute`.

<details>
<summary>Solution</summary>

If you copy `b.val` into `val` and test `val` but still call `b.val.upper()`,
the test narrows the local and leaves the attribute at `str | None`.
`ty check` then reports an `unresolved-attribute` on `b.val.upper()`.
The call also fails at run time with an `AttributeError`,
because `reset()` has set the attribute to `None`.
The solution calls `upper()` on the local, the name the test narrowed.

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

**Narrow a name the function owns.**
`reset()` still runs and still sets the attribute to `None`,
as the second line of output shows.
The call leaves `val` as it was, though.
`val` is a second name for the string `"hi"`.
`reset()` rebinds `b.val`, not the local.
The narrowing of `val` to `str` therefore holds through the call,
and the type checker's verdict matches what the program does.
In the chapter's version the verdict concerns `b.val`,
which the call sets to `None` after the test,
so the verdict is wrong by the time `upper()` runs.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. A `Final` tuple

> In `final_constants.py`, annotate `HISTORY` as `Final[tuple[str, ...]]`,
> start it as an empty tuple, and run `ty check`.
> Read what the type checker reports for the `append()` call.
> Then change the listing so `HISTORY` holds `"first"`,
> and explain why the entry must go into the definition of `HISTORY`.

<details>
<summary>Where to look</summary>

[Constants with Final](../../Chapters/08_Foundations--Static_Types.md#constants-with-final)
separates rebinding a name from changing the object the name holds.
A tuple has no `append()`, and `Final` forbids rebinding `HISTORY`,
so consider when a tuple receives its contents.

<details>
<summary>Done when</summary>

with `HISTORY` empty,
`ty check` reports `unresolved-attribute` for the `append()` call,
and your final `final_constants.py` passes the check and prints `3 hello ('first',)`.
Adding `"first"` later with `HISTORY = HISTORY + ("first",)` instead draws `invalid-assignment`.

<details>
<summary>Solution</summary>

If you keep the `append()` call, `ty check` reports `unresolved-attribute`,
since a tuple has no `append()`.
The call also fails at run time with an `AttributeError`.
Rebuilding the tuple with `HISTORY = HISTORY + ("first",)` runs,
but the type checker rejects it as a reassignment of a `Final` name.
The solution puts the entry into the tuple at the definition of `HISTORY`.

```python
# exercise_10.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"
HISTORY: Final[tuple[str, ...]] = ("first",)

# ty: tuple has no attribute "append":
# HISTORY.append("second")
# ty: cannot assign to final name "HISTORY":
# HISTORY = HISTORY + ("second",)

print(MAX_RETRIES, GREETING, HISTORY)
#: 3 hello ('first',)
```

**Freeze the name and the contents.**
On a list, `Final` forbids rebinding the name.
Any code holding a reference to the list can still change its contents.
On a tuple, the name and the contents both stay as the definition sets them.
`Final` stops a rebinding,
and the tuple type has no method that changes its contents.
The definition is therefore the one place to put a value into the constant.
A reader looks for the value there too.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
