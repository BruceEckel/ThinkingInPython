# Stateless

[Effect Management](44_Effect_Management.md#library-effect-management)
introduced library Effect systems and named [Stateless](https://github.com/suned/stateless)
as a library that implements an Effect Management System (EMS).

Stateless encodes an Effect's dependencies and failures into the return type of a function,
and a type checker verifies that every caller either absorbs the Effects or carries them forward.
Forget to declare a dependency and the check fails.
Forget to supply one and the check fails.
That is the Effect tracking and delayed binding of a full EMS,
with the bookkeeping moved into the type system.

Stateless is built on generators.
[Generators](45_Generators.md) covered what this chapter assumes:
the three-parameter `Generator` annotation,
a driver that answers a generator's requests one `send()` at a time,
and `yield from`, which composes generators and produces the inner one's return value.
Every Effect here travels that path.
Stateless supplies the vocabulary for the requests and the driver that answers them.

My understanding of Effects came from work with Bill Frasure and James Ward as we created [Effect Oriented Programming](https://effectorientedprogramming.com/).
Some of the examples in this chapter were derived from that book.

## The Effect Type

Stateless builds everything atop a single type.
The library defines it with type variables,
`A` bound to `Ability` and `E` bound to `Exception`:

```python
Effect: TypeAlias = Generator[A | E, Any, R]
```

An `Effect` is a generator that yields either an *ability* `A` or an exception `E`,
and eventually returns a result `R`.
The three type parameters answer the three questions [Effect Management](44_Effect_Management.md#library-effect-management)
asked of an Effect signature:

- `A` is what the computation *needs*.
- `E` is how it can *fail*.
- `R` is what it *produces*.

`A` and `E` share the first type parameter, and `R` is the third.
That leaves the second,
which [Generators](45_Generators.md#annotating-a-generator)
taught you to read as "what comes back from a `yield` call."
That `Any` is essential, and it explains an idiom the rest of the chapter uses.

A generator has one SendType for its whole life.
An Effect does not:

- Using `yield` to request a `Need[Console]` should get a `Console`.
- Using `yield` to request a `Need[Log]` should get a `Log`.

What comes back depends on which ability the `yield` requested,
and one SendType cannot vary from one `yield` to the next.
Pin it to `Console` and the checker reads `yield Need(Log)` as producing a `Console`.
Anything must come back through the `send()` channel, so we give it type `Any`.

`yield from` recovers the precision that `Any` gave up,
so a request can produce an answer whose type the checker knows.
A bare `yield` produces the SendType,
the type parameter that had to become `Any`.
`yield from` produces the inner generator's return type,
the third type parameter.
A single call returns a single type, so that type parameter has no such problem.
It can name that specific type instead of `Any`.
So a function that hands back a typed answer declares it as `R`.
`need()` returns `Depend[Need[T], T]`, which is `Generator[Need[T], Any, T]`,
and `console = yield from need(Console)` reads the `Console` out of that third type parameter without touching the `Any`.

That is why every request in this chapter is written as `yield from` rather than `yield`,
and why custom abilities get a small function of their own later on.

Three aliases name the common cases,
each one filling in `Never` for a type parameter that is not used:

| Alias | Meaning |
|---|---|
| `Success[R]` | Needs nothing, cannot fail, produces `R` |
| `Depend[A, R]` | Needs `A`, cannot fail, produces `R` |
| `Try[E, R]` | Needs nothing, can fail with `E`, produces `R` |

`Never` is the type with no values,
so `Success[R]` promises there is no ability it can request and no error it can yield.
The signature is the entire claim.

Here, `success()` wraps a value in an Effect, and `run()` executes it.
`run()` is the Stateless library's driver,
replacing the `drive()` of [Generators](45_Generators.md#a-generator-is-a-description).
`run()` primes the generator, answers each request, and returns the result.
Nothing computes until `run()` is called, and a program calls it once,
at its outermost edge:

```python
# simplest_effect.py
from stateless import Success, run, success

def double(n: int) -> Success[int]:
    return success(n * 2)

print(run(double(21)))
#: 42
```

`Success[int]` says `double()` is pure.
It cannot read anything, and it cannot fail.

Notice that `double()` contains no `yield`, so it is not a generator function.
It does not need to be.
`success()` returns an object that implements the generator protocol,
and the annotation only promises that calling `double()` produces an Effect.
`success()` exists for yield-free functions like this one.
In a generator function, an ordinary `return` sets the result;
wrap it in `success()` there and the checker reports a return-type mismatch.
Functions that request things are generator functions, which we look at next.

Nothing is gained yet, because `double()` was already pure.
Effects become useful when a function needs something it doesn't create for itself.

## Declaring a Dependency

`Need` is the built-in ability for dependency injection.
`need(SomeClass)` is an Effect that produces an instance of `SomeClass`,
without saying where the instance comes from:

```python
# greeter.py
from stateless import Depend, Need, need

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")
```

Read the signature as a sentence.
`greet()` needs a `Console`, cannot fail, and produces nothing.
Compare that to `def greet(name: str) -> None`,
the version that calls `print()` directly.
That signature is a lie by omission.
`-> None` claims the function returns nothing and mentions nothing else,
while the body writes to standard output.
The only thing that version does is the thing its type leaves out,
so a caller cannot see the dependency, redirect the output,
or test the function without capturing stdout.
`Depend[Need[Console], None]` states the dependency,
and the rest of the chapter is about who enforces the difference.

Two details deserve attention.
`greet()` is a generator function, because it contains `yield from`,
so calling it builds the Effect its signature declares.
And `console` really is a `Console` to the type checker,
so `console.print()` is checked the same as any other method call.
The dependency is deferred without becoming untyped.

## Nothing Runs Yet

Calling `greet()` performs no work at all:

```python
# describe_only.py
from greeter import greet

description = greet("Alice")
print(type(description).__name__)
#: generator
```

Nothing is printed except the type name.
`greet("Alice")` builds a description of a greeting.
This is the description/execution split from [Effect Management](44_Effect_Management.md#library-effect-management),
and the reason a library EMS needs one.
The library gets no chance to intercept `console.print()` as it happens.
Its only power is over values, so the greeting must first become a value.

## Supplying the Dependency

`supply()` binds an instance to the `Need` that asked for it:

```python
# supply_console.py
from greeter import Console, greet
from stateless import run, supply

bound = supply(Console())(greet)
run(bound("Alice"))
#: Hello, Alice!
```

That line does three things, and separating them makes the shape clear:

1. `supply(Console())` builds a *handler*,
   an object that knows how to answer `Need[Console]`.
2. Calling the handler on `greet` returns a new function that answers the requests `greet()` makes.
3. Calling that function with `"Alice"` builds an Effect with nothing left to supply,
   which `run()` executes.

Now compare the types.
`greet` is `(str) -> Depend[Need[Console], None]`.
`bound` is `(str) -> Success[None]`.
To see a type yourself, add `reveal_type(bound)` and run `ty check`.
The checker reports `(name: str) -> Generator[Never, Any, None]`,
the expanded form of `Success[None]`,
with `Never` in the channel the alias table promised.
Handling an ability *subtracts* it from the type.
An Effect with every ability subtracted is a `Success`,
and `run()` refuses an unanswered ability.
Binding an implementation and satisfying the type checker are the same act.

## Forgetting to Supply

Let's break it and see what happens.
Hand `run()` an Effect that still needs a `Console`:

```python
# unsupplied.py
from greeter import greet
from stateless import run
from stateless.errors import MissingAbilityError

try:
    run(greet("Alice"))  # type: ignore
except MissingAbilityError as e:
    print(type(e).__name__)
#: MissingAbilityError
```

At runtime this raises a `MissingAbilityError`,
which the listing catches so it can print something.
But the runtime failure is not the point.
Remove the `# type: ignore` and `ty` rejects the program before it runs:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
 --> unsupplied.py:7:9
  |
7 |     run(greet("Alice"))
  |         ^^^^^^^^^^^^^^ Expected
  |         `Generator[Async | Exception, Any, Unknown]`, found
  |         `Generator[Need[Console], Any, None]`
```

This is the guarantee, and it is the reason the chapter exists.
A dependency that was never bound is a type error, not a production incident.
No test had to exercise the path.
No reviewer had to notice the omission.

The expected type in that message names two things this chapter has not covered.
`Async` is a built-in ability for asynchronous work,
which `run()` handles on its own.
`Exception` is the error channel, which a later section fills.
`run()` insists on every other ability being answered,
and those two are what remain when they are.

## Swapping the Implementation

Delayed binding earns its keep when the binding changes.
A test binds a `Console` that records instead of printing:

```python
# recorder.py
from dataclasses import dataclass, field
from typing import override
from greeter import Console

@dataclass
class Recorder(Console):
    messages: list[str] = field(default_factory=list)
    @override
    def print(self, message: str) -> None:
        self.messages.append(message)
```

```python
# test_greeter.py
from greeter import Console, greet
from recorder import Recorder
from stateless import as_type, run, supply

def test_greet() -> None:
    recorder = Recorder()
    console = as_type(Console)(recorder)
    run(supply(console)(greet)("Alice"))
    assert recorder.messages == ["Hello, Alice!"]
```

There is no `capsys`, no monkeypatching of `print`, and no mock.
The test supplies a different `Console` and reads what the code produced.
`greet()` is unchanged and unaware.

`as_type()` needs explaining, because it looks like nothing.
At runtime it is the identity function and returns the object it was given.
Its purpose is the annotation.
`supply(recorder)` would build a handler for `Need[Recorder]`,
and `greet()` asked for `Need[Console]`, which is a different ability.
`as_type(Console)(recorder)` says "treat this as the `Console` it implements,"
so `supply()` builds the handler that `greet()` is waiting for.
Supply an implementation for a declared interface and you will need this.
`typing.cast(Console, recorder)` does the same job.
`as_type()` is the library's named form of the cast.

`supply()` matches an instance to a `Need` by `isinstance()`,
which is why `Recorder` inherits from `Console`.
Every matching request over the Effect's run receives that same instance,
which is why the test can read the results back out of `recorder` afterward.
Inheriting from a concrete class only to replace all of it is a poor arrangement,
so make the ability an interface instead:

```python
# console_protocol.py
from typing import Protocol, runtime_checkable
from stateless import Depend, Need, need

@runtime_checkable
class Console(Protocol):
    def print(self, message: str) -> None: ...

class Terminal:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")
```

`Console` is now the second property of an EMS: an Effect's interface,
separate from any implementation.
`Terminal` is one implementation and `Recorder` would be another,
and neither is named anywhere in `greet()`.
`@runtime_checkable` is required because `supply()` uses `isinstance()`.

This is the form to write in production.
The smaller listings that follow keep importing `greeter.py`'s concrete `Console`,
because a supply site for a `Protocol` ability needs help naming the interface:
`supply(Console())` becomes `supply(as_type(Console)(Terminal()))`.
That is a real price the interface charges, not only a shortcut for the book.
[Composing the Whole Program](#composing-the-whole-program)
returns to `Protocol` abilities and shows the cheaper way to pay it:
a boundary function whose parameters are annotated with the interface types,
so the cast disappears into ordinary parameter annotations.
Everything in between works the same under either form.

You may also not need to declare an ability at all.
Stateless includes three of its own:
a `Console` in `stateless.console` with `print_line()` and `read_line()` accessors,
a `Files` in `stateless.files` that reads a whole file,
and the `Time` that a later section supplies to `retry()`.
The chapter builds its own `Console` because watching one get built is the point.
In your own code, check what the library already declares first.

## When Two Implementations Match

A structural check matches on method names alone,
so two supplied objects that both define `print()` are indistinguishable.
Supply both and argument order decides which one answers:

```python
# ambiguous_supply.py
from dataclasses import dataclass, field
from console_protocol import Console, Terminal, greet
from stateless import as_type, run, supply

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)
    def print(self, message: str) -> None:
        self.messages.append(message)

capture = Capture()
screen = as_type(Console)(Terminal())
memory = as_type(Console)(capture)
run(supply(screen, memory)(greet)("Alice"))
#: Hello, Alice!
print(capture.messages)
#: []
run(supply(memory, screen)(greet)("Bob"))
print(capture.messages)
#: ['Hello, Bob!']
```

`Terminal` and `Capture` share no base class and know nothing of each other.
Both satisfy `Console` structurally, so `isinstance()` accepts either,
and `supply()` hands over whichever it examines first.
Alice's greeting reaches the screen and leaves `capture` empty.
Swapping the two arguments sends Bob's greeting into `capture` and prints nothing.
Neither `greet()` nor the type checker can tell the two runs apart,
because both bindings have the same type.
Both instances go through `as_type(Console)`,
since neither is nominally a `Console`.

Here Stateless gives up something ZIO keeps.
ZIO reports two implementations of one requirement as a compile-time error naming both candidates,
because its `provide` resolves the dependency graph during compilation.
`supply()` resolves at runtime by scanning its arguments,
so the same mistake produces a program that runs and does the wrong thing.
Give abilities distinct method names when that ambiguity is possible,
and supply one implementation per ability.

## Effects Propagate, and the Checker Verifies It

A function that calls an effectful function becomes effectful.
`greet_all()` must declare the `Console` it never touches:

```python
# greet_all.py
from greeter import Console, greet
from stateless import Depend, Need, run, supply

def greet_all(names: list[str]) -> Depend[Need[Console], None]:
    for name in names:
        yield from greet(name)

run(supply(Console())(greet_all)(["Alice", "Bob"]))
#: Hello, Alice!
#: Hello, Bob!
```

This is the same virality `async` has.
An `async` function's callers must become `async`,
all the way to `asyncio.run()`.
A `Depend` function's callers must declare the dependency,
all the way to `supply()`.
The difference is that you can declare as many abilities as you like,
where Python hard-codes one.

The `yield from` is not optional.
Write `greet(name)` alone, without it,
and the program still type-checks and runs.
It builds a description, immediately discards it,
and the greeting never happens.
Neither the type checker nor the linter flags the dropped value.
The same trap exists in ZIO for the same reason.
An Effect written as a bare statement is a discarded value there too,
and the fix is `.run` where Python's is `yield from`.
The hazard belongs to deferred execution rather than to generators.
When an Effect seems not to happen, look for a missing `yield from`.

Declaring the ability is still manual, and it is fair to ask what was gained.
The gain is that the declaration is checked.
Annotate `greet_all()` as pure and `ty` refuses:

```python
# undeclared_need.py
from greeter import greet
from stateless import Success

def greet_all(names: list[str]) -> Success[None]:
    for name in names:
        yield from greet(name)  # type: ignore
```

```text
error[invalid-yield]: Yield expression type does not match annotation
 --> undeclared_need.py:5:36
  |
5 | def greet_all(names: list[str]) -> Success[None]:
  |                                    ------------- Function annotated
  |                                    with yield type `Never` here
6 |     for name in names:
7 |         yield from greet(name)
  |                    ^^^^^^^^^^^ expression of type `Need[Console]`,
  |                    expected `Never`
```

A function cannot claim to be pure while calling something impure.
Compare that to `ask_tell.py` in [Effect Management](44_Effect_Management.md#effects-by-hand),
where `greet(ask, tell)` took its dependencies as arguments.
Nothing there stopped an intermediate function from constructing its own `Console` and quietly performing an undeclared Effect.
Here, the signature and the body cannot disagree.

## Where `run()` Can Be Called

The error message in `unsupplied.py` said `run()` handles `Async` on its own.
It can do that because `run()` is `asyncio.run(run_async(effect))` underneath.
That has a consequence worth knowing before you wire Stateless into an existing application.
`asyncio.run()` refuses to start a second event loop inside a running one,
so `run()` cannot be called from any `async def`:

```python
# inside_a_loop.py
import asyncio
from greeter import Console, greet
from stateless import run, run_async, supply

bound = supply(Console())(greet)

async def main() -> None:
    try:
        run(bound("Alice"))
    except RuntimeError as e:
        print(e)
    await run_async(bound("Bob"))

asyncio.run(main())
#: asyncio.run() cannot be called from a running event loop
#: Hello, Bob!
```

Running this prints a `RuntimeWarning` on standard error alongside the caught message.
`run()` builds the `run_async()` coroutine before handing it to `asyncio.run()`,
which then refuses, leaving that coroutine un-awaited.
It is harmless and it tells you where the boundary is.

`run_async()` is the same driver as a coroutine, so you `await` it instead.
A synchronous program calls `run()` once at its outermost edge.
A program that is already asynchronous, a web service or a bot,
awaits `run_async()` at the edge of each request.
Picking the wrong one is a runtime error rather than a type error,
which makes it one of the few mistakes in this chapter the checker will not catch for you.

## Adding an Effect Deep in the Stack

The second exercise in [Effect Management](44_Effect_Management.md#exercises)
has you add a `Log` Effect alongside `greet()` and count the signatures you edit.
Here is that experiment in Stateless:

```python
# audit_log.py
from dataclasses import dataclass, field
from greeter import Console, greet
from stateless import Depend, Need, need, run, supply

@dataclass
class Log:
    entries: list[str] = field(default_factory=list)
    def write(self, entry: str) -> None:
        self.entries.append(entry)

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

log = Log()
run(supply(Console(), log)(greet_all)(["Alice", "Bob"]))
print(log.entries)
#: Hello, Alice!
#: Hello, Bob!
#: ['greeted Alice', 'greeted Bob']
```

The signature count is the same as the by-hand version.
Every function on the path to the new Effect gained a `Need[Log]`,
and `supply()` gained an argument.
Stateless does not remove that work.
What it removes is the searching.
The checker names every line that needs the change,
and the program does not build until the last one is fixed.
To watch it do the naming, delete `| Need[Log]` from either annotation:
the checker points at the yield that still carries the ability.
With dependencies passed as parameters,
a missed thread produces a runtime `TypeError` in whatever code path happens to reach it.

Multiple abilities combine with `|`, which reads correctly.
`greet_all()` needs a `Console` or a `Log` at each individual request,
and both over its lifetime.

The repeated union invites a `type` alias,
and the book's own habits would normally endorse one.
Resist it here.
Under `ty` (0.0.64 at this writing),
a `type` alias as a generator's return annotation turns the yield check off,
and everything this section demonstrated silently stops being verified.
Stateless avoids the trap in its own definitions:
`Effect` and its aliases are older `TypeAlias` assignments rather than `type` statements,
and those keep the check alive.
Write Effect signatures out in full until your checker proves it sees through the alias.

## One Effect, Many Environments

`audit_log.py` supplied two abilities at one call site.
A test suite usually needs many, one per environment.
Because the dependencies live in the return type rather than the argument list,
varying the environment means varying data:

```python
# nailer.py
from dataclasses import dataclass
from stateless import Depend, Need, need

@dataclass(frozen=True)
class Material:
    brittleness: int

@dataclass(frozen=True)
class Nailer:
    force: int

def holds() -> Depend[Need[Material] | Need[Nailer], bool]:
    material = yield from need(Material)
    nailer = yield from need(Nailer)
    return nailer.force < material.brittleness
```

`holds()` decides whether a nailer's force stays under a material's brittleness.
It requests both and names neither implementation.
`Material` and `Nailer` are distinct types,
so `supply()` matches each request to one of them without the ambiguity `ambiguous_supply.py` showed:

```python
# test_nailer.py
from typing import Final
import pytest
from nailer import Material, Nailer, holds
from stateless import run, supply

WOOD: Final[Material] = Material(brittleness=5)
PLASTIC: Final[Material] = Material(brittleness=10)
HAND: Final[Nailer] = Nailer(force=4)
ROBOTIC: Final[Nailer] = Nailer(force=11)

@pytest.mark.parametrize("material, nailer, expected", [
    (WOOD, HAND, True),
    (PLASTIC, HAND, True),
    (WOOD, ROBOTIC, False),
    (PLASTIC, ROBOTIC, False),
])
def test_holds(
    material: Material, nailer: Nailer, expected: bool
) -> None:
    assert run(supply(material, nailer)(holds)()) is expected
```

One test function covers four environments.
`holds()` takes no arguments, so `material` and `nailer` are not inputs to it.
They are the bindings `supply()` will make,
so the table reads as a matrix of environments rather than a list of arguments.
A new `Material` is a new row.

Be honest about the size of the win here.
Dependencies as parameters would serve this test as well,
because `holds(material, nailer)` is easy to call four times.
The difference appears when the dependency sits three calls deep.
Then the parameter version threads two arguments through every function on the path,
and this version changes nothing but the row.

## The Error Channel

Dependencies are one half of the type.
The other half is failure.
`@throws` converts a raised exception into a yielded one:

```python
# scores.py
from typing import Final
from stateless import throws

SCORES: Final[dict[str, int]] = {"alice": 42, "bob": 7}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name.lower()]
```

`score()` looks like an ordinary function that raises a `KeyError`,
but the decorator changes its type to `(str) -> Try[KeyError, int]`.
This is the `Result` type of [Error Handling](42_Functional_Error_Handling.md#turning-exceptions-into-results),
arrived at from the other direction.
There, you rewrote a function to return `Ok` or `Err`.
Here, you leave the body alone and lift the exception into the signature.

You can watch the failure travel.
Calling `score()` still runs nothing.
Drive the description one step and the `KeyError` arrives as a value,
not as a raised exception:

```python
# error_is_yielded.py
from scores import score

effect = score("carol")
print(repr(next(effect)))
#: KeyError('carol')
```

The body raised the exception, the decorator caught it,
and the exception object went out over the channel abilities use.
That is why `Effect`'s first type parameter holds `A | E`:
requests and failures are both values a description yields to its driver.

Because errors and abilities share a channel, they propagate the same way:

```python
# announce.py
from greeter import Console
from scores import score
from stateless import Effect, Need, need

def announce(name: str) -> Effect[Need[Console], KeyError, None]:
    value: int = yield from score(name)
    console = yield from need(Console)
    console.print(f"{name}: {value}")
```

Here is where the full `Effect[A, E, R]` earns its three type parameters.
`announce()` needs a `Console`, can fail with `KeyError`, and produces nothing.
All three questions are answered by its first line.
Drop the `KeyError` from the annotation and `ty` reports the same class of error it did before,
this time pointing at the `yield from score(name)` line.
Declared exceptions cannot be dropped by forgetting them.

A declared error can, however, ride all the way to the edge.
`run()` accepts an Effect whose error channel is still occupied,
and a failure that reaches it surfaces as an ordinary raised exception:

```python
# error_escapes.py
from announce import announce
from greeter import Console
from stateless import run, supply

try:
    run(supply(Console())(announce)("Carol"))
except KeyError as e:
    print(type(e).__name__)
#: KeyError
```

The channel tracks failures without forcing you to handle them,
and at the boundary they turn back into normal Python exceptions.
Handling one inside the system is the next section.

## Turning an Error Into a Value

`catch()` handles an error the way `supply()` handles an ability.
It removes the error from the type and moves it into the result.
`@throws` and `catch()` are two ends of one pipe:
the decorator puts a raised exception into the channel,
and `catch()` takes it back out:

```python
# catch_score.py
from greeter import Console
from scores import score
from stateless import Depend, Need, catch, need, run, supply

def report(name: str) -> Depend[Need[Console], None]:
    value: int | KeyError = yield from catch(KeyError)(score)(name)
    console = yield from need(Console)
    match value:
        case KeyError():
            console.print(f"{name}: unknown")
        case _:
            console.print(f"{name}: {value}")

run(supply(Console())(report)("Alice"))
run(supply(Console())(report)("Carol"))
#: Alice: 42
#: Carol: unknown
```

`score` was `(str) -> Try[KeyError, int]`.
`catch(KeyError)(score)` is `(str) -> Success[int | KeyError]`.
The error left the error type parameter and joined the result type parameter,
so `value` is something you `match` on rather than an exception you catch.

That relocation makes the failure impossible to ignore.
Skip the `KeyError` branch and use `value` as a number,
and the checker reports it:

```text
error[unsupported-operator]: Unsupported `+` operation
 --> catch_score.py:9:30
  |
9 |     console.print(f"{name}: {value + 1}")
  |                              -----^^^-
  |                              |       |
  |                              |       Has type `Literal[1]`
  |                              Has type `int | KeyError`
```

This is the same guarantee a `Result` type gives in [Error Handling](42_Functional_Error_Handling.md#a-result-type),
reached without rewriting the body of `score()`.

`catch()` takes as many error types as you need to handle,
and handling a subset is tracked as carefully as handling all of them.
A function that declares two failures shows the difference.
`parse_score()` looks a name up and converts what it finds,
so an unknown name raises a `KeyError` and an unreadable value raises a `ValueError`:

```python
# parse_score.py
from typing import Final
from stateless import throws

RAW: Final[dict[str, str]] = {"alice": "42", "bob": "seven"}

@throws(KeyError, ValueError)
def parse_score(name: str) -> int:
    return int(RAW[name.lower()])
```

`@throws(KeyError, ValueError)` makes it `(str) -> Try[KeyError | ValueError, int]`.
Now catch both errors, then catch one of them:

```python
# catch_subset.py
from parse_score import parse_score
from stateless import Success, Try, catch, run

both = catch(KeyError, ValueError)(parse_score)
one = catch(KeyError)(parse_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case ValueError():
            return f"{name}: unreadable"
        case _:
            return f"{name}: {value}"

def one_left(name: str) -> Try[ValueError, str]:
    value: int | KeyError = yield from one(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case _:
            return f"{name}: {value}"

for who in ["alice", "bob", "carol"]:
    print(run(all_handled(who)))
#: alice: 42
#: bob: unreadable
#: carol: unknown
print(run(one_left("alice")))
#: alice: 42
try:
    run(one_left("bob"))
except ValueError as e:
    print(type(e).__name__)
#: ValueError
```

`both` is `(str) -> Success[int | KeyError | ValueError]`.
Every failure moved into the result and nothing is left in the error channel,
so `all_handled()` can promise `Success[str]`: no failure escapes it,
and the three names exercise its three branches.

`one` is `(str) -> Try[ValueError, int | KeyError]`.
The caught error moved to the result and the uncaught one stayed put,
so `one_left()` must declare a `ValueError` it never handles.
Calling it on `"bob"` carries that failure to the edge,
where `run()` raises it as an ordinary exception,
the same escape `error_escapes.py` showed for a single error.
Failures cannot be lost, only relocated.

## Abilities Are Not Special

`Need` looks built-in, but it is an ordinary class, and you can write your own.
An ability subclasses `Ability[T]`, where `T` is the type its handler returns.
Here is the `Ask` and `Tell` program from [Effect Management](44_Effect_Management.md#effects-by-hand),
rebuilt:

```python
# ask_tell_effect.py
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

def scripted(request: Ask) -> str:
    return "Alice"

def capture(request: Tell) -> None:
    messages.append(request.message)

half = handle(capture)(greet)
full = handle(scripted)(half)
run(full())
print(messages)
#: ['Hello, Alice!']
```

Inside `ask()`, `yield from Ask(prompt)` yields the ability object and returns whatever the handler sends back.
`ask()` and `tell()` are *accessors*:
small functions that each wrap one ability and declare its answer type.
`need()` has the same shape,
and the ZIO listing in [Effect Management](44_Effect_Management.md#library-effect-management)
had an accessor object doing the same job.
The declared `Depend[Ask, str]` types `name` as `str` inside `greet()`.
You can skip the accessor and yield the ability directly,
and the program still runs,
but under `ty` 0.0.64 the answer comes back as `Unknown` and the checking quietly stops.
The accessor pins it down.
That is what the `answer: str` inside `ask()` is doing.
`yield from Ask(prompt)` produces `Unknown` there too,
so the annotation is an assertion the checker takes on faith rather than a type it worked out.
`Ability[str]` is where the claim comes from,
and writing it at the binding keeps the accessor's promise in one place,
one line above the `Depend[Ask, str]` that repeats it to callers.

That annotation reads `Depend[Ask, str]`, not `Depend[Need[Ask], str]`,
and the difference deserves a moment.
`Ask` is an ability, so it sits in the channel bare.
`Console` never was one.
It is an ordinary class, and `Need[Console]` is the ability:
a request object carrying the class it asks for.
The bound the chapter opened with enforces the distinction.
`Effect`'s first type parameter accepts only `Ability` subclasses,
so writing `Depend[Console, None]` is rejected at the annotation,
before any `yield` is examined: `Console` is not assignable to the bound.

`handle()` reads the annotation on its argument to decide which ability it answers,
which is why `scripted` and `capture` must annotate their parameters.
Each `handle()` subtracts one ability,
so `half` still needs an `Ask` and `full` needs nothing.
Naming the two stages also matters to the checker,
for a reason the next section gives.

Now compare this listing to `ask_tell.py` again.
The by-hand version threaded two objects through every signature.
This one threads nothing.
`greet()` takes no arguments at all,
and the two Effects live in the return type where a checker can follow them.
That second channel in the signature is the one that chapter said an EMS needs.

Return to `two_way_generator.py` in [Generators](45_Generators.md#a-generator-is-a-description)
and the whole library is visible.
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
and `scripted` returned `"Alice"` however often `greet()` requested a name.
A handler is an ordinary function, so it can answer differently at each request.
That is what makes an unpredictable source testable.

A coin toss is a side cause: the program reads something from outside,
and the reading does not repeat.
Turn it into an ability and the reading moves into a handler:

```python
# coin_toss.py
import random
from typing import Final
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

FLIPS: Final[tuple[bool, ...]] = (True, False, True, True, False)
script = iter(FLIPS)

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
where `Ask` and `Tell` each carried the payload the request had to deliver.
The ability's whole content is its type and the `bool` it promises back.

Two handlers answer the same function.
`scripted` walks an iterator over a fixed sequence,
so the five tosses are decided before the program runs and the count is `3`.
`coin` calls `random.random()`, so ten thousand tosses come out near half heads.
`count_heads()` cannot distinguish the two,
because either answer arrives through the same `send()` channel.

The scripted handler holds state, and that is the point.
`next(script)` produces a different value at each request,
which one supplied instance cannot do.
Every scripted test double has this shape: a queue handing out canned responses,
a network stub that fails twice and then succeeds, or the clock below.

A clock is the other side cause every test trips over.
`stamp()` puts the current time into its output,
and `batch_due()` decides whether a day has passed since the last run.
Against a real clock neither is testable.
One produces a different string every minute,
and the other needs you to wait a day to watch it return `True`:

```python
# frozen_clock.py
from datetime import datetime, timedelta
from typing import Final
from stateless import Ability, Depend, handle, run

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

`frozen` reports one moment,
so `stamp()` produces a fixed string a test can compare.
`tomorrow` reports a moment a day later,
and `batch_due()` returns `True` with no time having passed.
The schedule logic runs against whatever moment the handler names,
in microseconds rather than a day.
`batch_due()` holds no `datetime.now()` call,
so there is nothing to monkeypatch and nothing to wait for,
and a production handler that returns `datetime.now()` leaves the function unchanged.

Compare this to `student_pairs.py` in [Functional Toolkits](41_Functional_Toolkits.md#case-study-pairing-rotations),
which made randomness repeatable a different way, by taking a `seed` parameter.
That works, and it charges a parameter to every function between the caller and the `random.Random` call.
Here the source is named in the return type instead,
and no signature between `handle()` and the request mentions it.

Both abilities in this section are side causes,
in the vocabulary of [Effect Management](44_Effect_Management.md#subdividing-the-impure-portion):
the function reads something from outside.
`Recorder`, earlier in this chapter, stood in for a side effect,
where the function writes something outward.
The technique did not change between the two.
Name the seam as an ability and bind it at the edge to whatever the context needs.
What an EMS adds is that the seam cannot be skipped by accident.

## Composing the Whole Program

Every listing so far made one point in one or two steps.
A program is longer,
and the claim this chapter has been building is about what a longer program's signature tells you.
Here is a small application: fetch a headline,
find a topic worth researching in it, and look that topic up.
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

Read `research()`'s signature and you have the program's whole surface.
It reads two things from outside and can fail three ways,
and that is a complete account, checked against the body.
The three `@throws` functions are the pattern for reaching ordinary code:
`fetch()` and `look_up()` call methods that know nothing about Effects,
and the decorator lifts what they raise into the channel.
`topic_of()` needs nothing and touches nothing, so it declares no ability.

`fetch()` and `look_up()` take their dependencies as parameters,
which makes them ordinary functions rather than generator functions.
That is a choice, not a requirement.
`@throws` decorates a function returning an Effect just as readily,
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

Annotate the undecorated shape, `Depend[Need[Feed], str]`,
and the decorator adds the error the same way it did for `score()`.
`ty` reports `fetch_headline` as `() -> Generator[Need[Feed] | Unavailable, Any, str]`,
which is `Effect[Need[Feed], Unavailable, str]`.
`research()` splits the two apart because a function that only transforms its arguments is easier to test on its own,
and because the split keeps the ability requests collected in one place where you can read them.
Either shape type-checks and either propagates correctly.

The signature is also the only place this information appears.
Nothing in the body mentions a network, a file, or a print,
and `research()` performs no work when called.
Now supply the environment:

```python
# scenarios.py
from dataclasses import dataclass
from typing import Final
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
        case _:
            return found

STOCKS: Final[Wire] = Wire("stock market rising")
WEATHER: Final[Wire] = Wire("mild and cloudy")
SHELF: Final[Library] = Library({"stock market": "a history"})
EMPTY: Final[Library] = Library({})

def outcome(feed: Feed, book: Encyclopedia) -> str:
    return run(supply(feed, book)(report)())

print(outcome(STOCKS, SHELF))
print(outcome(WEATHER, SHELF))
print(outcome(STOCKS, EMPTY))
print(outcome(DeadWire(), SHELF))
#: feed: fetching
#: library: looking up stock market
#: a history
#: feed: fetching
#: nothing worth researching
#: feed: fetching
#: library: looking up stock market
#: no article on that topic
#: no headline today
```

Four runs of one program, differing in what was supplied.
The first finds its article.
The second exercises `NotInteresting`, the third `NoArticle`,
and the fourth `Unavailable`, so every failure the signature declares gets used.
Each pair of bindings is what a full Effect system would call a *scenario*,
and here a scenario is nothing more than arguments to `supply()`.

The trace shows two things worth watching for.
Every printed line comes from a supplied implementation,
because the pipeline holds no output of its own.
And the second run stops after `feed: fetching`.
`topic_of()` yielded a `NotInteresting`,
which ended `research()` where it stood,
so the `need(Encyclopedia)` two lines below it never ran and no library was consulted.
`catch()` received that failure and `report()` matched on it as a value,
which is why the run still prints a message.
A failure ends the remaining steps the way a raised exception would,
and no step tested for it.
The cut moves with the failure.
The fourth run prints no trace,
since `DeadWire.latest()` raises before printing,
while the third reaches the library and fails there.

`report()` is where the two channels come apart,
and its annotation is worth reading twice.
`catch()` emptied the error channel, so `report()` cannot fail.
It still declares both abilities,
because catching an error does nothing about a dependency.
Annotate `report()` as `Success[str]` and `ty` names the `yield from` that still carries `Need[Feed] | Need[Encyclopedia]`.
`supply()` empties that half, and `run()` accepts what is left.

`outcome()` also earns its annotations.
`Wire` and `Library` are structural implementations,
so `supply(Wire(...), Library(...))` would build handlers for `Need[Wire]` and `Need[Library]`,
the mismatch `test_greeter.py` fixed with `as_type()`.
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
The name says what the by-hand version cannot avoid being:
`research()` and `report()` in one function.

Both versions short-circuit.
The by-hand one returns early, and the Effect one abandons the generator.
The difference is who writes the branch that does it.

Be fair about what this comparison shows.
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

## Adding Behavior to an Existing Effect

The previous section promised that a caller could retry a pipeline without touching it.
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

One attempt fails.
Three attempts against a database that fails twice succeed on the third,
and three attempts against one that always fails produce a `RetryError` holding every failure.
`save_user()` was not edited for any of this.

Notice that `retry()` decorates the *function*, not the Effect.
`retry(three)(save_user("Morty"))` is not available,
and the reason is the substrate.
A Stateless Effect is a generator, so it runs once and is then spent.
Re-running a spent Effect does not fail loudly:
`run()` returns `None` where the signature promised a `str`,
with no exception and no complaint from the checker.
So a second attempt has to rebuild the description from the function,
which is what `retry()` does internally.
Where ZIO attaches `retryN` to an Effect value it can replay,
Stateless attaches it one level up.

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
`Async` arrived because waiting between attempts is asynchronous,
and `run()` answers that one on its own.
And `Need[Time]` arrived, which is why `supply()` gained a `Time()`.
Retrying is not free: it needs a clock, and the signature says so.
Leave the `Time()` out and the program does not build.
This is the chapter's thesis applied to a cross-cutting concern.
Adding retry to a hundred call sites in a system with untracked Effects changes nothing you can see;
here it changes a type, and every caller learns about the new dependency.

One rough edge: `RetryError` declares an `errors` attribute that `retry()` never assigns,
so the collected failures are reachable as `outcome.args[0]` and not as `outcome.errors`.

`repeat()` is the sibling that runs an Effect on a schedule and collects every result.
`memoize()` is the one that answers the spent-generator problem head on:

```python
# memoizing.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db = Database(failures=0)
bound = supply(db)(memoize(save_user))
print(run(bound("Morty")))
print(run(bound("Morty")))
print(f"attempts: {db.attempts}")
#: attempt 1: saving Morty
#: Morty saved
#: Morty saved
#: attempts: 1
```

Two runs, one attempt, and the second run still produces the value.
`memoize()` caches by argument the way `functools.lru_cache` does,
and it wraps the Effect in an object that records the result and replays it rather than driving the spent generator again.
That wrapper exists because a generator cannot be replayed,
which is the same fact that made `retry()` decorate the function.

## Running Effects in Parallel

Effects can also run at the same time.
`fork()` hands an Effect to an `Executor` and returns a `Task`,
and `wait()` collects the result:

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
The pool is an ability, not a global,
so `squares()` declares `Need[Executor]` and names no pool.
Supplying a `ProcessPoolExecutor` instead moves the same work into processes,
with no change to `squares()`.
`as_type(Executor)` appears for the reason it always does:
`ThreadPoolExecutor` is the more specific type,
and `squares()` asked for the general one.

One restriction is worth understanding, because the checker enforces it.
A forked Effect must have nothing left to supply.
`fork()`'s four overloads accept an Effect whose ability channel holds `Never`,
an exception type, or `Async`, and nothing else,
because `fork()` runs the Effect with `run()` inside the worker.
Decorate a function that still declares a `Need` and `ty` rejects it,
listing the overloads it failed to match.
Supply first, then fork.

Notice where the pool's lifetime is managed.
The `with` block sits outside `run()`, at the edge, in ordinary Python.
Stateless has no scoping mechanism of its own,
so a resource either lives in a `with` block outside the Effect,
as the pool does here, or the ability method owns it:
the library's own `Files` ability opens and closes a file inside a single `read_file()` call.
What you cannot express is acquiring a resource in one Effect and releasing it after a later one finishes,
which is the flat resource management a native Effect system provides.

## The Toolkit in One Table

That completes the toolkit.
Every tool either builds a description, rewrites a description's type,
or executes one, and the type column is the part worth memorizing:

| Tool | Applied to | What it does to the type |
|---|---|---|
| `success(value)` | a value | wraps it as `Success[R]` |
| `need(C)` | a class | builds `Depend[Need[C], C]`, producing an instance |
| `supply(*instances)` | a function returning an Effect | subtracts each `Need[T]` matched by `isinstance()` |
| `handle(handler)` | a function returning an Effect | subtracts the ability the handler's parameter names |
| `@throws(*E)` | a function that can raise exceptions | adds each `E` to the error channel |
| `catch(*E)` | a function returning an Effect | moves each `E` from the error channel into the result |
| `retry(schedule)` | a function returning an Effect | adds `Need[Time]` and `Async`; the error becomes `RetryError[E]` |
| `repeat(schedule)` | a function returning an Effect | same additions; the result becomes a tuple of every run |
| `memoize` | a function returning an Effect | type unchanged; the result is cached by argument |
| `fork` | a function returning a supplied Effect | adds `Need[Executor]`; the result becomes `Task[R]` |
| `wait(task)` | a `Task` | adds `Async`; produces the task's `R` |
| `run(effect)` | an Effect with only `Async` and errors left | executes it; a leftover error is raised |
| `await run_async(effect)` | the same | the same, from inside a running event loop |

Everything above the last two rows transforms descriptions.
Only `run()` and `run_async()` perform work,
which is the description/execution split in table form.

## Where the Guarantee Stops

A full accounting needs the limits,
and there are five worth knowing before you commit a codebase to this.

The first is that nothing stops an undeclared Effect.
`Success[int]` promises purity, and this function breaks that promise:

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
`@throws` catches only the exception types it names,
so an unlisted exception propagates as an ordinary raised exception, untracked.
And `catch()` matches the values an Effect yields,
not exceptions the body raises,
so a failure that was never lifted by `@throws` goes past `catch()` untouched.
The channel carries only what was put into it.

The second limit is about how much of the type survives partial handling,
and it depends on your checker rather than on the library.
Handling some of what an Effect declares works correctly under `ty` 0.0.64.
Supply one of two abilities and the other stays in the signature:

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
Catch one of two declared errors and the other stays in the error channel.

What still defeats the checker is applying two handlers in one expression.
Write `handle(scripted)(handle(capture)(greet))` and `ty` gives up on the nested inference and infers `Unknown`,
which is permissive enough to hide a genuinely missing handler.
Name the intermediate and the types come back:

```python
half = handle(capture)(greet)  # () -> Depend[Ask, None]
full = handle(scripted)(half)  # () -> Success[None]
```

That is why `ask_tell_effect.py` binds `half` and `full` instead of nesting the calls.
The habit is worth keeping generally.
A named intermediate is where you read the ability that is left,
which is the information this library exists to give you.
The chapter has now met three of these checker gaps:
the nested handler expression here,
the direct ability yield that types as `Unknown`,
and the `type` alias that turns the yield check off.
Each has the same shape.
The library's types are asking the checker a hard inference question,
and where the checker gives up, it gives up quietly.
Trust a green check only where a red one has shown you it can appear.

The third limit constrains what a handler can do,
and naming the machinery precisely shows why.
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
`handle()` passes a handler the ability and takes back an answer,
and the driver resumes the Effect with that answer, once, always.
A native handler instead receives the *continuation* and chooses what to do with it.
Invoke it once and you have what Stateless has.
Decline to invoke it and the handled scope produces the handler's value instead,
which is how an exception behaves.
Invoke it repeatedly and you have backtracking and search.
Stateless offers only the first, a *tail-resumptive* handler.
The ceiling is the substrate rather than the design.
A Python generator is one-shot, so there is nothing to resume twice.

Two pieces of the library are evidence of that ceiling.
`Effect[A, E, R]` carries a separate `E`, worked by `@throws` and `catch()`.
Koka needs no such type parameter,
because an exception there is an ordinary Effect whose handler declines to resume.
The extra type parameter exists because a Stateless ability cannot fail,
and the `ZIO[R, E, A]` of [Effect Management](44_Effect_Management.md#library-effect-management)
carries one for the same reason.
`Async` is the other piece.
Native systems demonstrate asynchronous execution derived from Effects,
while Stateless provides `Async` as a built-in that `run()` interprets,
because the driver loop can await where a handler cannot.

The fourth limit is the cost.
Every effectful function becomes a generator function,
which means it cannot also be a plain function,
and calling it returns a description that somebody must run.
Type errors from a library this generic are long and mention internals.
And a third-party function that knows nothing about Effects must be wrapped in `@throws` or reached through a `need()` before it can participate.
An EMS is a decision about a whole codebase,
not a utility you import for one module.

The fifth limit is how much of a mature Effect system is present.
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
not something the type checker helps with.
Above that sit the resilience patterns a production system eventually needs,
rate limiting, bulkheads, and circuit breakers, none of which exist here.
The library is a working demonstration of Effect tracking in Python's type system,
and that is a different thing from a platform to build a distributed system on.

## Costs and Benefits

[Effect Management](44_Effect_Management.md#effects-are-the-next-barrier)
argued that Effects are the next scaling barrier,
and that the tracking will eventually move into the language.
Stateless shows what that looks like inside Python today,
which is the value of studying it, whether or not you use it in production.

Read the signatures once more, in order:

- `Success[int]`: pure.
- `Depend[Need[Console], None]`: prints, somehow,
  through something supplied later.
- `Effect[Need[Console], KeyError, None]`: prints, might not find the name.

Each one answers what a function depends on, what it can produce,
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
A function that awaits, might fail,
and holds a resource uses three of these mechanisms and returns a type that mentions one.

`Effect[A, E, R]` is one type for the dependency, the failure, and the result,
and `yield from` is one operator for joining two Effects.
`research()` joined five steps of two kinds with that one operator,
once `@throws` had brought the ordinary functions in at the boundary.
`Async` is one more ability in the same channel rather than a second viral annotation.
Resource lifetime is the concern this does not absorb.
Stateless has no scoping mechanism,
so `with` blocks stay where they are and stay nested.

What Stateless charges for that property is the generator discipline,
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
Python got one Effect tracked into its type system with `async`,
and nobody now argues that was a mistake.
The languages listed under [Native Effect Management](44_Effect_Management.md#native-effect-management)
track all of them.
Stateless is the demonstration that Python's type system is expressive enough to do it,
given a library willing to encode everything into return types.
What is missing is not the capacity.
It is a language that does the encoding for you.

## Exercises

1.  Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
    an Effect that asks for a name and greets the result.
    Supply a scripted `Console` in a test and a real one in a demo,
    and confirm `ask_and_greet()` is unchanged between them.
2.  Take `undeclared_need.py`, remove the `# type: ignore`,
    and run `ty check` on it.
    Fix the error by changing only the annotation,
    then check what `greet_all()`'s callers must now declare.
3.  Apply `reveal_type()` to `catch(ValueError)(one_left)` and run `ty check`.
    Explain why its result type differs from `all_handled()`'s,
    given that both have handled every error `parse_score()` declares.
4.  Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
    then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.
5.  `frozen` and `tomorrow` in `frozen_clock.py` each report a single moment.
    Write an advancing handler for `Now` that reports a moment one hour later at each request,
    then write an Effect that asks the time twice and returns the elapsed `timedelta`.
    Say which of `coin_toss.py`'s two handlers yours resembles,
    and why neither `frozen` nor `tomorrow` can test elapsed-time logic.
6.  `leaky_effect.py` type-checks while lying about its purity.
    Describe a review rule or a lint check that would catch it,
    and explain why a type checker cannot.
    Then demonstrate the error-side twin:
    write a function that raises a `KeyError` with no `@throws`,
    wrap it in `catch(KeyError)`, and run it on a failing input.
    Explain what the types claim, what the run does,
    and which line restores the guarantee.
7.  Add a `Metal` material to `test_nailer.py` with a brittleness that survives the robotic nailer,
    and add its two rows to the table.
    Then explain why the test function body needed no change.
8.  Add a fourth failure to `research()`:
    a `TooLong` raised when an article exceeds some length.
    Follow the checker's complaints until the program builds again,
    and list every line you had to edit.
    Then do the same to `research_by_hand.py` and say which tool told you where to go in each case.
9.  `scenarios.py` supplies a `DeadWire` that fails before printing.
    Write a `SlowWire` whose `latest()` succeeds but returns a headline with no topic in `TOPICS`,
    and predict the trace before running it.
10. Wrap `research()` in `retry()` and supply a `Time()`.
    Explain what happens under the `WEATHER` scenario and why retrying a `NotInteresting` failure is the wrong behavior,
    then say what an Effect system would need for you to retry only `Unavailable`.
11. Change `parallel.py` to use a `ProcessPoolExecutor` instead of a `ThreadPoolExecutor`,
    and confirm `squares()` is unchanged.
    Then try to fork an Effect that still declares a `Need`,
    and record what `ty` says.
12. Break `greet_all.py` by removing the `yield from` in front of `greet(name)`.
    Run `ty check`, `ruff check`, and the script,
    and record what each reports and what the program prints.
    Explain where the greetings went and why no tool objects.
    Then explain why the same mistake in front of `need(Console)` inside `greet()` would be caught,
    and by what.
