# Observer

> Something changes, and something else is interested in that change.
> The *Observer* pattern connects the two.

*Observer* decouples code that changes state from code that reacts to that state change.
An *observer* attaches to a *subject*.
When the subject changes state, it notifies the observer.
The subject knows each observer only as something to call,
and it decides which arguments every call receives.
This is [designing the communication rather than the parts](21_Patterns--Design_Patterns.md#design-principles).

Use *Observer* if a group of objects must update themselves based on a state change.
Event handling typically uses *Observer*.
A widget (like a button)
keeps a list of handlers and calls each one when its event (a button press)
arrives.

In its common form, where observers attach and detach at runtime,
*Observer* is the most dynamic of the callback patterns.
[Setting the Responders at Construction](#setting-the-responders-at-construction)
shows a form that keeps the decoupling and connects the observers once,
when you create the subject.

The classic example is Smalltalk's *Model-View-Controller* (MVC),
or the nearly-equivalent *Document-View* architecture,
which folds the controller into the view.
In both, *Observer* connects the state change to its views.
One subject keeps a list of views and accepts any view that has the update method it calls.
This way, a *document* can have more than one way to view it,
such as a plot and a table.
With *Observer*, a change in the subject's data notifies each interested view,
so that every view refreshes.

## The Classic Observer

The classic design comes from *GoF Design Patterns*:

- The object that changes is the *subject*.
- Each *observer* implements an interface with one method.

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

`Thermometer`'s `celsius` setter stores the new reading and calls `notify()`.
Because a setter runs on every assignment to its attribute,
every assignment to `celsius` reaches the observers:

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

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
        self.notify(value)
```

Because `Subject` creates the observer list in its constructor,
`Thermometer`'s constructor must call [`super().__init__()`](07_Foundations--Classes.md#calling-the-base-constructor).
Without that call, a `Thermometer` has no `_observers` attribute.

The `Display` observer prints each new reading:

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
t.celsius = 25
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
Each observer depends on the subject's interface.
To read `celsius`, an observer must know it is watching a `Thermometer`.
The type checker enforces that dependency.
`Subject[float]` has no `celsius`,
so the observer must declare its `subject` parameter as a `Thermometer`.
To use pull, you must add either a runtime `isinstance()` check or a second type parameter on the protocol.

GoF also leaves open a second choice, independent of push or pull:
which code calls `notify()`.
In `Thermometer`, the `celsius` setter calls it,
so each assignment notifies the observers immediately.
Three assignments in a row produce three notifications.
The alternative leaves the call to the client,
the code that changes the subject.
The client makes all its changes and then calls `notify()` once,
so the observers receive one notification for the whole batch.
In exchange, every client must make that call.
Until it does, the observers hold stale data.

### Why `notify()` Copies the List

Inside `notify()`, copying `_observers` via `list(self._observers)` appears redundant.
It is not.

The problem is that an observer may react to a notification by detaching.
If the `for` loop in `notify()` reads `self._observers` instead of a copy,
a `detach()` shifts the remaining observers down one index,
and the loop skips the observer after the one that detached,
without raising an exception.
With the copy, `detach()` changes `self._observers` while the loop reads the copied list.
A `notify()` call therefore reaches every observer in `_observers` at the moment the call begins.
If `detach()` removes an observer from `_observers` partway through a `notify()` call,
the copy still holds that observer,
so the observer receives the call's notification.
Attaching an observer during the call does not attach to the copy,
so the new observer isn't part of the `notify()` on the copy.
[Disconnecting During a Notification](#disconnecting-during-a-notification)
runs a responder that disconnects itself,
and shows index by index which responder the loop skips without the copy.

## Easier Names

The traditional names are hard to hold in your head.
Both `java.util.Observable` and the reactive libraries call the subject an `Observable`.
`Observer` and `Observable` share a stem and name opposite roles,
so every listing asks you to decode which end you are looking at.
GoF's method names are a second obstacle.
When the subject changes, it calls its own `notify()`,
and `notify()` calls `update()` on each observer.
Those two names describe one change from its two ends.
`notify()` is the subject sending a change,
and `update()` is an observer receiving that change.
Nothing in the two words pairs them,
so you must remember that `update()` is the receiving end of `notify()`.
The word "update" also fits the subject better than the observer.
`Thermometer`'s setter updates the reading,
while `Display.update()` only prints it.
The rest of this chapter uses names you can tell apart at a glance:

| *GoF Design Patterns* | This chapter |
|---|---|
| subject | `Broadcaster` |
| observer | responder == any callable |
| `attach()` / `detach()` | `connect()` / `disconnect()` |
| `notify()` | `announce()` |
| `update()` | calling the responder |

The last row has no method name on the right.
A responder is a callable, so the receiving end needs no specially-named method.
Sending a change and receiving it share one name, `announce()`,
where GoF has two.

GoF calls the pattern *Observer*,
and Java and the reactive libraries use the older nouns.
The table is your map into that literature.
Java and JavaScript call a responder a *listener*,
as in `ActionListener` and `addEventListener()`.

The essential part of *Observer* is the response: something changes,
and code elsewhere runs because of that change.
The words "observer" and "listener" name a role that waits and watches,
and neither word says what happens when the change arrives.
"Responder" names the action.
That word points you at the question every *Observer* design must answer:
what does this code do when there's a change?
A responder can disconnect itself mid-notification, raise an exception,
wait on a slow network call, or write back to its broadcaster,
and each of those behaviors changes how the broadcaster is written.

## The Pythonic Observer

A responder is any callable that takes a notification and returns `None`.
A broadcaster keeps a list of those callables and announces a change to every responder:

```python
# broadcaster.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    def disconnect(self, responder: Responder[T]) -> None:
        self._responders.remove(responder)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
```

`Broadcaster` is `classic_observer.py`'s `Subject` with its three methods renamed:
GoF's `attach()`, `detach()`, and `notify()` become `connect()`, `disconnect()`,
and `announce()`.
The call inside the loop changes as well.
`Broadcaster.announce()` calls `responder(data)`,
so a function serves as a responder.
`announce()` passes the data alone, so `Broadcaster` uses the push model.

`Broadcaster` knows nothing about what it announces.
Its type parameter `T` sets the type of each notification,
and a class that inherits `Broadcaster` gets `connect()`, `disconnect()`,
and `announce()`.

A responder returns `None`, as seen in the `Responder` `type` alias.
At runtime, `announce()` discards whatever a responder returns,
since it calls each responder as a statement.
The alias turns that silent discard into a type error.
The type checker rejects a responder that returns a value,
because the author of that responder likely expected someone to use the value.
The alternative alias `Callable[[T], object]` accepts any callable that takes a `T`,
since every return type, `None` included, is assignable to `object`.
That alternative trades correctness for convenience.
If a responder returns a value, `announce()` quietly drops it.
The strict version of `Responder` returning `None` catches that mistake.
Notification runs one way, from broadcaster to responders.
*GoF Design Patterns* supplies the premise under broadcast communication:
a notification goes to every connected responder,
and each one decides whether to handle it.
Allowing return values produces different values from an unknown number of responders.
The broadcaster would require a rule for combining those different values.
Returning `None` removes that question.

A design that needs an answer uses a different pattern.
For example, [*Chain of Responsibility*](28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime)
tries its handlers in turn and returns the result from the first one that succeeds.

The new `Thermometer` changes only its base class and the call in its `celsius` setter,
`announce()` in place of `notify()`:

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

The setter first stores the new reading, which is the state change.
Then it calls `announce()`,
which is what the thermometer chooses to do about that change.
In this case, the setter announces every assignment.
[Deciding What Matters](#deciding-what-matters)
shows a setter that announces a reading only when it differs enough from the previous reading.

The constructor assigns its argument to `_celsius` directly,
bypassing the setter.
The first reading is the thermometer's starting state, not a change to it.
No responder can connect before the constructor returns,
so there is no one to tell.
A responder that needs the current reading when it connects reads `celsius`.

`Thermometer`'s constructor is simple and suggests using a `dataclass`.
A class that inherits from another can be a `dataclass`,
but [a `dataclass`-generated `__init__()` does not call the base class's `__init__()`](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance).
A `@dataclass` `Thermometer` would have no list of responders.
A `__post_init__()` that calls `super().__init__()` fixes that,
but at greater length and complexity than the `__init__()` it replaces.
[Decorated Responders](#decorated-responders)
gets a generated `__init__()` and the list another way.

`Thermometer` inherits `Broadcaster` because that is the shortest way to get `connect()` and `announce()`,
not because the pattern requires a base class.
A `Thermometer` could use composition, holding a `Broadcaster` as an attribute
(`self.temperature_changed = Broadcaster[float]()`).
Code that connects a responder would name that attribute
(`t.temperature_changed.connect(display)`).
An object can hold multiple attributes,
so it can publish more than one kind of change.
[Notifying Without a Base Class](#notifying-without-a-base-class)
drops the base class and the properties together.
Event-heavy programs have mature libraries (signal/slot systems),
but for most cases the *Observer* pattern is only a list of responders.

Connected callables react to every `celsius` assignment:

```python
# thermometer_demo.py
from thermometer import Thermometer

t = Thermometer(20.0)
t.connect(lambda c: print(f"display: {c}C"))
t.connect(lambda c: print("alarm!" if c > 100 else "ok"))
t.celsius = 25
#: display: 25C
#: ok
t.celsius = 150
#: display: 150C
#: alarm!
```

The responders here are lambdas, but any function or bound method works.
`Thermometer` knows its responders only as callables that take a `float`.
This figure shows one notification,
naming the two lambdas `display` and `alarm`:

![](_images/observer_story)

The shaded side holds the responders as the program wrote them;
`Thermometer` keeps each one as a callable in its list.
Two kinds of arrow cross the boundary, in opposite directions:
`connect()` carries a responder into the list,
and `announce()` calls each stored responder in turn.
No result crosses back, so `Thermometer` has nothing to wait for or interpret.
A new responder such as `plot` connects the same way as all responders.

### Testing the Broadcaster

The test file confirms that:

- Every responder receives the announced value in connection order.
- Announcing to an empty list succeeds.
- Delivery stops after `disconnect()`.
- A callable connected twice receives each announcement twice,
  and one `disconnect()` removes one of the two.
- A `disconnect()` matching no connection raises a `ValueError`.
- `Thermometer`'s setter stores each reading and announces it.
- A responder receives only the changes made after it connects.

```python
# test_broadcaster.py
import pytest
from broadcaster import Broadcaster
from thermometer import Thermometer

def test_announce_calls_every_responder() -> None:
    received: list[tuple[str, object]] = []
    broadcaster = Broadcaster[int]()
    broadcaster.connect(
        lambda d: received.append(("a", d)))
    broadcaster.connect(
        lambda d: received.append(("b", d)))
    broadcaster.announce(42)
    assert received == [("a", 42), ("b", 42)]

def test_no_responders_is_a_noop() -> None:
    # Must not raise anything
    Broadcaster[str]().announce("anything")

def test_disconnect_stops_delivery() -> None:
    received: list[object] = []
    broadcaster = Broadcaster[object]()
    broadcaster.connect(received.append)
    broadcaster.announce(1)
    assert received.append == received.append
    assert received.append is not received.append
    broadcaster.disconnect(received.append)
    broadcaster.announce(2)
    assert received == [1]

def test_connecting_twice_notifies_twice() -> None:
    received: list[object] = []
    broadcaster = Broadcaster[object]()
    broadcaster.connect(received.append)
    broadcaster.connect(received.append)
    broadcaster.announce(1)
    assert received == [1, 1]
    broadcaster.disconnect(received.append)  # One of two
    broadcaster.announce(2)
    assert received == [1, 1, 2]

def test_disconnect_without_connect_raises() -> None:
    broadcaster = Broadcaster[object]()
    with pytest.raises(ValueError):
        broadcaster.disconnect(print)

def test_thermometer_announces_each_assignment() -> None:
    readings: list[float] = []
    t = Thermometer(20.0)
    t.connect(readings.append)
    t.celsius = 25.0
    t.celsius = 150.0
    assert readings == [25.0, 150.0]
    assert t.celsius == 150.0

def test_late_responder_misses_earlier_changes() -> None:
    readings: list[float] = []
    t = Thermometer(0.0)
    t.celsius = 10.0  # No responder yet
    t.connect(readings.append)
    t.celsius = 20.0
    assert readings == [20.0]
```

The tests connect a list's `append` to the broadcaster,
so the list records every announced value.

`disconnect()` matches by equality, and a lambda equals only itself.
That is, you cannot disconnect a lambda using a second lambda with the same text.
Disconnecting a lambda requires an intermediate name bound to the lambda,
so you can use that name to both `connect()` and `disconnect()`.

A bound method is different.
`test_disconnect_stops_delivery()` disconnects `received.append` without storing it first.
Each reference to `received.append` builds a new bound-method object,
so `received.append is received.append` is `False`.
Two bound methods compare equal when they wrap the same instance and the same function.
The two `assert` lines before the `disconnect()` call show both facts.
`disconnect()` relies on equality:
the bound method it receives equals the one `connect()` stored,
so it finds that entry and removes it.

`test_connecting_twice_notifies_twice()` and `test_disconnect_without_connect_raises()` follow from the `list` methods that `connect()` and `disconnect()` call:
`append()` stores a callable a second time,
and `remove()` takes out the first equal entry and raises a `ValueError` when none matches.

### Disconnecting During a Notification

The copy in `announce()` matters when a responder disconnects itself mid-notification:

```python
# self_removing_responder.py
from broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
seen: list[str] = []

def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Disconnects mid-notification
    broadcaster.disconnect(once)

def always(data: object) -> None:
    seen.append(f"always: {data}")

broadcaster.connect(once)
broadcaster.connect(always)
broadcaster.announce(1)
broadcaster.announce(2)
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` receives the first change and disconnects itself.
That call removes it from the broadcaster's list,
not from the copy that `announce()`'s loop reads,
so `once` still gets this notification but no later ones.
`always` receives both.
Without the copy, `announce()`'s `for` loop reads the list that `disconnect()` changes.
`once` is at index 0 and `always` at index 1.
Removing `once` moves `always` to index 0, which the loop has visited,
so the loop looks for index 1, finds the list ended there, and stops.
`always` misses the first change, and `seen` ends as `['once: 1', 'always: 2']`,
with no exception to say a responder was skipped.

### Raising an Exception

If a responder raises an exception, it stops the `announce()` loop.
The remaining responders in the list do not get notified.
The exception propagates to the code that assigned to `celsius`.
You must decide whether `announce()` should catch, collect, and continue
(see exercise 3).

Alternatively, the responder can catch its own exception and [return the error as a value](42_Functional--Error_Handling.md#return-the-error-as-a-value).
In this approach, `announce()` collects the returned errors for the caller.
Every responder runs, and every failure arrives as a value.
However, the `Responder` type becomes a callable that returns a success or an error,
so a method such as `readings.append()`, which returns `None`, needs a wrapper
(see exercise 5).

### Lapsed Listeners

Connections are strong references.
A bound method holds the object it came from,
so connecting `plot.redraw` keeps that `plot` in memory for as long as the broadcaster holds the connection.
When the program finishes with `plot`,
it drops its other references to the object.
A `plot.redraw` that is still connected keeps `plot` in memory,
and `redraw()` runs on every announcement.
A responder the program stops using but leaves connected creates a *lapsed listener*.
Over a long run the broadcaster accumulates lapsed listeners,
creating a memory leak.
Long-lived broadcasters need either disciplined `disconnect()` calls or [weak references](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
which do not keep the responder alive.
A weak responder holds its object through a weak reference.
On each announcement the responder passes the announcement to the object while the object is alive,
and disconnects itself after Python collects the object:

```python
# weak_responder.py
import gc
from weakref import WeakMethod
from broadcaster import Broadcaster
from exceptions import expected

class Plot:
    def redraw(self, celsius: float) -> None:
        print(f"plot: {celsius}C")

broadcaster = Broadcaster[float]()
plot = Plot()
ref = WeakMethod(plot.redraw)

def weak(celsius: float) -> None:
    live = ref()
    if live is None:
        broadcaster.disconnect(weak)  # Gone: drop out
    else:
        live(celsius)

broadcaster.connect(weak)
broadcaster.announce(25.0)
#: plot: 25.0C

del plot  # The only strong reference
gc.collect()
broadcaster.announce(30.0)  # Prints nothing

with expected(ValueError):
    broadcaster.disconnect(weak)
#: [ValueError] list.remove(x): x not in list
```

A `Broadcaster` holds a strong reference to whatever you `connect()`,
so `weak_responder.py` puts the weak reference inside the responder.
A different broadcaster could store weak references for every responder.
With `Broadcaster`, a responder that needs a weak reference supplies its own.

An ordinary `weakref.ref(plot.redraw)` is dead the moment it is created.
Its argument, `plot.redraw`, builds a new bound-method object,
and the weak reference becomes the single reference to that object.
A weak reference lets Python collect its target,
so Python collects the bound method as soon as `weakref.ref()` returns,
and that leaves the weak reference dead.
Using `WeakMethod`, you store the instance and the function separately,
both weakly, and rebuild the bound method each time you call `ref()`.

`announce(25.0)` runs while `plot` is alive,
so the weak reference still has its target.
`ref()` rebuilds the bound method `plot.redraw`, and `weak` stores it in `live`.
`live` is a strong reference,
so the `Plot` object stays alive while `live(celsius)` runs `redraw()` and prints `plot: 25.0C`.
When `weak` returns, `live` goes away,
and the responder again holds the `Plot` object through the weak reference alone.

`del plot` removes the one strong reference to the `Plot` object.
CPython's reference counting collects the object at once.
An implementation with a [tracing collector](10_Foundations--Cleanup.md#watching-objects-without-holding-them),
such as PyPy, collects the object when its collector runs,
and the `gc.collect()` call runs that collector before `announce(30.0)`.
A program that leaves the timing to the collector sees `weak` keep calling `redraw()` until the collector runs.

During `announce(30.0)`, `ref()` returns `None` and `weak` disconnects itself.
The copy that `announce()` iterates over makes a mid-notification disconnect safe,
as it does for `once` in `self_removing_responder.py`.
The listing's last statement tries to disconnect `weak` a second time.
The broadcaster's list is empty by then,
so `disconnect()` raises a `ValueError`,
the evidence that `weak` removed itself.

For most programs, strong connections are fine.
A broadcaster that lives no longer than its responders releases them when it goes away,
and an explicit `disconnect()` covers a responder that leaves early.
Use a weak responder only when a long-lived broadcaster holds short-lived responders that the program drops while they are still connected.

### Re-entrant Notification

A responder that writes back to the broadcaster re-enters `announce()` from inside `announce()`.
Two-way bindings are the usual source.
The view edits the model, the model notifies the view, the view edits the model,
and it continues until you get a `RecursionError`:

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
        # A responder that sets value re-enters this setter
        self.announce(new)

model = TwoWay()
model.connect(
    lambda v: setattr(model, "value", v))
with expected(RecursionError):
    model.value = 1
#: [RecursionError] maximum recursion depth exceeded
```

To prevent this, you need a guard.
Here, the setter returns early when the new value equals the stored one:

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

model.connect(echo)
model.value = 1
print(seen)
#: [1]
```

`echo` writes back the value,
so the setter returns before it reaches `announce()` a second time.
`announce()` runs only once, for the original assignment.

The alternative is a re-entry flag, set before `announce()` and cleared after,
with the setter returning early while the flag is set.
The flag breaks the cycle without comparing values,
so a second write of the same reading still reaches the responders,
which is the behavior you want when a responder counts readings rather than modifications.

### Setting the Responders at Construction

A program can choose its responders at any of four points:

1.  **Source time.**
    The broadcaster's code calls each responder by name,
    as a setter that calls `display.update()` and then `alarm.update()`.
    The broadcaster names every responder,
    and *Observer* replaces those names with a list of callables.
2.  **Load time.**
    Each responder registers itself with a decorator as Python imports its module.
    Django's `@receiver` decorator and `atexit.register()` work this way.
    Registration runs at runtime,
    but the set is normally complete once the imports finish (see exercise 11).
3.  **Runtime.**
    Responders connect and disconnect at any moment, as with `Broadcaster`.
4.  **Construction time.**
    The broadcaster receives its responders when you create it,
    and the set stays the same for as long as the broadcaster lives.
    The rest of this section builds that broadcaster.

`Broadcaster`'s `connect()` and `disconnect()` make it dynamic.
Its list of responders can change at any moment,
including in the middle of an `announce()`.
Three earlier sections handle a consequence of that dynamism:
the copy in `announce()` guards against a `disconnect()` call during the loop,
a lambda written inline in `connect()` cannot be disconnected,
and a lapsed listener is a connection that outlives the program's use of its responder.

Decoupling and dynamism are separate properties.
A decoupled broadcaster knows its responders only as callables.
A dynamic broadcaster lets the set of responders change after the broadcaster exists.
A broadcaster that receives its responders at construction is decoupled but not dynamic:

```python
# bound_broadcaster.py
from broadcaster import Responder
from record import record

@record
class BoundBroadcaster[T]:
    responders: tuple[Responder[T], ...]

    def announce(self, data: T) -> None:
        for responder in self.responders:
            responder(data)

log: list[float] = []
broadcaster = BoundBroadcaster[float]((
    log.append,
    lambda c: print("alarm!" if c > 100 else "ok"),
))
broadcaster.announce(25.0)
#: ok
broadcaster.announce(150.0)
#: alarm!
print(log)
#: [25.0, 150.0]
```

The `@record` freezes the field, and the tuple freezes its contents,
so the responders can't change.
`announce()` iterates through the tuple but does not need to copy it.
The broadcaster holds strong references to its responders.

### Notifying Without a Base Class

`Thermometer` writes a getter and a setter for each attribute it publishes,
and inherits `connect()` and `announce()` from `Broadcaster`.
We can simplify this using `__setattr__()`.
Python calls it for every attribute assignment,
so one `__setattr__()` covers every attribute of the class:

```python
# weather_station.py
from collections.abc import Callable

type AttrResponder = Callable[[str, object], None]

class WeatherStation:
    def __init__(
        self, celsius: float, humidity: float
    ) -> None:
        self.celsius = celsius
        self.humidity = humidity

    @property
    def _responders(self) -> list[AttrResponder]:
        return self.__dict__.setdefault("_responders", [])

    def connect(self, responder: AttrResponder) -> None:
        self._responders.append(responder)

    def disconnect(self, responder: AttrResponder) -> None:
        self._responders.remove(responder)

    def __setattr__(
        self, name: str, value: object
    ) -> None:
        responders = list(self._responders)
        super().__setattr__(name, value)
        for responder in responders:
            responder(name, value)

station = WeatherStation(20.0, 0.4)
changes: list[tuple[str, object]] = []
station.connect(lambda n, v: changes.append((n, v)))
station.celsius = 25.0
station.humidity = 0.5
print(changes)
#: [('celsius', 25.0), ('humidity', 0.5)]
```

Python routes every attribute assignment through `__setattr__()`,
including assignments within the constructor.
`__setattr__()` begins by reading `self._responders`,
so an ordinary `self._responders = []` in the constructor reaches that read before the list exists,
raising an `AttributeError`.
To prevent this, the `_responders` property creates the list upon first read,
using `setdefault()` on the instance `__dict__`.
A property takes precedence over an instance attribute of the same name,
so every later read also goes through the getter and finds the existing list.

The constructor's two assignments go through `__setattr__()`.
Each notifies an empty list,
since callers can connect responders only after the constructor returns.

In `__setattr__()`, `super().__setattr__()` does the storing,
because an ordinary assignment inside `__setattr__()` calls `__setattr__()`.

One `__setattr__()` for every attribute gives up three things that `Thermometer`'s property per attribute keeps:

1.  `WeatherStation`'s responders have a wider signature.
    Each takes the attribute name along with the value,
    and filters by name to act on one attribute.
    `Thermometer` publishes one attribute and is a `Broadcaster[float]`,
    so each responder takes the `float` reading as its one argument.
    This issue is revisited in [Deciding What Matters](#deciding-what-matters).
    A responder that sorts its own notifications means the broadcaster has left the decision to its responders.
2.  Every assignment reaches the responders, including the internal ones.
    A cached result or a hit counter broadcasts like a published attribute,
    unless the class writes it through `self.__dict__`,
    as the `_responders` property does.
3.  `__setattr__()` accepts any name,
    so the type checker stops checking assignments.
    The type checker passes `station.celcius = 25.0`,
    a misspelling of `celsius`, which quietly creates a new attribute.
    The same misspelling on a `Thermometer` produces an `unresolved-attribute` error.
    `Thermometer` defines no `__setattr__()`,
    so the type checker checks each assignment against the attributes the class declares.

### Decorated Responders

Using decorators, we can simplify and automate the attachment of responders to broadcasters:

```python
# broadcasting_thermometer.py
from broadcasting import Broadcasting

class Thermometer(Broadcasting[float]):
    celsius: float

thermometer = Thermometer(100)

@thermometer.respond
def report(celsius: float) -> None:
    print(f"report: {celsius}C")

@thermometer.respond
def alarm(celsius: float) -> None:
    print("alarm!" if celsius > 100 else "ok")

thermometer.celsius = 90
#: report: 90C
#: ok
thermometer.celsius = 150
#: report: 150C
#: alarm!
thermometer.disconnect(alarm)
thermometer.celsius = 200
#: report: 200C
```

The `respond()` decorator method appends its function to the `thermometer` list and returns the function unchanged,
so `report` stays callable by name.

To minimize application code, all common behaviors are captured in the library.
The first piece builds the property that publishes a field:

```python
# published.py
from typing import Any

def published(name: str) -> property:
    def read(self: Any) -> Any:
        return self.__dict__[name]

    def write(self: Any, value: Any) -> None:
        self.__dict__[name] = value  # [1]
        self.announce(value)  # [2]

    return property(read, write)  # [3]
```

`property` is the class behind [`@property`](07_Foundations--Classes.md#properties).
Called directly (`[3]`),
it returns a class attribute that intercepts every read and write of that name on an instance,
routing the read through `read()` and the write through `write()`
(these function names can be anything).
The `@property` form needs a method written in the class body for each attribute,
where `published()` builds the pair as nested functions, once,
for any field name.

`published()` takes a field name and builds the two functions a `property` needs.
`read()` returns the value stored under that name in the instance's `__dict__`.
`write()` stores a new value (`[1]`) and then calls `announce()` with it
(`[2]`), so every assignment to the field notifies the responders.
Nothing in this file defines `announce()`.
It is a method of `Broadcasting`, the class that will own the property,
and `published()` reaches it through `self`, which is annotated `Any`,
so the type checker accepts the call and the runtime finds the method on the instance when `write()` runs.
`value` is `Any` for the same reason:
`published()` knows the field by name alone,
and the type checker types each field from the subclass's annotation,
not from this property.
`[3]` returns the pair as a `property()`.

`Broadcasting` installs that property on each subclass and holds the responders:

```python
# broadcasting.py
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import dataclass_transform
from published import published

type Responder[T] = Callable[[T], None]

@dataclass_transform(eq_default=False)
class Broadcasting[T]:
    def __init_subclass__(cls) -> None:
        built = dataclass(eq=False)(cls)  # [1]
        for field in fields(built):  # [2]
            prop = published(field.name)  # [3]
            setattr(cls, field.name, prop)  # [4]

    @property
    def _responders(self) -> list[Responder[T]]:
        return self.__dict__.setdefault("_responders", [])

    def respond(self, fn: Responder[T]) -> Responder[T]:
        self._responders.append(fn)
        return fn

    def disconnect(self, fn: Responder[T]) -> None:
        self._responders.remove(fn)

    def announce(self, data: T) -> None:
        for responder in list(self._responders):
            responder(data)
```

`__init_subclass__()` runs once, at the moment Python creates the subclass.
After the body of `class Thermometer(Broadcasting[float]):` runs,
Python builds the class object and then calls `__init_subclass__()` on its base,
passing the new class as `cls`
([Self-Registration of Subclasses](17_Techniques--Metaprogramming.md#self-registration-of-subclasses)).
`__init_subclass__()` is implicitly a class method,
and at this point `Thermometer` has its annotation, no `__init__()`,
and no class attribute named `celsius`.

`[1]` passes the new class to `dataclass(eq=False)`.
This returns a decorator,
and applying that decorator to `cls` reads the [bare annotations](09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create)
(e.g. `celsius: float`),
and writes an `__init__()` and a `__repr__()` onto the class.
That `__init__()` has one parameter per field,
so `Thermometer`'s is `__init__(self, celsius: float)`,
and its body assigns `self.celsius = celsius`.
`eq=False` keeps identity equality and also leaves the instances hashable.
`dataclass()` modifies the class in place and returns it,
and `[1]` binds that result to `built`.

`[2]` asks `fields()` for the dataclass fields, one `Field` per annotation,
each carrying its name.
It passes `built` rather than `cls` to satisfy the type checker,
which still sees `cls` as the class the `class` statement declared and rejects `fields(cls)`.

`[3]` builds the property for the field's name,
and `[4]` installs it on the class under that name,
so `Thermometer.celsius` is now a property.
Python looks up a data descriptor on the class before it looks in the instance `__dict__`,
so every `thermometer.celsius` read or write reaches the property,
which reads or writes the `__dict__` entry of the same name behind it.
The generated `__init__()` captures any default the field declares at `[1]`,
so replacing the class attribute at `[4]` changes nothing about construction.
Now the subclass behaves as if its author had written `thermometer.py`'s constructor and property pair.

`@dataclass_transform` on the base class is the type checker's side of `[1]`
([`@dataclass_transform` Is a Claim](17_Techniques--Metaprogramming.md#dataclass-transform)).
It tells the checker that every subclass is dataclass-like,
so the checker synthesizes the same `__init__(self, celsius: float)` that `dataclass()` builds at runtime,
and accepts `Thermometer(100)` because `100` fits that parameter.
`eq_default=False` makes the checker's claim match the runtime `eq=False`.

`Broadcasting` has one type parameter, so a subclass publishes one value.
A class that declares `celsius` and `humidity` would send both readings to the same responders with no name attached.
A class with several published attributes uses `WeatherStation`'s name-and-value signature
(exercise 12), or gives each attribute its own responders with the descriptor in exercise 10.

## Observer and I/O

All the examples so far assume that every responder finishes at once.
Each prints, appends, or writes back, then returns.
`announce()` calls the responders one at a time, in connection order,
so a responder that calls a network service or writes to a database makes the responders connected after it wait for that call to finish,
and the setter that announced the change waits for all of them.

An asynchronous `Broadcaster` removes the wait between responders.
Its responders are coroutines,
and its `announce()` awaits them together with `asyncio.gather()`,
so one state change notifies every responder concurrently,
and each finishes on its own schedule.
`gather()` waits for all of them,
so `announce()` returns only after every responder finishes.

[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
covers the mechanics (`async def`, `await`, `gather()`, `run()`)
the `asyncio` `Broadcaster` uses:

```python
# async_broadcaster.py
import asyncio
from collections.abc import Awaitable, Callable

type AsyncResponder[T] = Callable[[T], Awaitable[None]]

class Broadcaster[T]:
    def __init__(self) -> None:
        self._responders: list[AsyncResponder[T]] = []

    def connect(
        self, responder: AsyncResponder[T]
    ) -> None:
        self._responders.append(responder)

    def disconnect(
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
`_responders` is a list assigned in the constructor, as in `broadcaster.py`.
The `_responders` property in `weather_station.py` and `broadcasting.py` exists because their `__setattr__()` reads the list before the constructor assigns it,
and this class has no `__setattr__()`.

The `AsyncResponder` `type` alias makes the type checker reject a plain function as a responder.
A responder must return an awaitable,
and calling an `async` function produces one.
The type checker also rejects the reverse mistake,
an `async` function connected to the synchronous `Broadcaster`.

An `announce()` that awaits is a coroutine,
and its caller must `await` it in turn,
so the setter that calls it must also be `async`.
The asynchronous `Thermometer` changes `celsius` with an awaitable method,
`set_celsius()`, rather than an assignment `t.celsius = value`:

```python
# async_thermometer.py
from async_broadcaster import Broadcaster

class Thermometer(Broadcaster[float]):
    def __init__(self, celsius: float) -> None:
        super().__init__()
        self._celsius = celsius

    async def set_celsius(self, value: float) -> None:
        # A property setter cannot be awaited
        self._celsius = value
        await self.announce(value)
```

The demo's responders are coroutines:

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
    t.connect(alarm)
    t.connect(log_reading)
    await t.set_celsius(20)  # Below the alarm threshold
    await t.set_celsius(150)  # Triggers the alarm too

asyncio.run(main())
#: logged: 20C
#: logged: 150C
#: alarm sent: 150C
```

`alarm` is connected before `log_reading`,
yet at 150 degrees the log prints first.
Awaiting the responders in sequence prints in connection order, alarm first.
Concurrent fan-out lets each responder finish as soon as its own wait ends,
so the faster responder prints first.
The results `gather()` returns stay in argument order;
only the side effects interleave.

A responder chooses which notifications to act on.
Below its threshold, the alarm returns at once.

### Disconnecting During an Async Notification

The async `announce()` needs no `list()` copy.
The `*` unpacks the generator into a tuple of coroutines before `gather()` runs,
so a `disconnect()` call during the fan-out cannot skip a responder.
The tuple also means a responder that disconnects itself mid-notification still receives this change,
an async counterpart to `self_removing_responder.py`:

```python
# async_self_removing_responder.py
import asyncio
from async_broadcaster import Broadcaster

broadcaster = Broadcaster[object]()
seen: list[str] = []

async def once(data: object) -> None:
    seen.append(f"once: {data}")
    # Disconnects mid-notification
    broadcaster.disconnect(once)

async def always(data: object) -> None:
    seen.append(f"always: {data}")

async def main() -> None:
    broadcaster.connect(once)
    broadcaster.connect(always)
    await broadcaster.announce(1)
    await broadcaster.announce(2)

asyncio.run(main())
print(seen)
#: ['once: 1', 'always: 1', 'always: 2']
```

`once` disconnects itself while `gather()` is running it,
and `always` still receives the change,
because `gather()` held both coroutines before either ran.
`announce(2)` builds its tuple from the shortened list,
so only `always` receives the second change.

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
`gather(*coros, return_exceptions=True)` returns the failures as data,
the async form of exercise 3's catch-collect-continue.
[Concurrency](19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup` is the usual choice for concurrent awaits,
but not here.
A `TaskGroup` cancels a failing task's siblings,
so a single broken responder cancels the others mid-notification.

Use the async fan-out only when the responders are I/O-bound.
For in-memory responders the synchronous `Broadcaster` from `broadcaster.py` is simpler and needs no event loop.

## A Visual Example

This example emphasizes the model-view split.
The *model*, `box_observer.py`,
is a grid of colored boxes and the rule that decides what a selection changes.
It manipulates `Grid`s and leaves displaying them to the view.
The *view*, `box_view.py`,
displays the boxes using the standard library's `tkinter`.
Clicking a box advances it to the next color, along with the boxes above, below,
left, and right of it.

One click changes up to five boxes, which makes the window a puzzle:
try to turn every box `palegreen`.
Only `palegreen` works; on the 8x8 grid that `box_view.py` opens,
no sequence of clicks turns every box `skyblue` or every box `khaki`.
The size decides that, and a 3x3 grid reaches all three colors (see exercise 9).

### The Model

The model knows nothing about how it is displayed:

```python
# box_observer.py
from enum import StrEnum
from broadcaster import Broadcaster

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

type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): Color.at(x + y)
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
`Color.at(n)` counts `n` places around that cycle,
and `n % len(members)` wraps a count past the last member back to the start.
`at()` is a classmethod because it works on the whole set rather than a single member.
(A class attribute holding the list is not an option, because an ordinary assignment in an `Enum` body creates another member.)
Calling `next()` on a member finds that member's position with `index()`,
then asks `at()` for the position after it,
so `Color.KHAKI.next()` is `Color.SKYBLUE`.

A `Grid` maps each `(column, row)` coordinate to a `Color`.
`new_grid()` builds a square grid, `size` cells on a side,
banded into three colors.
A cell's color is `Color.at(x + y)`, so the cells along a diagonal,
where `x + y` is constant, share one color.

`recolored()` computes the grid that results from selecting a cell.
`cross` holds the selected cell and the four cells that share an edge with it.
A cell on the border has fewer neighbors,
so some of the coordinates in its `cross` lie outside the grid.
Because a `Grid` is keyed by coordinate,
`cell in grid` is `True` only for a coordinate inside the grid.
The comprehension's `if` clause applies that test and skips any outside coordinates,
so `recolored()` needs no grid size.
The comprehension maps each cell that passes the test to its color's `next()`.
The [dictionary merge](03_Foundations--Containers.md#dictionaries)
builds the new grid.
`|` produces a new dictionary holding the keys of both operands.
Every key on the right is also in `grid`, and for a key in both,
the result takes the right operand's value.
The new grid is a copy of `grid` that differs in the cells of the cross.

`BoxModel` is a `Broadcaster[Grid]`,
and `select()` announces each new grid that `recolored()` produces.

### Testing the Model

The model is testable without a GUI.
The test file confirms that:

- `new_grid()` builds a grid of the requested size,
  starting from `skyblue` at `(0, 0)`,
  and cells with the same `x + y` share a color.
- `Color.next()` steps to the next color and wraps from the last back to the first.
- `recolored()` changes the cross and no other cell, and returns a new grid.
- A selection in a corner stays on the grid.
- Responders receive the new grid once after a selection.

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

def test_next_steps_and_wraps() -> None:
    assert Color.SKYBLUE.next() == Color.PALEGREEN
    assert Color.KHAKI.next() == Color.SKYBLUE

def test_recolored_changes_the_cross() -> None:
    grid = new_grid(3)
    out = recolored(grid, (1, 1))
    cross = {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}
    assert all(out[c] == grid[c].next() for c in cross)
    assert all(out[c] == grid[c]
               for c in grid if c not in cross)
    assert out is not grid
    assert grid == new_grid(3)

def test_corner_selection_stays_on_the_grid() -> None:
    grid = new_grid(3)
    out = recolored(grid, (0, 0))
    changed = {c for c in grid if out[c] != grid[c]}
    assert changed == {(0, 0), (1, 0), (0, 1)}
    assert out.keys() == grid.keys()

def test_responders_receive_the_new_grid() -> None:
    model = BoxModel(3)
    before = model.grid[(1, 1)]
    seen: list[Grid] = []
    model.connect(seen.append)
    model.select((1, 1))
    assert len(seen) == 1
    assert seen[-1] is model.grid
    assert model.grid[(1, 1)] != before
```

### The View

The view is the only code that displays on the screen.
Run `tip box_view` to play.
Because `box_view.py` opens a window, the example harness skips it
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

    model.connect(draw)  # Repaint on every model change
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
`draw()` paints the grid, and the view connects `draw()` to the model,
so every change repaints.
`draw()` is defined inside `show()`,
so it is a [closure](40_Functional--Foundations.md#closures)
that reads `canvas` and `cell_px`.
For each cell it paints one rectangle,
whose pixel corners come from multiplying the cell's column and row by `cell_px`.
It takes a `Grid` and returns `None`,
the shape `connect()` requires of a responder.
When the window opens,
`show()` calls `draw(model.grid)` once to paint the starting grid.

`draw()` starts with `canvas.delete("all")`,
which clears the canvas before repainting.
Otherwise, each notification adds another `size * size` rectangles on top of the previous ones.
The window looks the same but the canvas's list of items grows without limit,
the same quiet accumulation as a [lapsed listener](#lapsed-listeners).

`canvas.bind()` registers the lambda as the responder for `"<Button-1>"`,
a press of the left mouse button.
When you press the left button over the canvas,
`tkinter` calls the responder with an event `e`.
`e.x` and `e.y` give the click's position in pixels,
measured from the canvas's top-left corner.
Floor division by `cell_px` converts that position to a cell.
With 60-pixel cells, a click at `e.x == 130` is in column `130 // 60`,
which is `2`.
A click on the canvas becomes a `select()` on the model,
and the resulting notification repaints the view.
The responder calls the model, and `draw()`, run by that notification,
does all the painting.
So the view handles the mouse as well as the screen,
folding the controller's job into the view.
`select()` takes a cell rather than a mouse event, so a keypress, a touch,
or a test call drives the model the way a click does.

The model reaches a view only through the responders it calls,
so you can connect a second view to the same model and keep both views in step
(see exercise 8).
Only the view uses the model's names: `box_view.py` imports `BoxModel`,
reads `size` and `grid`, and calls `select()`.

## Where the Controller Goes

This chapter opened by saying Document-View folds the controller into the view.
The next two listings isolate that fold:
both share one model and one notification,
and they differ only in where the input handling lives.
The model is a counter:

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
from record import record

@record
class View:
    model: Counter

    def draw(self, count: int) -> None:
        print(f"count: {count}")

    def key(self, char: str) -> None:
        if char == "+":
            self.model.add(1)
        elif char == "-":
            self.model.add(-1)

model = Counter()
view = View(model)
model.connect(view.draw)
for char in "++-x":
    view.key(char)
#: count: 1
#: count: 2
#: count: 1
```

`draw()` is the output and `key()` is the input,
and `View` holds the model because `key()` needs somewhere to send the request.
`draw()` uses the count the model pushes to it, so only `key()` needs `model`.
`x` falls through both branches, so `key()` returns without touching the model,
and the four characters of `"++-x"` print three counts.

MVC splits that class in two:

```python
# model_view_controller.py
from typing import Protocol
from counter_model import Counter
from record import record

class Keys(Protocol):
    def key(self, char: str) -> None: ...

class View:  # Draws, and holds no model
    def draw(self, count: int) -> None:
        print(f"count: {count}")

@record
class StepKeys:  # Interprets, and holds the model
    model: Counter

    def key(self, char: str) -> None:
        if char == "+":
            self.model.add(1)
        elif char == "-":
            self.model.add(-1)

class NoKeys:  # Reads input and changes nothing
    def key(self, char: str) -> None: ...

model = Counter()
view = View()
model.connect(view.draw)
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

The two versions share three things: the `Counter` model,
the `model.connect(view.draw)` call that connects the view to the model,
and the printed output for the same input, `"++-x"`.
*Observer* does the same work either way,
which is why the chapter's opening calls the two architectures nearly equivalent.

One thing moves.
`key()` leaves `View` for `StepKeys`, and the model reference goes with it.
The MVC `View` keeps `draw()` and `StepKeys` gets `key()`, one job each.

Swapping in `NoKeys` at the end of `model_view_controller.py` shows what that move gives you.
`NoKeys` satisfies `Keys` and ignores every key,
so assigning it to `control` makes the program ignore input while `View` and the model work as before.
*GoF Design Patterns* gives this example for the separation:
a controller that ignores input disables a view's input.
`StepKeys` needs only a `Counter`, so a test can build a `StepKeys`,
call `key()`, and read `model.count`.
Supporting a different set of keys means writing a third class that satisfies `Keys`,
with `View` and the model unchanged.

MVC separates drawing from input handling,
the two jobs `document_view.py` gives one class,
and the `connect()` call stays the same.
`box_view.py` has the Document-View shape.
Its `draw()` paints, its `bind()` lambda handles the click,
and both are defined inside `show()`.

## What Stays Constant

*Observer* appears in four scenarios in this chapter:
a thermometer whose responders print a reading,
the same thermometer whose coroutine responders run concurrently,
a grid model whose responder repaints a canvas,
and a counter wired as Document-View and as MVC.
In every case the responder is a callable,
and the broadcaster holds responders and calls each one when its state changes.
The point at which the broadcaster receives its responders varies.
All four scenarios connect their responders at runtime,
`BoundBroadcaster` takes its responders at construction,
`Broadcasting` collects each instance's responders as Python runs their decorated `def` statements,
and exercise 11's registry collects them as Python imports a module.
The pattern requires no interface, no `update()` method, no class per responder,
and no `disconnect()`.

## Deciding What Matters

`Thermometer` has three jobs: it measures, it decides which changes to announce,
and it notifies the responders.
[Cohesion](21_Patterns--Design_Patterns.md#design-principles)
means one job per class.
Measuring is the thermometer's own job, and *Observer* adds the other two.
The code for notifying can leave the class.
`Broadcaster` holds the responder list and the notification loop,
and `Thermometer` inherits them.
`weather_station.py` uses no base class and calls its responders from `__setattr__()`,
so one method covers every attribute.
Either way the object still notifies its responders,
but the loop that calls them is written once,
in `Broadcaster` or in `__setattr__()`, apart from the code that measures.

The second job *Observer* adds is deciding which changes to announce.
That decision belongs to the object whose state changes, or to whoever calls it.
It never belongs to a responder,
whose choice is limited to filtering the changes it receives.
`Thermometer`'s setter announces every assignment,
which says that every change matters to everyone.
[Leaving that call to the client](#push-or-pull)
lets several changes coalesce into one announcement,
but then every caller must make that call,
and the responders stay out of date until it does.
Push sends the value, so the thermometer decides what each responder receives.
Pull sends the thermometer,
so each responder reads the attributes it needs from the thermometer and depends on the thermometer's interface.
`weather_station.py` leaves the choice to its responders.
Two states, `celsius` and `humidity`, share one channel,
so every responder receives both kinds of change,
along with the attribute name to filter by.

*Observer* therefore removes one coupling and keeps another.
The object that changes knows its responders only as callables,
yet it still decides what they hear.
A threshold makes that concrete.
This thermometer announces a reading only when it differs from the reading before it by at least `_delta`:

```python
# threshold_thermometer.py
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
t.connect(log.append)
t.connect(display)
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
Half a degree is the wrong judgment for `log`,
which exists to record every reading,
and the thermometer announces two of the four readings.
`log` loses the other two for good,
and nothing in `ThresholdThermometer` says which responder the half degree serves.
[`reentrant_announce_fixed.py`](#re-entrant-notification)
makes a smaller version of the same decision:
its setter returns early when the new value equals the current reading,
so a responder that counts readings rather than changes misses that repeated reading.

If the comparison moves into the responders,
each threshold sits with the responder that needs it.
`display` then remembers the last value it drew and skips a reading close to it,
`log` appends whatever arrives, and the setter announces every assignment again.
The thermometer knows nothing about tolerance,
and each responder that filters by size repeats the same comparison.
`async_thermometer_demo.py`'s `alarm` works this way,
returning at once for a reading below 100 degrees.

Repeating the comparison in each responder works for a question about *how much*,
because each responder sets its own threshold.
*Which kind* is a different question, and repetition handles it poorly,
because every kind of change arrives on one channel and each responder sorts them itself.
A responder in `weather_station.py` receives every attribute's changes,
so each responder that cares about one attribute repeats the same filter by name.
[Function Objects](28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type)
removes that repetition.
One list becomes a dictionary of lists keyed by event type,
so an announcement carries the type of thing that happened and each responder connects to the one type it handles.
The broadcaster then decides which event it is announcing, something it knows,
instead of guessing which responders need the event.

## Exercises

This chapter's [solutions](../Solutions/30_Patterns--Observer/) give a hint,
usually the shape of the code, and a full answer for each exercise.

1.  Create a minimal *Observer* design of your own,
    without looking at `broadcaster.py`:
    the smallest `Broadcaster` that lets you connect callables,
    then notifies them.
    Demonstrate it by connecting several responders and causing one change that updates them all.
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
    and raise them together as an exception group.
    Write a test in which the first responder raises an exception and the second still records its notification.
5.  Redo exercise 3 with each failure returned as a value instead of raised as an exception.
    Each responder returns a [`Result`](42_Functional--Error_Handling.md#a-result-type)
    from `utils/result.py`,
    and `announce()` returns the `Err` values it collects.
    Write an adapter that lets a responder returning `None`,
    such as `received.append`, be connected.
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
8.  Add a second view to `box_observer.py`'s `BoxModel`.
    Write one view that prints a letter per cell and another that prints how many cells each color holds,
    connect both to the same model,
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
    Connecting needs the descriptor, not the value it stores,
    so `__get__()` returns the descriptor for an access through the class,
    and `Thermometer.celsius.connect(t, readings.append)` reaches it.
    Show that an assignment to one attribute calls no responder of the other.
11. Write a load-time version of `Broadcaster`:
    a module-level list of responders and a `@responds` decorator that appends a function to it and returns the function unchanged.
    Each responder then registers when Python runs its `def` statement,
    and for a module-level function Python runs that statement while it imports the module.
    Give a `Thermometer` a `celsius` setter that announces to that list,
    and create two thermometers.
    Say which of the problems in this chapter's runtime sections the load-time form keeps,
    which it removes, and what it costs that `Broadcaster` does not.
12. Give `Broadcasting` the name-and-value signature of `weather_station.py`:
    `published()`'s setter announces the field's name along with the new value,
    and `Responder[T]` becomes `Callable[[str, T], None]`.
    Declare a subclass with `celsius` and `humidity` fields,
    and attach one responder that reports `celsius` readings and lets `humidity` pass.
    Show that an assignment to either field reaches that responder,
    so filtering by name is the responder's job, as it is for `WeatherStation`.
