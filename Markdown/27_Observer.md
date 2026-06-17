# Observer

> Decoupling code behavior

The *Observer* pattern is a kind of callback: an object
registers interest in another object and is notified when that object's state
changes. It is the most dynamic of the callback patterns. (A related family,
multiple dispatching, includes the *Visitor* pattern from *Design Patterns*;
see the Multiple Dispatching and Visitor chapters. [[Create links]]

*Observer* is often used for the specific case of
changes based on another object's change of state, but is also the basis
of event management.

The observer pattern solves a fairly common problem: What if a group of
objects needs to update themselves when some object changes state? This
can be seen in the "model-view" aspect of Smalltalk's MVC
(model-view-controller), or the almost-equivalent "Document-View
Architecture." Suppose that you have some data (the "document") and more
than one view, say a plot and a textual view. When you change the data,
the two views must know to update themselves. This is what
observer facilitates.

There are two types of objects used to implement the observer pattern in
Python. The `Observable` class keeps track of everybody who wants to
be informed when a change happens, whether the "state" has changed or
not. When someone says "OK, everybody should check and potentially
update themselves," the `Observable` class performs this task by
calling the `notify_observers()` method for each one on the list.

There are actually two "things that change" in the observer pattern: the
quantity of observing objects and the way an update occurs.

`Observer` is an "interface" class that only has one method,
`update()`. This function is called by the object that's being
observed, when that object decides it's time to update all its observers.
The arguments are optional; you can have an `update()` with no
arguments which still fits the observer pattern.
This allows the observed object to pass the object that
caused the update (since an `Observer` may be registered with more
than one observed object) and any extra information if that's helpful,
rather than forcing the `Observer` object to hunt around to see who is
updating and to fetch any other information it needs.

`Observable` has a flag to indicate whether it's been changed. In a
simpler design, there would be no flag; if something happened, everyone
would be notified. The flag allows you to wait, and only notify the
`Observer`s when you decide the time is right. Notice, however, that
the control of the flag's state is `protected`, so that only an
inheritor can decide what constitutes a change, and not the end user of
the resulting derived `Observer` class.

Most of the work is done in `notify_observers()`. If the `changed`
flag has not been set, this does nothing. Otherwise, it first clears the
`changed` flag so repeated calls to `notify_observers()` won't waste
time. This is done before notifying the observers in case the calls to
`update()` do anything that causes a change back to this
`Observable` object. Then it moves through the `set` and calls back
to the `update()` method of each `Observer`.

At first it may appear that you can use an ordinary `Observable`
object to manage the updates. But this doesn't work; to get an effect,
you *must* inherit from `Observable` and somewhere in your
derived-class code call `set_changed()`. This is the method
that sets the "changed" flag, which means that when you call
`notify_observers()` all of the observers will, in fact, get notified.
*Where* you call `set_changed()` depends on the logic of your program.

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
exactly that, and checks the result.

### A Visual Example of Observers

This creates a grid of boxes, each starting with some color.
Every box observes a shared `Observable`. When one box is
"clicked," the `Observable` notifies every box, and each box adjacent to the
clicked one changes its color to match it.

The original was a Swing GUI. The pattern itself has nothing to do with a GUI,
so here it is as a headless program that clicks a box in code and then checks
the result. That keeps the focus on the Observer mechanics and lets the example
verify itself. It reuses the `Observable` and `Observer` classes from
`observer.py`:

```python
# box_observer.py
# A headless version of the ColorBoxes Observer example. Boxes in a
# grid observe a shared Observable; "clicking" one recolors its
# neighbors.
from typing import Any

from observer import Observable, Observer


class BoxObservable(Observable):
    # You must subclass Observable and call set_changed(), or notify
    # does nothing:
    def notify_observers(self, arg: Any = None) -> None:
        self.set_changed()
        Observable.notify_observers(self, arg)


class Box(Observer):
    def __init__(self, x: int, y: int, color: str,
                 notifier: BoxObservable) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.notifier = notifier
        notifier.add_observer(self)

    def click(self) -> None:
        # A click announces this box to every observer:
        self.notifier.notify_observers(self)

    def update(self, observable: Any, clicked: Box) -> None:
        if self is not clicked and self.next_to(clicked):
            self.color = clicked.color

    def next_to(self, other: Box) -> bool:
        return (abs(self.x - other.x) <= 1
                and abs(self.y - other.y) <= 1)


def make_grid(size: int,
              notifier: BoxObservable) -> list[list[Box]]:
    return [[Box(x, y, f"color{(x + y) % 3}", notifier)
             for y in range(size)]
            for x in range(size)]


if __name__ == "__main__":
    notifier = BoxObservable()
    grid = make_grid(5, notifier)
    center = grid[2][2]
    center.color = "red"
    center.click()
    print(f"(1,1) -> {grid[1][1].color}")
    print(f"(2,3) -> {grid[2][3].color}")
    print(f"(0,0) -> {grid[0][0].color}")
    assert grid[1][1].color == "red"   # diagonally adjacent: changed
    assert grid[2][3].color == "red"   # adjacent: changed
    assert grid[0][0].color != "red"   # two away: unchanged
    print("Observer notifications verified.")
```

`BoxObservable` does the required `set_changed()` in one place, inside its own
`notify_observers()`, so a click always notifies. Because every box
talks only to the base `Observable` interface after it is constructed, you could
swap in a different `Observable` subclass to change notification behavior
without touching the boxes at all.


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
