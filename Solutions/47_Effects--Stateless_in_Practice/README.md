# Stateless in Practice: Solutions

## 1. An advancing handler, and the fix it cannot break

> `crossing` in `midnight.py` walks a scripted list,
> so it answers two requests.
> Write a handler that instead advances a stored moment by one second at each request,
> and confirm `archive()` still crosses midnight under it.
> Then rewrite `archive()` so the file name and the stamp cannot disagree,
> and explain why no handler can reproduce the bug afterward.

<details>
<summary>Where to look</summary>

[A Clock That Crosses Midnight](../../Chapters/47_Effects--Stateless_in_Practice.md#a-clock-that-crosses-midnight)
walks a scripted list inside a handler.
A handler can be a closure.
Keep the stored moment in the enclosing scope and update it with `nonlocal`.
For the second half, count how many times `archive()` reads the clock,
since a mismatch between name and stamp needs two readings.

<details>
<summary>The shape</summary>

```python
# The shape of advancing_clock.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
from stateless import Ability, Depend, handle, run

type FileName = str

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    ...

def ticking(
    start: datetime, step: timedelta
) -> Callable[[Now], datetime]:
    ...

def archive_twice(
    entry: str
) -> Depend[Now, tuple[FileName, str]]:
    ...

def archive_once(
    entry: str
) -> Depend[Now, tuple[FileName, str]]:
    ...

LATE: Final[datetime] = datetime(2026, 1, 1, 23, 59, 59)
SECOND: Final[timedelta] = timedelta(seconds=1)
```

<details>
<summary>Done when</summary>

your handler, started at `LATE` with a one-second step,
makes the chapter's `archive()` return `('log-2026-01-01.txt', '[2026-01-02] ok')` for the entry `"ok"`.
Under a fresh handler with the same start,
your rewritten `archive()` puts `2026-01-01` in both strings,
and your explanation counts the clock readings in each version.

<details>
<summary>Solution</summary>

```python
# advancing_clock.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
from stateless import Ability, Depend, handle, run

type FileName = str

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
) -> Depend[Now, tuple[FileName, str]]:
    opened = yield from now()
    path = f"log-{opened:%Y-%m-%d}.txt"
    stamped = yield from now()
    return path, f"[{stamped:%Y-%m-%d}] {entry}"

def archive_once(
    entry: str
) -> Depend[Now, tuple[FileName, str]]:
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

**Keep the moment between requests.**
`ticking()` is a handler factory that stores a moment.
`nonlocal` makes the handler stateful.
Where `crossing` in `midnight.py` walks a two-element list,
`ticking()` answers any number of requests,
so the same handler serves an Effect that reads the clock three times or thirty.
Each call to `ticking()` builds a fresh handler with its own stored moment,
so both runs in the listing start at 23:59:59.

If you leave out `nonlocal`,
`moment += step` makes `moment` a local name of `advancing()`,
so `current = moment` raises an `UnboundLocalError` at the first request.
`ty` reports the mistake before any run,
as an `unresolved-reference` on both lines that use `moment`.
The solution declares `moment` nonlocal,
so each request rebinds the enclosing variable and the stored moment carries over to the next request.

**Reproduce the bug under the new handler.**
`archive_twice()` is the original function.
The new handler reproduces the bug, because the bug is in the function,
not in the handler.

**Make the two strings agree.**
`archive_once()` reads the clock one time and derives both strings from that value.
The mismatch needs two readings that could differ.
With one reading, the two strings must agree.
A handler still chooses the moment, and it can choose 23:59:59,
but both strings then carry that moment.
No handler can reproduce the bug,
because the bug belongs to a function that asks twice and treats the answers as one.

Asking twice and treating the answers as one is the general shape of a clock bug,
since two readings of a changing value are two facts.
Naming the clock as an Ability makes the failure reproducible.
Deriving both strings from a single reading removes it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A leak the type checker cannot see

> `leaky_effect.py` type-checks even though its `Success[int]` claim is false.
> Describe a review rule or a lint check that catches it,
> and explain why a type checker cannot.
> Then demonstrate the error-side twin:
> write a function that raises a `KeyError` with no `@throws`,
> wrap it in `catch(KeyError)`, and run it on a failing input.
> Explain what the types claim, what the run does,
> and which line restores the guarantee.

<details>
<summary>Where to look</summary>

[Nothing stops an undeclared Effect](../../Chapters/47_Effects--Stateless_in_Practice.md#nothing-stops-an-undeclared-effect)
explains why a signature cannot describe what a body does before it returns.
For the error side, ask whether an ordinary function body raises its `KeyError` before or after `catch()` starts handling the failures in the channel.
`@throws` is the decorator that moves a raised exception into the channel.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from typing import Final
from exceptions import expect
from stateless import Success, catch, run, success, throws

RAW: Final[dict[str, int]] = {"Alice": 42}

def size(name: str) -> Success[int]:
    ...

def caller() -> Success[int | KeyError]:
    ...

@throws(KeyError)
def declared_size(name: str) -> int:
    ...

def fixed() -> Success[int | KeyError]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your file,
yet `run()` raises a `KeyError` for a missing key despite the `catch(KeyError)` around your function.
Adding `@throws(KeyError)` makes `run()` return the `KeyError` as a value.
Your review rule flags the `print()` line in `leaky_effect.py` and accepts a body that holds the `return` alone.

<details>
<summary>Solution</summary>

The rule that catches `leaky_effect.py` is a reading rule about one line:
when a function's return type is an `Effect` and its body is not a generator,
the body must contain only the expression it returns.

```python
def double(n: int) -> Success[int]:
    return success(n * 2)  # Nothing above this line
```

A line above the `return` runs while the caller builds the description,
not while `run()` executes it.
If that line is a `print()`, an `open()`, a mutation,
or a call to a function that does one of those,
the side effect occurs at build time,
the opposite of what the signature advertises.

A linter can enforce a conservative version of that rule:
flag any function annotated `Effect[...]`, `Depend[...]`, `Success[...]`,
or `Try[...]` that contains no `yield` and whose body is more than a single `return` statement.
That rule has false positives,
since a pure local computation above the `return` is harmless,
and false negatives, since a call inside the returned expression,
as in `return success(datetime.now())`, also runs at build time.

A type checker cannot catch that leak because purity is not a type.
`print()` is a call returning `None`, legal in any function.
Python's type system says what values a function accepts and produces,
not what its body does before it returns.
The annotation `Success[int]` describes the returned object,
and `success(n * 2)` produces a `Success[int]`,
so the annotation and the returned object agree.
A language that tracks Effects puts the side effect in the signature.
[Stateless](../../Chapters/46_Effects--Stateless.md)
and [Stateless in Practice](../../Chapters/47_Effects--Stateless_in_Practice.md)
simulate that tracking with a library and an annotation,
so the guarantee holds only for Effects that the body requests with `yield`.

The error side has the same limit:

```python
# exercise_2.py
from typing import Final
from exceptions import expect
from stateless import Success, catch, run, success, throws

RAW: Final[dict[str, int]] = {"Alice": 42}

def size(name: str) -> Success[int]:
    return success(RAW[name])  # KeyError, undeclared

def caller() -> Success[int | KeyError]:
    out: int | KeyError = (
        yield from catch(KeyError)(size)("Bob"))
    return out

expect(KeyError, run, caller())
#: [KeyError] 'Bob'

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

**Leak the failure past `catch()`.**
The types claim that `catch()` handles the `KeyError`.
`catch(KeyError)(size)` says it moves a `KeyError` from the error channel to the return channel,
and `caller()`'s `int | KeyError` says the caller is ready for either.
The run does something else.
`RAW["Bob"]` raises a `KeyError` while `size()` is still building its description,
before the Effect exists and before `catch()` receives any failure from it.
The exception unwinds the stack in the ordinary way and propagates out of `run()`.
`catch()` cannot catch what never entered the channel.

**Lift the failure into the channel.**
The line that restores the guarantee is `@throws(KeyError)`.
It turns `declared_size()` into a function that yields its failure instead of raising it,
so the exception reaches `catch()` as a value yielded on the error channel.
`catch()` then does what its type says.
`run(fixed())` returns the `KeyError` rather than raising it.

`success()` is for a value you already have.
`@throws` is for work that can fail.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## Shared code: the microgrid

Exercises 3 and 4 both use the chapter's microgrid,
repeated here without its demo so the two listings can import it:

```python
# grid.py
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Protocol
from record import record
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

`Turbine` is the only addition: a source available during a set range of hours.
Its `deplete()` is empty, since a turbine burns no fuel.

## 3. A wind turbine between solar and the battery

> Add a wind turbine to `power.py` that is available only during a set windy stretch of the evening,
> put it between solar and the battery in the `sun_first` order,
> and confirm `run_load()` needs no change.
> Then shorten every source until some hour has no source,
> run `run_load()` again,
> and say where the `Blackout` propagates and why `catch(Blackout)` around `run_load()` does not intercept it.

<details>
<summary>Where to look</summary>

[Switching Implementations Mid-Run](../../Chapters/47_Effects--Stateless_in_Practice.md#switching-implementations-mid-run)
shows `run_load()` asking for a `Source` and using the source the handler returns.
Add a source class with the same two methods and place it in the tuple that `controller()` receives.
For the blackout, trace which stack frames the handler's `Blackout` unwinds,
and whether any `yield` lies between the handler's `raise` and `run()`.

<details>
<summary>Done when</summary>

`run_load()` is unchanged and your `sun_first` trace shows the turbine's hours between `Solar offline` and `Battery online`.
With every source shortened,
`run()` raises a `Blackout` for the first uncovered hour,
with or without `catch(Blackout)` around `run_load()`,
and you can say which function raises it and why that function sits outside the Effect.

<details>
<summary>Solution</summary>

The listing runs the `sun_first` order with the turbine added,
then a shortened order that leaves an hour with no source:

```python
# exercise_3.py
from exceptions import expect
from grid import (Backup, Battery, Blackout, Grid, Solar,
                  Turbine, controller, run_load)
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
expect(Blackout, run, handle(short)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Turbine online
#:   19:00
#: Turbine offline
#: [Blackout] 20
```

**Slot a new source into the order.**
The turbine takes 19:00 through 21:00,
the hours the battery and the grid cover in the chapter's `sun_first` run.

`run_load()` needs no change.
It asks for a `Source` at an hour and uses the source the handler returns.
The handler decides which sources exist, the order in which it prefers them,
and whether one of them is new.
Choosing the source in the handler is the same substitution `Console` and `Feed` allow,
applied to a choice made fresh at every request rather than once at the start.

**Leave an hour with no supplier.**
With the turbine, the battery, the grid, and the backup shortened,
hour 20 has no supplier.
The `Blackout` propagates out of `run()` instead of arriving on the Effect's error channel.
`catch(Blackout)` around `run_load()` does not intercept it,
because `catch()` handles the failures an Effect yields on its error channel,
and `choose()`, the handler, raises this one.
A handler answers each request from inside the driver.
No `yield` sits between the `raise` and `run()`'s own stack frame,
so the exception unwinds the driver's stack frames in the ordinary Python way.
The driver never throws it into the suspended Effect.

If you wrap `run_load()` in `catch(Blackout)` to turn the blackout into a value,
the program type-checks and the run prints the same trace through `Turbine offline`.
Then the `Blackout` escapes `run()`,
and the traceback ends with `grid.Blackout: 20`.
The run is the same with or without the wrapper,
so the solution drops it and uses `expect()` to show the `Blackout` arriving at `run()`.

Exercise 2 draws the same distinction from the other side.
A failure is part of the Effect only if the Effect yields it as a value.
A `raise` in code the driver calls is outside the description.

Making a `Blackout` catchable means giving the Ability a failure type.
The handler then returns a value rather than raising an exception,
and `plug()` declares the failure it can produce.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. A scripted outlet

> Write a handler for `Outlet` that ignores `request.hour` and hands out a preset sequence of sources,
> the way `scripted` hands out a preset sequence of tosses.
> Use it to test that `run_load()` re-requests after a failure,
> without modeling weather, a clock, or a battery.
> Then say what such a test cannot tell you about `controller()`.

<details>
<summary>Where to look</summary>

[Scripting an Unpredictable Source](../../Chapters/47_Effects--Stateless_in_Practice.md#scripting-an-unpredictable-source)
shows `scripted` answering each `Flip` from a preset sequence.
Write a handler factory that closes over an iterator and returns `next()` on each request,
ignoring the request's fields.
Supply a source whose `available()` is always false so the first draws fail.
Then list what the handler ignores,
and which of `controller()`'s decisions the test therefore leaves unchecked.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Callable, Iterator
from grid import Outlet, Solar, Source, run_load
from stateless import handle, run

def scripted(
    sources: Iterator[Source]
) -> Callable[[Outlet], Source]:
    # request.hour ignored
    ...

class Dead:  # Never available, so every draw fails
    def available(self, hour: int) -> bool:
        ...
    def deplete(self) -> None:
        ...
```

<details>
<summary>Done when</summary>

with two failing sources scripted ahead of `Solar()`,
`run_load(10, 2)` prints an online and offline pair for each failing source,
then `Solar online`, `10:00`, `11:00`, and `Solar offline`.
The run makes three requests for two hours.
You can name a decision `controller()` makes by the hour that your test leaves unchecked.

<details>
<summary>Solution</summary>

If you script working sources alone, such as `iter([Solar()])`,
the run prints `Solar online`, both hours, and `Solar offline`,
all from a single request.
Every draw succeeds, so `run_load()` asks for one source,
and the test passes without exercising the re-request it exists to check.
The solution puts two `Dead()` sources ahead of `Solar()`,
so the first two draws fail and force two re-requests.

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

**Force a re-request.**
The run makes three requests for two hours of power.
Each time a draw fails, `run_load()` breaks out of the inner loop,
leaves the `connected` block, and asks for another source.
The test checks that re-request behavior with a handler that answers from a list instead of weather,
a clock, or a battery.

The test cannot tell you whether `controller()` is right.
It leaves every question about policy unchecked:
whether `controller()` prefers solar before the battery,
whether the battery reports itself unavailable once exhausted,
whether `controller()` asks about the hour for which `run_load()` draws power.
The scripted handler ignores `request.hour`,
which makes it simple to write and means the test exercises none of the choices `controller()` makes by the hour.
The scripted test checks the consumer of the Ability and leaves the producer untested.

`controller()` needs its own test, and that test can be an ordinary one.
`controller()` builds an ordinary function from an `Outlet` to a `Source`,
so a test can call that function with an `Outlet` and check which `Source` it returns.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## Shared code: the research pipeline

The chapter's `research.py` and the doubles from `newswire.py` appear here,
with exercise 6's `StaleWire` added,
so the listings that follow can import them:

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

class StaleWire:
    def latest(self) -> str:
        print("feed: fetching")
        raise Unavailable("stale connection")

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
```

```python
# report.py
from typing import assert_never
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, research)
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

> Add a fourth failure to `research()`:
> a `TooLong` raised when an article exceeds some length.
> Follow the type checker's diagnostics until the program type-checks again,
> and list every line you edited.
> Then do the same to `research_by_hand.py` and say which tool named the lines to change in each case.

<details>
<summary>Where to look</summary>

[Composing a Program](../../Chapters/47_Effects--Stateless_in_Practice.md#composing-a-program)
builds `research()` from `yield from` steps,
and [The Success Path](../../Chapters/47_Effects--Stateless_in_Practice.md#the-success-path)
writes the same pipeline with ordinary calls.
In the Effect version,
add a `@throws` function for the new check and widen the error parameter of the signature until the program type-checks again.
In the by-hand version, ask which tool, if any, reports the changes.

<details>
<summary>The shape</summary>

```python
# The shape of research_long.py
from typing import Final
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, fetch,
                      look_up, topic_of)
from stateless import Effect, Need, need, throws

class TooLong(Exception):
    pass

LIMIT: Final[int] = 100

@throws(TooLong)
def within_limit(article: str) -> str:
    ...

def research() -> Effect[
    Need[Feed] | Need[Encyclopedia],
    Unavailable | NotInteresting | NoArticle | TooLong,
    str,
]:
    ...
```

```python
# The shape of research_by_hand.py
from feeds import Library, Wire
from research import (TOPICS, Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable)
from research_long import LIMIT, TooLong

def topic_of(headline: str) -> str:
    ...

def within_limit(article: str) -> str:
    ...

def research_and_report(
    feed: Feed, book: Encyclopedia
) -> str:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your Effect version and on `report()`,
which has a branch for `TooLong`.
Taking `TooLong` back out of `research()`'s error parameter makes `ty` report `invalid-yield` at your new `yield from`.
The type checker accepts your by-hand version whether or not it handles `TooLong`,
and your edit list says which tool named each line.

<details>
<summary>Solution</summary>

The solution decorates `within_limit()` with `@throws(TooLong)`,
which moves the raised exception into the error channel,
where `catch()` handles it:

```python
# research_long.py
from typing import Final
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable, fetch,
                      look_up, topic_of)
from stateless import Effect, Need, need, throws

class TooLong(Exception):
    pass

LIMIT: Final[int] = 100

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

**Add and declare the failure.**
`research.py` takes four edits, one of which the type checker names.
`report()` needs three more.

1. A new exception class, `TooLong`.
2. A new `@throws(TooLong)` function, `within_limit()`,
   since `@throws` lifts a raised `TooLong` into a failure the Effect yields.
3. One new line in `research()`, the `yield from within_limit(article)`.
4. `research()`'s error parameter, widened to include `TooLong`.
5. `report()`'s `catch()` call, widened to include `TooLong`.
6. The `found:` annotation, widened to include `TooLong`.
7. A new `case TooLong():` branch in `report()`'s `match`.

If you write `within_limit()` without `@throws`,
an article over the limit raises a `TooLong` that escapes `catch()` and `run()` as an ordinary exception,
the way `size()`'s `KeyError` does in exercise 2.
`ty` flags the mistake first,
as an `invalid-yield` at `yield from within_limit(article)`,
because the undecorated function returns a `str` rather than an Effect.

**Widen the signature to match.**
If you make edit 3 without edit 4,
`ty` reports an `invalid-yield` at the new line rather than at the signature:
`expression of type 'TooLong', expected 'Need[Feed] | Need[Encyclopedia] | Unavailable | NotInteresting | NoArticle'`.
Widening the signature then breaks every caller that names the old set.
`ty` reports the same `invalid-yield` at `report()`'s own `yield from`,
now with `TooLong` in the yielded type.
Once edits 5 and 6 widen `catch()` and the `found:` annotation to match,
`assert_never()` reports `TooLong` as an unhandled branch until edit 7 adds its case.
Each missing edit fails the type check before the program runs,
instead of failing in production.
Starting with edit 4, the type checker reports each line the change requires,
one edit at a time.

The by-hand version needs a comparable edit, and no tool reports any of it:

```python
# research_by_hand.py
from feeds import Library, Wire
from research import (TOPICS, Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable)
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
    try:  # [1]
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

In the Effect version, the type checker reports where to edit.
It flags the undeclared failure at the delegation that introduces it,
then the widened union at every caller whose annotations name the old set of failures.
In the by-hand version,
adding `except TooLong` to the `try` at `[1]` is a choice you make by reading the code.
If you forget `except TooLong`, a `TooLong` escapes `research_and_report()`,
whose signature still says it returns a `str`.
Both versions run.
Only in the Effect version does a tool report that the set of failures changed.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A stale wire

> `scenarios.py` supplies a `DeadWire` that fails without printing anything.
> Write a `StaleWire` whose `latest()` prints `feed: fetching` and then raises `Unavailable`.
> Predict the trace, then say why it differs from `DeadWire`'s trace even though both fail the same way.

<details>
<summary>Where to look</summary>

[Composing a Program](../../Chapters/47_Effects--Stateless_in_Practice.md#composing-a-program)
shows `scenarios.py` supplying a `Feed` implementation to the whole pipeline.
Write a class with a `latest()` method that calls `print()` before it raises `Unavailable`.
Compare where in each `latest()` the failure begins,
since the trace records how far the implementation got.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from feeds import SHELF, StaleWire
from report import report
from research import Encyclopedia, Feed
from stateless import run, supply

def outcome(feed: Feed, book: Encyclopedia) -> str:
    ...
```

<details>
<summary>Done when</summary>

you wrote your prediction before running,
and the run prints `feed: fetching` and then `no headline today`,
with no `library:` line.
Your explanation says what the extra trace line tells you about how far `latest()` got,
and why the value `report()` returns matches the value `DeadWire` returns.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from feeds import SHELF, StaleWire
from report import report
from research import Encyclopedia, Feed
from stateless import run, supply

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(StaleWire(), SHELF))
#: feed: fetching
#: no headline today
```

The prediction is two lines: `feed: fetching`, then `no headline today`.

`StaleWire` and `DeadWire` fail the same way.
Each `latest()` raises `Unavailable`,
and `@throws` on `fetch()` sends it into the error channel.
`research()` stops there, before `need(Encyclopedia)`,
so neither trace has a `library:` line.
`report()` matches the failure and returns `"no headline today"`.
The difference is where inside `latest()` the failure arises.
`StaleWire.latest()` prints its trace line before it raises the exception,
so `feed: fetching` appears.
`DeadWire.latest()` raises the exception on its first line,
so `no headline today` is all the run prints.
The trace shows how far each supplied implementation got before it failed.
The value `report()` returns is the same for both.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. Retrying the wrong failure

> Wrap `research()` in `retry()` and supply a `Time()`.
> Explain what `retry()` does under the `WEATHER` scenario and why retrying a `NotInteresting` failure is the wrong behavior,
> then say what an Effect system needs for you to retry `Unavailable` alone.

<details>
<summary>Where to look</summary>

[What Retry Cannot Judge](../../Chapters/47_Effects--Stateless_in_Practice.md#what-retry-cannot-judge)
describes `retry()` applying one schedule to the whole error channel.
Wrap `research()` with `retry()`, `catch()` the `RetryError`,
and supply a `Time()` along with the feed and encyclopedia.
Ask whether a headline that is the same on every attempt can produce a different result,
then look at what `retry()` takes as arguments.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from datetime import timedelta
from feeds import SHELF, WEATHER
from research import Encyclopedia, Feed, research
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

def attempt(
    feed: Feed, book: Encyclopedia
) -> str | RetryError:
    # Named, so ty follows it
    ...
```

<details>
<summary>Done when</summary>

under `WEATHER` your run prints `feed: fetching` once per attempt and ends in a `RetryError` whose failures all read `NotInteresting: mild and cloudy`.
Your explanation says why a later attempt cannot give a different answer,
and describes what the retry would have to know about each failure to try `Unavailable` again and stop on `NotInteresting`.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from datetime import timedelta
from feeds import SHELF, WEATHER
from research import Encyclopedia, Feed, research
from stateless import catch, retry, run, supply
from stateless.functions import RetryError
from stateless.schedule import recurs, spaced
from stateless.time import Time

three = recurs(3, spaced(timedelta(milliseconds=1)))

def attempt(
    feed: Feed, book: Encyclopedia
) -> str | RetryError:
    # Named, so ty follows it
    retried = retry(three)(research)
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

**Run out of attempts.**
Retrying is the wrong behavior because this `NotInteresting` failure is deterministic.
`WEATHER`'s headline is the same on every attempt,
and `TOPICS` holds the same two topics,
so `topic_of()` returns the same answer however many times it runs.
`retry()` sleeps after every failed attempt, the last included,
so the retry makes three fetches and three sleeps.
It ends with the answer the first attempt produced.
It also turns a clear `NotInteresting` into a `RetryError` that the caller must unwrap.

`Unavailable` is the failure worth retrying.
A feed that is offline now may be online in a moment,
so another attempt can succeed.
Distinguishing `Unavailable` from `NotInteresting` needs something the library does not offer:
a retry that selects on the error type.
`retry()` here applies to the whole error channel,
treating every declared failure as transient,
because its schedule decides when to try again,
while every declared failure gets another try.
ZIO provides that retry as `retryWhile`, which takes a predicate on the error.

In Stateless, a selective retry means narrowing the channel first.
`catch()` the failures that retrying cannot help,
so they leave the error channel as values.
Then apply `retry()` to what remains.
That narrowing takes more machinery than a predicate,
and it changes the result type.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Processes instead of threads

> Change `parallel.py` to use a `ProcessPoolExecutor` instead of a `ThreadPoolExecutor`,
> and confirm `squares()` stays unchanged.
> Processes re-import the module,
> so the driver needs the `if __name__ == "__main__":` guard [Concurrency](../../Chapters/19_Techniques--Concurrency.md)
> describes.
> Without it the pool breaks before any work starts.
> Then try to fork an Effect that still declares a `Need`,
> and record what the type checker says.

<details>
<summary>Where to look</summary>

[Running Effects in Parallel](../../Chapters/47_Effects--Stateless_in_Practice.md#running-effects-in-parallel)
forks work onto an `Executor`.
Swap in a `ProcessPoolExecutor`,
and protect the driver with the `__main__` guard because each worker re-imports the module.
For the `Need`, consider where the forked work runs and whether a handler can answer its requests there.

<details>
<summary>Done when</summary>

your process-pool version prints `[0, 1, 4, 9, 16]` with `squares()` unchanged character for character,
and removing the `__main__` guard makes `run()` fail with a `BrokenProcessPool`.
Decorating an Effect that still declares a `Need` with `@fork` makes `ty` report `no-matching-overload`.

<details>
<summary>Solution</summary>

The solution swaps in a `ProcessPoolExecutor` and puts the driver under the `__main__` guard:

```python
import time
from concurrent.futures import Executor, ProcessPoolExecutor
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

**Leave the Effect alone.**
`squares()` stays the same, character for character.
It asks for an `Executor` of any kind,
so a process pool satisfies the request as a thread pool does.

**Guard the driver.**
The code around `squares()` did change, all of it outside the Effect:
the executor class, the timing the chapter's version prints,
and the `__main__` guard.
The guard is now required,
because a process pool starts workers by re-importing the module.

If you leave out the `__main__` guard, each worker re-imports the module,
reaches the `with` block,
and tries to start a pool of its own before it has finished starting.
The workers die with a `RuntimeError` about their bootstrapping phase,
and the driver's `run()` fails with a `BrokenProcessPool` instead of printing the squares.
Under the guard, the driver runs in the main process alone,
so a worker loads `slow_square()` without running the driver.

`slow_square()` stays as it was.
`fork()` checks for a `ProcessPoolExecutor` and serializes the function and its arguments with `cloudpickle`.
`cloudpickle` serializes a function defined in the running script by value,
so a worker receives `slow_square()` without importing it by name.

Forking an Effect that still declares a `Need` fails the type check:

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

**Keep requests out of forked work.**
Every overload accepts an Effect whose yield channel holds errors, `Async`,
or `Never`, and none accepts one that still holds a `Need`.
The forked work runs in a worker,
outside the driver and the handler stack that answers requests.
So you must remove the requirement before the fork.
Supply it first and fork the bound function.
The type system enforces a rule about where a handler can answer a request.
That rule is the guarantee on which [Stateless](../../Chapters/46_Effects--Stateless.md)
and [Stateless in Practice](../../Chapters/47_Effects--Stateless_in_Practice.md)
rely.
`fork()` extends that guarantee to a boundary between threads or processes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 9. A scripted wallet

> `test_wallet.py` runs `spree()` against a `Cell`.
> Script it instead.
> Write a `Get` handler that answers from a preset sequence of balances and a `Put` handler that appends every request to a list,
> the way `scripted` feeds `Flip`.
> Assert that `spree()` attempts every price and writes once per purchase.
> Then say what this test cannot detect that the `Cell` version can.

<details>
<summary>Where to look</summary>

[State as an Ability](../../Chapters/47_Effects--Stateless_in_Practice.md#state-as-an-ability)
reads and writes the balance through `Get` and `Put` requests.
Write one handler factory that reads from an iterator of balances and another that appends each `Put` to a list,
then `handle()` both around `spree()`.
Check the list, check that the balance iterator has run out,
and ask what ties the scripted balances to the writes.

<details>
<summary>Done when</summary>

`uv run pytest` passes on your test,
which runs `spree()` on `(60, 50, 30, 20)` from a scripted start of `100`,
asserts it returns `2` and records the writes `[40, 10]`,
and checks that the run reads every scripted balance.
Dropping the last price from the call makes that last check fail.

<details>
<summary>Solution</summary>

Every attempt reads a balance, whether the purchase succeeds or fails,
so the solution scripts four balances, with `40` twice:

```python
# test_ch47_wallet.py
from collections.abc import Callable, Iterator
from record import record
from stateless import Ability, Depend, handle, run

type Count = int

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

def spree(
    prices: tuple[int, ...]
) -> Depend[Get | Put, Count]:
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

**Replay the balances.**
The scripted balances are the four the `Cell` version produces:
`100` before the first purchase, `40` after it,
`40` again because `purchase()` refuses the `50` and returns `False` before its `Put`,
and `10` after the `30` goes through.

**Prove the loop tries every price.**
The test proves from both sides that `spree()` attempts all four prices.
A `spree()` that makes a fifth `Get` request exhausts the script.
`handle()` reads the `StopIteration` from `read()` as the end of the Effect,
the silent failure the chapter describes,
so `run()` returns `None` and the first assertion fails on `None == 2`.
A `spree()` that stops early leaves a balance unread,
which the final assertion catches by checking that the iterator has run out.

If you script three balances, `[100, 40, 10]`,
and forget that the refused `50` still reads one,
the script runs out at the fourth price.
The test then fails on `assert None == 2`,
as it does when a fifth request exhausts the script.

**Record each write.**
`written` records one entry per successful purchase, `[40, 10]`,
so the assertions together say that `spree()` tries every price and writes only the affordable ones.

This test cannot check whether the `Get` and `Put` handlers agree.
The `Cell` version has one piece of state,
so the next `Get` returns the value the last `Put` wrote.
Here the test scripts the balances independently of the writes.
The script says 40 follows the first purchase because the test's author did that subtraction.
A `spree()` that writes the wrong amount,
say `funds` instead of `funds - price`, still fails the test,
at `written == [40, 10]`.

The scripted test checks the Effect's shape: which requests the Effect makes,
in which order, with which payloads.
The `Cell` test checks that the requests compose into correct arithmetic.
Each test checks what the other leaves unchecked, so a suite needs both.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 10. `throw()` and `@throws` side by side

> `fetch_nonempty()` puts `Empty` into the channel with `throw()`.
> Rewrite it to raise `Empty` in the body and lift it with `@throws(Empty)`,
> and confirm the two versions type-check and behave identically.
> Then make each version fail with an undeclared exception type and compare what the type checker reports for each.

<details>
<summary>Where to look</summary>

[Failing from Inside an Effect](../../Chapters/47_Effects--Stateless_in_Practice.md#failing-from-inside-an-effect)
contrasts `throw()` with `@throws` for putting `Empty` into the channel.
Move the `raise` into an ordinary body and decorate it with `@throws(Empty)`.
Then change each version to fail with a different exception and note which one the type checker flags,
and at which line.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from record import record
from stateless import (Effect, Need, catch, need, run,
                       supply, throw, throws)

class Unavailable(Exception):
    pass

class Empty(Exception):
    pass

@record
class Ticker:
    headline: str
    def latest(self) -> str:
        ...

@throws(Unavailable)
def fetch(feed: Ticker) -> str:
    ...

def thrown() -> Effect[
    Need[Ticker], Unavailable | Empty, str
]:
    ...

@throws(Empty)
def lifted() -> Effect[Need[Ticker], Unavailable, str]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes and both versions return the same results for a non-empty and an empty headline under `catch(Unavailable, Empty)`.
Changing `throw(Empty())` to `throw(ValueError())` makes `ty` report `invalid-yield` on that line,
while the same change to the `raise` passes `ty` and the `ValueError` escapes `run()`.

<details>
<summary>Solution</summary>

```python
# exercise_10.py
from record import record
from stateless import (Effect, Need, catch, need, run,
                       supply, throw, throws)

class Unavailable(Exception):
    pass

class Empty(Exception):
    pass

@record
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
def lifted() -> Effect[Need[Ticker], Unavailable, str]:
    feed = yield from need(Ticker)
    headline = yield from fetch(feed)
    if not headline:
        raise Empty()
    return headline

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

**Give both versions one type.**
`reveal_type()` reports the same return type for both:
`Generator[Need[Ticker] | Unavailable | Empty, Any, str]`.
`thrown()` writes that union in its annotation.
`lifted()` annotates the undecorated shape,
`Effect[Need[Ticker], Unavailable, str]`,
and `@throws(Empty)` adds `Empty` to it,
the way the chapter's `fetch_effectful.py` adds `Unavailable`.

**Send the failure into the channel.**
The versions differ in where you write the failure.
`throw()` puts an exception into the channel at the point of the `yield from`.
With `@throws`, the body fails with an ordinary `raise` statement,
and the decorator moves that exception into the channel.

Making each version fail with an undeclared type shows the same asymmetry exercise 2 finds.
If you change `throw(Empty())` to `throw(ValueError())`,
the type checker reports an `invalid-yield` at that line.
The yielded type is `ValueError`,
and the annotation allows `Need[Ticker] | Unavailable | Empty`.
If you change `lifted()`'s `raise Empty()` to `raise ValueError()` while its decorator still says `@throws(Empty)`,
the checker accepts the change.
At runtime the `ValueError` propagates through `catch(Unavailable, Empty)` and out of `run()` as an ordinary exception.
The decorator's argument is a claim about the function, not a check on it.
No type checker compares a `raise` with a decorator's arguments.
So the type checker verifies the version that yields its failure,
and accepts the version that raises its failure without checking the `raise`.

That difference decides which one to use.
Use `throw()` when the Effect chooses to fail,
so the type checker verifies the failure.
Keep `@throws` for ordinary code that raises exceptions, such as `latest()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 11. A fourth failure, with `catch_all()`

> Exercise 5 adds a `TooLong` failure to `research()`.
> Repeat it with `catch_everything.py` in the build.
> Predict what the type checker reports in `outcome()`, then confirm.
> Remove `outcome()`'s return annotation and rerun `ty`,
> and explain what the type checker stopped verifying.

<details>
<summary>Where to look</summary>

[Catching the Whole Channel](../../Chapters/47_Effects--Stateless_in_Practice.md#catching-the-whole-channel)
uses `catch_all()` to move the entire error channel into the return type.
Widen `research()`'s failures,
then read the `ty` diagnostic on `outcome()`'s return line before fixing the annotation.
Afterward, delete the annotation and look at what `reveal_type()` reports for the function.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_11.py
from record import record
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable)
from research_long import TooLong, research
from stateless import run, supply
from stateless.effect import catch_all

@record
class Bulletin:
    headline: str
    def latest(self) -> str:
        ...

class BareShelf:
    def article(self, topic: str) -> str:
        ...

class LongShelf:
    def article(self, topic: str) -> str:
        ...

def outcome(
    feed: Feed, book: Encyclopedia
) -> (str | Unavailable | NotInteresting | NoArticle
      | TooLong):
    ...
```

<details>
<summary>Done when</summary>

before you widen the annotation,
`ty` reports `invalid-return-type` on `outcome()`'s `return` line;
after you add `TooLong`, it passes and a too-long article returns a `TooLong`.
With the return annotation deleted,
`ty` passes and `reveal_type(outcome)` shows the return type as `Unknown`.

<details>
<summary>Solution</summary>

```python
# exercise_11.py
from record import record
from research import (Encyclopedia, Feed, NoArticle,
                      NotInteresting, Unavailable)
from research_long import TooLong, research
from stateless import run, supply
from stateless.effect import catch_all

@record
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
print(type(long).__name__)  # [1]
#: TooLong
```

**Widen the annotation with the channel.**
The prediction is that `outcome()`'s return annotation fails the type check.
`catch_all()` moves the entire error channel into the return type,
so widening `research()`'s failures to include `TooLong` widens what `catch_all()` returns.
The declared `str | Unavailable | NotInteresting | NoArticle` is now too narrow.
`ty` reports an `invalid-return-type` on the `return run(...)` line,
naming `TooLong` as the member that does not fit.
Adding `| TooLong` to the annotation fixes it.
The `print()` at `[1]` exercises the new branch.

Removing `outcome()`'s return annotation makes the error disappear.
`ty` infers no return type from the body.
`reveal_type(outcome)` reports `-> Unknown`,
and `Unknown` is compatible with every type,
so the type checker accepts whatever the function returns.
Pyright does infer the union from the body,
so under Pyright the function changes its type every time `research()`'s error set changes.

`ty` stops checking the correspondence between the annotation and the Effect.
The annotation is where a human writes down which failures this program expects,
and the checker's job is to confirm that the Effect agrees.
Once you delete the annotation,
the type checker has one description instead of two,
so it can no longer report a disagreement.
Callers lose their check too.
Under `ty` the result is `Unknown`,
so a caller that treats it as a `str` type-checks.
Under Pyright, each unannotated caller's inferred type gains the new member,
up to the first caller with an annotation.
Exercise 4 of [Generators](../../Chapters/45_Effects--Generators.md)
needs a declared type to catch a missing `yield from` for the same reason.
A type checker verifies claims.
An inferred type is not a claim.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 12. A `Random` Ability

> Write a `Random` Ability whose handler returns an `int` in a range carried on the request,
> and an accessor `roll(low, high)` for it.
> Use it to write a dice game as an Effect, then run the game twice:
> once with a handler that calls `random.randint()`,
> and once with a handler that walks a scripted sequence.
> Then delete the `low: int` annotation from the accessor's parameter and say what changes,
> and delete the annotation on the handler's parameter and say what changes.

<details>
<summary>Where to look</summary>

[Abilities Are Not Special](../../Chapters/47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
defines an Ability as a class, an accessor that yields it,
and a handler that answers it.
Give the Ability fields for the range,
and read them off the request in the handler.
Use a closure over `random.randint()` for one run and over an iterator for the other.
For the annotations, ask who reads each one: the type checker or `handle()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_12.py
import random
from collections.abc import Callable, Iterator
from record import record
from stateless import Ability, Depend, handle, run

@record(slots=False)
class Random(Ability[int]):
    low: int
    high: int

def roll(low: int, high: int) -> Depend[Random, int]:
    ...

def game() -> Depend[Random, str]:
    ...

def real(request: Random) -> int:
    ...

def scripted_from(
    values: Iterator[int],
) -> Callable[[Random], int]:
    ...
```

<details>
<summary>Done when</summary>

one `game()` runs under both handlers,
and the scripted run reports your scripted values.
With the accessor's `low` annotation in place,
`ty` reports `roll("a", 6)` as `invalid-argument-type`; with it deleted,
`ty` accepts that call.
With the handler's annotation deleted,
`handle()` raises a `ValueError` before any Effect runs.

<details>
<summary>Solution</summary>

The solution gives `Random` the fields `low` and `high`,
so the handler reads the range off the request:

```python
# exercise_12.py
import random
from collections.abc import Callable, Iterator
from record import record
from stateless import Ability, Depend, handle, run

@record(slots=False)
class Random(Ability[int]):
    low: int
    high: int

def roll(low: int, high: int) -> Depend[Random, int]:
    value: int = yield from Random(low, high)
    return value

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

**Carry the question's arguments.**
The request carries the range, which is the difference from a `Need`.
`Need[T]` asks for an instance of `T`,
so its request consists of the type alone.
`Random(1, 6)` asks a question with arguments,
and the handler reads them off the request.
That is why this Ability is a record with fields,
where the chapter's `Flip` is an empty class.
The fields are the parameters of the question.

If you declare `Random` as an empty class, the way the chapter declares `Flip`,
the request has no field to carry the range.
`roll()` fails at `Random(low, high)` with a `TypeError`,
and `ty` reports `too-many-positional-arguments` there and `unresolved-attribute` where the handler reads `request.low`.

**Run one game under two handlers.**
You write `game()` once, and it runs under both handlers unchanged.
The scripted handler is the testable one.
It is a closure over an iterator rather than a class,
because a handler is an ordinary function.

Deleting `low: int` from the accessor leaves the type checker's report on this file as it was.
It changes what the checker reports about callers.
With the annotation, `roll("a", 6)` is `error[invalid-argument-type]`.
Without it, the parameter's type is `Unknown`, and `roll("a", 6)` type-checks.
At runtime, `random.randint()` raises a `TypeError` when the handler calls it from the driver.
The traceback names `real()` and the library, and neither `roll()` nor `game()`.
The accessor is the only place where the type checker verifies a caller's arguments,
since once the accessor builds the request,
the arguments are fields that the handler alone reads.

Deleting the annotation on the handler's parameter produces an exception whose message says what to annotate,
and it comes earlier:

```text
ValueError: Not enough annotated arguments to handler function
'<function scripted_from.<locals>.scripted at 0x...>'. Expected 1,
got 0. 'handle' uses type annotations to match handlers with
abilities, so the argument to '<function ...>' must be annotated.
```

`handle()` raises that `ValueError` as soon as you call it,
before any Effect runs,
because `handle()` reads `get_type_hints()` on the handler to learn which Ability the handler answers.

The two annotations therefore do different jobs.
The accessor's annotation serves the type checker.
The handler's annotation is data the library reads at runtime.
The accessor's annotation is the optional one,
though the handler's annotation looks more like bookkeeping.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## Shared code: the bakery

Exercise 13 extends the chapter's bakery,
repeated here without its demo so the solution can import it:

```python
# kitchen.py
from record import record
from stateless import Depend, Need, need

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
```

## 13. A dependency two levels down

> Add a `Butter` leaf to `bakery.py` and a `buttered()` Effect that needs it and calls `toast()`.
> Write `buttered()`'s signature with `Need[Butter]` alone first, run `ty`,
> and read the diagnostic before fixing it.
> Then remove `Toaster(3)` from `supply()` and say which of the two diagnostics tells you about a dependency two levels below `run()`.

<details>
<summary>Where to look</summary>

[Dependencies That Need Dependencies](../../Chapters/47_Effects--Stateless_in_Practice.md#dependencies-that-need-dependencies)
shows `Need[...]` unions growing as one Effect delegates to another with `yield from`.
Write the first signature with the new appliance alone and read which line the type checker reports.
Then compare that diagnostic with the one `run()` reports when `supply()` leaves a requirement unanswered.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_13.py
from kitchen import Dough, Oven, Toaster, toast
from record import record
from stateless import Depend, Need, need, run, supply

@record
class Butter:
    grams: int
    def spread(self, slice_: str) -> str:
        ...

def buttered() -> Depend[
    Need[Dough] | Need[Oven] | Need[Toaster] | Need[Butter],
    str
]:
    ...
```

<details>
<summary>Done when</summary>

the `Need[Butter]`-only signature makes `ty` report `invalid-yield` at `yield from toast()`,
naming `Need[Dough] | Need[Oven] | Need[Toaster]`.
With the full union,
the run prints the chapter's bread and toast lines and then your butter line.
Dropping `Toaster(3)` makes `ty` report `invalid-argument-type` at `run()`,
naming `Need[Toaster]`.

<details>
<summary>Solution</summary>

```python
# exercise_13.py
from kitchen import Dough, Oven, Toaster, toast
from record import record
from stateless import Depend, Need, need, run, supply

@record
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

Writing the signature as `Depend[Need[Butter], str]` first produces this diagnostic:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> exercise_13.py:14:25
   |
13 | def buttered() -> Depend[Need[Butter], str]:
   |                   ------------------------- Function annotated with yield
   |                   type `Need[Butter]` here
14 |     slice_ = yield from toast()
   |                         ^^^^^^^ expression of type
   |                         `Need[Dough] | Need[Oven] | Need[Toaster]`,
   |                         expected `Need[Butter]`
```

**Declare every inherited requirement.**
The diagnostic points at the `yield from`, not at the signature,
and it prints the whole union that `toast()` yields.
That union is the answer to "what does `buttered()` need?"
The fix is to write it down.
`buttered()` declares `Dough` and `Oven` in its type,
and its body reaches them through `toast()`.
That is the propagation the chapter describes:
a caller inherits every requirement of every Effect to which it delegates.

Removing `Toaster(3)` from `supply()` produces the second diagnostic,
and it is a different shape:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
  --> exercise_13.py:23:11
   |
23 | print(run(kitchen(buttered)()))
   |           ^^^^^^^^^^^^^^^^^^^ Expected `Generator[Async | Exception, Any, Unknown]`,
   |                               found `Generator[Need[Toaster], Any, str]`
```

**Answer every requirement at the edge.**
The second diagnostic tells you about the dependency two levels below `run()`.
`supply()` leaves `Need[Toaster]` in the channel,
so the requirement reaches `run()`.
`buttered()`'s body names `toast()` and `Butter` alone.
The requirement comes from `toast()`, which `buttered()` calls.
The type checker reports it at `run()`, the program's edge,
where no handler remains to answer it.

The two diagnostics divide the work.
`invalid-yield` catches an under-declared signature at the delegation that breaks it.
`invalid-argument-type` at `run()` catches an under-supplied environment at the program's edge.
In both, the type checker reads what depends on what from the types.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 14. A shared signature for a cast

> `play()` in `casts.py` accepts any three actors, matched or not.
> `kitties_and_puzzles()` and `warriors_and_weapons()` already share a signature.
> Give that shape a name so a caller can pass either one where a cast belongs,
> and say what that recovers of the *Abstract Factory* and what it does not.
> Then add a fourth actor to `encounter()` and count the lines you edit in `quest.py`,
> `casts.py`, and `two_games.py`.

<details>
<summary>Where to look</summary>

[Supplying a Whole Cast](../../Chapters/47_Effects--Stateless_in_Practice.md#supplying-a-whole-cast)
shows `casts.py` grouping matched actors in factory functions,
and [The Nine-Argument Ceiling](../../Chapters/47_Effects--Stateless_in_Practice.md#the-nine-argument-ceiling)
shows the limit of passing them to `supply()` one by one.
Give the shared signature a `type` alias over `Callable`,
and have the caller take that alias.
For the *Abstract Factory* question,
ask what the type says about the actors inside each factory.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_14.py
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
    ...

class Kitty:
    def name(self) -> str: ...

class Puzzle:
    def blocks(self) -> str: ...

class Warrior:
    def name(self) -> str: ...

class Weapon:
    def blocks(self) -> str: ...

class Loud:
    def say(self, line: str) -> None: ...

def play(
    narrator: Narrator, hero: Hero, obstacle: Obstacle
) -> None:
    ...

def kitties_and_puzzles(narrator: Narrator) -> None:
    ...

def warriors_and_weapons(narrator: Narrator) -> None:
    ...

type Cast = Callable[[Narrator], None]

def run_season(casts: list[Cast]) -> None:
    ...
```

<details>
<summary>Done when</summary>

a caller annotated with your named shape accepts both factories, `ty` passes,
and `play(Loud(), Kitty(), Weapon())` still type-checks and prints `and bats at the nasty weapon`.
Your fourth-actor count puts the most edits in `casts.py`, fewer in `quest.py`,
two in `two_games.py`, and none in the named shape.

<details>
<summary>Solution</summary>

The two factories in `casts.py` already have the same signature.
The exercise is to name it and see what naming it gains.
Here is the chapter's cast,
with each actor trimmed to one method so the whole cast fits in one listing:

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

def kitties_and_puzzles(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle())

def warriors_and_weapons(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon())

type Cast = Callable[[Narrator], None]

def run_season(casts: list[Cast]) -> None:
    for cast in casts:
        cast(Loud())

run_season([kitties_and_puzzles, warriors_and_weapons])
#: Kitty meets the puzzle
#: Warrior meets the nasty weapon
play(Loud(), Kitty(), Weapon())
#: Kitty meets the nasty weapon
```

**Name the factory's shape.**
The shared signature recovers the *Abstract Factory*'s interface.
`run_season()` accepts any function that stages a scene,
and its body names no family of actors.
Independence from the family is the property the pattern exists to provide.
Python provides that property,
because a function is already an object with a type.
Saying so takes no abstract factory class.

**Show the mismatch getting through.**
The shared signature does not recover the guarantee that makes the pattern worth naming.
`Cast` says "give me a narrator and I will stage something."
It leaves the actors inside free to come from different worlds.
The listing's last call is the proof: `play(Loud(), Kitty(), Weapon())`,
which the chapter also runs in `two_games.py`.
`play()` accepts a `Kitty` facing a `Weapon`.
Both satisfy their `Protocol`s, so the type checker accepts the call.
An *Abstract Factory* in a language with a family type expresses "these come from one world" in the type.
Here the matching is in `kitties_and_puzzles()`'s body,
a fact about how someone wrote that function.
Nothing checks it.

So the shared signature prevents some mismatches and permits others.
A caller that takes a `Cast` can no longer assemble a mismatched set by accident,
because it receives a whole cast and names no actor.
`play()` is still there and still accepts any three actors.

Adding a fourth actor to the chapter's three-actor version shows which files need the edits.
`quest.py` gains a `Protocol`, a member in `encounter()`'s `Need[...]` union,
a `yield from`, and a line that uses the new actor, so four edits.
`casts.py` gains a name in its `from quest import` line,
a parameter on `play()`, an argument in the `supply()` call,
a class for each family, and an argument in each of the two factory calls,
so seven.
`two_games.py` needs two edits:
its direct `play()` call and the `from casts import` list that supplies the new actor.
Its two factory calls stay as they are.
The `Cast` alias keeps its signature,
because the new actor stays inside the factories.

That distribution is the argument for the factory.
The functions that name a whole cast take the edits,
and the code that calls a factory to stage a scene stays the same.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
