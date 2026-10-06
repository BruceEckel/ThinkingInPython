# Stateless: Solutions

Each listing below is self-contained, redeclaring the `Console` and
`greet()` it needs instead of importing the chapter's, so a solution
keeps working when a chapter listing changes.

## 1. A `Console` that reads as well as prints

> Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
> an Effect that asks for a name and greets the result.
> Supply a scripted `Console` in a test and a real one in a demo,
> and confirm `ask_and_greet()` stays unchanged between them.

<details>
<summary>Where to look</summary>

[Supplying an Interface](../../Chapters/46_Effects--Stateless.md#supplying-an-interface) shows a `Protocol` standing in for a base class, and `need(Console)` hands back whatever object the supplier gave.
Add `read()` to the protocol, then write `ask_and_greet()` as a generator that gets the `Console` with `need()` and calls `read()` and `print()` on it.
A scripted class that returns a canned answer goes to `supply()` in the test, and a class wrapping `input()` goes to it in the demo.

<details>
<summary>Solution</summary>

If you pass `scripted` to `supply()` without `as_type(Console)`,
the demo still prints `['Hello, Bob!']`,
but `ty` reports an `invalid-argument-type` at each `run()` call.
The Effect reaching `run()` still carries the `Need[Console]` that `ask_and_greet()` requests,
so the solution wraps each supplied object in `as_type(Console)`.

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

Supplying a real `Console` is the same call with `Terminal()` in place of
`Scripted(...)`, and the session reads:

```text
What is your name? Alice
Hello, Alice!
```

The demo in `test_ch46_ask_and_greet.py` uses `Scripted` rather than
`Terminal` for the reason any book listing does: a call to `input()`
has no terminal from which to read. The substitution is the point
either way, and neither binding requires a change to
`ask_and_greet()`, which is character-for-character the same function
under both.

**Request a capability, not a class.** No binding could have required a change. `ask_and_greet()` names a capability
in its return type and calls two methods on whatever answers.
`Terminal`, `Scripted`, and any third implementation are
interchangeable because none of them appears in the Effect. Adding
`read()` to the protocol changed which classes qualify, and `supply()`
still picks among them the same way.

**Supply under the protocol's type.** `as_type(Console)` does quiet work in both calls, and the work is
static. `supply()` reads the Ability from the declared type of its
argument, so `supply(scripted)` alone builds a handler for
`Need[Scripted]` rather than the `Need[Console]` that
`ask_and_greet()` requests. The wrapper turns that static type into
`Console`. At runtime the wrapper returns `scripted` untouched, and
`supply()` still finds it, because `Console` is `@runtime_checkable`
and `isinstance()` matches `Scripted` on shape.

</details>
</details>

## 2. An undeclared need, declared

> Take `undeclared_need.py`, remove the `# type: ignore`,
> and run `ty check` on it.
> Fix the error by changing only the annotation,
> then check what `greet_all()`'s callers must now declare.

<details>
<summary>Where to look</summary>

[Effects Propagate, and the Type Checker Verifies It](../../Chapters/46_Effects--Stateless.md#effects-propagate-and-the-type-checker-verifies-it) shows what `ty` says when a function's annotation hides a request that `greet()` makes.
Read the error's yield type, then change the return annotation of `greet_all()` so it names the request that comes up through `yield from`.
Whoever calls `greet_all()` inherits that request, so look at what its callers declare next.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from stateless import Depend, Need, need, run, supply

class Console:
    def print(self, message: str) -> None:
        ...

def greet(name: str) -> Depend[Need[Console], None]:
    ...

def greet_all(names: list[str]) -> Depend[
    Need[Console], None
]:
    ...
```

<details>
<summary>Solution</summary>

If you fix the annotation but keep a caller that runs `greet_all()` with no environment,
as `run(greet_all(["Alice", "Bob"]))` does,
`ty` reports an `invalid-argument-type` at that `run()` call.
The run raises a `MissingAbilityError` before the first greeting prints.
The new annotation hands the requirement to every caller,
so the solution wraps `greet_all` in `supply(Console())` before calling `run()`.

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

**Fix the signature, not the body.** The body stays as it is.
`greet_all()` did the right thing all along. Its signature described a
different function.

What `greet_all()`'s callers must now declare is the point of the exercise. Before,
`greet_all()` claimed to need nothing, so a caller could run it with no
environment: `run(greet_all(names))`. Now every caller has two
options, the same two `greet()`'s callers have. Supply a `Console`,
ending the requirement, or declare `Need[Console]` in its own return
type and pass the requirement further up. No third option exists,
which makes the dependency visible. The requirement appears in
the signature of every function between the one that uses the `Console`
and the one that supplies it, and the type checker refuses to let any of them
stay silent.

</details>
</details>
</details>

## 3. Catching an error that is already handled

> Apply `reveal_type()` to `catch(ValueError)(one_unhandled)` and run `ty check`.
> Explain why its result type differs from `all_handled()`'s,
> given that both have handled every error `read_score()` declares.

<details>
<summary>Where to look</summary>

[Turning an Error Into a Value](../../Chapters/46_Effects--Stateless.md#turning-an-error-into-a-value) shows `catch()` moving a declared error out of the failure channel.
Compare the two result types and ask what remains in each return type after `catch()` has run.
Then look at what a `match` over the caught value does to that type, and which function in the pair contains one that covers every case.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import Final, assert_never, reveal_type
from stateless import Success, Try, catch, throws

RAW: Final[dict[str, str]] = {"Alice": "42", "Bob": "seven"}

@throws(KeyError, ValueError)
def read_score(name: str) -> int:
    ...

def all_handled(name: str) -> Success[str]:
    ...

def one_unhandled(name: str) -> Try[ValueError, str]:
    ...
```

<details>
<summary>Solution</summary>

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
`Generator[Never, Any, str]`. The revealed type and `all_handled()`'s type both
carry `Never` in the yield channel, so both agree that nothing can
fail from here on. They differ in the return channel: `str` for
`all_handled()`, `str | ValueError` for the wrapped `one_unhandled()`.

**Consume every caught error.** The difference is where the error stops travelling. `all_handled()`
catches both errors, then consumes both in its `match`, turning each
into a sentence and returning a `str`. No error remains, and the
`assert_never()` proves it. The `match` covers every case inside the
function.

**Pass the remaining error up.** `one_unhandled()` catches the
`KeyError` and consumes that one.
The `ValueError` stays declared, as `Try[ValueError, str]` says, so it
is still in the yield channel when `catch(ValueError)` wraps
`one_unhandled()`. `catch()` does not delete an error. It moves the error
from the yield channel to the return channel, as a value. So the
`ValueError` leaves the failure channel and reappears beside the
`str`, and a caller needing a bare `str` has one case left to handle.

Both functions have handled every error `read_score()` declares. Only
`all_handled()` has *interpreted* what it caught. `catch()` turns a
failure into a value, and a `match` turns that value into a result.
Skipping the `match` leaves the caught error sitting in the return
type.

</details>
</details>
</details>

## 4. A `Log` protocol, and a test that records both

> Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
> then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.

<details>
<summary>Where to look</summary>

[Retrofitting an Effect](../../Chapters/46_Effects--Stateless.md#retrofitting-an-effect) builds `Log` as an Ability alongside `Console`, and [Supplying an Interface](../../Chapters/46_Effects--Stateless.md#supplying-an-interface) shows how a `Protocol` replaces a concrete class.
Declare `Log` with a `write()` method, and write a recording class for each protocol.
Pass both instances to `supply()` in one call, run the Effect, and assert on each recorder's list.

<details>
<summary>Solution</summary>

If you declare `Log` as a `Protocol` without `@runtime_checkable`,
`ty` passes the listing,
but the run raises a `TypeError` at the first request for a `Log`.
`supply()` matches each request with `isinstance()`,
and `isinstance()` raises a `TypeError` on a `Protocol` without that decorator.
The solution puts the decorator on both protocols, as `console_protocol.py` does on `Console`.

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

**Fill both roles with one object.** One object satisfies both
protocols. The concrete-class version could not arrange that. `Log` is
a `dataclass` holding its own entries, so a test must construct one and
read `log.entries` afterward. As a
`Protocol`, `Log` is a shape, and a single `Recorder` can have that
shape and the `Console` shape at once.

**Supply one object under two types.** The two `as_type()` calls make one object answerable to two
requests. `supply()` reads the Ability from each argument's declared
type, so `supply(recorder, recorder)` builds a handler for
`Need[Recorder]`, an Ability neither Effect requests. Each wrapper
names the role this instance fills. Supplying the same object twice
under two different types is the case for which `as_type()` exists.

**Check the greeting and the log together.** Writing both assertions in one test is the payoff. A test holding the
whole environment can check that the greeting reached the console
*and* that the log recorded it, in one function, with no capture of
stdout and no temporary file. Both Effects are requests before they
are actions, so the test decides what performing them means.

</details>
</details>

## 5. A third material in the table

> Add a `Metal` material to `test_nailer.py` with a strength that survives the robotic nailer,
> and add its two rows to the table.
> Then explain why the test function body needs no change.

<details>
<summary>Where to look</summary>

[One Effect, Many Environments](../../Chapters/46_Effects--Stateless.md#one-effect-many-environments) shows `parametrize` running `holds()` against a table of materials and nailers.
Define a `Metal` value whose strength exceeds the robotic nailer's force, and add one row for each nailer.
Consider what `holds()` asks for by type, and whether a new instance of that type changes the request.

<details>
<summary>Solution</summary>

If you give `METAL` a strength of `11` or less, the
`(METAL, ROBOTIC, True)` row fails with `assert False is True`.
`holds()` compares with a strict `<`, so a material survives a nailer
when its strength exceeds the force, not when it matches it. The
solution picks `20`, which clears both forces with room to spare.

```python
# test_ch46_nailer.py
from typing import Final
import pytest
from record import record
from stateless import Depend, Need, need, run, supply

@record
class Material:
    strength: int

@record
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

**Pick a strength above both forces.** `METAL` at strength `20` outlasts the robotic nailer's force of `11`,
so its two rows read `True` and `True`. `METAL` is the first material
in the table that survives both nailers.

**Build each environment from a row.** The test function body needs no change because it mentions no
material or nailer. It receives two objects and an expectation,
builds an environment from them with `supply()`, and asks whether the
answer matches. The `parametrize` table decides which two objects
those are, and adding a row adds a case without touching the function body that
runs it.

That split between the table and the body is the same one running through the whole chapter, seen
from the testing side. `holds()` declares two requirements and names
no instance, so every combination of instances is a valid
environment for it. The parametrize table is a list of environments,
and the test body is the driver that runs the Effect in each one. Six
rows share one assertion. A version constructing its own `Material`
inside `holds()` needs three copies of the function, one per material,
and a version that also constructs its own `Nailer` needs all six.

</details>
</details>

## 6. A handler that builds what the request names

> This one looks ahead to `handle()`,
> which [Abilities Are Not Special](../../Chapters/47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
> covers.
> `default_console.py` defaults by supplying an instance.
> Write the other kind of default, one that builds whatever the request names.
> `handle()` reads its handler's parameter annotation to decide what it answers,
> so a function annotated `Need[Console]` and returning `ability.t()` hands back a default-constructed instance of the requested class.
> Run it against `greeter.py`'s `greet()`,
> whose `Console` constructs with no arguments,
> and confirm the greeting prints.
> Then declare a second Ability and request that one too,
> and report which requests your handler answered at runtime and which ones the type checker believes it answered.
> Account for the difference,
> using `handle()`'s `t = get_origin(t) or t` as the evidence.

<details>
<summary>Where to look</summary>

[Layering Handlers](../../Chapters/46_Effects--Stateless.md#layering-handlers) shows a default supplied under a more specific handler, and [Abilities Are Not Special](../../Chapters/47_Effects--Stateless_in_Practice.md#abilities-are-not-special) covers `handle()`.
Write a handler function that takes a `Need[Console]` parameter and returns a new instance of the class the request carries in `ability.t`.
Wrap it with `handle()`, then compare what runs against what the annotation tells the type checker.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from stateless import Depend, Need, handle, need, run

class Console:
    def print(self, message: str) -> None:
        ...

class Clock:
    def now(self) -> str:
        ...

def greet(name: str) -> Depend[Need[Console], None]:
    ...

def stamped(
    name: str,
) -> Depend[Need[Console] | Need[Clock], None]:
    ...

def default(ability: Need[Console]) -> Console:
    ...
```

<details>
<summary>Solution</summary>

If you return `Console()` in place of `ability.t()`, `greet()` still
prints its greeting, but `stamped()` fails with
`AttributeError: 'Console' object has no attribute 'now'`.
The handler answers the
`Clock` request too, as it answers every `Need`, and hands it a
`Console`, while the type checker reports nothing, since `default()`
declares that it returns a `Console`. The solution calls `ability.t()`,
which builds the class the request names, so the `Clock` request
receives a `Clock`.

```python
# exercise_6.py
from stateless import Depend, Need, handle, need, run

class Console:
    def print(self, message: str) -> None:
        print(message)

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

**Build the class the request names.** `default()` names no `Console` in its body. It reads `ability.t`,
the class the request carries, and calls that class, so `default()`
answers a request by constructing the requested class. That is the
other kind of default. `default_console.py` supplies one prepared
instance, and `default()` builds whatever the request names, on demand.

**Run both Effects through one handler.** At runtime the handler
answered three requests across the two calls, two for `Console` and one
for `Clock`, although `default()` annotates its parameter
`Need[Console]`. The type checker believes the handler answers
`Need[Console]` and leaves `Need[Clock]` open, so the second `run()`
needs a `# type: ignore`. Without that pragma, the type checker reports
a leftover `Need[Clock]`.

`handle()`'s `t = get_origin(t) or t` is the evidence. `handle()`
reads the annotation, reduces `Need[Console]` to its origin, `Need`,
and installs the runtime check `isinstance(ability, Need)`. That check
ignores the type argument, so every `Need[...]` request matches. The
type checker reads the same annotation without that reduction,
subtracts `Need[Console]` from the requirements, and leaves
`Need[Clock]` in place.

Neither view is wrong about what it describes. `isinstance()` cannot
test a type argument. `Need[Clock]` and `Need[Console]` are the same
runtime class, so no runtime check tells the two apart. The annotation
is the only place the distinction exists, and `handle()` uses the annotation
for matching but cannot enforce the distinction. A handler like
`default()` genuinely handles more than its type says, and one that
assumes `ability.t` is a `Console` receives a `Clock` with
nothing to stop it.

</details>
</details>
</details>

## 7. Two ways to drop a `yield from`

> Break `audit_log.py` by removing the `yield from` in front of `greet(name)` in `greet_logged()`.
> Run `ty check`, `ruff check`, and the script,
> and record what each reports and what the program prints.
> Explain where the greetings went and why no tool objects.
> Then restore it, and instead remove the `yield from` in front of `need(Console)` in `greeter.py`'s `greet()`.
> This time `ty` produces two diagnostics.
> Explain what each one catches,
> and why the type checker catches assigning a dropped request but not discarding one.

<details>
<summary>Where to look</summary>

[Nothing Runs Yet](../../Chapters/46_Effects--Stateless.md#nothing-runs-yet) shows that calling a generator function builds an Effect without running its body, and [Why `yield from`](../../Chapters/46_Effects--Stateless.md#why-yield-from) explains what the keyword does.
Ask whether a discarded generator breaks any rule `ty` or `ruff` checks.
For the second case, read both diagnostics and ask what the function has become once it loses its only `yield from`, and whether the next line uses the dropped value.

<details>
<summary>Solution</summary>

Removing the `yield from` in front of `greet(name)` in `greet_logged()`:

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

No greeting prints. `greet(name)` calls a generator function, so
it builds an Effect and returns it. Nothing then drives that Effect,
so its body does not run and makes no `Need[Console]` request.
The log entries still appear because the deletion touches only the
greeting half of the function. The surviving entries make the failure
quieter still. The program looks like it worked and produced most of
its output.

No tool objects because the code breaks no rule. Building a value and
discarding it is legal Python, and `greet(name)`'s value is a
generator like any other. The declared `Need[Console]` in the return
type still holds, since a declaration says what the function may
request, not what it must. Those two deleted words are the chapter's
own caveat about the limits of the guarantee.

Removing the `yield from` in front of `need(Console)` in `greet()` draws two diagnostics:

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
this library. A type checker verifies how a program uses its values,
so a value nobody uses is a value nobody checks.

</details>
</details>

## 8. A registry of Effects, and why `retry()` takes a function

> Build a registry of Effects:
> a `dict[str, Success[None]]` that maps each of two names to `supply(Console())(greet)(name)`.
> Run every entry, then run every entry a second time,
> and record what prints on each pass.
> Change the values to functions that build the Effect when called,
> and run both passes again.
> Explain which of the two shapes `retry()` requires,
> and why it takes a schedule and returns a decorator of type `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`,
> rather than being an operation on an Effect.

<details>
<summary>Where to look</summary>

[An Effect Runs Once](../../Chapters/46_Effects--Stateless.md#an-effect-runs-once) shows a spent Effect returning `None` when you run it again.
Store the Effects in one dictionary and functions that build them in another, then run each twice.
`retry()` starts the work over after a failure, so consider what it needs to call each time.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Callable
from functools import partial
from typing import Final
from stateless import (Depend, Need, Success, need,
                       run, supply)

class Console:
    def print(self, message: str) -> None:
        ...

def greet(name: str) -> Depend[Need[Console], None]:
    ...

NAMES: Final[list[str]] = ["Alice", "Bob"]

def make(name: str) -> Success[None]:
    ...
```

<details>
<summary>Solution</summary>

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

**Run each stored Effect twice.** The first pass over `built` greets both names. The second prints
nothing, and `run()` returns `None` for each entry without
raising an exception. An Effect is a generator, and a generator runs
once. Resuming a finished generator raises `StopIteration` immediately,
which `run()` reads as "already returned, with no value."
So a spent Effect looks the same as one that succeeded and returned
`None`, and nothing reports the difference.

**Build a fresh Effect per run.** The dictionary of builders behaves as a reader expects. Each pass
calls each entry, each call builds a new generator, and each generator
runs its body once. The stored value goes from a description `run()`
consumes once to a recipe a caller can follow as often as it likes.

That difference is why `retry()` takes a schedule and returns a
decorator of type
`Callable[P, Effect[...]] -> Callable[P, Effect[...]]` rather than
one of type `Effect[...] -> Effect[...]`. Retrying means running the
same work more than once, and an Effect cannot supply the second run.
By the time the first attempt fails, that attempt has run the
generator to its end, leaving nothing to resume. `retry()` needs to
build a fresh Effect per attempt, and only the function that builds
the Effect can do that.
So `retry()` decorates the function, calls it once per attempt, and
hands back a function that takes the same arguments.

The Effect the returned function builds has a wider type. `retry()`
adds the clock on which it sleeps and replaces the error with a
`RetryError`.

The same reasoning explains `repeat()` and `memoize()`. It also
explains why storing Effects in a registry, a queue, or a cache is a
mistake that looks fine until something runs an entry twice. Store the
function, and apply the arguments where you need the Effect.

</details>
</details>
</details>

## 9. Three reports, one Effect

> Write `report_all()`,
> which calls `stateless_coroutine.py`'s `report()` for three URLs with `yield from` and returns the three results.
> Importing that module runs its own unguarded `print(run(...))`,
> so expect one line of its output before yours.
> Work out what its annotation must be, and confirm it with the type checker.
> Then call it from inside an `async def`,
> once with `run()` and once with `await run_async()`,
> and record what each one does.
> Explain why the type checker accepts both.

<details>
<summary>Where to look</summary>

[Waiting on a Coroutine](../../Chapters/46_Effects--Stateless.md#waiting-on-a-coroutine) shows `wait()` putting an `Async` request into an Effect, and [Where to Call `run()`](../../Chapters/46_Effects--Stateless.md#where-to-call-run) covers running one from inside an event loop.
Loop over the URLs, delegate to `report()` with `yield from`, and collect the results in a list.
The annotation carries the `Async` request, and the two runners differ in whether they start their own event loop.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
import asyncio
from exceptions import expect
from stateless import Async, Depend, run, run_async, wait

async def fetch(url: str) -> str:
    ...

def report(url: str) -> Depend[Async, str]:
    ...

def report_all(urls: list[str]) -> Depend[Async, list[str]]:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_9.py
import asyncio
from exceptions import expect
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
    expect(RuntimeError, run, report_all(["a"]))
    for line in await run_async(
            report_all(["a", "b", "c"])):
        print(line)

asyncio.run(main())
#: [RuntimeError] asyncio.run() cannot be called from a
#: running event loop
#: body = 'fetched a', len(body) = 9
#: body = 'fetched b', len(body) = 9
#: body = 'fetched c', len(body) = 9
```

**Relay the request, collect the results.** The annotation is `Depend[Async, list[str]]`. `report()` needs `Async`,
and `yield from` passes that requirement straight up, so `report_all()`
needs it too. Three delegations to the same Effect type add nothing
new to the channel. `Need[Console] | Need[Log]` grows because the two
requirements differ, and here they do not. Only the return type
changes, from one `str` to a `list[str]`, since `report_all()`
collects the results rather than relaying them.

**Drive the Effect from a coroutine.** `run()` raises a `RuntimeError`, and `await run_async(...)` works.
`run(effect)` is `asyncio.run(run_async(effect))`. `asyncio.run()`
refuses to start an event loop inside a running one, so calling
`run()` from `main()` fails. `run_async()` is the same driver in
coroutine form, so the running loop can await it.

The type checker accepts both calls because both are correctly typed. `run()` takes an
Effect and returns its result. `run_async()` takes an Effect and returns
an awaitable of its result. `report_all(["a"])` satisfies either
signature, and nothing in the type system records that this call site
sits inside a coroutine. Whether an event loop is running is a fact
about the moment of the call, not about the types involved, so calling
`run()` inside a coroutine is a mistake the type checker cannot
report. The rule is positional rather than
type-based: `run()` at the outermost edge of a synchronous program,
`run_async()` anywhere inside an asynchronous one.

</details>
</details>
</details>

## 10. A second failure in the channel

> `announce()` declares `Effect[Need[Console], KeyError, None]`.
> Give it a second failure:
> a helper that formats the score and raises a `ValueError` on a negative one,
> lifted with `@throws(ValueError)`.
> Follow the type checker until the program builds,
> add a negative score to `scores.py`'s `SCORES` so the new failure can occur,
> then run it on a name that produces each failure and on one that succeeds,
> and say where each failure surfaced.
> Then delete `ValueError` from `announce()`'s annotation and record what the type checker reports and at which line.

<details>
<summary>Where to look</summary>

[Multiple Errors](../../Chapters/46_Effects--Stateless.md#multiple-errors) shows an Effect declaring more than one failure, and [The Error Channel](../../Chapters/46_Effects--Stateless.md#the-error-channel) covers `@throws`.
Lift the helper with `@throws(ValueError)`, then widen `announce()`'s failure type to a union and call the helper with `yield from`.
Run the three names and note whether each failure comes out of `run()` as an exception.
Deleting `ValueError` from the annotation makes the type checker flag the `yield from` of the helper.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from typing import Final
from exceptions import expected
from stateless import (Effect, Need, need, run, supply,
                       throws)

class Console:
    def print(self, message: str) -> None:
        ...

SCORES: Final[dict[str, int]] = {
    "Alice": 42, "Bob": 7, "Cyd": -3}

@throws(KeyError)
def score(name: str) -> int:
    ...

@throws(ValueError)
def format_score(name: str, value: int) -> str:
    ...

def announce(
    name: str,
) -> Effect[Need[Console], KeyError | ValueError, None]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_10.py
from typing import Final
from exceptions import expected
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
    with expected((KeyError, ValueError)):
        run(bound(who))
#: Alice: 42
#: [ValueError] negative score for Cyd: -3
#: [KeyError] 'Dana'
```

**Lift the helper into an Effect.** `@throws(ValueError)` turns `format_score()` from a function that
raises an exception into an Effect that declares one, so its failure
travels as a value in the yield channel instead of unwinding the stack.

**Declare the second failure.** Following the type checker until the program builds means one edit: widening
`announce()`'s error parameter from `KeyError` to
`KeyError | ValueError`. `line: str` and `value: int` carry
annotations by choice, not by demand. `yield from` on a `@throws`
function produces the declared success type, and naming that type
keeps the type checker's inference pinned.

**Surface each failure at `run()`.** Each failure surfaces at `run()`, and nowhere earlier. `Cyd` has a
score, so the lookup succeeds and `format_score()` fails. `Dana` has
none, so the lookup fails and `format_score()` does not run. In both
cases the error value travels up through the `yield from` chain
untouched, past `announce()`, past `supply()`, to the driver. `run()`
raises it as an ordinary exception because nothing along the way
catches it. Declaring a failure is not handling it. The declaration
says the failure can arrive, and `catch()` turns it into a value the
program handles.

Deleting `ValueError` from the annotation gives:

```text
error[invalid-yield]: Yield expression type does not match annotation
  --> exercise_10.py:29:28
   |
27 | ) -> Effect[Need[Console], KeyError, None]:
   |      ------------------------------------- Function annotated with
   |      yield type `Need[Console] | KeyError` here
28 |     value: int = yield from score(name)
29 |     line: str = yield from format_score(name, value)
   |                            ^^^^^^^^^^^^^^^^^^^^^^^^^
   |                            expression of type `ValueError`,
   |                            expected `Need[Console] | KeyError`
```

The error appears on line 29, the `yield from` that introduces the
undeclared failure, not on the signature and not at the call site.
That statement is the useful place for the diagnostic. The diagnostic
names both the failure that escaped and the delegation through which
it escaped, so the fix is either to declare the failure or to catch
it, right there.

</details>
</details>
</details>

## 11. Making the ambiguity a type error

> `ambiguous_supply.py` picks its `Console` by argument order.
> Add a third implementation and predict, before running it,
> which of the six orderings send Alice's greeting where.
> Then follow the advice in [When Two Implementations Match](../../Chapters/46_Effects--Stateless.md#when-two-implementations-match):
> give the recording implementation a method name the screen one does not have,
> declare each as its own `Protocol`,
> and show that handing the wrong implementation to an Effect is now a type error rather than a silent choice.
> Two implementations sharing one method name stay ambiguous under both `Protocol`s,
> so say what the technique does and does not prevent.

<details>
<summary>Where to look</summary>

[When Two Implementations Match](../../Chapters/46_Effects--Stateless.md#when-two-implementations-match) explains why `supply()` takes the first argument that satisfies the request.
Predict from argument order, since the first match wins.
If you give each implementation its own `Protocol` with a differently named method, the type checker rejects an implementation that lacks the method the Effect requests.
Then check whether the type checker can tell two classes apart when they share one method name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_11.py
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
        ...

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)
    def record(self, message: str) -> None:
        ...

def to_screen(name: str) -> Depend[Need[Screen], None]:
    ...

def to_log(name: str) -> Depend[Need[Recorder], None]:
    ...
```

<details>
<summary>Solution</summary>

If you keep `print()` on both implementations and declare it in both
`Protocol`s, each implementation satisfies both, and the type checker
accepts `as_type(Recorder)(Terminal())`. Handing that object to `to_log`
prints `Hello, Carol!` to the screen while `capture.messages` stays
`['Hello, Bob!']`, with no diagnostic. Two `Protocol`s that share one
method name describe one shape under two names, so the solution renames
the recording method to `record()`, and `Terminal` no longer fits
`Recorder`.

Three implementations have six orderings, and the prediction is short.
`supply()` scans its arguments and takes the first that satisfies the
request, so whichever implementation comes first answers it. Two of
the six orderings put `Terminal` first and send the greeting to the
screen, and the remaining four split evenly between `Capture` and the
third implementation.
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

**Give each role its own protocol.** The fix renames `Capture.print()` to `record()`, gives each method its
own `Protocol`, `Screen` and `Recorder`, and splits `greet()` into one
Effect per `Protocol`. The two `Protocol`s no longer overlap, so
neither implementation satisfies both, and each Effect names the
`Protocol` it needs.

That change turns the coin flip into a diagnostic. If you add one
more line to the end of the listing, handing `to_log` the object that
prints instead of the one that records, `ty` rejects it before the
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

In the second `info` line, the type checker names the missing
method rather than the missing type, and that is
what structural typing means: `Terminal` fails not because of what it
is but because of what it does not do.

One limit remains. Distinct method names remove the ambiguity *between*
abilities. They do nothing about two implementations of the *same*
ability. If you add a second recorder, an `Audit` that also defines
`record()`, `supply(capture, audit)` is ambiguous again by argument
order, with no diagnostic.
[When Two Implementations Match](../../Chapters/46_Effects--Stateless.md#when-two-implementations-match)
gives its advice in two halves for that reason. No type can enforce
the second half, "supply one implementation per Ability." Stateless
resolves a request by scanning its arguments at runtime, so a
duplicate is a fact about the call rather than about the types. ZIO's
compile-time rejection of this case is the difference that section
names.

</details>
</details>
</details>
