# Stateless: Solutions

Each listing below is self-contained, redeclaring the `Console` and
`greet()` it needs instead of importing the chapter's, so a solution
keeps working when a chapter listing changes.

## 1. A `Console` that reads as well as prints

```python
# test_ch46_ask_and_greet.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Console(Protocol):
    def print(self, message: str) -> None: ...
    def read(self, prompt: str) -> str: ...

class Terminal:
    def print(self, message: str) -> None:
        print(message)

    def read(self, prompt: str) -> str:
        return input(prompt)

@dataclass
class Scripted:
    answer: str
    printed: list[str] = field(default_factory=list)

    def print(self, message: str) -> None:
        self.printed.append(message)

    def read(self, prompt: str) -> str:
        return self.answer

def ask_and_greet() -> Depend[Need[Console], None]:
    console = yield from need(Console)
    name = console.read("What is your name? ")
    console.print(f"Hello, {name}!")

def test_ask_and_greet_uses_the_answer_it_reads() -> None:
    scripted = Scripted("Alice")
    run(supply(as_type(Console)(scripted))(ask_and_greet)())
    assert scripted.printed == ["Hello, Alice!"]

scripted = Scripted("Bob")
run(supply(as_type(Console)(scripted))(ask_and_greet)())
print(scripted.printed)
#: ['Hello, Bob!']
```

Supplying the real one is the same call with `Terminal()` in place of
`Scripted(...)`, and the session reads:

```text
What is your name? Alice
Hello, Alice!
```

The demo in `test_ch46_ask_and_greet.py` uses `Scripted` rather than
`Terminal` for the reason any book listing does: a call to `input()`
has no terminal to read from. The substitution is the whole point
either way, and neither binding required a change to
`ask_and_greet()`, which is character-for-character the same function
under both.

It could not have required one. `ask_and_greet()` names a capability
in its return type and calls two methods on whatever answers.
`Terminal`, `Scripted`, and any third implementation are
interchangeable because none of them appears in the Effect. Adding
`read()` to the protocol changed which classes qualify, and `supply()`
still picks among them the same way.

`as_type(Console)` is doing quiet work in both calls, and the work is
static. `supply()` reads the Ability from the declared type of its
argument, so `supply(scripted)` alone would build a handler for
`Need[Scripted]` rather than the `Need[Console]` that
`ask_and_greet()` requests. The wrapper turns that static type into
`Console`. At runtime the wrapper returns `scripted` untouched, and
`supply()` still finds it, because `Console` is `@runtime_checkable`
and `isinstance()` matches `Scripted` on shape.

## 2. An undeclared need, declared

Removing the `# type: ignore` from `undeclared_need.py` produces:

```text
error[invalid-yield]: Yield expression type does not match annotation
 --> undeclared_need.py:7:20
  |
5 | def greet_all(names: list[str]) -> Success[None]:
  |                                    ------------- Function annotated
  |                                    with yield type `Never` here
6 |     for name in names:
7 |         yield from greet(name)
  |                    ^^^^^^^^^^^ expression of type `Need[Console]`,
  |                    expected `Never`
```

`Success[None]` is `Effect[Never, Never, None]`: an Effect that needs
nothing, fails with nothing, and returns nothing. `Never` in the yield
channel means no value of any type may travel there, so a single
`Need[Console]` coming up from `greet()` contradicts it.

The fix is the annotation, and only the annotation:

```python
# exercise_2.py
from stateless import Depend, Need, need, run, supply

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_all(names: list[str]) -> Depend[
    Need[Console], None
]:
    for name in names:
        yield from greet(name)

run(supply(Console())(greet_all)(["Alice", "Bob"]))
#: Hello, Alice!
#: Hello, Bob!
```

The body never changes. `greet_all()` was already doing the right
thing. Its signature was describing a different function.

What its callers must now declare is the point of the exercise. Before,
`greet_all()` claimed to need nothing, so a caller could run it with no
environment: `run(greet_all(names))`. Now every caller has two
options, the same two `greet()`'s callers had. Supply a `Console`,
ending the requirement, or declare `Need[Console]` in its own return
type and pass the requirement further up. No third option exists,
which is what makes the dependency visible. The requirement appears in
the signature of every function between the one that uses it and the
one that supplies it, and the type checker refuses to let any of them
stay silent.

## 3. Catching an error that is already handled

```python
# exercise_3.py
from typing import Final, assert_never, reveal_type
from stateless import Success, Try, catch, throws

RAW: Final[dict[str, str]] = {"Alice": "42", "Bob": "seven"}

@throws(KeyError, ValueError)
def read_score(name: str) -> int:
    text = RAW[name]  # KeyError
    return int(text)  # ValueError

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(
        name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case ValueError():
            return f"{name}: unreadable"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

def one_unhandled(name: str) -> Try[ValueError, str]:
    value: int | KeyError = yield from one(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

if __name__ == "__main__":
    reveal_type(catch(ValueError)(one_unhandled))
```

`ty` reveals:

```text
info[revealed-type]: Revealed type
`(name: str) -> Generator[Never, Any, str | ValueError]`
```

`all_handled()` is `Success[str]`, which expands to
`Generator[Never, Any, str]`. The revealed type and that one both
carry `Never` in the yield channel, so both agree that nothing can
fail from here on. They differ in the return channel: `str` for
`all_handled()`, `str | ValueError` for the wrapped `one_unhandled()`.

The difference is where the error stopped travelling. `all_handled()`
catches both errors, then consumes both in its `match`, turning each
into a sentence and returning a `str`. No error remains, and the
`assert_never()` proves it: the `match` covers every case inside the
function.

`one_unhandled()` catches only the `KeyError` and consumes that one.
The `ValueError` stays declared, as `Try[ValueError, str]` says, so it
is still in the yield channel when `catch(ValueError)` wraps
`one_unhandled()`. `catch()` does not delete an error. It moves it
from the yield channel to the return channel, as a value. So the
`ValueError` leaves the failure channel and reappears beside the
`str`, and a caller needing a bare `str` has one case left to handle.

Both functions have handled every error `read_score()` declares. Only
`all_handled()` has *interpreted* what it caught. `catch()` turns a
failure into a value, and a `match` turns that value into a result.
Skipping the `match` leaves the caught error sitting in the return
type.

## 4. A `Log` protocol, and a test that records both

```python
# test_ch46_audit_log.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Console(Protocol):
    def print(self, message: str) -> None: ...

@runtime_checkable
class Log(Protocol):
    def write(self, entry: str) -> None: ...

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_logged(
    name: str,
) -> Depend[Need[Console] | Need[Log], None]:
    yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")

def greet_all(
    names: list[str],
) -> Depend[Need[Console] | Need[Log], None]:
    for name in names:
        yield from greet_logged(name)

@dataclass
class Recorder:
    printed: list[str] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)

    def print(self, message: str) -> None:
        self.printed.append(message)

    def write(self, entry: str) -> None:
        self.entries.append(entry)

def test_greeting_and_logging_are_both_recorded() -> None:
    recorder = Recorder()
    environment = supply(
        as_type(Console)(recorder), as_type(Log)(recorder))
    run(environment(greet_all)(["Alice", "Bob"]))
    assert recorder.printed == ["Hello, Alice!",
                                "Hello, Bob!"]
    assert recorder.entries == ["greeted Alice",
                                "greeted Bob"]

recorder = Recorder()
run(supply(as_type(Console)(recorder),
           as_type(Log)(recorder))(greet_all)(["Cyd"]))
print(recorder.printed, recorder.entries)
#: ['Hello, Cyd!'] ['greeted Cyd']
```

One object satisfies both protocols. The concrete-class version could
not arrange that: `Log` was a `dataclass` holding its own entries, so
a test had to construct one and read `log.entries` afterward. As a
`Protocol`, `Log` is a shape, and a single `Recorder` can have that
shape and the `Console` shape at once.

The two `as_type()` calls are what make one object answerable to two
requests. `supply()` reads the Ability from each argument's declared
type, so `supply(recorder, recorder)` would build a handler for
`Need[Recorder]`, an Ability neither Effect requests. Each wrapper
names the role this instance fills. Supplying the same object twice
under two different types is the case `as_type()` exists for.

Writing both assertions in one test is the payoff. A test holding the
whole environment can check that the greeting reached the console
*and* that the log recorded it, in one function, with no capture of
stdout and no temporary file. Both Effects were requests before they
were actions, so the test decides what performing them means.

## 5. A third material in the table

```python
# test_ch46_nailer.py
from dataclasses import dataclass
from typing import Final
import pytest
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Material:
    strength: int

@dataclass(frozen=True)
class Nailer:
    force: int

def holds() -> Depend[Need[Material] | Need[Nailer], bool]:
    material = yield from need(Material)
    nailer = yield from need(Nailer)
    return nailer.force < material.strength

WOOD: Final[Material] = Material(strength=5)
PLASTIC: Final[Material] = Material(strength=10)
METAL: Final[Material] = Material(strength=20)
HAND: Final[Nailer] = Nailer(force=4)
ROBOTIC: Final[Nailer] = Nailer(force=11)

@pytest.mark.parametrize("material, nailer, expected", [
    (WOOD, HAND, True),
    (PLASTIC, HAND, True),
    (METAL, HAND, True),
    (WOOD, ROBOTIC, False),
    (PLASTIC, ROBOTIC, False),
    (METAL, ROBOTIC, True),
])
def test_holds(
    material: Material, nailer: Nailer, expected: bool
) -> None:
    assert run(
        supply(material, nailer)(holds)()) is expected

print(run(supply(METAL, ROBOTIC)(holds)()))
#: True
```

`METAL` at strength `20` outlasts the robotic nailer's force of `11`,
so its two rows read `True` and `True`. `METAL` is the first material
in the table that survives both nailers.

The test function body needed no change because it never mentions a
material or a nailer. It receives two objects and an expectation,
builds an environment from them with `supply()`, and asks whether the
answer matches. The `parametrize` table decides which two objects
those are, and adding a row adds a case without touching the code that
runs it.

That separation is the same one running through the whole chapter, seen
from the testing side. `holds()` declares two requirements and never
names an instance, so every combination of instances is a valid
environment for it. The parametrize table is a list of environments,
and the test body is the driver that runs the Effect in each one. Six
rows share one assertion. A version constructing its own `Material`
inside `holds()` would need six copies of the function.

## 6. A handler that builds what was requested

```python
# exercise_6.py
from dataclasses import dataclass
from stateless import Depend, Need, handle, need, run

@dataclass
class Console:
    def print(self, message: str) -> None:
        print(message)

@dataclass
class Clock:
    def now(self) -> str:
        return "noon"

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def stamped(
    name: str,
) -> Depend[Need[Console] | Need[Clock], None]:
    clock = yield from need(Clock)
    console = yield from need(Console)
    console.print(f"[{clock.now()}] Hello, {name}!")

def default(ability: Need[Console]) -> Console:
    print(f"handler answered a request "
          f"for {ability.t.__name__}")
    return ability.t()

defaults = handle(default)
run(defaults(greet)("Alice"))
#: handler answered a request for Console
#: Hello, Alice!
run(defaults(stamped)("Bob"))  # type: ignore
#: handler answered a request for Clock
#: handler answered a request for Console
#: [noon] Hello, Bob!
```

`default()` never names `Console` in its body. It reads `ability.t`,
the class the request carries, and calls it, so it answers a request
by constructing the class asked for. That is the other kind of
default: `default_console.py` supplies one prepared instance, and
`default()` builds whatever the request names, on demand.

At runtime the handler answered three requests across the two calls,
two for `Console` and one for `Clock`, even though `default()`
annotates its parameter `Need[Console]`. `ty` believes the handler
answers only `Need[Console]`, which is why the second `run()` needs a
`# type: ignore` and would otherwise report a leftover `Need[Clock]`.

`handle()`'s `t = get_origin(t) or t` is the evidence. `handle()`
reads the annotation, reduces `Need[Console]` to its origin, `Need`,
and installs the runtime check `isinstance(ability, Need)`. That check
ignores the type argument, so every `Need[...]` request matches. The
type checker reads the same annotation without that reduction and
subtracts only `Need[Console]` from the requirements.

Neither view is wrong about what it describes. `isinstance()` cannot
test a type argument: `Need[Clock]` and `Need[Console]` are the same
runtime class, so no runtime check tells the two apart. The annotation
is the only place the distinction exists, and `handle()` uses it for
matching but cannot enforce it. The gap is real. A handler like
`default()` genuinely handles more than its type says, and one that
assumes `ability.t` is a `Console` would receive a `Clock` with
nothing to stop it.

## 7. Two ways to drop a `yield from`

Removing it from `greet(name)` in `greet_logged()`:

```python
def greet_logged(
    name: str,
) -> Depend[Need[Console] | Need[Log], None]:
    greet(name)  # Was: yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")
```

`ty check` reports nothing. `ruff check` reports nothing. The script
runs to completion and prints:

```text
['greeted Alice', 'greeted Bob']
```

The greetings are gone. `greet(name)` calls a generator function, so
it builds an Effect and returns it. Nothing then drives that Effect,
so its body never runs and never makes the `Need[Console]` request.
The log entries still appear because the deletion touched only the
greeting half of the function. That makes the failure quieter still:
the program looks like it worked and produced most of its output.

No tool objects because the code breaks no rule. Building a value and
discarding it is legal Python, and `greet(name)`'s value is a
generator like any other. The declared `Need[Console]` in the return
type still holds, since a declaration says what the function may
request, not what it must. Those two deleted words are the chapter's
own caveat about the limits of the guarantee.

Removing it from `need(Console)` in `greet()` draws two diagnostics:

```python
def greet(name: str) -> Depend[Need[Console], None]:
    console = need(Console)  # Was: yield from need(Console)
    console.print(f"Hello, {name}!")
```

```text
error[invalid-return-type]: Function always implicitly returns `None`,
which is not assignable to return type
`Generator[Need[Console], Any, None]`
 --> greeter.py:8:25
  |
8 | def greet(name: str) -> Depend[Need[Console], None]:
  |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^

error[unresolved-attribute]: Object of type
`Generator[Need[Console], Any, Console]` has no attribute `print`
  --> greeter.py:10:5
   |
10 |     console.print(f"Hello, {name}!")
   |     ^^^^^^^^^^^^^
```

The `invalid-return-type` error says the function stopped being a
generator. Removing the only `yield from` in the body leaves no
`yield` anywhere, so `greet()` is an ordinary function returning
`None`. `None` is not the `Generator` its annotation declares. The
`unresolved-attribute` error says the value in `console` is the wrong
kind of thing: a `Generator` rather than a `Console`, and generators
have no `print()`.

The difference between the two cases is whether anything later uses
the dropped value. Discarding `greet(name)` is invisible because
nothing afterward depends on it, and a discarded expression has no
type to contradict. Assigning `need(Console)` binds a generator to a
name the next line then uses as a `Console`, so the mistake reaches an
operation the type checker can evaluate. The lesson generalizes past
this library: a type checker verifies how a program uses its values,
so a value nobody uses is a value nobody checks.

## 8. A registry of Effects, and why `retry()` takes a function

```python
# exercise_8.py
from collections.abc import Callable
from functools import partial
from typing import Final
from stateless import (Depend, Need, Success, need,
                       run, supply)

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

NAMES: Final[list[str]] = ["Alice", "Bob"]

built: dict[str, Success[None]] = {
    name: supply(Console())(greet)(name) for name in NAMES
}
for effect in built.values():
    run(effect)
#: Hello, Alice!
#: Hello, Bob!
# The same objects, a second time
for effect in built.values():
    run(effect)

def make(name: str) -> Success[None]:
    return supply(Console())(greet)(name)

builders: dict[str, Callable[[], Success[None]]] = {
    name: partial(make, name) for name in NAMES
}
for builder in builders.values():
    run(builder())
#: Hello, Alice!
#: Hello, Bob!
# A fresh Effect each time
for builder in builders.values():
    run(builder())
#: Hello, Alice!
#: Hello, Bob!
```

The first pass over `built` greets both names. The second prints
nothing at all, and `run()` returns `None` for each entry without
raising an exception. An Effect is a generator, and a generator runs
once. Resuming a finished generator raises `StopIteration` immediately,
which `run()` reads as "already returned, with no value."
So a spent Effect looks exactly like one that succeeded and returned
`None`, and nothing reports the difference.

The dictionary of builders behaves as a reader expects. Each pass
calls each entry, each call builds a new generator, and each generator
runs its body once. The stored value went from a description `run()`
consumes once to a recipe a caller can follow as often as it likes.

That difference is the whole reason `retry()`'s type is
`Callable[P, Effect[...]] -> Callable[P, Effect[...]]` rather than
`Effect[...] -> Effect[...]`. Retrying means running the same work
more than once, and an Effect cannot supply the second run: by the
time the first attempt fails, that attempt has already run the
generator to its end, leaving nothing to resume. `retry()` needs to
build a fresh Effect per attempt, and only the function can do that.
So `retry()` decorates the function, calls it once per attempt, and
hands back a function of the same signature.

The same reasoning explains `repeat()` and `memoize()`. It also
explains why storing Effects in a registry, a queue, or a cache is a
mistake that looks fine until something runs an entry twice. Store the
function, and apply the arguments where you need the Effect.

## 9. Three reports, one Effect

```python
# exercise_9.py
import asyncio
from stateless import Async, Depend, run, run_async, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched {url}"

def report(url: str) -> Depend[Async, str]:
    body = yield from wait(fetch(url))
    return f"{body = }, {len(body) = }"

def report_all(urls: list[str]) -> Depend[Async, list[str]]:
    reports: list[str] = []
    for url in urls:
        reports.append((yield from report(url)))
    return reports

async def main() -> None:
    try:
        run(report_all(["a"]))
    except RuntimeError as e:
        print(e)
    for line in await run_async(
            report_all(["a", "b", "c"])):
        print(line)

asyncio.run(main())
#: asyncio.run() cannot be called from a running event loop
#: body = 'fetched a', len(body) = 9
#: body = 'fetched b', len(body) = 9
#: body = 'fetched c', len(body) = 9
```

The annotation is `Depend[Async, list[str]]`. `report()` needs `Async`,
and `yield from` passes that requirement straight up, so `report_all()`
needs it too. Three delegations to the same Effect type add nothing
new to the channel: `Need[Console] | Need[Log]` grows because the two
requirements differ, and here they do not. Only the return type
changes, from one `str` to a `list[str]`, since `report_all()`
collects the results rather than relaying them.

`run()` raised a `RuntimeError`, and `await run_async(...)` worked.
`run(effect)` is `asyncio.run(run_async(effect))`. `asyncio.run()`
refuses to start an event loop inside a running one, so calling
`run()` from `main()` fails. `run_async()` is the same driver in
coroutine form, so the loop already running can await it.

`ty` accepted both because both are correctly typed. `run()` takes an
Effect and returns its result. `run_async()` takes an Effect and returns
an awaitable of its result. `report_all(["a"])` satisfies either
signature, and nothing in the type system records that this call site
sits inside a coroutine. Whether an event loop is running is a fact
about the moment of the call, not about the types involved, so calling
`run()` inside a coroutine is one of the few mistakes in the chapter a
type checker cannot catch. The rule is positional rather than
type-based: `run()` at the outermost edge of a synchronous program,
`run_async()` anywhere inside an asynchronous one.

## 10. A second failure in the channel

```python
# exercise_10.py
from typing import Final
from stateless import (Effect, Need, need, run, supply,
                       throws)

class Console:
    def print(self, message: str) -> None:
        print(message)

SCORES: Final[dict[str, int]] = {
    "Alice": 42, "Bob": 7, "Cyd": -3}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name]

@throws(ValueError)
def format_score(name: str, value: int) -> str:
    if value < 0:
        raise ValueError(
            f"negative score for {name}: {value}")
    return f"{name}: {value}"

def announce(
    name: str,
) -> Effect[Need[Console], KeyError | ValueError, None]:
    value: int = yield from score(name)
    line: str = yield from format_score(name, value)
    console = yield from need(Console)
    console.print(line)

bound = supply(Console())(announce)
for who in ("Alice", "Cyd", "Dana"):
    try:
        run(bound(who))
    except (KeyError, ValueError) as e:
        print(f"{type(e).__name__}: {e}")
#: Alice: 42
#: ValueError: negative score for Cyd: -3
#: KeyError: 'Dana'
```

`@throws(ValueError)` turns `format_score()` from a function that
raises an exception into an Effect that declares one, so its failure
travels as a value in the yield channel instead of unwinding the stack.
Following `ty` until the program builds means two edits: widening
`announce()`'s error parameter from `KeyError` to
`KeyError | ValueError`, and annotating `line: str`. `value: int`
carries an annotation for the same reason: `yield from` on a
`@throws` function produces the declared success type, and naming
that type keeps the type checker's inference pinned.

Each failure surfaced at `run()`, and nowhere earlier. `Cyd` has a
score, so the lookup succeeds and `format_score()` fails. `Dana` has
none, so the lookup fails and `format_score()` never runs. In both
cases the error value travels up through the `yield from` chain
untouched, past `announce()`, past `supply()`, to the driver. `run()`
raises it as an ordinary exception because nothing along the way
caught it. Declaring a failure is not handling it. The declaration
says the failure can arrive, and `catch()` turns it into a value the
program deals with.

Deleting `ValueError` from the annotation gives:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> exercise_10.py:28:28
   |
26 | ) -> Effect[Need[Console], KeyError, None]:
   |      ------------------------------------- Function annotated with
   |      yield type `Need[Console] | KeyError` here
27 |     value: int = yield from score(name)
28 |     line: str = yield from format_score(name, value)
   |                            ^^^^^^^^^^^^^^^^^^^^^^^^^
   |                            expression of type `ValueError`,
   |                            expected `Need[Console] | KeyError`
```

The error appears on line 28, the `yield from` that would introduce the
undeclared failure, not on the signature and not at the call site. That
is the useful place for it. The diagnostic names both the failure that
escaped and the delegation it escaped through, so the fix is either to
declare it or to catch it, right there.

## 11. Making the ambiguity a type error

Three implementations have six orderings, and the prediction is short.
`supply()` scans its arguments and takes the first that satisfies the
request, so whichever implementation comes first answers it. Two of
the six orderings put `Terminal` first and send the greeting to the
screen, and the remaining four split evenly between the two recorders.
No ordering produces an error, and no ordering produces a warning.

The fix is to stop letting one structural check match three objects:

```python
# exercise_11.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Screen(Protocol):
    def print(self, message: str) -> None: ...

@runtime_checkable
class Recorder(Protocol):
    def record(self, message: str) -> None: ...

@dataclass
class Terminal:
    def print(self, message: str) -> None:
        print(message)

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)
    def record(self, message: str) -> None:
        self.messages.append(message)

def to_screen(name: str) -> Depend[Need[Screen], None]:
    device = yield from need(Screen)
    device.print(f"Hello, {name}!")

def to_log(name: str) -> Depend[Need[Recorder], None]:
    device = yield from need(Recorder)
    device.record(f"Hello, {name}!")

capture = Capture()
run(supply(as_type(Screen)(Terminal()))(to_screen)("Alice"))
#: Hello, Alice!
run(supply(as_type(Recorder)(capture))(to_log)("Bob"))
print(capture.messages)
#: ['Hello, Bob!']
```

Renaming `Capture.print()` to `record()` is the whole change. The two
`Protocol`s no longer overlap, so no object satisfies both, and each
Effect names the one it needs.

That change buys a diagnostic where a coin flip used to be. Add one
more line to the end of the listing, handing `to_log` the object that
prints instead of the one that records, and `ty` rejects it before the
program runs:

```text
error[invalid-argument-type]: Argument is incorrect
  --> exercise_11.py:40:30
   |
40 | run(supply(as_type(Recorder)(Terminal()))(to_log)("Carol"))
   |                              ^^^^^^^^^^ Expected `Recorder`, found `Terminal`
info: type `Terminal` is not assignable to protocol `Recorder`
info: └── protocol member `record` is not defined on type `Terminal`
```

The second `info` line is the part worth reading. The type checker
names the missing method rather than the missing type, and that is
what structural typing means: `Terminal` fails not because of what it
is but because of what it does not do.

One honest limit. Distinct method names remove the ambiguity *between*
abilities. They do nothing about two implementations of the *same*
ability. Add a second recorder, an `Audit` that also defines
`record()`, and `supply(capture, audit)` is ambiguous again by argument
order, with no diagnostic.
[When Two Implementations Match](../Chapters/46_Effects--Stateless.md#when-two-implementations-match)
gives its advice in two halves for that reason. No type can enforce
the second half, "supply one implementation per Ability." Stateless
resolves a request by scanning its arguments at runtime, so a
duplicate is a fact about the call rather than about the types. ZIO's
compile-time rejection of exactly this case is the difference that
section names.
