# Observer

The *Observer* pattern, a kind of callback,
decouples code that changes state from code that reacts to the change.
An *observer* registers interest with an *observable*.
Whenever the observable changes state, it notifies the observer.
The observable only defines a list of callables and the arguments it passes to those callables.
That choice follows [the principle of designing the communication rather than the parts](21_Patterns--Design_Patterns.md#design-principles).
*Observer* is the most dynamic of the callback patterns because observers attach and detach at runtime,
and the observable does not name their concrete types.

Event handling is the everyday use.
A widget keeps a list of handlers and calls each one when its event arrives.
More generally, use *Observer* if a group of objects must update themselves when other objects change state.
The classic example is Smalltalk's MVC (model-view-controller),
or the nearly-equivalent Document-View architecture.
A *document* has more than one way to view it, for example a plot and a table.
When the data changes, every view must refresh.
With *Observer*, a change in the observable data notifies each interested view.

The classic design comes from *GoF Design Patterns*,
which calls the observable the *subject*.
Here, we use `Observable` because it says what the object does.
It is also the name used by `java.util.Observable` and the reactive libraries.

The design has three parts: an `Observer` interface every observer implements,
an `Observable` base class that keeps the observer list,
and `Observable.notify()` that broadcasts to every observer:

```python
# classic_observer.py
from typing import Protocol

class Observer[T](Protocol):
    def update(
        self, observable: Observable[T], arg: T
    ) -> None: ...

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def attach(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Display:
    def update(
        self, observable: Observable[float], arg: float
    ) -> None:
        print(f"display: {arg}C")

class Thermometer(Observable[float]):
    def set_celsius(self, value: float) -> None:
        self.notify(value)

t = Thermometer()
t.attach(Display())
t.set_celsius(25)
#: display: 25C
```

`update()` is where each observer modifies itself.
`notify()` calls it on every observer in the list,
so one change to the observable's state reaches all of them:
`Display` prints the new reading, and a plot or a table would redraw.

![One call to set_celsius() becomes one update() call on every observer in the list](_images/observer_broadcast)

`Thermometer` holds the list and names no observer type,
so `Plot` and `Table` attach the same way `Display` does.

Passing `arg` is the *push* model.
The observable (`Thermometer`) supplies what changed (the temperature),
so an observer needs no reference back into the observable's state.
The *pull* model sends only `observable` and lets each observer read what it needs by calling back into the observable.
This further decouples observer and observable.

GoF leaves one choice open: who calls `notify()`.
Here `set_celsius()` calls it, so every change broadcasts at once.
The alternative leaves that call to the client,
so several changes can coalesce into one broadcast,
but a caller can forget to make the call.

The `list(self._observers)` copy inside `notify()` looks redundant,
since `_observers` is already a list.
It is not.
An observer may react to a notification by detaching.
A one-shot listener detaches after its first call,
and the detach mutates `self._observers` in the middle of the loop walking it.
If you iterate the list directly,
removing the current observer lowers every later observer's index by one,
while the loop's own index keeps advancing, so the loop skips the next observer.
No exception reports the skip.
Walking a copy makes detaching during notification safe,
and a newcomer attaching mid-notification receives its first notification at the next change.

## The Pythonic Observer: a List of Callables

In Python an observer is any callable,
and an observable is a list of callables plus a way to notify them.
A `@property` setter runs at every assignment to its attribute,
so the setter is the place to send the notification when state changes:

```python
# observers.py
from collections.abc import Callable

type Observer[T] = Callable[[T], None]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def subscribe(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self, data: T) -> None:
        for observer in list(self._observers):
            observer(data)

class Thermometer(Observable[float]):
    def __init__(self) -> None:
        super().__init__()
        self._celsius = 0.0

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)
```

Subscribed callables then react to every assignment to `celsius`:

```python
# thermometer.py
from observers import Thermometer

t = Thermometer()
t.subscribe(lambda c: print(f"display: {c}C"))
t.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
t.celsius = 25
#: display: 25C
#: ok
t.celsius = 150
#: display: 150C
#: alarm!
```

The observers here are lambdas, but any function or bound method works.
Four things from the classic version disappear: the `Observer` interface,
its `update()` method, a class per reaction, and the `observable` argument.
A classic observer is an object,
so the observable needs the name of a method to call on it.
In Python the observer is the callable, so `notify()` calls it directly:
`observer(data)` where the classic version called `observer.update(self, arg)`.
The remaining method names change as well:
GoF's `attach()` and `detach()` become `subscribe()` and `unsubscribe()`,
as in the reactive libraries.
An observer that needs the changed object takes it as part of the payload
(`notify((self, value))`),
or subscribes a bound method whose instance already holds the reference.

`Thermometer` inherits `Observable` because that is the shortest way to get `subscribe()` and `notify()`,
not because the pattern requires a base class.
Holding one as an attribute (`self.temperature_changed = Observable[float]()`)
works the same and lets one object publish more than one kind of change.
Event-heavy programs have mature libraries (signal/slot systems),
but for most cases the *Observer* pattern is only a list of callbacks.

`Thermometer` writes its `__init__()` by hand.
Inheriting does not stop a class from being a data class,
but a generated `__init__()` does not call the base class's `__init__()`
([Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance)),
so a `@dataclass` `Thermometer` would have no list of observers,
and `subscribe()` would raise an `AttributeError`.
A `__post_init__()` that calls `super().__init__()` fixes that,
at greater length than the `__init__()` it replaces.

An observer returns `None`.
Notification runs one way, from observable to observers, and nothing comes back.
Getting a value back is a different pattern,
such as [*Chain of Responsibility*](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime)
for the first handler that answers.

Testing confirms that every subscriber receives the new value in subscription order,
that a subscriber receives only the changes made after it subscribes,
and that delivery stops after `unsubscribe()`:

```python
# test_observers.py
from observers import Observable, Thermometer

def test_notify_calls_every_subscriber() -> None:
    received: list[tuple[str, object]] = []
    obs = Observable[int]()
    obs.subscribe(lambda d: received.append(("a", d)))
    obs.subscribe(lambda d: received.append(("b", d)))
    obs.notify(42)
    assert received == [("a", 42), ("b", 42)]

def test_no_subscribers_is_a_noop() -> None:
    # Must not raise anything
    Observable[str]().notify("anything")

def test_unsubscribe_stops_delivery() -> None:
    received: list[object] = []
    obs = Observable[object]()
    # A bound method: equal, not identical
    record = received.append
    obs.subscribe(record)
    obs.notify(1)
    obs.unsubscribe(record)
    obs.notify(2)
    assert received == [1]

def test_thermometer_pushes_new_value_on_set() -> None:
    readings: list[float] = []
    t = Thermometer()
    t.subscribe(readings.append)
    t.celsius = 25.0
    t.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert t.celsius == 150.0

def test_late_subscriber_misses_earlier_changes() -> None:
    readings: list[float] = []
    t = Thermometer()
    t.celsius = 10.0  # No subscriber yet
    t.subscribe(readings.append)
    t.celsius = 20.0
    assert readings == [20.0]
```

The tests subscribe a list's `append`, so the list records what arrived.
`unsubscribe()` matches by equality, and a lambda equals only itself,
so a detachable observer needs a named reference, not an inline lambda.
A bound method needs no stashed reference.
Writing `obj.update` twice builds two distinct objects that compare equal,
because they share an instance and a function.
`unsubscribe(obj.update)` therefore finds the one that subscribed.
`unsubscribe()` delegates to `list.remove()`,
so detaching an observer that never subscribed raises a `ValueError`.
Subscribing the same callable twice means two notifications and two `unsubscribe()` calls to stop them.

The copy in `notify()` shows its value when an observer unsubscribes mid-notification:

```python
# self_removing_observer.py
from observers import Observable

obs = Observable[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Detaches itself mid-notification
    obs.unsubscribe(once)

obs.subscribe(once)
obs.subscribe(lambda d: seen.append(f"always: {d}"))
obs.notify(1)
obs.notify(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` receives the first change and detaches.
`always` receives both.
Without the copy, `once`'s self-removal would skip `always`,
and `always: 1` would be missing.

An observer that raises an exception stops the loop,
and the observers after it are not called.
Decide whether `notify()` should catch, collect, and continue
(exercise 3 makes this concrete).

Subscriptions are strong references.
An observable that outlives its observers keeps alive the instance behind every subscribed bound method,
the classic *lapsed listener* leak.
Long-lived observables need disciplined `unsubscribe()` calls,
or [weak references](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
which do not keep the observer alive
(`weakref.WeakMethod` is the bound-method form).

An observer that writes back to the observable re-enters `notify()` from inside `notify()`.
Two-way bindings are the usual source.
The view edits the model, the model notifies the view, the view edits the model.
Without a guard, an observer that always writes back recurses until Python raises a `RecursionError`:

```python
# reentrant_notify.py
from exceptions import expected
from observers import Observable

class TwoWay(Observable[int]):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int) -> None:
        self._value = new
        self.notify(new)  # Re-enters if written back

model = TwoWay()
model.subscribe(
    lambda v: setattr(model, "value", v))
with expected(RecursionError):
    model.value = 1
#: [RecursionError] maximum recursion depth exceeded
```

The setter calls `notify()`, the observer writes back through the same setter,
and each write calls `notify()` again.
Making the write conditional on the value changing breaks the cycle:

```python
# reentrant_notify_fixed.py
from observers import Observable

class TwoWay(Observable[int]):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int) -> None:
        if new == self._value:
            return  # Breaks the re-entry
        self._value = new
        self.notify(new)

model = TwoWay()
seen: list[int] = []

def echo(v: int) -> None:
    seen.append(v)
    model.value = v  # Now a no-op

model.subscribe(echo)
model.value = 1
print(seen)
#: [1]
```

Because `echo`'s write-back matches the value the setter already holds,
the setter returns before it reaches `notify()` again.
The model still notifies once.
The alternative is a re-entry flag set before `notify()` and cleared after.
The flag breaks the cycle too,
and fits the case where a write of an unchanged value should still proceed.

## Observer and I/O

Until now, no observer has waited on anything.
Each prints, appends, or writes back, then returns.
If an observer calls a network service or writes to a database,
notifying observers one at a time blocks on each.
Each observer's wait delays every observer after it.

If observers are coroutines,
`notify()` awaits them together with `asyncio.gather()`,
so one state change notifies every observer concurrently.
A slow observer no longer delays the others.
`gather()` still waits for all of them,
so the change finishes only after every notification succeeds.

One limitation: an `async` setter returns a coroutine instead of running its body,
and an assignment offers no place for the `await` that would run the coroutine.
The assignment therefore discards the coroutine, and the body never runs.
The state change becomes an awaitable method rather than the assignment `t.celsius = value`.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
covers the `asyncio` mechanics here (`async def`, `await`, `gather()`, `run()`).
For this example, you only need a coroutine that pauses at `await` while others run:

```python
# async_observers.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver[T] = Callable[[T], Awaitable[None]]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver[T]] = []

    def subscribe(self, observer: AsyncObserver[T]) -> None:
        self._observers.append(observer)

    def unsubscribe(
        self, observer: AsyncObserver[T]
    ) -> None:
        self._observers.remove(observer)

    async def notify(self, data: T) -> None:
        # Fan out to every observer, then wait for all
        await asyncio.gather(
            *(obs(data) for obs in self._observers))

class Thermometer(Observable[float]):
    def __init__(self) -> None:
        super().__init__()
        self._celsius = 0.0

    @property
    def celsius(self) -> float:
        return self._celsius

    async def set_celsius(self, value: float) -> None:
        # A property setter cannot be awaited
        self._celsius = value
        await self.notify(value)

async def alarm(celsius: float) -> None:
    if celsius > 100:
        await asyncio.sleep(0.05)  # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)  # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer()
    t.subscribe(alarm)
    t.subscribe(log_reading)
    await t.set_celsius(20)  # Below the alarm threshold
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
```

The `AsyncObserver` alias makes the type checker reject a plain function as an observer.
An observer must return an awaitable,
and calling an `async` function produces one.
The type checker also rejects the reverse mistake,
an `async` function subscribed to the synchronous `Observable`.
Calling that function returns a coroutine rather than `None`,
and a coroutine discarded without an `await` does nothing.
The alias's type parameter does the same job as the synchronous `Observer[T]`'s.

`notify()` needs no `list()` copy here.
The `*` unpacks the generator into a tuple of coroutines before `gather()` runs,
so a detach during the fan-out cannot skip an observer.
The tuple also means an observer that unsubscribes mid-notification still receives this change,
an async counterpart to `self_removing_observer.py`:

```python
# async_self_removing_observer.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver[T] = Callable[[T], Awaitable[None]]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver[T]] = []

    def subscribe(
        self, observer: AsyncObserver[T]
    ) -> None:
        self._observers.append(observer)

    def unsubscribe(
        self, observer: AsyncObserver[T]
    ) -> None:
        self._observers.remove(observer)

    async def notify(self, data: T) -> None:
        await asyncio.gather(
            *(obs(data) for obs in self._observers))

obs = Observable[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    obs.unsubscribe(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    obs.subscribe(once)
    obs.subscribe(always)
    await obs.notify(1)
    await obs.notify(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

This listing repeats `async_observers.py`'s `Observable` rather than importing it,
because that module's own top-level `asyncio.run(main())` would run its thermometer demo again on import.

`once` unsubscribes mid-notification and still receives that notification,
because `gather()` already holds its coroutine before `once` runs.
The next `notify()` no longer calls it.

The `alarm` is slower than the log, yet the log prints first.
Awaiting the observers in sequence would print in subscription order,
alarm first.
Concurrent fan-out lets each observer finish as soon as its own wait ends,
so the faster observer prints first.
The results `gather()` returns stay in argument order regardless.
Only the side effects interleave.

An observer need not act on every notification.
Below its threshold, the alarm returns at once.

A failing observer behaves differently here than in the synchronous version.
`gather()` re-raises the first exception into `set_celsius()` right away,
and the unfinished observers keep running with nobody awaiting them:

```python
# gather_orphan.py
import asyncio
from exceptions import aexpect

async def loud(data: int) -> None:
    raise ValueError(f"bad: {data}")

async def slow(data: int) -> None:
    await asyncio.sleep(0.05)
    print(f"slow finished: {data}")

async def main() -> None:
    await aexpect(
        ValueError, asyncio.gather, loud(1), slow(1))
    await asyncio.sleep(0.25)  # Let the orphan finish

asyncio.run(main())
#: [ValueError] bad: 1
#: slow finished: 1
```

The failure prints the moment `loud()` raises its `ValueError`.
`slow` is still sleeping at that point, with nothing left awaiting it,
and it prints only because `main()` sleeps long enough afterward to let it finish.
A real caller rarely adds that wait.
The program moves on before the orphan finishes,
and an exception the orphan later raises is never retrieved.
`gather(*coros, return_exceptions=True)` returns the failures as data instead,
the async form of exercise 3's catch-collect-continue.
[Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup` is the usual choice for concurrent awaits,
but not here.
A `TaskGroup` cancels a failing task's siblings,
so a single broken observer would cancel the others mid-notification.

Use the async fan-out only when the observers are I/O-bound.
For in-memory observers the synchronous `Observable` from `observers.py` is simpler and needs no event loop.
The type-keyed [event bus](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
is the same fan-out, routed by event type.

## A Visual Example of Observers

The last example is the model-view split made visible.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule for a click.
It only manipulates `Grid`s and doesn't know anything about displaying them.
The *view*, `box_view.py`,
displays the boxes using the standard library's `tkinter`.
Clicking a box advances it to the next color, along with the boxes above, below,
left, and right of it.
A click changes up to five boxes at once, so the window is a puzzle:
try to turn every box `palegreen`.
From this starting grid, `palegreen` is the one color all the boxes can share.
No sequence of clicks turns the grid all `skyblue` or all `khaki`.

The model reuses the same `Observable` as the thermometer, from `observers.py`:

```python
# box_observer.py
from enum import StrEnum
from observers import Observable

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    def next(self) -> Color:
        colors = list(Color)
        nxt = colors.index(self) + 1
        return colors[nxt % len(colors)]

type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, clicked: Coord) -> Grid:
    x, y = clicked
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class BoxModel(Observable[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.notify(self.grid)
```

`Color` is a `StrEnum`, an `Enum`
([Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too))
whose members are also strings.
`Color.KHAKI` compares equal to `"khaki"` and goes wherever a `str` goes,
so the view can pass a `Color` to `tkinter` as a color name.
Iterating over an enum produces its members in definition order,
so `list(Color)` is the cycle of colors.
`next()` finds the member's position in that list with `index()` and adds one.
`nxt` is the position of the next color,
and `nxt % len(colors)` wraps it around,
so `Color.KHAKI.next()` is `Color.SKYBLUE`.

A `Grid` maps each `(column, row)` coordinate to a `Color`.
`new_grid()` builds a size x size grid banded into three colors.
A cell's color is `colors[(x + y) % len(colors)]`,
so the cells along a diagonal, where `x + y` is constant, share one color.

`recolored()` computes the grid that results from a click: values in,
values out.
`cross` lists the clicked cell and the four cells that share an edge with it.
A cell on the border has fewer neighbors,
so some of the coordinates in `cross` lie outside the grid.
A `Grid` is keyed by coordinate,
so `cell in grid` is only `True` for a coordinate inside the grid.
The comprehension's `if` clause applies that test and skips the outside coordinates,
so `recolored()` needs no grid size.
The comprehension maps each cell that passes the test to its color's `next()`.
The dictionary merge from [Containers](03_Foundations--Containers.md#dictionaries)
builds the new grid: `|` produces a new dictionary,
and when both operands hold the same key, the right operand's value wins.
The result is a copy of `grid` that differs in the cells of the cross,
and `grid` is unchanged.

Neither function needs a `BoxModel`,
so both are defined at module level and not inside the class.
A test calls them directly, and a second model can reuse them.
`BoxModel` is an `Observable[Grid]`.
Like `Thermometer`, it writes its own `__init__()`,
which calls `Observable.__init__()` and then builds `grid` from `size`.
`BoxModel.click()` makes the next grid with `recolored()` and passes it to `notify()`.
An enum, two functions, and one class make up the model:
`Color` holds the colors and their order, the functions compute grids,
and `BoxModel` holds the current grid and notifies its observers.

The model contains no display code so it can be tested without the challenges of a GUI.
Testing confirms that `recolored()` changes the cross and no other cell,
that a click in a corner stays on the grid,
and that observers receive the new grid after a click:

```python
# test_box_observer.py
from box_observer import (BoxModel, Color, Grid,
                          new_grid, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == Color.SKYBLUE
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_next_wraps() -> None:
    assert Color.SKYBLUE.next() == Color.PALEGREEN
    assert Color.KHAKI.next() == Color.SKYBLUE

def test_recolored_changes_the_cross() -> None:
    grid = new_grid(3)
    out = recolored(grid, (1, 1))
    cross = {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}
    assert all(out[c] == grid[c].next() for c in cross)
    assert all(out[c] == grid[c]
               for c in grid if c not in cross)
    assert out is not grid  # Pure: a new grid

def test_corner_click_stays_on_the_grid() -> None:
    grid = new_grid(3)
    out = recolored(grid, (0, 0))
    changed = {c for c in grid if out[c] != grid[c]}
    assert changed == {(0, 0), (1, 0), (0, 1)}
    assert out.keys() == grid.keys()

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    # The observer is a callable
    model.subscribe(seen.append)
    model.click((1, 1))
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
```

The view lives in its own file.
It is the only code that draws to the screen.
Run `box_view.py` to play.
It opens a window, so the example harness skips it
(`tools/data/norun.txt` lists it).

```python
# box_view.py
import tkinter as tk
from box_observer import BoxModel, Grid

def show(model: BoxModel, cell_px: int = 60) -> None:
    root = tk.Tk()
    root.title("ColorBoxes")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=model.size * cell_px,
                       height=model.size * cell_px)
    canvas.pack()

    def draw(grid: Grid) -> None:
        # Or the old rectangles accumulate
        canvas.delete("all")
        for (x, y), color in grid.items():
            canvas.create_rectangle(
                x * cell_px, y * cell_px,
                (x + 1) * cell_px, (y + 1) * cell_px,
                fill=color, outline="white")

    model.subscribe(draw)  # Repaint on every model change
    canvas.bind("<Button-1>",
                lambda e: model.click(
                    (e.x // cell_px, e.y // cell_px)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
```

`show()` makes a square canvas, `model.size` cells on a side,
each cell `cell_px` pixels wide.
`draw()` paints the grid, and the view subscribes `draw()`,
so every change repaints.
`draw()` is defined inside `show()`,
so it is a closure that reads `canvas` and `cell_px`.
It paints one rectangle per cell,
multiplying the cell's column and row by `cell_px` to get the rectangle's corners in pixels.
It takes a `Grid` and returns `None`,
the shape `subscribe()` requires of an observer.
No notification has arrived when the window opens,
so `show()` calls `draw(model.grid)` once to paint the starting grid.

`draw()` clears the canvas before repainting.
Without that line each notification adds another `size * size` rectangles on top of the last set.
The window looks the same while the canvas's list of items grows without limit,
the same quiet accumulation as a lapsed listener.

`canvas.bind()` registers the lambda as the handler for `"<Button-1>"`,
a press of the left mouse button.
`tkinter` calls the handler with an event `e`,
and `e.x` and `e.y` give the click's position in pixels,
measured from the canvas's top-left corner.
Floor division by `cell_px` converts that position to a cell:
with 60-pixel cells, a click at `e.x == 130` is in column `130 // 60`,
which is `2`.
A click on the canvas becomes a model `click()`,
and the resulting notification repaints the view.
The handler calls the model and draws nothing.

The model and the view share only the subscribe-and-notify contract,
so you can attach a second view to the same model and keep both views in step.

## What Stayed Constant

One design served three jobs in this chapter: a thermometer pushing a float,
a fan-out awaiting network calls, and a GUI repainting a grid.
In every case the observer was a callable and the observable was a list of them.
Nothing in the pattern required an interface, a flag, or a class per reaction.
[Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
already took the last step.
One list becomes a dictionary of lists keyed by event type,
and the *Observer* is an event bus.

## Exercises

1.  Create a minimal *Observer* design of your own,
    without looking at `observers.py`:
    the smallest `Observable` that lets callables subscribe, then notifies them.
    Demonstrate it by subscribing several observers and causing one change that updates them all.
2.  Turn `box_observer.py` into a simple game:
    you own the contiguous patch of same-colored squares containing the top-left corner,
    and clicking any square recolors your patch to that square's color,
    absorbing neighbors that now match.
    Write the neighbor test yourself, counting diagonals.
    Track the clicks it takes to make the whole field one color.
    For competition, alternate turns between players.
3.  Make `Observable.notify()` survive an observer that raises an exception:
    every other observer is still notified,
    and `notify()` re-raises the failures afterward, together,
    as an [`ExceptionGroup`](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
    (which you build yourself here: `raise ExceptionGroup("message", failures)`).
    Write a test in which the first observer raises an exception and the second still records its notification.
4.  Redo exercise 3 for `async_observers.py`.
    Make `notify()` use `gather(*coros, return_exceptions=True)`,
    separate the returned exceptions from the successes,
    and raise them together as an `ExceptionGroup`.
    Write a test in which the first observer raises an exception and the second still records its notification.
5.  Change the rule for a click in `box_observer.py`:
    make `recolored()` advance every box in the clicked box's row and column.
    Run `box_view.py` without editing it,
    and explain why the view needed no change.
