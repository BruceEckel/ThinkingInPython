# Observer

> Decoupling code behavior

The *Observer* pattern is a kind of callback. One object, the *observer*,
registers interest in another, the *observable*, and is notified whenever the
observable's state changes. Of the callback patterns it is the most dynamic:
observers attach and detach at run time, and the observable never needs to know
their types. It underlies event handling, and the model-view split that keeps a
display in step with the data behind it.

The problem it solves is common: a group of objects must update themselves when
some other object changes state. The classic example is Smalltalk's MVC
(model-view-controller), or the almost-equivalent Document-View architecture.
You have some data, the *document*, and more than one view of it, say a plot and
a table. When the data changes, every view must refresh. The observer pattern
arranges that, without the data having to know which views exist.

Python expresses this with far less machinery than the classic design needs, so
this chapter shows the Pythonic version first, then the literal translation of
Java's `Observable` and `Observer` classes for when you actually need it.

## The Pythonic Observer: a List of Callables

In Python an *observer* need not be an
object implementing an `Observer` interface; it is simply a callable. An
*observable* need not be a base class with a `changed` flag; it is a list of
callables and a way to notify them. A `@property` setter is a natural place to
fire the notification when state changes:

```python
# observers.py
# An observer is just a callable; an observable is a list of them.
# No Observer interface and no Observable base class to inherit.
from collections.abc import Callable
from typing import Any


class Observable:
    def __init__(self) -> None:
        self._observers: list[Callable[[Any], None]] = []

    def subscribe(self, observer: Callable[[Any], None]) -> None:
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
        self.notify(value)   # state changed; tell the observers


thermo = Thermometer()
thermo.subscribe(lambda c: print(f"display: {c}C"))
thermo.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
thermo.celsius = 25
thermo.celsius = 150
```

The observers here are lambdas, but any function or bound method works. There is
no `Observer` base class to inherit and no `set_changed()`/`notify_observers()`
protocol: assigning to `celsius` notifies everyone. For event-heavy programs
there are mature libraries (signal/slot systems, `asyncio` events), but for most
cases a list of callbacks is all the Observer pattern amounts to.

A test confirms the two things that matter: every subscriber is called with the
new value, and a subscriber sees only the changes that happen after it
subscribes. A list whose `append` is the observer records what arrived:

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
    Observable().notify("anything")  # must not raise


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
    thermo.celsius = 10.0  # no subscriber yet
    thermo.subscribe(readings.append)
    thermo.celsius = 20.0
    assert readings == [20.0]
```

The rest of this chapter translates Java's `Observable` and `Observer` classes
directly. That is useful when you are porting Java code or need the exact
`set_changed()` semantics, but use it only when the simple version above is
not enough.

## The Classic Observable and Observer

The classic design, translated from Java's `java.util`, makes the two roles
explicit base classes. An `Observable` keeps a list of observers and a
`changed` flag. You call `set_changed()` and then `notify_observers()`, and
every registered `Observer` has its `update()` called. The flag lets the
subject decide when a batch of changes is worth announcing.

```python
# observer.py
# The classic Observable/Observer base classes, in the style of Java's
# java.util, without the thread synchronization.
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

A bare `Observable` does nothing on its own: you must subclass it and call
`set_changed()`, or `notify_observers()` is a no-op. The example below shows
exactly that, and a test pins down the result.

### A Visual Example of Observers

This is the model-view split from the chapter's opening, made visible with
`tkinter` (in the standard library, so there is nothing to install). The *model*
is a grid of colored boxes. Click a box and every box touching it, diagonals
included, repaints to the clicked box's color. The model is an `Observable`; the
on-screen view is an `Observer` that repaints whenever the model announces a
change.

The logic is kept apart from the screen. Building the grid, testing adjacency,
and computing the grid that results from a click are plain functions: values in,
values out. Only one function, the view's `draw()`, puts anything on screen.
That split is what lets the model be tested with no display open, in
`test_box_observer.py` below. The classic `Observable` and `Observer` come from
`observer.py`:

```python
# box_observer.py
# A visual ColorBoxes: the model-view split wired with the classic
# Observer. The model holds the grid and announces each change; the
# view observes it and repaints. Every function that computes returns
# a value; only the view's draw() touches the screen.
import tkinter as tk
from typing import Any

from observer import Observable, Observer

COLORS = ("skyblue", "palegreen", "khaki")
type Grid = dict[tuple[int, int], str]   # (column, row) -> color


def new_grid(size: int) -> Grid:
    "Build a size x size grid, banded into three colors."
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}


def adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    "True if two distinct cells touch, including diagonally."
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


def recolored(grid: Grid, clicked: tuple[int, int]) -> Grid:
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

    def click(self, cell: tuple[int, int]) -> None:
        self.grid = recolored(self.grid, cell)
        self.set_changed()
        self.notify_observers(self.grid)


def show(model: BoxModel, cell: int = 60) -> None:
    "The only function that touches the screen."
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

    # The observer is the view: repaint when the model changes.
    class View(Observer):
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

`box_observer.py` opens a window, so the example harness does not run it (it is
listed in `tools/norun.txt`). The model carries the logic, though, so a test
drives it with no display: build a model, click a cell, and check that the
neighbors took its color and that the observers were notified with the new grid.

```python
# test_box_observer.py
from typing import Any

from box_observer import BoxModel, adjacent, new_grid, recolored
from observer import Observer


def test_new_grid_size_and_banding() -> None:
    grid = new_grid(3)
    assert len(grid) == 9
    assert grid[(0, 0)] == "skyblue"     # COLORS[0]
    assert grid[(0, 1)] == grid[(1, 0)]  # same (x + y) color band


def test_adjacent() -> None:
    assert adjacent((1, 1), (2, 2))      # diagonal
    assert adjacent((1, 1), (1, 2))      # edge
    assert not adjacent((1, 1), (1, 1))  # not its own neighbor
    assert not adjacent((0, 0), (2, 0))  # two away


def test_recolored_touches_only_neighbors() -> None:
    grid = new_grid(5)
    out = recolored(grid, (2, 2))
    assert out[(1, 1)] == grid[(2, 2)]   # diagonal neighbor: changed
    assert out[(2, 3)] == grid[(2, 2)]   # edge neighbor: changed
    assert out[(0, 0)] == grid[(0, 0)]   # two away: unchanged
    assert out is not grid               # pure: a new grid


def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(5)
    seen: list[Any] = []

    class Recorder(Observer):
        def update(self, observable: Any, grid: Any) -> None:
            seen.append(grid)

    model.add_observer(Recorder())
    model.click((2, 2))
    assert seen[-1] is model.grid        # observer got the new grid
    assert model.grid[(1, 1)] == model.grid[(2, 2)]
```

`BoxModel` is the subject: its `click()` builds the next grid with `recolored()`,
sets the changed flag, and notifies. The view is the `Observer`, and its
`update()` does nothing but repaint. Neither side knows much about the other, so
you can test the model with no window open, or attach a second view to the same
model and both stay in step. That decoupling, with the model-view split, is the
whole point of *Observer*.


### Exercises

1.  Write a class decorator that wraps every method of a class to print when
    the method is entered and exited, giving an execution trace. (The
    [Decorators](13_Decorators.md) and [Metaprogramming](15_Metaprogramming.md)
    chapters show the techniques.)
2.  Create a minimal Observer-Observable design in two classes. Just
    create the bare minimum in the two classes, then demonstrate your
    design by creating one `Observable` and many `Observer`s, and
    cause the `Observable` to update the `Observer`s.
3.  Modify `box_observer.py` to turn it into a simple game. If any of
    the squares surrounding the one you clicked is part of a contiguous
    patch of the same color, then all the squares in that patch are
    changed to the color you clicked on. You can configure the game for
    competition between players or to keep track of the number of clicks
    that a single player uses to turn the field into a single color. You
    may also want to restrict a player's color to the first one that was
    chosen.
