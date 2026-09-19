# Observer

The *Observer* pattern, a kind of callback,
decouples code that changes state from code that reacts to the change.
An *observer* registers interest with a *subject*.
Whenever the subject changes state, it notifies the observer.
The subject defines only a list of callables and the arguments it passes to them.
That choice follows [the principle of designing the communication rather than the parts](21_Patterns--Design_Patterns.md#design-principles).
*Observer* is the most dynamic of the callback patterns because observers attach and detach at runtime,
and the subject does not name their concrete types.

Event handling is the everyday use.
A widget keeps a list of handlers and calls each one when its event arrives.
More generally, use *Observer* if a group of objects must update themselves when other objects change state.
The classic example is Smalltalk's MVC (model-view-controller),
or the nearly-equivalent Document-View architecture.
A *document* has more than one way to view it, for example a plot and a table.
When the data changes, every view must refresh.
With *Observer*, a change in the subject's data notifies each interested view.

## The Classic Observer: an Interface to Implement

The classic design comes from *GoF Design Patterns*,
and this section uses its vocabulary: the object that changes is the *subject*,
and each *observer* implements an interface with one method.

The design has three parts: an `Observer` interface every observer implements,
a `Subject` base class that keeps the observer list,
and `Subject.notify()` that broadcasts to every observer:

```python
# classic_observer.py
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

    def detach(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self, arg: T) -> None:
        for observer in list(self._observers):
            observer.update(self, arg)

class Display:
    def update(
        self, subject: Subject[float], arg: float
    ) -> None:
        print(f"display: {arg}C")

class Thermometer(Subject[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    def set_celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)

t = Thermometer(20.0)
t.attach(Display())
t.set_celsius(25)
#: display: 25C
```

`update()` is where each observer reacts.
`notify()` calls it on every observer in the list,
so one change to the subject's state reaches all of them:
`Display` prints the new reading, and a plot or a table redraws.

`Thermometer` holds the list and names no observer type,
so a `Plot` or a `Table` attaches the same way `Display` does.

Passing `arg` is the *push* model.
The subject (`Thermometer`) supplies what changed (the temperature),
so an observer needs no reference back into the subject's state.
The *pull* model sends only `subject` and lets each observer read what it needs by calling back into the subject,
here `subject.celsius`.
With pull, the subject does not decide what its observers need.
In exchange, each observer depends on the subject's interface:
to read `celsius`, an observer must know it is watching a `Thermometer`.

GoF leaves one choice open: who calls `notify()`.
Here `set_celsius()` calls it, so every change broadcasts at once.
The alternative leaves that call to the client,
so several changes can coalesce into one broadcast,
but a caller can forget to make the call.

### Why `notify()` Copies the List

The `list(self._observers)` copy inside `notify()` looks redundant,
since `_observers` is already a list.
It is not.
An observer may react to a notification by detaching,
and a detach that reached the list the loop is reading would make the loop skip the next observer,
with no exception to report the skip.
The copy is a second list,
so `detach()` changes `self._observers` while the loop reads a list nobody is modifying.
The set of observers is therefore fixed when `notify()` begins.
An observer detached partway through still receives this notification,
and a newcomer attaching mid-notification receives its first one at the next change.
[Unsubscribing During a Notification](#unsubscribing-during-a-notification)
traces the failure the copy prevents, one index at a time.

## The Names This Chapter Uses

The pattern's traditional names are hard to hold in your head.
`java.util.Observable` and the reactive libraries call the subject an `Observable`.
`Observer` and `Observable` share a stem and name opposite roles,
so every listing asks you to decode which end you are looking at.
GoF's `notify()` and `update()` name one event from two sides.
The rest of this chapter uses names you can tell apart at a glance:

| *GoF Design Patterns* | This chapter |
|---|---|
| subject | `Broadcaster` |
| observer | listener, any callable |
| `attach()` / `detach()` | `subscribe()` / `unsubscribe()` |
| `notify()` | `announce()` |
| `update()` | calling the listener |

The pattern keeps its name.
*Observer* is what the catalogs call it,
and those libraries use the older nouns,
so the table is also your map into that literature.

## The Pythonic Observer: a List of Callables

In Python a listener is any callable that takes the notification and returns `None`,
and a broadcaster is a list of those callables plus a way to announce a change to them.
A `@property` setter runs at every assignment to its attribute,
so the setter is the place to send the notification when state changes:

```python
# broadcaster.py
from collections.abc import Callable

type Listener[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Listener[T]) -> None:
        self._listeners.remove(listener)

    def announce(self, data: T) -> None:
        for listener in list(self._listeners):
            listener(data)

class Thermometer(Broadcaster[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.announce(value)
```

The constructor assigns its argument to `_celsius` rather than to `celsius`,
so construction skips the setter and doesn't call `announce()`.

Subscribed callables react to every `celsius` assignment:

```python
# thermometer.py
from broadcaster import Thermometer

t = Thermometer(20.0)
t.subscribe(lambda c: print(f"display: {c}C"))
t.subscribe(lambda c: print("alarm!" if c > 100 else "ok"))
t.celsius = 25
#: display: 25C
#: ok
t.celsius = 150
#: display: 150C
#: alarm!
```

The listeners here are lambdas, but any function or bound method works.

![One assignment to celsius calls every listener in the list](_images/observer_broadcast)

The dashed `plot` is not in the listing.
Any callable of the right shape subscribes the way the two lambdas do,
and `Thermometer` names no listener type.

Four things from the classic version disappear: the `Observer` interface,
its `update()` method, a class per reaction, and the `subject` argument.
A classic observer is an object,
so the subject needs the name of a method to call on it.
In Python the listener is the callable, so `announce()` calls it directly:
`listener(data)`, where the classic version calls `observer.update(self, arg)`.
The remaining method names change as well:
GoF's `attach()` and `detach()` become `subscribe()` and `unsubscribe()`,
as in the reactive libraries.
A listener that needs the changed object takes it as part of the payload
(`announce((self, value))`),
or subscribes a bound method whose instance already holds the reference.

`Thermometer` inherits `Broadcaster` because that is the shortest way to get `subscribe()` and `announce()`,
not because the pattern requires a base class.
A `Thermometer` can hold a `Broadcaster` as an attribute instead
(`self.temperature_changed = Broadcaster[float]()`),
and a subscriber then names that attribute:
`t.temperature_changed.subscribe(display)`.
One object can hold several such attributes,
so it can publish more than one kind of change.
[Notifying Without a Base Class](#notifying-without-a-base-class)
drops the base class and the properties together.
Event-heavy programs have mature libraries (signal/slot systems),
but for most cases the *Observer* pattern is only a list of callbacks.

`Thermometer`'s constructor is simple and suggests using a `dataclass`.
Inheriting does not stop a class from being a `dataclass`,
but [a generated `__init__()` does not call the base class's `__init__()`](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance).
A `@dataclass` `Thermometer` would have no list of listeners,
and `subscribe()` would raise an `AttributeError`.
A `__post_init__()` that calls `super().__init__()` fixes that,
but at greater length and complexity than the `__init__()` it replaces.

A listener returns `None`, as seen in the `Listener` alias.
The type checker rejects a subscriber that returns a value.
Notification runs one way, from broadcaster to listeners,
so `announce()` calls each listener as a statement.
*GoF Design Patterns* gives the reason under broadcast communication.
A notification names no receiver, and each listener may handle or ignore it,
so one call with several listeners has no single answer to collect.
A design that needs an answer uses a different pattern;
for example [*Chain of Responsibility*](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime)
tries its handlers in turn and returns the result from the first one that succeeds.

### Testing the Broadcaster

Testing confirms that `celsius` reports the value given to the constructor,
that every subscriber receives the new value in subscription order,
that a subscriber receives only the changes made after it subscribes,
and that delivery stops after `unsubscribe()`.
Two more tests cover a callable subscribed twice and an `unsubscribe()` that matches no subscription:

```python
# test_broadcaster.py
import pytest
from broadcaster import Broadcaster, Thermometer

def test_announce_calls_every_subscriber() -> None:
    received: list[tuple[str, object]] = []
    source = Broadcaster[int]()
    source.subscribe(lambda d: received.append(("a", d)))
    source.subscribe(lambda d: received.append(("b", d)))
    source.announce(42)
    assert received == [("a", 42), ("b", 42)]

def test_no_subscribers_is_a_noop() -> None:
    # Must not raise anything
    Broadcaster[str]().announce("anything")

def test_unsubscribe_stops_delivery() -> None:
    received: list[object] = []
    source = Broadcaster[object]()
    source.subscribe(received.append)
    source.announce(1)
    # A new bound method: equal, not identical
    source.unsubscribe(received.append)
    source.announce(2)
    assert received == [1]

def test_subscribing_twice_notifies_twice() -> None:
    received: list[object] = []
    source = Broadcaster[object]()
    record = received.append
    source.subscribe(record)
    source.subscribe(record)
    source.announce(1)
    assert received == [1, 1]
    source.unsubscribe(record)  # Removes one of the two
    source.announce(2)
    assert received == [1, 1, 2]

def test_unsubscribe_without_subscribe_raises() -> None:
    source = Broadcaster[object]()
    with pytest.raises(ValueError):
        source.unsubscribe(print)

def test_thermometer_pushes_new_value_on_set() -> None:
    readings: list[float] = []
    t = Thermometer(20.0)
    assert t.celsius == 20.0  # The starting reading
    t.subscribe(readings.append)
    t.celsius = 25.0
    t.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert t.celsius == 150.0

def test_late_subscriber_misses_earlier_changes() -> None:
    readings: list[float] = []
    t = Thermometer(0.0)
    t.celsius = 10.0  # No subscriber yet
    t.subscribe(readings.append)
    t.celsius = 20.0
    assert readings == [20.0]
```

The tests subscribe a list's `append` to the broadcaster,
so the list records what arrived.
`unsubscribe()` matches by equality, and a lambda equals only itself,
so a listener you mean to remove later needs a named reference,
not an inline lambda.
A bound method needs no stashed reference,
as `test_unsubscribe_stops_delivery()` shows.
Each `received.append` builds a new bound-method object,
so `received.append is received.append` is `False`.
Two bound methods compare equal when they wrap the same instance and the same function,
so `unsubscribe(received.append)` removes the subscription that `subscribe(received.append)` made.
The same equality rule explains the last two tests.
Subscribing one callable twice puts two equal entries in the list,
so each notification calls it twice and each `unsubscribe()` removes one entry.
`list.remove()` raises a `ValueError` when it matches nothing,
which is what `unsubscribe()` does with a callable that never subscribed.

### Unsubscribing During a Notification

The copy in `announce()` shows its value when a listener unsubscribes mid-notification:

```python
# self_removing_listener.py
from broadcaster import Broadcaster

source = Broadcaster[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    source.unsubscribe(once)

def always(data: object) -> None:
    seen.append(f"always: {data}")

source.subscribe(once)
source.subscribe(always)
source.announce(1)
source.announce(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` receives the first change and unsubscribes.
That call removes it from the broadcaster's list,
not from the copy the loop is reading,
so `once` finishes this notification and receives none after it.
`always` receives both.
Without the copy, the loop would be reading the list it changes.
`once` is at index 0 and `always` at index 1.
Removing `once` moves `always` to index 0, which the loop has already visited,
so the loop looks for index 1, finds the list ended there, and stops.
`always` misses the first change, and `seen` ends as `['once: 1', 'always: 2']`,
with no exception to say a listener was skipped.

### A Listener That Raises an Exception

A listener that raises an exception stops the loop,
and the listeners after it are not called.
Decide whether `announce()` should catch, collect, and continue
(exercise 2 makes this concrete).

### Lapsed Listeners

Subscriptions are strong references.
A bound method holds the object it came from,
so subscribing `plot.redraw` keeps that `plot` in memory for as long as the broadcaster holds the subscription.
A broadcaster that outlives its listeners holds every one of them that way,
the classic *lapsed listener* leak.
Long-lived broadcasters need disciplined `unsubscribe()` calls,
or [weak references](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
which do not keep the listener alive
(`weakref.WeakMethod` is the bound-method form).
A weak listener resolves its reference at every call and drops out once its object is gone:

```python
# weak_listener.py
from weakref import WeakMethod
from broadcaster import Broadcaster
from exceptions import expected

class Plot:
    def redraw(self, celsius: float) -> None:
        print(f"plot: {celsius}C")

source = Broadcaster[float]()
plot = Plot()
ref = WeakMethod(plot.redraw)

def weak(celsius: float) -> None:
    live = ref()
    if live is None:
        source.unsubscribe(weak)  # Gone: drop out
    else:
        live(celsius)

source.subscribe(weak)
source.announce(25.0)
#: plot: 25.0C

del plot  # The only strong reference
source.announce(30.0)  # Prints nothing

with expected(ValueError):
    source.unsubscribe(weak)
#: [ValueError] list.remove(x): x not in list
```

A `Broadcaster` holds a strong reference to whatever you subscribe,
so the weak part lives inside the listener.
`WeakMethod` stores the instance and the function separately, both weakly,
and rebuilds the bound method when you call the reference.
An ordinary `weakref.ref(plot.redraw)` is dead the moment it is created:
`plot.redraw` builds a new bound-method object that nothing else holds,
so Python collects it at once and the reference returns `None`.
While `plot` is alive, `weak` forwards the reading to it.
Once `plot` is gone, `ref()` returns `None` and `weak` unsubscribes itself,
which is safe mid-notification because `announce()` loops over a copy.
The `ValueError` confirms the subscription is gone:
`unsubscribe()` finds nothing left to remove.

### Re-entrant Notification

A listener that writes back to the broadcaster re-enters `announce()` from inside `announce()`.
Two-way bindings are the usual source.
The view edits the model, the model notifies the view, the view edits the model.
Without a guard, a listener that always writes back recurses until Python raises a `RecursionError`:

```python
# reentrant_announce.py
from broadcaster import Broadcaster
from exceptions import expected

class TwoWay(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int) -> None:
        self._value = new
        self.announce(new)  # Re-enters if written back

model = TwoWay()
model.subscribe(
    lambda v: setattr(model, "value", v))
with expected(RecursionError):
    model.value = 1
#: [RecursionError] maximum recursion depth exceeded
```

The setter calls `announce()`, the listener writes back through the same setter,
and each write calls `announce()` again.
To break the cycle, the setter returns early when the new value equals the stored one:

```python
# reentrant_announce_fixed.py
from broadcaster import Broadcaster

class TwoWay(Broadcaster[int]):
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
        self.announce(new)

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

`echo` writes back the value the model now stores,
so the setter returns before it reaches `announce()` a second time.
`announce()` runs once, for the original assignment.
The alternative is a re-entry flag, set before `announce()` and cleared after,
with the setter returning early while the flag is set.
The flag breaks the cycle without comparing values,
so a second write of the same reading still reaches the listeners,
which is the behavior you want when a listener counts readings rather than changes.

### Notifying Without a Base Class

`Thermometer` writes a getter and a setter for each attribute it publishes,
and inherits `subscribe()` and `announce()` from `Broadcaster`.
We can simplify all of this using `__setattr__()`.
Python calls it on every attribute assignment,
so one method covers every attribute of the class:

```python
# watched.py
from collections.abc import Callable

type Watcher = Callable[[str, object], None]

class Watched:
    _watchers: list[Watcher]  # Bare annotation

    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        # __setattr__() reads _watchers, so it
        # must exist before the first assignment
        self.__dict__["_watchers"] = []
        self.celsius = celsius
        self.humidity = humidity

    def watch(self, watcher: Watcher) -> None:
        self._watchers.append(watcher)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        super().__setattr__(name, value)
        for watcher in list(self._watchers):
            watcher(name, value)

w = Watched(20.0, 0.4)
changes: list[tuple[str, object]] = []
w.watch(lambda n, v: changes.append((n, v)))
w.celsius = 25.0
w.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
```

The constructor writes `_watchers` through `self.__dict__` to bypass `__setattr__()`,
which would read `_watchers` before the assignment that creates it.
The two assignments after that line are ordinary
(they go through `__setattr__()`).
Each notifies a list that is still empty;
because the constructor hasn't returned, no caller can register a watcher.
`super().__setattr__()` does the storing,
because an ordinary assignment inside `__setattr__()` would call `__setattr__()` again.

In a class body, a name with a type and no initialization value [declares an attribute rather than creating one](09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create).
Such a name is a *bare annotation*.
It looks like a class variable but is not, because it is not assigned a value.
`_watchers` creates no attribute anywhere,
and the constructor gives each `Watched` its own `_watchers` list.
The same line with `= []` would create a class attribute,
a single list shared by every `Watched`.
[Class Attributes](09_Foundations--Class_Attributes.md#a-classvar-with-no-value-declares-too)
covers the difference between declaring an attribute and creating one,
for instance attributes and class variables both.

`ty` takes an instance attribute and its type from an assignment like `self.celsius = celsius`,
which is why `celsius` and `humidity` need no declaration.
The constructor writes `self.__dict__["_watchers"] = []` instead,
a write to a dictionary rather than an assignment to an attribute,
and `ty` does not read it as one.
The bare annotation supplies what that assignment would have: without it,
`ty` reports an `unresolved-attribute` error in each method that reads the list.

One method for every attribute is less precise than a property per attribute,
in three ways.
First, a watcher is a listener with a wider signature:
it takes the attribute name along with the value,
and filters by name to act on one attribute.
`Thermometer` publishes one attribute and is a `Broadcaster[float]`,
so its listeners take the `float` reading and need no name.
Second, every assignment reaches the watchers, including the internal ones:
a cached result or a hit counter broadcasts like a published attribute,
unless the class writes it through `self.__dict__` as the constructor does.
Third, `__setattr__()` accepts any name,
so `ty` stops checking assignments and reports nothing for `w.celcius = 25.0`,
which quietly creates a new attribute.
The same misspelling on `Thermometer` is an `unresolved-attribute` error.
`Thermometer` defines no `__setattr__()`,
so `ty` checks each assignment against the attributes the class declares.

## Observer and I/O

So far, no listener has had to wait.
Each prints, appends, or writes back, then returns.
If a listener calls a network service or writes to a database,
notifying listeners one at a time delays every listener after it.

If listeners are coroutines,
`announce()` awaits them together with `asyncio.gather()`,
so one state change notifies every listener concurrently.
A slow listener no longer delays the others.
`gather()` waits for all of them,
so `announce()` returns only after every listener finishes.

An `async` setter returns a coroutine instead of running its body,
and an assignment offers no place for the `await` that would run the coroutine.
The assignment therefore discards the coroutine, and the body never runs.
The state change becomes an awaitable method rather than the assignment `t.celsius = value`.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
covers the `asyncio` mechanics here (`async def`, `await`, `gather()`, `run()`).
For this example, it is enough to know that a coroutine pauses at `await` while others run:

```python
# async_broadcaster.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncListener[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[AsyncListener[T]] = []

    def subscribe(self, listener: AsyncListener[T]) -> None:
        self._listeners.append(listener)

    def unsubscribe(
        self, listener: AsyncListener[T]
    ) -> None:
        self._listeners.remove(listener)

    async def announce(self, data: T) -> None:
        # Fan out to every listener, then wait for all
        await asyncio.gather(
            *(fn(data) for fn in self._listeners))

class Thermometer(Broadcaster[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    async def set_celsius(self, value: float) -> None:
        # A property setter cannot be awaited
        self._celsius = value
        await self.announce(value)
```

The module defines classes and runs nothing,
so a later listing can import `Broadcaster` without starting a demo.
The thermometer demo lives in its own file, and its listeners are coroutines:

```python
# async_thermometer.py
import asyncio
from async_broadcaster import Thermometer

async def alarm(celsius: float) -> None:
    if celsius > 100:
        await asyncio.sleep(0.05)  # Slow network alert
        print(f"alarm sent: {celsius}C")

async def log_reading(celsius: float) -> None:
    await asyncio.sleep(0.01)  # Faster local write
    print(f"logged: {celsius}C")

async def main() -> None:
    t = Thermometer(15.0)
    t.subscribe(alarm)
    t.subscribe(log_reading)
    await t.set_celsius(20)  # Below the alarm threshold
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
```

`gather()` takes one awaitable per argument rather than an iterable of them,
so `announce()` calls the listeners in a generator expression and [unpacks](05_Foundations--Functions.md#unpacking-arguments)
that generator with `*`, turning each coroutine into its own argument.

The `AsyncListener` alias makes the type checker reject a plain function as a listener.
A listener must return an awaitable,
and calling an `async` function produces one.
The type checker also rejects the reverse mistake,
an `async` function subscribed to the synchronous `Broadcaster`.
Calling that function returns a coroutine rather than `None`,
and a coroutine discarded without an `await` does nothing.
In both aliases the type parameter ties the listener's argument to the broadcaster's payload:
a `Broadcaster[float]` accepts a listener that takes a `float` and rejects one that takes a `str`.

The `alarm` is slower than the log, yet the log prints first.
Awaiting the listeners in sequence would print in subscription order,
alarm first.
Concurrent fan-out lets each listener finish as soon as its own wait ends,
so the faster listener prints first.
The results `gather()` returns stay in argument order regardless.
Only the side effects interleave.

A listener need not act on every notification.
Below its threshold, the alarm returns at once.

### Unsubscribing During an Async Notification

The async `announce()` needs no `list()` copy.
The `*` unpacks the generator into a tuple of coroutines before `gather()` runs,
so an unsubscribe during the fan-out cannot skip a listener.
The tuple also means a listener that unsubscribes mid-notification still receives this change,
an async counterpart to `self_removing_listener.py`:

```python
# async_self_removing_listener.py
import asyncio
from async_broadcaster import Broadcaster

source = Broadcaster[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    source.unsubscribe(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    source.subscribe(once)
    source.subscribe(always)
    await source.announce(1)
    await source.announce(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` unsubscribes while `gather()` is running it,
and `always` still receives the change,
because `gather()` held both coroutines before either ran.
The next `announce()` builds its tuple from the shortened list and calls `always` alone.

### A Failing Listener Orphans the Rest

A failing asynchronous listener behaves differently from a failing synchronous one.
`gather()` re-raises the first exception to its caller right away,
and the unfinished listeners keep running with nobody awaiting them:

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
and an exception from the orphan is discarded without a report.
`gather(*coros, return_exceptions=True)` returns the failures as data instead,
the async form of exercise 2's catch-collect-continue.
[Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup` is the usual choice for concurrent awaits,
but not here.
A `TaskGroup` cancels a failing task's siblings,
so a single broken listener would cancel the others mid-notification.

Use the async fan-out only when the listeners are I/O-bound.
For in-memory listeners the synchronous `Broadcaster` from `broadcaster.py` is simpler and needs no event loop.

## A Visual Example: a Model and Its View

This example emphasizes the model-view split.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule that decides what a selection changes.
It only manipulates `Grid`s and doesn't know anything about displaying them.
The *view*, `box_view.py`,
displays the boxes using the standard library's `tkinter`.
Clicking a box advances it to the next color, along with the boxes above, below,
left, and right of it.
A click changes up to five boxes at once, so the window is a puzzle:
try to turn every box `palegreen`.
From this starting grid, `palegreen` is the one color all the boxes can share.
No sequence of clicks turns the grid all `skyblue` or all `khaki`.

The model reuses the same `Broadcaster` as the thermometer,
from `broadcaster.py`:

```python
# box_observer.py
from enum import StrEnum
from broadcaster import Broadcaster

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

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class BoxModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)
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

`recolored()` computes the grid that results from selecting a cell: values in,
values out.
`cross` lists the selected cell and the four cells that share an edge with it.
A cell on the border has fewer neighbors,
so some of the coordinates in `cross` lie outside the grid.
A `Grid` is keyed by coordinate,
so `cell in grid` is `True` only for a coordinate inside the grid.
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
`BoxModel` is a `Broadcaster[Grid]`.
Like `Thermometer`, it writes its own `__init__()`,
which calls `Broadcaster.__init__()` and then builds `grid` from `size`.
`BoxModel.select()` makes the next grid with `recolored()` and passes it to `announce()`.
An enum, two functions, and one class make up the model:
`Color` holds the colors and their order, the functions compute grids,
and `BoxModel` holds the current grid and notifies its listeners.

### Testing the Model

The model contains no display code, so you can test it without a GUI.
Testing confirms that `recolored()` changes the cross and no other cell,
that a selection in a corner stays on the grid,
and that listeners receive the new grid after one:

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

def test_corner_selection_stays_on_the_grid() -> None:
    grid = new_grid(3)
    out = recolored(grid, (0, 0))
    changed = {c for c in grid if out[c] != grid[c]}
    assert changed == {(0, 0), (1, 0), (0, 1)}
    assert out.keys() == grid.keys()

def test_model_notifies_with_the_new_grid() -> None:
    model = BoxModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    # The listener is a callable
    model.subscribe(seen.append)
    model.select((1, 1))
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
```

### The View

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
                lambda e: model.select(
                    (e.x // cell_px, e.y // cell_px)))
    draw(model.grid)
    root.mainloop()

if __name__ == "__main__":
    show(BoxModel(8))
```

`show()` makes a square canvas, `model.size` cells on a side,
each cell `cell_px` pixels wide.
`draw()` paints the grid, and the view subscribes `draw()` to the model,
so every change repaints.
`draw()` is defined inside `show()`,
so it is a closure that reads `canvas` and `cell_px`.
It paints one rectangle per cell,
multiplying the cell's column and row by `cell_px` to get the rectangle's corners in pixels.
It takes a `Grid` and returns `None`,
the shape `subscribe()` requires of a listener.
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
A click on the canvas becomes a `select()` on the model,
and the resulting notification repaints the view.
The handler calls the model and draws nothing.
The mouse belongs to the view.
The model's method is `select()`, so a keypress, a touch,
or a test call reaches the same rule.

The model and the view share only the subscribe-and-announce contract,
so you can attach a second view to the same model and keep both views in step.

## What Stays Constant

One design serves three jobs in this chapter: a thermometer pushing a float,
a fan-out awaiting network calls, and a GUI repainting a grid.
In every case the listener is a callable and the broadcaster is a list of them.
The pattern requires no interface, no `update()` method,
and no class per reaction.
[Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
takes the last step.
One list becomes a dictionary of lists keyed by event type,
and the *Observer* is an event bus.

## Exercises

1.  Create a minimal *Observer* design of your own,
    without looking at `broadcaster.py`:
    the smallest `Broadcaster` that lets callables subscribe,
    then notifies them.
    Demonstrate it by subscribing several listeners and causing one change that updates them all.
2.  Make `Broadcaster.announce()` survive a listener that raises an exception:
    every other listener is still notified,
    and `announce()` re-raises the failures afterward, together,
    as an [`ExceptionGroup`](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
    (which you build yourself here: `raise ExceptionGroup("message", failures)`).
    Write a test in which the first listener raises an exception and the second still records its notification.
3.  Redo exercise 2 for `async_broadcaster.py`.
    Make `announce()` use `gather(*coros, return_exceptions=True)`,
    separate the returned exceptions from the successes,
    and raise them together as an `ExceptionGroup`.
    Write a test in which the first listener raises an exception and the second still records its notification.
4.  Turn `box_observer.py` into a simple game:
    you own the contiguous patch of same-colored squares containing the top-left corner,
    and selecting any square recolors your patch to that square's color,
    absorbing neighbors that now match.
    Write the neighbor test yourself, counting diagonals.
    Track the moves it takes to make the whole field one color.
    For competition, alternate turns between players.
5.  Change the rule for a selection in `box_observer.py`:
    make `recolored()` advance every box in the selected box's row and column.
    Run `box_view.py` without editing it,
    and explain why the view needed no change.
6.  Write a `Notifying` descriptor
    ([Metaprogramming](17_Techniques--Metaprogramming.md#a-descriptor-that-validates))
    that replaces the `@property` and `announce()` pair,
    so one class declares several independently watched attributes:
    `celsius = Notifying[float]()` beside `humidity = Notifying[float]()`.
    Each attribute keeps its own listeners.
    Subscribing needs the descriptor, not the value it stores,
    so `__get__()` returns the descriptor when the class accesses it,
    and `Thermometer.celsius.subscribe(t, readings.append)` reaches it.
    Show that an assignment to one attribute calls no listener of the other.
