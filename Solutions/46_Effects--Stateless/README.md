# Stateless: Solutions

Each listing below is self-contained.
It redeclares the `Console` and `greet()` it needs instead of importing them from the chapter,
so a solution keeps working when a chapter listing changes.

## 1. A `Console` that reads as well as prints

> Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
> an Effect that asks for a name and greets the result.
> Supply a scripted `Console` in a test and a real one in a demo,
> and confirm `ask_and_greet()` stays unchanged between them.

<details>
<summary>Where to look</summary>

[Supplying an Interface](../../Chapters/46_Effects--Stateless.md#supplying-an-interface)
shows a `Protocol` standing in for a base class,
and `need(Console)` hands back the object the supplier gave.
Add `read()` to the protocol,
then write `ask_and_greet()` as a generator that gets the `Console` with `need()` and calls `read()` and `print()` on it.
In the test, pass `supply()` a scripted object that returns a canned answer,
and in the demo, an object wrapping `input()`.

<details>
<summary>Done when</summary>

`uv run pytest` passes your test,
which asserts that a scripted `Console` printed the greeting built from its canned answer,
and your demo greets the name it reads.
`uv run ty check` accepts both `run()` calls,
and `ask_and_greet()` is the same text in both.

<details>
<summary>Solution</summary>

The solution wraps each supplied object in `as_type(Console)`:

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

Supplying a real `Console` is the same call with `Terminal()` in place of `Scripted(...)`,
and the session reads:

```text
What is your name? Alice
Hello, Alice!
```

The demo in `test_ch46_ask_and_greet.py` uses `Scripted` rather than `Terminal` for the reason any book listing does:
a call to `input()` has no terminal from which to read.
`ask_and_greet()` stays character-for-character the same function under both bindings.

**Request an interface, not a class.**
`Terminal`, `Scripted`,
and any third implementation are interchangeable because none of them appears in the Effect.
Adding `read()` to the protocol changed which classes qualify.
`supply()` still picks among them the same way.

**Supply under the protocol's type.**
`supply()` reads the Ability from the declared type of its argument,
so `supply(scripted)` alone builds a handler for `Need[Scripted]` rather than the `Need[Console]` that `ask_and_greet()` requests.
In both calls, `as_type(Console)` changes the argument's static type from `Scripted` to `Console`.
At runtime the wrapper returns the same `scripted` object.
`supply()` still finds it,
because `Console` is `@runtime_checkable` and `isinstance()` matches `Scripted` on shape.

If you pass `scripted` to `supply()` without `as_type(Console)`,
the demo still prints `['Hello, Bob!']`,
but `ty` reports an `invalid-argument-type` at each `run()` call.
`supply(scripted)` handles `Need[Scripted]`,
so the `Need[Console]` that `ask_and_greet()` requests stays in the type of the Effect passed to `run()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. An undeclared need, declared

> Take `undeclared_need.py`, remove the `# type: ignore`,
> and run `ty check` on it.
> Fix the error by changing only the annotation,
> then check what `greet_all()`'s callers must now declare.

<details>
<summary>Where to look</summary>

[Effects Propagate, and the Type Checker Verifies It](../../Chapters/46_Effects--Stateless.md#effects-propagate-and-the-type-checker-verifies-it)
shows what `ty` says when a function's annotation hides a request that `greet()` makes.
Read the error's yield type,
then change the return annotation of `greet_all()` so it names the request that `yield from` relays from `greet()`.
Whoever calls `greet_all()` inherits that request,
so look at what its callers declare next.

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
<summary>Done when</summary>

`uv run ty check` passes on your file with the `# type: ignore` gone and only the annotation of `greet_all()` changed,
and running it with a `Console` supplied prints `Hello, Alice!` and `Hello, Bob!`.
A caller that hands `greet_all()` to `run()` with no `Console` supplied draws an `invalid-argument-type`.

<details>
<summary>Solution</summary>

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

`Success[None]` is `Effect[Never, Never, None]`:
an Effect with empty Ability and error channels and a `None` result.
`Never` in the yield channel means the function may yield no value of any type,
so the `Need[Console]` that `yield from greet(name)` relays contradicts the annotation.

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

**Fix the signature, not the body.**
`greet_all()` did the right thing all along.
Its signature described a different function.

The new annotation changes what `greet_all()`'s callers must declare.
Before, `greet_all()` claimed to be pure,
so a caller could hand it to `run()` with no environment:
`run(greet_all(names))`.
Now every caller has two options, the same two `greet()`'s callers have.
A caller can supply a `Console`, which ends the requirement,
or declare `Need[Console]` in its own return type,
which puts the same choice to its callers.
Those two are the only options, so the dependency stays visible.
The requirement appears in the signature of every function between the one that uses the `Console` and the one that supplies it.
The type checker reports an error at any of those functions that leaves the requirement out.

If you fix the annotation but keep a caller that runs `greet_all()` with no environment,
as `run(greet_all(["Alice", "Bob"]))` does,
`ty` reports an `invalid-argument-type` at that `run()` call.
The run raises a `MissingAbilityError` before the first greeting prints.
The solution therefore wraps `greet_all()` in `supply(Console())` before calling `run()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Catching an error that is already handled

> Apply `reveal_type()` to `catch(ValueError)(one_unhandled)` and run `ty check`.
> Explain why its result type differs from `all_handled()`'s result type,
> given that both have handled every error `read_score()` declares.

<details>
<summary>Where to look</summary>

[Turning an Error Into a Value](../../Chapters/46_Effects--Stateless.md#turning-an-error-into-a-value)
shows `catch()` moving a declared error out of the error channel.
Compare the two result types and ask what remains in each return type after `catch()` has run.
Then look at what a `match` over the caught value does to that type,
and which function in the pair has a `match` that covers every error `read_score()` declares.

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
<summary>Done when</summary>

`ty check` reveals `(name: str) -> Generator[Never, Any, str | ValueError]` for `catch(ValueError)(one_unhandled)`,
and your explanation says which channel `catch()` moves the `ValueError` into and what in `all_handled()` leaves its return type a bare `str`.

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

`all_handled()` is `Success[str]`,
which expands to `Generator[Never, Any, str]`.
The revealed type and `all_handled()`'s type both carry `Never` in the yield channel,
so neither can yield a failure to its caller.
They differ in the return channel: `str` for `all_handled()`,
`str | ValueError` for the wrapped `one_unhandled()`.

**Consume every caught error.**
The difference is which function consumes each caught error.
The `match` in `all_handled()` covers every case, so no error remains,
and the `assert_never()` proves it.

**Pass the remaining error up.**
The `ValueError` in `one_unhandled()` stays declared,
as `Try[ValueError, str]` says,
so it is still in the yield channel when `catch(ValueError)` wraps `one_unhandled()`.
`catch()` does not delete an error.
It moves the error from the yield channel to the return channel, as a value.
So the `ValueError` leaves the error channel,
and the return type becomes `str | ValueError`.
A caller needing a bare `str` has one case left to handle.

Both functions have handled every error `read_score()` declares.
Only `all_handled()` has interpreted what it caught.
`catch()` turns a failure into a value,
and a `match` turns that value into a result.
Skipping the `match` leaves the caught error in the return type.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A `Log` protocol, and a test that records both

> Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
> then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.

<details>
<summary>Where to look</summary>

[Retrofitting an Effect](../../Chapters/46_Effects--Stateless.md#retrofitting-an-effect)
builds `Log` as an Ability alongside `Console`,
and [Supplying an Interface](../../Chapters/46_Effects--Stateless.md#supplying-an-interface)
shows how a `Protocol` replaces a concrete class.
Declare `Log` with a `write()` method,
and write a recording class for each protocol.
Pass both instances to `supply()` in one call, run the Effect,
and assert on each recorder's list.

<details>
<summary>Done when</summary>

`uv run pytest` passes your test,
which runs `greet_all()` under one `supply()` call and asserts both the greetings
(`Hello, Alice!`, `Hello, Bob!`) and the log entries
(`greeted Alice`, `greeted Bob`).
`uv run ty check` accepts the file, and `Log` is a `Protocol`.

<details>
<summary>Solution</summary>

If you declare `Log` as a `Protocol` without `@runtime_checkable`,
the type checker passes the listing,
but the run raises a `TypeError` at the first request for a `Log`.
`supply()` matches each request with `isinstance()`,
and `isinstance()` raises a `TypeError` on a `Protocol` without that decorator.
The solution puts the decorator on both protocols,
as `console_protocol.py` does on `Console`.

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

**Fill both roles with one object.**
In `audit_log.py`, `Log` is a `dataclass` that holds its own entries,
so a test constructs one and reads `log.entries` afterward.
For one object to fill both roles there,
it must belong to a class that inherits from both `Log` and `Console`.
As a `Protocol`, `Log` is a shape,
so a single `Recorder` can have that shape and the `Console` shape at once.

**Supply one object under two types.**
The two `as_type()` calls make one object answerable to two requests.
`supply()` reads the Ability from each argument's declared type,
so `supply(recorder, recorder)` builds a handler for `Need[Recorder]`,
an Ability neither Effect requests.
Each wrapper names the role this instance fills.

**Check the greeting and the log together.**
One test holds both assertions because it supplies the whole environment.
The test reads both recorders, with no capture of stdout and no temporary file.
Each `need()` yields a request that the supplied object answers,
so the test chooses what printing and logging do.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. A third material in the table

> Add a `Metal` material to `test_nailer.py` with a strength that survives the robotic nailer,
> and add its two rows to the table.
> Then explain why the test function body stays the same.

<details>
<summary>Where to look</summary>

[One Effect, Many Environments](../../Chapters/46_Effects--Stateless.md#one-effect-many-environments)
shows `parametrize` running `holds()` against a table of materials and nailers.
Define a `Metal` value whose strength exceeds the robotic nailer's force,
and add one row for each nailer.
Consider what `holds()` asks for by type,
and whether a new instance of that type changes the request.

<details>
<summary>Done when</summary>

`uv run pytest` collects six `test_holds` cases and all pass,
including your `Metal` against `ROBOTIC` with `True` expected,
and the body of `test_holds()` is unchanged.
You can say what in `holds()` makes a new row enough.

<details>
<summary>Solution</summary>

If you give `METAL` a strength of `11` or less,
the `(METAL, ROBOTIC, True)` row fails with `assert False is True`.
`holds()` compares with a strict `<`,
so a material survives a nailer when its strength exceeds the force,
not when strength and force are equal.
The solution picks `20`, well above both forces.

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

**Pick a strength above both forces.**
`METAL` at strength `20` exceeds the robotic nailer's force of `11`,
so both its rows read `True`.

**Build each environment from a row.**
The test function body stays the same because every material and nailer arrives as an argument.
The `parametrize` table decides which material and nailer the body receives,
so adding a row adds a case and leaves the function body that runs it as it is.

That split between the table and the body is the chapter's split between an Effect and its environment,
applied to a test.
`holds()` declares two requirements and leaves the instances to `supply()`,
so every combination of instances is a valid environment for it.
The parametrize table is a list of environments,
and the test body is the driver that runs the Effect in each one.
Six rows share one assertion.
A version constructing its own `Material` inside `holds()` needs three copies of the function,
one per material, and a version that also constructs its own `Nailer` needs all six.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 6. A handler that builds what the request names

> This one looks ahead to `handle()`,
> which [Abilities Are Not Special](../../Chapters/47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
> covers.
> `default_console.py` defaults by supplying an instance.
> Write the other kind of default, one that builds the type the request names.
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

[Layering Handlers](../../Chapters/46_Effects--Stateless.md#layering-handlers)
shows a default supplied under a more specific handler,
and [Abilities Are Not Special](../../Chapters/47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
covers `handle()`.
Write a handler function that takes a `Need[Console]` parameter and returns a new instance of the class the request carries in `ability.t`.
Wrap it with `handle()`,
then compare what runs against what the annotation tells the type checker.

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
<summary>Done when</summary>

your handler, wrapped with `handle()`,
makes `greeter.py`'s `greet()` print its greeting,
and an Effect that also requests a second Ability runs to completion,
with a `print()` in the handler showing it answered both requests.
`ty` reports an `invalid-argument-type` at that second `run()`,
naming the leftover `Need`.

<details>
<summary>Solution</summary>

If you return `Console()` in place of `ability.t()`,
`greet()` still prints its greeting,
but `stamped()` fails with `AttributeError: 'Console' object has no attribute 'now'`.
The handler answers the `Clock` request too, as it answers every `Need`,
and hands that request a `Console`.
The type checker accepts `return Console()`,
since `default()` declares that it returns a `Console`.
The solution calls `ability.t()`, which builds the class the request names,
so the `Clock` request receives a `Clock`.

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

**Build the class the request names.**
`default()` names `Console` only in its annotations.
It reads `ability.t`, the class the request carries, and calls that class,
so `default()` answers a request by constructing the requested class.
That is the other kind of default.
`default_console.py` supplies one prepared instance.
`default()` builds the type the request names, on demand.

**Run both Effects through one handler.**
At runtime the handler answered three requests across the two calls,
two for `Console` and one for `Clock`,
although `default()` annotates its parameter `Need[Console]`.
The type checker removes `Need[Console]` from the requirements and leaves `Need[Clock]` open,
so the second `run()` needs a `# type: ignore`.
Without that pragma, the type checker reports a leftover `Need[Clock]`.

`handle()`'s `t = get_origin(t) or t` is the evidence.
`handle()` reads the annotation, reduces `Need[Console]` to its origin, `Need`,
and installs the runtime check `isinstance(ability, Need)`.
That check ignores the type argument, so every `Need[...]` request matches.
The type checker reads the same annotation with its type argument kept,
subtracts `Need[Console]` from the requirements,
and leaves `Need[Clock]` in place.

`handle()` and the type checker are each right about what they describe.
`isinstance()` cannot test a type argument.
`Need[Clock]` and `Need[Console]` are the same runtime class,
so at runtime the two look alike.
The distinction lives in the annotation, where the type checker reads it.
`handle()` matches on the annotation's origin, which erases the distinction.
A handler like `default()` handles more than its type says.
A handler that assumes `ability.t` is a `Console` receives a `Need[Clock]` request unchecked.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. Two ways to drop a `yield from`

> Break `audit_log.py` by removing the `yield from` in front of `greet(name)` in `greet_logged()`.
> Run `ty check`, `ruff check`, and the script,
> and record what each reports and what the program prints.
> Explain where the greetings went and why no tool reports an error.
> Then restore that `yield from`,
> and instead remove the `yield from` in front of `need(Console)` in `greeter.py`'s `greet()`.
> This time the type checker produces two diagnostics.
> Explain what each one catches,
> and why the checker catches assigning a dropped request but not discarding one.

<details>
<summary>Where to look</summary>

[Nothing Runs Yet](../../Chapters/46_Effects--Stateless.md#nothing-runs-yet)
shows that calling a generator function builds an Effect without running its body,
and [Why `yield from`](../../Chapters/46_Effects--Stateless.md#why-yield-from)
explains what the keyword does.
Ask whether a discarded generator breaks any rule `ty` or `ruff` checks.
For the second case,
read both diagnostics and ask what the function has become once it loses its only `yield from`,
and whether the next line uses the dropped value.

<details>
<summary>Done when</summary>

for the first deletion your record shows `ty check` and `ruff check` silent and the script printing `['greeted Alice', 'greeted Bob']` with no greetings,
and for the second it shows `invalid-return-type` and `unresolved-attribute`.
You can say which line makes the second break visible to the type checker.

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

`ty check` and `ruff check` both accept the file.
The script runs to completion and prints:

```text
['greeted Alice', 'greeted Bob']
```

The log entries are the whole output.
`greet()` is a generator function,
so calling `greet(name)` builds an Effect and returns it.
The statement then discards that Effect before its body starts,
so the body never yields its `Need[Console]` request.

The log entries appear because the deletion touches the greeting half of the function and leaves the logging half intact.
The surviving entries make the failure harder to notice.
The program looks like it worked and produced most of its output.

The tools stay silent because the code follows every rule they check.
Building a value and discarding it is legal Python,
and `greet(name)`'s value is a generator like any other.
[Composing Is Not Interpreting](../../Chapters/45_Effects--Generators.md#composing-is-not-interpreting)
and its exercise 4 show the same silence for a generator with no Effect in it.
The declared `Need[Console]` in the return type still holds,
since a declaration says what the function may request, not what it must.
The chapter warns about this deletion.
A bare `greet(name)` passes every check and discards the greeting.

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

The `invalid-return-type` error says `greet()` has become an ordinary function.
Removing the body's one `yield from` removes its last `yield`,
so `greet()` returns `None` where its annotation declares a `Generator`.
The `unresolved-attribute` error says the value in `console` has the wrong type,
a `Generator` rather than a `Console`.

The difference between the two cases is whether anything later uses the dropped value.
The discarded `greet(name)` ends at its statement,
so the type checker evaluates that statement alone and accepts it.
Assigning `need(Console)` binds a generator to `console`,
and the next line calls `print()` on it as if it were a `Console`.
The type checker evaluates that call and rejects it.
A type checker verifies how a program uses its values,
so a value nobody uses is a value nobody checks.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[An Effect Runs Once](../../Chapters/46_Effects--Stateless.md#an-effect-runs-once)
shows a spent Effect returning `None` when you run it again.
Store the Effects in one dictionary and functions that build them in another,
then run each twice.
`retry()` starts the work over after a failure,
so consider what it needs to call each time.

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
<summary>Done when</summary>

your four passes print `Hello, Alice!` and `Hello, Bob!` three times:
the first pass over the stored Effects prints them, the second runs silently,
and both passes over the functions print them.
You can say why a retry needs something it can call once per attempt.

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

**Run each stored Effect twice.**
The second pass over `built` runs silently,
and `run()` returns `None` for each entry.
An Effect is a generator, and a generator runs once.
Resuming a finished generator raises `StopIteration` immediately,
which `run()` reads as "already returned, with no value."
So a spent Effect looks the same as one that succeeded and returned `None`,
and nothing reports the difference.

**Build a fresh Effect per run.**
The stored value changes from a generator, which `run()` consumes once,
to a function, which a caller can call each time it needs a fresh Effect.

That difference is why `retry()` takes a schedule and returns a decorator of type `Callable[P, Effect[...]] -> Callable[P, Effect[...]]` rather than one of type `Effect[...] -> Effect[...]`.
Retrying means running the same work more than once.
An Effect supplies one run.
By the time the first attempt fails,
that attempt has run the generator to its end,
and a finished generator stays finished.
`retry()` needs a fresh Effect per attempt,
and the function that builds the Effect supplies one on each call.
So `retry()` decorates the function, calls it once per attempt,
and hands back a function that takes the same arguments.

The Effect the returned function builds has a wider type.
[`retry()`](../../Chapters/47_Effects--Stateless_in_Practice.md#retry-and-a-flaky-database)
adds `Need[Time]` and `Async` for the sleeps between attempts and replaces the error with a `RetryError`.

The same reasoning explains [`repeat()` and `memoize()`](../../Chapters/47_Effects--Stateless_in_Practice.md#repeat-and-memoize).
It also explains the mistake in storing Effects in a registry, a queue,
or a cache.
The stored Effect looks fine until something runs it twice.
Store the function, and apply the arguments where you need the Effect.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Three reports, one Effect

> Write `report_all()`,
> which calls `stateless_coroutine.py`'s `report()` for three URLs with `yield from` and returns the three results.
> Work out what `report_all()`'s annotation must be,
> and confirm it with the type checker.
> Then call it from inside an `async def`,
> once with `run()` and once with `await run_async()`,
> and record what each one does.
> Explain why the type checker accepts both.

<details>
<summary>Where to look</summary>

[Waiting on a Coroutine](../../Chapters/46_Effects--Stateless.md#waiting-on-a-coroutine)
shows `wait()` putting an `Async` request into an Effect,
and [Where to Call `run()`](../../Chapters/46_Effects--Stateless.md#where-to-call-run)
covers running one from inside an event loop.
Loop over the URLs, delegate to `report()` with `yield from`,
and collect the results in a list.
The annotation carries the `Async` request,
and the two runners differ in whether they start their own event loop.

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
<summary>Done when</summary>

`uv run ty check` passes with your annotation on `report_all()`,
and inside your `async def` the `run()` call raises a `RuntimeError`
(`asyncio.run() cannot be called from a running event loop`)
while `await run_async()` returns three reports, one per URL, in order.

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
    return f"{body = }"

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
#: body = 'fetched a'
#: body = 'fetched b'
#: body = 'fetched c'
```

**Relay the request, collect the results.**
`report()` needs `Async`,
and `yield from` relays each `Async` request to `report_all()`'s caller,
so `report_all()` needs it too.
A channel becomes a union such as `Need[Console] | Need[Log]` when its requirements differ.
Here all three delegations request `Async`, so the channel stays at `Async`.
The return type changes, from one `str` to a `list[str]`,
since `report_all()` collects the results rather than relaying them.

**Drive the Effect from a coroutine.**
`run(effect)` is `asyncio.run(run_async(effect))`.
`asyncio.run()` refuses to start an event loop inside a running one,
so calling `run()` from `main()` fails.
`run_async()` is the same driver in coroutine form,
so the running loop can await it.

The type checker accepts both calls because both are correctly typed.
`run()` takes an Effect and returns its result.
`run_async()` takes an Effect and returns an awaitable of its result.
`report_all(["a"])` satisfies either signature.
Nothing in the type system records that this call site sits inside a coroutine.
Whether an event loop is running is a fact about the moment of the call,
not about the types involved.
A `run()` inside a coroutine therefore passes the type checker and fails at runtime,
with the `RuntimeError` above.
The rule is positional rather than type-based:
`run()` at the outermost edge of a synchronous program,
`run_async()` anywhere inside an asynchronous one.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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
> and say where the program reported each failure.
> Then delete `ValueError` from `announce()`'s annotation and record what the type checker reports and at which line.

<details>
<summary>Where to look</summary>

[Multiple Errors](../../Chapters/46_Effects--Stateless.md#multiple-errors)
shows an Effect declaring more than one failure,
and [The Error Channel](../../Chapters/46_Effects--Stateless.md#the-error-channel)
covers `@throws`.
Lift the helper with `@throws(ValueError)`,
then widen `announce()`'s failure type to a union and call the helper with `yield from`.
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
<summary>Done when</summary>

`uv run ty check` passes, and three names
(one with a positive score, one with a negative score, one missing from `SCORES`)
print one line and raise a `ValueError` and a `KeyError` out of `run()`.
With `ValueError` deleted from `announce()`'s annotation,
`ty` reports `invalid-yield` at your helper's `yield from`.

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

**Lift the helper into an Effect.**
`@throws(ValueError)` turns `format_score()` from a function that raises an exception into an Effect that declares one,
so a call yields the exception as a value instead of letting it propagate up the stack.

**Declare the second failure.**
Following the type checker until the program builds means one edit:
widening `announce()`'s error parameter from `KeyError` to `KeyError | ValueError`.

`line: str` and `value: int` carry annotations by choice,
not because the type checker requires them.
`yield from` on a `@throws` function produces the declared success type,
and specifying that type makes the type checker compare its inference with the annotation.

**Let `run()` raise each failure.**
`Cyd` has a score, so the lookup succeeds and `format_score()` fails.
`Dana` has none, so the lookup fails and the Effect ends before `format_score()`.
In both cases each `yield from` relays the error value as is,
through `announce()` and the `supply()` handler, to the driver.
`run()` is the first code to act on the error,
and it raises the error as an ordinary exception.
Declaring a failure is not handling it.
The declaration says the failure can occur.
`catch()` turns it into a value the program handles.

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

The error appears on line 29,
the `yield from` that introduces the undeclared failure,
not on the signature and not at the call site.
That statement is the useful place for the diagnostic.
The diagnostic gives the undeclared failure's type and marks the delegation that yields it,
so the fix is either to declare the failure or to catch it, right there.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[When Two Implementations Match](../../Chapters/46_Effects--Stateless.md#when-two-implementations-match)
explains why `supply()` takes the first argument that satisfies the request.
Predict from argument order, since `supply()` uses the first match.
If you give each implementation its own `Protocol` with a differently named method,
the type checker rejects an implementation that lacks the method the Effect requests.
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
<summary>Done when</summary>

your six predictions match six runs with the third implementation added.
With separate `Protocol`s,
handing `Terminal` to the recording Effect draws an `invalid-argument-type` that names the missing method,
and you can name the case that two `Protocol`s still leave to argument order.

<details>
<summary>Solution</summary>

Three implementations have six orderings, and one rule predicts them all.
`supply()` scans its arguments and takes the first that satisfies the request,
so whichever implementation comes first answers it.
Two of the six orderings put `Terminal` first and send the greeting to the screen.
The remaining four split evenly between `Capture` and the third implementation.
All six orderings run cleanly.

The fix splits the one structural check that all three objects match:

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

**Give each role its own protocol.**
The fix renames `Capture.print()` to `record()`,
gives each method its own `Protocol`, `Screen` and `Recorder`,
and splits `greet()` into one Effect per `Protocol`.
The two `Protocol`s now describe different shapes,
so each implementation satisfies one of them,
and each Effect requests the `Protocol` it needs.

That change turns the silent choice into a diagnostic.
One more line at the end of the listing could hand `to_log()` the object that prints instead of the one that records.
`ty` rejects that line before the program runs:

```text
error[invalid-argument-type]: Argument is incorrect
  --> exercise_11.py:40:30
   |
40 | run(supply(as_type(Recorder)(Terminal()))(to_log)("Carol"))
   |                              ^^^^^^^^^^ Expected `Recorder`, found `Terminal`
info: type `Terminal` is not assignable to protocol `Recorder`
info: └── protocol member `record` is not defined on type `Terminal`
```

In the second `info` line,
the type checker names the missing method rather than the missing type.
That is what structural typing means: `Terminal` fails for the method it lacks,
not for the class it is.

If you keep `print()` on both implementations and declare it in both `Protocol`s,
each implementation satisfies both,
and the type checker accepts `as_type(Recorder)(Terminal())`.
Handing that object to `to_log()` prints `Hello, Carol!` to the screen while `capture.messages` stays `['Hello, Bob!']`,
with no diagnostic.
Two `Protocol`s that share one method name describe one shape under two names.

One limit remains.
Distinct method names remove the ambiguity between Abilities.
They leave two implementations of the same Ability ambiguous.
A second recorder, an `Audit` that also defines `record()`,
brings the ambiguity back.
Supplying `capture` and `audit` both through `as_type(Recorder)` leaves the choice to argument order,
with no diagnostic.

That limit is why [When Two Implementations Match](../../Chapters/46_Effects--Stateless.md#when-two-implementations-match)
gives its advice in two halves.
No type can enforce the second half, "supply one implementation per Ability."
Because `supply()` resolves a request by scanning its arguments at runtime,
a duplicate is a fact about the call rather than about the types.
ZIO's compile-time rejection of this case is the difference that section describes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
