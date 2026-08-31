# Stateless in Practice

[Stateless](46_Effects--Stateless.md)
established the two channels an `Effect[A, E, R]` carries.
A dependency is a `Need` that `supply()` answers.
A failure is an exception that `@throws` lifts into the type and `catch()` takes back out.
A type checker verifies that every caller either absorbs an Effect or declares it.

Every Ability so far came from the library: the `Need` that `supply()` answers,
and the `Async` that `run()` awaits.
This chapter opens by writing an Ability from scratch,
which shows it is an ordinary class rather than a special form.
The rest of the chapter applies the machinery:

- Handlers that make an unpredictable source testable
- A handler that swaps implementations while a program runs
- A cell of shared state that programs read and write through the channel
- A program whose signature is its own documentation,
  and whose body is only the success path
- A failure that enters the channel as a value,
  and a catch that takes the whole channel
- Dependency graphs that go deep, and a cast of Abilities that goes wide
- Decorators that add retry and parallelism to code they do not edit
- An account of what the guarantee does not cover

The chapter then collects every tool in one place and weighs what the whole approach costs.

## Abilities Are Not Special

A custom Ability is a request you design.
A `Need` asks for an instance and gets whatever the handler supplies.
Your own Ability can ask for anything you can name,
and the handler answering it is an ordinary function,
so the answer can differ at every request.

An Ability subclasses `Ability[T]`, where `T` is the type its handler returns.
Here is the Stateless version of `Ask` and `Tell` from [Effect Management](44_Effects--Effect_Management.md#effects-by-hand):

```python
# ask_tell_stateless.py
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

@dataclass(frozen=True)
class Ask(Ability[str]):
    prompt: str

@dataclass(frozen=True)
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
The `yield from` then evaluates to that generator's return value,
the rule from [The Return Channel](45_Effects--Generators.md#the-return-channel),
and here that value is whatever the handler sent back.
The Ability produces nothing on its own.
`prompt` is payload on the request, there for the handler to read,
so the answer to an `Ask` is whatever `scripted()` returns.
A `Tell` needs no answer,
which is why `Tell` is `Ability[None]` and `capture()` returns `None`.
`ask()` and `tell()` are *accessors*:
small functions that each wrap one Ability and declare its answer type.
`need()` has the same shape,
and the ZIO listing in [Effect Management](44_Effects--Effect_Management.md#library-effect-management)
had an accessor object doing the same job.
The declared `Depend[Ask, str]` types `name` as `str` inside `greet()`.
You can skip the accessor and yield the Ability directly,
and the program still runs,
but under `ty` 0.0.75 the answer comes back as `Unknown` and the checking quietly stops.
The accessor pins it down.
The `answer: str` inside `ask()` does that job.
`yield from Ask(prompt)` produces `Unknown` there too,
so the annotation is an assertion the type checker takes on faith rather than a type it worked out.
`Ability[str]` is where the claim comes from,
and writing it at the binding keeps the accessor's claim in one place,
one line above the `Depend[Ask, str]` that repeats it to callers.

That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`,
the distinction [Waiting on a Coroutine](46_Effects--Stateless.md#waiting-on-a-coroutine)
drew for `Async`.
`Ask` is an Ability, so it sits in the channel bare,
and the type bound makes that more than a convention:
the type checker rejects `Depend[Console, None]` at the annotation,
before it examines any `yield`,
because `Console` is not assignable to `Ability[Any]`.

`handle()` reads the annotation on its argument to decide which Ability it answers,
which is why `scripted` and `capture` must annotate their parameters.
If you leave the annotation off,
`handle()` raises a `ValueError` at the point of decoration,
since nothing names the type a request must match.
Each `handle()` subtracts one Ability,
so `half` still needs an `Ask` and `full` needs nothing.
Naming the two stages also matters to the type checker,
for a reason [The type checker can give up quietly](#the-type-checker-can-give-up-quietly)
gives.

Now compare this listing to `ask_tell.py` again.
The by-hand version puts two objects in every signature.
This one threads nothing.
`greet()` takes no arguments,
and the two Effects live in the return type where a type checker can follow them.
That second channel in the signature is the one [Effect Management](44_Effects--Effect_Management.md#effect-management-systems)
said an EMS needs.

The whole library is visible in `two_way_generator.py` from [Generators](45_Effects--Generators.md#a-generator-is-a-description).
An Effect is a generator, so nothing stops you from driving one yourself,
which `hand_driven.py` in [Nothing Runs Yet](46_Effects--Stateless.md#nothing-runs-yet)
did.
`next()` on `greet("Alice")` produced a `Need` object carrying the requested type,
as `interview()` yielded `"name"`, and `send(Console())` resumed the body,
which printed the greeting and finished.
Every tool in the library packages those two calls.
`handle()` is `drive()` with a type lookup in place of the dictionary,
`run()` is that loop sitting at the bottom of the stack of handlers,
and `supply()` is `handle()` prepackaged for `Need`:
a handler whose answer to `Need[T]` is whichever supplied instance is a `T`.

## Scripting an Unpredictable Source

Every handler so far gave the same answer at every request.
`supply()` binds one instance for the whole run,
and `scripted` returned `"Alice"` no matter how many times `greet()` requested a name.
A handler is an ordinary function, so it can answer differently at each request.
That makes an unpredictable source testable.

### A Coin Toss

Tossing a coin is a side cause: the program reads something from outside,
and the reading does not repeat.
If you turn it into an Ability, the reading moves into a handler:

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

`count_heads()` needs a `Flip` and produces an `int`.
Its body contains no `random` call, no seed, and no parameter for either.
`Flip` carries no data, so it needs no fields.
`Ask` and `Tell` each carry the payload the request must deliver.
The Ability's whole content is its type and the `bool` it produces.

The parentheses in `if (yield from flip()):` are mandatory.
A `yield` expression can appear on the right side of an assignment,
as a statement of its own, or inside parentheses.
An `if` condition is none of those,
so `if yield from flip():` is a syntax error.

Two handlers feed the same function.
`scripted` walks an iterator over a fixed sequence,
so the sequence decides the five tosses before the program runs and the count is `3`.
`coin` calls `random.random()`, so ten thousand tosses come out near half heads.
`count_heads()` cannot distinguish the two,
because either answer arrives through the same `send()` channel.

The scripted handler holds state.
`next(script)` produces a different value at each request,
which one supplied instance cannot do.
Every scripted test double has this shape: a queue handing out canned responses,
a network stub that fails twice and then succeeds, or the clock below.

That state brings one trap, and it is silent.
`next(script)` raises `StopIteration` once the sequence runs out,
and `StopIteration` is how a driver learns that an Effect has finished,
so `handle()` reads the exhausted script as the end of the program.
Asking `count_heads()` for six tosses from this five-value script makes `run()` produce `None` instead of a count,
with no exception.
That is the same silent `None` that [An Effect Runs Once](46_Effects--Stateless.md#an-effect-runs-once)
shows for a spent Effect.
Every other exception a handler raises travels out of `run()` normally.
This one collides with the protocol.
Indexing a list rather than walking an iterator turns the mistake into an `IndexError` you can see.

### A Clock

Reading the current time is another side cause.
A real clock answers with the present moment,
so a test cannot ask it what happens at some critical time
(midnight, tomorrow, etc.).
`stamp()` puts the current time into its output,
and `batch_due()` decides whether a day has passed since the last run.
Against a real clock neither is testable.
One produces a different string every minute,
and the other needs you to wait a day to watch it return `True`.
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
Its answer type is its whole content: a handler for `Now` returns a `datetime`,
and `now()` is the accessor that declares that type.
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

`frozen()` reports a single moment over and over,
so `stamp()` produces a fixed string a test can compare.
`tomorrow` reports a moment a day later,
and `batch_due()` returns `True` with no time having passed.
The schedule logic runs against whatever moment the handler names,
in microseconds rather than a day.
`batch_due()` holds no `datetime.now()` call,
so a test has nothing to monkeypatch and nothing to wait for,
and a production handler that returns `datetime.now()` leaves the function unchanged.

Those three runs are claims about testability, so here they are as tests.
The handler moves inside each test, and every test names the moment it needs:

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

def test_stamp_names_the_supplied_moment() -> None:
    stamped = run(handle(at(MOMENT))(stamp)("started"))
    assert stamped == "[2026-03-14 09:30] started"

@pytest.mark.parametrize("elapsed, due", [
    (timedelta(hours=23, minutes=59), False),
    (timedelta(hours=24), True),
])
def test_batch_due(elapsed: timedelta, due: bool) -> None:
    moment = MOMENT + elapsed
    is_due = run(handle(at(moment))(batch_due)(MOMENT))
    assert is_due is due
```

`at()` builds a handler from a moment,
so each test freezes its own clock in one line.
The parametrized case one minute short of a day is the reading a real clock cannot produce on demand.
Getting it live means starting the test at the right minute,
but here the margin is a `timedelta`.
No fixture patches `datetime`, nothing sleeps,
and each assertion compares values the test chose.

Skipping the wait is the obvious benefit.
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
`crossing` answers the first request at one second before midnight and the second two seconds later.
Now the file carries January 1's name and the entry inside it carries January 2's date.
A day of entries can end up in the wrong file,
and the window for the mistake is one second wide.

Using a real clock, you wait for that window and probably miss it.
Tests that run at nine in the morning cannot see it,
and the bug report says the log file is occasionally short by a few lines.
The Ability makes the moment reachable.
`archive()` does not read a clock.
It asks for a moment, and a handler decides which moment that is.
Both handlers answer the same two requests.
They differ in whether midnight falls between them.

`crossing` follows the same pattern as `scripted` in `coin_toss.py`.
It walks a fixed list, so it holds state between requests,
which is how it answers the same question two ways.
A supplied instance cannot do this, and neither can `frozen` or `tomorrow`,
since each reports one moment however often you ask.

Compare this to `student_pairs.py` in [Functional Toolkits](41_Functional--Toolkits.md#case-study-pairing-rotations),
which made randomness repeatable a different way, by taking a `seed` parameter.
That works, but every function between the caller and the `random.Random` call must declare the parameter and pass it along.
Here the return type names the source instead,
and no signature between `handle()` and the request mentions it.

Both Abilities in this section are side causes,
in the vocabulary of [Effect Management](44_Effects--Effect_Management.md#subdividing-the-impure-portion):
the function reads something from outside.
The `Recorder` of [Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
stood in for a side effect, where the function writes something outward.
The technique is the same for both.
Name each contact with the outside as an Ability and bind it at the edge to whatever the context needs.
What an EMS adds is that you cannot skip the declaration by accident.

## Switching Implementations Mid-Run

Every handler so far answered with data: a name, a `bool`, a `datetime`.
A handler can also answer with an implementation,
an object whose methods the program then calls,
and it can choose a different one at each request.
`supply()` cannot do that, because it binds one instance for the whole run.
When the implementation a program depends on must change while the program is running,
the choosing belongs in a handler.

A building's power supply works this way.
Solar carries the load while the sun is up.
The battery carries it while the charge stays above a threshold.
The utility grid carries it when neither can,
and a diesel backup carries it when the grid is down too.
Each stops for its own reason,
and when one stops the building must obtain another.

Sources are ordinary objects.
Each reports whether it can supply a given hour, and depletes when drawn from:

```python
# power.py
from dataclasses import dataclass
from typing import Protocol
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

@dataclass(frozen=True)
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

`Outlet` is an Ability whose handler returns a `Source`,
and it carries the hour so the handler can consult the conditions at that moment.
`Ask` carried a prompt for the same reason.
`Source` carries no `@runtime_checkable`,
because nothing calls `isinstance()` against it.
That decorator matters where `supply()` matches an instance to a requested class
([Supplying an Interface](46_Effects--Stateless.md#supplying-an-interface)).
Here `handle()` matches on the Ability's own type, `Outlet`,
and the `Source` that comes back is only a return value.
`draw()` is the lifting wrapper: it asks the source whether it can still supply,
and `@throws` lifts the refusal into the error channel.

Here is the consumer and the handler that feeds it:

```python
# microgrid.py
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from power import (
    Backup,
    Battery,
    Drained,
    Grid,
    Outlet,
    Solar,
    Source,
    draw,
    plug,
)
from stateless import Depend, catch, handle, run

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
def connected(source: Source) -> Iterator[Source]:
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

Read `run_load()` from the outside in.
The outer loop obtains a source, the inner one draws from it hour after hour,
and `connected()` brackets the pair.
`draw()` returns `None` on success,
so anything else at that binding is the `Drained` that ends the inner loop and sends the outer one back to `plug()` for a replacement.
The hour does not advance on that path,
so the replacement supplies the hour the failed source refused.

The first trace is an evening.
Solar covers two hours and stops at sunset.
The battery covers two more and stops when its charge falls below the threshold.
The grid covers one and stops when the outage begins at 22:00.
The backup covers the last.
Four implementations, one Ability, one running program.

`run_load()` names none of them,
which is why the second run tells a different story from the same code.
`battery_first` puts the battery ahead of the sun,
so the charge drains first and the grid picks up at 19:00.
Reordering that tuple is the whole difference between the two runs.
Priority, thresholds, and the outage schedule live in `controller()`,
and `run_load()` decides when to give up on the source it holds.

The load's declared dependency does not change.
`Depend[Outlet, None]` says it needs an `Outlet` from the first hour to the last,
and that type appears once.
What changes is the object answering the need, four times, mid-run.
Binding a dependency before the program starts cannot express this,
because no single answer stays right for the whole run.
Here the binding is a function call, so it reads the world at each request.
[Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
swapped an implementation between runs.
This swaps one during a run, and the consumer cannot tell.

`connected()` is an ordinary context manager,
and its `with` block sits inside the generator body.
Acquiring and releasing within one Effect works,
since the block opens and closes between two `yield from` expressions in the same function.
What you cannot write is an acquisition in one Effect released after a later one finishes,
a gap that [Running Effects in Parallel](#running-effects-in-parallel) revisits.

One thing stays outside the types.
`choose()` raises a `Blackout` when no source can supply the hour,
and that is ordinary code raising an ordinary exception.
No `@throws` lifts it,
so it travels through `run()` untracked and no signature mentions it.
`catch()` matches values an Effect yields,
and a handler is not part of the Effect,
so no `catch()` around this program intercepts it.
A handler sits outside the channel it feeds.

## State as an Ability

Each Ability so far moves information in one direction.
`Flip` and `Now` read from outside: side causes.
`Tell` writes outward: a side effect.
Shared mutable state is both at once,
because whoever holds it must read it and write it back.
An Ability declares one answer type,
so a cell of state becomes a pair of Abilities:
reading answers with the stored value,
and writing carries a new value and answers with nothing.

```python
# wallet.py
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

class Get(Ability[int]):
    pass

@dataclass(frozen=True)
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

cell = Cell(100)

def read(request: Get) -> int:
    return cell.amount

def write(request: Put) -> None:
    cell.amount = request.amount

half = handle(read)(spree)
shop = handle(write)(half)
print(run(shop((60, 50, 30, 20))))
#: 2
print(f"remaining: {cell.amount}")
#: remaining: 10
```

`Get` has `Flip`'s shape: no payload, and the answer type is its whole content.
`Put` has `Tell`'s: payload out, nothing back.
`purchase()` is where the pair earns its keep.
It reads, decides, and writes, and the decision sits between the two requests,
in code that mentions no cell.
Its signature announces the shared state:
`Depend[Get | Put, bool]` tells a caller this function touches something that outlives it.
`spree()` composes purchases, and the union travels up unchanged.

The handlers own the cell.
`read()` and `write()` are two functions sharing one `Cell`,
chained through the named stages of [Abilities Are Not Special](#abilities-are-not-special).
After the run, the cell shows what the program did to it:
two purchases went through, and 10 remained.
A test builds its own pair from a fresh `Cell`,
the way `at()` builds a clock from a moment, and asserts on what remains,
with no global to reset between tests.

For a number one function owns, a local variable is the right tool,
and `count_heads()` keeps its count in one.
The pair pays off when separate functions share the cell,
as `purchase()` and any other spender would,
without a parameter threaded through every signature between them.

This pattern has a name.
Treatments of algebraic effects open with the *State effect*,
`get` and `put` as its two operations,
and this section built that effect on Stateless's machinery.
One warning comes with it,
and [Where the Guarantee Stops](#where-the-guarantee-stops)
returns to the theme.
Nothing guards the cell.
Forking two Effects that share a `Cell` interleaves their reads and writes,
and no type reports the race.
ZIO's `Ref` is this cell with atomic update built in.
Stateless has no equivalent,
so under `fork()` the cell is as exposed as any Python global.

## Composing a Program

This small application fetches a headline,
finds a topic worth researching within that headline, and looks up that topic.
Each step needs something or can fail, and no step names an implementation:

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

The `research()` signature tells you the program's entire surface.
It reads two things from outside and can fail three ways.
The three `@throws` functions are the pattern for bringing ordinary code in:
`fetch()` and `look_up()` call methods that know nothing about Effects,
and the decorator lifts what they raise into the channel.
`topic_of()` needs nothing and touches nothing, so it declares no Ability.

`fetch()` and `look_up()` take their dependencies as parameters,
which makes them ordinary functions rather than generator functions.
That is a choice, not a requirement.
`@throws` decorates a function returning an Effect,
so the request and the failure can live in one function:

```python
# fetch_effectful.py
from research import Feed, Unavailable
from stateless import Depend, Need, need, throws

@throws(Unavailable)
def fetch_headline() -> Depend[Need[Feed], str]:
    feed = yield from need(Feed)
    return feed.latest()
```

The decorator adds the error the same way it did for `score()` in [The Error Channel](46_Effects--Stateless.md#the-error-channel).
`ty` reports `fetch_headline` as `() -> Generator[Need[Feed] | Unavailable, Any, str]`,
which is `Effect[Need[Feed], Unavailable, str]`.
`research()` splits the two because a function that only transforms its arguments is easier to test on its own,
and because the split keeps the Ability requests in one place.
Either shape type-checks and either propagates correctly.

The signature is also the only place this information appears.
Nothing in the body mentions a network, a file, or a print,
and `research()` performs no work when called.
Now supply the environment:

```python
# scenarios.py
from dataclasses import dataclass
from typing import Final, assert_never
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    research,
)
from stateless import Depend, Need, catch, run, supply

@dataclass
class Wire:
    headline: str
    def latest(self) -> str:
        print("feed: fetching")
        return self.headline

class DeadWire:
    def latest(self) -> str:
        raise Unavailable("offline")

@dataclass
class Library:
    articles: dict[str, str]
    def article(self, topic: str) -> str:
        print(f"library: looking up {topic}")
        if topic not in self.articles:
            raise NoArticle(topic)
        return self.articles[topic]

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

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library(
    {"stock market": "a history"})
EMPTY: Final[Library] = Library({})

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))
#: feed: fetching
#: library: looking up stock market
#: a history
print(outcome(WEATHER, SHELF))
#: feed: fetching
#: nothing worth researching
print(outcome(STOCKS, EMPTY))
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
print(outcome(DeadWire(), SHELF))
#: no headline today
```

Four runs of one program, differing in what you supply.
The first finds its article.
The second exercises `NotInteresting`, the third `NoArticle`,
and the fourth `Unavailable`,
so the runs cover every failure the signature declares.
A full Effect system calls each pair of bindings a *scenario*,
and here a scenario is nothing more than arguments to `supply()`.

Every printed line in that trace comes from a supplied implementation,
because the pipeline holds no output of its own.
The second run also stops after `feed: fetching`.
`topic_of()` yields a `NotInteresting`, which ends `research()` where it stands,
so the `need(Encyclopedia)` two lines below it does not run and no one consults a library.
`catch()` receives that failure and `report()` matches on it as a value,
which is why the run still prints a message.
A failure ends the remaining steps the way a raised exception would,
and no step tests for it.
Where the run stops depends on where the failure arises.
The fourth run prints no trace,
since `DeadWire.latest()` raises `Unavailable` before printing,
while the third reaches the library and fails there.

`report()` is where the two channels come apart.
`catch()` empties the error channel, so `report()` cannot fail.
It still declares both Abilities,
because catching an error does nothing about a dependency.
If you annotate `report()` as `Success[str]`,
`ty` names the `yield from` that still carries `Need[Feed] | Need[Encyclopedia]`.
`supply()` empties that half, and `run()` accepts what remains.

`outcome()` also earns its annotations.
`Wire` and `Library` are structural implementations,
so `supply(Wire(...), Library(...))` builds handlers for `Need[Wire]` and `Need[Library]`,
the mismatch that [Supplying an Interface](46_Effects--Stateless.md#supplying-an-interface)
fixed with `as_type()`.
Declaring the parameters as `Feed` and `Encyclopedia` does the same job at the boundary,
without a cast.

## The Success Path

`research()` handles no errors.
Its body is a straight run of six lines, each saying what should happen next,
and no line tests whether the previous one worked.
The error channel makes that possible.
Here is the same pipeline with the failures handled where they arise:

```python
# research_by_hand.py
from research import (
    TOPICS,
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
)

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

`topic_of()` appears again in full because `research.py`'s version carries a decorator:
it returns an Effect, and ordinary `try`/`except` code cannot call it directly.

Three lines of work sit inside nine lines of handling.
The pipeline is in there, but you have to look for it.
The Effect version moves those nine lines into `report()`,
one `match` over the failures instead of a `try` at each step.
The name records the merge the by-hand version cannot avoid:
`research()` and `report()` in one function.

Both versions short-circuit.
The by-hand one returns early, and the Effect one abandons the generator.
The difference is who writes the branch that does it.

The comparison has limits.
At this size the by-hand version is respectable,
and a reader who prefers it is not making a mistake.
Two differences outlast the size argument.
Its signature, `(Feed, Encyclopedia) -> str`,
mentions none of the three failures,
so a fourth one can arrive with nothing to tell the caller.
And the handling interleaves with the logic:
`research_and_report()` decides both what to do about a failure and what to say about it.
The Effect version separates those,
so a second caller can catch the same three failures and choose different messages,
retry the whole pipeline, or let one failure through to the edge,
without touching the pipeline.

## Two More Doors

The error channel you have seen has one entrance and one exit.
`@throws` lifts what ordinary code raises,
and `catch()` takes named errors back out as values.
The library provides a second door on each side.

### Failing from Inside an Effect

`throw()` is the counterpart of `success()`.
Where `success(value)` builds a description that produces a value,
`throw(reason)` builds one that fails.
Its type is `Try[E, Never]`,
the alias from [The Effect Type](46_Effects--Stateless.md#the-effect-type),
with `Never` recording that no value can come out of it.
`yield from` sends that failure into the channel of the Effect that contains it:

```python
# fetch_guarded.py
from dataclasses import dataclass
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

@dataclass
class Ticker:
    headline: str
    def latest(self) -> str:
        return self.headline

def edge(feed: Feed) -> str | Unavailable | Empty:
    guarded = catch(Unavailable, Empty)(fetch_nonempty)
    return run(supply(feed)(guarded)())

print(edge(Ticker("markets close mixed")))
#: markets close mixed
print(type(edge(Ticker(""))).__name__)
#: Empty
```

`fetch_nonempty()` fails through both doors.
`Unavailable` originates in ordinary code: `latest()` raises it,
and the `@throws` on `fetch()` lifts it.
`Empty` originates here, in the generator,
where the headline is available to inspect.
No decorator takes part and nothing raises an exception.
`throw(Empty())` yields the failure the way `Ask(prompt)` yields a request,
and the driver takes it from there.
Execution does not come back: a driver that receives a failure stops sending,
so anything after a `yield from throw(...)` is unreachable,
which the `Never` in its type records.

The difference between the doors is what the type checker can see.
If you change `Empty()` to some undeclared exception,
`ty` flags the `yield from` where it stands,
because the yielded type no longer fits the declared channel,
the `invalid-yield` that [Dependencies That Need Dependencies](#dependencies-that-need-dependencies)
shows in full.
A `raise` gets no such check.
`@throws` lifts the types it names, anything else escapes untracked,
and no diagnostic connects the decorator's list to what the body raises.
A failure that enters through `throw()` is in the type system from the moment it exists.

### Catching the Whole Channel

`catch()` names what it takes.
`catch_all()` takes whatever the channel declares:

```python
# catch_everything.py
from dataclasses import dataclass
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    research,
)
from stateless import run, supply
from stateless.effect import catch_all

@dataclass
class Bulletin:
    headline: str
    def latest(self) -> str:
        return self.headline

class BareShelf:
    def article(self, topic: str) -> str:
        raise NoArticle(topic)

def outcome(
    feed: Feed, book: Encyclopedia
) -> str | Unavailable | NotInteresting | NoArticle:
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(Bulletin("mild and cloudy"), BareShelf())
print(type(dull).__name__)
#: NotInteresting
missing = outcome(Bulletin("genome mapped"), BareShelf())
print(type(missing).__name__)
#: NoArticle
```

`outcome()` is the boundary function `scenarios.py` used,
with the same upcasting annotations.
Its result type is the union `report()` earned by naming all three errors,
and this listing names none of them at the catch.
Two failures from two different sources come back as values through one undecorated call.

`outcome()` supplies first and catches second, the reverse of `scenarios.py`,
and neither the runtime nor the type checker minds.
A handler passes error values upward untouched,
so the failures travel through `supply()`'s driver to the catch either way,
and under `ty` 0.0.75 both orders infer the same result type.
What both orders need is the intermediate name.
In one nested expression the inference collapses:
`supply(feed, book)(catch_all(research))` fails with an `invalid-argument-type`,
and `catch_all(supply(feed, book)(research))` fails with a `no-matching-overload` and infers `Unknown`.
That is why `bound` has a name,
and it is the gap [The type checker can give up quietly](#the-type-checker-can-give-up-quietly)
takes apart.

Choosing between the two decides what a new failure does.
When `research()` gains a fourth error,
`report()`'s named `catch()` leaves it in the channel,
so `report()`'s declared type no longer matches and `ty` points at the `yield from`:
you decide whether to catch the newcomer or declare it.
`catch_all()` absorbs it into the result union instead,
so the guard must sit downstream, in an annotation that spells the union out,
as `outcome()`'s return type does,
or in a `match` that ends with `assert_never()`.
Without such a guard, the new failure becomes a value that flows on unexamined.
`catch()` makes each failure an explicit decision.
`catch_all()` decides for all of them at once.

Two cautions.
`catch_all` comes from `stateless.effect`,
since the package root does not export it.
And it widens nothing about the guarantee:
a failure that `@throws` did not lift is not in the channel,
so `catch_all()` passes it by as readily as `catch()` does.

## Dependencies That Need Dependencies

`research()` asked for two things, and both were leaves.
Nothing needed building before you could supply a `Feed` or an `Encyclopedia`.
Real graphs nest.
Toast needs bread and a toaster, and bread needs dough and an oven.
This example rebuilds the `Bread` sequence from [Effect Oriented Programming](https://effectorientedprogramming.com/),
where ZIO wires the same graph with `ZLayer`s:

```python
# bakery.py
from dataclasses import dataclass
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Dough:
    flour: str
    def risen(self) -> str:
        print("dough: risen")
        return f"{self.flour} dough"

@dataclass(frozen=True)
class Oven:
    celsius: int
    def bake(self, dough: str) -> str:
        print(f"oven: baking at {self.celsius}")
        return f"loaf of {dough}"

@dataclass(frozen=True)
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

You supply appliances and make products, and the listing keeps the two apart.
`Dough`, `Oven`, and `Toaster` are the leaves,
so `supply()` binds one instance of each.
The loaf is not a leaf.
`bread()` is an Effect that produces a loaf,
so `toast()` obtains one by writing `yield from bread()` rather than by asking for a `Need[Bread]`.
Nothing supplies a loaf, because no loaf exists when `supply()` runs.

The graph arrives in the signature, flattened into a union.
`toast()` declares all three leaves although its body names one of them.
`Need[Dough]` and `Need[Oven]` travel up through `yield from bread()`,
which carries the inner Effect's Abilities to its caller.
The type checker maintains that union.
If you declare `toast()` with `Need[Toaster]` alone,
`ty` points at the delegation:

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

The type checker covers the other end too.
`ty` rejects the `run()` call,
finding a `Generator[Need[Oven], Any, str]` where it expected an empty Ability channel,
the rejection that [Forgetting to Supply](46_Effects--Stateless.md#forgetting-to-supply)
showed, now arising from a dependency two levels down.
`Oven` and `Toaster` are distinct types,
so the ambiguity of [When Two Implementations Match](46_Effects--Stateless.md#when-two-implementations-match)
cannot arise here.
ZIO makes both of them a `HeatSource` and must report the clash.

Here is what ZIO does that Stateless cannot.
`Bread.homeMade` is a `ZLayer`: a constructor that is an Effect.
It can print, it can fail, and you can retry it.
The compiler resolves it into a tree with `Oven` and `Dough` beneath it.
You provide that layer rather than a finished loaf.
Stateless has no such thing.
`supply()` matches instances that exist,
and `handle()` answers an Ability with an ordinary function,
so a constructor cannot be an Effect.
That is the shape of the listing above.
Leaves bind at the edge, products come from an explicit `yield from`,
and the graph you can read is the union in the signature.

## Supplying a Whole Cast

The bakery graph went deep.
Three appliances, one of them reached through another Effect.
The next example goes wide.
[Abstract Factories](27_Patterns--Factory.md#abstract-factories)
built a gaming environment where a `GameElementFactory` returned a matched `Character` and `Obstacle`,
and a `GameEnvironment` played whatever that factory produced.
Here the cast widens to five kinds of actor, each requested as an Ability:

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

@runtime_checkable
class Terrain(Protocol):
    def underfoot(self) -> str: ...

@runtime_checkable
class Reward(Protocol):
    def prize(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator]
    | Need[Hero]
    | Need[Obstacle]
    | Need[Terrain]
    | Need[Reward],
    None,
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    terrain = yield from need(Terrain)
    obstacle = yield from need(Obstacle)
    reward = yield from need(Reward)
    narrator.say(
        f"{hero.name()} crosses the {terrain.underfoot()}")
    narrator.say(hero.approach(obstacle.blocks()))
    narrator.say(f"and wins {reward.prize()}")
```

`encounter()` is the entire engine,
and the only types it mentions are the five Protocols.
No concrete class appears in it, and it prints nothing.
Output is an Ability like the other four:
`Narrator` is one of the five requests,
so the code that supplies it chooses whether a line prints, goes into a list,
or disappears.
The program constructs no `GameEnvironment` and holds no factory.
The five-way union appears in full rather than as an alias,
the practice [Retrofitting an Effect](46_Effects--Stateless.md#retrofitting-an-effect)
recommends.

Five Abilities need five distinct shapes.
`Obstacle.blocks()` and `Terrain.underfoot()` could each have carried the name `describe()`.
Then any obstacle would satisfy `Terrain` as well,
leaving argument order to decide which request each one answered,
the ambiguity of [When Two Implementations Match](46_Effects--Stateless.md#when-two-implementations-match).
A wide cast raises the odds of a collision,
since every pair of Abilities is a chance for one.

The cast is a set of ordinary classes that inherit nothing:

```python
# casts.py
from quest import (Hero, Narrator, Obstacle, Reward,
                   Terrain, encounter)
from stateless import run, supply

class Kitty:
    def name(self) -> str: return "Kitty"
    def approach(self, obstacle: str) -> str:
        return f"and bats at the {obstacle}"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Garden:
    def underfoot(self) -> str: return "garden path"

class Yarn:
    def prize(self) -> str: return "a ball of yarn"

class Warrior:
    def name(self) -> str: return "Warrior"
    def approach(self, obstacle: str) -> str:
        return f"and battles the {obstacle}"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

class Wasteland:
    def underfoot(self) -> str: return "cracked wasteland"

class Gold:
    def prize(self) -> str: return "a chest of gold"

def play(
    narrator: Narrator,
    hero: Hero,
    obstacle: Obstacle,
    terrain: Terrain,
    reward: Reward,
) -> None:
    cast = supply(narrator, hero, obstacle, terrain, reward)
    run(cast(encounter)())

def kitties_and_puzzles(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle(), Garden(), Yarn())

def warriors_and_weapons(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon(), Wasteland(), Gold())
```

`play()` is the boundary function of [Composing a Program](#composing-a-program),
grown from two parameters to five.
Its annotations do the upcasting, so no actor needs `as_type()`,
and its body is the one place in the program where an Ability meets an implementation.
`kitties_and_puzzles()` and `warriors_and_weapons()` are what the two concrete factories became.
Each was a class with a method per product.
Each is now a function that hands `play()` a matched set.
The parallel hierarchies vanish with them.
`Kitty` does not extend a `Character` base class,
`Puzzle` does not extend an `Obstacle` base class,
and the engine names no class:

```python
# two_games.py
from dataclasses import dataclass, field
from casts import (
    Kitty,
    Wasteland,
    Weapon,
    Yarn,
    kitties_and_puzzles,
    play,
    warriors_and_weapons,
)

class Loud:
    def say(self, line: str) -> None: print(line)

@dataclass
class Script:
    lines: list[str] = field(default_factory=list)
    def say(self, line: str) -> None:
        self.lines.append(line)

kitties_and_puzzles(Loud())
#: Kitty crosses the garden path
#: and bats at the puzzle
#: and wins a ball of yarn
warriors_and_weapons(Loud())
#: Warrior crosses the cracked wasteland
#: and battles the nasty weapon
#: and wins a chest of gold
play(Loud(), Kitty(), Weapon(), Wasteland(), Yarn())
#: Kitty crosses the cracked wasteland
#: and bats at the nasty weapon
#: and wins a ball of yarn
script = Script()
kitties_and_puzzles(script)
print(len(script.lines), script.lines[1])
#: 3 and bats at the puzzle
```

One engine, four runs, and the only difference is what you supply.

The third mixes the casts, and nothing objects.
A `Kitty` bats at a `Weapon` across a `Wasteland`.
It type-checks, and it runs.
That is a real loss against the Abstract Factory,
whose purpose is families of matched products:
`KittiesAndPuzzles.make_obstacle()` cannot return a `Weapon`,
because the pairing lives inside the class.
`supply()` takes a flat list and checks each argument against one Ability,
not against the others.
The matched set comes back only if you write it down,
which `kitties_and_puzzles()` does.
The guarantee moved from a class hierarchy into a two-line function.
Know which of those you are getting.

The fourth run swaps one cast member and captures the output.
`Script` records what arrives,
so a test reads the lines back as a list with no `capsys` and no monkeypatching,
the same swap `test_greeter.py` in [Swapping the Implementation](46_Effects--Stateless.md#swapping-the-implementation)
made with one Ability rather than five.
The engine holds no printing to intercept.

The cast has a ceiling on how wide it can get.
`supply()`'s declaration carries overloads for one through nine values,
so a tenth argument matches none of them:

```text
error[no-matching-overload]: No overload of function `supply`
matches arguments
```

The call still runs correctly, since the implementation is variadic,
but the checking on which this chapter relies disappears.
Two chained handlers keep it: `supply()` the first five,
apply that to the Effect, then `supply()` the rest to what remains,
which is the layered supply of [Dependency Injection](46_Effects--Stateless.md#dependency-injection).
Nine is also a fair warning about the design.
An Effect that asks for ten separate things is usually two Effects.

## Adding Behavior to an Existing Effect

[The Success Path](#the-success-path)
said that a caller could retry a pipeline without touching it.
Stateless provides a few decorators that add such behavior.
Retry is the one to study, because of what it does to the type.

`Database` fails a fixed number of times before working,
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
        print(f"attempt {self.attempts}: saving {user}")
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

`retry()` takes a `Schedule` and decorates a function that returns an Effect:

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
#: attempt 1: saving Morty
#: database crashed
three = recurs(3, spaced(timedelta(milliseconds=1)))
retried = retry(three)(save_user)
print(run(
    supply(Database(failures=2), Time())(retried)("Morty")))
#: attempt 1: saving Morty
#: attempt 2: saving Morty
#: attempt 3: saving Morty
#: Morty saved
caught = catch(RetryError)(retried)
outcome = run(
    supply(Database(failures=9), Time())(caught)("Morty"))
print(type(outcome).__name__)
#: attempt 1: saving Morty
#: attempt 2: saving Morty
#: attempt 3: saving Morty
#: RetryError
```

The first run is the baseline: one attempt, no retry, and it fails.
`three` comes from the only two schedule combinators the library has:
`spaced()` yields a fixed interval forever,
and `recurs()` stops it after `n` yields.
Three attempts against a database that fails twice succeed on the third,
and three attempts against one that always fails produce a `RetryError` holding every failure.
`save_user()` stayed unchanged through all of it.

Read the trace before you use this on real code.
Each attempt line is `Database.save()` running again,
so the decorated function runs its whole body once per attempt.
Retrying a charge or an append duplicates it.
Nothing in the type says whether a retry is safe,
because `Effect[A, E, R]` tracks what a function needs and how it fails,
not whether running it twice means the same as running it once.
That judgment stays with you.

`retry()` decorates the function, not the Effect.
`retry(three)(save_user("Morty"))` is not available,
for the reason [An Effect Runs Once](46_Effects--Stateless.md#an-effect-runs-once)
gave: the Effect is a generator, one `run()` spends it,
and only the function can build a second description.

### What Retry Costs the Signature

`save_user()` was `(str) -> Effect[Need[Database], Crashed, str]`.
Under `reveal_type()`, `retried` is:

```text
(user: str) -> Generator[
    Need[Database] | Need[Time] | Async | RetryError[Crashed],
    Any,
    str,
]
```

Three changes, none of them silent.
The error became `RetryError[Crashed]`,
which is why the third run catches `RetryError` rather than `Crashed`.
`Async` arrived because waiting between attempts is asynchronous.
And `Need[Time]` arrived, which is why `supply()` gained a `Time()`.
Retrying is not free: it needs a clock, and the signature says so.
If you leave the `Time()` out, `ty` rejects the `run()` call.
This is the thesis of both chapters applied to a cross-cutting concern.
Adding retry to a hundred call sites in a system with untracked Effects changes nothing you can see.
Here it changes a type, and every caller learns about the new dependency.

The renamed error invites a mistake the type checker accepts.
If you write `catch(Crashed)(retried)`, catching the error you started with,
nothing complains.
The result type gains a `Crashed` branch that cannot occur,
`RetryError[Crashed]` stays in the error channel,
and at runtime the failure passes the useless `catch()` and escapes at the edge.
`catch()` must name what the channel holds at the point of decoration,
and after `retry()` that is `RetryError[Crashed]`, not `Crashed`.

One rough edge: `RetryError` declares an `errors` attribute that `retry()` does not assign,
so the collected failures are reachable as `outcome.args[0]` and not as `outcome.errors`.

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
#: attempt 1: saving Morty
#: attempt 2: saving Morty
#: attempt 3: saving Morty
#: ('Morty saved', 'Morty saved', 'Morty saved')
```

The same schedule that governed three attempts now governs three runs,
and the tuple holds every result in order.
Where `retry()` stops at the first success,
`repeat()` continues until the schedule runs out,
and a failure on any run propagates unchanged rather than becoming a `RetryError`.

`memoize()` solves the spent-generator problem:

```python
# memoizing.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db = Database(failures=0)
bound = supply(db)(memoize(save_user))
print(run(bound("Morty")))
#: attempt 1: saving Morty
#: Morty saved
print(run(bound("Morty")))
#: Morty saved
print(f"attempts: {db.attempts}")
#: attempts: 1
```

Two runs, one attempt, and the second run still produces the value.
`memoize()` caches by argument the way `functools.lru_cache` does,
and it wraps the Effect in an object that records the result and replays it rather than driving the spent generator again.
That wrapper exists because a generator cannot run twice,
which is the same fact that made `retry()` decorate the function.

## Running Effects in Parallel

`fork()` hands an Effect to an `Executor` and returns a `Task`,
and `wait()` collects the result.
This is the same `wait()` that awaited a coroutine in [Waiting on a Coroutine](46_Effects--Stateless.md#waiting-on-a-coroutine).
It accepts a `Task` as readily as an awaitable:

```python
# parallel.py
import time
from concurrent.futures import Executor, ThreadPoolExecutor
from benchmark import report
from stateless import (
    Async,
    Depend,
    Need,
    Success,
    Task,
    as_type,
    fork,
    run,
    success,
    supply,
    wait,
)

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
That comes from the two loops.
`squares()` forks every task before it waits for any of them,
so the five sleeps overlap.
Forking and waiting inside a single loop makes each `wait()` block on the task the same iteration just created,
which runs the sleeps one after another and takes about five times as long.
The pool is an Ability, not a global,
so `squares()` declares `Need[Executor]` and names no pool.
Supplying a `ProcessPoolExecutor` instead moves the same work into processes,
with no change to `squares()`.
`as_type(Executor)` appears for the reason it always does:
`ThreadPoolExecutor` is the more specific type,
and `squares()` asked for the general one.

The type checker enforces one restriction.
A forked Effect must have nothing left to supply.
`fork()`'s four overloads accept an Effect whose Ability channel holds `Never`,
an exception type, or `Async`,
because `fork()` runs the Effect with `run()` inside the worker.
If you decorate a function that still declares a `Need`, `ty` rejects it,
listing the overloads it failed to match.
Supply first, then fork.

Notice who manages the pool's lifetime.
The `with` block sits outside `run()`, at the edge, in ordinary Python.
Stateless has no scoping mechanism of its own,
so either a resource lives in a `with` block outside the Effect,
as the pool does here, or the supplied object owns it:
the library's own `Files` class opens and closes a file inside a single `read_file()` call.
What you cannot express is acquiring a resource in one Effect and releasing it after a later one finishes,
which is the flat resource management a native Effect system provides.
Python's own answer to that is `ExitStack` in [Combining Context Managers](15_Techniques--Context_Managers.md#combining-context-managers),
which holds a set of managers decided at runtime and unwinds them together.
It flattens the nesting without knowing anything about Effects,
so this gap is narrower than it first appears.

## The Toolkit

Here is every tool from both chapters that acts on a description:
each one builds a description, rewrites a description's type, or executes one.
Three sit outside the tables.
`as_type()` relabels a value for the type checker and does nothing at runtime.
`spaced()` and `recurs()` build the `Schedule` that `retry()` and `repeat()` consume.

Four build a description:

| Tool | Applied to | What it does to the type |
|---|---|---|
| `success(value)` | A value | Wraps it as `Success[R]` |
| `throw(reason)` | An exception instance | Wraps it as `Try[E, Never]` |
| `need(C)` | A class | Builds `Depend[Need[C], C]`, producing an instance |
| `wait(target)` | A `Task` or any awaitable | Adds `Async`; produces the awaited `R` |

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
| `fork` | Adds `Need[Executor]`; the result becomes `Task[R]` |
| `@throws(*E)` | Adds each `E` to the error channel |

Three rows carry a caveat.
`fork` needs a function whose Effect has nothing left to supply,
so supply first, then fork.
`@throws` is an entry point rather than a transformation:
it decorates an ordinary function that raises exceptions,
turning it into one that returns an Effect.
`throw()` instead builds the failure as a description directly.
And `catch_all` comes from `stateless.effect`,
since the package root does not export it.

Two execute an Effect that has only `Async` and errors left,
raising a leftover error rather than returning it:

| Tool | Where to call it |
|---|---|
| `run(effect)` | From synchronous code |
| `await run_async(effect)` | From inside a running event loop |

These two are the only functions that perform work,
which is the description/execution split in table form.

## Where the Guarantee Stops

The guarantee has five limits.

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
A library can only check the ones you wrote down.
The guarantee is about consistency, not completeness.

The same hole opens on the error side.
Here `Success[float]` claims that `ratio()` cannot fail:

```python
# undeclared_failure.py
from stateless import Success, catch, run, success

def ratio(a: int, b: int) -> Success[float]:
    return success(a / b)

def caller() -> Success[float | ZeroDivisionError]:
    out: float | ZeroDivisionError
    out = yield from catch(ZeroDivisionError)(ratio)(1, 0)
    return out

try:
    run(caller())
except ZeroDivisionError as e:
    print(e)
#: division by zero
```

`@throws` lifts only the exception types it names, and `ratio()` names none,
so the `ZeroDivisionError` propagates as an ordinary raised exception,
untracked.
`catch()` matches the values an Effect yields, not exceptions the body raises,
so a failure `@throws` never lifted goes past `catch()` untouched.
That is the version of this hole to watch for,
because `catch(ZeroDivisionError)` type-checks and then does nothing:
the protection appears to be there.
The channel carries only what you put into it.

ZIO does not catch this at compile time either.
Its own documentation uses the same example:
`def divide(a: Int, b: Int): ZIO[Any, Nothing, Int] = ZIO.succeed(a / b)` declares an error type of `Nothing`,
and a zero denominator still throws.
The difference is at runtime.
An exception thrown inside a computation ZIO runs becomes a *defect*,
recorded on the `Cause` beside the typed error channel,
where `sandbox()` can recover it and the runtime logs it as a dying fiber.
Stateless has no defect channel,
so the exception leaves `run()` as an ordinary Python exception.

### 2. The type checker can give up quietly

How much of a type survives partial handling depends on your type checker rather than on the library.
Handling some of what an Effect declares works correctly under `ty` 0.0.75.
If you supply one of two Abilities, the other stays in the signature:

```python
# partial_handling.py
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
try:
    run(half())  # type: ignore
except MissingAbilityError as e:
    print(e)
#: Need(t=<class '__main__.Log'>)
```

`half` is `() -> Depend[Need[Log], None]`.
The handler subtracts the `Console` and not the `Log`,
so `run()` rejects it before the program starts:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
  --> partial_handling.py:18:9
   |
18 |     run(half())
   |         ^^^^^^ Expected
   |         `Generator[Async | Exception, Any, Unknown]`, found
   |         `Generator[Need[Log], Any, None]`
```

The `# type: ignore` lets the listing run far enough to show the matching runtime failure.
`catch()` behaves the same way.
If you catch one of two declared errors, the other stays in the error channel.

What still defeats the type checker is applying two handlers in one expression.
If you write `handle(scripted)(handle(capture)(greet))`,
`ty` gives up on the nested inference and infers `Unknown`,
which is permissive enough to hide a genuinely missing handler.
If you name the intermediate, the types come back:

```python
half = handle(capture)(greet)  # () -> Depend[Ask, None]
full = handle(scripted)(half)  # () -> Success[None]
```

That is why `ask_tell_stateless.py` binds `half` and `full` instead of nesting the calls.
Keep the habit generally:
a named intermediate is where you read the Ability that remains,
which is the information this library exists to give you.
That makes two type-checker gaps: the nested handler expression here,
and the direct Ability yield that types as `Unknown`.
Each has the same shape.
The library's types ask the type checker a hard inference question,
and where the type checker gives up, it gives up quietly.
Trust a green check only where a red one has shown you it can appear.

### 3. Handlers cannot capture the continuation

`Effect` is a monad.
`success()` lifts a value into it, `yield from` chains two of them together,
and the generator body is syntax that hides the chaining.
`Result` in [Error Handling](42_Functional--Error_Handling.md#composing-with-bind)
had the same two operations, written out by hand.
The library's documentation calls this an algebraic effect system,
and both descriptions are right.
A monad plus handlers is how you build algebraic effects in a language with no native support for them.
The monad is the plumbing, and the handlers are the interface.

What a library cannot copy is the handler's power.
`handle()` passes a handler the Ability and takes back an answer,
and the driver resumes the Effect with that answer, once, always.
A native handler instead receives the *continuation* and chooses what to do with it.
Invoking it once gives you what Stateless has.
Declining to invoke it makes the handled scope produce the handler's value instead,
which is how an exception behaves.
Invoking it repeatedly gives you backtracking and search.
Stateless offers only the first, a *tail-resumptive* handler.
The ceiling is the substrate rather than the design.
A Python generator is one-shot, so a handler has nothing to resume twice.

Two pieces of the library show that ceiling.
`Effect[A, E, R]` carries a separate `E` that `@throws` and `catch()` work.
Koka needs no such type parameter,
because an exception there is an ordinary Effect whose handler declines to resume.
The extra type parameter exists because a Stateless Ability cannot fail,
and the `ZIO[R, E, A]` of [Effect Management](44_Effects--Effect_Management.md#library-effect-management)
carries one for the same reason.
`Async` is the other piece.
Native systems derive asynchronous execution from Effects.
Stateless provides `Async` as a built-in that `run()` interprets,
because the driver loop can await where a handler cannot.

### 4. The discipline is all-or-nothing

Every effectful function becomes a generator function,
so it cannot also be a plain function,
and calling it returns a description that somebody must run.
Type errors from a library this generic are long and mention internals.
And a third-party function that knows nothing about Effects needs a `@throws` wrapper or a `need()` route before it can participate.
An EMS is a decision about a whole codebase,
not a utility you import for one module.

### 5. Much of a mature Effect system is missing

Dependency wiring is the first gap,
and `bakery.py` in [Dependencies That Need Dependencies](#dependencies-that-need-dependencies)
showed its shape.
`supply()` binds instances that are already built,
and `handle()` takes an ordinary function,
so constructing a dependency cannot be an Effect.
ZIO's `ZLayer` is a constructor that can read configuration, fail, and retry,
and it resolves a dependency graph at compile time,
reporting a cycle or a missing provider by name.
Stateless has no equivalent, so you write the wiring at the edge by hand,
and the type checker verifies a `supply()` call for completeness but not for how you assembled it.
The operator set is thin in the same way.
The library has `retry()` and `repeat()`,
and `Schedule` offers a fixed interval and a repeat count,
with no exponential backoff and no jitter.
Stateless provides no timeout, no `race`, no fallback combinator,
and no finalizer, which rules out the hedging strategy that races a delayed second request.
Concurrency is `fork()` and `wait()` with no guarded mutable cell.
Forking two Effects that share the `Cell` of [State as an Ability](#state-as-an-ability)
produces a race no type reports,
so shared state between forked Effects is your problem and Python's,
with no help from the type checker.
Above that sit the resilience patterns a production system eventually needs
(rate limiting, bulkheads, and circuit breakers), none of which exist here.
The library is a working demonstration of Effect tracking in Python's type system,
and that is different from a platform for building distributed systems.

## What Survives the Library

[Effect Management](44_Effects--Effect_Management.md#effects-are-the-next-barrier)
argued that Effects are the next scaling barrier,
and that the tracking will eventually move into the language.
Stateless shows what that looks like inside Python today,
which is the value of studying it, whether or not you use it in production.

Consider the signatures once more:

- `Success[int]`: pure.
- `Depend[Need[Console], None]`: prints, somehow,
  through something supplied later.
- `Effect[Need[Console], KeyError, None]`: prints, might not find the name.

Each one describes what a function depends on, what it can produce,
and how it can fail, before you read a single line of the body.
That is the property this book has been circling since [Foundations](40_Functional--Foundations.md#pure-functions).
Purity is valuable because it is verifiable,
and verifying it by reading code does not scale.

A second gain shows when you put functions together.
Python has a separate mechanism for each concern an Effect type carries.
Absence is `T | None`.
Failure is a raised exception,
or the `Result` that [Error Handling](42_Functional--Error_Handling.md#a-result-type)
built.
Asynchrony is `async def` and `await`.
A resource's lifetime is a `with` block.
Each is reasonable alone, and they do not compose with each other.
Some pairs allow no conversion.
An `Awaitable` cannot become a `Result` without blocking and giving up the asynchrony.
A `with` block's guarantee is lexical,
so you cannot hand it to a caller as a value the way you can a `Result`.
Consider a function that awaits, might fail, and holds a resource.
It uses three of these mechanisms, and its return type mentions one.

`Effect[A, E, R]` is one type for the dependency, the failure, and the result,
and `yield from` is one operator for joining two Effects.
`research()` joined five steps of two kinds with that one operator,
once `@throws` had brought the ordinary functions in at the boundary.
`Async` is one more Ability in the same channel rather than a second viral annotation.
Resource lifetime is the concern this does not absorb.
Stateless has no scoping mechanism, so `with` blocks stay where they are.
They need not stay nested, since `ExitStack` flattens them,
but they remain a separate mechanism from the Effect type.

What Stateless requires for that property is the generator discipline,
the description/execution split, and an ecosystem that has never heard of it.
For most Python code that price is too high.
The techniques in [Converting Effectful to Pure](44_Effects--Effect_Management.md#converting-effectful-to-pure)
(returning a `Result`, restricting a type so bad values cannot exist, and passing dependencies in rather than constructing them)
capture much of the benefit at a fraction of the cost.
Use Stateless when a system is large enough that hidden Effects have already cost you a production incident,
and when the team will hold the line at every boundary.
Below that scale, the discipline matters and the machinery is optional.

Whatever you decide about the library, the habit survives it.
Name each contact with the outside (the clock, the feed, the pool, the console)
and bind it at the edge instead of calling it in the middle.
`at()` and `crossing` and `controller()` are all that habit,
and none of them needs an Effect type to work.

But watch the direction.
Python got one Effect tracked into its type system with `async`.
The languages listed under [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
track all of them.
Stateless is the demonstration that Python's type system is expressive enough to do it,
given a library willing to encode everything into return types.
What is missing is not the capacity.
It is a language that does the encoding for you.

## Exercises

1.  `crossing` in `midnight.py` walks a fixed list, so it answers two requests.
    Write a handler that instead advances a stored moment by one second at each request,
    and confirm `archive()` still crosses midnight under it.
    Then rewrite `archive()` so the file name and the stamp cannot disagree,
    and explain why no handler can reproduce the bug afterward.
2.  `leaky_effect.py` type-checks while lying about its purity.
    Describe a review rule or a lint check that catches it,
    and explain why a type checker cannot.
    Then demonstrate the error-side twin:
    write a function that raises a `KeyError` with no `@throws`,
    wrap it in `catch(KeyError)`, and run it on a failing input.
    Explain what the types claim, what the run does,
    and which line restores the guarantee.
3.  Add a wind turbine to `power.py` that is available only during a fixed windy stretch of the evening,
    put it between solar and the battery in `controller()`,
    and confirm `run_load()` needs no change.
    Then shorten every source until some hour has no supplier, run it,
    and say where the `Blackout` surfaces and why `catch(Blackout)` around `run_load()` does not intercept it.
4.  Write a handler for `Outlet` that ignores `request.hour` and hands out a fixed sequence of sources,
    the way `scripted` handed out a fixed sequence of tosses.
    Use it to test that `run_load()` re-requests after a failure,
    with no weather, no clock, and no battery model.
    Then say what such a test cannot tell you about `controller()`.
5.  Add a fourth failure to `research()`:
    a `TooLong` raised when an article exceeds some length.
    Follow the type checker's complaints until the program type-checks again,
    and list every line you edited.
    Then do the same to `research_by_hand.py` and say which tool told you where to go in each case.
6.  `scenarios.py` supplies a `DeadWire` that fails before printing.
    Write a `DullWire` whose `latest()` succeeds but returns a headline with no topic in `TOPICS`,
    and predict the trace before running it.
7.  Wrap `research()` in `retry()` and supply a `Time()`.
    Explain what happens under the `WEATHER` scenario and why retrying a `NotInteresting` failure is the wrong behavior,
    then say what an Effect system needs for you to retry only `Unavailable`.
8.  Change `parallel.py` to use a `ProcessPoolExecutor` instead of a `ThreadPoolExecutor`,
    and confirm `squares()` stays unchanged.
    Then try to fork an Effect that still declares a `Need`,
    and record what `ty` says.
9.  `wallet.py` runs `spree()` against a `Cell`.
    Script it instead: write a `Get` handler that answers from a fixed sequence of balances and a `Put` handler that appends every request to a list,
    the way `scripted` fed `Flip`.
    Assert that `spree()` attempts every price and writes once per purchase.
    Then say what this test cannot detect that the `Cell` version can.
10. `fetch_nonempty()` puts `Empty` into the channel with `throw()`.
    Rewrite it to raise `Empty` in the body and lift it with `@throws(Empty)`,
    and confirm the two versions type-check and behave identically.
    Then make each version fail with an undeclared exception type and compare what `ty` reports for each.
11. Exercise 5 added a `TooLong` failure to `research()`.
    Repeat it with `catch_everything.py` in the build:
    predict what `ty` reports in `outcome()`, then confirm.
    Remove `outcome()`'s return annotation and rerun `ty`,
    and explain what the type checker stopped verifying.
12. Write a `Random` Ability whose handler returns an `int` in a range carried on the request,
    and an accessor `roll(low, high)` for it.
    Use it to write a dice game as an Effect, then run the game twice:
    once with a handler that calls `random.randint()`,
    and once with a handler that walks a scripted sequence.
    Then delete the `low: int` annotation from the accessor's parameter and say what changes,
    and delete the annotation on the *handler's* parameter and say what changes.
13. Add a `Butter` appliance to `bakery.py` and a `buttered()` Effect that needs it and calls `toast()`.
    Write `buttered()`'s signature with only `Need[Butter]` first, run `ty`,
    and read the diagnostic before fixing it.
    Then remove `Toaster(3)` from `supply()` and say which of the two diagnostics tells you about a dependency two levels down.
14. `play()` in `casts.py` accepts any five actors, matched or not.
    Give `kitties_and_puzzles()` and `warriors_and_weapons()` a shared signature so a caller can pass either one where a cast belongs,
    and say what that recovers of the Abstract Factory and what it does not.
    Then add a sixth actor to `encounter()` and count the lines you edit in `quest.py`,
    `casts.py`, and `two_games.py`.
