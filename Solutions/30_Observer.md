# Observer: Solutions

## 1. A class decorator that traces every method

```python
# exercise_1.py
from collections.abc import Callable
from functools import wraps
from typing import Any

def trace_all(cls: type) -> type:
    for name, value in vars(cls).copy().items():
        if callable(value) and not name.startswith("__"):
            def make_wrapper(
                func: Callable, name: str = name
            ) -> Callable:
                @wraps(func)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    print(f"-> {name}")
                    result = func(*args, **kwargs)
                    print(f"<- {name}")
                    return result
                return wrapper
            setattr(cls, name, make_wrapper(value))
    return cls

@trace_all
class Greeter:
    def hello(self, name: str) -> str:
        return f"Hello, {name}"

    def bye(self) -> str:
        return "Bye"

g = Greeter()
print(g.hello("Bob"))
#: -> hello
#: <- hello
#: Hello, Bob
```

`trace_all` runs once, at class-definition time, over
`vars(cls)`, the class's own namespace, wrapping every plain callable
that is not a dunder. `make_wrapper` captures each method's `name` as
a default argument (`name: str = name`), which freezes that
particular loop iteration's value; without it, every wrapper would
share the loop variable's final value instead of its own method's
name, the classic late-binding closure trap. This is
[Decorating Classes](14_Decorators.md#decorating-classes)'s
`register` idea taken further: instead of only recording the class,
this decorator reaches inside it and rewrites every method.

## 2. A minimal Observer-Observable pair

```python
# exercise_2.py
from collections.abc import Callable
from typing import Any

class Observable:
    def __init__(self) -> None:
        self._observers: list[Callable] = []

    def subscribe(self, observer: Callable) -> None:
        self._observers.append(observer)

    def notify(self, *args: Any) -> None:
        for obs in self._observers:
            obs(*args)

calls: list[tuple[str, int]] = []
observable = Observable()
observable.subscribe(lambda v: calls.append(("A", v)))
observable.subscribe(lambda v: calls.append(("B", v)))
observable.notify(42)
print(calls)
#: [('A', 42), ('B', 42)]
```

There is no separate `Observer` class at all, the same design
`observers.py` already uses. Any callable, here two `lambda`s, is an
observer. `subscribe()` collects them in a list, and `notify()` calls
each one in turn with whatever arguments it was given, so every
subscribed observer sees the same update, in subscription order.

## 3. Turning `box_observer.py` into a flood-fill game

```python
# exercise_3.py
from typing import Final

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]
type Grid = dict[Coord, str]

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

class FloodGame:
    "Flood-fill game: grow a patch from the origin to fill the board."
    def __init__(self, size: int, origin: Coord = (0, 0)) -> None:
        self.size = size
        self.grid = new_grid(size)
        self.origin = origin
        self.clicks = 0
        self.owned = self._flood(self.grid[origin])

    def _flood(self, color: str) -> set[Coord]:
        "Every cell reachable from origin through same-colored cells."
        seen: set[Coord] = set()
        stack = [self.origin]
        while stack:
            cell = stack.pop()
            if cell in seen or self.grid.get(cell) != color:
                continue
            seen.add(cell)
            for other in self.grid:
                if adjacent(cell, other) and other not in seen:
                    stack.append(other)
        return seen

    def click(self, cell: Coord) -> bool:
        "Recolor the owned patch to the clicked cell's color."
        new_color = self.grid[cell]
        if new_color == self.grid[self.origin]:
            return False  # No-op: already this color
        for c in self.owned:
            self.grid[c] = new_color
        self.owned = self._flood(new_color)  # Absorb new neighbors
        self.clicks += 1
        return True

    def is_complete(self) -> bool:
        return len(self.owned) == self.size * self.size

game = FloodGame(4)
while not game.is_complete():
    remaining = [c for c in game.grid if c not in game.owned]
    game.click(remaining[0])
print("solved in", game.clicks, "clicks")
#: solved in 6 clicks
```

`_flood()` is a plain graph search (depth-first, using a stack)
starting from `origin`, walking to every neighbor `adjacent()` already
knows how to test, as long as that neighbor is still the same color.
It reuses `new_grid()` and `adjacent()` from `box_observer.py`
unchanged. `click()` is the game move: repaint every cell in the
*currently owned* patch to the clicked cell's color, then re-run
`_flood()` to discover which previously-unowned neighbors now match
that new color and have joined the patch. `game.clicks` gives the
single-player scoring the exercise asks for, "how many clicks to turn
the field into one color"; two-player competition follows the same
`click()` method, alternating whose turn supplies the next color, with
whoever's move leaves the larger owned patch after a fixed number of
rounds. `FloodGame` inheriting from `Observable`, the same as
`BoxModel`, and calling `self.notify(self.grid)` at the end of a
successful `click()` would let `box_view.py`'s existing view repaint
after every move with no changes to the view itself.
