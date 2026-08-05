# Stateless in Practice

[Stateless](46_Stateless.md)
established the two channels an `Effect[A, E, R]` carries.
A dependency is a `Need` that `supply()` answers.
A failure is an exception that `@throws` lifts into the type and `catch()` takes back out.
A type checker verifies that every caller either absorbs an Effect or declares it.

Every Ability so far has been a `Need`.
This chapter opens by writing a `Need` from scratch,
which shows it is an ordinary class rather than a special form.
The rest of the chapter applies the machinery:

- Handlers that make an unpredictable source testable
- A handler that swaps implementations while a program runs
- A program whose signature is its own documentation,
  and whose body is only the success path
- Dependency graphs that go deep, and a cast of abilities that goes wide
- Decorators that add retry and parallelism to code they never edit
- An account of what the guarantee does not cover

## Abilities Are Not Special

An Ability subclasses `Ability[T]`, where `T` is the type its handler returns.
Here is the Stateless version of `Ask` and `Tell` from [Effect Management](44_Effect_Management.md#effects-by-hand):

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
the rule from [The Return Channel](45_Generators.md#the-return-channel),
and here that value is whatever the handler sent back.
The Ability produces nothing on its own.
`prompt` is payload on the request, there for the handler to read,
so the answer to an `Ask` is whatever `scripted()` returns.
A `Tell` needs no answer,
which is why `Tell` is `Ability[None]` and `capture()` returns `None`.
`ask()` and `tell()` are *accessors*:
small functions that each wrap one Ability and declare its answer type.
`need()` has the same shape,
and the ZIO listing in [Effect Management](44_Effect_Management.md#library-effect-management)
had an accessor object doing the same job.
The declared `Depend[Ask, str]` types `name` as `str` inside `greet()`.
You can skip the accessor and yield the Ability directly,
and the program still runs,
but under `ty` 0.0.65 the answer comes back as `Unknown` and the checking quietly stops.
The accessor pins it down.
That is what the `answer: str` inside `ask()` is doing.
`yield from Ask(prompt)` produces `Unknown` there too,
so the annotation is an assertion the checker takes on faith rather than a type it worked out.
`Ability[str]` is where the claim comes from,
and writing it at the binding keeps the accessor's claim in one place,
one line above the `Depend[Ask, str]` that repeats it to callers.

That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`,
and the difference deserves a moment.
`Ask` is an Ability, so it sits in the channel bare.
`Console` never was one.
It is an ordinary class, and `Need[Console]` is the Ability:
a request object carrying the class it asks for.
A type bound enforces the distinction.
`Effect`'s first type parameter accepts only `Ability` subclasses,
so writing `Depend[Console, None]` is rejected at the annotation,
before any `yield` is examined: `Console` is not assignable to the bound.

`handle()` reads the annotation on its argument to decide which Ability it answers,
which is why `scripted` and `capture` must annotate their parameters.
Each `handle()` subtracts one Ability,
so `half` still needs an `Ask` and `full` needs nothing.
Naming the two stages also matters to the checker,
for a reason the next section gives.

Now compare this listing to `ask_tell.py` again.
The by-hand version put two objects in every signature.
This one threads nothing.
`greet()` takes no arguments,
and the two Effects live in the return type where a checker can follow them.
That second channel in the signature is the one [Effect Management](44_Effect_Management.md#effect-management-systems)
said an EMS needs.

The whole library is visible in `two_way_generator.py` from [Generators](45_Generators.md#a-generator-is-a-description).
An Effect is a generator, so nothing stops you from driving one yourself:

```python
# effect_by_hand.py
from greeter import Console, greet

effect = greet("Alice")
request = next(effect)
print(f"{type(request).__name__}({request.t.__name__})")
#: Need(Console)
try:
    effect.send(Console())
except StopIteration:
    print("returned")
#: Hello, Alice!
#: returned
```

`greet("Alice")` yields a `Need` object carrying the requested type,
as `interview()` yielded `"name"`.
Answering it with `send(Console())` resumes the body,
which prints the greeting and finishes.
Every tool in the library packages those two calls.
`handle()` is `drive()` with a type lookup in place of the dictionary,
`run()` is the loop at the bottom,
and `supply()` is `handle()` prepackaged for `Need`:
a handler whose answer to `Need[T]` is whichever supplied instance is a `T`.

## Scripting an Unpredictable Source

Every handler so far gave the same answer each time it was asked.
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
`Flip` carries no data, so it needs no fields,
while `Ask` and `Tell` each carried the payload the request had to deliver.
The Ability's whole content is its type and the `bool` it produces.

The parentheses in `if (yield from flip()):` are required.
A `yield` expression is allowed on the right side of an assignment,
as a statement of its own, or inside parentheses.
An `if` condition is none of those,
so `if yield from flip():` is a syntax error.

Two handlers answer the same function.
`scripted` walks an iterator over a fixed sequence,
so the five tosses are decided before the program runs and the count is `3`.
`coin` calls `random.random()`, so ten thousand tosses come out near half heads.
`count_heads()` cannot distinguish the two,
because either answer arrives through the same `send()` channel.

The scripted handler holds state.
`next(script)` produces a different value at each request,
which one supplied instance cannot do.
Every scripted test double has this shape: a queue handing out canned responses,
a network stub that fails twice and then succeeds, or the clock below.

### A Clock

Reading the current time is another side cause.
A real clock answers with the present moment,
so a test cannot ask it what happens at some critical time (midnight, tomorrow, etc.).
The Ability and its accessor sit in their own file,
because two listings in this section ask the same clock different questions:

```python
# clock.py
from datetime import datetime
from stateless import Ability, Depend

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment
```

Like `Flip`, `Now` carries no data.
Its answer type is its whole content: a handler for `Now` returns a `datetime`,
and `now()` is the accessor that declares that type.

`stamp()` puts the current time into its output,
and `batch_due()` decides whether a day has passed since the last run.
Against a real clock neither is testable.
One produces a different string every minute,
and the other needs you to wait a day to watch it return `True`.

```python
# frozen_clock.py
from datetime import datetime, timedelta
from typing import Final
from clock import Now, now
from stateless import Depend, handle, run

def stamp(message: str) -> Depend[Now, str]:
    moment = yield from now()
    return f"[{moment:%Y-%m-%d %H:%M}] {message}"

def batch_due(last_run: datetime) -> Depend[Now, bool]:
    moment = yield from now()
    return moment - last_run >= timedelta(hours=24)

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
so there is nothing to monkeypatch and nothing to wait for,
and a production handler that returns `datetime.now()` leaves the function unchanged.

Skipping the wait is the obvious benefit.
A handler can also produce moments that are hard to get from a real clock.
Here, `archive()` reads the clock twice,
once to name a file and once to stamp what goes in it:

```python
# midnight.py
from datetime import datetime, timedelta
from typing import Final
from clock import Now, now
from stateless import Depend, handle, run

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
Now the file is named for January 1 and the entry inside it is dated January 2.
A day of entries can end up in the wrong file,
and the window where this happens is one second wide.

Using a real clock, you wait for that window and probably miss it.
Tests that run at nine in the morning cannot see it,
and the bug report says the log file is occasionally short by a few lines.
The Ability makes the moment reachable.
`archive()` does not read a clock; it asks for a moment,
and a handler decides which moment that is.
Both handlers answer the same two requests;
they differ in whether midnight falls between them.

`crossing` follows the same pattern as `scripted` in `coin_toss.py`.
It walks a fixed list, so it holds state between requests,
which is how it answers the same question two ways.
A supplied instance could not do this, and neither could `frozen` or `tomorrow`,
since each reports one moment however often it is asked.

Compare this to `student_pairs.py` in [Functional Toolkits](41_Functional_Toolkits.md#case-study-pairing-rotations),
which made randomness repeatable a different way, by taking a `seed` parameter.
That works, but every function between the caller and the `random.Random` call must declare the parameter and pass it along.
Here the source is named in the return type instead,
and no signature between `handle()` and the request mentions it.

Both abilities in this section are side causes,
in the vocabulary of [Effect Management](44_Effect_Management.md#subdividing-the-impure-portion):
the function reads something from outside.
The `Recorder` of [Swapping the Implementation](46_Stateless.md#swapping-the-implementation)
stood in for a side effect, where the function writes something outward.
The technique did not change between the two.
Name each contact with the outside as an Ability and bind it at the edge to whatever the context needs.
What an EMS adds is that the declaration cannot be skipped by accident.

## Switching Implementations Mid-Run

Both handlers in the last section answered with a value.
A handler can also answer with an object,
and it can choose a different object at each request.
That is what `supply()` cannot do,
because it binds one instance for the whole run.
When the implementation a program depends on has to change while the program is running,
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
`draw()` is the boundary function:
it asks the source whether it can still supply,
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

def run_load(start: int, hours: int) -> Depend[Outlet, None]:
    caught = catch(Drained)
    hour, remaining = start, hours
    while remaining:
        source = yield from plug(hour)
        with connected(source) as power:
            while remaining:
                failure = yield from caught(draw)(power, hour)
                if failure is not None:
                    break
                print(f"  {hour}:00")
                hour += 1
                remaining -= 1

def site() -> tuple[Solar, Battery, Grid, Backup]:
    return Solar(), Battery(40), Grid(range(22, 24)), Backup(3)

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
so the charge is spent first and the grid picks up at 19:00.
Reordering that tuple is the whole difference between the two runs.
Priority, thresholds, and the outage schedule live in `controller()`,
while `run_load()` decides when to give up on the source it holds.

The load's declared dependency never changes.
`Depend[Outlet, None]` says it needs an `Outlet` from the first hour to the last,
and that type is written once.
What changes is the object answering the need, four times, mid-run.
Binding a dependency before the program starts cannot express this,
because there is no single right answer to bind.
Here the binding is a function call, so it reads the world at each request.
[Swapping the Implementation](46_Stateless.md#swapping-the-implementation)
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
No `@throws` lifted it,
so it travels through `run()` untracked and no signature mentions it.
A handler sits outside the channel it feeds.

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
The three `@throws` functions are the pattern for reaching ordinary code:
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

The decorator adds the error the same way it did for `score()` in [The Error Channel](46_Stateless.md#the-error-channel).
`ty` reports `fetch_headline` as `() -> Generator[Need[Feed] | Unavailable, Any, str]`,
which is `Effect[Need[Feed], Unavailable, str]`.
`research()` splits the two because a function that only transforms its arguments is easier to test on its own,
and because the split keeps the Ability requests collected in one place.
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

def report() -> Depend[Need[Feed] | Need[Encyclopedia], str]:
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
SHELF: Final[Library] = Library({"stock market": "a history"})
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

Four runs of one program, differing in what was supplied.
The first finds its article.
The second exercises `NotInteresting`, the third `NoArticle`,
and the fourth `Unavailable`, so every failure the signature declares gets used.
A full Effect system calls each pair of bindings a *scenario*,
and here a scenario is nothing more than arguments to `supply()`.

Every printed line in that trace comes from a supplied implementation,
because the pipeline holds no output of its own.
The second run also stops after `feed: fetching`.
`topic_of()` yielded a `NotInteresting`,
which ended `research()` where it stood,
so the `need(Encyclopedia)` two lines below it never ran and no library was consulted.
`catch()` received that failure and `report()` matched on it as a value,
which is why the run still prints a message.
A failure ends the remaining steps the way a raised exception would,
and no step tested for it.
Where the run stops depends on where the failure arises.
The fourth run prints no trace,
since `DeadWire.latest()` raises before printing,
while the third reaches the library and fails there.

`report()` is where the two channels come apart,
and its annotation is worth reading twice.
`catch()` emptied the error channel, so `report()` cannot fail.
It still declares both abilities,
because catching an error does nothing about a dependency.
If you annotate `report()` as `Success[str]`,
`ty` names the `yield from` that still carries `Need[Feed] | Need[Encyclopedia]`.
`supply()` empties that half, and `run()` accepts what is left.

`outcome()` also earns its annotations.
`Wire` and `Library` are structural implementations,
so `supply(Wire(...), Library(...))` builds handlers for `Need[Wire]` and `Need[Library]`,
the mismatch that [Supplying an Interface](46_Stateless.md#supplying-an-interface)
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

Three lines of work sit inside nine lines of handling.
The pipeline is in there, but you have to look for it.
The Effect version moved those nine lines into `report()`,
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
so a fourth one can be added with nothing to tell the caller.
And the handling is interleaved with the logic:
`research_and_report()` decides both what to do about a failure and what to say about it.
The Effect version separates those,
so a second caller can catch the same three failures and choose different messages,
retry the whole pipeline, or let one failure through to the edge,
without touching the pipeline.

## Dependencies That Need Dependencies

`research()` asked for two things, and both were leaves.
Nothing had to be built before a `Feed` or an `Encyclopedia` could be supplied.
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

Appliances are supplied and products are made,
and the listing keeps the two apart.
`Dough`, `Oven`, and `Toaster` are the leaves,
so `supply()` binds one instance of each.
The loaf is not a leaf.
`bread()` is an Effect that produces a loaf,
so `toast()` obtains one by writing `yield from bread()` rather than by asking for a `Need[Bread]`.
Nothing supplies a loaf, because when `supply()` is called there is no loaf.

The graph arrives in the signature, flattened into a union.
`toast()` declares all three leaves although its body names one of them.
`Need[Dough]` and `Need[Oven]` travel up through `yield from bread()`,
which carries the inner Effect's abilities to its caller.
The checker maintains that union.
If you declare `toast()` with `Need[Toaster]` alone,
`ty` points at the delegation:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> bakery.py:31:16
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

The other end is checked too.
If you leave `Oven(220)` out of `supply()`,
`run()` reports a `Generator[Need[Oven], Any, str]` where it expected an empty Ability channel,
the rejection that [Forgetting to Supply](46_Stateless.md#forgetting-to-supply)
showed, now arising from a dependency two levels down.
`Oven` and `Toaster` are distinct types,
so the ambiguity of [When Two Implementations Match](46_Stateless.md#when-two-implementations-match)
cannot arise here.
ZIO makes both of them a `HeatSource` and must report the clash.

Here is what ZIO does that Stateless cannot.
`Bread.homeMade` is a `ZLayer`: a constructor that is an Effect.
It can print, it can fail, and it can be retried,
and the compiler resolves it into a tree with `Oven` and `Dough` beneath it.
You provide that layer rather than a finished loaf.
Stateless has no such thing.
`supply()` matches instances that exist,
and `handle()` answers an Ability with an ordinary function,
so a constructor cannot be an Effect.
That is the shape of the listing above.
Leaves are bound at the edge, products come from an explicit `yield from`,
and the graph you can read is the union in the signature.

## Supplying a Whole Cast

The bakery graph went deep.
Three appliances, one of them reached through another Effect.
The next example goes wide.
[Abstract Factories](27_Factory.md#abstract-factories)
built a gaming environment where a `GameElementFactory` returned a matched `Character` and `Obstacle`,
and a `GameEnvironment` played whatever that factory produced.
Here the cast widens to five kinds of actor, each requested as an Ability:

```python
# arena.py
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
    narrator.say(f"{hero.name()} crosses the {terrain.underfoot()}")
    narrator.say(hero.approach(obstacle.blocks()))
    narrator.say(f"and wins {reward.prize()}")
```

`encounter()` is the entire engine,
and the only types it mentions are the five Protocols.
No concrete class appears in it, and it prints nothing.
Output is an Ability like the other four:
`Narrator` is one of the five requests,
so the code that supplies it chooses whether a line is printed,
collected in a list, or discarded.
There is no `GameEnvironment` to construct and no factory to hold.
The five-way union is written out in full rather than aliased,
for the reason given in [Retrofitting an Effect](46_Stateless.md#retrofitting-an-effect).

Five abilities need five distinct shapes.
`Obstacle.blocks()` and `Terrain.underfoot()` could each have been named `describe()`,
and then any obstacle would satisfy `Terrain` as well,
leaving argument order to decide which request each one answered,
the ambiguity of [When Two Implementations Match](46_Stateless.md#when-two-implementations-match).
Every pair of abilities with a wide cast raises the odds of a collision.

The cast is a set of ordinary classes that inherit nothing:

```python
# casts.py
from arena import Hero, Narrator, Obstacle, Reward, Terrain, encounter
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

class NastyWeapon:
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
    play(narrator, Warrior(), NastyWeapon(), Wasteland(), Gold())
```

`play()` is the boundary function of [Composing a Program](#composing-a-program),
grown from two parameters to five.
Its annotations do the upcasting, so no actor needs `as_type()`,
and its body is the one place in the program where an Ability meets an implementation.
`kitties_and_puzzles()` and `warriors_and_weapons()` are what the two concrete factories became.
Each was a class with a method per product;
each is now a function that hands `play()` a matched set.
The parallel hierarchies are gone with them.
`Kitty` does not extend a `Character` base class,
`Puzzle` does not extend an `Obstacle` base class,
and no class is named in the engine:

```python
# two_games.py
from dataclasses import dataclass, field
from casts import (
    Kitty,
    NastyWeapon,
    Wasteland,
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
play(Loud(), Kitty(), NastyWeapon(), Wasteland(), Yarn())
#: Kitty crosses the cracked wasteland
#: and bats at the nasty weapon
#: and wins a ball of yarn
script = Script()
kitties_and_puzzles(script)
print(len(script.lines), script.lines[1])
#: 3 and bats at the puzzle
```

One engine, four runs, and the only difference is what was supplied.
The last two are the ones to study.

The third mixes the casts, and nothing objects.
A `Kitty` bats at a `NastyWeapon` across a `Wasteland`; it type-checks,
and it runs.
That is a real loss against the Abstract Factory,
whose purpose is families of matched products:
`KittiesAndPuzzles.make_obstacle()` cannot return a `NastyWeapon`,
because the pairing is built into the class.
`supply()` takes a flat list and checks each argument against one Ability,
never against the others.
The matched set comes back only if you write it down,
which `kitties_and_puzzles()` does.
The guarantee moved from a class hierarchy into a two-line function,
and it is worth knowing which of those you are getting.

The fourth run swaps one cast member and captures the output.
`Script` records what it is told,
so a test reads the lines back as a list with no `capsys` and no monkeypatching,
the same swap `test_greeter.py` in [Swapping the Implementation](46_Stateless.md#swapping-the-implementation)
made with one Ability rather than five.
Printing was never in the engine to be intercepted.

There is a ceiling on how wide the cast can get.
`supply()` is declared with overloads for one through nine values,
so a tenth argument matches none of them:

```text
error[no-matching-overload]: No overload of function `supply`
matches arguments
```

The call still runs correctly, since the implementation is variadic,
but the checking this chapter relies on is gone.
Two chained handlers keep it: `supply()` the first five,
apply that to the Effect, then `supply()` the rest to what remains,
which is the partial handling of [Emptying the Channels](46_Stateless.md#emptying-the-channels).
Nine is also a fair warning about the design.
An Effect that asks for ten separate things is usually two Effects.

## Adding Behavior to an Existing Effect

[The Success Path](#the-success-path)
said that a caller could retry a pipeline without touching it.
Stateless provides a few decorators that add such behavior.
Retry is the one worth studying, because of what it does to the type.

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

def save_user(user: str) -> Effect[Need[Database], Crashed, str]:
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
print(run(supply(Database(failures=2), Time())(retried)("Morty")))
#: attempt 1: saving Morty
#: attempt 2: saving Morty
#: attempt 3: saving Morty
#: Morty saved
caught = catch(RetryError)(retried)
outcome = run(supply(Database(failures=9), Time())(caught)("Morty"))
print(type(outcome).__name__)
#: attempt 1: saving Morty
#: attempt 2: saving Morty
#: attempt 3: saving Morty
#: RetryError
```

`three` is built from the only two schedule combinators the library has:
`spaced()` yields a fixed interval forever,
and `recurs()` stops it after `n` yields.
One attempt fails.
Three attempts against a database that fails twice succeed on the third,
and three attempts against one that always fails produce a `RetryError` holding every failure.
`save_user()` was not edited for any of this.

Read the trace before you use this on real code.
Each attempt line is `Database.save()` running again,
so anything the decorated function does happens once per attempt.
Retrying a charge or an append duplicates it.
Nothing in the type says whether a retry is safe,
because `Effect[A, E, R]` tracks what a function needs and how it fails,
not whether running it twice means the same as running it once.
That judgment stays with you.

### Why `retry()` Decorates the Function

Notice that `retry()` decorates the function, not the Effect.
`retry(three)(save_user("Morty"))` is not available,
and the reason is the substrate.
A Stateless Effect is a generator, so it runs once and is then spent:

```python
# spent.py
from flaky import Database, save_user
from stateless import run, supply

effect = supply(Database(failures=0))(save_user)("Morty")
print(repr(run(effect)))
#: attempt 1: saving Morty
#: 'Morty saved'
print(repr(run(effect)))
#: None
```

Re-running the spent Effect does not fail loudly.
The exhausted generator has nothing left to do,
so the second `run()` returns `None` where the signature declares a `str`,
with no exception and no complaint from the checker.
A retry therefore has to rebuild the description from the function,
which `retry()` does internally.
The special case is `success()`: it builds a constant rather than a generator,
and a constant answers every `run()` with the same value.
The one-shot behavior belongs to any Effect that contains a `yield`,
which is any Effect that does work.
Where ZIO attaches `retryN` to an Effect value it can replay,
Stateless attaches it one level up.

### What Retry Costs the Signature

Now read what the decoration did to the type.
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
If you leave the `Time()` out, the program does not build.
This is the thesis of both chapters applied to a cross-cutting concern.
Adding retry to a hundred call sites in a system with untracked Effects changes nothing you can see;
here it changes a type, and every caller learns about the new dependency.

The renamed error invites a mistake the checker accepts.
If you write `catch(Crashed)(retried)`, catching the error you started with,
nothing complains.
The result type gains a `Crashed` branch that cannot occur,
`RetryError[Crashed]` stays in the error channel,
and at runtime the failure passes the useless `catch()` and escapes at the edge.
`catch()` must name what the channel holds at the point of decoration,
and after `retry()` that is `RetryError[Crashed]`, not `Crashed`.

One rough edge: `RetryError` declares an `errors` attribute that `retry()` never assigns,
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
`repeat()` continues until the schedule is exhausted,
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
That wrapper exists because a generator cannot be replayed,
which is the same fact that made `retry()` decorate the function.

## Running Effects in Parallel

`fork()` hands an Effect to an `Executor` and returns a `Task`,
and `wait()` collects the result.
This is the same `wait()` that awaited a coroutine in [Waiting on a Coroutine](46_Stateless.md#waiting-on-a-coroutine);
it accepts a `Task` as readily as an awaitable:

```python
# parallel.py
import time
from concurrent.futures import Executor, ThreadPoolExecutor
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
print(out)
#: [0, 1, 4, 9, 16]
print(f"five 50ms tasks under 150ms: {elapsed < 0.15}")
#: five 50ms tasks under 150ms: True
```

Five tasks that each sleep 50 milliseconds finish in about the time of one.
The pool is an Ability, not a global,
so `squares()` declares `Need[Executor]` and names no pool.
Supplying a `ProcessPoolExecutor` instead moves the same work into processes,
with no change to `squares()`.
`as_type(Executor)` appears for the reason it always does:
`ThreadPoolExecutor` is the more specific type,
and `squares()` asked for the general one.

The checker enforces one restriction.
A forked Effect must have nothing left to supply.
`fork()`'s four overloads accept an Effect whose Ability channel holds `Never`,
an exception type, or `Async`,
because `fork()` runs the Effect with `run()` inside the worker.
If you decorate a function that still declares a `Need`, `ty` rejects it,
listing the overloads it failed to match.
Supply first, then fork.

Notice where the pool's lifetime is managed.
The `with` block sits outside `run()`, at the edge, in ordinary Python.
Stateless has no scoping mechanism of its own,
so a resource either lives in a `with` block outside the Effect,
as the pool does here, or the Ability method owns it:
the library's own `Files` Ability opens and closes a file inside a single `read_file()` call.
What you cannot express is acquiring a resource in one Effect and releasing it after a later one finishes,
which is the flat resource management a native Effect system provides.
Python's own answer to that is `ExitStack` in [Combining Context Managers](15_Context_Managers.md#combining-context-managers),
which holds a set of managers decided at runtime and unwinds them together.
It flattens the nesting without knowing anything about Effects,
so this gap is narrower than it first appears.

## The Toolkit

Here is every tool from both chapters.
Each one builds a description, rewrites a description's type, or executes one.
The type column is the part worth memorizing.

Three build a description:

| Tool | Applied to | What it does to the type |
|---|---|---|
| `success(value)` | A value | Wraps it as `Success[R]` |
| `need(C)` | A class | Builds `Depend[Need[C], C]`, producing an instance |
| `wait(target)` | A `Task` or any awaitable | Adds `Async`; produces the awaited `R` |

The rest decorate a function that returns an Effect,
rewriting the type that function declares:

| Tool | What it does to the type |
|---|---|
| `supply(*instances)` | Subtracts each `Need[T]` matched by `isinstance()` |
| `handle(handler)` | Subtracts the Ability the handler's parameter names |
| `catch(*E)` | Moves each `E` from the error channel into the result |
| `retry(schedule)` | Adds `Need[Time]` and `Async`; the error becomes `RetryError[E]` |
| `repeat(schedule)` | Same additions; the result becomes a tuple of every run |
| `memoize` | Type unchanged; the result is cached by argument |
| `fork` | Adds `Need[Executor]`; the result becomes `Task[R]` |
| `@throws(*E)` | Adds each `E` to the error channel |

Two rows carry a caveat.
`fork` needs a function whose Effect has nothing left to supply,
so supply first, then fork.
`@throws` is the entry point rather than a transformation:
it decorates an ordinary function that raises exceptions,
turning it into one that returns an Effect.

Two execute an Effect that has only `Async` and errors left,
raising a leftover error rather than returning it:

| Tool | Where it is called |
|---|---|
| `run(effect)` | From synchronous code |
| `await run_async(effect)` | From inside a running event loop |

These two are the only functions that perform work,
which is the description/execution split in table form.

## Where the Guarantee Stops

There are five limits worth knowing.

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
It cannot verify that everything effectful was declared,
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
    print(type(e).__name__)
#: ZeroDivisionError
```

`@throws` lifts only the exception types it names, and `ratio()` names none,
so the `ZeroDivisionError` propagates as an ordinary raised exception,
untracked.
`catch()` matches the values an Effect yields, not exceptions the body raises,
so a failure that was never lifted by `@throws` goes past `catch()` untouched.
That is the version of this hole to watch for,
because `catch(ZeroDivisionError)` type-checks and then does nothing:
the protection appears to be there.
The channel carries only what was put into it.

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

### 2. The checker can give up quietly

How much of a type survives partial handling depends on your checker rather than on the library.
Handling some of what an Effect declares works correctly under `ty` 0.0.65.
If you supply one of two abilities, the other stays in the signature:

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
    print(type(e).__name__)
#: MissingAbilityError
```

`half` is `() -> Depend[Need[Log], None]`.
The `Console` was subtracted and the `Log` was not,
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

What still defeats the checker is applying two handlers in one expression.
If you write `handle(scripted)(handle(capture)(greet))`,
`ty` gives up on the nested inference and infers `Unknown`,
which is permissive enough to hide a genuinely missing handler.
If you name the intermediate, the types come back:

```python
half = handle(capture)(greet)  # () -> Depend[Ask, None]
full = handle(scripted)(half)  # () -> Success[None]
```

That is why `ask_tell_stateless.py` binds `half` and `full` instead of nesting the calls.
The habit is worth keeping generally.
A named intermediate is where you read the Ability that is left,
which is the information this library exists to give you.
You have now seen three of these checker gaps:
the nested handler expression here,
the direct Ability yield that types as `Unknown`,
and the `type` alias in [Retrofitting an Effect](46_Stateless.md#retrofitting-an-effect)
that turns the yield check off.
Each has the same shape.
The library's types are asking the checker a hard inference question,
and where the checker gives up, it gives up quietly.
Trust a green check only where a red one has shown you it can appear.

### 3. Handlers cannot capture the continuation

`Effect` is a monad.
`success()` lifts a value into it, `yield from` chains two of them together,
and the generator body is syntax that hides the chaining.
`Result` in [Error Handling](42_Functional_Error_Handling.md#composing-with-bind)
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
A Python generator is one-shot, so there is nothing to resume twice.

Two pieces of the library are evidence of that ceiling.
`Effect[A, E, R]` carries a separate `E`, worked by `@throws` and `catch()`.
Koka needs no such type parameter,
because an exception there is an ordinary Effect whose handler declines to resume.
The extra type parameter exists because a Stateless Ability cannot fail,
and the `ZIO[R, E, A]` of [Effect Management](44_Effect_Management.md#library-effect-management)
carries one for the same reason.
`Async` is the other piece.
Native systems derive asynchronous execution from Effects,
while Stateless provides `Async` as a built-in that `run()` interprets,
because the driver loop can await where a handler cannot.

### 4. Cost

Every effectful function becomes a generator function,
which means it cannot also be a plain function,
and calling it returns a description that somebody must run.
Type errors from a library this generic are long and mention internals.
And a third-party function that knows nothing about Effects must be wrapped in `@throws` or reached through a `need()` before it can participate.
An EMS is a decision about a whole codebase,
not a utility you import for one module.

### 5. Much of a mature Effect system is missing

Dependency wiring is the first gap,
and `bakery.py` in [Dependencies That Need Dependencies](#dependencies-that-need-dependencies)
showed its shape.
`supply()` binds instances that are already built,
and `handle()` takes an ordinary function,
so constructing a dependency can never be an Effect.
ZIO's `ZLayer` is a constructor that can read configuration, fail,
and be retried, and it resolves a dependency graph at compile time,
reporting a cycle or a missing provider by name.
Stateless has no equivalent,
so the wiring at the edge is written by hand and a `supply()` call is checked for completeness but not for how it was assembled.
The operator set is thin in the same way.
There is `retry()` and `repeat()`,
and `Schedule` offers a fixed interval and a repeat count,
with no exponential backoff and no jitter.
There is no timeout, no `race`, no fallback combinator, and no finalizer,
which rules out the hedging strategy that races a delayed second request.
Concurrency is `fork()` and `wait()` with no guarded mutable cell,
so shared state between forked Effects is your problem and Python's,
with no help from the type checker.
Above that sit the resilience patterns a production system eventually needs,
rate limiting, bulkheads, and circuit breakers, none of which exist here.
The library is a working demonstration of Effect tracking in Python's type system,
and that is different from a platform for building distributed systems.

## Costs and Benefits

[Effect Management](44_Effect_Management.md#effects-are-the-next-barrier)
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
That is the property this book has been circling since [Foundations](40_Functional_Foundations.md#pure-functions).
Purity is valuable because it is verifiable,
and verification performed by reading code does not scale.

There is a second gain, and it shows when you put functions together.
Python has a separate mechanism for each concern an Effect type carries.
Absence is `T | None`.
Failure is a raised exception,
or the `Result` that [Error Handling](42_Functional_Error_Handling.md#a-result-type)
built.
Asynchrony is `async def` and `await`.
A resource's lifetime is a `with` block.
Each is reasonable alone, and they do not compose with each other.
Some pairs cannot be converted.
An `Awaitable` cannot become a `Result` without blocking and giving up the asynchrony.
A `with` block's guarantee is lexical,
so it cannot be handed to a caller as a value the way a `Result` can.
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
The techniques in [Converting Effectful to Pure](44_Effect_Management.md#converting-effectful-to-pure),
returning a `Result`, restricting a type so bad values cannot exist,
and passing dependencies in rather than constructing them,
capture much of the benefit at a fraction of the cost.
Use Stateless when a system is large enough that hidden Effects have already cost you a production incident,
and when the team will hold the line at every boundary.
Below that scale, the discipline matters and the machinery is optional.

But the direction is worth watching.
Python got one Effect tracked into its type system with `async`.
The languages listed under [Native Effect Management](44_Effect_Management.md#native-effect-management)
track all of them.
Stateless is the demonstration that Python's type system is expressive enough to do it,
given a library willing to encode everything into return types.
What is missing is not the capacity.
It is a language that does the encoding for you.

## Exercises

1.  `crossing` in `midnight.py` walks a fixed list,
    so it answers two requests.
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
    Follow the checker's complaints until the program builds again,
    and list every line you had to edit.
    Then do the same to `research_by_hand.py` and say which tool told you where to go in each case.
6.  `scenarios.py` supplies a `DeadWire` that fails before printing.
    Write a `DullWire` whose `latest()` succeeds but returns a headline with no topic in `TOPICS`,
    and predict the trace before running it.
7.  Wrap `research()` in `retry()` and supply a `Time()`.
    Explain what happens under the `WEATHER` scenario and why retrying a `NotInteresting` failure is the wrong behavior,
    then say what an Effect system needs for you to retry only `Unavailable`.
8.  Change `parallel.py` to use a `ProcessPoolExecutor` instead of a `ThreadPoolExecutor`,
    and confirm `squares()` is unchanged.
    Then try to fork an Effect that still declares a `Need`,
    and record what `ty` says.
