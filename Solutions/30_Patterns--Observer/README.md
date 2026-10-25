# Observer: Solutions

## 1. A minimal broadcaster-responder pair

> Create a minimal *Observer* design of your own,
> without looking at `broadcaster.py`:
> the smallest `Broadcaster` that lets you connect callables,
> then notifies them.
> Demonstrate it by connecting several responders and causing one change that updates them all.

<details>
<summary>Where to look</summary>

The design is the one [The Pythonic *Observer*](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer)
describes: a list of callables, one method that appends to it,
and one that calls each entry with the same argument.
Any callable is a responder, a `lambda` included,
so the demonstration needs no observer class.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Callable

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(
        self, responder: Callable[[T], None]
    ) -> None:
        ...

    def announce(self, data: T) -> None:
        ...
```

<details>
<summary>Done when</summary>

one change reaches every connected responder once,
in the order you connected them, each with the same value.
Connecting two `lambda`s that record a tag and the value, then announcing `42`,
gives `[('A', 42), ('B', 42)]`,
and a third `connect()` adds a third entry with no change to your `Broadcaster`.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from collections.abc import Callable

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Callable[[T], None]] = []

    def connect(
        self, responder: Callable[[T], None]
    ) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        for responder in self._responders:
            responder(data)

calls: list[tuple[str, int]] = []
broadcaster = Broadcaster[int]()
broadcaster.connect(lambda v: calls.append(("A", v)))
broadcaster.connect(lambda v: calls.append(("B", v)))
broadcaster.announce(42)
print(calls)
#: [('A', 42), ('B', 42)]
```

Like `broadcaster.py`, this solution has no separate `Observer` class.
Any callable, here two `lambda`s, is a responder.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Push or Pull](../../Chapters/30_Patterns--Observer.md#push-or-pull)
describes the pull model.
The type problem is that a parameter is contravariant.
An `update()` that narrows `subject` to `Thermometer` accepts less than `Observer[float]` requires.
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
<summary>Done when</summary>

both versions print `display: 25C`,
`uv run ty check` passes on each with `t.attach(Display())` in place,
and only the second declares `subject: Thermometer` in `Display.update()`.
Making that change in the first version draws `invalid-argument-type` at `t.attach()`.
You can say what each version adds.

<details>
<summary>Solution</summary>

If you declare `subject: Thermometer` in `Display.update()` and keep the classic `Observer[T]`,
the program still prints `display: 25C`,
but the type checker rejects `t.attach(Display())`.
A parameter is contravariant,
so an `update()` that accepts only a `Thermometer` cannot substitute for one that accepts any `Subject[float]`.
Both versions below keep the read of `subject.celsius` and make `t.attach(Display())` type-check,
the first by widening the parameter again and the second by changing the protocol.

**Declare the widest subject type.**
The protocol here is the one from `classic_observer.py`, unchanged.
`update()` declares the widest type `notify()` can hand it, `Subject[float]`,
and narrows that to a `Thermometer` before reading `celsius`:

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

**Narrow the subject at runtime.**
The `assert` runs on every notification.
It states a requirement the protocol cannot express:
this `Display` works for a `Thermometer` and fails on any other `Subject[float]`.
That failure arrives at the first notification,
not at the `attach()` call the type checker reads.

**Let the subject supply its own type.**
The second version moves the subject's type into the protocol.
`Observer[S, T]` takes the subject's type as a parameter,
and `Subject` supplies its own type with `Self`,
so `Thermometer.attach()` asks for an `Observer[Thermometer, float]`:

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

**Name the subject the observer reads.**
With `Display.update()` declaring `subject: Thermometer`,
`t.attach(Display())` now type-checks.
The requirement the first version's `assert` stated now sits in the observer's type,
which declares the subject the observer watches.
An observer that declares the wider `Subject[float]` still attaches to any `Subject[float]`,
because a parameter is contravariant.
An observer that reads `celsius` must declare `Thermometer`,
and it attaches to a `Thermometer` alone.

Both versions ignore `arg`.
Under pull, each observer's own code selects what to read from the subject,
so each observer must specify the type of the subject it watches.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. An `announce()` that survives a failing responder

> Make `Broadcaster.announce()` survive a responder that raises an exception:
> every other responder still receives the announcement,
> and `announce()` re-raises the failures afterward, together,
> as an [`ExceptionGroup`](../../Chapters/19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
> (which you build yourself here: `raise ExceptionGroup("message", failures)`).
> Write a test in which the first responder raises an exception and the second still records its notification.

<details>
<summary>Where to look</summary>

[Raising an Exception](../../Chapters/30_Patterns--Observer.md#raising-an-exception)
shows one failing responder stopping the loop in `announce()`.
Put a `try` inside the loop, append each exception to a list,
and after the loop raise an `ExceptionGroup` if the list holds any exceptions.
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
<summary>Done when</summary>

your test passes against your `Broadcaster`:
the first responder raises an exception,
`announce()` raises an `ExceptionGroup` holding it,
and the second responder has recorded the value.
If `announce()` discards each exception instead,
the test fails with `DID NOT RAISE`.

<details>
<summary>Solution</summary>

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

**Catch any ordinary failure.**
Catching bare `Exception` here is deliberate.
`announce()` calls arbitrary callables,
so its code cannot list the exceptions they raise.
Catching `Exception` lets every other `BaseException` propagate,
so a `KeyboardInterrupt` or an `asyncio.CancelledError` raised in a responder stops the notification instead of joining `failures`.

**Record each failure.**
Keeping the exceptions matters as much as catching them.
A responder that fails silently is worse than one that stops the loop.
The stopped loop raises an exception the caller sees;
the silent failure leaves the caller believing every responder succeeded.

If you catch each exception and discard it, every responder runs,
but `announce()` returns normally.
The demo's `print()` sits inside its `except*` block,
so the script prints nothing,
and the test's `pytest.raises(ExceptionGroup)` fails with `DID NOT RAISE`.

**Report every failure together.**
`ExceptionGroup` is the right container because more than one responder can fail on a single notification,
and the caller needs every failure, not the first.
`except*` then lets a caller handle one kind of failure and re-raise the rest.
A plain `except RuntimeError` misses the group,
because the exception `announce()` raises is the `ExceptionGroup` itself.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. The same rescue, for the async fan-out

> Redo exercise 3 for `async_broadcaster.py`.
> Make `announce()` use `gather(*coros, return_exceptions=True)`,
> separate the returned exceptions from the successes,
> and raise them together as an exception group.
> Write a test in which the first responder raises an exception and the second still records its notification.

<details>
<summary>Where to look</summary>

[A Failing Responder Orphans the Rest](../../Chapters/30_Patterns--Observer.md#a-failing-responder-orphans-the-rest)
shows `gather()` raising the first failure while the other coroutines keep running with nothing awaiting them.
With `return_exceptions=True`, `gather()` returns every result,
exceptions among them.
Keep the results that are exceptions and raise them as one group.
A cancelled responder comes back as a `CancelledError`, a `BaseException`,
so the filter and the group must accept one.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class AsyncBroadcaster[T]:
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
<summary>Done when</summary>

your test passes: `announce()` raises an exception group and the second responder has recorded the value.
Removing `return_exceptions=True` fails it,
since a bare `RuntimeError` escapes `pytest.raises(ExceptionGroup)`.
A first responder that raises `asyncio.CancelledError` also ends up in the group,
with the second value still recorded.

<details>
<summary>Solution</summary>

The solution passes `return_exceptions=True`,
so `gather()` waits for every responder.

```python
# exercise_4.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class AsyncBroadcaster[T]:
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
            r for r in results
            if isinstance(r, BaseException)]
        if failures:
            raise BaseExceptionGroup(
                "responder failures", failures)

received: list[int] = []

async def broken(data: int) -> None:
    raise RuntimeError(f"cannot handle {data}")

async def record(data: int) -> None:
    await asyncio.sleep(0)
    received.append(data)

async def main() -> None:
    broadcaster = AsyncBroadcaster[int]()
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
from exercise_4 import AsyncBroadcaster

def test_later_responder_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        broadcaster = AsyncBroadcaster[int]()
        broadcaster.connect(broken)
        broadcaster.connect(record)
        with pytest.raises(ExceptionGroup):
            await broadcaster.announce(1)

    asyncio.run(run())
    assert received == [1]

def test_a_cancelled_responder_is_reported() -> None:
    received: list[int] = []

    async def cancelled(data: int) -> None:
        raise asyncio.CancelledError()

    async def record(data: int) -> None:
        received.append(data)

    async def run() -> None:
        broadcaster = AsyncBroadcaster[int]()
        broadcaster.connect(cancelled)
        broadcaster.connect(record)
        with pytest.raises(BaseExceptionGroup) as info:
            await broadcaster.announce(1)
        assert info.group_contains(
            asyncio.CancelledError)

    asyncio.run(run())
    assert received == [1]
```

**Run every responder to completion.**
`return_exceptions=True` changes `gather()` from "re-raise the first failure immediately" to "run everything and return a list."
The synchronous version needs a `try` inside its loop to keep going past a failure.
Here that one keyword does the same job,
because `gather()` runs the loop over the responders.

If you leave out `return_exceptions=True`,
`gather()` re-raises the first failure as a bare `RuntimeError`.
`pytest.raises(ExceptionGroup)` lets that `RuntimeError` propagate,
which fails the test.
The demo still prints `1 [7]`,
because `except*` wraps a bare exception in a group and `record()` finishes before `main()` resumes.
A slower responder, though, keeps running with nothing awaiting it,
as [A Failing Responder Orphans the Rest](../../Chapters/30_Patterns--Observer.md#a-failing-responder-orphans-the-rest)
shows.

**Pick out the failures.**
The results come back in argument order,
so the list shows which responder produced what.
This version needs the failures alone,
so its comprehension keeps each result for which `isinstance(r, BaseException)` is true.

**Report a cancelled responder too.**
If another task cancels the awaiting task while `gather()` waits,
`gather()` cancels every responder.
`asyncio.CancelledError` then reaches the awaiting task before `announce()` has any results to filter,
so that cancellation bypasses the filter.
The cancellation that `return_exceptions=True` does return is a responder's own:
a `CancelledError` raised inside the responder,
which is what a cancelled `await` propagates.
Because `CancelledError` derives from `BaseException` and not from `Exception`,
an `isinstance(r, Exception)` filter drops that result from `failures` silently.
This version filters on `BaseException`.

**Hold a cancellation in the group.**
`ExceptionGroup` cannot hold a `BaseException`.
With the wider filter,
`ty` reports an `invalid-argument-type` at an `ExceptionGroup(...)` call.
The listing raises a `BaseExceptionGroup`.
That constructor returns an `ExceptionGroup` when every member is an `Exception`,
so the demo's `except* RuntimeError` and the first test still see the group the exercise asks for.
When a cancellation is among the failures, the group is a `BaseExceptionGroup`.
The second test confirms that this group reports the cancelled responder and that the later responder still runs.

Exercise 3's synchronous version keeps `except Exception`.
The two versions differ in where a `BaseException` goes.
In the synchronous version it propagates out of the loop and stops the notification,
which is right for a `KeyboardInterrupt`.
Here `gather()` has turned it into a value,
and a filter that drops the value hides the failure.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Failures returned as values

> Redo exercise 3 with each failure returned as a value instead of raised as an exception.
> Each responder returns a [`Result`](../../Chapters/42_Functional--Error_Handling.md#a-result-type)
> from `utils/result.py`,
> and `announce()` returns the `Err` values it collects.
> Write an adapter that lets you connect a responder returning `None`,
> such as `received.append`.
> Write a test in which the first responder fails and the second still records its notification.

<details>
<summary>Where to look</summary>

Change the responder type to return a [`Result`](../../Chapters/42_Functional--Error_Handling.md#a-result-type),
and make `announce()` a comprehension that keeps each result that is an `Err`.
The adapter takes a `None`-returning callable and returns a responder that calls it and answers `Ok(None)`.

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
<summary>Done when</summary>

your test passes: the first responder returns an `Err`,
`announce()` returns a list holding that `Err`, and `received.append`,
connected through your adapter, has recorded the value.
An announcement every responder handles returns `[]`,
and `uv run ty check` passes on your file.

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

**Collect the failures as values.**
Each responder reports a failure by returning an `Err`,
so `announce()` needs no `try`.
The caller receives the failures as an ordinary list and decides what to do with them,
where exercise 3's caller must catch an `ExceptionGroup`.
An empty list means every responder succeeded.

**Adapt a `None`-returning callable.**
The type change applies to every responder.
`received.append` returns `None`, and a `Responder[int]` must return a `Result`,
so the type checker rejects `broadcaster.connect(received.append)`.
The adapter, `succeeds()`, assumes the wrapped callable always succeeds.
An exception the callable does raise propagates out of `announce()` as it does in the chapter's version.

Returning errors as values works when you write the responders.
For a broadcaster that accepts arbitrary callables,
exercise 3's catch-and-collect keeps the loop running when a responder someone else wrote raises an exception.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Turning `grid_observer.py` into a flood-fill game

> Turn `grid_observer.py` into a simple game:
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
<summary>Done when</summary>

on a 4x4 `new_grid()` field,
repeatedly selecting the first cell outside your patch, in the grid's key order,
completes the field in 6 moves.
Your neighbor test is true for `(0, 0)` and `(1, 1)` and false for a cell paired with itself,
and you can describe what a second player adds to the state.

<details>
<summary>Solution</summary>

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

**Reuse the model's grid.**
`FloodGame` reuses `new_grid()` from `grid_observer.py` unchanged and adds the `adjacent()` the exercise asks for.

**Find the owned patch.**
`_flood()` is a depth-first search that keeps its pending cells on a stack.

**Grow the patch by recoloring.**
`select()` is the game move.

If you repaint the patch and stop there, `owned` stays `{(0, 0)}`,
which the demo's first move recolors to match the first unowned cell.
Every later `select()` picks that same cell,
finds that its color matches the patch, and returns `False`,
so the demo's `while not game.is_complete()` loop runs forever.

**Score the game.**
`game.moves` gives the single-player scoring the exercise asks for:
the moves it takes to make the whole field one color.

`FloodGame` holds one `origin` and one `owned` set,
so a two-player version gives each player an origin of their own,
in opposite corners, and an owned set of their own, over one grid.
The players alternate turns, each recoloring their own patch,
and after a set number of rounds whoever owns the larger patch wins.

`FloodGame` can also inherit from `Broadcaster[Grid]`, as `GridModel` does,
and call `self.announce(self.grid)` at the end of a successful `select()`.
`grid_view.py`'s existing view then repaints after every move.
The drawing code needs no change, but `show()`'s parameter annotation does.
That annotation specifies `GridModel`, which a `FloodGame` is not.
Widening the annotation lets the same view draw either model.
The wider type can be a Protocol that declares `connect()`, `size`, `grid`,
and `select()`.
It can also be a base class that both models inherit,
one that extends `Broadcaster[Grid]` with `size`, `grid`, and `select()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. A new selection rule, and the same view

> Change the rule for a selection in `grid_observer.py`:
> make `recolored()` advance every box in the selected box's row and column.
> Run `grid_view.py` without editing it,
> and explain why the view needed no change.

<details>
<summary>Where to look</summary>

In [The Model](../../Chapters/30_Patterns--Observer.md#the-model),
`recolored()` alone decides which cells change.
`GridModel.select()` calls it and announces the result.
Build the new `Grid` from every cell that shares the selection's `x` or its `y`.
For why the view needs no change,
see what `draw()` receives in [The View](../../Chapters/30_Patterns--Observer.md#the-view).

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
<summary>Done when</summary>

selecting column 1, row 2 of a 4x4 `new_grid()` advances the seven cells of that column and row one color each and leaves the other nine as they were.
`grid_view.py` runs unedited under the new rule,
and you can say what `draw()` receives and why that keeps the rule out of the view.

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

**Advance the selection's row and column.**
`Color` and `new_grid()` come from `grid_observer.py` unchanged,
and `recolored()` is the one function that differs.
The cells come from `grid`,
so every one lies inside it and the comprehension needs no `in grid` test.

**Show the grid as text.**
`initials()` prints each cell's first letter, one row per line.
After the selection at column 1, row 2,
that column and that row have advanced one color.
The other nine cells are as they were.

Pasting this `recolored()` over the one in `grid_observer.py` changes what the window does.
`grid_view.py` runs as it stands.
Two places in the view involve a selection.
Its mouse responder calls `model.select()` with a coordinate,
and its `draw()` receives a whole `Grid` and paints every cell.
Both leave the choice of cells to the model,
so the view stays correct under any rule.
`recolored()` holds the rule, `GridModel.select()` calls it,
and `announce()` delivers the result.
`initials()` shows the same separation.
It is a second view of a `Grid`, and it prints the `Grid` the rule produces.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Two views on one model

> Add a second view to `grid_observer.py`'s `GridModel`.
> Write one view that prints a letter per cell and another that prints how many cells each color holds,
> connect both to the same model,
> and show that one `select()` updates the pair.
> Keep both views textual so the example runs without a window,
> and leave the model as `grid_observer.py` has it.

<details>
<summary>Where to look</summary>

In [The View](../../Chapters/30_Patterns--Observer.md#the-view),
`draw()` is a responder that takes a `Grid`,
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

class GridModel(Broadcaster[Grid]):
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
<summary>Done when</summary>

one `select((1, 1))` on a 3x3 `GridModel` prints both views,
the letter grid and the counts, in connection order.
The counts come to 2 `skyblue`, 3 `palegreen`, and 4 `khaki`,
and your `GridModel` matches `grid_observer.py` unchanged.

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

class GridModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)

model = GridModel(3)

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

**Reuse the chapter's model.**
The model is the one from `grid_observer.py`,
copied here so the solution runs on its own: `Color`, `new_grid()`,
and `recolored()` unchanged,
and a `Broadcaster` trimmed to the two methods this example calls.
`GridModel` stays as the chapter writes it, which the exercise requires.

**Write each view as a responder.**
`letters()` and `tally()` are the two views.
Each takes a `Grid` and returns `None`, the shape `connect()` requires,
so each is a responder the same way `draw()` is.
Neither one names the other, and neither contains the model's rule.

**Update both views from one change.**
Both views read the same `Grid` object,
so the letters and the counts describe one state of the model.

The first selection advances the five cells of the cross:
two from `skyblue` to `palegreen`, two from `palegreen` to `khaki`,
and the center from `khaki` to `skyblue`.
The tally therefore drops `skyblue` by one and raises `khaki` by one.
The corner selection that follows has three cells inside the grid rather than five.

Adding a third view means one more `connect()` call.
`grid_view.py`'s `draw()` is such a view,
and `show(model)` connects it beside `letters()` and `tally()`,
so the window and the terminal report the same grid.
`show()` ends in `root.mainloop()`,
which runs the window's event loop until the window closes,
so call `show()` last.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Which colors a grid can reach

> Work out which colors the whole grid can reach from `new_grid(size)` under `grid_observer.py`'s rule.
> Selecting a cell advances up to five cells by one, modulo three,
> and selections commute, so this is a linear system over the integers mod 3.
> The unknowns are how many times you select each cell.
> Write Gaussian elimination mod 3 to decide whether the system has a solution,
> and print the reachable colors for every size from 3 through 8.
> The 8x8 grid reaches `palegreen` alone,
> and one smaller size reaches nothing.

<details>
<summary>Where to look</summary>

The rule in [The Model](../../Chapters/30_Patterns--Observer.md#the-model)
adds one, modulo three, to the selected cell and its four neighbors,
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
<summary>Done when</summary>

your script prints one line per size from 3 through 8.
`5x5` reaches nothing, `8x8` reaches `palegreen` alone, and 3x3, 4x4, 6x6,
and 7x7 each reach all three colors.
Every entry your elimination produces stays in `0`, `1`, or `2`.

<details>
<summary>Solution</summary>

Reducing every product and difference mod 3 keeps each entry in `0`, `1`,
or `2`, where every nonzero value has an inverse.

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

**State the puzzle as a linear system.**
Selecting a cell adds one, modulo three,
to that cell and to each neighbor `cross()` finds,
and selecting it twice adds two.
Selections commute, so a whole sequence of them reduces to a count per cell.
The puzzle then becomes one linear system over the integers mod 3: `M v = b`.
`M` records which cells each selection advances, `v` counts the selections,
and `b` is how far each cell must advance to reach the target color.
`system()` builds `M` and `b` together, one row per cell,
with `b` in the last column.

**Decide solvability by elimination.**
`solvable()` answers whether that system has a solution,
which is all the question asks: which colors are reachable, not how.
It is Gaussian elimination, with two changes for arithmetic mod 3.
Dividing by a pivot is multiplying by its inverse,
which `pow(x, -1, MOD)` supplies, and every subtraction ends in `% MOD`.

If you leave the `% MOD` off the subtraction, as ordinary elimination would,
an entry can become a nonzero multiple of three.
`next()` accepts such an entry as a pivot, since it is not zero.
`pow(x, -1, MOD)` then raises a `ValueError`
("base is not invertible for the given modulus"),
so the script stops at 3x3 before printing a line.

**Check the zero rows.**
Elimination either finds a pivot in a column or leaves that column free.
The rows whose coefficients are all zero after elimination determine the answer.
Such a row states `0 == row[-1]`,
so a nonzero last column means no count of selections reaches that color.

**Report the reachable colors.**
The six sizes split three ways.
At 3x3, 6x6, and 7x7 the matrix has full rank,
so every color is reachable from any starting grid.
At 4x4 the rank is 14 of 16, and at 8x8 it is 60 of 64.
Each missing dimension is a combination of cells that every selection leaves unchanged,
so the starting grid must agree with the target on each such combination.
The 4x4 banded grid agrees for all three colors,
and the 8x8 grid for `palegreen` alone, which is the puzzle the window poses.
At 5x5 three dimensions are missing and no color satisfies them,
so no sequence of selections turns that board one color.

`Color` is a `StrEnum`,
so its members are strings and go straight into `", ".join(reachable(size))`.
String members also let `grid_view.py` pass a `Color` to `tkinter`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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
> Show that an assignment to one attribute calls that attribute's responders alone.

<details>
<summary>Where to look</summary>

As [A Descriptor That Validates](../../Chapters/17_Techniques--Metaprogramming.md#a-descriptor-that-validates)
shows, a descriptor's `__set_name__()` receives the attribute's name,
from which it can derive one storage name and one responder-list name per attribute.
`__set__()` stores the value and then calls that attribute's responders.
`__get__()` returns `self` when `obj` is `None`,
so `Thermometer.celsius.connect()` reaches the descriptor,
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
<summary>Done when</summary>

assigning `celsius` twice and `humidity` once on one `Thermometer` leaves two readings in the `celsius` responder's list and one in the `humidity` responder's list.
`uv run ty check` passes on a file that holds both `Thermometer.celsius.connect(t, readings.append)` and `t.celsius * 2`.

<details>
<summary>Solution</summary>

```python
# exercise_10.py
from collections.abc import Callable
from typing import overload

type Responder[T] = Callable[[T], None]

class Notifying[T]:
    def __set_name__(
        self, owner: type, name: str
    ) -> None:
        self._storage = f"_{name}"
        self._responders = f"_responders_{name}"

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
        return getattr(obj, self._storage)

    def __set__(self, obj: object, value: T) -> None:
        setattr(obj, self._storage, value)
        for responder in getattr(obj, self._responders, ()):
            responder(value)

    def connect(self, obj: object,
                responder: Responder[T]) -> None:
        obj.__dict__.setdefault(
            self._responders, []).append(responder)

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

**Give each attribute its own storage.**
`__set_name__()` receives the name each descriptor has in the class body,
so `celsius` and `humidity` derive different attribute names:
`_celsius` and `_responders_celsius` for one,
`_humidity` and `_responders_humidity` for the other.
Two `Notifying` instances in one class therefore keep separate storage and separate responder lists.
`Broadcaster` keeps one list for the whole object;
a descriptor keeps one per attribute.

**Return the descriptor on class access.**
Class access is the part a validating descriptor never needs.
`Thermometer.celsius` calls `__get__()` with `obj` set to `None`.
Returning the descriptor there lets `Thermometer.celsius.connect()` call the descriptor's method.

If `__get__()` always returns the stored value,
as a validating descriptor's `__get__()` does,
`Thermometer.celsius` runs `getattr(None, "_celsius")` and raises an `AttributeError` before the call to `connect()`.
The type checker passes that version,
since the overloads still declare that class access returns the descriptor.
The failure appears only when the program runs.

**Type each kind of access.**
If you remove the two `@overload` declarations,
the declared return type is the union.
The type checker then rejects `t.celsius * 2`,
and `Thermometer.celsius.connect()` as well, since `float` has no `connect()`.
The overloads also check the responder against the attribute:
`Thermometer.celsius.connect(t, readings.append)` passes because `readings.append` accepts a `float`.

Pyright rejects `Thermometer.celsius.connect`.
It reads the constructor's `self.celsius = celsius` as declaring an instance attribute of type `float` beside the descriptor,
so it types the class access as `Notifying[float] | float` and reports that `float` has no `connect`.
`ty` types the class access from the `__get__()` overload alone.
A codebase on Pyright looks the descriptor up in `type(obj).__dict__`,
which Pyright accepts.

**Announce on assignment.**
`Thermometer`'s property setter does the work of `__set__()` with `self.announce(value)`.

**Keep each instance's responders apart.**
`connect()` writes the responder list into the instance's `__dict__` rather than declaring it on the class,
where every instance would share one list.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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
> which it removes, and which new problems it brings that `Broadcaster` avoids.

<details>
<summary>Where to look</summary>

Two pieces make every decorated `def` a registration:
a module-level list and a decorator that appends its function and returns it unchanged.
For the comparison, reread the problems the runtime sections raise after [The Pythonic *Observer*](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer):
disconnecting, a raised exception, lapsed listeners,
and re-entrant notification.

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
<summary>Done when</summary>

an assignment to either thermometer's `celsius` reaches every decorated responder,
a decorated function still runs when called by name,
and `uv run ty check` passes.
You can name three runtime problems the load-time form removes, two it keeps,
and three it brings that `Broadcaster` avoids.

<details>
<summary>Solution</summary>

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

**Register at definition time.**
Python calls `responds()` once for each decorated `def`,
when it runs that statement.
For a module-level function, that is while Python imports the module,
so the registry is complete before any thermometer exists.

**Keep the function callable.**
`responds()` returns `fn` unchanged,
so `display` is still a function you can call by name.

If `responds()` appends the function and returns `None`,
the demo still prints its three lines, because `RESPONDERS` holds each function.
The decorator's result replaces the name, though,
so the name `display` refers to `None`.
Calling `display(5.0)` then raises a `TypeError`.
The type checker catches the mistake before any run.
With `-> Responder` declared,
it reports an `invalid-return-type` on `responds()`.

The return value also separates `Broadcasting.respond()` from the chapter's `Broadcaster.connect()`.
`connect()` appends and returns `None`,
so `@thermometer.connect` above a `def` binds that name to `None`.
`respond()` exists to return the function.

The load-time form removes three of the runtime problems:

- `Broadcaster.announce()` copies its list because a responder can disconnect itself mid-notification.
  The registry has no `disconnect()`,
  so the setter iterates over `RESPONDERS` and skips the copy.
- A lambda written inline in `connect()` leaves its caller nothing to pass to `disconnect()`.
  That problem disappears along with `disconnect()`.
  The `@` form also needs a `def`, so every decorated responder has a name.
- A lapsed listener is an object kept alive by its connection.
  The registry holds module-level functions,
  and their module keeps them alive for the whole program.
  The registry's strong references therefore keep nothing alive that Python would otherwise collect.

Two problems remain.
A responder that raises an exception stops the loop,
and the exception propagates to the assignment to `celsius`.
A responder that assigns to `celsius` re-enters the setter.

The load-time form also brings three problems that `Broadcaster` avoids:

- The registry is global.
  `room` and `oven` announce to the same two responders,
  and `alarm` receives a reading with no reference to the thermometer that changed.
  `Broadcaster` keeps one list per instance.
  Sending the thermometer along with the reading tells the responders the source,
  but every responder still receives every thermometer's changes.
- A responder registers only if Python imports its module.
  A responder in a module that nothing imports does not run,
  and nothing reports its absence.
  Django's documentation handles this by importing an app's signal handlers from its `AppConfig.ready()` method,
  which Django calls at startup.
- Tests share the registry.
  A test that decorates a responder leaves that responder registered for every later test,
  so the test must remove the responder from `RESPONDERS` before it ends.

The first of those problems, the shared registry,
comes from storing the list at module level rather than from the decorator.
[Decorated Responders](../../Chapters/30_Patterns--Observer.md#decorated-responders)
keeps registration by decorator and moves the list onto each instance.
`Broadcasting` is a base class whose `respond()` method is a decorator,
so `@thermometer.respond` appends a function to that thermometer's own list and returns the function unchanged.
In that form, `room` and `oven` each announce to their own responders.
A test creates its own thermometer and registers against it,
so each test has a registry of its own too.
The import problem stays.
A responder registers when Python runs its `def`,
so a responder in a module nothing imports still registers nothing.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 12. A name with each announcement

> Give `Broadcasting` the name-and-value pair of `weather_station.py`:
> `published()`'s setter announces the field's name paired with the new value,
> so each responder receives a `tuple[str, T]`.
> Declare a subclass with `celsius` and `humidity` fields,
> and attach one responder that reports `celsius` readings and lets `humidity` pass.
> Show that an assignment to either field reaches that responder,
> so filtering by name is the responder's job, as it is for `WeatherStation`.

<details>
<summary>Where to look</summary>

`published()` receives the field's name when `__init_subclass__()` builds each property,
so `write()` can pair that name with the value and pass the pair to `announce()`.
Make the payload a `tuple[str, T]`,
so `Responder[T]` takes that tuple and `announce()` passes the pair through unchanged.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_12.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, dataclass_transform

type Responder[T] = Callable[[tuple[str, T]], None]

def published(name: str) -> property:
    ...

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls, **kwargs: object) -> None:
        ...

    @property
    def _responders(self) -> list[Responder[T]]:
        ...

    def respond(
        self, responder: Responder[T]
    ) -> Responder[T]:
        ...

    def disconnect(self, responder: Responder[T]) -> None:
        ...

    def announce(self, data: tuple[str, T]) -> None:
        ...

class Station(Broadcasting[float]):
    celsius: float
    humidity: float

station = Station(20.0, 0.4)

@station.respond
def report(change: tuple[str, float]) -> None:
    ...
```

<details>
<summary>Done when</summary>

after you attach your responder,
assigning `celsius` and then `humidity` calls it twice,
first with `('celsius', <value>)` and then with `('humidity', <value>)`,
and it reports the first alone.
`uv run ty check` passes with the responder's parameter declared `tuple[str, float]`.

<details>
<summary>Solution</summary>

The solution changes two places.
`published()` closes over the field's name,
so `write()` reads `name` from the closure and calls `self.announce((name, value))`.
In `Broadcasting` the payload becomes a `tuple[str, T]`.
`Responder[T]` becomes `Callable[[tuple[str, T]], None]`,
and `announce()` passes the pair through to each responder unchanged.
`__init_subclass__()`, `respond()`,
and `disconnect()` stay as the chapter writes them.

```python
# exercise_12.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, dataclass_transform

type Responder[T] = Callable[[tuple[str, T]], None]

def published(name: str) -> property:
    def read(self: Any) -> Any:
        return self.__dict__[name]

    def write(self: Any, value: Any) -> None:
        self.__dict__[name] = value
        self.announce((name, value))

    return property(read, write)

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        built = dataclass(eq=False)(cls)
        for field in fields(built):
            prop = published(field.name)
            setattr(cls, field.name, prop)

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(
        self, responder: Responder[T]
    ) -> Responder[T]:
        self._responders.append(responder)
        return responder

    def disconnect(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: tuple[str, T]) -> None:
        for responder in list(self._responders):
            responder(data)

class Station(Broadcasting[float]):
    celsius: float
    humidity: float

station = Station(20.0, 0.4)
calls: list[str] = []

@station.respond
def report(change: tuple[str, float]) -> None:
    name, value = change
    calls.append(name)
    if name == "celsius":
        print(f"report: {value}C")

station.celsius = 25.0
#: report: 25.0C
station.humidity = 0.5
print(calls)
#: ['celsius', 'humidity']
```

**Announce the name from the property.**
`__init_subclass__()` calls `published(field.name)` once per field,
and each `write()` closes over its own `name`.
An assignment to `station.humidity` runs the `humidity` property's `write()`,
which announces `"humidity"`,
so the closure tells `Broadcasting` which field changed.

**Filter in the responder.**
`announce()` calls every responder for every field,
as `WeatherStation.__setattr__()` does.
The one `report:` line comes from the `celsius` assignment,
and `calls` shows that both assignments called `report()`,
including the one to `humidity`.

**Share one type across the fields.**
`Broadcasting[float]` gives every field's responders the same `T`,
so `celsius` and `humidity` are both `float`.
A subclass whose fields have different types declares `Broadcasting[object]`,
and its responders narrow the value after checking the name.
`object` is also the value type in `WeatherStation`'s `Change` tuple,
`tuple[str, object]`.

The generated `__init__()` assigns both fields through their properties,
so constructing `station` announces twice.
The responder list is still empty then,
so `calls` holds the two assignments that follow `@station.respond`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 13. A second view on the counter

> Connect a second view to `model_view_controller.py`'s `Counter`:
> one that prints a bar of asterisks as long as the count,
> beside the `CountView` that prints the number.
> Drive both with a `Controller` whose keys are `k` and `j`,
> and show that one key updates the pair.
> Then say what each class knows about the others,
> and which of them a third view would require you to change.

<details>
<summary>Where to look</summary>

In [Document-View and MVC](../../Chapters/30_Patterns--Observer.md#document-view-and-mvc),
`CountView` connects its `display()` to the model in `__post_init__()`.
A second view does the same with its own display method,
and a `Controller` that drives the `Counter` feeds both.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_13.py
from collections.abc import Callable
from record import record

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        ...

    def connect(self, responder: Responder[T]) -> None:
        ...

    def announce(self, data: T) -> None:
        ...

class Counter(Broadcaster[int]):
    def __init__(self) -> None:
        ...

    @property
    def count(self) -> int:
        ...

    def increment(self) -> None:
        ...

    def decrement(self) -> None:
        ...

@record
class CountView:
    model: Counter

    def __post_init__(self) -> None:
        ...

    def display(self, count: int) -> None:
        ...

@record
class BarView:
    model: Counter

    def __post_init__(self) -> None:
        ...

    def display(self, count: int) -> None:
        ...

@record
class Controller:
    model: Counter
    up: str = "+"
    down: str = "-"

    def key(self, char: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

feeding `k`, `k`, `j` to your `Controller` prints six lines,
each count beside a bar of that many asterisks, ending at a count of 1.
You can say which objects `Counter`, each view, and `Controller` each reference,
and whether a third view would change any existing class.

<details>
<summary>Solution</summary>

```python
# exercise_13.py
from collections.abc import Callable
from record import record

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)

class Counter(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def increment(self) -> None:
        self._count += 1
        self.announce(self._count)

    def decrement(self) -> None:
        self._count -= 1
        self.announce(self._count)

@record
class CountView:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"count: {count}")

@record
class BarView:
    model: Counter

    def __post_init__(self) -> None:
        self.model.connect(self.display)

    def display(self, count: int) -> None:
        print(f"[{'*' * count}]")

@record
class Controller:
    model: Counter
    up: str = "+"
    down: str = "-"

    def key(self, char: str) -> None:
        match char:
            case self.up:
                self.model.increment()
            case self.down:
                self.model.decrement()
            case _:
                pass

model = Counter()
view = CountView(model)
bar = BarView(model)
vim = Controller(model, up="k", down="j")
for char in "kkj":
    vim.key(char)
#: count: 1
#: [*]
#: count: 2
#: [**]
#: count: 1
#: [*]
```

Each key press updates both views through the model.
The views print in the order they connected.
The controller holds no reference to either view.

This copy of `Controller` drives the `Counter` alone,
since the exercise concerns views on the `Counter`.
The chapter's `Controller` also records each key in a `History` model,
and a second view connects to `History` the same way.

`Counter` knows a list of responders and nothing about views or controllers.
Each view knows the `Counter` to which it connects.
The controller knows the `Counter` to which it sends requests.
Each view and the controller hold the model, and none of them holds another.

A third view leaves every existing class as it is.
The new view connects in its own `__post_init__()`.
In `document_view.py` the controller is a method of the one view,
so a second view either duplicates `key()` or has no input of its own.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
