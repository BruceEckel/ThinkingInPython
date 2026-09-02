# Observer

The *Observer* pattern, a kind of callback,
decouples the code that changes state from the code that reacts to the change.
One object, the *observer*, registers interest in another, the *observable*,
and hears from the observable whenever its state changes.
Of the callback patterns it is the most dynamic:

- Observers attach and detach at runtime
- The observable need not know their types

It underlies event handling,
and the model-view split that keeps a display in step with the data behind it.

Use *Observer* if a group of objects must update themselves when some other object changes state.
The classic example is Smalltalk's MVC (model-view-controller),
or the almost-equivalent Document-View architecture.
You have some data, the *document*, and more than one view of it,
say a plot and a table.
When the data changes, every view must refresh.
The *Observer* pattern arranges that,
without the data knowing which views exist.

The classic design from *GoF Design Patterns* has three parts:
an `Observer` interface every observer implements,
a `Subject` base class that keeps the observer list,
and a `notify()` that broadcasts to each observer in turn:

```python
# classic_observer.py
from abc import ABC, abstractmethod
from typing import override

class Observer(ABC):
    @abstractmethod
    def update(
        self, subject: Subject, arg: object
    ) -> None: ...

class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, arg: object = None) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Display(Observer):
    @override
    def update(
        self, subject: Subject, arg: object
    ) -> None:
        print(f"display: {arg}C")

class Thermometer(Subject):
    def set_celsius(self, value: float) -> None:
        self.notify(value)

t = Thermometer()
t.attach(Display())
t.set_celsius(25)
#: display: 25C
```

Passing `arg` is the *push* model: the subject hands observers what changed,
so an observer needs no reference back into the subject's state.
The *pull* model sends only `subject` and lets each observer ask for what it wants,
which decouples the two further and costs a call back.

GoF leaves one choice open: who calls `notify()`.
Here `set_celsius()` calls it, so every change broadcasts at once.
The alternative leaves that call to the client,
which lets several changes coalesce into one broadcast,
at the price of a caller who can forget to make it.
`notify()` walks a copy of the list,
so an observer that detaches itself mid-broadcast cannot disturb the loop.

Python expresses this with far less machinery.
The rest of the chapter shows the Pythonic version first,
then extends it to async for I/O-bound observers.
It closes with a visual model-view example built on the same callable observers.

## The Pythonic Observer: a List of Callables

In Python an *observer* need not be an object implementing an `Observer` interface.
It is simply a callable.
An *observable* need not be a `Subject` base class with `attach()` and `detach()`.
It is a list of callables and a way to notify them.
A `@property` setter is a natural place to fire the notification when state changes:

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
        # Copy: observers may detach during notification
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
        # State changed; tell the observers
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
Assigning to `celsius` notifies everyone.
Three things from the classic version disappear: the `Observer` interface,
the `update()` method it demanded, and a class per reaction.
The `subject` argument goes too.
An observer that needs to know who changed takes it as part of the payload
(`notify((self, value))`),
or subscribes a bound method whose instance already holds the reference.

The type parameter carries the notification's type through to the observers,
so subscribing a `list[str]`'s `append` to a `Thermometer` fails the type checker instead of quietly collecting floats in a list of strings.

`Thermometer` inherits `Observable` because that is the shortest way to get `subscribe()` and `notify()`,
not because the pattern demands a base class.
Holding one as an attribute (`self.temperature_changed = Observable[float]()`)
works the same and lets one object publish more than one kind of change.
Event-heavy programs have mature libraries
(signal/slot systems, `asyncio` events),
but for most cases the *Observer* pattern is only a list of callbacks.

An observer returns `None`.
Notification runs one way, from observable to observers, and nothing comes back.
Getting a value back is a different pattern,
such as [Chain of Responsibility](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime)
for the first handler that answers.

The tests check that every subscriber receives the new value in subscription order,
that a subscriber sees only the changes made after it subscribes,
and that an unsubscribed observer stops hearing them.
`unsubscribe()` matches by equality, and a lambda equals only itself,
so a detachable observer needs a named reference, not an inline lambda.
A bound method needs no stashed reference.
Writing `obj.update` twice builds two distinct objects that compare equal,
because they share an instance and a function,
so `unsubscribe(obj.update)` finds the one that subscribed.
`unsubscribe()` delegates to `list.remove()`,
so detaching an observer that never subscribed raises a `ValueError`.
Subscribing the same callable twice means two notifications and two `unsubscribe()` calls to stop them.
The tests subscribe a list's `append`, so the list records what arrived:

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

The `list()` copy inside `notify()` looks redundant.
It is not.
An observer may react to a notification by unsubscribing.
A one-shot listener that detaches after its first call is the natural example,
and the detach mutates `self._observers` in the middle of the loop walking it.
If you iterate the list directly,
removing the current observer shifts every later one left,
so the loop silently skips the next observer, and nothing signals the loss.
The copy makes detaching during notification safe,
and a newcomer subscribing mid-notification starts hearing from the next change:

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

`once` hears the first change and detaches.
`always` hears both.
Without the copy, `always: 1` would be missing:
`once`'s self-removal would skip it.

An observer that raises an exception stops the loop,
and the observers after it miss the change.
Decide whether `notify()` should catch, collect, and continue
(exercise 3 makes this concrete).
Subscriptions are strong references:
an observable that outlives its observers keeps each subscribed bound method's instance alive,
the classic *lapsed listener* leak.
Long-lived observables need disciplined `unsubscribe()` calls,
or weak references (`weakref.WeakMethod`, see [Cleanup](10_Foundations--Cleanup.md#watching-objects-without-holding-them)),
which forget automatically.

An observer that writes back to the observable re-enters `notify()` from inside `notify()`.
Two-way bindings are the usual source: the view edits the model,
the model notifies the view, the view edits the model.
Either make the write conditional on the value changing,
or guard the setter with a re-entry flag.

## Observer and I/O

Until now, an observer only prints or appends to a list, then returns.
If an observer calls a network service or writes to a database,
notifying observers one at a time blocks on each.
The list of callbacks becomes a line of waits.

If observers are coroutines,
`notify()` awaits them together with `asyncio.gather()`,
so one state change reaches every observer at once.
A slow observer no longer holds up the others.
`gather()` still waits for all of them,
so the change finishes only after every notification succeeds.
One limitation: an assignment discards whatever the setter returns,
so an `async` setter never runs its body and you cannot await an assignment.
The state change moves from `t.celsius = value` to an awaitable method.
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

The `AsyncObserver` alias makes the type checker reject a plain function as an observer:
an observer must return an awaitable,
which calling an `async` function produces.
Its type parameter does the same job as the synchronous `Observer[T]`'s.
The type checker also rejects the reverse mistake,
an `async` function subscribed to the synchronous `Observable`:
calling that function returns a coroutine rather than `None`,
and a coroutine discarded without an `await` does nothing.

`notify()` needs no `list()` copy here:
`*` drains the generator into a tuple before `gather()` runs,
so a detach during the fan-out cannot skip anyone.
The tuple also means an observer that unsubscribes mid-notification still hears this change.

The `alarm` is slower than the log, yet the log prints first.
Awaiting the observers in sequence would print in subscription order,
alarm first.
Concurrent fan-out lets each finish on its own schedule,
so the faster observer reports first.
The results `gather()` hands back stay in argument order regardless.
Only the side effects interleave.
The alarm also shows an observer that can decline to act.
Below its threshold it returns without sending anything.

A failing observer behaves differently here than in the synchronous version.
`gather()` re-raises the first exception into `set_celsius()` right away,
and the unfinished observers keep running with nobody awaiting them.
`gather(*coros, return_exceptions=True)` returns the failures as data instead,
which is the async form of the catch-collect-continue that exercise 3 asks for.
[Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup` is the usual choice for concurrent awaits,
but not here: it cancels its siblings when one task fails,
so a single broken observer would stop the rest from hearing the change.

Use this only when the observers are I/O-bound.
For in-memory observers the synchronous list from earlier is simpler and needs no event loop.
The type-keyed [event bus](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
is the same fan-out, routed by event type.

## A Visual Example of Observers

The last example is the model-view split from the chapter's opening,
made visible with `tkinter` (in the standard library, so you install nothing),
and split across two files.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule for a click.
It holds no display code.
The *view*, `box_view.py`, is the only file that draws.
Clicking a box gives every box touching it, diagonals included,
the clicked box's color.

The model is an `Observable`.
`new_grid()` builds a size x size grid banded into three colors,
`adjacent()` tests whether two distinct cells touch, including diagonally,
and `recolored()` computes the grid that results from a click: values in,
values out.
`BoxModel.click()` makes the next grid with `recolored()` and announces it with `notify()`.
`tkinter` plays no part here.
The model reuses the same `Observable` as the thermometer, from `observers.py`:

```python
# box_observer.py
from typing import Final
from observers import Observable

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, str]  # Cell -> color

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return (a != b and abs(a[0] - b[0]) <= 1
            and abs(a[1] - b[1]) <= 1)

def recolored(grid: Grid, clicked: Coord) -> Grid:
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked)
            else current
            for cell, current in grid.items()}

class BoxModel(Observable[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.notify(self.grid)
```

Because the model carries no display code, a test drives it without a GUI.
Build a model, click a cell,
and check that the neighbors took its color and that observers received the new grid:

```python
# test_box_observer.py
from box_observer import (BoxModel, Grid, adjacent,
                          new_grid, recolored)

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"  # COLORS[0]
    # Same (x + y) color band
    assert grid[(0, 1)] == grid[(1, 0)]

def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))  # Diagonal
    assert adjacent((1, 1), (1, 2))  # Edge
    # Not its own neighbor
    assert not adjacent((1, 1), (1, 1))
    assert not adjacent((0, 0), (2, 0))  # Two away

def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    # Diagonal neighbor: changed
    assert out[(1, 1)] == grid[(2, 2)]
    # Edge neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]
    # Two away: unchanged
    assert out[(0, 0)] == grid[(0, 0)]
    assert out is not grid  # Pure: a new grid

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Grid] = []
    # The observer is a callable
    model.subscribe(seen.append)
    model.click((2, 2))
    # Observer got the new grid
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
```

The view lives in its own file.
It is the only code that touches the screen.
`draw()` paints the grid, and the view subscribes it, so every change repaints.
A click on the canvas becomes a model `click()`,
and the resulting notification repaints the view.
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

`draw()` clears the canvas before repainting.
Without that line each notification adds another `size * size` rectangles on top of the last set.
The canvas looks identical and grows without limit,
the same quiet accumulation as a lapsed listener.

The model and the view share only the subscribe-and-notify contract,
so you can attach a second view to the same model and keep both in step.

## What Stayed Constant

One design served three jobs in this chapter: a thermometer pushing a float,
a fan-out awaiting network calls, and a GUI repainting a grid.
In every case the observer was a callable and the observable was a list of them.
Nothing in the pattern required an interface, a flag, or a class per reaction.
[Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
already took the last step:
one list becomes a dictionary of lists keyed by event type,
and the Observer is an event bus.

## Exercises

1.  Create a minimal Observer-Observable design of your own,
    without looking at `observers.py`:
    the smallest `Observable` that lets callables subscribe, then notifies them.
    Demonstrate it by subscribing several observers and causing one change that updates them all.
2.  Turn `box_observer.py` into a simple game:
    you own the contiguous patch of same-colored squares containing the top-left corner,
    and clicking any square recolors your patch to that square's color,
    absorbing neighbors that now match.
    Track the clicks it takes to make the whole field one color.
    For competition, alternate turns between players.
3.  Make `Observable.notify()` survive an observer that raises an exception:
    every other observer still hears the change,
    and `notify()` re-raises the failures afterward, together,
    as an `ExceptionGroup`
    (the container [Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup) introduced, which you build yourself here: `raise ExceptionGroup("message", failures)`).
    Write a test in which the first observer raises an exception and the second still records its notification.
4.  Redo exercise 3 for `async_observers.py`.
    Make `notify()` use `gather(*coros, return_exceptions=True)`,
    separate the returned exceptions from the successes,
    and raise them together as an `ExceptionGroup`.
    Write a test in which the first observer raises an exception and the second still records its notification.
