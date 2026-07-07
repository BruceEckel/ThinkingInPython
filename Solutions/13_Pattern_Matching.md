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
(`[_, *_]`), or the general one would match first and the specific
cases would never run. `Point()` matches any `Point` instance without
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
`Rectangle` value would fall through both `case`s and reach `case _`.
`assert_never()` demands its argument have type `Never`, meaning "this
code is unreachable," but the checker now knows `shape` could
genuinely be a `Rectangle` at that point, so the two types disagree
and it reports an error. This is exactly the safety net the chapter
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
