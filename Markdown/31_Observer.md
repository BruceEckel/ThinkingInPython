# Observer

> Decoupling code behavior

The *Observer* pattern is a kind of callback.
One object, the *observer*, registers interest in another, the *observable*,
and is notified whenever the observable's state changes.
Of the callback patterns it is the most dynamic:
observers attach and detach at runtime,
and the observable never needs to know their types.
It underlies event handling,
and the model-view split that keeps a display in step with the data behind it.

The problem it solves is common:
a group of objects must update themselves when some other object changes state.
The classic example is Smalltalk's MVC (model-view-controller),
or the almost-equivalent Document-View architecture.
You have some data, the *document*, and more than one view of it,
say a plot and a table.
When the data changes, every view must refresh.
The *Observer* pattern arranges that,
without the data having to know which views exist.

Python expresses this with far less machinery than the classic design needs,
so this chapter shows the Pythonic version first,
then the literal translation of Java's `Observable` and `Observer` classes for when you actually need it.

## The Pythonic Observer: a List of Callables

In Python an *observer* need not be an object implementing an `Observer` interface;
it is simply a callable.
An *observable* need not be a base class with a `changed` flag;
it is a list of callables and a way to notify them.
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

thermo = Thermometer()
thermo.subscribe(lambda c: print(f"display: {c}C"))
thermo.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
thermo.celsius = 25
#: display: 25C
#: ok
thermo.celsius = 150
#: display: 150C
#: alarm!
```

The observers here are lambdas, but any function or bound method works.
There is no `Observer` base class to inherit and no `set_changed()`/`notify_observers()` protocol:
assigning to `celsius` notifies everyone.
For event-heavy programs there are mature libraries (signal/slot systems, `asyncio` events),
but for most cases a list of callbacks is all the *Observer* pattern amounts to.

Testing confirms the two things that matter:
every subscriber is called with the new value,
and a subscriber sees only the changes that happen after it subscribes.
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

def test_thermometer_pushes_new_value_on_set() -> None:
    readings: list[float] = []
    thermo = Thermometer()
    thermo.subscribe(readings.append)
    thermo.celsius = 25.0
    thermo.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert thermo.celsius == 150.0

def test_late_subscriber_misses_earlier_changes() -> None:
    readings: list[float] = []
    thermo = Thermometer()
    thermo.celsius = 10.0  # No subscriber yet
    thermo.subscribe(readings.append)
    thermo.celsius = 20.0
    assert readings == [20.0]
```

The rest of this chapter translates Java's `Observable` and `Observer` classes directly.
That is useful when you are porting Java code or need the exact `set_changed()` semantics,
but use it only when the simple version above is not enough.

## The Classic Observable and Observer

The classic design, translated from Java's `java.util` but without its thread synchronization,
makes the two roles explicit base classes.
An `Observable` keeps a list of observers and a `changed` flag.
You call `set_changed()` and then `notify_observers()`,
and every registered `Observer` has its `update()` called.
The flag lets the subject decide when a batch of changes is worth announcing.

```python
# observer.py
from typing import Any

class Observer:
    def update(self, observable: Any, arg: Any, /) -> None:
        "Called when the observed object changes."

class Observable:
    def __init__(self) -> None:
        self.observers: list[Observer] = []
        self.changed = False

    def add_observer(self, observer: Observer) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def delete_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def set_changed(self) -> None:
        self.changed = True

    def notify_observers(self, arg: Any = None) -> None:
        if not self.changed:
            return
        self.changed = False
        for observer in list(self.observers):
            observer.update(self, arg)
```

A bare `Observable` does nothing on its own:
you must subclass it and call `set_changed()`,
or `notify_observers()` is a no-op.

### A Visual Example of Observers

This is the model-view split from the chapter's opening,
made visible with `tkinter` (in the standard library, so there is nothing to install),
and split across two files to make the point.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule for a click; it holds no display code.
The *view*, `box_view.py`, is the only file that draws.
Click a box and every box touching it, diagonals included,
repaints to the clicked box's color.

The model is an `Observable`.
Building the grid, testing adjacency,
and computing the grid that results from a click are plain functions: values in,
values out.
`BoxModel.click()` makes the next grid with `recolored()` and announces it.
There is no `tkinter` here at all,
which is what lets the model be tested with no window open.
The classic `Observable` comes from `observer.py`:

```python
# box_observer.py
from typing import Final
from observer import Observable

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]             # (column, row)
type Grid = dict[Coord, str]             # Cell -> color

def new_grid(size: int) -> Grid:
    "Build a size x size grid, banded into three colors."
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    "True if two distinct cells touch, including diagonally."
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

def recolored(grid: Grid, clicked: Coord) -> Grid:
    "Return a new grid: every neighbor of the click takes its color."
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked) else current
            for cell, current in grid.items()}

class BoxModel(Observable):
    "The subject: holds the grid and announces every change."
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.set_changed()
        self.notify_observers(self.grid)
```

Because the model carries no display code, a test drives it with no window open:
build a model, click a cell,
and check that the neighbors took its color and that observers were notified with the new grid.
This is the model's correctness, established apart from how it is shown:

```python
# test_box_observer.py
from typing import Any, override
from box_observer import BoxModel, adjacent, new_grid, recolored
from observer import Observer

def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"     # COLORS[0]
    assert grid[(0, 1)] == grid[(1, 0)]  # Same (x + y) color band

def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))      # Diagonal
    assert adjacent((1, 1), (1, 2))      # Edge
    assert not adjacent((1, 1), (1, 1))  # not its own neighbor
    assert not adjacent((0, 0), (2, 0))  # Two away

def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    assert out[(1, 1)] == grid[(2, 2)]   # Diagonal neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]   # Edge neighbor: changed
    assert out[(0, 0)] == grid[(0, 0)]   # Two away: unchanged
    assert out is not grid               # pure: a new grid

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Any] = []

    class Recorder(Observer):
        @override
        def update(self, observable: Any, grid: Any) -> None:
            seen.append(grid)

    model.add_observer(Recorder())
    model.click((2, 2))
    assert seen[-1] is model.grid        # Observer got the new grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
```

The view lives in its own file.
It is the only `Observer` and the only code that touches the screen:
`draw()` paints the grid,
and `update()` calls `draw()` whenever the model changes.
A click on the canvas becomes a model `click()`,
and the resulting notification repaints the view.
Run `box_view.py` to play; it opens a window,
so the example harness does not run it (it is listed in `tools/norun.txt`).

```python
# box_view.py
import tkinter as tk
from typing import Any, override
from box_observer import BoxModel, Grid
from observer import Observer

def show(model: BoxModel, cell: int = 60) -> None:
    "Open the window and keep it in step with the model."
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

    class View(Observer):  # Repaints on every model change
        @override
        def update(self, observable: Any, grid: Any) -> None:
            draw(grid)

    model.add_observer(View())
    canvas.bind("<Button-1>",
                lambda e: model.click((e.x // cell, e.y // cell)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
```

The model and the view share only the `Observable`/`Observer` contract.
That is what lets the test exercise the model with no display,
and what would let you attach a second view to the same model and keep both in step.
Showing that the model is correct, separately from how it is drawn,
is the model-view split made concrete.

## Exercises

1.  Write a class decorator that wraps every method of a class to print when the method is entered and exited,
    giving an execution trace.
    ([Decorators](15_Decorators.md#decorating-classes) and [Metaprogramming](18_Metaprogramming.md#writing-a-metaclass) show the techniques.)
2.  Create a minimal Observer-Observable design in two classes.
    Just create the bare minimum in the two classes,
    then demonstrate your design by creating one `Observable` and many `Observer`s,
    and cause the `Observable` to update the `Observer`s.
3.  Modify `box_observer.py` to turn it into a simple game.
    If any of the squares surrounding the one you clicked is part of a contiguous patch of the same color,
    then all the squares in that patch are changed to the color you clicked on.
    You can configure the game for competition between players or to keep track of the number of clicks that a single player uses to turn the field into a single color.
    You may also restrict a player's color to the first one that was chosen.
