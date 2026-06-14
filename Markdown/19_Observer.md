# Observer

> Decoupling code behavior

*Observer*, and a category of callbacks called "multiple dispatching
(not in *Design Patterns*)" including the *Visitor* from *Design
Patterns*. Like the other forms of callback, this contains a hook point
where you can change code. The difference is in the observer's
completely dynamic nature. It is often used for the specific case of
changes based on other object's change of state, but is also the basis
of event management. Anytime you want to decouple the source of the call
from the called code in a completely dynamic way.

The observer pattern solves a fairly common problem: What if a group of
objects needs to update themselves when some object changes state? This
can be seen in the "model-view" aspect of Smalltalk's MVC
(model-view-controller), or the almost-equivalent "Document-View
Architecture." Suppose that you have some data (the "document") and more
than one view, say a plot and a textual view. When you change the data,
the two views must know to update themselves, and that's what the
observer facilitates. It's a common enough problem that its solution has
been made a part of the standard `java.util` library.

There are two types of objects used to implement the observer pattern in
Python. The `Observable` class keeps track of everybody who wants to
be informed when a change happens, whether the "state" has changed or
not. When someone says "OK, everybody should check and potentially
update themselves," the `Observable` class performs this task by
calling the `notifyObservers()` method for each one on the list. The
`notifyObservers()` method is part of the base class `Observable`.

There are actually two "things that change" in the observer pattern: the
quantity of observing objects and the way an update occurs. That is, the
observer pattern allows you to modify both of these without affecting
the surrounding code.

`Observer` is an "interface" class that only has one member function,
`update()`. This function is called by the object that's being
observed, when that object decides its time to update all its observers.
The arguments are optional; you could have an `update()` with no
arguments and that would still fit the observer pattern; however this is
more general: it allows the observed object to pass the object that
caused the update (since an `Observer` may be registered with more
than one observed object) and any extra information if that's helpful,
rather than forcing the `Observer` object to hunt around to see who is
updating and to fetch any other information it needs.

The "observed object" that decides when and how to do the updating will
be called the `Observable`.

`Observable` has a flag to indicate whether it's been changed. In a
simpler design, there would be no flag; if something happened, everyone
would be notified. The flag allows you to wait, and only notify the
`Observer`s when you decide the time is right. Notice, however, that
the control of the flag's state is `protected`, so that only an
inheritor can decide what constitutes a change, and not the end user of
the resulting derived `Observer` class.

Most of the work is done in `notifyObservers()`. If the `changed`
flag has not been set, this does nothing. Otherwise, it first clears the
`changed` flag so repeated calls to `notifyObservers()` won't waste
time. This is done before notifying the observers in case the calls to
`update()` do anything that causes a change back to this
`Observable` object. Then it moves through the `set` and calls back
to the `update()` member function of each `Observer`.

At first it may appear that you can use an ordinary `Observable`
object to manage the updates. But this doesn't work; to get an effect,
you *must* inherit from `Observable` and somewhere in your
derived-class code call `setChanged()`. This is the member function
that sets the "changed" flag, which means that when you call
`notifyObservers()` all of the observers will, in fact, get notified.
*Where* you call `setChanged()` depends on the logic of your program.

## The Pythonic Observer: a List of Callables

The description above is the Java design. In Python an *observer* need not be an
object implementing an `Observer` interface; it is simply a callable. An
*observable* need not be a base class with a `changed` flag; it is a list of
callables and a way to notify them. A `@property` setter is a natural place to
fire the notification when state changes:

```python
# Observer/observers.py
# An observer is just a callable; an observable is a list of them. No Observer
# interface and no Observable base class to inherit.
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
no `Observer` base class to inherit and no `setChanged()`/`notifyObservers()`
protocol: assigning to `celsius` notifies everyone. For event-heavy programs
there are mature libraries (signal/slot systems, `asyncio` events), but for most
cases a list of callbacks is all the Observer pattern amounts to.

The rest of this chapter translates Java's `Observable` and `Observer` classes
directly. That is useful when you are porting Java code or need the exact
`setChanged()` semantics, but reach for it only when the simple version above is
not enough.

## Observing Flowers

Since Python doesn't have standard library components to support the
observer pattern (like Java does), we must first create one. The
simplest thing to do is translate the Java standard library `Observer`
and `Observable` classes. This also provides easier translation from
Java code that uses these libraries.

In trying to do this, we encounter a minor snag, which is the fact that
Java has a `synchronized` keyword that provides built-in support for
thread synchronization. We could certainly accomplish the same thing by
hand, using code like this:

```python
# Util/ToSynch.py

import threading
class ToSynch:
    def __init__(self) -> None:
        self.mutex = threading.RLock()
        self.val = 1
    def aSynchronizedMethod(self) -> int:
        self.mutex.acquire()
        try:
            self.val += 1
            return self.val
        finally:
            self.mutex.release()
```

But this rapidly becomes tedious to write and to read. Peter Norvig
provided me with a much nicer solution:

```python
# Util/Synchronization.py
'''Simple emulation of Java's 'synchronized'
keyword, from Peter Norvig.'''
import threading
from typing import Any, Callable

def synchronized(method: Callable[..., Any]) -> Callable[..., Any]:
    def f(*args: Any) -> Any:
        self = args[0]
        self.mutex.acquire()
        # print(method.__name__, 'acquired')
        try:
            return method(*args)
        finally:
            self.mutex.release()
            # print(method.__name__, 'released')
    return f

def synchronize(klass: type, names: str | None = None) -> None:
    """Synchronize methods in the given class.
    Only synchronize the methods whose names are
    given, or all methods if names=None."""
    selected = names.split() if names is not None else None
    for (name, val) in list(klass.__dict__.items()):
        if callable(val) and name != '__init__' and \
          (selected is None or name in selected):
            # print("synchronizing", name)
            setattr(klass, name, synchronized(val))

# You can create your own self.mutex, or inherit
# from this class:
class Synchronization:
    def __init__(self) -> None:
        self.mutex = threading.RLock()
```

The `synchronized()` function takes a method and wraps it in a
function that adds the mutex functionality. The method is called inside
this function:

    return method(*args)

and as the `return` statement passes through the `finally` clause,
the mutex is released.

This is in some ways the *Decorator* design pattern, but much simpler to
create and use. All you have to say is:

    myMethod = synchronized(myMethod)

To surround your method with a mutex.

`synchronize()` is a convenience function that applies
`synchronized()` to an entire class, either all the methods in the
class (the default) or selected methods which are named in a string as
the second argument.

Finally, for `synchronized()` to work there must be a `self.mutex`
created in every class that uses `synchronized()`. This can be
created by hand by the class author, but it's more consistent to use
inheritance, so the base class `Synchronization` is provided.

Here's a simple test of the `Synchronization` module:

```python
# Util/TestSynchronization.py
from Synchronization import *

# To use for a method:
class C(Synchronization):
    def __init__(self) -> None:
        Synchronization.__init__(self)
        self.data = 1
    @synchronized
    def m(self) -> int:
        self.data += 1
        return self.data
    def f(self) -> int: return 47
    def g(self) -> str: return 'spam'

# So m is synchronized, f and g are not.
c = C()

# On the class level:
class D(C):
    def __init__(self) -> None:
        C.__init__(self)
    # You must override an un-synchronized method
    # in order to synchronize it (just like Java):
    def f(self) -> int: return C.f(self)

# Synchronize every (defined) method in the class:
synchronize(D)
d = D()
d.f() # Synchronized
d.g() # Not synchronized
d.m() # Synchronized (in the base class)

class E(C):
    def __init__(self) -> None:
        C.__init__(self)
    def m(self) -> int: return C.m(self)
    def g(self) -> str: return C.g(self)
    def f(self) -> int: return C.f(self)
# Only synchronizes m and g. Note that m ends up
# being doubly-wrapped in synchronization, which
# doesn't hurt anything but is inefficient:
synchronize(E, 'm g')
e = E()
e.f()
e.g()
e.m()
```

You must call the base class constructor for `Synchronization`, but
that's all. In class `C` you can see the use of `synchronized()`
for `m`, leaving `f` and `g` alone. Class `D` has all its
methods synchronized en masse, and class `E` uses the convenience
function to synchronize `m` and `g`. Note that since `m` ends up
being synchronized twice, it will be entered and left twice for every
call, which isn't very desirable \[there may be a fix for this\]:

```python
# Util/Observer.py
# Class support for "observer" pattern.
from typing import Any

from Synchronization import *

class Observer:
    def update(self, observable: Any, arg: Any) -> None:
        '''Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.'''
        pass

class Observable(Synchronization):
    def __init__(self) -> None:
        self.obs: list[Observer] = []
        self.changed = 0
        Synchronization.__init__(self)

    def addObserver(self, observer: Observer) -> None:
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer: Observer) -> None:
        self.obs.remove(observer)

    def notifyObservers(self, arg: Any = None) -> None:
        '''If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'.'''

        self.mutex.acquire()
        try:
            if not self.changed: return
            # Make a local copy in case of synchronous
            # additions of observers:
            localArray = self.obs[:]
            self.clearChanged()
        finally:
            self.mutex.release()
        # Updating is not required to be synchronized:
        for observer in localArray:
            observer.update(self, arg)

    def deleteObservers(self) -> None: self.obs = []
    def setChanged(self) -> None: self.changed = 1
    def clearChanged(self) -> None: self.changed = 0
    def hasChanged(self) -> int: return self.changed
    def countObservers(self) -> int: return len(self.obs)

synchronize(Observable,
  "addObserver deleteObserver deleteObservers " +
  "setChanged clearChanged hasChanged " +
  "countObservers")
```

Using this library, here is an example of the observer pattern:

```python
# Observer/ObservedFlower.py
# Demonstration of "observer" pattern.
import sys
sys.path += ['../Util']
from Observer import Observer, Observable  # type: ignore

class Flower:
    def __init__(self):
        self.isOpen = 0
        self.openNotifier = Flower.OpenNotifier(self)
        self.closeNotifier= Flower.CloseNotifier(self)
    def open(self): # Opens its petals
        self.isOpen = 1
        self.openNotifier.notifyObservers()
        self.closeNotifier.open()
    def close(self): # Closes its petals
        self.isOpen = 0
        self.closeNotifier.notifyObservers()
        self.openNotifier.close()
    def closing(self): return self.closeNotifier

    class OpenNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
            self.alreadyOpen = 0
        def notifyObservers(self):
            if self.outer.isOpen and \
            not self.alreadyOpen:
                self.setChanged()
                Observable.notifyObservers(self)
                self.alreadyOpen = 1
        def close(self):
            self.alreadyOpen = 0

    class CloseNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
            self.alreadyClosed = 0
        def notifyObservers(self):
            if not self.outer.isOpen and \
            not self.alreadyClosed:
                self.setChanged()
                Observable.notifyObservers(self)
                self.alreadyClosed = 1
        def open(self):
            alreadyClosed = 0

class Bee:
    def __init__(self, name):
        self.name = name
        self.openObserver = Bee.OpenObserver(self)
        self.closeObserver = Bee.CloseObserver(self)
    # An inner class for observing openings:
    class OpenObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Bee " + self.outer.name +
              "'s breakfast time!")
    # Another inner class for closings:
    class CloseObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Bee " + self.outer.name +
              "'s bed time!")

class Hummingbird:
    def __init__(self, name):
        self.name = name
        self.openObserver = \
          Hummingbird.OpenObserver(self)
        self.closeObserver = \
          Hummingbird.CloseObserver(self)
    class OpenObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Hummingbird " + self.outer.name + \
              "'s breakfast time!")
    class CloseObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Hummingbird " + self.outer.name + \
              "'s bed time!")

f = Flower()
ba = Bee("Eric")
bb = Bee("Eric 0.5")
ha = Hummingbird("A")
hb = Hummingbird("B")
f.openNotifier.addObserver(ha.openObserver)
f.openNotifier.addObserver(hb.openObserver)
f.openNotifier.addObserver(ba.openObserver)
f.openNotifier.addObserver(bb.openObserver)
f.closeNotifier.addObserver(ha.closeObserver)
f.closeNotifier.addObserver(hb.closeObserver)
f.closeNotifier.addObserver(ba.closeObserver)
f.closeNotifier.addObserver(bb.closeObserver)
# Hummingbird 2 decides to sleep in:
f.openNotifier.deleteObserver(hb.openObserver)
# A change that interests observers:
f.open()
f.open() # It's already open, no change.
# Bee 1 doesn't want to go to bed:
f.closeNotifier.deleteObserver(ba.closeObserver)
f.close()
f.close() # It's already closed; no change
f.openNotifier.deleteObservers()
f.open()
f.close()
```

The events of interest are that a `Flower` can open or close. Because
of the use of the inner class idiom, both these events can be separately
observable phenomena. `OpenNotifier` and `CloseNotifier` both
inherit `Observable`, so they have access to `setChanged()` and can
be handed to anything that needs an `Observable`.

The inner class idiom also comes in handy to define more than one kind
of `Observer`, in `Bee` and `Hummingbird`, since both those
classes may want to independently observe `Flower` openings and
closings. Notice how the inner class idiom provides something that has
most of the benefits of inheritance (the ability to access the
`private` data in the outer class, for example) without the same
restrictions.

In `main()`, you can see one of the prime benefits of the observer
pattern: the ability to change behavior at run time by dynamically
registering and un-registering `Observer`s with `Observable`s.

If you study the code above you'll see that `OpenNotifier` and
`CloseNotifier` use the basic `Observable` interface. This means
that you could inherit other completely different `Observer` classes;
the only connection the `Observer`s have with `Flower`s is the
`Observer` interface.

### A Visual Example of Observers

This is the `ColorBoxes` example from *Thinking in Java*. A grid of boxes each
start with some color. Every box observes a shared `Observable`. When one box is
"clicked," the `Observable` notifies every box, and each box adjacent to the
clicked one changes its color to match it.

The original was a Swing GUI. The pattern itself has nothing to do with a GUI,
so here it is as a headless program that clicks a box in code and then checks
the result. That keeps the focus on the Observer mechanics and lets the example
verify itself. It reuses the `Observable` and `Observer` classes from
`Util/Observer.py`:

```python
# Observer/BoxObserver.py
# A headless version of the ColorBoxes Observer example. Boxes in a grid
# observe a shared Observable; "clicking" one recolors its neighbors.
import sys
from typing import Any

sys.path += ['../Util']
from Observer import Observer, Observable  # type: ignore


class BoxObservable(Observable):
    # You must subclass Observable and call setChanged(), or notify does nothing:
    def notifyObservers(self, arg: Any = None) -> None:
        self.setChanged()
        Observable.notifyObservers(self, arg)


class Box(Observer):
    def __init__(self, x: int, y: int, color: str,
                 notifier: BoxObservable) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.notifier = notifier
        notifier.addObserver(self)

    def click(self) -> None:
        # A click announces this box to every observer:
        self.notifier.notifyObservers(self)

    def update(self, observable: Any, clicked: "Box") -> None:
        if self is not clicked and self.next_to(clicked):
            self.color = clicked.color

    def next_to(self, other: "Box") -> bool:
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1


def make_grid(size: int, notifier: BoxObservable) -> list[list["Box"]]:
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

As with the flower example, a bare `Observable` does nothing: you must subclass
it and call `setChanged()`, or `notifyObservers()` is a no-op. `BoxObservable`
does that in one place, inside its own `notifyObservers()`. Because every box
talks only to the base `Observable` interface after it is constructed, you could
swap in a different `Observable` subclass to change notification behavior
without touching the boxes at all.


### Exercises

1.  Using the approach in `Synchronization.py`, create a tool that
    will automatically wrap all the methods in a class to provide an
    execution trace, so that you can see the name of the method and when
    it is entered and exited.
2.  Create a minimal Observer-Observable design in two classes. Just
    create the bare minimum in the two classes, then demonstrate your
    design by creating one `Observable` and many `Observer`s, and
    cause the `Observable` to update the `Observer`s.
3.  Modify `BoxObserver.py` to turn it into a simple game. If any of
    the squares surrounding the one you clicked is part of a contiguous
    patch of the same color, then all the squares in that patch are
    changed to the color you clicked on. You can configure the game for
    competition between players or to keep track of the number of clicks
    that a single player uses to turn the field into a single color. You
    may also want to restrict a player's color to the first one that was
    chosen.
