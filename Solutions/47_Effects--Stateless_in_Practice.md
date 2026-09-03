# Stateless in Practice: Solutions

## 1. An advancing handler, and the fix it cannot break

```python
# advancing_clock.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
from stateless import Ability, Depend, handle, run

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment

def ticking(
    start: datetime, step: timedelta
) -> Callable[[Now], datetime]:
    moment = start
    def advancing(request: Now) -> datetime:
        nonlocal moment
        current = moment
        moment += step
        return current
    return advancing

def archive_twice(
    entry: str
) -> Depend[Now, tuple[str, str]]:
    opened = yield from now()
    path = f"log-{opened:%Y-%m-%d}.txt"
    stamped = yield from now()
    return path, f"[{stamped:%Y-%m-%d}] {entry}"

def archive_once(
    entry: str
) -> Depend[Now, tuple[str, str]]:
    moment = yield from now()
    path = f"log-{moment:%Y-%m-%d}.txt"
    return path, f"[{moment:%Y-%m-%d}] {entry}"

LATE: Final[datetime] = datetime(2026, 1, 1, 23, 59, 59)
SECOND: Final[timedelta] = timedelta(seconds=1)

print(run(
    handle(ticking(LATE, SECOND))(archive_twice)("ok")))
#: ('log-2026-01-01.txt', '[2026-01-02] ok')
print(run(
    handle(ticking(LATE, SECOND))(archive_once)("ok")))
#: ('log-2026-01-01.txt', '[2026-01-01] ok')
```

`ticking()` is a handler factory.
It stores a moment.
The handler answers each request with the current value,
then advances the stored moment by `step`.
`nonlocal` makes the handler stateful.
Without it, `moment += step` binds a local name,
and every request answers the same instant.
`crossing` in `midnight.py` walks a two-element list and stops there,
while `ticking()` answers any number of requests,
so the same handler serves an Effect that reads the clock three times or thirty.
Each call to `ticking()` builds a fresh handler with its own stored moment,
so both runs in the listing start at 23:59:59.

`archive_twice()` is the original function.
The first request names the file for January 1 and the second stamps the entry January 2,
so the bug survives the change of handler.
It should.
Nothing about the handler caused it.

`archive_once()` reads the clock one time and derives both strings from that value.
The mismatch needed two readings that could differ.
With one reading, the two strings cannot disagree.
A handler still chooses the moment, and it can choose 23:59:59,
but both strings then carry that moment.
No handler can reproduce the bug, because the bug was not in the handler.
It was in a function that asked twice and treated the answers as one.

That is the general shape of a clock bug.
Reading a clock twice reads a changing value twice,
and two readings are two facts rather than one.
Naming the clock as an ability made the failure reproducible.
Deriving both strings from a single reading removed it.

## 2. A leak the type checker cannot see

The rule that catches `leaky_effect.py` is a reading rule about one line:
a function whose return type is an `Effect` and whose body is not a generator
must contain nothing but the expression it returns.

```python
def double(n: int) -> Success[int]:
    return success(n * 2)  # Nothing above this line
```

Put a `print()`, an `open()`, a mutation, or a call to any function that does one
of those above the `return`, and it runs while the caller builds the description
rather than while `run()` executes it,
the opposite of what the signature advertises.
A linter can enforce a conservative version of that rule:
flag any function annotated `Effect[...]`, `Depend[...]`, `Success[...]`, or `Try[...]`
that contains no `yield` and whose body is more than a single `return` statement.
That rule has false positives, since a pure local computation above the `return` is harmless,
but the shape it looks for is the shape a leak takes.

A type checker cannot do this because purity is not a type.
`print()` is a call returning `None`, legal in any function,
and Python's type system says what values a function accepts and produces,
not what its body touches on the way.
The annotation `Success[int]` describes the returned object,
and `success(n * 2)` genuinely produces one, so nothing is inconsistent.
An effect-tracking language puts the side effect in the signature.
These two chapters simulate that by hand,
so the guarantee holds only for effects that go through `yield`.

The error side has the same hole:

```python
# exercise_2.py
from typing import Final
from stateless import Success, catch, run, success, throws

RAW: Final[dict[str, int]] = {"Alice": 42}

def size(name: str) -> Success[int]:
    return success(RAW[name])  # KeyError, undeclared

def caller() -> Success[int | KeyError]:
    out: int | KeyError = (
        yield from catch(KeyError)(size)("Bob"))
    return out

try:
    run(caller())
except KeyError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: KeyError: 'Bob'

@throws(KeyError)
def declared_size(name: str) -> int:
    return RAW[name]

def fixed() -> Success[int | KeyError]:
    caught = catch(KeyError)(declared_size)
    out: int | KeyError = yield from caught("Bob")
    return out

print(type(run(fixed())).__name__)
#: KeyError
```

The types claim that `catch()` handles the `KeyError`.
`catch(KeyError)(size)` says it moves a `KeyError` from the failure channel to the
return channel, and `caller()`'s `int | KeyError` says the caller is ready for either.
The run does something else.
`RAW["Bob"]` raises a `KeyError` while `size()` is still building its description,
before the Effect exists and long before `catch()` has anything to watch,
so the exception unwinds the stack in the ordinary way and escapes `run()` entirely.
`catch()` cannot catch what never entered the channel.

The line that restores the guarantee is `@throws(KeyError)`.
It turns `declared_size()` into a function that yields its failure instead of
raising it, so the exception becomes a value travelling the error channel.
`catch()` then does what its type says: `run(fixed())` returns the `KeyError`
rather than raising it.
`success()` is for a value you already have. `@throws` is for work that can fail.

## Shared code: the microgrid

Exercises 3 and 4 both use the chapter's microgrid, repeated here without its
demo so the two listings can import it:

```python
# grid.py
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Protocol
from stateless import Ability, Depend, catch, throws

class Drained(Exception):
    pass

class Blackout(Exception):
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
class Turbine:
    windy: range
    def available(self, hour: int) -> bool:
        return hour in self.windy
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

def run_load(
    start: int, hours: int
) -> Depend[Outlet, None]:
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

`Turbine` is the only addition: a source available during a fixed range of hours,
depleting nothing, since wind costs no fuel.

## 3. A wind turbine between solar and the battery

```python
# exercise_3.py
from grid import (
    Backup,
    Battery,
    Blackout,
    Grid,
    Solar,
    Turbine,
    controller,
    run_load,
)
from stateless import handle, run

full = controller((Solar(), Turbine(range(19, 22)),
                   Battery(40), Grid(range(22, 24)),
                   Backup(3)))
run(handle(full)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Turbine online
#:   19:00
#:   20:00
#:   21:00
#: Turbine offline
#: Battery online
#:   22:00
#: Battery offline

short = controller((Solar(), Turbine(range(19, 20)),
                    Battery(0), Grid(range(0, 24)),
                    Backup(0)))
try:
    run(handle(short)(run_load)(17, 6))
except Blackout as e:
    print(f"Blackout at hour {e.args[0]}, out of run()")
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Turbine online
#:   19:00
#: Turbine offline
#: Blackout at hour 20, out of run()
```

The turbine takes the evening hours the battery used to cover, and the battery
drops back to one hour at 22:00 once the wind stops.
`run_load()` needs no change, and could not have needed one: it asks for a
`Source` at an hour and uses whatever the handler hands back.
The handler decides which sources exist, which order it prefers them in, and
whether one of them is new.
That is the same substitution `Console` and `Feed` allow, applied to a choice
made fresh at every request rather than once at the start.

With every source shortened, hour 20 has no supplier, and the `Blackout`
surfaces out of `run()`, not out of the Effect.
`catch(Blackout)` around `run_load()` does not intercept it because `catch()`
watches the error channel, and this exception never entered that channel.
`choose()`, the handler, raises the `Blackout`, and a handler runs inside the
driver while it answers a request.
No `yield` sits between the `raise` and `run()`'s own stack frame,
so the exception unwinds the driver in the ordinary Python way,
past the suspended Effect rather than through it.

Exercise 2 draws the same distinction from the other side.
A failure is part of the Effect only if it travels as a value,
and a `raise` in code the driver calls is outside the description.
Making a `Blackout` catchable means giving the Ability a failure type,
so the handler returns a value rather than raising an exception,
and `plug()` declares the failure it can produce.

## 4. A scripted outlet

```python
# exercise_4.py
from collections.abc import Callable, Iterator
from grid import Outlet, Solar, Source, run_load
from stateless import handle, run

def scripted(
    sources: Iterator[Source]
) -> Callable[[Outlet], Source]:
    # request.hour ignored
    def choose(request: Outlet) -> Source:
        return next(sources)
    return choose

class Dead:  # Never available, so every draw fails
    def available(self, hour: int) -> bool:
        return False
    def deplete(self) -> None:
        pass

sequence = iter([Dead(), Dead(), Solar()])
run(handle(scripted(sequence))(run_load)(10, 2))
#: Dead online
#: Dead offline
#: Dead online
#: Dead offline
#: Solar online
#:   10:00
#:   11:00
#: Solar offline
```

Three requests for two hours of power. The first two hand back a `Dead` source
that fails immediately, and `run_load()` responds by breaking out of the inner
loop, leaving the `connected` block, and asking for another source.
The third request produces a working one, which then covers both hours.
The test pins down that re-request behavior with no weather, no clock, and no
battery: the handler answers from a list.

What the test cannot tell you is whether `controller()` is right.
Every question about policy is out of its reach: whether `controller()` prefers
solar before the battery, whether the battery reports itself unavailable once
exhausted, whether the hour `controller()` asks about is the hour `run_load()`
draws power for. The scripted handler ignores `request.hour` entirely, and that
omission is the source of both its convenience and its blindness.
It tests the consumer of the Ability while saying nothing about the producer.
`controller()` needs its own test, and that test can be an ordinary one:
`controller()` builds a plain function from an `Outlet` to a `Source`, with no
Effect in sight.

## Shared code: the research pipeline

The chapter's `research.py` and the doubles from `scenarios.py` appear here
without their demos, so the listings that follow can import them:

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

```python
# feeds.py
from dataclasses import dataclass
from typing import Final
from research import NoArticle, Unavailable

@dataclass
class Wire:
    headline: str
    def latest(self) -> str:
        print("feed: fetching")
        return self.headline

class DeadWire:
    def latest(self) -> str:
        raise Unavailable("offline")

class DullWire:
    def latest(self) -> str:
        print("feed: fetching")
        return "local council approves new roundabout"

@dataclass
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
LONG: Final[Library] = Library({"genome": "chapter " * 40})
```

```python
# report.py
from typing import assert_never
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    research,
)
from stateless import Depend, Need, catch

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
```

## 5. A fourth failure

```python
# research_long.py
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
    fetch,
    look_up,
    topic_of,
)
from stateless import Effect, Need, need, throws

class TooLong(Exception):
    pass

LIMIT: int = 100

@throws(TooLong)
def within_limit(article: str) -> str:
    if len(article) > LIMIT:
        raise TooLong(f"{len(article)} characters")
    return article

def research() -> Effect[
    Need[Feed] | Need[Encyclopedia],
    Unavailable | NotInteresting | NoArticle | TooLong,
    str,
]:
    feed = yield from need(Feed)
    headline = yield from fetch(feed)
    topic = yield from topic_of(headline)
    book = yield from need(Encyclopedia)
    article = yield from look_up(book, topic)
    checked = yield from within_limit(article)
    return checked
```

Four edits, and the type checker names three of them.

1. A new exception class, `TooLong`.
2. A new `@throws(TooLong)` function, `within_limit()`, since a failure has to be
   lifted before it can travel.
3. One new line in `research()`, the `yield from within_limit(article)`.
4. `research()`'s error parameter, widened to include `TooLong`.

Adding line 3 without line 4 is the one `ty` reports, at the new line rather than
at the signature: `expression of type 'TooLong', expected 'Need[Feed] |
Need[Encyclopedia] | Unavailable | NotInteresting | NoArticle'`.
Fixing that then breaks every caller that named the old set. `report()` stops at
its own `yield from` with the same `invalid-yield`, now carrying `TooLong` in the
type it did not expect. Widen `catch()` and the `found:` annotation to match, and
`assert_never()` reports `TooLong` as an unhandled branch. Every one of these is a
compile-time stop rather than a surprise in production.
The type checker walked the change through the program, one edit at a time.

The by-hand version takes a comparable edit and reports none of it:

```python
# research_by_hand.py
from feeds import Library, Wire
from research import (
    TOPICS,
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
)
from research_long import LIMIT, TooLong

def topic_of(headline: str) -> str:
    for candidate in TOPICS:
        if candidate in headline:
            return candidate
    raise NotInteresting(headline)

def within_limit(article: str) -> str:
    if len(article) > LIMIT:
        raise TooLong(f"{len(article)} characters")
    return article

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
        return within_limit(book.article(topic))
    except NoArticle:
        return "no article on that topic"
    except TooLong:
        return "article too long"

print(research_and_report(
    Wire("genome mapped"),
    Library({"genome": "short enough"})))
#: feed: fetching
#: library: looking up genome
#: short enough
```

In the Effect version, `ty` told you where to go: it flagged the undeclared
failure at the delegation that introduced it, then the widened union at every
caller that had claimed to handle everything.
In the by-hand version nothing told you anything.
Adding `except TooLong` to the third `try` was a choice you make by reading the
code. Forget it, and a `TooLong` escapes `research_and_report()`, whose
signature still says it returns a `str` no matter what.
Both versions run. Only one of them has a tool that knows the set of failures
changed.

## 6. A dull headline

```python
# exercise_6.py
from feeds import SHELF, DullWire
from report import report
from research import Encyclopedia, Feed
from stateless import run, supply

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(DullWire(), SHELF))
#: feed: fetching
#: nothing worth researching
```

The prediction is two lines: `feed: fetching`, then
`nothing worth researching`.

`DullWire.latest()` succeeds, so `fetch()` returns a headline and the feed's own
trace line prints, a line `DeadWire` never reached.
The pipeline then stops one step later. `topic_of()` scans `TOPICS` for
`"stock market"` and `"genome"`, finds neither in a headline about a roundabout,
and raises `NotInteresting`, which `@throws` sends into the error channel.
`research()` never reaches `need(Encyclopedia)`, so no library lookup happens
and no `library:` line prints.

`DullWire` and `WEATHER` produce identical traces, and that sameness is the
useful part. `DullWire` is a class whose method returns a fixed uninteresting
string, while `WEATHER` is a `Wire` holding one, so they differ in construction
and not in behavior.
`report()` cannot tell the two apart, and that is the point of a test double:
the Effect sees a `Feed`, and every `Feed` that behaves the same way is the same
scenario.

## 7. Retrying the wrong failure

```python
# exercise_7.py
from datetime import timedelta
from feeds import SHELF, WEATHER
from research import Encyclopedia, Feed, research
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

THREE = recurs(3, spaced(timedelta(milliseconds=1)))

def attempt(
    feed: Feed, book: Encyclopedia
) -> str | RetryError:
    # Named, so ty follows it
    retried = retry(THREE)(research)
    caught = catch(RetryError)(retried)
    return run(supply(feed, book, Time())(caught)())

outcome = attempt(WEATHER, SHELF)
#: feed: fetching
#: feed: fetching
#: feed: fetching
print(type(outcome).__name__)
#: RetryError
if isinstance(outcome, RetryError):
    for failure in outcome.args[0]:
        print(f"  {type(failure).__name__}: {failure}")
#:   NotInteresting: mild and cloudy
#:   NotInteresting: mild and cloudy
#:   NotInteresting: mild and cloudy
```

Under `WEATHER`, `fetch()` reads the feed three times, each attempt fails with
the same `NotInteresting`, and the retry gives up with a `RetryError` carrying
three identical failures.

Retrying is the wrong behavior because this failure is deterministic.
`WEATHER`'s headline is the same on every attempt, and `TOPICS` holds the same
two topics, so `topic_of()` returns the same answer however many times it runs.
The retry costs three fetches and two sleeps to arrive at the answer the first
attempt already had, and it turns a clear `NotInteresting` into a `RetryError`
that the caller has to unwrap. `Unavailable` is the failure worth retrying: a
feed that is offline now may be online in a moment, so another attempt can
succeed.

Distinguishing them needs something the library does not offer:
a retry that selects on the error type.
`retry()` here applies to the whole error channel, treating every declared
failure as transient, because its schedule decides *when* to try again and
nothing decides *whether* to. ZIO spells the missing piece `retryWhile`, a
retry taking a predicate on the error. Without it, selective behavior means
narrowing the channel first: `catch()` the failures that retrying cannot help,
so they leave the error channel and become values, then apply `retry()` to what
remains. That is more machinery than a predicate, and it changes the result
type. Both are the honest cost of a missing operator.

## 8. Processes instead of threads

```python
import time
from concurrent.futures import Executor, ProcessPoolExecutor
from stateless import (
    Async, Depend, Need, Success, Task, as_type, fork, run,
    success, supply, wait,
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

# Required: workers re-import this module
if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=5) as pool:
        out = run(
            supply(as_type(Executor)(pool))(squares)(5))
    print(out)
```

```text
[0, 1, 4, 9, 16]
```

`squares()` stays the same, character for character. It asks for an `Executor`
and never says which kind, so a process pool satisfies the request as a thread
pool did. Two things around it did change, and neither is in the Effect.
The `__main__` guard is now required, because a process pool starts workers by
re-importing the module, and without the guard each worker builds another pool.
This book's output checker also skips the listing, for the same reason:
`slow_square()` must be picklable by name from an importable module, and code
executed inside another program's process is not importable that way.

Forking an Effect that still declares a `Need` does not type-check:

```python
@fork
def announce(n: int) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"{n}")
```

```text
error[no-matching-overload]: No overload of function `fork` matches arguments
info: Possible overloads for function `fork`:
info:   [**P, R](f: (**P) -> Generator[Never, Any, R])
info:            -> ((**P) -> Generator[Need[Executor], Any, Task[R]])
info:   [**P, E, R](f: (**P) -> Generator[E, Any, R])
info:            -> ((**P) -> Generator[Need[Executor], Any, Task[R]])
info:   [**P, R](f: (**P) -> Generator[Async, Any, R])
info:            -> ((**P) -> Generator[Need[Executor], Any, Task[R]])
info:   [**P, E, R](f: (**P) -> Generator[Async | E, Any, R])
info:            -> ((**P) -> Generator[Need[Executor], Any, Task[R]])
```

Every overload accepts an Effect whose yield channel holds errors, `Async`, or
nothing, and none accepts one holding an Ability. The forked work leaves the
driver: it runs in a worker with no access to the handler stack that would
answer a request. So you must remove the requirement before the fork: supply it
first and fork the bound function. The type system enforces a rule about where a
handler can answer a request, and that is the same guarantee running through
both chapters, applied to a boundary between threads or processes.

## 9. A scripted wallet

```python
# test_ch47_wallet.py
from collections.abc import Callable, Iterator
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

def spree(
    prices: tuple[int, ...]
) -> Depend[Get | Put, int]:
    bought = 0
    for price in prices:
        if (yield from purchase(price)):
            bought += 1
    return bought

def reading(
    balances: Iterator[int]
) -> Callable[[Get], int]:
    def read(request: Get) -> int:
        return next(balances)
    return read

def recording(written: list[int]) -> Callable[[Put], None]:
    def write(request: Put) -> None:
        written.append(request.amount)
    return write

def test_spree_attempts_every_price() -> None:
    written: list[int] = []
    balances = iter([100, 40, 40, 10])
    half = handle(reading(balances))(spree)
    shop = handle(recording(written))(half)
    assert run(shop((60, 50, 30, 20))) == 2
    assert written == [40, 10]
    assert next(balances, None) is None  # All four read

written: list[int] = []
scripted = handle(recording(written))(
    handle(reading(iter([100, 40, 40, 10])))(spree))
print(run(scripted((60, 50, 30, 20))), written)
#: 2 [40, 10]
```

The scripted balances are the four the `Cell` version would have produced:
`100` before the first purchase, `40` after it, `40` again because `purchase()`
refuses the `50` and writes nothing, and `10` after the `30` goes through.
`spree()` attempts all four prices, and the test proves it from both sides.
A fifth attempt would raise a `StopIteration` from `read()`. Stopping early
would leave a balance unread, and the final assertion catches that by checking
that the iterator has nothing left.
`written` records one entry per successful purchase, `[40, 10]`, so the
assertions together say that `spree()` tried every price and wrote only the
affordable ones.

What this test cannot check is whether the two handlers agree. The `Cell`
version has one piece of state, so the next `Get` returns whatever the last
`Put` wrote. Here the test scripts the balances independently of the writes, so
a `spree()` that wrote the wrong amount, say `funds` instead of `funds - price`,
would still see the same balance sequence and still pass.
The scripted test checks the Effect's shape: which requests the Effect makes, in
which order, with which payloads.
The `Cell` test checks that the requests compose into correct arithmetic.
Both are worth having, and each one's blind spot is the other's subject.

## 10. `throw()` and `@throws` side by side

```python
# exercise_10.py
from dataclasses import dataclass
from stateless import (
    Effect,
    Need,
    catch,
    need,
    run,
    supply,
    throw,
    throws,
)

class Unavailable(Exception):
    pass

class Empty(Exception):
    pass

@dataclass
class Ticker:
    headline: str
    def latest(self) -> str:
        return self.headline

@throws(Unavailable)
def fetch(feed: Ticker) -> str:
    return feed.latest()

def thrown() -> Effect[
    Need[Ticker], Unavailable | Empty, str
]:
    feed = yield from need(Ticker)
    headline = yield from fetch(feed)
    if not headline:
        yield from throw(Empty())
    return headline

@throws(Empty)
def nonempty(headline: str) -> str:
    if not headline:
        raise Empty()
    return headline

def lifted() -> Effect[
    Need[Ticker], Unavailable | Empty, str
]:
    feed = yield from need(Ticker)
    headline = yield from fetch(feed)
    checked = yield from nonempty(headline)
    return checked

for version in (thrown, lifted):
    guarded = catch(Unavailable, Empty)(version)
    for feed in (Ticker("markets close mixed"), Ticker("")):
        result = run(supply(feed)(guarded)())
        print(f"{version.__name__}: {result!r}")
#: thrown: 'markets close mixed'
#: thrown: Empty()
#: lifted: 'markets close mixed'
#: lifted: Empty()
```

The two versions have the same signature and produce the same results, as the
loop demonstrates: identical types, identical behavior on both inputs.
They differ in where you write the failure. `throw()` puts an exception into
the channel at the point of the `yield from`, inside the Effect. `@throws` lifts
a function that raises an exception, so the `raise` sits in an ordinary function
and the decorator does the moving.

Prefer `@throws` when the check is reusable or belongs to the value rather than
the pipeline, as `nonempty()` does. Prefer `throw()` for a condition that only
makes sense at that point in the Effect.

Making each version fail with an undeclared type shows the same asymmetry
exercise 2 found. Change `throw(Empty())` to `throw(ValueError())` and `ty`
reports it at that line: the yielded type is `ValueError` and the annotation
allows `Need[Ticker] | Unavailable | Empty`. Change `nonempty()`'s body to
`raise ValueError()` while its decorator still says `@throws(Empty)`, and `ty`
reports nothing at all. The decorator's argument is a claim about the function,
not a check on it, and a `raise` inside a function body is invisible to a type
checker in Python. So `ty` verifies the version whose failure travels through a
`yield`, and trusts the version whose failure starts as a `raise`.

## 11. A fourth failure, with `catch_all()`

```python
# exercise_11.py
from dataclasses import dataclass
from research import (
    Encyclopedia,
    Feed,
    NoArticle,
    NotInteresting,
    Unavailable,
)
from research_long import TooLong, research
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

class LongShelf:
    def article(self, topic: str) -> str:
        return "chapter " * 40

def outcome(
    feed: Feed, book: Encyclopedia
) -> (str | Unavailable | NotInteresting | NoArticle
      | TooLong):
    bound = supply(feed, book)(research)
    return run(catch_all(bound)())

dull = outcome(Bulletin("mild and cloudy"), BareShelf())
print(type(dull).__name__)
#: NotInteresting
missing = outcome(Bulletin("genome mapped"), BareShelf())
print(type(missing).__name__)
#: NoArticle
long = outcome(Bulletin("genome mapped"), LongShelf())
print(type(long).__name__)
#: TooLong
```

The prediction is that `outcome()`'s return annotation breaks.
`catch_all()` moves the entire error channel into the return type, so widening
`research()`'s failures to include `TooLong` widens what `catch_all()` returns,
and the declared
`str | Unavailable | NotInteresting | NoArticle` no longer covers it.
`ty` reports an `invalid-return-type` on the `return run(...)` line, naming
`TooLong` as the member that does not fit. Adding `| TooLong` to the annotation
is the whole fix, and the third `print()` above exercises the new branch.

Removing `outcome()`'s return annotation makes the error disappear, and that is
the interesting half. With no declared return type, `ty` infers one from the
body, and the inferred type is whatever `catch_all()` produces, so there is
nothing left to contradict. The function silently changes its type every time
`research()`'s error set changes.

What `ty` stopped checking is the correspondence between the annotation and the
Effect. The annotation was where a human wrote down which failures this program
expects, and `ty`'s job was to confirm that the Effect agrees.
Delete the annotation and the type checker has one description instead of two,
so it can no longer notice a disagreement. Callers still see a union, but they
see whatever union the implementation happens to produce, and the new member
propagates outward until it reaches something with an annotation.
That is the same reason exercise 4 of
[Generators](../Chapters/45_Effects--Generators.md) needed a declared type to
catch a missing `yield from`: a type checker verifies claims, and an inferred
type is not a claim.

## 12. A `Random` Ability

```python
# exercise_12.py
import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

@dataclass(frozen=True)
class Random(Ability[int]):
    low: int
    high: int

def roll(low: int, high: int) -> Depend[Random, int]:
    return (yield Random(low, high))

def game() -> Depend[Random, str]:
    first = yield from roll(1, 6)
    second = yield from roll(1, 6)
    return f"{first} + {second} = {first + second}"

def real(request: Random) -> int:
    return random.randint(request.low, request.high)

def scripted_from(
    values: Iterator[int],
) -> Callable[[Random], int]:
    def scripted(request: Random) -> int:
        return next(values)
    return scripted

random.seed(0)
print(run(handle(real)(game)()))
#: 4 + 4 = 8
print(run(handle(scripted_from(iter([3, 4])))(game)()))
#: 3 + 4 = 7
```

The request carries the range, which is the difference from a `Need`.
`Need[T]` asks for an instance of `T` and there is nothing else to say.
`Random(1, 6)` asks a question with arguments, and the handler reads them off
the request. That is why an Ability is a dataclass rather than a marker: its
fields are the parameters of the question.

You write `game()` once, and it runs under both handlers unchanged. The scripted
handler is the testable one, and it is a closure over an iterator rather than a
class, because a handler is an ordinary function.

Deleting `low: int` from the accessor changes nothing that `ty` reports about
this file. It changes what `ty` reports about callers. With the annotation,
`roll("a", 6)` is `error[invalid-argument-type]`. Without it, the parameter has
no type, `roll("a", 6)` type-checks, and the mistake surfaces at runtime inside
`random.randint()`, one frame away from the code that made it. The accessor is
the only place where `ty` checks a caller's arguments, since after that they are
fields on a dataclass that nobody inspects.

Deleting the annotation on the handler's parameter fails much louder, and
earlier:

```text
ValueError: Handler function <function scripted_from.<locals>.scripted
at 0x...> was not annotated.
```

`handle()` raises that `ValueError` as soon as you call it, before any Effect
runs, because `handle()` reads `get_type_hints()` on the handler to learn which
Ability the handler answers. The two annotations therefore do different jobs:
the accessor's is for the type checker, and the handler's is data the library
reads at runtime. Only one of them is optional, and it is not the one that looks
like bookkeeping.

## Shared code: the bakery

Exercise 13 extends the chapter's bakery, repeated here without its demo so the
solution can import it:

```python
# kitchen.py
from dataclasses import dataclass
from stateless import Depend, Need, need

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
```

## 13. A dependency two levels down

```python
# exercise_13.py
from dataclasses import dataclass
from kitchen import Dough, Oven, Toaster, toast
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Butter:
    grams: int
    def spread(self, slice_: str) -> str:
        print(f"butter: {self.grams}g")
        return f"buttered {slice_}"

def buttered() -> Depend[
    Need[Dough] | Need[Oven] | Need[Toaster] | Need[Butter],
    str
]:
    slice_ = yield from toast()
    butter = yield from need(Butter)
    return butter.spread(slice_)

kitchen = supply(Dough("rye"), Oven(220), Toaster(3),
                 Butter(10))
print(run(kitchen(buttered)()))
#: dough: risen
#: oven: baking at 220
#: toaster: setting 3
#: butter: 10g
#: buttered toasted loaf of rye dough
```

Writing the signature as `Depend[Need[Butter], str]` first is the instructive
half:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> exercise_13.py:13:25
   |
12 | def buttered() -> Depend[Need[Butter], str]:
   |                   ------------------------- Function annotated with yield
   |                   type `Need[Butter]` here
13 |     slice_ = yield from toast()
   |                         ^^^^^^^ expression of type
   |                         `Need[Dough] | Need[Oven] | Need[Toaster]`,
   |                         expected `Need[Butter]`
```

The diagnostic points at the `yield from`, not at the signature, and it prints
the whole union that arrived. That union is the answer to "what does
`buttered()` actually need," and the fix is to write it down. `buttered()` names
`Dough` and `Oven` in its type without mentioning either in its body, which is
the propagation the chapter describes: a caller inherits every requirement of
everything it delegates to.

Removing `Toaster(3)` from `supply()` produces the second diagnostic, and it is
a different shape:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
  |
  | print(run(kitchen(buttered)()))
  |           ^^^^^^^^^^^^^^^^^^^ Expected `Generator[Async | Exception, Any, Unknown]`,
  |                               found `Generator[Need[Toaster], Any, str]`
```

This one tells you about the dependency two levels down. `supply()` failed to
subtract `Need[Toaster]`, so it reaches `run()` still in the channel. Nothing in
`buttered()`'s body mentions a toaster. The requirement came from `toast()`,
which `buttered()` calls, and the error names it at the program's edge, past the
last place that could have answered it.

The two diagnostics divide the work cleanly. `invalid-yield` catches an
under-declared signature at the delegation that broke it. `invalid-argument-type`
at `run()` catches an under-supplied environment at the program's edge. Neither
one required a comment or a docstring to say what depends on what.

## 14. A shared signature for a cast

The two factories in `casts.py` already have the same signature. The exercise
is to name it and see what naming it buys. Here is the chapter's cast, with
each actor trimmed to one method so the whole thing fits in one listing:

```python
# exercise_14.py
from collections.abc import Callable
from typing import Protocol, runtime_checkable
from stateless import Depend, Need, need, run, supply

@runtime_checkable
class Narrator(Protocol):
    def say(self, line: str) -> None: ...

@runtime_checkable
class Hero(Protocol):
    def name(self) -> str: ...

@runtime_checkable
class Obstacle(Protocol):
    def blocks(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator] | Need[Hero] | Need[Obstacle], None
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    obstacle = yield from need(Obstacle)
    blocker = obstacle.blocks()
    narrator.say(f"{hero.name()} meets the {blocker}")

class Kitty:
    def name(self) -> str: return "Kitty"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Warrior:
    def name(self) -> str: return "Warrior"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

class Loud:
    def say(self, line: str) -> None: print(line)

def play(
    narrator: Narrator, hero: Hero, obstacle: Obstacle
) -> None:
    run(supply(narrator, hero, obstacle)(encounter)())

def kitties(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle())

def warriors(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon())

type Cast = Callable[[Narrator], None]

def run_season(casts: list[Cast]) -> None:
    for cast in casts:
        cast(Loud())

run_season([kitties, warriors])
#: Kitty meets the puzzle
#: Warrior meets the nasty weapon
play(Loud(), Kitty(), Weapon())
#: Kitty meets the nasty weapon
```

What the shared signature recovers is the Abstract Factory's *interface*.
`run_season()` accepts anything that can stage a scene and stays ignorant of
which family it gets, and that ignorance is the property the pattern exists to
provide. Python gives it away, because a function is already an object with a
type: saying so takes no abstract factory class.

What it does not recover is the guarantee that made the pattern worth naming.
`Cast` says "give me a narrator and I will stage something." It says nothing
about the actors inside agreeing with each other. The last line is the proof,
and the chapter runs the same line in `two_games.py`: `play()` accepts a
`Kitty` facing a `Weapon`, both satisfy their `Protocol`s, and nothing
objects. An Abstract Factory in a language with a family type expresses "these
come from one world" in the type itself. Here the matching lives inside
`kitties()`'s body, a fact about how someone wrote that function, and nothing
checks it.

So the shared signature narrows the loss without closing it. A caller that
takes a `Cast` can no longer assemble a mismatched set by accident, because it
never sees the actors. `play()` is still there and still accepts any of them.

Adding a fourth actor to the chapter's three-actor version shows where the
cost falls. `quest.py` gains a `Protocol`, a member in `encounter()`'s `Need[...]`
union, and a `yield from`, so four edits. `casts.py` gains a parameter on
`play()`, an argument in the `supply()` call, a class for each family, and an
argument in each of the two factory calls, so seven. `two_games.py` needs two
edits, its direct `play()` call and the `from casts import` list it draws the
new actor from, and none for its two factory calls. The
`Cast` alias does not change at all, because the new actor never reaches the
caller.

That distribution is the argument for the factory. The functions that name a
whole cast absorb the change, and the code that only wants a scene does not
notice. It is also why the chapter uses a factory function rather than more
`supply()` arguments: `supply()` tops out at nine overloads, and a wide cast is
what a positional interface handles worst.
