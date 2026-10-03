# Observer: Solutions

## 1. A minimal broadcaster-responder pair

> Create a minimal *Observer* design of your own,
> without looking at `broadcaster.py`:
> the smallest `Broadcaster` that lets you connect callables,
> then notifies them.
> Demonstrate it by connecting several responders and causing one change that updates them all.

<details>
<summary>Where to look</summary>

The design is the one [The Pythonic Observer](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer) describes:
a list of callables, one method that appends to it,
and one that calls each entry with the same arguments.
Any callable is a responder, a `lambda` included,
so the demonstration needs no observer class.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Callable
from typing import Any

class Broadcaster:
    def __init__(self) -> None:
        ...

    def connect(self, responder: Callable) -> None:
        ...

    def announce(self, *args: Any) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from collections.abc import Callable
from typing import Any

class Broadcaster:
    def __init__(self) -> None:
        self._responders: list[Callable] = []

    def connect(self, responder: Callable) -> None:
        self._responders.append(responder)

    def announce(self, *args: Any) -> None:
        for responder in self._responders:
            responder(*args)

calls: list[tuple[str, int]] = []
broadcaster = Broadcaster()
broadcaster.connect(lambda v: calls.append(("A", v)))
broadcaster.connect(lambda v: calls.append(("B", v)))
broadcaster.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
```

**Collect the responders.** Like `broadcaster.py`, this solution has no separate `Observer` class at
all. Any callable, here two `lambda`s, is a responder. `connect()`
collects them in a list.

**Deliver one update to every responder.** `announce()` then hands its own arguments to
each one in turn, so every connected responder sees the same update,
in connection order.

</details>
</details>
</details>

## 2. The pull model, twice

> Rewrite the classic listings to use the pull model:
> `Display.update()` reads `subject.celsius` instead of `arg`.
> A `Display` that narrows its `subject` parameter to `Thermometer` no longer satisfies `Observer[float]`,
> so make it type-check two ways:
> once with a runtime `isinstance()` check inside `update()`,
> and once with an `Observer[S, T]` protocol whose first parameter is the subject type,
> which `Subject` supplies as `Self`.
> Say what each version adds.

<details>
<summary>Where to look</summary>

[Push or Pull](../../Chapters/30_Patterns--Observer.md#push-or-pull) describes the pull model.
The type problem is that a parameter is contravariant:
an `update()` that narrows `subject` to `Thermometer` accepts less than `Observer[float]` requires.
The first version keeps the protocol and narrows at runtime with `isinstance()`.
The second gives the protocol a second type parameter for the subject,
and `Subject.attach()` asks for an `Observer[Self, T]`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2_narrowing.py
from typing import Protocol

class Observer[T](Protocol):
    def update(
        self, subject: Subject[T], arg: T
    ) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        ...

    def attach(self, observer: Observer[T]) -> None:
        ...

    def notify(self, arg: T) -> None:
        ...

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        ...

    @property
    def celsius(self) -> float:
        ...

    @celsius.setter
    def celsius(self, value: float) -> None:
        ...

class Display:
    def update(
        self, subject: Subject[float], arg: float
    ) -> None:
        ...
```

```python
# The shape of exercise_2_generic.py
from typing import Protocol, Self

class Observer[S, T](Protocol):
    def update(self, subject: S, arg: T) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        ...

    def attach(
        self, observer: Observer[Self, T]
    ) -> None:
        ...

    def notify(self, arg: T) -> None:
        ...

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        ...

    @property
    def celsius(self) -> float:
        ...

    @celsius.setter
    def celsius(self, value: float) -> None:
        ...

class Display:
    def update(
        self, subject: Thermometer, arg: float
    ) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you declare `subject: Thermometer` in `Display.update()` and keep the classic `Observer[T]`,
the program still prints `display: 25C`,
but the type checker rejects `t.attach(Display())`.
A parameter is contravariant,
so an `update()` that accepts only a `Thermometer` cannot stand in for one that accepts any `Subject[float]`.
Both versions below keep the read of `subject.celsius` and repair the type,
the first by widening the parameter again and the second by changing the protocol.

**Declare the widest subject type.** The protocol here is `classic_observer.py`'s, unchanged.
`update()` declares the widest type `attach()` can hand it,
`Subject[float]`, and narrows that to a `Thermometer` before reading
`celsius`:

```python
# exercise_2_narrowing.py
from typing import Protocol

class Observer[T](Protocol):
    def update(
        self, subject: Subject[T], arg: T
    ) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def attach(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)

class Display:
    def update(
        self, subject: Subject[float], arg: float
    ) -> None:
        assert isinstance(subject, Thermometer)
        print(f"display: {subject.celsius}C")

t = Thermometer(20.0)
t.attach(Display())
t.celsius = 25
#: display: 25C
```

**Narrow the subject at runtime.** The `assert` is the cost. It runs on every notification, and it states
a requirement the protocol cannot: this `Display` works for a
`Thermometer` and fails on any other `Subject[float]`, at the moment
of the first notification rather than at the `attach()` call the type
checker reads.

**Let the subject supply its own type.** The second version moves the subject's type into the protocol.
`Observer[S, T]` takes the subject's type as a parameter, and `Subject` supplies its
own type with `Self`, so `Thermometer.attach()` asks for an
`Observer[Thermometer, float]`:

```python
# exercise_2_generic.py
from typing import Protocol, Self

class Observer[S, T](Protocol):
    def update(self, subject: S, arg: T) -> None: ...

class Subject[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[Self, T]] = []

    def attach(
        self, observer: Observer[Self, T]
    ) -> None:
        self._observers.append(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)

class Display:
    def update(
        self, subject: Thermometer, arg: float
    ) -> None:
        print(f"display: {subject.celsius}C")

t = Thermometer(20.0)
t.attach(Display())
t.celsius = 25
#: display: 25C
```

**Name the subject the observer reads.** `Display.update()` now declares `subject: Thermometer` and
`t.attach(Display())` type-checks. The cost is at the other end: each observer's type names
the subject it watches, so a display written for a `Thermometer`
cannot attach to a different `Subject[float]`. A parameter is
contravariant, so an observer that declares the wider `Subject[float]`
still attaches to any `Subject[float]`, and an observer that reads `celsius` is
the one that gives up that freedom.

Both versions print the same line, and neither needs `arg`. That is
pull's bargain: the subject decides nothing about what its observers
read, and each observer pays by knowing what it is watching.

</details>
</details>
</details>

## 3. An `announce()` that survives a failing responder

> Make `Broadcaster.announce()` survive a responder that raises an exception:
> every other responder is still notified,
> and `announce()` re-raises the failures afterward, together,
> as an [`ExceptionGroup`](../../Chapters/19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
> (which you build yourself here: `raise ExceptionGroup("message", failures)`).
> Write a test in which the first responder raises an exception and the second still records its notification.

<details>
<summary>Where to look</summary>

[Raising an Exception](../../Chapters/30_Patterns--Observer.md#raising-an-exception) shows one failing responder stopping the loop in `announce()`.
Put a `try` inside the loop, append each exception to a list,
and after the loop raise an `ExceptionGroup` when the list is not empty.
The test catches it with `pytest.raises(ExceptionGroup)`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(self, responder: Responder[T]) -> None:
        ...

    def announce(self, data: T) -> None:
        ...

def broken(data: int) -> None:
    ...
```

<details>
<summary>Solution</summary>

If you catch each exception and move on without keeping it,
every responder runs, but `announce()` returns normally.
The demo's `except*` block does not run, so the script prints nothing,
and the test's `pytest.raises(ExceptionGroup)` fails with "DID NOT RAISE".
The solution keeps each exception in a list and raises the list as one `ExceptionGroup` once the loop ends.

```python
# exercise_3.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        failures: list[Exception] = []
        for responder in list(self._responders):
            try:
                responder(data)
            except Exception as e:
                failures.append(e)
        if failures:
            raise ExceptionGroup(
                "responder failures", failures)

received: list[int] = []

def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

broadcaster = Broadcaster[int]()
broadcaster.connect(broken)
broadcaster.connect(received.append)
try:
    broadcaster.announce(7)
except* RuntimeError as group:
    print(len(group.exceptions), received)
#: 1 [7]
```

```python
# test_resilient_announce.py
import pytest
from exercise_3 import Broadcaster

def test_later_responder_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    broadcaster = Broadcaster[int]()
    broadcaster.connect(broken)
    broadcaster.connect(received.append)
    with pytest.raises(ExceptionGroup):
        broadcaster.announce(1)
    assert received == [1]
```

**Keep the loop going past a failure.** The loop catches each failure and keeps going, so connection order
stops deciding who hears the change.

**Catch any ordinary failure.** Catching bare `Exception` here is deliberate: `announce()` has no idea
what its responders do, so it cannot name their failure modes. Catching
`Exception` still lets `BaseException` through, so a
`KeyboardInterrupt` or an `asyncio.CancelledError` passing through a
responder stops the notification instead of joining `failures`.

**Record each failure.** Collecting the exceptions rather
than discarding them matters as much as catching them: a responder that fails silently
is worse than one that stops the loop, because nothing reports the
failure.

**Report every failure together.** `ExceptionGroup` is the right container because more than one responder
can fail on a single notification, and the caller needs every failure,
not the first. `except*` then lets a caller handle one kind of failure
and re-raise the rest, something a plain `except` on a single
re-raised exception cannot do.

</details>
</details>
</details>

## 4. The same rescue, for the async fan-out

> Redo exercise 3 for `async_broadcaster.py`.
> Make `announce()` use `gather(*coros, return_exceptions=True)`,
> separate the returned exceptions from the successes,
> and raise them together as an `ExceptionGroup`.
> Write a test in which the first responder raises an exception and the second still records its notification.

<details>
<summary>Where to look</summary>

[A Failing Responder Orphans the Rest](../../Chapters/30_Patterns--Observer.md#a-failing-responder-orphans-the-rest) shows `gather()` abandoning the other coroutines on the first failure.
With `return_exceptions=True`, `gather()` returns every result, exceptions among them.
Keep the results that are `Exception` instances and raise them as one `ExceptionGroup`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(
        self, responder: AsyncResponder[T]
    ) -> None:
        ...

    async def announce(self, data: T) -> None:
        ...

async def broken(data: int) -> None:
    ...

async def record(data: int) -> None:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

If you leave out `return_exceptions=True`,
`gather()` re-raises the first failure as a bare `RuntimeError`,
and the test fails because `pytest.raises(ExceptionGroup)` does not match it.
The demo still prints `1 [7]`:
`except*` wraps a bare exception in a group,
and `record()` finishes before `main()` resumes.
A slower responder keeps running with nothing awaiting it, as [A Failing Responder Orphans the Rest](../../Chapters/30_Patterns--Observer.md#a-failing-responder-orphans-the-rest) shows,
so the solution passes the keyword and `gather()` waits for every responder.

```python
# exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[AsyncResponder[T]] = []

    def connect(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.append(responder)

    async def announce(self, data: T) -> None:
        results = await asyncio.gather(
            *(responder(data)
              for responder in self._responders),
            return_exceptions=True)
        failures = [
            r for r in results if isinstance(r, Exception)]
        if failures:
            raise ExceptionGroup(
                "responder failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    broadcaster = Broadcaster[int]()
    broadcaster.connect(broken)
    broadcaster.connect(record)
    try:
        await broadcaster.announce(7)
    except* RuntimeError as group:
        print(len(group.exceptions), received)

asyncio.run(main())
#: 1 [7]
```

```python
# test_async_resilient_announce.py
import asyncio
import pytest
from exercise_4 import Broadcaster

def test_later_responder_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        broadcaster = Broadcaster[int]()
        broadcaster.connect(broken)
        broadcaster.connect(record)
        with pytest.raises(ExceptionGroup):
            await broadcaster.announce(1)

    asyncio.run(run())
    assert received == [1]
```

**Run every responder to completion.** `return_exceptions=True` changes `gather()` from "re-raise the first
failure immediately" to "run everything and hand back a list." That
one keyword does what the synchronous version needed a `try` inside a
loop to do, because `gather()` is already the loop.

**Pick out the failures.** The results come back in argument order, so the list is a record of
which responder produced what. This version needs the failures alone,
so its comprehension keeps each result for which
`isinstance(r, Exception)` is true. A successful responder returned
`None`, which fails that test and stays out of `failures`.

**Keep cancellation out of the failures.** The exception filter uses `Exception`, not `BaseException`, for the
reason exercise 3 gives, and for a second reason here.
If another task cancels the awaiting task while `gather()` waits,
`gather()` cancels every responder,
and `asyncio.CancelledError` reaches the awaiting task with either filter,
since `announce()` gets no results to filter.
The cancellation that `return_exceptions=True` does return comes from a responder that cancels its own task,
and the `Exception` filter drops it from `failures` because `asyncio.CancelledError` derives from `BaseException`.
A `BaseException` filter would put that cancellation in `failures`,
which `ExceptionGroup` cannot hold:
`ty` reports an `invalid-argument-type` at the constructor call,
and at runtime `announce()` raises a `TypeError` ("Cannot nest BaseExceptions in an ExceptionGroup")
in place of the responder failures.
The `Exception` filter is the right one:
it reports every ordinary failure,
at the cost of treating a responder that cancelled itself as one that finished.

The synchronous and asynchronous versions now answer the same
question, and both end in an `ExceptionGroup`. The difference is only
where the loop lives: written by hand in the synchronous version,
supplied by `gather()` in the async one.

</details>
</details>
</details>

## 5. Failures returned as values

> Redo exercise 3 with each failure returned as a value instead of raised as an exception.
> Each responder returns a [`Result`](../../Chapters/42_Functional--Error_Handling.md#a-result-type)
> from `utils/result.py`,
> and `announce()` returns the `Err` values it collects.
> Write an adapter that lets a responder returning `None`,
> such as `received.append`, be connected.
> Write a test in which the first responder fails and the second still records its notification.

<details>
<summary>Where to look</summary>

Change the responder type to return a [`Result`](../../Chapters/42_Functional--Error_Handling.md#a-result-type),
and make `announce()` a comprehension that keeps each result that is an `Err`.
The adapter takes a `None`-returning callable
and returns a responder that calls it and answers `Ok(None)`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Callable
from result import Err, Ok, Result

type Responder[T] = Callable[[T], Result[None, str]]

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(self, responder: Responder[T]) -> None:
        ...

    def announce(self, data: T) -> list[Err[str]]:
        ...

def succeeds[T](
    action: Callable[[T], None],
) -> Responder[T]:
    ...

def checked(data: int) -> Result[None, str]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from collections.abc import Callable
from result import Err, Ok, Result

type Responder[T] = Callable[[T], Result[None, str]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> list[Err[str]]:
        return [
            result
            for responder in list(self._responders)
            if isinstance(result := responder(data), Err)
        ]

def succeeds[T](
    action: Callable[[T], None],
) -> Responder[T]:
    def responder(data: T) -> Result[None, str]:
        action(data)
        return Ok(None)
    return responder

def checked(data: int) -> Result[None, str]:
    if data < 0:
        return Err(f"cannot handle {data}")
    return Ok(None)

received: list[int] = []
broadcaster = Broadcaster[int]()
broadcaster.connect(checked)
broadcaster.connect(succeeds(received.append))
print(broadcaster.announce(7), received)
#: [] [7]
print(broadcaster.announce(-1), received)
#: [Err(error='cannot handle -1')] [7, -1]
```

```python
# test_result_announce.py
from exercise_5 import Broadcaster, succeeds
from result import Err, Result

def test_later_responder_runs_after_an_err() -> None:
    received: list[int] = []

    def broken(data: int) -> Result[None, str]:
        return Err("boom")

    broadcaster = Broadcaster[int]()
    broadcaster.connect(broken)
    broadcaster.connect(succeeds(received.append))
    assert broadcaster.announce(1) == [Err("boom")]
    assert received == [1]
```

**Collect the failures as values.** No responder raises an exception, so `announce()` needs no `try`.
It calls every responder and keeps each result that is an `Err`.
The caller receives the failures as an ordinary list
and decides what to do with them,
where exercise 3's caller had to catch an `ExceptionGroup`.
An empty list means every responder succeeded.

**Adapt a `None`-returning callable.** The type change reaches every responder.
`received.append` returns `None`,
so the type checker rejects `broadcaster.connect(received.append)`:
a `Responder[int]` must return a `Result`.
`succeeds()` adapts any `None`-returning callable
by calling it and returning `Ok(None)`.
The adapter assumes the wrapped callable cannot fail;
if the callable raises an exception anyway,
that exception leaves `announce()` as it did in the chapter's version.

Returning errors as values works when you write the responders.
For a broadcaster that accepts arbitrary callables,
exercise 3's catch-and-collect protects the loop from code you did not write.

</details>
</details>
</details>

## 6. Turning `box_observer.py` into a flood-fill game

> Turn `box_observer.py` into a simple game:
> you own the contiguous patch of same-colored squares containing the top-left corner,
> and selecting any square recolors your patch to that square's color,
> absorbing neighbors that now match.
> Write the neighbor test yourself, and count diagonal squares as neighbors.
> Track the moves it takes to make the whole field one color.
> For competition, alternate turns between players.

<details>
<summary>Where to look</summary>

Keep `Color` and `new_grid()` from [The Model](../../Chapters/30_Patterns--Observer.md#the-model).
Your patch is the set of cells a depth-first search reaches from the origin through same-colored cells,
with a neighbor test that allows a difference of at most one in each coordinate.
A move repaints that set and then searches again.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        ...

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    ...

def adjacent(a: Coord, b: Coord) -> bool:
    ...

class FloodGame:
    ("Flood-fill game: grow a patch "
     "from the origin to fill the board.")
    def __init__(self, size: int,
                 origin: Coord = (0, 0)) -> None:
        ...

    def _flood(self, color: Color) -> set[Coord]:
        ("Every cell reachable from origin "
         "through same-colored cells.")
        ...

    def select(self, cell: Coord) -> bool:
        ("Recolor the owned patch "
         "to the selected cell's color.")
        ...

    def is_complete(self) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If you repaint the patch and stop there, `owned` holds only `(0, 0)`,
which the demo's first move recolors to match the first unowned cell.
Every later `select()` picks that same cell, finds that its color matches the patch, and returns `False`,
so the `while` loop runs forever.
The patch grows because `select()` searches again from the origin after repainting.

```python
# exercise_6.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        members = list(cls)
        return members[n % len(members)]

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): Color.at(x + y)
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
        self.moves = 0
        self.owned = self._flood(self.grid[origin])

    def _flood(self, color: Color) -> set[Coord]:
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

    def select(self, cell: Coord) -> bool:
        ("Recolor the owned patch "
         "to the selected cell's color.")
        new_color = self.grid[cell]
        if new_color == self.grid[self.origin]:
            return False  # No-op: already this color
        for c in self.owned:
            self.grid[c] = new_color
        # Absorb new neighbors
        self.owned = self._flood(new_color)
        self.moves += 1
        return True

    def is_complete(self) -> bool:
        return len(self.owned) == self.size * self.size

game = FloodGame(4)
while not game.is_complete():
    remaining = [
        c for c in game.grid if c not in game.owned]
    game.select(remaining[0])
print("solved in", game.moves, "moves")
#: solved in 6 moves
```

**Reuse the model's grid.** `FloodGame` reuses `new_grid()` from `box_observer.py` unchanged and
adds the `adjacent()` the exercise asks for.

**Find the owned patch.** `_flood()` is a plain graph search (depth-first, using a stack)
starting from `origin` and walking from each cell to every neighbor
`adjacent()` reports, as long as that neighbor is still the same color.

**Grow the patch by recoloring.** `select()` is the game
move: it repaints
every cell in the *currently owned* patch to the selected cell's color,
then re-runs `_flood()` to pick up the neighbors that now match that
new color and have joined the patch.

**Score the game.** `game.moves` gives the
single-player scoring the exercise asks for:
the moves it takes to make the whole field one color.
Two players can share the same `select()`
method, alternating whose turn supplies the next color, and after a
fixed number of rounds whoever owns the larger patch wins.

`FloodGame`
can also inherit from `Broadcaster[Grid]`, as `BoxModel` does, and
call `self.announce(self.grid)` at the end of a successful `select()`.
`box_view.py`'s existing view then repaints after every move. The
drawing code needs no change, but `show()`'s parameter annotation does:
it names `BoxModel`, and a `FloodGame` is not one. Widening it to a
Protocol (or to `Broadcaster[Grid]` plus `size`, `grid`, and
`select()`) lets the same view draw either model.

</details>
</details>
</details>

## 7. A new selection rule, and the same view

> Change the rule for a selection in `box_observer.py`:
> make `recolored()` advance every box in the selected box's row and column.
> Run `box_view.py` without editing it,
> and explain why the view needed no change.

<details>
<summary>Where to look</summary>

In [The Model](../../Chapters/30_Patterns--Observer.md#the-model), `recolored()` alone decides which cells change;
`BoxModel.select()` calls it and announces the result.
Build the new `Grid` from every cell that shares the selection's `x` or its `y`.
For why the view needs no change, see what `draw()` receives in [The View](../../Chapters/30_Patterns--Observer.md#the-view).

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        ...

    def next(self) -> Color:
        ...

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    ...

def recolored(grid: Grid, selected: Coord) -> Grid:
    ...

def initials(grid: Grid, size: int) -> str:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        members = list(cls)
        return members[n % len(members)]

    def next(self) -> Color:
        return Color.at(list(Color).index(self) + 1)

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): Color.at(x + y)
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    return grid | {cell: color.next()
                   for cell, color in grid.items()
                   if cell[0] == x or cell[1] == y}

def initials(grid: Grid, size: int) -> str:
    return "\n".join(
        " ".join(grid[(x, y)][0] for x in range(size))
        for y in range(size))

grid = new_grid(4)
print(initials(grid, 4))
#: s p k s
#: p k s p
#: k s p k
#: s p k s
print(initials(recolored(grid, (1, 2)), 4))
#: s k k s
#: p s s p
#: s p k s
#: s k k s
```

**Advance the selection's row and column.** `Color` and `new_grid()` come from `box_observer.py` unchanged, and
`recolored()` is the one function that differs. It keeps every cell
whose column matches the selection's `x` or whose row matches its `y`,
and advances each one. The cells come from `grid`, so none lies
outside it and the `in grid` test goes away.

**Show the grid as text.** `initials()` prints each
cell's first letter, one row per line. After selecting column 1, row
2, that column and that row have moved one color along, and the other
nine cells are as they were.

Pasting this `recolored()` over the one in `box_observer.py` changes
what the window does, and `box_view.py` runs as it stands. The view
touches the model in two places. Its mouse handler calls
`model.select()` with a coordinate, and its `draw()` receives a whole
`Grid` and paints every cell. Neither one says which cells a selection
changes, so the view holds nothing that a new rule could make wrong.
The rule sits in `recolored()`, `BoxModel.select()` calls it, and
`announce()` delivers the result. `initials()` makes the same point
from the other side: it is a second view of a `Grid`, written without
knowing the rule.

</details>
</details>
</details>

## 8. Two views on one model

> Add a second view to `box_observer.py`'s `BoxModel`.
> Write one view that prints a letter per cell and another that prints how many cells each color holds,
> connect both to the same model,
> and show that one `select()` updates the pair.
> Keep both views textual so the example runs without a window,
> and leave the model as `box_observer.py` has it.

<details>
<summary>Where to look</summary>

In [The View](../../Chapters/30_Patterns--Observer.md#the-view), `draw()` is a responder that takes a `Grid`,
and any function with that signature is another view.
Write one that prints a letter per cell and one that counts with `collections.Counter`,
then `connect()` both before calling `select()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections import Counter
from collections.abc import Callable
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        ...

    def next(self) -> Color:
        ...

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]
type Responder[T] = Callable[[T], None]

def new_grid(size: int) -> Grid:
    ...

def recolored(grid: Grid, selected: Coord) -> Grid:
    ...

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(self, responder: Responder[T]) -> None:
        ...

    def announce(self, data: T) -> None:
        ...

class BoxModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        ...

    def select(self, cell: Coord) -> None:
        ...

def letters(grid: Grid) -> None:
    ...

def tally(grid: Grid) -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from collections import Counter
from collections.abc import Callable
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        members = list(cls)
        return members[n % len(members)]

    def next(self) -> Color:
        return Color.at(list(Color).index(self) + 1)

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]
type Responder[T] = Callable[[T], None]

def new_grid(size: int) -> Grid:
    return {(x, y): Color.at(x + y)
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)

class BoxModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)

model = BoxModel(3)

def letters(grid: Grid) -> None:
    for y in range(model.size):
        print(" ".join(grid[(x, y)][0]
                       for x in range(model.size)))

def tally(grid: Grid) -> None:
    counts = Counter(grid.values())
    print(" ".join(f"{c[0]}:{counts[c]}" for c in Color))

model.connect(letters)
model.connect(tally)
model.select((1, 1))
#: s k k
#: k s p
#: k p p
#: s:2 p:3 k:4
model.select((0, 0))
#: p s k
#: s s p
#: k p p
#: s:3 p:4 k:2
```

**Reuse the chapter's model.** The model is `box_observer.py`'s, copied here so the solution runs on
its own: `Color`, `new_grid()`, and `recolored()` unchanged, and a
`Broadcaster` trimmed to the two methods this example calls.
`BoxModel` is the chapter's, and the exercise adds nothing to it.

**Write each view as a responder.** `letters()` and `tally()` are the two views. Each takes a `Grid` and
returns `None`, the shape `connect()` requires, so each is a
responder the same way `draw()` is. `letters()` prints the first
character of each color, one row per line, and `tally()` counts the
colors with a `Counter`.
Neither one names the other, and neither names the model's rule.

**Update both views from one change.** `model.select((1, 1))` calls `recolored()` once and `announce()` once,
and `announce()` calls both views in connection order. They read the
same `Grid` object, so the letters and the counts describe one state
of the model: the first selection advances the five cells of the
cross, which moves two cells out of `skyblue` and two into `khaki`.
The corner selection that follows has three cells inside the grid
rather than five.

Adding a third view means one more `connect()` call. `box_view.py`'s
`draw()` is such a view, and `show(model)` connects it to a model that
already has `letters()` and `tally()`, so the window and the terminal
report the same grid. Running that combination means `show()` takes
over with `root.mainloop()`, so call `show()` last.

</details>
</details>
</details>

## 9. Which colors a grid can reach

> Work out which colors the whole grid can reach from `new_grid(size)` under `box_observer.py`'s rule.
> Selecting a cell advances up to five cells by one, modulo three,
> and selections commute, so this is a linear system over the integers mod 3:
> the unknowns are how many times you select each cell.
> Write Gaussian elimination mod 3 to decide whether the system has a solution,
> and print the reachable colors for every size from 3 through 8.
> The 8x8 grid reaches `palegreen` alone,
> and one smaller size reaches nothing.

<details>
<summary>Where to look</summary>

The rule in [The Model](../../Chapters/30_Patterns--Observer.md#the-model) adds one, modulo three, to the selected cell and its four neighbors,
so each selection is a column of a 0/1 matrix and the target color is a right-hand side.
Gaussian elimination mod 3 differs from the usual in two places:
divide by a pivot with `pow(x, -1, 3)`, and reduce every subtraction with `% 3`.
A zero row with a nonzero right-hand side means no solution.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from enum import StrEnum
from typing import Final

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

type Coord = tuple[int, int]
type Row = list[int]

MOD: Final[int] = len(Color)

def cross(cell: Coord, size: int) -> list[Coord]:
    ...

def system(size: int, target: int) -> list[Row]:
    "One row per cell, with the target in the last column."
    ...

def solvable(rows: list[Row]) -> bool:
    ...

def reachable(size: int) -> list[Color]:
    ...
```

<details>
<summary>Solution</summary>

If you leave the `% MOD` off the subtraction, as ordinary elimination would,
an entry can become a nonzero multiple of three.
`next()` accepts such an entry as a pivot, since it is not zero,
and `pow(x, -1, MOD)` then raises a `ValueError` ("base is not invertible for the given modulus"),
so the script stops at 3x3 before printing a line.
Reducing every result mod 3 keeps each entry in `0`, `1`, or `2`, where every nonzero value has an inverse.

```python
# exercise_9.py
from enum import StrEnum
from typing import Final

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

type Coord = tuple[int, int]
type Row = list[int]

MOD: Final[int] = len(Color)

def cross(cell: Coord, size: int) -> list[Coord]:
    x, y = cell
    around = [(x, y), (x - 1, y), (x + 1, y),
              (x, y - 1), (x, y + 1)]
    return [(a, b) for a, b in around
            if 0 <= a < size and 0 <= b < size]

def system(size: int, target: int) -> list[Row]:
    "One row per cell, with the target in the last column."
    cells = [(x, y) for x in range(size)
             for y in range(size)]
    at = {cell: i for i, cell in enumerate(cells)}
    rows = [[0] * (len(cells) + 1) for _ in cells]
    for cell in cells:
        for other in cross(cell, size):
            rows[at[other]][at[cell]] = 1
    for i, (x, y) in enumerate(cells):
        rows[i][-1] = (target - (x + y)) % MOD
    return rows

def solvable(rows: list[Row]) -> bool:
    width = len(rows[0]) - 1
    pivot = 0
    for col in range(width):
        found = next((r for r in range(pivot, len(rows))
                      if rows[r][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = pow(rows[pivot][col], -1, MOD)
        rows[pivot] = [v * scale % MOD for v in rows[pivot]]
        for r, row in enumerate(rows):
            if r != pivot and row[col]:
                factor = row[col]
                rows[r] = [(a - factor * b) % MOD for a, b
                           in zip(row, rows[pivot])]
        pivot += 1
    # A row of zeros with a nonzero target is 0 == 1
    return all(any(row[:-1]) or row[-1] == 0
               for row in rows)

def reachable(size: int) -> list[Color]:
    return [color for target, color in enumerate(Color)
            if solvable(system(size, target))]

for size in range(3, 9):
    names = ", ".join(reachable(size))
    print(f"{size}x{size}: {names or 'nothing'}")
#: 3x3: skyblue, palegreen, khaki
#: 4x4: skyblue, palegreen, khaki
#: 5x5: nothing
#: 6x6: skyblue, palegreen, khaki
#: 7x7: skyblue, palegreen, khaki
#: 8x8: palegreen
```

**State the puzzle as a linear system.** Selecting a cell adds one, modulo three, to that cell and to each
neighbor `cross()` finds, and selecting it twice adds two. The order
of the selections makes no difference, so a whole sequence of them is
a count per cell, and the puzzle becomes one linear system: `M v = b`,
over the integers mod 3. `M` records which cells each selection
advances, `v` counts the selections, and `b` is how far each cell must
advance to reach the target color. `system()` builds `M` and `b` together,
one row per cell, with `b` in the last column.

**Decide solvability by elimination.** `solvable()` answers whether that system has a solution, and never
computes one: the question is which colors are reachable, not how.
It is Gaussian elimination, with two changes for arithmetic mod 3.
Dividing by a pivot is multiplying by its inverse, which `pow(x, -1,
MOD)` supplies, and every subtraction ends in `% MOD`. Elimination
either finds a pivot in a column or leaves that column free; what
decides the answer is the rows that survive with every coefficient
zero. Such a row states `0 == row[-1]`, so a nonzero last column means
no count of selections reaches that color.

**Report the reachable colors.** The six sizes split three ways. At 3x3, 6x6, and 7x7 the matrix has
full rank, so every color is reachable from any starting grid. At 4x4
the rank is 14 of 16, and at 8x8 it is 60 of 64: the missing
dimensions are combinations of cells that no selection can change, so
the starting grid must already agree with the target on each of them.
The 4x4 banded grid agrees for all three colors, and the 8x8 grid for
`palegreen` alone, which is the puzzle the window poses. At 5x5 three
dimensions are missing and no color satisfies them, so no sequence of
selections turns that board one color.

`Color` is a `StrEnum`, so its members go straight into
`", ".join(reachable(size))` with no conversion, the same property
that lets `box_view.py` hand a `Color` to `tkinter`.

</details>
</details>
</details>

## 10. A descriptor per watched attribute

> Write a `Notifying` [descriptor](../../Chapters/17_Techniques--Metaprogramming.md#a-descriptor-that-validates)
> that replaces the `@property` and `announce()` pair,
> so one class declares several independently watched attributes:
> `celsius = Notifying[float]()` beside `humidity = Notifying[float]()`.
> Each attribute keeps its own responders.
> Connecting needs the descriptor, not the value it stores,
> so `__get__()` returns the descriptor for an access through the class,
> and `Thermometer.celsius.connect(t, readings.append)` reaches it.
> Show that an assignment to one attribute calls no responder of the other.

<details>
<summary>Where to look</summary>

A descriptor's `__set_name__()` ([A Descriptor That Validates](../../Chapters/17_Techniques--Metaprogramming.md#a-descriptor-that-validates)) receives the attribute's name,
from which it can derive one storage name and one responder-list name per attribute.
`__set__()` stores the value and then calls that attribute's responders.
`__get__()` returns `self` when `obj` is `None`, so `Thermometer.celsius.connect()` reaches it,
and two `@overload`s tell the type checker which result each access gets.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from collections.abc import Callable
from typing import overload

type Responder[T] = Callable[[T], None]

class Notifying[T]:
    def __set_name__(
        self, owner: type, name: str
    ) -> None:
        ...

    @overload
    def __get__(self, obj: None,
                owner: type) -> Notifying[T]: ...
    @overload
    def __get__(self, obj: object,
                owner: type) -> T: ...
    def __get__(self, obj: object | None,
                owner: type) -> T | Notifying[T]:
        ...

    def __set__(self, obj: object, value: T) -> None:
        ...

    def connect(self, obj: object,
                responder: Responder[T]) -> None:
        ...

class Thermometer:
    celsius = Notifying[float]()
    humidity = Notifying[float]()

    def __init__(self, celsius: float,
                 humidity: float) -> None:
        ...
```

<details>
<summary>Solution</summary>

If `__get__()` always returns the stored value, as a validating descriptor's does,
`Thermometer.celsius` runs `getattr(None, "_celsius")`
and raises an `AttributeError` before the call to `connect()`.
The type checker passes that version, since the overloads still declare that class access returns the descriptor,
so the failure appears only when the program runs.
The solution tests for `obj is None` and returns the descriptor.

```python
# exercise_10.py
from collections.abc import Callable
from typing import overload

type Responder[T] = Callable[[T], None]

class Notifying[T]:
    def __set_name__(
        self, owner: type, name: str
    ) -> None:
        self.storage = f"_{name}"
        self.responders = f"_responders_{name}"

    @overload
    def __get__(self, obj: None,
                owner: type) -> Notifying[T]: ...
    @overload
    def __get__(self, obj: object,
                owner: type) -> T: ...
    def __get__(self, obj: object | None,
                owner: type) -> T | Notifying[T]:
        if obj is None:
            return self  # Thermometer.celsius
        return getattr(obj, self.storage)

    def __set__(self, obj: object, value: T) -> None:
        setattr(obj, self.storage, value)
        for responder in getattr(obj, self.responders, ()):
            responder(value)

    def connect(self, obj: object,
                responder: Responder[T]) -> None:
        obj.__dict__.setdefault(
            self.responders, []).append(responder)

class Thermometer:
    celsius = Notifying[float]()
    humidity = Notifying[float]()

    def __init__(self, celsius: float,
                 humidity: float) -> None:
        self.celsius = celsius
        self.humidity = humidity

t = Thermometer(20.0, 0.4)
readings: list[float] = []
humidities: list[float] = []
Thermometer.celsius.connect(t, readings.append)
Thermometer.humidity.connect(t, humidities.append)
t.celsius = 25.0
t.humidity = 0.5
t.celsius = 150.0
print(readings, humidities)
#: [25.0, 150.0] [0.5]
print(t.celsius, t.humidity)
#: 150.0 0.5
```

**Give each attribute its own storage.** `__set_name__()` receives the name the class body binds each
descriptor to, so `celsius` and `humidity` derive different attribute
names: `_celsius` and `_responders_celsius` for one, `_humidity` and
`_responders_humidity` for the other. Two `Notifying` instances in one
class therefore share no storage and no responder list, so the two
attributes are independent. `Broadcaster` keeps one list for
the whole object; a descriptor keeps one per attribute.

**Return the descriptor on class access.** Class access is the part a validating descriptor never needs.
`Thermometer.celsius` calls `__get__()` with `obj` set to `None`, and
returning the descriptor there puts `connect()` within reach. The
two `@overload` declarations tell the type checker which result each
access gets: `Notifying[T]` from the class, `T` from an instance. Without
them the declared return type is the union, and `t.celsius * 2` fails
to check. The overloads also check the responder against the
attribute: `Thermometer.celsius.connect(t, readings.append)` passes
only because `readings` is a `list[float]`.

Pyright rejects `Thermometer.celsius.connect`.
It reads the constructor's `self.celsius = celsius` as declaring an instance attribute of type `float` beside the descriptor,
so it types the class access as `Notifying[float] | float` and reports that `float` has no `connect`.
`ty` types the class access from the `__get__()` overload alone.
A codebase on Pyright looks the descriptor up in `type(obj).__dict__` instead,
which draws no complaint from Pyright.

**Announce on assignment.** `__set__()` stores the value and then calls each responder connected
to that attribute, the work `Thermometer`'s property setter did with
`self.announce(value)`.

**Keep each instance's responders apart.** `connect()` writes the responder list into the instance's `__dict__`
rather than declaring it on the class, where every instance shares
one list.

</details>
</details>
</details>

## 11. Responders registered at load time

> Write a load-time version of `Broadcaster`:
> a module-level list of responders and a `@responds` decorator that appends a function to it and returns the function unchanged.
> Each responder then registers when Python runs its `def` statement,
> and for a module-level function Python runs that statement while it imports the module.
> Give a `Thermometer` a `celsius` setter that announces to that list,
> and create two thermometers.
> Say which of the problems in this chapter's runtime sections the load-time form keeps,
> which it removes, and what it costs that `Broadcaster` does not.

<details>
<summary>Where to look</summary>

A module-level list and a decorator that appends its function and returns it unchanged make every decorated `def` a registration.
For the comparison, reread the problems the runtime sections raise after [The Pythonic Observer](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer):
disconnecting, a raised exception, lapsed listeners, and re-entrant notification.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_11.py
from collections.abc import Callable
from typing import Final

type Responder = Callable[[float], None]

RESPONDERS: Final[list[Responder]] = []

def responds(fn: Responder) -> Responder:
    ...

class Thermometer:
    def __init__(self, celsius: float) -> None:
        ...

    @property
    def celsius(self) -> float:
        ...

    @celsius.setter
    def celsius(self, value: float) -> None:
        ...

@responds
def display(celsius: float) -> None:
    ...

@responds
def alarm(celsius: float) -> None:
    ...
```

<details>
<summary>Solution</summary>

If `responds()` appends the function and returns nothing,
the demo still prints its three lines, because `RESPONDERS` holds each function.
The decorator's result replaces the name, though,
so the name `display` refers to `None`, and calling `display(5.0)` raises a `TypeError`.
The type checker catches the mistake before any run: with `-> Responder` declared, `responds()` draws an `invalid-return-type`.
Returning `fn` keeps each decorated name bound to its function.

```python
# exercise_11.py
from collections.abc import Callable
from typing import Final

type Responder = Callable[[float], None]

RESPONDERS: Final[list[Responder]] = []

def responds(fn: Responder) -> Responder:
    RESPONDERS.append(fn)
    return fn

class Thermometer:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        for responder in RESPONDERS:
            responder(value)

@responds
def display(celsius: float) -> None:
    print(f"display: {celsius}C")

@responds
def alarm(celsius: float) -> None:
    if celsius > 100:
        print("alarm!")

room = Thermometer(20.0)
oven = Thermometer(180.0)
room.celsius = 21.0
#: display: 21.0C
oven.celsius = 200.0
#: display: 200.0C
#: alarm!
```

**Register at definition time.** Python calls `responds()` once for each decorated `def`, when it runs that statement.
For a module-level function, that is while Python imports the module,
so the registry is complete before any thermometer exists.

**Keep the function callable.** `responds()` returns `fn` unchanged,
so `display` is still a function you can call directly.

The load-time form removes three of the runtime problems:

- `Broadcaster.announce()` copies its list because a responder can disconnect itself mid-notification.
  The registry has no `disconnect()`, so the setter iterates through `RESPONDERS` directly.
- A lambda cannot be disconnected, a question that disappears along with `disconnect()`.
  The `@` form also needs a `def`, so every decorated responder has a name.
- A lapsed listener is an object kept alive by its connection.
  The registry holds module-level functions,
  which their module keeps alive for the whole program,
  so the strong references keep nothing alive that Python would otherwise collect.

Two problems remain.
A responder that raises an exception stops the loop,
and the exception reaches the assignment to `celsius`.
A responder that assigns to `celsius` re-enters the setter.

The load-time form also costs three things that `Broadcaster` does not:

- The registry is global.
  `room` and `oven` announce to the same two responders,
  and `alarm` cannot tell which thermometer changed.
  `Broadcaster` keeps one list per instance.
  Sending the thermometer along with the reading tells the responders the source,
  but every responder still receives every thermometer's changes.
- A responder registers only if Python imports its module.
  A responder in a module that nothing imports does not run, and nothing reports its absence.
  Django's documentation meets this by importing an app's signal handlers from its `AppConfig.ready()` method,
  which Django calls at startup.
- Tests share the registry.
  A test that decorates a responder leaves it registered for every test that runs after it,
  unless the test removes it from `RESPONDERS`.

</details>
</details>
</details>
