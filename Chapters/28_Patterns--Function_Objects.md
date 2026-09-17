# Function Objects

A *function object* decouples the choice of function to call from the place that calls it.
That decoupling is the goal of three patterns: *Command*, *Strategy*,
and *Chain of Responsibility*.
The call site names the signature it will call and says nothing about where the callable came from.
[Design Patterns](21_Patterns--Design_Patterns.md#design-principles)
states that principle as "design the communication, not the parts."

Each pattern defers something:

- *Command* defers *what* to do, so you can store the action and run it later.
- *Strategy* defers *how*: the job is fixed,
  and the caller picks the algorithm that does it.
- *Chain of Responsibility* defers *which* handler takes the job,
  trying candidates until one accepts.

In Python a function is already an object.
You can name it, store it in a list, pass it as an argument, and return it.
That makes all three patterns largely unnecessary.
Where *GoF Design Patterns* builds a hierarchy, Python uses a function,
the dissolution that [Design Patterns](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
describes.

## Command: Choosing the Operation at Runtime

A *Command* wraps an action so you can pass it around and run it later.
In Python the action is a function.
In this example, a "macro" is a list of actions:

```python
# command.py
from collections.abc import Callable

type Command = Callable[[], None]

def no_more() -> None:
    print("This parrot is no more.")

def ceased() -> None:
    print("It has ceased to be.")

def fjords() -> None:
    print("It's pining for the fjords.")

macro: list[Command] = [no_more, ceased, fjords]
for command in macro:
    command()
#: This parrot is no more.
#: It has ceased to be.
#: It's pining for the fjords.
```

`Command` names the signature every entry must have: no arguments,
nothing returned.
The classic object form turns that name into a base class and wraps each action in a `Command` subclass with an `execute()` method:

```python
# command_pattern.py
from typing import override

class Command:
    def execute(self) -> None:
        raise NotImplementedError

class NoMore(Command):
    @override
    def execute(self) -> None:
        print("This parrot is no more.")

class Ceased(Command):
    @override
    def execute(self) -> None:
        print("It has ceased to be.")

class Fjords(Command):
    @override
    def execute(self) -> None:
        print("It's pining for the fjords.")

# An object that holds commands:
class Macro:
    def __init__(self) -> None:
        self.commands: list[Command] = []
    def add(self, command: Command) -> None:
        self.commands.append(command)
    def run(self) -> None:
        for c in self.commands:
            c.execute()

macro = Macro()
macro.add(NoMore())
macro.add(Ceased())
macro.add(Fjords())
macro.run()
#: This parrot is no more.
#: It has ceased to be.
#: It's pining for the fjords.
```

Both forms do the same thing.
The class version is four classes and a wrapper to say what one list of functions says directly.
*GoF Design Patterns* calls commands "an object-oriented replacement for callbacks."
Because in Python a callback is a function, the replacement is unnecessary.
A `Command` base class is worthwhile when the commands share implementation.
A second operation alone does not call for one;
the undo discussion below needs only a type.

Halfway between the function form and the class form,
a *bound method* is a ready-made command.
`account.deposit` names a function with its instance attached,
so a command list can hold it alongside plain functions.
The method keeps its state without any `Command` class:

```python
# bound_method.py
from collections.abc import Callable

type Command = Callable[[], None]

class Account:
    def __init__(self, balance: int) -> None:
        self.balance = balance
    def deposit(self) -> None:
        self.balance += 50
        print(f"balance: {self.balance}")

def alert() -> None:
    print("audit: checking balance")

account = Account(100)
macro: list[Command] = [
    account.deposit, alert, account.deposit,
]
for command in macro:
    command()
#: balance: 150
#: audit: checking balance
#: balance: 200
```

`account.deposit` sits in the same list as `alert`, a plain function,
with no `Command` class.
Each call still reads and updates `account.balance`,
the state the bound method carries with it.

An object can be callable too.
When a class defines `__call__()`
([Decorators](14_Techniques--Decorators.md#a-class-decorator-with-state)),
its instances carry state and still satisfy `Command`.
Here, `Repeat` is a [frozen data class](12_Techniques--Data_Classes_as_Types.md#immutability),
so its configuration cannot change after construction:

```python
# callable_command.py
from collections.abc import Callable
from record import record

type Command = Callable[[], None]

@record
class Repeat:
    text: str
    times: int
    def __call__(self) -> None:
        for _ in range(self.times):
            print(self.text)

def spam() -> None:
    print("Spam, eggs, sausage, spam.")

macro: list[Command] = [
    spam,
    Repeat("Ni!", 3),
]
for command in macro:
    command()
#: Spam, eggs, sausage, spam.
#: Ni!
#: Ni!
#: Ni!
```

A callable alone cannot express a second operation, `undo()`.
`Command` describes one call,
so an undoable list of commands needs a type with two members,
`__call__()` and `undo()`, and that type is a `Protocol`.
Exercise 1 builds that `Protocol`.

Building commands in a loop can produce Python's best-known closure mistake:

```python
# late_binding.py
from collections.abc import Callable
from functools import partial

type Command = Callable[[], None]

commands: list[Command] = [
    lambda: print(f"step {n}") for n in range(3)
]
for command in commands:
    command()  # Every lambda sees the final n
#: step 2
#: step 2
#: step 2

fixed: list[Command] = [
    partial(print, f"step {n}") for n in range(3)
]
for command in fixed:
    command()
#: step 0
#: step 1
#: step 2
```

The two comprehensions differ in when they read `n`.
A lambda's body runs when you call the command, not when you create it,
and all three lambdas close over the same loop variable,
which holds 2 by the time anything calls them.
The argument to `functools.partial`
([Functional Foundations](40_Functional--Foundations.md#partial-application))
is an ordinary expression that Python evaluates where you write it,
so each command stores the string built from its own iteration's `n` and has nothing left to look up later.
The older fix, `lambda n=n: print(f"step {n}")`,
does the same job with a default argument, which Python evaluates once,
when the lambda is created.
When commands built in a loop all behave like the last one,
the shared loop variable is the cause.

## Strategy: Choosing the Algorithm at Runtime

A *Strategy* is an interchangeable algorithm.
Three algorithms below find a *root* of a function `f`,
a value where `f(x)` is zero.
Each takes the function and two hints and returns the root,
or `None` when it cannot find one.
Bisection reads the two hints as a bracket,
an interval whose ends straddle the root.
The secant method reads them as two starting points,
and Newton's method averages them into one.
The secant and Newton methods are *open*: they need somewhere to start,
not a bracket, so the chain in `chain.py` can fall back on them.
All three share one signature, so they are interchangeable,
and `solve()` runs whichever one it is given:

```python
# algorithms.py
from collections.abc import Callable
from typing import Final

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200

def bisection(f: Fn, a: float, b: float) -> float | None:
    if f(a) * f(b) > 0:  # Endpoints must bracket a root
        return None
    for _ in range(MAX_ITER):
        mid = (a + b) / 2
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return None

def secant(f: Fn, a: float, b: float) -> float | None:
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:  # Flat step: cannot continue
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f: Fn, a: float, b: float) -> float | None:
    x = (a + b) / 2  # Start between the hints
    h = 1e-7
    for _ in range(MAX_ITER):
        # Approximate the derivative by central difference:
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None

def solve(f: Fn, a: float, b: float,
          finder: RootFinder) -> float:
    root = finder(f, a, b)
    if root is None:
        raise ValueError(f"no root in [{a}, {b}]")
    return root
```

`solve()` is the part of the procedure that does not change.
It runs a finder and turns a failed search into an exception,
so a caller receives a root or an exception and never handles `None`.
Because each finder is a function with the same signature,
passing one to `solve()` chooses the strategy:

```python
# strategy.py
from algorithms import bisection, newton, secant, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for finder in (bisection, newton, secant):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
```

In the classic form,
each algorithm becomes a class derived from a `FindRoot` interface,
with a `find()` method.
A "Context" class holds the chosen algorithm.
The Context becomes useful when something must hold the current algorithm between calls,
a job no parameter can do.

Python uses strategies-as-functions constantly without calling them a pattern.
The `key` argument passed to `sorted()`, `min()`, and `max()` is a strategy.
That argument determines how comparison works.

When a strategy needs configuration,
use a [*closure*](40_Functional--Foundations.md#closures).
An outer function takes the settings and returns the strategy,
and those settings stay available to the strategy after the outer function returns:

```python
# configured_strategy.py
from algorithms import Fn, RootFinder, solve

def bisection_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: float, b: float) -> float | None:
        if f(a) * f(b) > 0:  # Endpoints must bracket a root
            return None
        while abs(b - a) > tolerance:
            mid = (a + b) / 2
            if f(a) * f(mid) <= 0:
                b = mid
            else:
                a = mid
        return (a + b) / 2
    return finder

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = bisection_within(0.1)
fine = bisection_within(1e-9)
for finder in (coarse, fine):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.406250
#: 1.414214
```

Each call to `bisection_within()` returns a new finder whose closure holds that call's tolerance.
The coarse strategy stops within a tenth and reports 1.406250.
The fine one agrees with the true root to six places.
Because both satisfy `RootFinder`, `solve()` accepts either unchanged,
and so does the chain in `chain.py`.

When the algorithm takes the setting as an ordinary parameter,
`functools.partial` replaces the closure.
`partial` fills positional parameters from the left,
so bind a trailing setting by keyword:

```python
# partial_bisection.py
from functools import partial
from algorithms import Fn

def bisection_tol(f: Fn, a: float, b: float,
                  tolerance: float) -> float | None:
    while abs(b - a) > tolerance:
        mid = (a + b) / 2
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = partial(bisection_tol, tolerance=0.1)
fine = partial(bisection_tol, tolerance=1e-9)
print(f"{coarse(f, 0.0, 2.0):.6f}")
#: 1.406250
print(f"{fine(f, 0.0, 2.0):.6f}")
#: 1.414214
```

Because `bisection_tol` takes `tolerance` as an ordinary parameter,
`partial` binds it by keyword, once per strategy,
in place of `bisection_within`'s closure.
A positional-only parameter takes no keyword,
so binding one means passing a `Placeholder`
([Functional Foundations](40_Functional--Foundations.md#leaving-a-gap-with-placeholder))
in each position the caller will fill.

Save the strategy class for an algorithm that carries several related methods or mutable state.
Configuration alone is a closure's job.

## Chain of Responsibility: Choosing the Handler at Runtime

*Chain of Responsibility* tries a sequence of handlers until one succeeds.
*GoF Design Patterns* implements the chain as a linked structure,
each handler holding a reference to the next and deciding whether to pass the request along.
In Python that chain is simply a list of functions.

Bisection needs the interval to bracket a root.
The open methods do not:

```python
# chain.py
from algorithms import (Fn, RootFinder, bisection,
                        newton, secant)

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

chain: list[RootFinder] = [bisection, secant, newton]
# [0, 2] brackets the root, so bisection succeeds first:
r1 = solve(f, 0.0, 2.0, chain)
print(f"{r1:.6f}" if r1 is not None else "no root")
#: 1.414214
# No bracket in [1.0, 1.3]: bisection fails, secant works:
print(bisection(f, 1.0, 1.3))
#: None
r2 = solve(f, 1.0, 1.3, chain)
print(f"{r2:.6f}" if r2 is not None else "no root")
#: 1.414214
```

Each handler is a *Strategy* function, `chain` is the list of strategies,
and success is a non-`None` return.
This `solve()` reuses the name from `algorithms.py` with the opposite failure contract:
an exhausted chain returns `None` rather than raising,
and the caller decides what an empty result means.
The second `solve()` call shows the fall-through:
because the interval `[1.0, 1.3]` does not straddle the root,
bisection fails by returning `None`.
The loop continues to a method that needs no bracket.
To add, remove, or reorder the handlers you edit the `chain` list.

The test is `root is not None`, not `if root`.
A finder returns `0.0` for a function whose root is at zero, and `0.0` is falsy,
so a truthiness test would discard a correct answer and call the next finder.
The hazard is the truthiness test, not the choice of failure value.
Whichever value marks failure, compare the result against it with `is`.
`None` is the right failure value here because a root is never `None`,
so `float | None` says which result is which.
A `sentinel()` ([Sentinel Values](05_Foundations--Functions.md#sentinel-values))
is for the case where `None` is a possible result and cannot double as the failure mark.

The chain has no check of its own:
each handler decides for itself whether it failed,
and reports that decision as its return value.
`secant()` and `newton()` report success when their latest step shrinks below the tolerance.
A step below the tolerance is not quite the same as reaching a root,
so a chain is no more reliable than its handlers.

Testing confirms that the first finder to converge returns the root while the rest never run,
that a later finder succeeds where an earlier one fails,
that an empty chain returns `None`,
and that a chain whose finders all fail returns `None` too:

```python
# test_chain.py
from algorithms import bisection, newton, secant
from chain import Fn, RootFinder, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def watched(finder: RootFinder,
            tried: list[str]) -> RootFinder:
    def recording(f: Fn, a: float,
                  b: float) -> float | None:
        tried.append(finder.__name__)  # type: ignore
        return finder(f, a, b)
    return recording

def test_first_successful_finder_wins() -> None:
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = solve(f, 0.0, 2.0, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection"]  # The rest never ran

def test_chain_falls_through_to_a_later_method() -> None:
    # [1.0, 1.3] does not bracket the root: bisection fails
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = solve(f, 1.0, 1.3, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection", "secant"]

def test_empty_chain_returns_none() -> None:
    assert solve(f, 0.0, 2.0, []) is None

def test_all_fail_returns_none() -> None:
    def g(x: float) -> float:
        return x * x + 1  # No real root
    assert solve(g, 0.0, 2.0, [bisection]) is None
```

The first two tests wrap each finder in `watched()`,
which records the finder's name as it runs.
The tests can then assert not just the root but *which* finders ran.

## An Event Bus: Handlers Keyed by Type

*Chain of Responsibility* keeps its handlers in a list and tries them in order.
If you key that structure by type instead of by position,
you have an *event bus*.
The bus is a `dict` keyed by event type.
Each key maps to a list of handlers,
and `subscribe()` appends a handler to the list under the event type it handles.
The events are values,
written as [frozen data classes](12_Techniques--Data_Classes_as_Types.md#immutability).
Publishing an event looks up its type and calls every handler registered for that type.
The handlers are ordinary functions, so they need no base class.
Registering one is a single `subscribe()` call.
Here, `Handler` names their signature, not an interface:

```python
# event_bus.py
from collections import defaultdict
from collections.abc import Callable
from typing import Any
from record import record

type Handler[E] = Callable[[E], None]

@record
class Deposit:
    amount: int

@record
class Withdraw:
    amount: int

@record
class Closed:
    reason: str

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

def on_deposit(event: Deposit) -> None:
    print(f"+ deposit {event.amount}")

def audit(event: Deposit) -> None:
    print(f"  audit: a deposit of {event.amount}")

def on_withdraw(event: Withdraw) -> None:
    print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
# Two handlers for one event type
bus.subscribe(Deposit, audit)
bus.subscribe(Withdraw, on_withdraw)

bus.publish(Deposit(100))
#: + deposit 100
#:   audit: a deposit of 100
bus.publish(Withdraw(30))
#: - withdraw 30
# No handler: nothing happens
bus.publish(Closed("inactivity"))
```

`subscribe` is generic on the event type `E`, which appears in both parameters.
The type checker must therefore find one `E` that satisfies the event type and the handler together.
No such `E` exists for `subscribe(Deposit, on_withdraw)`,
so the type checker reports a type error.
The check runs once, at registration.
The stored `defaultdict`, though,
mixes handlers for every event type in one structure.
Its lists cannot name a single event class,
so their element type is `Handler[Any]`.

`subscribe` indexes `self._handlers` directly,
letting the `defaultdict` build each event type's list on first use.
`publish` reads with `.get(type(event), [])` instead of indexing,
because indexing a `defaultdict` inserts an empty list as a side effect.
Every published event type with no subscriber, such as `Closed`,
would otherwise leave a stray entry behind.

The lookup uses `type(event)`, which matches the class and no ancestor.
A subclass of `Deposit` published to this bus matches no handler,
so `publish()` calls nothing, exactly as it does for `Closed`.
Walking `type(event).__mro__` and calling every handler along it would give a subclass event its parent's handlers.
An event would then run every handler registered anywhere in its ancestry,
not only the ones registered for its own type.

Testing confirms that publishing calls every handler registered for a type,
a handler receives only its own event type,
an event with no handler calls nothing,
and publishing an unhandled event leaves no stray entry behind:

```python
# test_event_bus.py
from event_bus import Closed, Deposit, EventBus, Withdraw

def test_every_handler_for_the_type_is_called() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit,
                  lambda e: seen.append(f"a{e.amount}"))
    bus.subscribe(Deposit,
                  lambda e: seen.append(f"b{e.amount}"))
    bus.publish(Deposit(5))
    assert seen == ["a5", "b5"]

def test_only_the_matching_type_is_called() -> None:
    calls: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit,
                  lambda e: calls.append("deposit"))
    bus.subscribe(Withdraw,
                  lambda e: calls.append("withdraw"))
    bus.publish(Withdraw(1))
    assert calls == ["withdraw"]

def test_no_handler_is_a_noop() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))  # Must not raise

def test_get_leaves_no_stray_handler_list() -> None:
    # publish() reads with .get(): no stray entry appears
    bus = EventBus()
    bus.publish(Closed("done"))
    assert Closed not in bus._handlers
```

In `event_bus.py`, the events are frozen data classes,
the handlers are functions, and the bus is a `dict`.
A second version gives each side a decorator,
both producing frozen data classes.
`@event` records its class in `EVENTS`.
`@handler` makes a function object whose fields are its configuration,
and records in `HANDLES` which event its `__call__` accepts.
`Handler` becomes a `Protocol` whose one method is `__call__()`,
because the handlers are now objects rather than functions;
it still names their signature and nothing more.
`subscribe()` then takes one argument, since the handler says what it handles,
and `publish()` refuses an object that no `@event` class produced:

```python
# tagged_bus.py
import inspect
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Final, Protocol, dataclass_transform
from exceptions import expect

EVENTS: Final[set[type]] = set()
HANDLES: Final[dict[type, type]] = {}

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    EVENTS.add(cls)
    return dataclass(frozen=True)(cls)

class Handler[E](Protocol):
    def __call__(self, event: E, /) -> None: ...

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    call = vars(cls).get("__call__")
    if call is None:
        raise TypeError(f"{cls.__name__} has no __call__")
    sig = inspect.signature(call)
    handled = list(sig.parameters.values())[1].annotation
    if handled not in EVENTS:
        raise TypeError(f"{cls.__name__}: not an @event")
    HANDLES[cls] = handled
    return dataclass(frozen=True)(cls)

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe(self, handler: Handler[Any]) -> None:
        handled = HANDLES.get(type(handler))
        if handled is None:
            name = type(handler).__name__
            raise TypeError(f"{name} is not a @handler")
        self._handlers[handled].append(handler)

    def publish(self, event: object) -> None:
        if type(event) not in EVENTS:
            name = type(event).__name__
            raise TypeError(f"{name} is not an @event")
        for handler in self._handlers.get(type(event), []):
            handler(event)

@event
class Deposit:
    amount: int

@event
class Withdraw:
    amount: int

@event
class Closed:
    reason: str

@handler
class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        print(f"{self.prefix} deposit {event.amount}")

@handler
class Audit:
    threshold: int
    def __call__(self, event: Deposit) -> None:
        if event.amount > self.threshold:
            print(f"  audit: large deposit {event.amount}")

@handler
class OnWithdraw:
    def __call__(self, event: Withdraw) -> None:
        print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Announce("+"))
bus.subscribe(Audit(threshold=50))
bus.subscribe(OnWithdraw())
bus.publish(Deposit(100))
#: + deposit 100
#:   audit: large deposit 100
bus.publish(Deposit(10))
#: + deposit 10
bus.publish(Withdraw(30))
#: - withdraw 30
bus.publish(Closed("inactivity"))  # An event, no handler
expect(TypeError, bus.publish, "Deposit")
#: [TypeError] str is not an @event
```

`dataclass_transform`
([Metaprogramming](17_Techniques--Metaprogramming.md#where-enforcement-lives))
tells the type checker that a class passing through either decorator comes out a frozen data class.
`Audit(threshold=50)` therefore has its generated `__init__`,
and `ty` reports `Audit(50).threshold = 1` as assignment to a read-only property,
as it would with `@dataclass(frozen=True)` written directly.
The tags are runtime facts.
`@handler` reads the annotation on the first parameter after `self` in `__call__`,
the same annotation the type checker checks, so a handler names its event once.
`publish()` keeps its `object` parameter,
because no static type means "a class `@event` decorated",
so a stray string reaches the bus and `EVENTS` rejects it there.

The price is the registration-time check of the first version.
`subscribe(Deposit, on_withdraw)` fails under `ty` because no `E` fits both arguments.
With one argument there is no pair to compare,
so a class with the right `__call__` that skipped `@handler` passes the type checker and fails only when `subscribe()` looks it up.
Tests cover that refusal and the other three: a non-event published,
a `@handler` class with no `__call__`,
and one whose `__call__` accepts something no `@event` produced:

```python
# test_tagged_bus.py
import pytest
from tagged_bus import Deposit, EventBus, Withdraw, handler

def test_handler_receives_its_event() -> None:
    seen: list[int] = []
    @handler
    class Record:
        def __call__(self, event: Deposit) -> None:
            seen.append(event.amount)
    bus = EventBus()
    bus.subscribe(Record())
    bus.publish(Deposit(5))
    bus.publish(Withdraw(1))
    assert seen == [5]

def test_publish_rejects_a_non_event() -> None:
    with pytest.raises(TypeError, match="not an @event"):
        EventBus().publish("Deposit")

def test_subscribe_rejects_an_undecorated_class() -> None:
    class Plain:
        def __call__(self, event: Deposit) -> None: ...
    with pytest.raises(TypeError, match="not a @handler"):
        EventBus().subscribe(Plain())

def test_handler_needs_a_call_on_an_event() -> None:
    with pytest.raises(TypeError, match="has no __call__"):
        @handler
        class NoCall:
            x: int
    with pytest.raises(TypeError, match="not an @event"):
        @handler
        class WrongEvent:
            def __call__(self, event: int) -> None: ...
```

The bus is the [*Observer*](30_Patterns--Observer.md#the-pythonic-observer-a-list-of-callables)
with one shared subject: instead of every observable holding its own list,
one bus holds every list and the event type selects the handlers.
Here a type may have many handlers.
When each type needs exactly one,
and a new type must add its own without editing a central function,
`functools.singledispatch` is the solution.
[*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
and [Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)
both use it.

## Choosing the Lightest Callable

Stop at the first form that supports what you need:

1.  A plain function, when the behavior needs no state of its own
    (`command.py`, `strategy.py`).
2.  A bound method, when the state already belongs to an object.
    `account.deposit` is a command with its instance attached.
3.  A closure or a `functools.partial`, when the state is a fixed configuration
    (`configured_strategy.py`).
4.  A callable object, when that configuration needs a name and a `repr`
    (`callable_command.py`).
5.  A class, when one call is not enough: a second operation such as `undo()`,
    or the several related methods and mutable state the *Strategy* section describes.

The *GoF Design Patterns* forms of *Command*, *Strategy*,
and *Chain of Responsibility* all start at number 5.
The C++ of that book had no lighter form that could carry state:
a function pointer carried none, and closures did not exist yet,
so a class was the only form available.
The GoF form then gives that class a named operation, `execute()`,
rather than a call, which is entry 5 rather than entry 4.

## Exercises

1.  Add an "undo" capability to `command.py`.
    What do the commands need to become, and is a function still enough,
    or do you now want an object?
2.  Rewrite `chain.py` so each handler also reports why it failed,
    and the solver prints every attempt before returning the winner.
3.  Use `sorted()` with a `key` function to sort a list of `(name, score)` tuples by score,
    then by name.
    Explain why `key` is the *Strategy* pattern.
4.  Following `bisection_within()`,
    add a `tolerance` parameter to `newton()` in `algorithms.py` and build a configured strategy from it two ways:
    with a closure, and with `functools.partial`.
    Confirm that `chain.py`'s `solve()` runs a chain holding either one,
    with no change to `solve()`.
5.  Because `EventBus.publish()` looks up `type(event)`,
    a subclass of `Deposit` finds no handler.
    Change `publish()` to walk `type(event).__mro__` and call every handler registered along it,
    parents last.
    Then add `unsubscribe()`.
    Which of the two changes can break an existing caller, and why?
6.  Build a list of three commands in a `for` loop (not a comprehension)
    with `lambda: print(n)`.
    Call them and explain the output.
    Fix the loop three ways: with a default argument, with `functools.partial`,
    and with a factory function that takes `n` and returns the command.
    Which one still works if you must compute the value at call time rather than at build time?
