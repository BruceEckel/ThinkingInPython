# Function Objects

> One place decides what to do,
> and another place does it later or does it a different way each time.
> A *function object* carries the decision from the first place to the second.

A *function object* decouples the choice of function to call from the place that calls it.
That decoupling is the goal of three patterns: *Command*, *Strategy*,
and *Chain of Responsibility*.
The call site specifies the signature it calls.
The callable can come from anywhere.
[Design Patterns](21_Patterns--Design_Patterns.md#design-principles)
states that principle as "design the communication, not the parts."

Each pattern defers something:

- *Command* defers what to do, so you can store the action and run it later.
- *Strategy* defers how to do the job.
  The job stays the same.
  The caller picks the algorithm that performs it.
- *Chain of Responsibility* defers which handler takes the job,
  trying candidates until one accepts.

In Python a function is an object.
You can name it, store it in a list, pass it as an argument, and return it.
That makes all three patterns largely unnecessary.
Where *GoF Design Patterns* builds a hierarchy, Python uses a function,
and the pattern [dissolves into the language](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves).

## Command: Choosing the Operation at Runtime

A *Command* wraps an action so you can pass it around and run it later.
In Python the action is a function.
Here, a "macro" is a list of actions:

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

`Command` names the signature every entry must have.
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

The class version takes four classes and a wrapper to say what one list of functions says.
*GoF Design Patterns* calls commands "an object-oriented replacement for callbacks."
Because in Python a callback is a function, the replacement is unnecessary.

A `Command` base class is worthwhile when the commands share implementation.
A second operation, such as `undo()`, calls for a type with two members.
The [undo discussion](#a-callable-object-as-a-command)
describes that type with a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols).

### A Bound Method as a Command

Halfway between the function form and the class form,
a *bound method* is a ready-made command.
`account.deposit` names a function with its instance attached,
so a macro can hold it alongside plain functions.
The bound instance carries the state that a `Command` subclass holds:

```python
# bound_method.py
from collections.abc import Callable
from dataclasses import dataclass

type Command = Callable[[], None]

@dataclass
class Account:
    balance: int
    def deposit(self) -> None:
        self.balance += 50
        print(f"balance: {self.balance}")

def audit() -> None:
    print("audit: checking balance")

account = Account(100)
macro: list[Command] = [
    account.deposit, audit, account.deposit,
]
for command in macro:
    command()
#: balance: 150
#: audit: checking balance
#: balance: 200
```

Each call to `account.deposit` reads and updates `account.balance` through `account`,
the instance the bound method stores as its `__self__`.

The entry is `account.deposit`, without parentheses.
`account.deposit()` calls the method while Python builds the list,
so the list stores the result, `None`.
The type checker rejects that list, because `None` is not a `Command`.

### A Callable Object as a Command

An object can be callable.
When a class defines `__call__()`,
its instances [carry state](14_Techniques--Decorators.md#a-class-form-decorator-with-state)
and still satisfy `Command`.
Here, `Repeat` is a [record](18_Techniques--Performance.md#record),
so its configuration stays the same after construction:

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
print(macro[1])
#: Repeat(text='Ni!', times=3)
```

Printing `macro[1]` shows the `repr` that `@record` generates,
so you can read the command's configuration from outside the object.
A closure's `repr` shows its function's name and a memory address.

`Command` describes one call.
An undoable macro needs a second operation on each command, `undo()`.
A command's type then has two members, `__call__()` and `undo()`,
and a `Protocol` describes that type (see exercise 1).
[*Memento*](36_Patterns--Memento.md#the-caretaker-a-generic-history)
undoes the other way,
by restoring a saved snapshot of the state instead of running an inverse.

### The Late-Binding Trap

Building commands in a loop can produce Python's best-known [closure](40_Functional--Foundations.md#closures)
mistake:

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

bound: list[Command] = [
    partial(print, f"step {n}") for n in range(3)
]
for command in bound:
    command()
#: step 0
#: step 1
#: step 2
```

The two comprehensions differ in when they read `n`.
A lambda's body runs when you call the command, not when you create it.
All three lambdas close over the same loop variable,
which holds 2 by the time anything calls them.
The argument to [`functools.partial()`](40_Functional--Foundations.md#partial-application)
is an ordinary expression that Python evaluates where you write it,
so each command stores the finished string built from its own iteration's `n`.
The older remedy binds the value through a default argument,
`lambda n=n: print(f"step {n}")`.
Python evaluates a default once, when it creates the lambda.
When commands built in a loop all behave like the last one,
the shared loop variable is the cause.

## Strategy: Choosing the Algorithm at Runtime

A *Strategy* is an interchangeable algorithm.
Three algorithms below find a *root* of a function `f`,
a value where `f(x)` is zero.
Each takes the function and two hints and returns the root,
or `None` when it cannot find one.

Bisection reads the two hints as a bracket,
an interval whose ends lie on opposite sides of the root.
The secant method reads them as two starting points.
Newton's method averages them into one.
The secant and Newton methods are *open*: they need somewhere to start,
not a bracket.

All three share one signature, so they are interchangeable,
and `solve()` runs whichever one the caller passes:

```python
# algorithms.py
from collections.abc import Callable
from typing import Final

type Fn = Callable[[float], float]
type Hint = float
type Root = float
type RootFinder = Callable[[Fn, Hint, Hint], Root | None]

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200

def bisection_tol(f: Fn, a: Hint, b: Hint,
                  tolerance: float) -> Root | None:
    if f(a) * f(b) > 0:  # Endpoints must bracket a root
        return None
    while abs(b - a) > tolerance:
        mid = (a + b) / 2
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2

def bisection(f: Fn, a: Hint, b: Hint) -> Root | None:
    return bisection_tol(f, a, b, TOLERANCE)

def secant(f: Fn, a: Hint, b: Hint) -> Root | None:
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

def newton(f: Fn, a: Hint, b: Hint) -> Root | None:
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

def solve(f: Fn, a: Hint, b: Hint,
          finder: RootFinder) -> Root:
    root = finder(f, a, b)
    if root is None:
        raise ValueError(f"no root in [{a}, {b}]")
    return root
```

`solve()` is the part of the procedure that stays the same.
It runs a finder and turns a failed search into an exception,
so a caller receives a root or an exception, not a `None` to check.
Because each finder is a function with the same signature,
passing one to `solve()` chooses the strategy:

```python
# strategy.py
from algorithms import bisection, newton, secant, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for finder in (bisection, newton, secant):
    root = solve(f, 0.0, 2.0, finder)
    print(f"{finder.__name__}: {root:.6f}")
#: bisection: 1.414214
#: newton: 1.414214
#: secant: 1.414214
```

In the classic form,
each algorithm becomes a class derived from a `FindRoot` interface,
with a `find()` method.
A "Context" class holds the chosen algorithm.
A parameter holds a strategy for the length of one call,
so you need a Context when the program must keep the algorithm after the call returns.

In Smalltalk's MVC, a view is that Context and its controller is the strategy.
*GoF Design Patterns* names the pair as an example of *Strategy*.
The controller decides how the view responds to input.
Replacing the controller changes the response and leaves the display as it was.
A controller that ignores input events disables the view.
[*Observer*](30_Patterns--Observer.md) covers MVC's other half,
where a model notifies its views.

Python uses strategies-as-functions constantly without calling them a pattern.
The `key` argument passed to `sorted()`, `min()`, and `max()` is a strategy.
It chooses the value the algorithm compares for each item.
The algorithm stays the same (see exercise 3).

When a strategy needs configuration,
use a [closure](40_Functional--Foundations.md#closures).
An outer function takes the settings and returns the strategy.
Those settings stay available to the strategy after the outer function returns.

In `algorithms.py`, `bisection()` calls `bisection_tol()`,
a bisection that stops once the bracket is narrower than `tolerance`,
and always passes it `TOLERANCE`.
`RootFinder` describes three parameters, while `bisection_tol()` has four.
A closure binds the fourth, a tolerance of your choosing,
and returns a three-parameter finder:

```python
# configured_strategy.py
from algorithms import (Fn, Hint, Root, RootFinder,
                        bisection_tol, solve)

def bisection_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: Hint, b: Hint) -> Root | None:
        return bisection_tol(f, a, b, tolerance)
    return finder

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for tolerance in (0.1, 1e-9):
    finder = bisection_within(tolerance)
    root = solve(f, 0.0, 2.0, finder)
    print(f"tolerance {tolerance}: {root:.6f}")
#: tolerance 0.1: 1.406250
#: tolerance 1e-09: 1.414214
```

Each call to `bisection_within()` returns a new finder whose closure holds that call's tolerance.
Because both finders satisfy `RootFinder`, `solve()` accepts either unchanged.
So does `first_root()`, which the next section defines in `chain.py`.

Because `bisection_tol()` takes the setting as an ordinary parameter,
`functools.partial()` can replace the closure.
`partial()` fills positional parameters from the left,
so bind a trailing setting by keyword:

```python
# partial_bisection.py
from functools import partial
from algorithms import bisection_tol, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for tolerance in (0.1, 1e-9):
    finder = partial(bisection_tol, tolerance=tolerance)
    root = solve(f, 0.0, 2.0, finder)
    print(f"tolerance {tolerance}: {root:.6f}")
#: tolerance 0.1: 1.406250
#: tolerance 1e-09: 1.414214
```

Each `partial` object satisfies `RootFinder`,
so `solve()` calls a `partial` object with the same three arguments it passes a closure.

Binding by keyword fails for a [positional-only parameter](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters),
which a caller must pass by position.
To bind one, `partial()` takes a [`Placeholder`](40_Functional--Foundations.md#leaving-a-gap-with-placeholder)
in each earlier position the caller fills.

Save the strategy class for an algorithm that carries several related methods or mutable state.
Configuration alone is a job for a closure or a `partial` object.

## Chain of Responsibility: Choosing the Handler at Runtime

*Chain of Responsibility* tries a sequence of handlers until one succeeds.
*GoF Design Patterns* implements the chain as a linked structure.
Each handler holds a reference to the next and decides whether to pass the request along.
In Python that chain is a list of functions.
`first_root()` returns the first root a finder in the list reports:

```python
# chain.py
from algorithms import Fn, Hint, Root, RootFinder

def first_root(f: Fn, a: Hint, b: Hint,
               chain: list[RootFinder]) -> Root | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None
```

Each handler is a *Strategy* function, `chain` is the list of strategies,
and a returned `float` signals success.
An exhausted chain returns `None` rather than raising an exception.
The caller decides what an empty result means.

Bisection needs the interval to bracket a root.
The open methods need only a place to start.
Running bisection alone and then the chain on two intervals shows the difference:

```python
# chain_demo.py
from algorithms import (Root, RootFinder, bisection,
                        newton, secant)
from chain import first_root

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def show(root: Root | None) -> str:
    return "None" if root is None else f"{root:.6f}"

chain: list[RootFinder] = [bisection, secant, newton]
for a, b in ((0.0, 2.0), (1.0, 1.3)):
    alone = show(bisection(f, a, b))
    first = show(first_root(f, a, b, chain))
    print(f"[{a}, {b}] bisection: {alone}, chain: {first}")
#: [0.0, 2.0] bisection: 1.414214, chain: 1.414214
#: [1.0, 1.3] bisection: None, chain: 1.414214
```

The `[1.0, 1.3]` line shows the fall-through.
Both ends of that interval lie below the root, so bisection returns `None`.
The loop in `first_root()` then calls `secant()`,
which reads the two ends as starting points and finds the root.
Adding, removing, or reordering the finders means editing the `chain` list.

The test in `first_root()` is `root is not None`, not `if root`.
A finder returns `0.0` for a function whose root is at zero.
Because `0.0` is falsy,
a [truthiness](02_Foundations--Tour.md#booleans-none-and-truthiness)
test discards that correct answer and calls the next finder.
The hazard is the truthiness test, not the choice of failure value.
Whichever value marks failure, compare the result against it with `is`.

`None` is the right failure value here because a root is always a `float`,
so a `None` result means the search failed.
When `None` is a possible result, it cannot double as the failure mark.
A [`sentinel()`](05_Foundations--Functions.md#sentinel-values) takes that role.

Each finder decides for itself whether it succeeded,
and reports that decision as its return value.
`secant()` and `newton()` report success when their latest step shrinks below the tolerance.
A small step shows that the estimate stopped moving.
Neither finder checks how close `f(x)` is to zero,
so a chain's answer is as trustworthy as the finder that gave it.

The test file confirms that:

- The first finder to converge returns the root,
  and the finders after it do not run.
- A later finder succeeds where an earlier one fails.
- An empty chain returns `None`.
- A chain whose finders all fail returns `None` too.

```python
# test_chain.py
from algorithms import (Fn, Hint, Root, RootFinder,
                        bisection, newton, secant)
from chain import first_root

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def watched(finder: RootFinder,
            tried: list[str]) -> RootFinder:
    def recording(f: Fn, a: Hint,
                  b: Hint) -> Root | None:
        tried.append(finder.__name__)  # type: ignore
        return finder(f, a, b)
    return recording

def test_first_successful_finder_wins() -> None:
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = first_root(f, 0.0, 2.0, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection"]  # The rest never ran

def test_chain_falls_through_to_a_later_method() -> None:
    assert f(1.0) * f(1.3) > 0  # No bracket
    assert bisection(f, 1.0, 1.3) is None
    tried: list[str] = []
    chain = [watched(x, tried)
             for x in (bisection, secant, newton)]
    root = first_root(f, 1.0, 1.3, chain)
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6
    assert tried == ["bisection", "secant"]

def test_empty_chain_returns_none() -> None:
    assert first_root(f, 0.0, 2.0, []) is None

def test_all_fail_returns_none() -> None:
    def g(x: float) -> float:
        return x * x + 1  # No real root
    chain: list[RootFinder] = [bisection, secant, newton]
    assert first_root(g, 0.0, 2.0, chain) is None
```

`watched()` carries a `# type: ignore` because `RootFinder` is a `Callable`,
and a `Callable` declares no `__name__`.
The type checker is right about the type.
A `partial` object is a `RootFinder`, and it has no `__name__`.
The three finders here are functions, and every function has one.
A `Protocol` that declares `__name__` beside `__call__()` states that requirement in the type,
in place of the `# type: ignore`.

All three patterns share one shape:

![](_images/function_objects_story)

In every lane the call site stays the same short loop or call,
and it depends on the signature alone.
The patterns differ in how many of the chosen function objects the call site runs:
all of them in turn, one per call, or the first that succeeds.
That count, rather than a class structure, separates *Command*, *Strategy*,
and *Chain of Responsibility* in Python.

## An Event Bus: Handlers Keyed by Type

*Chain of Responsibility* keeps its handlers in a list and tries them in order.
If you key that structure by type instead of by position,
you have an *event bus*.
Publishing an event looks up its type and calls every handler registered for that type.
Calling every handler is the second difference from the chain,
which stops at the first handler that succeeds.

The events are values, written as records.
The handlers are ordinary functions,
so any function with the right signature is a handler.
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
```

`subscribe()` is generic on the event type `E`,
which appears in both parameters.
The type checker must therefore find one `E` that satisfies the event type and the handler together.
No such `E` exists for a `Deposit` paired with a handler that takes a `Withdraw`,
so the type checker reports a type error.
The check runs once, at registration.
The stored `defaultdict`, though,
mixes handlers for every event type in one structure.
One annotation covers every list.
No single event class fits all of them, so the element type is `Handler[Any]`.

```python
# event_bus_demo.py
from event_bus import Closed, Deposit, EventBus, Withdraw

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

`subscribe()` indexes `self._handlers`,
letting the `defaultdict` build each event type's list on first use.
`publish()` reads with `.get(type(event), [])` instead of indexing,
because indexing a `defaultdict` inserts an empty list as a side effect.
Indexing leaves a stray entry behind for every published event type with no handler,
such as `Closed`.

The lookup uses `type(event)`, which matches the event's exact class.
A subclass of `Deposit` published to this bus gets the empty default list from `.get()`,
as `Closed` does.
Walking `type(event).__mro__` and calling every handler along it gives a subclass event its parent's handlers.
An event then runs the handlers registered for its own type and for every ancestor
(see exercise 5).

The test file confirms that:

- Publishing calls every handler registered for a type.
- A handler receives only its event type.
- Publishing an event with no handler returns normally.
- Publishing an unhandled event leaves `_handlers` as it was.

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

def test_handler_receives_only_its_event_type() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit,
                  lambda e: seen.append("deposit"))
    bus.subscribe(Withdraw,
                  lambda e: seen.append("withdraw"))
    bus.publish(Withdraw(1))
    assert seen == ["withdraw"]

def test_unhandled_event_raises_no_exception() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))

def test_unhandled_event_leaves_no_stray_entry() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))
    assert Closed not in bus._handlers
```

## A Tagged Bus: Handlers That Name Their Event

In `event_bus.py`, the events are records, the handlers are functions,
and the bus is a `dict`.
Each `subscribe()` call repeats the event type that the handler's annotation specifies.
A second version reads the annotation, so a handler specifies its event once.

The second version gives each side a decorator.
Both decorators produce records:

```python
# tagged_bus.py
import inspect
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final, dataclass_transform

EVENTS: Final[set[type]] = set()
HANDLES: Final[dict[type, type]] = {}

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    built = dataclass(frozen=True, slots=True)(cls)
    EVENTS.add(built)
    return built

type Handler[E] = Callable[[E], None]

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    call = vars(cls).get("__call__")
    if call is None:
        raise TypeError(f"{cls.__name__} has no __call__")
    sig = inspect.signature(call)
    handled = list(sig.parameters.values())[1].annotation
    if handled not in EVENTS:
        raise TypeError(f"{cls.__name__}: not an @event")
    built = dataclass(frozen=True, slots=True)(cls)
    HANDLES[built] = handled
    return built

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
```

`@handler` makes a class whose instances are function objects,
with fields that hold their configuration.
`Handler` keeps its `Callable` definition,
which accepts a callable object as `Command` accepts `Repeat` in `callable_command.py`.

`handler()` looks for `__call__()` in `vars(cls)`, the class's own namespace.
`hasattr(cls, "__call__")` cannot make that test,
because it is true of every class.
A class is callable, and calling it builds an instance.

Each decorator registers `built`, the class that `dataclass()` returns,
and not the `cls` it received.
Python sets a class's slots when it creates the class,
so `slots=True` makes `dataclass()` build a new class and return it.
Registering `cls` puts the original class in `EVENTS`.
Every event is an instance of `built`.
`publish()` then refuses every event.
`@handler` refuses every handler class,
because the annotation it reads evaluates to `built` (see exercise 7).

A bank account's events and handlers are classes under the two decorators:

```python
# bank_events.py
from tagged_bus import event, handler

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
```

[`dataclass_transform`](17_Techniques--Metaprogramming.md#dataclass-transform)
tells the type checker that a class decorated with either decorator is a frozen data class.
`Audit(threshold=50)` therefore has its generated `__init__()`,
and the type checker rejects `Audit(50).threshold = 1` as an assignment to a read-only property,
as it does for a class decorated with `@dataclass(frozen=True)`.

The two decorators fill `EVENTS` and `HANDLES` at run time.
The type checker reads the source and never runs it,
so it cannot check what those two collections hold.
`@handler` reads the annotation on the first parameter after `self` in `__call__()`,
the same annotation the type checker reads,
so a handler specifies its event once.

```python
# tagged_bus_demo.py
from bank_events import (Announce, Audit, Closed,
                         Deposit, OnWithdraw, Withdraw)
from exceptions import expect
from tagged_bus import EventBus

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

`publish()` keeps its `object` parameter,
because no static type means "an instance of a class decorated with `@event`".
The type checker therefore accepts a stray string as the argument.
`publish()` rejects the string at run time,
when it finds `str` missing from `EVENTS`.

The tagged bus gives up the registration-time check of the first version.
`subscribe(Deposit, on_withdraw)` fails under the type checker because no `E` fits both arguments.
The tagged `subscribe()` takes one argument, typed `Handler[Any]`,
so the type checker accepts any callable of that shape.
An instance of an undecorated class with the right `__call__()` therefore passes the type checker.
`subscribe()` rejects it at run time, when it looks up the class in `HANDLES`.

The test file confirms that:

- A handler receives the events of its own type.
- `publish()` refuses an object that is not an event.
- `subscribe()` refuses an instance of a class without `@handler`.
- `@handler` refuses a class with no `__call__()`,
  and one whose `__call__()` annotates `int` instead of an `@event` class.

```python
# test_tagged_bus.py
import pytest
from bank_events import Deposit, Withdraw
from tagged_bus import EventBus, handler

def test_handler_receives_its_event() -> None:
    seen: list[int] = []
    @handler
    class Collect:
        def __call__(self, event: Deposit) -> None:
            seen.append(event.amount)
    bus = EventBus()
    bus.subscribe(Collect())
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

The bus is the [*Observer*](30_Patterns--Observer.md#the-pythonic-observer)
with one shared subject
(*Observer* calls the subject a broadcaster and each handler a responder).
Instead of every subject holding its own list, one bus holds every list.
The event type selects the handlers.

On the bus, a type may have many handlers.
When each type needs exactly one,
and a new type must add its own without editing a central function,
use `functools.singledispatch`.
The dispatcher calls the function registered for the type of its first argument.
Each new type adds its own function with `register()`.
[*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
and [Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
both use `singledispatch`.

## Choosing the Lightest Callable

Stop at the first form that supports what you need:

1.  A plain function, when the behavior depends on its arguments alone
    (`command.py`, `strategy.py`).
2.  A bound method, when the state belongs to an existing object.
    `account.deposit` is a command with its instance attached
    (`bound_method.py`).
3.  A closure or a `functools.partial()`,
    when the state is a configuration set at creation
    (`configured_strategy.py`, `partial_bisection.py`).
4.  A callable object, when that configuration needs a name and a `repr`
    (`callable_command.py`).
5.  A class, when the behavior needs a second operation such as `undo()`,
    or the several related methods and mutable state the *Strategy* section describes.

A function that carries data in its `__dict__` sits between entries 1 and 3.
The list leaves it out.
The type checker reports each [dotted access to such an attribute](17_Techniques--Metaprogramming.md#attributes-on-a-function),
so configuration goes in a closure or a callable object instead.

The *GoF Design Patterns* forms of *Command*, *Strategy*,
and *Chain of Responsibility* all start at number 5.
In the C++ of that book, a class was the lightest form that could carry state.
A function pointer carried none, and closures did not exist yet.
The GoF form then gives that class a named operation, `execute()`,
where a callable object has `__call__()`.
The named operation puts the GoF form at entry 5 rather than entry 4.

## Exercises

Try each exercise before opening its [solution](../Solutions/27_Patterns--Function_Objects/).

1.  Add an "undo" capability to `command.py`.
    What do the commands need to become, and is a function still enough,
    or do you now want an object?
2.  Rewrite `chain.py` so each finder also reports why it failed,
    and `first_root()` prints every attempt before returning the winner.
3.  Use `sorted()` with a `key` function to sort a list of `(name, score)` tuples by score,
    then by name.
    Explain why `key` is the *Strategy* pattern.
4.  Following `bisection_within()`,
    add a `tolerance` parameter to `newton()` in `algorithms.py` and build a configured strategy from it two ways:
    with a closure, and with `functools.partial()`.
    Confirm that `chain.py`'s `first_root()` runs a chain holding either one,
    with no change to `first_root()`.
5.  Because `EventBus.publish()` looks up `type(event)`,
    a subclass of `Deposit` gets the empty default list.
    Change `publish()` to walk `type(event).__mro__` and call every handler registered along it,
    parents last.
    Then add `unsubscribe()`.
    Which of the two changes can break an existing caller, and why?
6.  Build a list of three commands in a `for` loop (not a comprehension)
    with `lambda: print(n)`.
    Call them and explain the output.
    Fix the loop three ways: with a default argument,
    with `functools.partial()`,
    and with a factory function that takes `n` and returns the command.
    Which one still works if you must compute the value at call time rather than at build time?
7.  In `tagged_bus.py`, change `event()` to register `cls` in place of `built`.
    Predict what importing `bank_events.py` then does, and which line stops it.
    Run it to check.
