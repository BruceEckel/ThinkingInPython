# Stateless in Practice

> An Effect states what it needs and how it can fail,
> and something outside it must answer the need and take the failure.
> This chapter writes those answers: Abilities of your own,
> handlers for testing and for production, and the operators that combine them.

[Stateless](46_Effects--Stateless.md)
establishes the two channels an `Effect[A, E, R]` carries.
A dependency is a `Need` that `supply()` answers.
A failure is an exception that `@throws` lifts into the type and `catch()` takes back out.
A type checker verifies that every caller either absorbs an Effect or declares it.

Every Ability so far comes from the library: the `Need` that `supply()` answers,
and the `Async` that `run()` awaits.
This chapter opens by writing an Ability from scratch.
That Ability turns out to be an ordinary class rather than a special form.
The rest of the chapter adds:

- Handlers that make an unpredictable source testable
- A handler that swaps implementations while a program runs
- A cell of shared state that programs read and write through the channel
- A program whose signature is its own documentation,
  and whose body is only the success path
- A failure that enters the channel as a value,
  and a catch that takes the whole channel
- Dependency graphs that go deep, and a cast of actors that goes wide
- Decorators that add retry and parallelism to code they leave as written
- An account of where the guarantee stops

## Abilities Are Not Special

A custom Ability is a request you design.
A `Need` asks for an instance and gets the instance the handler supplies.
Your own Ability asks for anything you can name.
The handler answering it is an ordinary function,
so the answer can differ at every request.

An Ability subclasses `Ability[T]`, where `T` is the type its handler returns.
`Ability` declares no `__slots__`,
so you decorate an Ability that carries fields with [`@record(slots=False)`](18_Techniques--Performance.md#record).
The base gives every instance its `__dict__` back,
and the flag says so at the class.
Here is the Stateless version of `Ask` and `Tell` from [Effect Management](44_Effects--Effect_Management.md#effects-by-hand):

```python
# ask_tell_stateless.py
from record import record
from stateless import Ability, Depend

@record(slots=False)
class Ask(Ability[str]):
    prompt: str

@record(slots=False)
class Tell(Ability[None]):
    message: str

def ask(prompt: str) -> Depend[Ask, str]:
    answer: str = yield from Ask(prompt)
    return answer

def tell(message: str) -> Depend[Tell, None]:
    yield from Tell(message)

def greet() -> Depend[Ask | Tell, None]:
    name = yield from ask("What is your name? ")
    yield from tell(f"Hello, {name}!")
```

A demo answers both requests and runs `greet()`:

```python
# ask_tell_demo.py
from ask_tell_stateless import Ask, Tell, greet
from stateless import handle, run

messages: list[str] = []

def capture(request: Tell) -> None:
    messages.append(request.message)

def scripted(request: Ask) -> str:
    return "Alice"

half = handle(capture)(greet)
full = handle(scripted)(half)
run(full())
print(messages)
#: ['Hello, Alice!']
```

`handle(capture)` builds a handler from `capture`,
the way `supply(Console())` builds one from an instance in [Supplying the Dependency](46_Effects--Stateless.md#supplying-the-dependency).
This chapter calls `capture` and `scripted` the handlers,
since each function is the part you write.

Inside `ask()`, the operand of `yield from` is not a generator but the Ability object.
`yield from` calls `iter()` on its operand,
and `Ability.__iter__` is a generator function,
so the delegation target is an ordinary generator after all.
Stripped of error handling, that method is:

```python
def __iter__(self: Self) -> Generator[Self, T, T]:
    v = yield self
    return v
```

It yields once, so the handler receives one request.
By the [return-channel rule](45_Effects--Generators.md#the-return-channel),
the `yield from` then evaluates to that generator's return value,
which here is the value the handler sent back.
`prompt` is payload on the request, there for the handler to read,
so the answer to an `Ask` is the value `scripted()` returns.
A `Tell` needs no answer,
which is why `Tell` is `Ability[None]` and `capture()` returns `None`.

`ask()` and `tell()` are accessors,
small functions that each wrap one Ability and declare its answer type.
`need()` has the same shape,
and the ZIO listing in [Effect Management](44_Effects--Effect_Management.md#library-effect-management)
has an accessor object doing the same job.
The declared `Depend[Ask, str]` types `name` as `str` inside `greet()`.

You can skip the accessor and write `yield from Ask(...)` inside `greet()`,
and both the program and the type checker still work,
because the checker reads the answer type from `Ask`'s base, `Ability[str]`.
A bare `yield Ask(...)` also runs, since the handler receives the same request,
but the answer then has the type `Any`.
A generator's send type is all the checker knows about a bare `yield`,
and an Effect's send type is `Any`.
With `name` typed `Any`, a mistake such as `name + 1` passes the check.
The accessor gives the request a name and keeps its answer type in one function.
The signature's `Depend[Ask, str]` states that type to callers,
and the `answer: str` binding inside `ask()` states it again.

`ask()`'s return annotation reads `Depend[Ask, str]`,
not `Depend[Need[Ask], str]`.
`Ask` is an Ability, so the channel names it bare,
as [Waiting on a Coroutine](46_Effects--Stateless.md#waiting-on-a-coroutine)
does for `Async`.
`Depend`'s first type parameter has the bound `Ability[Any]`.
That bound makes the bare name more than a convention.
The type checker rejects `Depend[Console, None]` at the annotation,
before it examines any `yield`,
because `Console` is not assignable to `Ability[Any]`.

`handle()` reads the annotation on its argument to decide which Ability it answers,
so `scripted` and `capture` must annotate their parameters.
If you leave the annotation off,
`handle()` raises a `ValueError` at the point of decoration,
since that annotation specifies the type a request must match.

Each `handle()` subtracts one Ability,
so `half` still needs an `Ask` and `full` is ready for `run()`.
Naming the two stages also gives the type checker a place to report what remains,
as [The type checker decides what survives handling](#the-type-checker-decides-what-survives-handling)
shows.

Now compare these two listings to `ask_tell.py` in [Effect Management](44_Effects--Effect_Management.md#effects-by-hand).
The by-hand version puts two objects in every signature.
In the Stateless version, `greet()` has an empty parameter list.
The two Abilities appear in the return type, where a type checker verifies them.
Python's signatures have no third part for Effects,
so the return type carries them,
the job that [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
gives Koka's Effect row.

Each tool in the library is a version of `drive()` from [Generators](45_Effects--Generators.md#a-generator-is-a-description).
An Effect is a generator, so you can drive one yourself,
as `hand_driven.py` in [Nothing Runs Yet](46_Effects--Stateless.md#nothing-runs-yet)
does with that chapter's `greet("Alice")`.
`next()` on that Effect produces a `Need` object carrying the requested type,
the way `interview()` yields `"name"`.
`send(Console())` then answers that request and resumes the body,
which prints the greeting and finishes.
Every tool in the library packages those two calls.
`handle()` is `drive()` with a type lookup in place of the dictionary,
`run()` is that loop applied after the last handler,
and `supply()` is `handle()` prepackaged for `Need`:
a handler whose answer to `Need[T]` is whichever supplied instance is a `T`.

## Scripting an Unpredictable Source

Every handler so far gives the same answer at every request.
`supply()` binds one instance for the whole run,
and `scripted` returns `"Alice"` however many times `greet()` requests a name.
A handler is an ordinary function, so it can answer differently at each request.
Answering differently at each request makes an unpredictable source testable.

### A Coin Toss

Tossing a coin is a side cause.
The program reads something from outside,
and each reading can differ from the last.
If you turn the toss into an Ability, the reading moves into a handler:

```python
# coin_toss.py
import random
from stateless import Ability, Depend, handle, run

class Flip(Ability[bool]):
    pass

def flip() -> Depend[Flip, bool]:
    result: bool = yield from Flip()
    return result

def count_heads(tosses: int) -> Depend[Flip, int]:
    heads = 0
    for _ in range(tosses):
        if (yield from flip()):
            heads += 1
    return heads

script = iter((True, False, True, True, False))

def scripted(request: Flip) -> bool:
    return next(script)

def coin(request: Flip) -> bool:
    return random.random() < 0.5

print(run(handle(scripted)(count_heads)(5)))
#: 3
heads = run(handle(coin)(count_heads)(10_000))
print(4_000 < heads < 6_000)
#: True
```

The body of `count_heads()` does not call `random`,
and no parameter carries a seed or a source.
`Ask` and `Tell` each carry a payload the request delivers,
whereas `Flip`'s whole content is its type and the `bool` it produces.

The parentheses in `if (yield from flip()):` are mandatory.
A `yield` expression can appear on the right side of an assignment,
as a statement of its own, or inside parentheses.
An `if` condition is none of those,
so `if yield from flip():` is a syntax error.

Two handlers feed the same function.
`count_heads()` runs the same code under both,
because either answer arrives through the same `send()` channel.

The scripted handler holds state.
`next(script)` produces a different value at each request,
which one supplied instance cannot do.
Every scripted test double has this shape: a queue handing out canned responses,
a network stub that fails twice and then succeeds,
or the clock in [A Clock That Crosses Midnight](#a-clock-that-crosses-midnight).

That state can fail in one way, and the failure is silent.
`next(script)` raises `StopIteration` once the sequence runs out.
A driver treats `StopIteration` as the signal that an Effect has finished,
so `handle()` treats the exhausted script as the end of the program.
Every other exception a handler raises propagates out of `run()` unchanged.
This one never propagates.
If you ask `count_heads()` for six tosses from this five-value script,
`run()` produces `None` instead of a count, with no exception.
That is the same silent `None` that [An Effect Runs Once](46_Effects--Stateless.md#an-effect-runs-once)
shows for a spent Effect.
If the handler indexes a list rather than walking an iterator,
the mistake becomes an `IndexError` that propagates out of `run()`.

### A Clock

Reading the current time is another side cause.
A real clock answers with the present moment,
so a test cannot set it to some critical time (midnight, or tomorrow).
`stamp()` puts the current time into its output,
and `batch_due()` decides whether a day has passed since the last run.
Against a real clock neither is testable.
`stamp()` produces a different string every minute,
and `batch_due()` needs you to wait a day to watch it return `True`.
Both sit in one file with the Ability and its accessor,
because two more listings and a test ask the same clock different questions:

```python
# timekeeping.py
from datetime import datetime, timedelta
from stateless import Ability, Depend

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment

def stamp(message: str) -> Depend[Now, str]:
    moment = yield from now()
    return f"[{moment:%Y-%m-%d %H:%M}] {message}"

def batch_due(last_run: datetime) -> Depend[Now, bool]:
    moment = yield from now()
    return moment - last_run >= timedelta(hours=24)
```

Like `Flip`, `Now` carries no data.
Its answer type is its whole content.
The handlers decide which moment `stamp()` and `batch_due()` receive:

```python
# frozen_clock.py
from datetime import datetime, timedelta
from typing import Final
from stateless import handle, run
from timekeeping import Now, batch_due, stamp

LAUNCH: Final[datetime] = datetime(2026, 1, 1, 3, 0)

def frozen(request: Now) -> datetime:
    return LAUNCH

def tomorrow(request: Now) -> datetime:
    return LAUNCH + timedelta(hours=24)

print(run(handle(frozen)(stamp)("started")))
#: [2026-01-01 03:00] started
print(run(handle(frozen)(batch_due)(LAUNCH)))
#: False
print(run(handle(tomorrow)(batch_due)(LAUNCH)))
#: True
```

`frozen` reports a single moment over and over,
so `stamp()` produces a known string a test can compare.
`tomorrow` reports a moment a day later,
so `batch_due()` returns `True` at once.
`batch_due()` holds no `datetime.now()` call,
so a test supplies the moment outright.
A production handler that returns `datetime.now()` runs the same function.

Those three runs are claims about testability, so each one becomes a test.
The handler moves inside each test, and every test sets the moment it needs:

```python
# test_timekeeping.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
import pytest
from stateless import handle, run
from timekeeping import Now, batch_due, stamp

MOMENT: Final[datetime] = datetime(2026, 3, 14, 9, 30)

def at(moment: datetime) -> Callable[[Now], datetime]:
    def fixed(request: Now) -> datetime:
        return moment
    return fixed

def test_stamp_names_the_handlers_moment() -> None:
    stamped = run(handle(at(MOMENT))(stamp)("started"))
    assert stamped == "[2026-03-14 09:30] started"

@pytest.mark.parametrize("elapsed, due", [
    (timedelta(hours=23, minutes=59), False),
    (timedelta(hours=24), True),
])
def test_batch_due_at_a_full_day(elapsed: timedelta,
                                 due: bool) -> None:
    moment = MOMENT + elapsed
    is_due = run(handle(at(moment))(batch_due)(MOMENT))
    assert is_due is due
```

A clock from `at()` can report the parametrized reading one minute short of a day,
which a real clock cannot produce on demand.
Against a real clock you must start the test at the right minute,
but here the margin is a `timedelta`.
The tests leave `datetime` as the standard library defines it and run at full speed.
Each assertion compares values the test chose.

### A Clock That Crosses Midnight

Skipping the wait is the obvious benefit of a handled clock.
A handler can also produce moments that are hard to get from a real clock.
Here, `archive()` reads the clock twice,
once to name a file and once to stamp what goes in it:

```python
# midnight.py
from datetime import datetime, timedelta
from typing import Final
from stateless import Depend, handle, run
from timekeeping import Now, now

def archive(entry: str) -> Depend[Now, tuple[str, str]]:
    opened = yield from now()
    path = f"log-{opened:%Y-%m-%d}.txt"
    stamped = yield from now()
    return path, f"[{stamped:%Y-%m-%d}] {entry}"

MIDDAY: Final[datetime] = datetime(2026, 1, 1, 12, 0)
LATE: Final[datetime] = datetime(2026, 1, 1, 23, 59, 59)
ticks = iter([LATE, LATE + timedelta(seconds=2)])

def steady(request: Now) -> datetime:
    return MIDDAY

def crossing(request: Now) -> datetime:
    return next(ticks)

print(run(handle(steady)(archive)("backup ok")))
#: ('log-2026-01-01.txt', '[2026-01-01] backup ok')
print(run(handle(crossing)(archive)("backup ok")))
#: ('log-2026-01-01.txt', '[2026-01-02] backup ok')
```

Under `steady` the two dates agree and the function looks correct.
Under `crossing`, an entry archived as midnight passes ends up in the previous day's file.
The window for the mistake is only as wide as the gap between the two reads.

Using a real clock, you wait for that window and probably miss it.
A test that runs at nine in the morning reads the clock twice on the same date and passes,
so the only evidence is a bug report saying the log file is occasionally short by a few lines.
With the Ability, `archive()` does not read a clock.
It asks for a moment, and a handler chooses which moment that is.
Both handlers answer the same two requests.
They differ in whether midnight falls between the two requests.

`crossing` follows the same pattern as `scripted` in `coin_toss.py`.
It walks a scripted list, so it holds state between requests.
That state lets it answer the same question two ways.
A supplied instance answers every request the same way,
and so do `frozen` and `tomorrow`,
each reporting one moment however often you ask.

### A Source Named in the Type

Compare these handlers to `student_groups.py` in [Functional Toolkits](41_Functional--Toolkits.md#groups-of-any-size),
which makes randomness repeatable a different way, by taking a `seed` parameter.
A `seed` parameter works,
but every function between the caller and the `random.Random` call must declare the parameter and pass it along.
Here the return type names the source.
No signature between `handle()` and the request mentions it.

`Flip` and `Now` are both side causes,
in the vocabulary of [Effect Management](44_Effects--Effect_Management.md#what-is-an-effect):
the function reads something from outside.
The `Recorder` of [Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
covers the other kind, a side effect,
where the function writes something outward.
The technique is the same for both.
Name each contact with the outside as an Ability and bind it at the edge to the implementation the context needs.
An EMS adds one thing: the type checker enforces the declaration.

## Switching Implementations Mid-Run

Every handler so far answers with data: a name, a `bool`, a `datetime`.
A handler can also answer with an implementation,
an object whose methods the program then calls,
and it can choose a different one at each request.
`supply()` cannot do that, because it binds one instance for the whole run.
When a program must change implementations while it runs,
a handler does the choosing.

A building's power supply works this way.
Solar carries the load while the sun is up.
The battery carries it while the charge stays above a threshold.
The utility grid carries it when neither can,
and a diesel backup carries it when the grid is down too.
Each stops for its own reason,
and when one stops the building must obtain another.

Sources are ordinary objects.
Each reports whether it can supply a given hour,
and drawing from a source depletes it:

```python
# power.py
from dataclasses import dataclass
from typing import Protocol
from record import record
from stateless import Ability, Depend, throws

class Drained(Exception):
    pass

class Source(Protocol):
    def available(self, hour: int) -> bool: ...
    def deplete(self) -> None: ...

class Solar:
    def available(self, hour: int) -> bool:
        return 6 <= hour < 19
    def deplete(self) -> None:
        pass

@dataclass
class Battery:
    charge: int
    def available(self, hour: int) -> bool:
        return self.charge >= 20
    def deplete(self) -> None:
        self.charge -= 20

@dataclass
class Grid:
    outage: range
    def available(self, hour: int) -> bool:
        return hour not in self.outage
    def deplete(self) -> None:
        pass

@dataclass
class Backup:
    fuel: int
    def available(self, hour: int) -> bool:
        return self.fuel > 0
    def deplete(self) -> None:
        self.fuel -= 1

@record(slots=False)
class Outlet(Ability[Source]):
    hour: int

def plug(hour: int) -> Depend[Outlet, Source]:
    source: Source = yield from Outlet(hour)
    return source

@throws(Drained)
def draw(source: Source, hour: int) -> None:
    if not source.available(hour):
        raise Drained(type(source).__name__)
    source.deplete()
```

An `Outlet` request carries the hour so the handler can check which sources are available at that hour.
`Ask` carries a prompt for the same reason.

`Source` carries no `@runtime_checkable`,
because the listings name `Source` in annotations and in `Outlet`'s base,
with no `isinstance()` check on it.
`supply()` needs that decorator,
because it [matches an instance to a requested class](46_Effects--Stateless.md#supplying-an-interface)
with `isinstance()`.
Here `handle()` matches on the Ability's own type, `Outlet`.
The `Source` that comes back is only a return value.

`draw()` is the lifting wrapper.
`@throws` lifts the `Drained` it raises into the error channel.

Here are the consumer and the handler that feeds it:

```python
# microgrid.py
from collections.abc import Callable, Generator
from contextlib import contextmanager
from power import Drained, Outlet, Source, draw, plug
from stateless import Depend, catch

class Blackout(Exception):
    pass

def controller(
    order: tuple[Source, ...],
) -> Callable[[Outlet], Source]:
    def choose(request: Outlet) -> Source:
        for source in order:
            if source.available(request.hour):
                return source
        raise Blackout(request.hour)
    return choose

@contextmanager
def connected(source: Source) -> Generator[Source]:
    name = type(source).__name__
    print(f"{name} online")
    try:
        yield source
    finally:
        print(f"{name} offline")

def run_load(start: int,
             hours: int) -> Depend[Outlet, None]:
    caught = catch(Drained)
    hour, remaining = start, hours
    while remaining:
        source = yield from plug(hour)
        with connected(source) as power:
            while remaining:
                failure = yield from caught(draw)(
                    power, hour)
                if failure is not None:
                    break
                print(f"  {hour}:00")
                hour += 1
                remaining -= 1
```

`draw()` returns `None` on success,
so anything else in `failure` is the `Drained` that ends the inner loop.
The outer loop then calls `plug()` again for a replacement.
The `break` leaves `hour` unchanged,
so the replacement supplies the hour the failed source refused.

`connected()` is an ordinary context manager,
and its `with` block sits inside the generator body.
Acquiring and releasing within one Effect works,
since the block opens and closes between two `yield from` expressions in the same function.
Stateless provides no way to acquire a resource in one Effect and release it after a later Effect finishes.
[Running Effects in Parallel](#running-effects-in-parallel) revisits that limit.

One thing stays outside the types.
`choose()` raises a `Blackout` when no source can supply the hour,
and that is ordinary code raising an ordinary exception.
No `@throws` lifts it,
so it propagates out of `run()` and no signature mentions it.
`catch()` matches values an Effect yields.
A handler runs in the driver, outside the Effect,
so the `Blackout` propagates past a `catch()` around this program.

The `Blackout` also leaves `run_load()` suspended at its `plug()` request,
since the exception propagates out through `handle()` and bypasses the generator.
In this program the `with` block has closed by then,
because `plug()` sits outside it.
If a handler raises an exception while a `with` block is open,
that block's exit waits until Python reclaims the abandoned generator.
The reclaiming can come after the `except` clause that handled the exception has finished.

```python
# microgrid_demo.py
from microgrid import controller, run_load
from power import Backup, Battery, Grid, Solar
from stateless import handle, run

def site() -> tuple[Solar, Battery, Grid, Backup]:
    return (Solar(), Battery(40), Grid(range(22, 24)),
            Backup(3))

solar, battery, grid, backup = site()
sun_first = controller((solar, battery, grid, backup))
run(handle(sun_first)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Battery online
#:   19:00
#:   20:00
#: Battery offline
#: Grid online
#:   21:00
#: Grid offline
#: Backup online
#:   22:00
#: Backup offline
solar, battery, grid, backup = site()
battery_first = controller((battery, solar, grid, backup))
run(handle(battery_first)(run_load)(17, 4))
#: Battery online
#:   17:00
#:   18:00
#: Battery offline
#: Grid online
#:   19:00
#:   20:00
#: Grid offline
```

`run_load()` draws from whichever source `plug()` hands it,
so the second run prints a different trace from the same code.
Apart from their lengths,
the two runs differ only in the order of the tuple passed to `controller()`.
`controller()` sets the priority,
the sources hold the thresholds and the outage schedule,
and `run_load()` decides when to stop drawing from the source it holds.

The load's declared dependency stays the same.
`Depend[Outlet, None]` says it needs an `Outlet` from the first hour to the last,
and that type appears once.
The object answering the need changes:
four objects in turn during the first run.
A dependency bound before the program starts gives one answer for the whole run.
Here the source that can supply the load changes with the hour.
In `microgrid.py` the binding is a call to `choose()`,
which checks each source's `available()` at each request.
[Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
swaps an implementation between runs.
`microgrid.py` swaps one during a run.
The consumer names no source, so its code stays the same.

## State as an Ability

Each Ability so far moves information in one direction.
`Flip` and `Now` read from outside, so they are side causes.
`Tell` writes outward, so it is a side effect.
Shared mutable state is both at once,
because whoever holds it must read it and write it back.
An Ability declares one answer type,
so a cell of state becomes a pair of Abilities.
Reading answers with the stored value,
and writing carries a new value and answers with `None`.

```python
# wallet.py
from collections.abc import Callable
from dataclasses import dataclass
from record import record
from stateless import Ability, Depend

class Get(Ability[int]):
    pass

@record(slots=False)
class Put(Ability[None]):
    amount: int

def get() -> Depend[Get, int]:
    amount: int = yield from Get()
    return amount

def put(amount: int) -> Depend[Put, None]:
    yield from Put(amount)

def purchase(price: int) -> Depend[Get | Put, bool]:
    funds = yield from get()
    if funds < price:
        return False
    yield from put(funds - price)
    return True

def spree(prices: tuple[int, ...]) -> Depend[
    Get | Put, int
]:
    bought = 0
    for price in prices:
        if (yield from purchase(price)):
            bought += 1
    return bought

@dataclass
class Cell:
    amount: int

def ledger(cell: Cell) -> tuple[
    Callable[[Get], int], Callable[[Put], None]
]:
    def read(request: Get) -> int:
        return cell.amount
    def write(request: Put) -> None:
        cell.amount = request.amount
    return read, write
```

`Get` has `Flip`'s shape: no payload, and the answer type is its whole content.
`Put` has `Tell`'s shape: payload out, `None` back.
`purchase()`'s comparison sits between the two requests,
in code that mentions no cell.

`purchase()`'s signature declares the shared state.
`Depend[Get | Put, bool]` tells a caller this function reads or writes something that outlives it.

The handlers own the cell.
`ledger()` builds `read()` and `write()` from one `Cell`,
the way `at()` builds a clock from a moment.

A test calls `ledger()` on a `Cell` of its own,
chains the pair through the named stages of [Abilities Are Not Special](#abilities-are-not-special),
and asserts on the count `spree()` returns and on what that cell holds afterward:

```python
# test_wallet.py
from stateless import handle, run
from wallet import Cell, ledger, spree

def test_spree_spends_from_the_tests_cell() -> None:
    cell = Cell(100)
    read, write = ledger(cell)
    half = handle(read)(spree)
    shop = handle(write)(half)
    assert run(shop((60, 50, 30, 20))) == 2
    assert cell.amount == 10
```

Each test builds its own cell and asserts on that cell,
so two tests can run in either order.

When one function owns a number, a local variable is the right tool,
and `count_heads()` keeps its count in one.
The pair of Abilities serves separate functions that share the cell,
such as `purchase()` and any other spender.
No parameter carries the cell through the signatures between them.

Treatments of algebraic effects open with this pattern and name it the *State effect*,
with `get` and `put` as its two operations.
`wallet.py` builds that effect from two `Ability` subclasses and the two handlers `ledger()` returns.

No lock protects the cell.
Forking two Effects that share a `Cell` interleaves their reads and writes,
so the two Effects race on the cell the way two threads race on a Python global.
No type reports the race.
ZIO's `Ref` is this cell with atomic update built in.
Stateless has no equivalent.

## Composing a Program

This small application takes three steps: it fetches a headline,
it finds a topic worth researching within that headline,
and it looks up that topic.
Each step needs something or can fail, and no step specifies an implementation:

```python
# research.py
from typing import Final, Protocol, runtime_checkable
from stateless import Effect, Need, need, throws

class Unavailable(Exception):
    pass

class NotInteresting(Exception):
    pass

class NoArticle(Exception):
    pass

@runtime_checkable
class Feed(Protocol):
    def latest(self) -> str: ...

@runtime_checkable
class Encyclopedia(Protocol):
    def article(self, topic: str) -> str: ...

TOPICS: Final[tuple[str, ...]] = ("stock market", "genome")

@throws(Unavailable)
def fetch(feed: Feed) -> str:
    return feed.latest()

@throws(NotInteresting)
def topic_of(headline: str) -> str:
    for candidate in TOPICS:
        if candidate in headline:
            return candidate
    raise NotInteresting(headline)

@throws(NoArticle)
def look_up(book: Encyclopedia, topic: str) -> str:
    return book.article(topic)

def research() -> Effect[
    Need[Feed] | Need[Encyclopedia],
    Unavailable | NotInteresting | NoArticle,
    str,
]:
    feed = yield from need(Feed)
    headline = yield from fetch(feed)
    topic = yield from topic_of(headline)
    book = yield from need(Encyclopedia)
    article = yield from look_up(book, topic)
    return article
```

The `research()` signature declares what the program needs and how it can fail.
Within `research()`,
the signature is also the only place the three failures appear.
The body requests each dependency by its type and leaves the network, the files,
and the printing to the implementations you supply.
Calling `research()` performs no work.

The three `@throws` functions are the pattern for bringing ordinary code in.
`fetch()` and `look_up()` call ordinary methods rather than Effects,
and the decorator lifts what they raise into the channel.
`topic_of()` computes its answer from its argument and a module constant,
so it declares no Ability.

`fetch()` and `look_up()` take their dependencies as parameters,
so they are ordinary functions rather than generator functions.
Taking dependencies as parameters is a choice, not a requirement.
`@throws` also decorates a generator function,
so one function can make the request and declare the failure:

```python
# fetch_effectful.py
from research import Feed, Unavailable
from stateless import Depend, Need, need, throws

@throws(Unavailable)
def fetch_headline() -> Depend[Need[Feed], str]:
    feed = yield from need(Feed)
    return feed.latest()
```

The decorator adds `Unavailable` to the yield type,
as it adds `KeyError` for `score()` in [The Error Channel](46_Effects--Stateless.md#the-error-channel).
`ty` reports `fetch_headline` as `() -> Generator[Need[Feed] | Unavailable, Any, str]`,
which is `Effect[Need[Feed], Unavailable, str]`.

`research.py` keeps the request and the failure in separate functions for two reasons.
A function that receives everything it uses as arguments is easier to test on its own,
and the split keeps the Ability requests in one place.
Either shape type-checks, and either puts `Unavailable` in the error channel.

Two feeds and an encyclopedia implement the two Protocols,
and four named instances serve the scenarios that follow:

```python
# newswire.py
from typing import Final
from record import record
from research import NoArticle, Unavailable

@record
class Wire:
    headline: str
    def latest(self) -> str:
        print("feed: fetching")
        return self.headline

class DeadWire:
    def latest(self) -> str:
        raise Unavailable("offline")

@record
class Library:
    articles: dict[str, str]
    def article(self, topic: str) -> str:
        print(f"library: looking up {topic}")
        if topic not in self.articles:
            raise NoArticle(topic)
        return self.articles[topic]

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library(
    {"stock market": "a history"})
EMPTY: Final[Library] = Library({})
```

`Wire` and `Library` are structural implementations,
so `supply(Wire(...), Library(...))` builds handlers for `Need[Wire]` and `Need[Library]` rather than for the two Protocols.
[Supplying an Interface](46_Effects--Stateless.md#supplying-an-interface)
resolves that mismatch with `as_type()`.

Now supply `research()`'s environment:

```python
# scenarios.py
from typing import assert_never
from newswire import EMPTY, SHELF, STOCKS, WEATHER, DeadWire
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
from stateless import Depend, Need, catch, run, supply

def report() -> Depend[
    Need[Feed] | Need[Encyclopedia], str
]:
    caught = catch(Unavailable, NotInteresting, NoArticle)
    found: str | Unavailable | NotInteresting | NoArticle
    found = yield from caught(research)()
    match found:
        case Unavailable():
            return "no headline today"
        case NotInteresting():
            return "nothing worth researching"
        case NoArticle():
            return "no article on that topic"
        case str():
            return found
        case _:
            assert_never(found)

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))  # [1]
#: feed: fetching
#: library: looking up stock market
#: a history
print(outcome(WEATHER, SHELF))  # [2]
#: feed: fetching
#: nothing worth researching
print(outcome(STOCKS, EMPTY))  # [3]
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
print(outcome(DeadWire(), SHELF))  # [4]
#: no headline today
```

The four runs of one program differ only in what you supply.
The run at `[1]` finds its article.
The run at `[2]` exercises `NotInteresting`, `[3]` exercises `NoArticle`,
and `[4]` exercises `Unavailable`,
so the runs cover every failure the signature declares.
[Effect Oriented Programming](https://effectorientedprogramming.com/)
calls each such set of bindings a *scenario*.
Here a scenario is nothing more than arguments to `supply()`.

Each run's last line is the outcome that `report()` returns.
Every line above it comes from a supplied implementation,
because the pipeline leaves every `print()` to the implementations you supply.
Those lines therefore record where each run stopped.
The run at `[2]` stops after `feed: fetching`.
`topic_of()` yields a `NotInteresting`,
and `research()` stops at that `yield from`.
The stop comes before the `need(Encyclopedia)` on the next line,
and so before any call to `Library.article()`.
`catch()` receives that failure and `report()` matches on it as a value,
which is why the run still prints a message.
A failure ends the remaining steps the way a raised exception does,
and no step tests for it.
Where the run stops depends on where the failure arises.
The run at `[4]` prints its outcome alone,
since `DeadWire.latest()` raises `Unavailable` where `Wire.latest()` prints `feed: fetching`.

`report()` handles the two channels differently.
`catch()` empties the error channel, so `report()` cannot fail.
`report()` still declares both Abilities,
because `catch()` acts on the error channel and leaves the Ability channel as it was.
If you annotate `report()` as `Success[str]`,
the type checker names the `yield from` that still carries `Need[Feed] | Need[Encyclopedia]`.
`supply()` empties that half, and `run()` accepts what remains.

Declaring `outcome()`'s parameters as `Feed` and `Encyclopedia` upcasts the two implementations at the boundary,
as `as_type()` would, without a cast.

## The Success Path

`research()` handles no errors.
Its body is a straight run of six lines, each calling the next step,
and no line tests whether the previous one worked.
The error channel makes that straight run possible.
Here is the same pipeline with the failures handled where they arise:

```python
# research_by_hand.py
from research import (TOPICS, Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable)

def topic_of(headline: str) -> str:
    for candidate in TOPICS:
        if candidate in headline:
            return candidate
    raise NotInteresting(headline)

def research_and_report(
    feed: Feed, book: Encyclopedia
) -> str:
    try:
        headline = feed.latest()
    except Unavailable:
        return "no headline today"
    try:
        topic = topic_of(headline)
    except NotInteresting:
        return "nothing worth researching"
    try:
        return book.article(topic)
    except NoArticle:
        return "no article on that topic"
```

`topic_of()` appears again in full because `research.py`'s version carries a decorator.
The decorated version returns an Effect.
Ordinary `try`/`except` code that calls it gets that Effect back in place of a topic.

Three lines of work sit inside nine lines of handling.
The pipeline is in there, spread across three `try` blocks.
The Effect version moves those nine lines into `report()`,
one `match` over the failures instead of a `try` at each step.
The name `research_and_report()` records the merge the by-hand version forces:
`research()` and `report()` in one function.

Both versions short-circuit.
The by-hand one returns early.
The Effect one stops at the failure, and the driver never resumes the generator.
The difference is who writes the branch that short-circuits.

At this size the by-hand version is respectable, and a reader may prefer it.
Two differences hold at any size.
The by-hand signature, `(Feed, Encyclopedia) -> str`,
mentions none of the three failures,
so adding a fourth failure leaves the signature as it is.
And the handling interleaves with the logic.
`research_and_report()` decides both what to do about a failure and what to say about it.
The Effect version separates the handling from the logic,
so a second caller can catch the same three failures and choose different messages,
retry the whole pipeline, or let one failure through to the edge,
while the pipeline stays as written.

## A Second Way In and Out

The error channel you have seen has one way in and one way out.
`@throws` lifts what ordinary code raises,
and `catch()` takes named errors back out as values.
The library provides a second of each.

### Failing from Inside an Effect

`throw()` is the counterpart of `success()`.
Where `success(value)` builds a description that produces a value,
`throw(reason)` builds one that fails.
Its type is `Try[E, Never]`,
the [`Try` alias](46_Effects--Stateless.md#the-effect-type),
with `Never` recording that no value can come out of it.
`yield from` sends that failure into the channel of the Effect that contains it:

```python
# fetch_guarded.py
from newswire import Wire
from research import Feed, Unavailable, fetch
from stateless import (Effect, Need, catch, need, run,
                       supply, throw)

class Empty(Exception):
    pass

def fetch_nonempty() -> Effect[
    Need[Feed], Unavailable | Empty, str
]:
    feed = yield from need(Feed)
    headline = yield from fetch(feed)
    if not headline:
        yield from throw(Empty())
    return headline

def edge(feed: Feed) -> str | Unavailable | Empty:
    guarded = catch(Unavailable, Empty)(fetch_nonempty)
    return run(supply(feed)(guarded)())

print(edge(Wire("markets close mixed")))
#: feed: fetching
#: markets close mixed
print(type(edge(Wire(""))).__name__)
#: feed: fetching
#: Empty
```

`fetch_nonempty()` can fail either way.
`Unavailable` originates in ordinary code.
`latest()` raises it, and the `@throws` on `fetch()` lifts it.
`Empty` originates here, in the generator,
where the headline is available to inspect.
The generator yields that failure as a value rather than raising it,
so no decorator takes part.
`throw(Empty())` yields the failure the way `Ask(prompt)` yields a request,
and the driver receives it.
Execution stops there.
A driver that receives a failure stops sending,
so anything after a `yield from throw(...)` is unreachable.
The `Never` in `throw()`'s type records that.

The difference between the two ways in is what the type checker verifies.
If you change `Empty()` to some undeclared exception,
the checker reports an error at that `yield from`,
because the yielded type falls outside the declared channel.
That error is the `invalid-yield` that [Dependencies That Need Dependencies](#dependencies-that-need-dependencies)
shows in full.
A `raise` gets no such check.
`@throws` lifts the types it specifies.
Anything else propagates untracked.
No diagnostic connects the decorator's list to what the body raises.
A failure that enters through `throw()` is in the type system from the moment it exists.

### Catching the Whole Channel

`catch()` names what it takes.
`catch_all()` takes what the channel declares:

```python
# catch_everything.py
from newswire import EMPTY, SHELF, STOCKS, WEATHER
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
from stateless import run, supply
from stateless.effect import catch_all

def outcome(
    feed: Feed, book: Encyclopedia
) -> str | Unavailable | NotInteresting | NoArticle:
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(WEATHER, SHELF)
#: feed: fetching
print(type(dull).__name__)
#: NotInteresting
missing = outcome(STOCKS, EMPTY)
#: feed: fetching
#: library: looking up stock market
print(type(missing).__name__)
#: NoArticle
```

`outcome()` is the boundary function `scenarios.py` uses,
with the same upcasting annotations.
Its result type is the union `report()` builds by listing all three errors.
This listing specifies none of them at the catch.
The two calls repeat the `NotInteresting` and `NoArticle` runs of `scenarios.py`.
Where `report()` turns those failures into messages,
`catch_all()` returns them as values.

`outcome()` supplies first and catches second, the reverse of `scenarios.py`.
Both the runtime and the type checker accept either order.
A handler passes error values to its caller unchanged,
so `supply()`'s driver relays the failures to the catch either way.
Under `ty` 0.0.91 both orders infer the same result type.
The Ability channel is where the orders differ.
`supply(feed, book)(catch_all(research))` comes back with `Never` there,
and `catch_all(supply(feed, book)(research))` with `Unknown`:
the same two calls in the other order.
`bound` has a name so that you can reveal its type on its own.
[The type checker decides what survives handling](#the-type-checker-decides-what-survives-handling)
explains the difference.

`catch()` and `catch_all()` differ in what they do with a new failure.
When `research()` gains a fourth error,
`report()`'s named `catch()` leaves it in the channel,
so `report()`'s declared type no longer matches and the type checker reports an error at the `yield from`.
You decide whether to catch the newcomer or declare it.
`catch_all()` absorbs it into the result union,
so the guard must be code that reads the result:
an annotation that writes the union out, as `outcome()`'s return type does,
or a `match` that ends with `assert_never()`.
Without such a guard,
the new failure becomes a value that reaches the caller unexamined.
`catch()` makes each failure a decision the source states.
`catch_all()` decides for all of them at once.

Two cautions.
`catch_all()` comes from `stateless.effect`,
since the package root does not export it.
And `catch_all()` has the reach of `catch()`.
It matches the failures `@throws` lifted into the channel.
An unlifted failure propagates past it as it does past `catch()`.

## Dependencies That Need Dependencies

`research()` asks for two things, and both are leaves.
A `Feed` or an `Encyclopedia` is ready to supply as soon as you construct it.
Real graphs nest.
Toast needs bread and a toaster, and bread needs dough and an oven.

```python
# bakery.py
from record import record
from stateless import Depend, Need, need, run, supply

@record
class Dough:
    flour: str
    def risen(self) -> str:
        print("dough: risen")
        return f"{self.flour} dough"

@record
class Oven:
    celsius: int
    def bake(self, dough: str) -> str:
        print(f"oven: baking at {self.celsius}")
        return f"loaf of {dough}"

@record
class Toaster:
    setting: int
    def brown(self, loaf: str) -> str:
        print(f"toaster: setting {self.setting}")
        return f"toasted {loaf}"

def bread() -> Depend[Need[Dough] | Need[Oven], str]:
    dough = yield from need(Dough)
    oven = yield from need(Oven)
    return oven.bake(dough.risen())

def toast() -> Depend[
    Need[Dough] | Need[Oven] | Need[Toaster], str
]:
    loaf = yield from bread()
    toaster = yield from need(Toaster)
    return toaster.brown(loaf)

kitchen = supply(Dough("rye"), Oven(220), Toaster(3))
print(run(kitchen(toast)()))
#: dough: risen
#: oven: baking at 220
#: toaster: setting 3
#: toasted loaf of rye dough
```

You supply leaves and make products.
The listing keeps the two apart.
`Dough`, `Oven`, and `Toaster` are the leaves,
so `supply()` binds one instance of each.
The loaf is a product.
`bread()` is an Effect that produces a loaf,
so `toast()` obtains one by writing `yield from bread()` rather than by asking for a `Need[Bread]`.
The loaf stays out of `supply()`, because `bread()` bakes it later,
while `run()` drives `toast()`.

The signature carries the graph, flattened into a union.
`toast()` declares all three leaves although its body requests one of them.
`yield from bread()` carries `Need[Dough]` and `Need[Oven]` from the inner Effect into `toast()`'s channel,
the way `yield from` relays each value the inner generator yields.
The type checker enforces that union.
If you declare `toast()` with `Need[Toaster]` alone,
`ty` reports an error at the delegation:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> bakery.py:34:23
   |
31 |   def toast() -> Depend[
   |  ________________-
32 | |     Need[Toaster], str
33 | | ]:
   | |_- Function annotated with yield type
   |     `Need[Toaster]` here
34 |       loaf = yield from bread()
   |                         ^^^^^^^ expression of type
   |                         `Need[Dough] | Need[Oven]`,
   |                         expected `Need[Toaster]`
```

The type checker verifies the other end too.
If you leave `Oven(220)` out of `supply()`,
the checker rejects the `run()` call,
finding a `Generator[Need[Oven], Any, str]` where it expected a yield channel holding only `Async` and errors.
That is the rejection [Forgetting to Supply](46_Effects--Stateless.md#forgetting-to-supply)
shows, now arising from a dependency two levels down.

`Oven` and `Toaster` are distinct types,
so the ambiguity of [When Two Implementations Match](46_Effects--Stateless.md#when-two-implementations-match)
cannot arise here.
[Effect Oriented Programming](https://effectorientedprogramming.com/)
builds this same toast in ZIO, where both appliances are a `HeatSource`,
so ZIO must report the clash.

Here is what ZIO does that Stateless cannot.
In that book's version, `Bread.homeMade` is a `ZLayer`:
a constructor that is an Effect.
It can print, it can fail, and you can retry it.
The compiler resolves it into a tree with `Oven` and `Dough` beneath it.
You provide that layer rather than a finished loaf.
Stateless has no such thing.
`supply()` matches instances that exist,
and `handle()` answers an Ability with an ordinary function,
so a constructor cannot be an Effect.
That is why `bakery.py` has the shape it has.
Leaves bind at the edge, products come from a `yield from` in the body,
and the graph you can read is the union in the signature.

## Supplying a Whole Cast

The bakery graph goes deep,
with two of its three leaves reached through `bread()`.
The next example goes wide.
[Abstract Factories](26_Patterns--Factory.md#abstract-factories)
builds a gaming environment where a `GameElementFactory` returns a matched `Character` and `Obstacle`,
and a `GameEnvironment` plays the elements that factory produces.
Here each kind of actor is a type the program requests through a `Need`:

```python
# quest.py
from typing import Protocol, runtime_checkable
from stateless import Depend, Need, need

@runtime_checkable
class Narrator(Protocol):
    def say(self, line: str) -> None: ...

@runtime_checkable
class Hero(Protocol):
    def name(self) -> str: ...
    def approach(self, obstacle: str) -> str: ...

@runtime_checkable
class Obstacle(Protocol):
    def blocks(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator] | Need[Hero] | Need[Obstacle], None
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    obstacle = yield from need(Obstacle)
    narrator.say(f"{hero.name()} arrives")
    narrator.say(hero.approach(obstacle.blocks()))
```

`encounter()` holds all the engine's logic.
It constructs no `GameEnvironment`, holds no factory,
and mentions only the three Protocols.
Output is a requested type like `Hero` and `Obstacle`.
`Narrator` is one of the three requests,
so the code that supplies it chooses whether a line prints, goes into a list,
or disappears.
As [Retrofitting an Effect](46_Effects--Stateless.md#retrofitting-an-effect)
recommends, the union appears in full rather than as an alias.

The cast is a set of ordinary classes that inherit nothing:

```python
# casts.py
from quest import Hero, Narrator, Obstacle, encounter
from stateless import run, supply

class Kitty:
    def name(self) -> str: return "Kitty"
    def approach(self, obstacle: str) -> str:
        return f"and bats at the {obstacle}"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Warrior:
    def name(self) -> str: return "Warrior"
    def approach(self, obstacle: str) -> str:
        return f"and battles the {obstacle}"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

def play(
    narrator: Narrator, hero: Hero, obstacle: Obstacle
) -> None:
    cast = supply(narrator, hero, obstacle)
    run(cast(encounter)())

def kitties_and_puzzles(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle())

def warriors_and_weapons(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon())
```

`play()` is the boundary function of [Composing a Program](#composing-a-program).
Its annotations do the upcasting,
so each actor reaches `supply()` as its Protocol type,
the job `as_type()` does elsewhere.
Its body is the one place in the program that binds an implementation to an Ability.

Each requested type needs a shape of its own.
You could rename `Obstacle.blocks()` to `name()`, which `Hero` declares too.
`Hero` stays distinct, since it also declares `approach()`.
But every hero then satisfies `Obstacle` as well.
`play()` supplies the hero first,
so the hero answers the request for an obstacle.
When two Protocols have matching methods,
argument order decides which request each implementation answers.
That is the ambiguity of [When Two Implementations Match](46_Effects--Stateless.md#when-two-implementations-match).

`kitties_and_puzzles()` and `warriors_and_weapons()` are what the two concrete factories became.
Each was a class with a method per product.
Each is now a function that hands `play()` a matched set.
No parallel hierarchy remains.
`Kitty` and `Puzzle` match the `Hero` and `Obstacle` Protocols by structure,
and the engine works with the three Protocols alone:

```python
# two_games.py
from dataclasses import dataclass, field
from casts import (Kitty, Weapon, kitties_and_puzzles, play,
                   warriors_and_weapons)

class Loud:
    def say(self, line: str) -> None: print(line)

@dataclass
class Script:
    lines: list[str] = field(default_factory=list)
    def say(self, line: str) -> None:
        self.lines.append(line)

kitties_and_puzzles(Loud())
#: Kitty arrives
#: and bats at the puzzle
warriors_and_weapons(Loud())
#: Warrior arrives
#: and battles the nasty weapon
play(Loud(), Kitty(), Weapon())
#: Kitty arrives
#: and bats at the nasty weapon
script = Script()
kitties_and_puzzles(script)
print(script.lines)
#: ['Kitty arrives', 'and bats at the puzzle']
```

`Script` records what arrives,
so a test reads the lines back as a list with no `capsys` and no monkeypatching.
The engine holds no printing to intercept.
`test_greeter.py` in [Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
makes the same swap with one Ability rather than three.

### The Unmatched Cast

The third run mixes the casts.
The unmatched cast type-checks, and it runs.
That is a loss compared with the *Abstract Factory*,
whose purpose is families of matched products.
`KittiesAndPuzzles.make_obstacle()` cannot return a `Weapon`,
because the class defines the pairing.
`supply()` takes a flat list and checks each argument against one requested type,
not against the others.
You recover the matched set by writing it down in a function,
as `kitties_and_puzzles()` does.
The guarantee moves from a class hierarchy into a two-line function.

### The Nine-Argument Ceiling

One `supply()` call can type-check at most nine actors.
`supply()`'s declaration carries overloads for one through nine values,
so a tenth argument matches none of them:

```text
error[no-matching-overload]: No overload of function `supply`
matches arguments
```

The call still runs and binds all ten actors,
since the implementation is variadic,
but the type checker no longer verifies the call.
Two chained handlers keep the checking.
[Layering Handlers](46_Effects--Stateless.md#layering-handlers)
shows how to chain them.
Each `supply()` in the chain stays within nine actors.
An Effect that asks for ten separate things is usually two Effects.

## Adding Behavior to an Existing Effect

[The Success Path](#the-success-path)
says that a caller can retry a pipeline without editing it.
Stateless provides a few decorators that add such behavior.
Retry is the one to study, because of what it does to the type.

### `retry()` and a Flaky Database

`Database` fails a set number of times before working,
so the example is repeatable:

```python
# flaky.py
from dataclasses import dataclass
from stateless import Effect, Need, need, throws

class Crashed(Exception):
    pass

@dataclass
class Database:
    failures: int
    attempts: int = 0
    def save(self, user: str) -> str:
        self.attempts += 1
        print(f"attempt {self.attempts}")
        if self.attempts <= self.failures:
            raise Crashed("database crashed")
        return f"{user} saved"

@throws(Crashed)
def store(db: Database, user: str) -> str:
    return db.save(user)

def save_user(user: str) -> Effect[
    Need[Database], Crashed, str
]:
    db = yield from need(Database)
    result = yield from store(db, user)
    return result
```

`retry(schedule: Schedule[A])` builds a decorator for a function that returns an Effect:

```python
# retrying.py
from datetime import timedelta
from flaky import Crashed, Database, save_user
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

once = catch(Crashed)(save_user)
print(run(supply(Database(failures=2))(once)("Morty")))
#: attempt 1
#: database crashed
three = recurs(3, spaced(timedelta(milliseconds=1)))
retried = retry(three)(save_user)
print(run(
    supply(Database(failures=2), Time())(retried)("Morty")))
#: attempt 1
#: attempt 2
#: attempt 3
#: Morty saved
caught = catch(RetryError)(retried)
outcome = run(
    supply(Database(failures=9), Time())(caught)("Morty"))
#: attempt 1
#: attempt 2
#: attempt 3
match outcome:
    case RetryError():
        print(type(outcome).__name__, len(outcome.args[0]))
#: RetryError 3
```

The first run is the baseline: one attempt, no retry, and it fails.
`three` comes from the only two schedule combinators the library has.
`spaced()` yields the same interval forever,
and `recurs()` stops it after `n` yields.
`save_user()` stays as written through all of it.

`retry()` decorates the function `save_user`,
not the Effect `save_user("Morty")`,
for the reason [An Effect Runs Once](46_Effects--Stateless.md#an-effect-runs-once)
gives.
The Effect is a generator, one `run()` spends it,
and only the function can build a second description.

### What Retry Cannot Judge

Read the trace before you use `retry()` on real code.
Each attempt line is `Database.save()` running again,
so the decorated function runs its whole body once per attempt.
Retrying a charge or an append duplicates it.
Whether a retry is safe lies outside the type,
because `Effect[A, E, R]` tracks what a function needs and how it fails,
not whether running it twice means the same as running it once.
That judgment stays with you.

`retry()` is also all-or-nothing over the error channel.
Its body catches every declared error and retries on any of them,
with no way to specify the ones worth another attempt.
Retrying `research()` with the `WEATHER` feed of [Composing a Program](#composing-a-program)
shows the problem.
A `WEATHER` headline names no known topic,
so `topic_of()` raises `NotInteresting` on every attempt, deterministically.
`retry()` treats that failure like one worth retrying.
Three attempts fetch the headline three times and collect three identical `NotInteresting` errors in the `RetryError`.
Retry what can change between attempts,
and let `catch()` take a deterministic failure out before it reaches `retry()`.

### What Retry Does to the Signature

`save_user()` is `(str) -> Effect[Need[Database], Crashed, str]`.
Under `reveal_type()`, `retried` is:

```text
(user: str) -> Generator[
    Need[Database] | Need[Time] | Async | RetryError[Crashed],
    Any,
    str,
]
```

`retry()` changes the signature in three visible ways.
The error becomes `RetryError[Crashed]`,
which is why the third run catches `RetryError` rather than `Crashed`.
`Async` appears because waiting between attempts is asynchronous.
And `Need[Time]` appears, which is why `supply()` gains a `Time()`.
Retrying needs a clock, and the signature says so.
If you leave the `Time()` out, the type checker rejects the `run()` call.

The added `Need[Time]` is the thesis of both chapters applied to a cross-cutting concern.
In a system with untracked Effects,
adding retry to a hundred call sites changes no signature.
Here adding retry changes a type.
Every caller that runs the retried function without a `Time` fails the check.

The renamed error allows a mistake the type checker accepts.
If you write `catch(Crashed)(retried)`, catching the original error,
the checker accepts the call.
The result type gains a `Crashed` branch that cannot occur,
while `RetryError[Crashed]` stays in the error channel.
At runtime the failure propagates past the useless `catch()` and out of `run()`.
`catch()` must specify what the channel holds at the point of decoration,
and after `retry()` that is `RetryError[Crashed]`, not `Crashed`.

The library leaves one gap here.
`RetryError` declares an `errors` attribute,
but `retry()` builds one as `RetryError(tuple(errors))`,
which leaves that attribute unset.
The collected failures therefore sit in `outcome.args[0]`,
and `outcome.errors` raises `AttributeError`.
The third run counts them there,
after the `match` narrows `outcome` from `str | RetryError` to the error.

### `repeat()` and `memoize()`

`repeat()` is the sibling that runs an Effect on a schedule and collects every result:

```python
# repeating.py
from datetime import timedelta
from flaky import Database, save_user
from stateless import repeat, run, supply
from stateless.schedule import recurs, spaced
from stateless.time import Time

three = recurs(3, spaced(timedelta(milliseconds=1)))
repeated = repeat(three)(save_user)
env = supply(Database(failures=0), Time())
print(run(env(repeated)("Morty")))
#: attempt 1
#: attempt 2
#: attempt 3
#: ('Morty saved', 'Morty saved', 'Morty saved')
```

The same schedule that governed three attempts now governs three runs,
and the tuple holds every result in order.
Where `retry()` stops at the first success,
`repeat()` continues until the schedule runs out.
A failure on any run propagates unchanged rather than becoming a `RetryError`.

`memoize()` solves the spent-generator problem:

```python
# memoizing.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db = Database(failures=0)
bound = supply(db)(memoize(save_user))
print(run(bound("Morty")))
#: attempt 1
#: Morty saved
print(run(bound("Morty")))
#: Morty saved
print(f"attempts: {db.attempts}")
#: attempts: 1
```

`memoize()` caches by argument through `functools.lru_cache`.
It wraps the Effect in an object that records the result and replays it rather than driving the spent generator again.
That wrapper exists because a generator runs once,
which is the same fact that makes `retry()` decorate the function.

Because the cache is an `lru_cache`, every argument must be hashable.
An unhashable one, such as a `list`, raises a `TypeError` at the call.
The cache also has no size limit by default,
so it keeps every result as long as the memoized function exists.
`memoize(maxsize=128)` bounds it.

That cache key is the argument, not the scenario.
`memoize()` wraps `save_user()` before `supply()` runs,
so the memoized call returns the same cache entry whichever `Database` you supply:

```python
# memoize_environment.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db1 = Database(failures=0)
db2 = Database(failures=0)
memoized = memoize(save_user)
print(run(supply(db1)(memoized)("Morty")))
#: attempt 1
#: Morty saved
print(run(supply(db2)(memoized)("Morty")))
#: Morty saved
print(db1.attempts, db2.attempts)
#: 1 0
```

The second call's answer comes from `db1`'s cache entry,
because `memoize()` keys on `"Morty"` alone.
Memoize a function only where one scenario serves the memoized call for its whole lifetime,
or key the cache on the scenario too.

## Running Effects in Parallel

`fork()` submits an Effect to an `Executor` and returns a `Task`.
`wait()` collects the result.
This is the same `wait()` that awaits a coroutine in [Waiting on a Coroutine](46_Effects--Stateless.md#waiting-on-a-coroutine).
It accepts a `Task` as readily as an awaitable:

```python
# parallel.py
import time
from concurrent.futures import Executor, ThreadPoolExecutor
from benchmark import report
from stateless import (Async, Depend, Need, Success, Task,
                       as_type, fork, run, success, supply,
                       wait)

@fork
def slow_square(n: int) -> Success[int]:
    time.sleep(0.05)
    return success(n * n)

def squares(
    count: int,
) -> Depend[Need[Executor] | Async, list[int]]:
    tasks: list[Task[int]] = []
    for n in range(count):
        task = yield from slow_square(n)
        tasks.append(task)
    results: list[int] = []
    for task in tasks:
        value = yield from wait(task)
        results.append(value)
    return results

with ThreadPoolExecutor(max_workers=5) as pool:
    start = time.perf_counter()
    out = run(supply(as_type(Executor)(pool))(squares)(5))
    elapsed = time.perf_counter() - start
report(elapsed=elapsed)
print(out)
#: [0, 1, 4, 9, 16]
print(f"five 50ms tasks under 150ms: {elapsed < 0.15}")
#: five 50ms tasks under 150ms: True
```

Five tasks that each sleep 50 milliseconds finish in about the time of one.
The overlap comes from the two loops.
`squares()` forks every task before it waits for any of them,
so the five sleeps overlap.
If you fork and wait inside a single loop,
each `wait()` blocks on the task the same iteration just created,
so the sleeps run one after another and take about five times as long.

The pool is a supplied dependency, not a global,
so `squares()` declares `Need[Executor]` and specifies no pool.
Supplying a `ProcessPoolExecutor` moves the same work into processes.
`squares()` stays as written.
`as_type(Executor)` appears for the reason it always does.
`ThreadPoolExecutor` is the more specific type,
and `squares()` asks for the general one.

The type checker enforces one restriction.
A forked Effect must arrive fully supplied.
`fork()`'s four overloads accept an Effect whose Ability channel holds `Never` or `Async`,
and whose error channel holds `Never` or an exception type,
because `fork()` runs the Effect with `run()` inside the worker.
If you decorate a function that still declares a `Need`, the checker rejects it,
listing the overloads it failed to match.
Supply first, then fork.

That restriction is the only one the checker enforces.
Two of those same four overloads accept an Effect that declares an error,
and both return a `Task` with [no error type on it](#fork-drops-the-error-channel).

The `with` block that manages the pool's lifetime sits outside `run()`,
at the edge, in ordinary Python.
Stateless has no scoping mechanism of its own,
so either a resource lives in a `with` block outside the Effect,
as the pool does here, or the supplied object owns it.
The library's own `Files` class opens and closes a file inside a single `read_file()` call.

The library gives you no way to acquire a resource in one Effect and release it after a later one finishes.
A native Effect system provides that flat resource management.
Python's own answer to that is `ExitStack` in [Combining Context Managers](15_Techniques--Context_Managers.md#combining-context-managers),
which holds a set of managers decided at runtime and unwinds them together.
`ExitStack` flattens nested `with` blocks in ordinary Python,
which covers part of what the missing scope mechanism would do.

## The Toolkit

Here is every tool from both chapters that acts on a description.
Each one builds a description, rewrites a description's type, or executes one.
Three sit outside the tables.
`as_type()` relabels a value for the type checker and hands the value back unchanged at runtime.
`spaced()` and `recurs()` build the `Schedule` that `retry()` and `repeat()` consume.
`print_line()`, `read_line()`, and `read_file()`,
the accessors for the library's own dependencies,
each call `need()` for one class, so `need()`'s row covers them.
`read_file()` also carries `@throws(FileNotFoundError, PermissionError)`,
so the `@throws` row applies to it as well.

Five build a description:

| Tool | Applied to | What it does to the type |
|---|---|---|
| `success(value)` | A value | Wraps it as `Success[R]` |
| `throw(reason)` | An exception instance | Wraps it as `Try[E, Never]` |
| `need(C)` | A class | Builds `Depend[Need[C], C]`, producing an instance |
| `wait(target)` | A `Task` or any awaitable | Adds `Async`; produces the awaited `R` |
| `sleep(seconds)` | A number of seconds | Adds `Need[Time]` and `Async`; produces `None` |

The rest decorate a function that returns an Effect,
rewriting the type that function declares:

| Tool | What it does to the type |
|---|---|
| `supply(*instances)` | Subtracts each `Need[T]` matched by `isinstance()` |
| `handle(handler)` | Subtracts the Ability the handler's parameter names |
| `catch(*E)` | Moves each `E` from the error channel into the result |
| `catch_all` | Moves every declared error into the result |
| `retry(schedule)` | Adds `Need[Time]` and `Async`; the error becomes `RetryError[E]` |
| `repeat(schedule)` | Same additions; the result becomes a tuple of every run |
| `memoize` | Type unchanged; the result caches by argument |
| `fork` | Replaces the channel with `Need[Executor]` and drops any declared error; the result becomes `Task[R]` |
| `@throws(*E)` | Adds each `E` to the error channel |

Three rows carry a caveat.
`fork` needs a fully supplied function, so supply first, then fork.
`@throws` also accepts an ordinary function that raises exceptions,
turning it into one that returns an Effect,
so it is both an entry point and a transformation.
On a function that already returns an Effect, as in `fetch_effectful.py`,
it adds each `E` to that Effect's error channel.
`throw()`, despite the similar name, belongs in the first table,
since it builds the failure as a description.
And `catch_all` comes from `stateless.effect`,
since the package root does not export it.

Two execute an Effect whose yield channel has narrowed to `Async` and errors,
raising a leftover error rather than returning it:

| Tool | Where to call it |
|---|---|
| `run(effect)` | From synchronous code |
| `await run_async(effect)` | From inside a running event loop |

These two are the only functions that perform work,
which is the description/execution split in table form.

## `run()` Builds a Loop per Call

`run()` is `asyncio.run(run_async(effect))`,
building a fresh event loop for the call and tearing it down after.
If you call it from inside a running loop (the shape of any async web handler),
`asyncio.run()` raises a `RuntimeError` before your Effect runs:

```python
# run_cost.py
import asyncio
import time
from typing import Final
from benchmark import report
from exceptions import expected
from stateless import Success, run, run_async, success

def trivial(n: int) -> Success[int]:
    return success(n)

async def inside_loop() -> None:
    with expected(RuntimeError):
        run(trivial(1))

asyncio.run(inside_loop())
#: [RuntimeError] asyncio.run() cannot be called from a
#: running event loop

ROUNDS: Final[int] = 2000

def time_run() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        run(trivial(1))
    return (time.perf_counter() - start) / ROUNDS

async def time_run_async() -> float:
    start = time.perf_counter()
    for _ in range(ROUNDS):
        await run_async(trivial(1))
    return (time.perf_counter() - start) / ROUNDS

per_run = time_run()
per_run_async = asyncio.run(time_run_async())
report(per_run=per_run, per_run_async=per_run_async)
print(f"run() at least 20x slower: "
      f"{per_run > per_run_async * 20}")
#: run() at least 20x slower: True
```

`run_async()` reuses the running loop and costs little beyond the Effect.
`run()` builds and tears down a loop on every call,
and by the listing's own measure that makes it at least twenty times slower than `run_async()`.
Running the listing with [`--numbers`](18_Techniques--Performance.md#numbers-on-your-machine)
prints both per-call costs.
Synchronous code has no loop to reuse, so each of its `run()` calls builds one.
From inside a running loop,
`run_async()` is both the one that works and the one that is fast.

## Where the Guarantee Stops

The guarantee has six limits.

### 1. Nothing stops an undeclared Effect

`Success[int]` claims purity, and this function breaks that claim:

```python
# leaky_effect.py
from stateless import Success, run, success

def double(n: int) -> Success[int]:
    print(f"doubling {n}")
    return success(n * 2)

print(run(double(21)))
#: doubling 21
#: 42
```

That listing type-checks.
Stateless verifies that declared Effects propagate.
It cannot verify that you declared everything effectful,
because Python's `print()`, `open()`,
and `requests.get()` are ordinary calls with ordinary types.
A native EMS computes a function's Effects from its body.
A library checks the Effects you wrote down and has no record of any others.
The guarantee is about consistency, not completeness.

The same limit applies on the error side.
Here `Success[float]` claims that `ratio()` cannot fail:

```python
# undeclared_failure.py
from exceptions import expect
from stateless import Success, catch, run, success

def ratio(a: int, b: int) -> Success[float]:
    return success(a / b)

def caller() -> Success[float | ZeroDivisionError]:
    out: float | ZeroDivisionError
    out = yield from catch(ZeroDivisionError)(ratio)(1, 0)
    return out

expect(ZeroDivisionError, run, caller())
#: [ZeroDivisionError] division by zero
```

`ratio()` carries no `@throws`,
so the `ZeroDivisionError` propagates as an ordinary raised exception,
untracked.
`catch()` matches the values an Effect yields, not exceptions the body raises,
so a failure that no `@throws` lifts goes past `catch()` untouched.
The `catch(ZeroDivisionError)` in `caller()` type-checks and then lets the `ZeroDivisionError` through,
so the protection appears to be there.
The channel carries only what you put into it.

ZIO does not catch an undeclared failure at compile time either.
Its own documentation uses the same example.
`def divide(a: Int, b: Int): ZIO[Any, Nothing, Int] = ZIO.succeed(a / b)` declares an error type of `Nothing`,
and a zero denominator still throws.
The difference is at runtime.
An exception thrown inside a computation ZIO runs becomes a *defect*,
recorded on the `Cause` beside the typed error channel.
`sandbox()` can recover a defect, and the runtime logs it as a dying fiber.
Stateless has no defect channel,
so the exception leaves `run()` as an ordinary Python exception.

### 2. The type checker decides what survives handling

How much of a type survives handling depends on your type checker rather than on the library.
Here, `nested` and `full` come from the same two calls in the same order,
one form nesting them and the other naming the intermediate:

```python
# nested_handle.py
from typing import reveal_type
from ask_tell_stateless import Ask, Tell, greet
from stateless import handle

def capture(request: Tell) -> None:
    print(request.message)

def scripted(request: Ask) -> str:
    return "Alice"

nested = handle(scripted)(handle(capture)(greet))
half = handle(capture)(greet)
full = handle(scripted)(half)

if __name__ == "__main__":
    reveal_type(nested)
    reveal_type(half)
    reveal_type(full)
```

Under `ty` 0.0.91, `ty check nested_handle.py` reads the two forms the same way:

```text
info[revealed-type]: Revealed type
  --> nested_handle.py:17:17
   |
17 |     reveal_type(nested)
   |                 ^^^^^^ `() -> Generator[Never, Any, None]`

info[revealed-type]: Revealed type
  --> nested_handle.py:18:17
   |
18 |     reveal_type(half)
   |                 ^^^^ `() -> Generator[Ask, Any, None]`

info[revealed-type]: Revealed type
  --> nested_handle.py:19:17
   |
19 |     reveal_type(full)
   |                 ^^^^ `() -> Generator[Never, Any, None]`
```

`half` still needs an `Ask`, and `full` and `nested` have every Ability handled,
so `run()` reports a handler left out of either form.
`ask_tell_demo.py` binds `half` and `full` instead of nesting the calls,
because a named intermediate is where you read the Ability that remains.
That is the information this library exists to give you.

The order of the handlers changes what the checker reports.
`catch_everything.py` supplies first and catches second,
and its `catch_all(bound)` comes back as `() -> Generator[Unknown, Any, ...]`.
With every Ability supplied and every error caught,
the channel that should read `Never` reads `Unknown`.
Catching first and supplying second, `supply(feed, book)(catch_all(research))`,
reads `Never`.
That `Unknown` hides no unsupplied `Need`.
A `Need` left unsupplied stays named through `catch_all()`,
`run()` rejects the Effect with an `invalid-argument-type`,
and a run raises a `MissingAbilityError` naming the same `Need`.
An `Unknown` in a revealed type means `ty` left the subtraction unfinished.
`reveal_type()` on the intermediate shows which channel `ty` left unfinished.

The type checker verifies the subtraction,
including where you answer part of what an Effect declares.
Here `supply()` answers one `Need` of two:

```python
# partial_handling.py
from exceptions import expected
from greeter import Console
from stateless import Depend, Need, need, run, supply
from stateless.errors import MissingAbilityError

class Log:
    def write(self, entry: str) -> None:
        print(f"log: {entry}")

def work() -> Depend[Need[Console] | Need[Log], None]:
    console = yield from need(Console)
    log = yield from need(Log)
    console.print("working")
    log.write("worked")

half = supply(Console())(work)
with expected(MissingAbilityError):
    run(half())  # type: ignore
#: [MissingAbilityError] Need(t=<class '__main__.Log'>)
```

`half` is `() -> Depend[Need[Log], None]`,
because the handler subtracts the `Console` and leaves the `Log`.
`run()` therefore rejects it before the program starts:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
  --> partial_handling.py:19:9
   |
19 |     run(half())
   |         ^^^^^^ Expected
   |         `Generator[Async | Exception, Any, Unknown]`, found
   |         `Generator[Need[Log], Any, None]`
```

The `# type: ignore` silences that diagnostic,
since the listing provokes the matching runtime failure on purpose.
The `MissingAbilityError` the listing prints names the `Log` nobody supplied.
Nesting the `supply()` inside the `run()` call draws the same diagnostic,
so the checker needs no named intermediate to catch the missing `Log`.

`catch()` handles part of a channel the way `supply()` does.
If you catch one of two declared errors, the other stays in the error channel.

The library's types ask the type checker a hard inference question,
and the answer changes from one release of the checker to the next.
Trust a green check only where you have seen the same construct produce a red one.

### 3. Handlers cannot capture the continuation

`Effect` is a monad.
`success()` lifts a value into it, `yield from` chains two of them together,
and the generator body is syntax that hides the chaining.
`Result` in [Error Handling](42_Functional--Error_Handling.md#composing-with-bind)
has the same two operations, with the chaining written as `bind()` calls.
Stateless's documentation calls the library an algebraic effect system,
and both descriptions are right.
A monad plus handlers is how you build algebraic effects in a language with no native support for them.
The monad is the mechanism that chains the steps,
and the handlers are the interface.

A library cannot reproduce a native handler's control over the rest of the Effect.
`handle()` passes a handler the Ability and takes back an answer,
and the driver resumes the Effect with that answer, once, always.
A native handler receives the [continuation](44_Effects--Effect_Management.md#native-effect-management)
and chooses what to do with it.
Invoking it once gives you what Stateless has.
Declining to invoke it makes the handled scope produce the handler's value,
which is how an exception behaves.
Invoking it repeatedly gives you backtracking and search.
Stateless offers only the first of the three, one invocation:
a *tail-resumptive* handler.
The limit comes from Python rather than from the library's design.
A Python generator is a [one-shot continuation](45_Effects--Generators.md#annotating-a-generator).
Python cannot copy a suspended generator, so each `yield` resumes once.

Two pieces of the library show that limit.
`Effect[A, E, R]` carries a separate `E` that `@throws` fills and `catch()` empties.
Koka needs no such type parameter,
because an exception there is an ordinary Ability whose handler declines to resume.
The extra type parameter exists because a Stateless handler always resumes the Effect,
so a failure cannot be an Ability.
The `ZIO[R, E, A]` of [Effect Management](44_Effects--Effect_Management.md#library-effect-management)
carries one for the same reason.
`Async` is the other piece.
Native systems derive asynchronous execution from Effects.
Stateless provides `Async` as a built-in that `run()` interprets,
because the driver loop can await where a handler cannot.

### 4. The discipline is all-or-nothing

Every effectful function becomes a generator function,
so it cannot also be a plain function.
Calling it returns a description that somebody must run.
Type errors from a library this generic are long and mention internals.
And a third-party function returns a value or raises an exception,
so it needs a `@throws` wrapper or a `need()` route before it can participate.
An EMS is a decision about a whole codebase,
not a utility you import for one module.

### 5. Much of a mature Effect system is missing

Dependency wiring is the first omission,
and `bakery.py` in [Dependencies That Need Dependencies](#dependencies-that-need-dependencies)
shows its shape.
`supply()` binds finished instances, and `handle()` takes an ordinary function,
so constructing a dependency cannot be an Effect.
ZIO's `ZLayer` is a constructor that can read configuration, fail, and retry.
It resolves a dependency graph at compile time,
reporting a cycle or a missing provider by name.
Stateless has no equivalent, so you write the wiring at the edge yourself.
The type checker verifies that a `supply()` call is complete but leaves the assembly of the graph to you.

The operator set is small in the same way.
The library has `retry()` and `repeat()`.
`Schedule` offers a regular interval and a repeat count,
with no exponential backoff and no jitter.
`retry()` retries every declared error alike,
with no way to specify the one worth retrying.
Stateless provides no timeout, `race`, fallback combinator, or finalizer.
The missing `race` rules out the hedging strategy that races a delayed second request.
Concurrency is `fork()` and `wait()` with no guarded mutable cell.
Two forked Effects that share the `Cell` of [State as an Ability](#state-as-an-ability)
race on it.
No type reports the race.
The library leaves state shared across forked Effects to you and to Python.
Above that sit the resilience patterns a production system eventually needs
(rate limiting, bulkheads, and circuit breakers), none of which exist here.
The library is a working demonstration of Effect tracking in Python's type system,
not a platform for building distributed systems.

### 6. `fork()` drops the error channel

[Running Effects in Parallel](#running-effects-in-parallel)
states the one restriction the type checker enforces on a forked function:
it must arrive fully supplied.
The checker accepts whatever error channel that function declares.
Two of `fork()`'s four overloads accept an Effect that still declares an error,
and every one of the four returns a `Task` with no error type on it:

```python
# fork_leak.py
from concurrent.futures import Executor, ThreadPoolExecutor
from exceptions import expect
from stateless import (Async, Depend, Need, Try, as_type,
                       fork, run, supply, throw, wait)

class Boom(Exception):
    pass

@fork
def bad(n: int) -> Try[Boom, int]:
    yield from throw(Boom(n))
    return 0

def go() -> Depend[Need[Executor] | Async, int]:
    task = yield from bad(1)
    value = yield from wait(task)
    return value

with ThreadPoolExecutor(max_workers=1) as pool:
    supplied = supply(as_type(Executor)(pool))(go)
    expect(Boom, run, supplied())
#: [Boom] 1
```

`fork()` runs the wrapped Effect with `run()` inside the worker thread,
with no `try`/`except` around that call,
so a raised failure crosses the thread boundary as an ordinary exception.
`wait()` raises the failure again when it awaits the `Task`'s future,
past any `catch()` the caller wraps around the result.
The type agrees with the runtime.
`reveal_type(bad)` under `ty` 0.0.91 reports `(n: int) -> Generator[Need[Executor], Any, Task[int]]`,
with `Boom` nowhere in it.

The fix is the discipline `catch()` and `catch_all()` teach:
move the failure into the result before you fork.
Apply `catch_all()` before `@fork`.
With `bad` left undecorated,
`fork(catch_all(bad))` matches the overload for an Effect with no declared error,
and `wait()` returns `Boom | int` instead of raising `Boom`.

## What Survives the Library

[Effect Management](44_Effects--Effect_Management.md#effects-are-the-next-barrier)
argues that Effects are the next barrier to program scale,
and that the tracking will eventually move into the language.
Stateless shows what that looks like inside Python today.
That preview is the value of studying the library,
whether or not you use it in production.
[Effect Tracking](A_Effect_Tracking.md)
looks at the other route Python offers toward algebraic effect tracking:
a row written in `typing.Annotated`, and what a tool would need to check it.

Consider the signatures once more:

- `Success[int]`: pure.
- `Depend[Need[Console], None]`: prints, somehow,
  through something supplied later.
- `Effect[Need[Console], KeyError, None]`: prints, might not find the name.

Each one describes what a function needs, what it can produce,
and how it can fail, before you read a single line of the body.
That is the property this book has returned to since [Functional Foundations](40_Functional--Foundations.md#pure-functions).
Purity is valuable because it is verifiable.
Verifying it by reading code does not scale.

A second gain shows when you put functions together.
Python has a separate mechanism for each concern an Effect type carries.
Absence is `T | None`.
Failure is a raised exception,
or the `Result` that [Error Handling](42_Functional--Error_Handling.md#a-result-type)
builds.
Asynchrony is `async def` and `await`.
A resource's lifetime is a `with` block.
Each is reasonable alone.
None composes with another.
Some pairs allow no conversion.
An `Awaitable` cannot become a `Result` without blocking and giving up the asynchrony.
A `with` block's guarantee is lexical,
so you cannot hand it to a caller as a value the way you can a `Result`.
Consider a function that awaits, might fail, and holds a resource.
It uses three of these mechanisms, and its return type mentions one.

`Effect[A, E, R]` is one type for the dependency, the failure, and the result,
and `yield from` is one operator for joining two Effects.
`research()` joins five steps of two kinds with that one operator,
once `@throws` has brought the ordinary functions in at the boundary.
`Async` is one more Ability in the same channel rather than a second viral annotation.
Resource lifetime is the one concern left outside the Effect type.
Because Stateless has no scoping mechanism, `with` blocks stay where they are.
`ExitStack` flattens them,
and they remain a separate mechanism from the Effect type.

Both gains demand the generator discipline, the description/execution split,
and a wrapper at the boundary for every library that does neither.
For most Python code that demand is larger than the benefit.
[Converting Effectful to Pure](44_Effects--Effect_Management.md#converting-effectful-to-pure)
gives three techniques: returning a `Result`, catching the exception you expect,
and restricting a type so bad values cannot exist.
They make most of a function's failures visible in its signature,
with no generator discipline and no description/execution split.
Use Stateless when a system is large enough that hidden Effects have caused a production incident,
and when the team will declare every Effect at every boundary.
Below that scale, use those three techniques, and treat Stateless as optional.

Whatever you decide about the library, the habit survives it.
Name each contact with the outside (the clock, the feed, the pool, the console)
and bind it at the edge instead of calling it in the middle.
`at()` and `crossing` and `controller()` are all that habit,
and none of them needs an Effect type to work.

But watch the direction.
Python got one Effect tracked into its type system with `async`.
The languages listed under [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
track all of them.
Stateless demonstrates that Python's type system is expressive enough to do it,
given a library willing to encode everything into return types.
The missing piece is a language that does the encoding for you.

## Exercises

Try each exercise before opening its [solution](../Solutions/47_Effects--Stateless_in_Practice/).

1.  `crossing` in `midnight.py` walks a scripted list,
    so it answers two requests.
    Write a handler that instead advances a stored moment by one second at each request,
    and confirm `archive()` still crosses midnight under it.
    Then rewrite `archive()` so the file name and the stamp cannot disagree,
    and explain why no handler can reproduce the bug afterward.
2.  `leaky_effect.py` type-checks even though its `Success[int]` claim is false.
    Describe a review rule or a lint check that catches it,
    and explain why a type checker cannot.
    Then demonstrate the error-side twin:
    write a function that raises a `KeyError` with no `@throws`,
    wrap it in `catch(KeyError)`, and run it on a failing input.
    Explain what the types claim, what the run does,
    and which line restores the guarantee.
3.  Add a wind turbine to `power.py` that is available only during a set windy stretch of the evening,
    put it between solar and the battery in the `sun_first` order,
    and confirm `run_load()` needs no change.
    Then shorten every source until some hour has no source,
    run `run_load()` again,
    and say where the `Blackout` propagates and why `catch(Blackout)` around `run_load()` does not intercept it.
4.  Write a handler for `Outlet` that ignores `request.hour` and hands out a preset sequence of sources,
    the way `scripted` hands out a preset sequence of tosses.
    Use it to test that `run_load()` re-requests after a failure,
    without modeling weather, a clock, or a battery.
    Then say what such a test cannot tell you about `controller()`.
5.  Add a fourth failure to `research()`:
    a `TooLong` raised when an article exceeds some length.
    Follow the type checker's diagnostics until the program type-checks again,
    and list every line you edited.
    Then do the same to `research_by_hand.py` and say which tool named the lines to change in each case.
6.  `scenarios.py` supplies a `DeadWire` that fails without printing anything.
    Write a `StaleWire` whose `latest()` prints `feed: fetching` and then raises `Unavailable`.
    Predict the trace, then say why it differs from `DeadWire`'s trace even though both fail the same way.
7.  Wrap `research()` in `retry()` and supply a `Time()`.
    Explain what `retry()` does under the `WEATHER` scenario and why retrying a `NotInteresting` failure is the wrong behavior,
    then say what an Effect system needs for you to retry `Unavailable` alone.
8.  Change `parallel.py` to use a `ProcessPoolExecutor` instead of a `ThreadPoolExecutor`,
    and confirm `squares()` stays unchanged.
    Processes re-import the module,
    so the driver needs the `if __name__ == "__main__":` guard [Concurrency](19_Techniques--Concurrency.md)
    describes.
    Without it the pool breaks before any work starts.
    Then try to fork an Effect that still declares a `Need`,
    and record what the type checker says.
9.  `test_wallet.py` runs `spree()` against a `Cell`.
    Script it instead.
    Write a `Get` handler that answers from a preset sequence of balances and a `Put` handler that appends every request to a list,
    the way `scripted` feeds `Flip`.
    Assert that `spree()` attempts every price and writes once per purchase.
    Then say what this test cannot detect that the `Cell` version can.
10. `fetch_nonempty()` puts `Empty` into the channel with `throw()`.
    Rewrite it to raise `Empty` in the body and lift it with `@throws(Empty)`,
    and confirm the two versions type-check and behave identically.
    Then make each version fail with an undeclared exception type and compare what the type checker reports for each.
11. Exercise 5 adds a `TooLong` failure to `research()`.
    Repeat it with `catch_everything.py` in the build.
    Predict what the type checker reports in `outcome()`, then confirm.
    Remove `outcome()`'s return annotation and rerun `ty`,
    and explain what the type checker stopped verifying.
12. Write a `Random` Ability whose handler returns an `int` in a range carried on the request,
    and an accessor `roll(low, high)` for it.
    Use it to write a dice game as an Effect, then run the game twice:
    once with a handler that calls `random.randint()`,
    and once with a handler that walks a scripted sequence.
    Then delete the `low: int` annotation from the accessor's parameter and say what changes,
    and delete the annotation on the handler's parameter and say what changes.
13. Add a `Butter` leaf to `bakery.py` and a `buttered()` Effect that needs it and calls `toast()`.
    Write `buttered()`'s signature with `Need[Butter]` alone first, run `ty`,
    and read the diagnostic before fixing it.
    Then remove `Toaster(3)` from `supply()` and say which of the two diagnostics tells you about a dependency two levels below `run()`.
14. `play()` in `casts.py` accepts any three actors, matched or not.
    `kitties_and_puzzles()` and `warriors_and_weapons()` already share a signature.
    Give that shape a name so a caller can pass either one where a cast belongs,
    and say what that recovers of the *Abstract Factory* and what it does not.
    Then add a fourth actor to `encounter()` and count the lines you edit in `quest.py`,
    `casts.py`, and `two_games.py`.
