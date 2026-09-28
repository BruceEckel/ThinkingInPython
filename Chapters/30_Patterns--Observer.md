# Observer

> Something changes, and something else is interested in that change.
> The *Observer* pattern connects the two.

![](_images/coupling_30)

*Observer* decouples code that changes state from code that reacts to that state change.
An *observer* attaches to a *subject*.
When the subject changes state, it notifies the observer.
The subject knows each observer only as something to call,
and it decides which arguments every call receives.
This is [designing the communication rather than the parts](21_Patterns--Design_Patterns.md#design-principles).

*Observer* is the most dynamic of the callback patterns because observers attach and detach at runtime.
Use *Observer* if a group of objects must update themselves when other objects change state.
Event handling typically works this way:
a widget keeps a list of handlers and calls each one when its event arrives.

The classic example is Smalltalk's *Model-View-Controller* (MVC),
or the nearly-equivalent *Document-View* architecture,
which folds the controller into the view.
In both, *Observer* connects the state change to its views:
one subject keeps a list of views and accepts any view that has the update method it calls.
This way, a *document* can have more than one way to view it,
such as a plot and a table.
When the data changes, every view must refresh.
With *Observer*, a change in the subject's data notifies each interested view.

## The Classic Observer

The classic design comes from *GoF Design Patterns*:

- The object that changes is the *subject*
- Each *observer* implements an interface with one method

The GoF design has three parts:
an `Observer` interface every observer implements,
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
```

`notify()` calls `update()` on every observer in the list,
so one change to the subject's state reaches all observers.

`Thermometer`'s `set_celsius()` stores the new reading and calls `notify()`:

```python
# classic_thermometer.py
from classic_observer import Subject

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
```

`Subject` creates the observer list in its constructor,
so `Thermometer`'s constructor must call [`super().__init__()`](07_Foundations--Classes.md#calling-the-base-constructor).
If you remove that call, a `Thermometer` has no `_observers` attribute,
and `attach()` raises an `AttributeError`.

`Display` is an observer that prints each new reading:

```python
# classic_thermometer_demo.py
from classic_observer import Subject
from classic_thermometer import Thermometer

class Display:
    def update(
        self, subject: Subject[float], arg: float
    ) -> None:
        print(f"display: {arg}C")

t = Thermometer(20.0)
t.attach(Display())
t.set_celsius(25)
#: display: 25C
```

`Thermometer`'s list accepts any `Observer[float]`,
meaning any object with a matching `update()` method,
so a `Plot` or a `Table` that redraws attaches as easily as `Display` does.

### Push or Pull

Passing `arg` is the *push* model.
The subject (`Thermometer`) supplies what changed (the temperature),
so an observer works from the value it receives.
The *pull* model sends only `subject` and lets each observer read what it needs by calling back into the subject,
here `subject.celsius`.
With pull, the subject does not decide what its observers need.
Each observer depends on the subject's interface: to read `celsius`,
an observer must know it is watching a `Thermometer`.
The type checker enforces that dependency.
`Subject[float]` has no `celsius`,
so the observer must declare its `subject` parameter as a `Thermometer`,
and `Observer[float]` rejects an `update()` with that narrower parameter.
To use pull, you must add either a runtime `isinstance()` check or a second type parameter on the protocol.

GoF leaves a second choice open, separate from push or pull:
who calls `notify()`.
Here `set_celsius()` calls it, so every change broadcasts at once.
Otherwise the client calls `notify()` after making its changes,
so several changes can coalesce into one broadcast,
but a client can forget to make the call.

### Why `notify()` Copies the List

`_observers` is a list, so inside `notify()`,
the copy via `list(self._observers)` appears redundant.
It is not.

The problem is that an observer may react to a notification by detaching.
If the `for` loop in `notify()` reads `self._observers` directly,
that `detach()` shifts the remaining observers down one index,
and the loop skips the observer after the one that detached,
without raising an exception.
With the copy, the `for` loop reads a second list,
so `detach()` changes `self._observers` while the loop reads a list nobody is modifying.
The copy therefore settles which observers a `notify()` call reaches before its loop starts.
An observer detached partway through a `notify()` call still receives that call's notification,
and a newcomer attached during the call receives its first notification from the next `notify()` call.
[Unsubscribing During a Notification](#unsubscribing-during-a-notification)
runs a responder that unsubscribes itself,
and shows index by index which responder the loop skips without the copy.

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
| observer | responder == any callable |
| `attach()` / `detach()` | `subscribe()` / `unsubscribe()` |
| `notify()` | `announce()` |
| `update()` | calling the responder |

The catalog calls it *Observer*,
and Java and the reactive libraries use the older nouns,
so the table is also your map into that literature.
Java and JavaScript call a responder a *listener*,
as in `ActionListener` and `addEventListener()`.

The essential part of *Observer* is the response: something changes,
and code elsewhere runs because of it.
The words "observer" and "listener" name a role that waits and watches,
and neither word says what happens when the change arrives.
"Responder" names the action,
so the word points you at the question every design here must answer:
what does this code do when a change reaches it?
The rest of the chapter keeps returning to that question.
A responder can unsubscribe itself mid-notification, raise an exception,
wait on a slow network call, or write back to its broadcaster,
and each of those behaviors changes how the broadcaster must be written.

## The Pythonic Observer: Callables in a List

A responder is any callable that takes a notification and returns `None`.
A broadcaster keeps a list of those callables and announces each change to every one:

```python
# broadcaster.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def subscribe(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def unsubscribe(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
```

Four things from the classic version disappear: the `Observer` interface,
its `update()` method, a class per reaction, and the `subject` argument.
A classic observer is an object,
so `notify()` calls the method its interface names, `update()`.
In Python the responder is a callable, so `announce()` calls it directly:
`responder(data)`, whereas the classic version calls `observer.update(self, arg)`.
The remaining method names change as well:
GoF's `attach()` and `detach()` become `subscribe()` and `unsubscribe()`.
A responder that needs the changed object takes it as part of the payload
(`announce((self, value))`),
or is a bound method of an object that holds a reference to the broadcaster.

`Broadcaster` knows nothing about what it announces.
Its type parameter `T` fixes the type of each notification,
and a class that inherits `Broadcaster` gets `subscribe()`, `unsubscribe()`,
and `announce()`.

A responder returns `None`, as seen in the `Responder` alias.
The type checker rejects a subscriber that returns a value.
Notification runs one way, from broadcaster to responders,
so `announce()` calls each responder as a statement.
*GoF Design Patterns* gives the reason under broadcast communication.
A notification names no receiver, and each responder may handle or ignore it,
so one call with several responders has no single answer to collect.
A design that needs an answer uses a different pattern;
for example [*Chain of Responsibility*](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime)
tries its handlers in turn and returns the result from the first one that succeeds.

`Thermometer` announces from its `celsius` setter.
A setter runs at every assignment to its attribute,
so every assignment to `celsius` reaches the responders:

```python
# thermometer.py
from broadcaster import Broadcaster

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

The constructor assigns its argument directly to `_celsius` rather than to `celsius`,
which would go through the setter.
This way, construction skips the setter and doesn't call `announce()`.

`Thermometer`'s constructor is simple and suggests using a `dataclass`.
Inheriting does not stop a class from being a `dataclass`,
but [a `dataclass`-generated `__init__()` does not call the base class's `__init__()`](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance).
A `@dataclass` `Thermometer` has no list of responders,
and `subscribe()` raises an `AttributeError`.
A `__post_init__()` that calls `super().__init__()` fixes that,
but at greater length and complexity than the `__init__()` it replaces.

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

Subscribed callables react to every `celsius` assignment:

```python
# thermometer_demo.py
from thermometer import Thermometer

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

The responders here are lambdas, but any function or bound method works.

![Assigning to celsius calls every responder](_images/observer_broadcast)

The dashed `plot` responder is not part of the example.
It's in the diagram to show that any callable of the right shape subscribes with the same `subscribe()` call as the two lambdas.
`Thermometer` knows its responders only as callables that take a `float`.

### Testing the Broadcaster

Testing confirms that `celsius` reports the value given to the constructor,
that every subscriber receives the new value in subscription order,
that a subscriber receives only the changes made after it subscribes,
and that delivery stops after `unsubscribe()`.
Two more tests cover a callable subscribed twice and an `unsubscribe()` that matches no subscription:

```python
# test_broadcaster.py
import pytest
from broadcaster import Broadcaster
from thermometer import Thermometer

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
so the list records every announced value.

You cannot `unsubscribe()` a lambda;
you need a named reference to the responder.
`unsubscribe()` matches by equality, and a lambda equals only itself.

A bound method is different:
`test_unsubscribe_stops_delivery()` unsubscribes `received.append` without storing it first.
Each `received.append` builds a new bound-method object,
so `received.append is received.append` is `False`.
Two bound methods compare equal when they wrap the same instance and the same function,
so `unsubscribe(received.append)` removes the subscription that `subscribe(received.append)` made.

The same equality rule explains the last two tests.
Subscribing one callable twice puts two equal entries in the list,
so each notification calls it twice and each `unsubscribe()` removes one entry.

`list.remove()` raises a `ValueError` when it matches nothing,
so `unsubscribe()` raises a `ValueError` when its callable never subscribed.

### Unsubscribing During a Notification

The copy in `announce()` matters when a responder unsubscribes mid-notification:

```python
# self_removing_responder.py
from broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Unsubscribes mid-notification
    broadcaster.unsubscribe(once)

def always(data: object) -> None:
    seen.append(f"always: {data}")

broadcaster.subscribe(once)
broadcaster.subscribe(always)
broadcaster.announce(1)
broadcaster.announce(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` receives the first change and unsubscribes.
That call removes it from the broadcaster's list,
not from the copy that `announce()`'s loop reads,
so `once` still gets this notification but no later ones.
`always` receives both.
Without the copy, `announce()`'s `for` loop reads the list that `unsubscribe()` changes.
`once` is at index 0 and `always` at index 1.
Removing `once` moves `always` to index 0, which the loop has already visited,
so the loop looks for index 1, finds the list ended there, and stops.
`always` misses the first change, and `seen` ends as `['once: 1', 'always: 2']`,
with no exception to say a responder was skipped.

### Raising an Exception

If a responder raises an exception,
the rest of the responders in the list are not called.
The exception leaves `announce()` and reaches the code that assigned to `celsius`.
You must decide whether `announce()` should catch, collect, and continue
(see exercise 3).

Another option keeps the failure inside the responder.
The responder catches its own exception and [returns the error as a value](42_Functional--Error_Handling.md#return-the-error-as-a-value),
and `announce()` collects the returned errors for the caller.
Every responder runs, and no failure escapes as an exception.
However, the `Responder` type becomes a callable that returns a success or an error,
so a method such as `readings.append()`, which returns `None`,
no longer fits without a wrapper (see exercise 5).

### Lapsed Listeners

Subscriptions are strong references.
A bound method holds the object it came from,
so subscribing `plot.redraw` keeps that `plot` in memory for as long as the broadcaster holds the subscription.
When a broadcaster outlives its responders,
its subscriptions keep every one of them in memory:
the classic *lapsed listener* leak.
Long-lived broadcasters need disciplined `unsubscribe()` calls,
or [weak references](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
which do not keep the responder alive
(`weakref.WeakMethod` is the bound-method form).
A weak responder resolves its reference at every call and drops out once its object is gone:

```python
# weak_responder.py
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
so the weak part lives inside the responder.
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

Most programs do not need weak responders.
A broadcaster that lives no longer than its responders releases them when it goes away,
and an explicit `unsubscribe()` covers a responder that leaves early.
A weak responder earns its extra code only when a long-lived broadcaster holds short-lived responders that nothing unsubscribes.

### Re-entrant Notification

A responder that writes back to the broadcaster re-enters `announce()` from inside `announce()`.
Two-way bindings are the usual source.
The view edits the model, the model notifies the view, the view edits the model.
Without a guard, a responder that always writes back recurses until Python raises a `RecursionError`:

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

The setter calls `announce()`,
the responder writes back through the same setter,
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
so a second write of the same reading still reaches the responders,
which is the behavior you want when a responder counts readings rather than changes.

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
        # __setattr__() reads _watchers before it
        # stores, so no assignment can create it
        self.__dict__["_watchers"] = []
        self.celsius = celsius
        self.humidity = humidity

    def watch(self, watcher: Watcher) -> None:
        self._watchers.append(watcher)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        watchers = list(self._watchers)
        super().__setattr__(name, value)
        for watcher in watchers:
            watcher(name, value)

w = Watched(20.0, 0.4)
changes: list[tuple[str, object]] = []
w.watch(lambda n, v: changes.append((n, v)))
w.celsius = 25.0
w.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
```

`__setattr__()` copies `_watchers` before it stores the new value,
so an ordinary `self._watchers = []` raises an `AttributeError`:
the copy reads an attribute that does not exist yet.
The constructor therefore writes `_watchers` through `self.__dict__`,
which bypasses `__setattr__()`.
The two assignments after that line are ordinary
(they go through `__setattr__()`).
Each notifies a list that is still empty;
because the constructor hasn't returned, no caller can register a watcher.
`super().__setattr__()` does the storing,
because an ordinary assignment inside `__setattr__()` calls `__setattr__()` again.

In a class body, a name with a type and no initialization value [declares an attribute rather than creating one](09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create).
Such a name is a *bare annotation*.
It looks like a class variable but is not, because it is not assigned a value.
`_watchers` creates no attribute anywhere,
and the constructor gives each `Watched` its own `_watchers` list.
The same line with `= []` creates a class attribute,
a single list shared by every `Watched`.
[Class Attributes](09_Foundations--Class_Attributes.md#a-classvar-with-no-value-declares-too)
covers the difference between declaring an attribute and creating one,
for instance attributes and class variables both.

`ty` takes an instance attribute and its type from an assignment like `self.celsius = celsius`,
which is why `celsius` and `humidity` need no declaration.
For `_watchers`, the constructor writes `self.__dict__["_watchers"] = []`,
and `ty` treats that as a write to a dictionary,
not an assignment to an attribute.
The bare annotation supplies the attribute and its type instead.
Without it, `ty` reports an `unresolved-attribute` error in each method that reads the list.

One method for every attribute is less precise than a property per attribute,
in three ways.
First, a watcher is a responder with a wider signature:
it takes the attribute name along with the value,
and filters by name to act on one attribute.
`Thermometer` publishes one attribute and is a `Broadcaster[float]`,
so each responder takes the `float` reading as its one argument.
[Deciding What Matters](#deciding-what-matters) revisits that name filter:
a watcher that sorts its own notifications means the subject has left the decision to its responders.
Second, every assignment reaches the watchers, including the internal ones:
a cached result or a hit counter broadcasts like a published attribute,
unless the class writes it through `self.__dict__` as the constructor does.
Third, `__setattr__()` accepts any name,
so `ty` stops checking assignments and passes `w.celcius = 25.0`,
which quietly creates a new attribute.
Making the same typo on a `Thermometer` produces an `unresolved-attribute` error.
`Thermometer` defines no `__setattr__()`,
so `ty` checks each assignment against the attributes the class declares.

## Observer and I/O

So far, no responder has had to wait.
Each prints, appends, or writes back, then returns.
If a responder calls a network service or writes to a database,
notifying responders one at a time delays every responder after that one.

If responders are coroutines,
`announce()` awaits them together with `asyncio.gather()`,
so one state change notifies every responder concurrently.
A slow responder no longer delays the others.
`gather()` waits for all of them,
so `announce()` returns only after every responder finishes.

[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
covers the `asyncio` mechanics here (`async def`, `await`, `gather()`, `run()`).
A coroutine pauses at `await` while others run:

```python
# async_broadcaster.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[AsyncResponder[T]] = []

    def subscribe(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.append(responder)

    def unsubscribe(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.remove(responder)

    async def announce(self, data: T) -> None:
        # Fan out to every responder, then wait for all
        await asyncio.gather(
            *(fn(data) for fn in self._responders))
```

`gather()` takes one awaitable per argument rather than an iterable of them,
so `announce()` calls the responders in a generator expression and [unpacks](05_Foundations--Functions.md#unpacking-arguments)
that generator with `*`, turning each coroutine into its own argument.

The `AsyncResponder` alias makes the type checker reject a plain function as a responder.
A responder must return an awaitable,
and calling an `async` function produces one.
The type checker also rejects the reverse mistake,
an `async` function subscribed to the synchronous `Broadcaster`.
Calling that function returns a coroutine rather than `None`,
and a coroutine discarded without an `await` does nothing.
In both aliases the type parameter ties the responder's argument to the broadcaster's payload:
a `Broadcaster[float]` accepts a responder that takes a `float` and rejects one that takes a `str`.

An `announce()` that awaits is a coroutine,
and its caller must `await` it in turn,
so the setter that calls it must also be `async`.
An `async` setter returns a coroutine instead of running its body,
and an assignment offers no place to `await` that coroutine.
The assignment therefore discards the coroutine, and the body never runs.
So the asynchronous `Thermometer` changes `celsius` with an awaitable method,
`set_celsius()`, rather than the assignment `t.celsius = value`,
and reads it through a property as the synchronous one does:

```python
# async_thermometer.py
from async_broadcaster import Broadcaster

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

Neither module runs anything,
so a later listing can import `Broadcaster` without starting a demo.
The demo lives in its own file, and its responders are coroutines:

```python
# async_thermometer_demo.py
import asyncio
from async_thermometer import Thermometer

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

`alarm` subscribes before `log_reading`,
yet at 150 degrees the log prints first.
Awaiting the responders in sequence prints in subscription order, alarm first.
Concurrent fan-out lets each responder finish as soon as its own wait ends,
so the faster responder prints first.
The results `gather()` returns stay in argument order regardless.
Only the side effects interleave.

A responder need not act on every notification.
Below its threshold, the alarm returns at once.

### Unsubscribing During an Async Notification

The async `announce()` needs no `list()` copy.
The `*` unpacks the generator into a tuple of coroutines before `gather()` runs,
so an unsubscribe during the fan-out cannot skip a responder.
The tuple also means a responder that unsubscribes mid-notification still receives this change,
an async counterpart to `self_removing_responder.py`:

```python
# async_self_removing_responder.py
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

### A Failing Responder Orphans the Rest

A failing asynchronous responder behaves differently from a failing synchronous one.
`gather()` re-raises the first exception to its caller right away,
and the unfinished responders keep running with nobody awaiting them:

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
`slow` is still sleeping at that point, with nothing left awaiting it.
Its line appears because `main()` sleeps for 0.25 seconds afterward,
long enough for `slow` to finish.
A real caller rarely adds that wait.
The program moves on before the orphan finishes,
and an exception from the orphan is discarded without a report.
`gather(*coros, return_exceptions=True)` returns the failures as data instead,
the async form of exercise 3's catch-collect-continue.
[Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup` is the usual choice for concurrent awaits,
but not here.
A `TaskGroup` cancels a failing task's siblings,
so a single broken responder cancels the others mid-notification.

Use the async fan-out only when the responders are I/O-bound.
For in-memory responders the synchronous `Broadcaster` from `broadcaster.py` is simpler and needs no event loop.

## A Visual Example: a Model and Its View

This example emphasizes the model-view split.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule that decides what a selection changes.
It only manipulates `Grid`s and doesn't know anything about displaying them.
The *view*, `box_view.py`,
displays the boxes using the standard library's `tkinter`.
Clicking a box advances it to the next color, along with the boxes above, below,
left, and right of it.

One click changes up to five boxes, which makes the window a puzzle:
try to turn every box `palegreen`.
This is the only color that works; on the 8x8 grid `box_view.py` opens with,
no sequence of clicks turns every box `skyblue` or every box `khaki`.
The size decides that, and a 3x3 grid reaches all three colors (see exercise 9).

### The Model

The model reuses `broadcaster.Broadcaster`:

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

`Color` is a `StrEnum`,
an [`Enum`](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too)
whose members are also strings.
`Color.KHAKI` compares equal to `"khaki"` and works anywhere a `str` does,
so the view can pass a `Color` to `tkinter` as a color name.
`list(Color)` is the cycle of colors,
because iterating over an enum produces its members in definition order.
`next()` finds the member's position in that list with `index()` and adds one.
`nxt` is the position of the next color,
and `nxt % len(colors)` wraps it around,
so `Color.KHAKI.next()` is `Color.SKYBLUE`.

A `Grid` maps each `(column, row)` coordinate to a `Color`.
`new_grid()` builds a square grid, `size` cells on a side,
banded into three colors.
A cell's color is `colors[(x + y) % len(colors)]`,
so the cells along a diagonal, where `x + y` is constant, share one color.

`recolored()` computes the grid that results from selecting a cell: values in,
values out.
`cross` holds the selected cell and the four cells that share an edge with it.
A cell on the border has fewer neighbors,
so some of the coordinates in `cross` lie outside the grid.
A `Grid` is keyed by coordinate,
so `cell in grid` is `True` only for a coordinate inside the grid.
The comprehension's `if` clause applies that test and skips the outside coordinates,
so `recolored()` needs no grid size.
The comprehension maps each cell that passes the test to its color's `next()`.
The [dictionary merge](03_Foundations--Containers.md#dictionaries)
builds the new grid: `|` produces a new dictionary,
and when both operands hold the same key, the right operand's value wins.
The result is a copy of `grid` that differs in the cells of the cross,
and `grid` is unchanged.

Neither function needs a `BoxModel`,
so both are defined at module level and not inside the class.
A test calls them directly, and a second model can reuse them.
`BoxModel` is a `Broadcaster[Grid]`.
Its `__init__()` calls `Broadcaster.__init__()` as `Thermometer`'s does,
then builds `grid` from `size`.
`BoxModel.select()` makes the next grid with `recolored()` and passes it to `announce()`.

### Testing the Model

The model contains no display code, so you can test it without a GUI.
Testing confirms that `recolored()` changes the cross and no other cell,
that a selection in a corner stays on the grid,
and that responders receive the new grid after a selection:

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
    # The responder is a callable
    model.subscribe(seen.append)
    model.select((1, 1))
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
```

### The View

The view is the only code that draws to the screen.
Run `box_view.py` to play.
Because it opens a window, the example harness skips it
(see `tools/data/norun.txt`).

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
        canvas.delete("all")  # Clear old rectangles
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
For each cell it paints one rectangle,
whose pixel corners come from multiplying the cell's column and row by `cell_px`.
It takes a `Grid` and returns `None`,
the shape `subscribe()` requires of a responder.
When the window opens,
`show()` calls `draw(model.grid)` once to paint the starting grid.

`draw()` clears the canvas before repainting.
Otherwise, each notification adds another `size * size` rectangles on top of the previous ones.
The window looks the same but the canvas's list of items grows without limit,
the same quiet accumulation as a *lapsed listener*.

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
`select()` takes a cell rather than a mouse event, so a keypress, a touch,
or a test call drives the model the way a click does.

The model names nothing about views,
so you can attach a second view to the same model and keep both views in step
(see exercise 8).
The dependency runs one way, and the view is the end that carries it:
`box_view.py` imports `BoxModel`, reads `size` and `grid`, and calls `select()`.

## Where the Controller Goes

The chapter opened by saying Document-View folds the controller into the view.
The next two listings isolate that fold:
both share one model and one notification,
and they differ only in where the input handling lives.
The model is a counter, and both versions import this one file:

```python
# counter_model.py
from broadcaster import Broadcaster

class Counter(Broadcaster[int]):
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def add(self, delta: int) -> None:
        self._count += delta
        self.announce(self._count)
```

In Document-View, one class draws and interprets input:

```python
# document_view.py
from counter_model import Counter

class View:
    def __init__(self, model: Counter) -> None:
        self._model = model

    def draw(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:
        if char == "+":
            self._model.add(1)
        elif char == "-":
            self._model.add(-1)

model = Counter()
view = View(model)
model.subscribe(view.draw)
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
```

`draw()` is the output and `key()` is the input,
and `View` holds the model because `key()` needs somewhere to send the request.
`x` falls through both branches, so `key()` returns without touching the model,
and four keystrokes print three counts.

MVC splits that class in two:

```python
# model_view_controller.py
from typing import Protocol
from counter_model import Counter

class Keys(Protocol):
    def key(self, char: str) -> None: ...

class View:  # Draws, and holds no model
    def draw(self, count: int) -> None:
        print(f"count: {count}")

class StepKeys:  # Interprets, and holds the model
    def __init__(self, model: Counter) -> None:
        self._model = model

    def key(self, char: str) -> None:
        if char == "+":
            self._model.add(1)
        elif char == "-":
            self._model.add(-1)

class NoKeys:  # Reads input and changes nothing
    def key(self, char: str) -> None: ...

model = Counter()
view = View()
model.subscribe(view.draw)
control: Keys = StepKeys(model)
for char in "++-x":
    control.key(char)
#: count: 1
#: count: 2
#: count: 1
control = NoKeys()  # View and model untouched
for char in "+++":
    control.key(char)
print(model.count)
#: 1
```

Three things are the same in the two versions.
The model file, imported by both.
The line that connects the model to the view, `model.subscribe(view.draw)`.
And the printed output for the same four keystrokes.
*Observer* does the same work either way,
which is why the chapter's opening calls the two architectures nearly equivalent.

One thing moves.
`key()` leaves `View` and becomes `StepKeys`,
and the model reference goes with it.
The MVC `View` holds nothing and defines one method.
Document-View's `View` does two jobs, and each MVC class does one.

The last four lines show what that move gives you.
`NoKeys` satisfies `Keys` and ignores every key,
so assigning it to `control` switches the input off and leaves `View` unchanged,
the example *GoF Design Patterns* gives for the separation.
`StepKeys` also runs with no view attached,
so a test can call `key()` and read `model.count` without drawing anything.
Supporting a different set of keys means writing a third class that satisfies `Keys`,
with `View` and the model unchanged.

The separation keeps the model-to-view coupling as it is:
both versions call `model.subscribe(view.draw)`.
It separates drawing from input handling,
two jobs that share one class in `document_view.py`.
`box_view.py` is the Document-View version as a working GUI: `draw()` paints,
the `bind()` lambda interprets the click, and both sit inside `show()`.

## What Stays Constant

*Observer* serves four scenarios in this chapter:
a thermometer whose responders print a reading,
the same thermometer whose coroutine responders run concurrently,
a grid model whose responder repaints a canvas,
and a counter wired as Document-View and as MVC.
In every case the responder is a callable,
and the broadcaster holds responders and calls each one when its state changes.
The pattern requires no interface, no `update()` method,
and no class per reaction.

## Deciding What Matters

`Thermometer` measures, decides which changes to announce,
and tells the responders.
[Cohesion](21_Patterns--Design_Patterns.md#design-principles)
means one job per class, and that is three.
Of the two added jobs, telling the responders can move out of the class.
`Broadcaster` keeps the responder list and the notification loop in a base class,
and `watched.py` drops the base class and calls its watchers from `__setattr__()`,
so one method covers every attribute.
The job still belongs to the object either way, and its code lives elsewhere.

The other added job is deciding which changes to announce.
That decision belongs to the object whose state changes, or to whoever calls it.
It never belongs to a responder,
whose choice is limited to filtering the changes it receives.
`Thermometer`'s setter announces every assignment,
which says that every change matters to everyone.
[Leaving that call to the client](#push-or-pull)
instead lets several changes coalesce into one announcement,
but a caller who forgets the call leaves every responder out of date.
Push sends the value, so the thermometer decides what each responder receives.
Pull sends the thermometer,
so each responder reads the attribute it names and depends on that interface.
`watched.py` leaves the choice to its watchers: two states,
`celsius` and `humidity`, share one channel,
so every watcher receives both kinds of change and filters by the name it is handed.

*Observer* therefore removes one coupling and keeps another.
The object that changes knows its responders only as callables,
yet it still decides what they hear.
A threshold makes that concrete.
This thermometer announces a reading only when it differs from the reading before it by at least `_delta`:

```python
# threshold.py
from broadcaster import Broadcaster

class ThresholdThermometer(Broadcaster[float]):
    def __init__(
        self, celsius: float, delta: float
    ) -> None:
        super().__init__()
        self._celsius = celsius
        self._delta = delta

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        change = abs(value - self._celsius)
        self._celsius = value
        if change >= self._delta:
            self.announce(value)

def display(celsius: float) -> None:
    print(f"display: {celsius}C")

log: list[float] = []
t = ThresholdThermometer(20.0, 0.5)
t.subscribe(log.append)
t.subscribe(display)
for reading in [20.2, 20.9, 21.0, 22.0]:
    t.celsius = reading
#: display: 20.9C
#: display: 22.0C
print(log)
#: [20.9, 22.0]
```

`_delta` is the thermometer's field and its responders' business.
Half a degree is a judgment about what a display needs,
and `display` prints whatever it receives.
It is the wrong judgment for `log`, which exists to record every reading,
and the thermometer announces only two of the four readings.
`log` loses the other two for good,
and nothing in `ThresholdThermometer` says which responder the half degree serves.
[`reentrant_announce_fixed.py`](#re-entrant-notification)
makes a smaller version of the same decision:
its setter returns early when the new value equals the current reading,
so a responder that counts readings rather than changes misses that repeated reading.

Move the comparison into the responders and the number sits where the need is.
`display` then remembers the last value it drew and skips a reading close to it,
`log` appends whatever arrives, and the setter announces every assignment again.
The thermometer knows nothing about tolerance,
and each responder that filters by size repeats the same comparison.
`async_thermometer_demo.py`'s `alarm` already works this way,
returning at once for a reading below 100 degrees.

Repeating the comparison in each responder suits a question about *how much*,
because each responder sets its own threshold.
*Which kind* is a different question, and repetition handles it poorly,
because every kind of change arrives on one channel and each responder sorts them itself.
`watched.py` shows that repetition,
with every watcher taking the attribute name and filtering it.
[Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
removes it: one list becomes a dictionary of lists keyed by event type,
so an announcement carries the kind of thing that happened and each handler subscribes to the kind it cares about.
The publisher then decides which event it is publishing, something it knows,
instead of guessing which responders need it.

## Exercises

1.  Create a minimal *Observer* design of your own,
    without looking at `broadcaster.py`:
    the smallest `Broadcaster` that lets callables subscribe,
    then notifies them.
    Demonstrate it by subscribing several responders and causing one change that updates them all.
2.  Rewrite the classic listings to use the pull model:
    `Display.update()` reads `subject.celsius` instead of `arg`.
    A `Display` that narrows its `subject` parameter to `Thermometer` no longer satisfies `Observer[float]`,
    so make it type-check two ways:
    once with a runtime `isinstance()` check inside `update()`,
    and once with an `Observer[S, T]` protocol whose first parameter is the subject type,
    which `Subject` supplies as `Self`.
    Say what each version adds.
3.  Make `Broadcaster.announce()` survive a responder that raises an exception:
    every other responder is still notified,
    and `announce()` re-raises the failures afterward, together,
    as an [`ExceptionGroup`](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
    (which you build yourself here: `raise ExceptionGroup("message", failures)`).
    Write a test in which the first responder raises an exception and the second still records its notification.
4.  Redo exercise 3 for `async_broadcaster.py`.
    Make `announce()` use `gather(*coros, return_exceptions=True)`,
    separate the returned exceptions from the successes,
    and raise them together as an `ExceptionGroup`.
    Write a test in which the first responder raises an exception and the second still records its notification.
5.  Redo exercise 3 with each failure returned as a value instead of raised as an exception.
    Each responder returns a [`Result`](42_Functional--Error_Handling.md#a-result-type)
    from `utils/result.py`,
    and `announce()` returns the `Err` values it collects.
    Write an adapter that lets a responder returning `None`,
    such as `received.append`, subscribe.
    Write a test in which the first responder fails and the second still records its notification.
6.  Turn `box_observer.py` into a simple game:
    you own the contiguous patch of same-colored squares containing the top-left corner,
    and selecting any square recolors your patch to that square's color,
    absorbing neighbors that now match.
    Write the neighbor test yourself, and count diagonal squares as neighbors.
    Track the moves it takes to make the whole field one color.
    For competition, alternate turns between players.
7.  Change the rule for a selection in `box_observer.py`:
    make `recolored()` advance every box in the selected box's row and column.
    Run `box_view.py` without editing it,
    and explain why the view needed no change.
8.  Attach a second view to `box_observer.py`'s `BoxModel`.
    Write one view that prints a letter per cell and another that prints how many cells each color holds,
    subscribe both to the same model,
    and show that one `select()` updates the pair.
    Keep both views textual so the example runs without a window,
    and leave the model as `box_observer.py` has it.
9.  Work out which colors the whole grid can reach from `new_grid(size)` under `box_observer.py`'s rule.
    Selecting a cell advances up to five cells by one, modulo three,
    and selections commute, so this is a linear system over the integers mod 3:
    the unknowns are how many times you select each cell.
    Write Gaussian elimination mod 3 to decide whether the system has a solution,
    and print the reachable colors for every size from 3 through 8.
    The 8x8 grid reaches `palegreen` alone,
    and one smaller size reaches nothing.
10. Write a `Notifying` [descriptor](17_Techniques--Metaprogramming.md#a-descriptor-that-validates)
    that replaces the `@property` and `announce()` pair,
    so one class declares several independently watched attributes:
    `celsius = Notifying[float]()` beside `humidity = Notifying[float]()`.
    Each attribute keeps its own responders.
    Subscribing needs the descriptor, not the value it stores,
    so `__get__()` returns the descriptor for an access through the class,
    and `Thermometer.celsius.subscribe(t, readings.append)` reaches it.
    Show that an assignment to one attribute calls no responder of the other.
