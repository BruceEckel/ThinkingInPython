# Observer

The *Observer* pattern, a kind of callback,
decouples the code that changes state from the code that reacts to the change.
One object, the *observer*, registers interest in another, the *observable*,
and receives a notification whenever the observable's state changes.
Of the callback patterns it is the most dynamic:

- Observers attach and detach at runtime
- The observable never needs to know their types

It underlies event handling,
and the model-view split that keeps a display in step with the data behind it.

Use *Observer* if a group of objects must update themselves when some other object changes state.
The classic example is Smalltalk's MVC (model-view-controller),
or the almost-equivalent Document-View architecture.
You have some data, the *document*, and more than one view of it,
say a plot and a table.
When the data changes, every view must refresh.
The *Observer* pattern arranges that,
without the data having to know which views exist.

Python expresses this with far less machinery than the classic design.
This chapter shows the Pythonic version first,
then extends it to async for I/O-bound observers.
It closes with a visual model-view example built on the same callable observers.

## The Pythonic Observer: a List of Callables

In Python an *observer* need not be an object implementing an `Observer` interface.
It is simply a callable.
An *observable* need not be a base class with a `changed` flag.
It is a list of callables and a way to notify them.
A `@property` setter is a natural place to fire the notification when state changes:

```python
# observers.py
from collections.abc import Callable
from typing import Any

type Observer = Callable[[Any], None]

class Observable:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, data: Any) -> None:
        for observer in self._observers:
            observer(data)

class Thermometer(Observable):
    def __init__(self) -> None:
        super().__init__()
        self._celsius = 0.0

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)   # State changed; tell the observers
```

Using it, subscribed callables react to every temperature change:

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
No `Observer` base class needs inheriting,
and no notification protocol needs implementing.
Assigning to `celsius` notifies everyone.
For event-heavy programs there are mature libraries
(signal/slot systems, `asyncio` events),
but for most cases the *Observer* pattern amounts to nothing more than a list of callbacks.

An observer returns `None`.
Notification runs one way, from observable to observers, and nothing comes back.
Collecting a value from each observer is a different pattern,
such as [Chain of Responsibility](28_Function_Objects.md#chain-of-responsibility) for the first handler that answers.

Testing confirms that every subscriber receives the new value,
and a subscriber sees only the changes that happen after it subscribes.
It also verifies that an unsubscribed observer stops hearing changes.
Removal is by identity, so a detachable observer needs a named reference,
not an inline lambda.
A list whose `append` is the observer records what arrived:

```python
# test_observers.py
from observers import Observable, Thermometer

def test_notify_calls_every_subscriber() -> None:
    received: list[tuple[str, object]] = []
    obs = Observable()
    obs.subscribe(lambda d: received.append(("a", d)))
    obs.subscribe(lambda d: received.append(("b", d)))
    obs.notify(42)
    assert received == [("a", 42), ("b", 42)]

def test_no_subscribers_is_a_noop() -> None:
    Observable().notify("anything")  # Must not raise

def test_unsubscribe_stops_delivery() -> None:
    received: list[object] = []
    obs = Observable()
    record = received.append   # Named so it can be removed
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

## Observer and I/O

Until now, an observer only prints or appends to a list, then returns.
If an observer calls a network service or writes to a database,
notifying observers one at a time blocks on each.
The list of callbacks becomes a line of waits.

If observers are coroutines,
`notify` awaits them together with `asyncio.gather`,
so one state change reaches every observer at once.
A slow observer no longer holds up the others.
`gather` still waits for all of them,
so the change finishes only after every notification succeeds.
One limitation: a `@property` setter cannot be a coroutine,
so an assignment cannot be awaited.
The state change moves from `t.celsius = value` to an awaitable method.
[Concurrency](19_Concurrency.md#asyncio-mechanics) covers the `asyncio` mechanics here
(`async def`, `await`, `gather`, `run`).
For this example, we only need a coroutine to pause at `await` while others run:

```python
# async_observers.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncObserver = Callable[[float], Awaitable[None]]

class Observable:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver] = []

    def subscribe(self, observer: AsyncObserver) -> None:
        self._observers.append(observer)

    async def notify(self, data: float) -> None:
        # Fan out to every observer at once, then wait for all
        await asyncio.gather(*(obs(data) for obs in self._observers))

class Thermometer(Observable):
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
        await asyncio.sleep(0.02)   # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)   # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer()
    t.subscribe(alarm)
    t.subscribe(log_reading)
    await t.set_celsius(20)   # Below the alarm threshold
    await t.set_celsius(150)   # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
```

The definition of `AsyncObserver` guarantees that only `async` functions can serve as observers.

The `alarm` is slower than the log, yet the log prints first.
Awaiting the observers in sequence would print in subscribe order, alarm first.
Concurrent fan-out lets each finish on its own schedule,
so the faster observer reports first.
The alarm also shows an observer that can decline to act.
Below its threshold it returns without sending anything.

Use this only when the observers are I/O-bound.
For in-memory observers the synchronous list from earlier is simpler and needs no event loop.
The type-keyed [event bus](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type) is the same fan-out,
routed by event type.

## A Visual Example of Observers

This is the model-view split from the chapter's opening,
made visible with `tkinter`
(in the standard library, so there is nothing to install),
and split across two files to make the point.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule for a click.
It holds no display code.
The *view*, `box_view.py`, is the only file that draws.
Click a box and every box touching it, diagonals included,
repaints to the clicked box's color.

The model is an `Observable`.
`new_grid()` builds a size x size grid banded into three colors,
`adjacent()` tests whether two distinct cells touch, including diagonally,
and `recolored()` computes the grid that results from a click: values in,
values out.
`BoxModel.click()` makes the next grid with `recolored()` and announces it with `notify()`.
`tkinter` plays no part here, so we can test the model without a GUI.
It reuses the same `Observable` as the thermometer, from `observers.py`:

```python
# box_observer.py
from typing import Final
from observers import Observable

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]             # (column, row)
type Grid = dict[Coord, str]             # Cell -> color

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

def recolored(grid: Grid, clicked: Coord) -> Grid:
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked) else current
            for cell, current in grid.items()}

class BoxModel(Observable):
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
from box_observer import BoxModel, Grid, adjacent, new_grid, recolored

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"     # COLORS[0]
    assert grid[(0, 1)] == grid[(1, 0)]  # Same (x + y) color band

def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))      # Diagonal
    assert adjacent((1, 1), (1, 2))      # Edge
    assert not adjacent((1, 1), (1, 1))  # Not its own neighbor
    assert not adjacent((0, 0), (2, 0))  # Two away

def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    assert out[(1, 1)] == grid[(2, 2)]   # Diagonal neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]   # Edge neighbor: changed
    assert out[(0, 0)] == grid[(0, 0)]   # Two away: unchanged
    assert out is not grid               # Pure: a new grid

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Grid] = []
    model.subscribe(seen.append)         # The observer is a callable
    model.click((2, 2))
    assert seen[-1] is model.grid        # Observer got the new grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
```

The view lives in its own file.
It is the only code that touches the screen.
`draw()` paints the grid, and the view subscribes it, so every change repaints.
A click on the canvas becomes a model `click()`,
and the resulting notification repaints the view.
Run `box_view.py` to play.
It opens a window, so the example harness does not run it
(`tools/norun.txt` lists it).

```python
# box_view.py
import tkinter as tk
from box_observer import BoxModel, Grid

def show(model: BoxModel, cell: int = 60) -> None:
    root = tk.Tk()
    root.title("ColorBoxes")
    canvas = tk.Canvas(root, highlightthickness=0,
                       width=model.size * cell,
                       height=model.size * cell)
    canvas.pack()

    def draw(grid: Grid) -> None:
        for (x, y), color in grid.items():
            canvas.create_rectangle(
                x * cell, y * cell, (x + 1) * cell, (y + 1) * cell,
                fill=color, outline="white")

    model.subscribe(draw)   # Repaint on every model change
    canvas.bind("<Button-1>",
                lambda e: model.click((e.x // cell, e.y // cell)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
```

The model and the view share only the subscribe-and-notify contract,
so the test can exercise the model without a display.
You can also attach a second view to the same model and keep both in step.
Showing that the model is correct, separately from how it is drawn,
is the model-view split made concrete.

## Exercises

1.  Write a class decorator that wraps every method of a class to print on method entry and exit,
    giving an execution trace.
    ([Decorators](14_Decorators.md#decorating-classes) and [Metaprogramming](17_Metaprogramming.md#writing-a-metaclass) show the techniques.)
2.  Create a minimal Observer-Observable design in two classes.
    Just create the bare minimum in the two classes,
    then demonstrate your design by creating one `Observable` and many `Observer`s,
    and cause the `Observable` to update the `Observer`s.
3.  Modify `box_observer.py` to turn it into a simple game.
    If any of the squares surrounding the one you clicked is part of a contiguous patch of the same color,
    then all the squares in that patch take on the color you clicked.
    You can configure the game for competition between players or to keep track of the number of clicks that a single player uses to turn the field into a single color.
    You may also restrict a player's color to the first one they chose.
