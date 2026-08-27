# Observer: Solutions

## 1. A minimal Observer-Observable pair

```python
# exercise_1.py
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

No separate `Observer` class exists at all, the same design
`observers.py` already uses. Any callable, here two `lambda`s, is an
observer. `subscribe()` collects them in a list, and `notify()` calls
each one in turn with whatever arguments it was given, so every
subscribed observer sees the same update, in subscription order.

## 2. Turning `box_observer.py` into a flood-fill game

```python
# exercise_2.py
from typing import Final

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]
type Grid = dict[Coord, str]

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return (a != b and abs(a[0] - b[0]) <= 1
            and abs(a[1] - b[1]) <= 1)

class FloodGame:
    ("Flood-fill game: grow a patch "
     "from the origin to fill the board.")
    def __init__(self, size: int,
                 origin: Coord = (0, 0)) -> None:
        self.size = size
        self.grid = new_grid(size)
        self.origin = origin
        self.clicks = 0
        self.owned = self._flood(self.grid[origin])

    def _flood(self, color: str) -> set[Coord]:
        ("Every cell reachable from origin "
         "through same-colored cells.")
        seen: set[Coord] = set()
        stack = [self.origin]
        while stack:
            cell = stack.pop()
            if cell in seen or self.grid.get(cell) != color:
                continue
            seen.add(cell)
            for other in self.grid:
                if (adjacent(cell, other)
                    and other not in seen):
                    stack.append(other)
        return seen

    def click(self, cell: Coord) -> bool:
        ("Recolor the owned patch "
         "to the clicked cell's color.")
        new_color = self.grid[cell]
        if new_color == self.grid[self.origin]:
            return False  # No-op: already this color
        for c in self.owned:
            self.grid[c] = new_color
        # Absorb new neighbors
        self.owned = self._flood(new_color)
        self.clicks += 1
        return True

    def is_complete(self) -> bool:
        return len(self.owned) == self.size * self.size

game = FloodGame(4)
while not game.is_complete():
    remaining = [
        c for c in game.grid if c not in game.owned]
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
rounds. `FloodGame` inheriting from `Observable[Grid]`, the same as
`BoxModel`, and calling `self.notify(self.grid)` at the end of a
successful `click()` lets `box_view.py`'s existing view repaint
after every move with no changes to the view itself.

## 3. A `notify()` that survives a failing observer

```python
# exercise_3.py
from collections.abc import Callable

type Observer[T] = Callable[[T], None]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def subscribe(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def notify(self, data: T) -> None:
        failures: list[Exception] = []
        for observer in list(self._observers):
            try:
                observer(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "observer failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

obs = Observable[int]()
obs.subscribe(broken)
obs.subscribe(received.append)
try:
    obs.notify(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
```

```python
# test_resilient_notify.py
import pytest
from exercise_3 import Observable

def test_later_observer_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    obs = Observable[int]()
    obs.subscribe(broken)
    obs.subscribe(received.append)
    with pytest.raises(ExceptionGroup):
        obs.notify(1)
    assert received == [1]
```

The loop catches each failure and keeps going, so subscription order
stops deciding who hears the change. Collecting the exceptions rather
than discarding them is the other half: an observer that fails
silently is worse than one that stops the loop, because nothing
reports that a notification was lost.

`ExceptionGroup` is the right container because more than one
observer can fail on a single notification, and the caller needs all
of them, not the first. `except*` then lets a caller handle one kind
of failure and re-raise the rest, which a plain `except` on a single
re-raised exception cannot do.

Catching bare `Exception` here is deliberate: `notify()` has no idea
what its observers do, so it cannot name their failure modes. It
still lets `BaseException` through, so a `KeyboardInterrupt` or an
`asyncio.CancelledError` passing through an observer stops the
notification instead of being collected as data.

## 4. The same rescue, for the async fan-out

```python
# exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver[T] = Callable[[T], Awaitable[None]]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver[T]] = []

    def subscribe(self, observer: AsyncObserver[T]) -> None:
        self._observers.append(observer)

    async def notify(self, data: T) -> None:
        results = await asyncio.gather(
            *(obs(data) for obs in self._observers),
            return_exceptions=True)
        failures = [
            r for r in results if isinstance(r, Exception)]
        if failures:
            raise ExceptionGroup(
                "observer failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    obs = Observable[int]()
    obs.subscribe(broken)
    obs.subscribe(record)
    try:
        await obs.notify(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
```

```python
# test_async_resilient_notify.py
import asyncio
import pytest
from exercise_4 import Observable

def test_later_observer_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        obs = Observable[int]()
        obs.subscribe(broken)
        obs.subscribe(record)
        with pytest.raises(ExceptionGroup):
            await obs.notify(1)

    asyncio.run(run())
    assert received == [1]
```

`return_exceptions=True` changes `gather()` from "re-raise the first
failure immediately" to "run everything and hand back a list." That
one keyword does what the synchronous version needed a `try` inside a
loop to do, because `gather()` is already the loop.

The results come back in argument order, so the list is a record of
which observer produced what. This version only needs the failures, so
it filters with `isinstance(r, Exception)` and drops the `None`s that
successful observers returned.

The exception filter uses `Exception`, not `BaseException`, for the
reason exercise 3 gives, and here it also matters that
`asyncio.CancelledError` derives from `BaseException`:
`return_exceptions=True` still returns a cancellation among the
results, and treating it as an ordinary observer failure would swallow
a cancellation the event loop meant to propagate.

The synchronous and asynchronous versions now answer the same
question, and both end in an `ExceptionGroup`. The difference is only
where the loop lives: written by hand in one, supplied by `gather()`
in the other.
