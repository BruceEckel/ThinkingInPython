# Stateless

> The easiest things to forget about a function are what it needs from outside and how it can fail.
> Stateless writes both into the function's type,
> and the type checker verifies every caller against them.

[Effect Management](44_Effects--Effect_Management.md#library-effect-management)
introduces library Effect systems.
[Stateless](https://github.com/suned/stateless)
implements an Effect Management System (EMS).

Stateless encodes an Effect's dependencies and failures into the return type of a function.
A type checker then verifies that every caller either handles each Effect or declares it in its own signature.
If you forget to declare a dependency, the check fails.
If you forget to supply one, the check fails.
Those two checks are the Effect tracking and delayed binding of a full EMS.
In Stateless, the type checker performs both.

Stateless builds on generators.
[Generators](45_Effects--Generators.md)
covers the three-parameter `Generator` annotation,
a driver that answers a generator's requests one `send()` at a time,
and `yield from`, which composes generators and produces the inner generator's return value.
Every Effect in this chapter is such a generator.
Stateless supplies the vocabulary for the requests and the driver that answers them.

An Effect's return type declares two things:
the dependencies it needs and the ways it can fail.
Both travel the yield channel every generator carries.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md)
builds examples with both.

My understanding of Effects came from work with Bill Frasure and James Ward as we created [Effect Oriented Programming](https://effectorientedprogramming.com/).
Some of the examples in these two chapters derive from that book.

## The Effect Type

Stateless builds everything atop a single type with three type parameters:

```python
Effect[A, E, R]
```

Those three parameters answer the three questions [Effect Management](44_Effects--Effect_Management.md#library-effect-management)
asked of an Effect signature:

- `A` is what the computation needs, an *Ability*.
- `E` is how it can fail.
- `R` is what it produces.

Stateless reuses the word Effect for the whole description a function returns.
The Effects of [Effect Management](44_Effects--Effect_Management.md#what-is-an-effect)
are what that description declares:
its Abilities in `A` and its failures in `E`.

For example:

```python
Effect[Need[Console], KeyError, None]
```

This Effect needs a `Console`, can fail with a `KeyError`, and produces `None`.
The first parameter is `Need[Console]` rather than `Console`.
The Effect asks for a console, and a later `supply()` call provides one.
[Nothing Runs Yet](#nothing-runs-yet)
explains why that request must be a value of its own.

Although you can write the full `Effect` signature each time,
the library provides three aliases for the most common cases.
Each one fills in `Never` for the type parameters it leaves out:

| Alias | Meaning |
|---|---|
| `Success[R]` | Needs nothing, cannot fail, produces `R` |
| `Depend[A, R]` | Needs `A`, cannot fail, produces `R` |
| `Try[E, R]` | Needs nothing, can fail with `E`, produces `R` |

`Never` is Python's *bottom type*:
it has no values and is a subtype of every other type.

## The Simplest Effect

`success()` wraps a value in an Effect, and `run()` executes it:

```python
# simplest_effect.py
from stateless import Success, run, success

def double(n: int) -> Success[int]:
    return success(n * 2)

print(run(double(21)))
#: 42
```

`run()` is the Stateless library's driver,
similar to [`drive()`](45_Effects--Generators.md#a-generator-is-a-description).
`run()` primes the generator, drives it to completion, and returns the result.
The work the Effect describes waits for a call to `run()`.
A synchronous program calls it once, at the outermost edge.

`success()` and `Success` differ only in case.
`success()` is a function that builds an Effect.
`Success` is the alias from the table, the type of that Effect.
`Success[int]` says `double()` is pure.
`double()` cannot read anything, and it cannot fail.

`double()` contains no `yield`, so it is an ordinary function.
Python decides generator-function status from the body alone.
A `yield` in the body makes a function a generator function,
whatever the return annotation says and whatever object the body returns.
`double()` calls `success()` and returns the Effect that `success()` builds,
the way an ordinary function returns a list.
The annotation describes that returned object rather than how the body reads.
The Effect implements the generator protocol,
and `run()` drives any object that implements that protocol.

`success()` returns a `SuccessEffect`,
a small class that implements that protocol with its own `send()` and `throw()` methods.
Its `send()` raises `StopIteration` carrying the value,
so `run()` gets the result on its first step.

`success()` exists for yield-free functions like `double()`.
In a generator function, `return value` sets the Effect's `R`.
`return success(value)` there produces a `Success[R]` where the signature expects an `R`,
so the type checker rejects it.

`double()` takes everything it uses as its argument,
so its Effect type has no dependency to declare.
An Effect type declares one when a function uses an object created elsewhere,
such as a console, a file, or a network connection.

## Declaring a Dependency

`Need` is how Stateless does dependency injection.
A `Need` is a request for an instance,
and code outside the requesting function answers it.
`need(SomeClass)` is an Effect that produces an instance of `SomeClass` and leaves open what supplies that instance:

```python
# utils/greeter.py
from stateless import Depend, Need, need

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")
```

`greeter.py` lives in `utils/` because both this chapter and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
import it.
This chapter builds its own `Console` rather than using the one Stateless provides.
[Built-in Dependencies](#builtin-dependencies), below, says why.

Compare `greeter.py`'s `greet()` to the version that calls the built-in `print()`:

```python
# untyped_greet.py
def greet(name: str) -> None:
    print(f"Hello, {name}!")
```

That signature is incomplete.
`-> None` describes the return value.
The body also writes to standard output, a side effect the signature leaves out.
A caller must capture stdout to redirect the output or to test the function.

`Depend[Need[Console], None]` states the dependency.
A caller now has two options: supply a `Console`,
or declare the same need in its own signature and pass the Ability to its own caller.
A caller that does neither fails the type check.

Two details in `greeter.py` matter:

1. `greet()` is a generator function, because it contains `yield from`,
   so calling it builds the Effect its signature declares.
2. `console` is of type `Console`,
   so the type checker verifies each `console.print()` call against `Console.print()`'s signature.
   `console` has that type before anything supplies an instance.

### The Effect Definition

The first detail holds for every Effect,
because `Effect` is an alias for a `Generator`:

```python
Effect: TypeAlias = Generator[A | E, Any, R]
```

The `Generator` yields either an Ability `A` or an exception `E`,
and eventually returns a result `R`.
The `Effect[Need[Console], KeyError, None]` from [The Effect Type](#the-effect-type)
becomes:

```python
Generator[Need[Console] | KeyError, Any, None]
```

`A` and `E` share the first type parameter.
`R` is the third.
The union lists requests and failures alike.
Two bounds on the library's type variables tell them apart.
`A`'s bound is `Ability[Any]`, and `E`'s bound is `Exception`.
[Waiting on a Coroutine](#waiting-on-a-coroutine)
states the `A` bound as the rule for `Depend`.

At runtime, `run()`'s driver tells a request from a failure with `case Exception() as error`.
A yielded value that matches `Exception` is a failure.
Everything else is an Ability request.
The two bounds overlap.
A class that subclasses both satisfies each at once,
and at runtime it counts as a failure.
No listing here builds one.

The second type parameter is `Any`,
which [Generators](45_Effects--Generators.md#annotating-a-generator)
taught you to read as the type the `yield` expression produces inside the generator.
That `Any` is deliberate, and it decides how `greet()` must write its request.

### Why `yield from`

The request in `greet()` reads `console = yield from need(Console)`,
not `console = yield Need(Console)`.
The reason is that `Any`.

A generator has one SendType for its whole life.
An Effect needs a different answer for each request:

- A `yield` that requests a `Need[Console]` should get back a `Console`.
- A `yield` that requests a `Need[Log]` should get back a `Log`.

What comes back depends on which Ability the `yield` requested.
One SendType covers every `yield`.
If you pin it to `Console`,
the type checker reads `yield Need(Log)` as producing a `Console`.
So the SendType is `Any`, which accepts every answer unchecked.

A bare `yield` produces that SendType, `Any`.
`yield from` produces the inner generator's `ReturnType`,
so the type checker knows the answer's type.
`need(Console)` builds a small generator that serves one request,
so its `ReturnType` can be a specific type.
`need()` returns `Depend[Need[T], T]`,
which expands to `Generator[Need[T], Any, T]`.
Calling `need(Console)` binds `T` to `Console`,
so `console` takes its type from that `ReturnType`,
not from the `Any` in the SendType.

For that reason every request in this chapter uses `yield from` rather than `yield`,
and the custom Abilities of [Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
get a small function of their own.

## Built-in Dependencies {#builtin-dependencies}

The `Console` in `greeter.py` is one this chapter defines.
Stateless also provides three dependencies of its own:

- `Console` in `stateless.console`,
  whose `print_line()` and `read_line()` *accessors* call its `print()` and `input()` methods
  (an accessor is a small function that wraps one request and declares its answer type),
- `Files` in `stateless.files` that reads a whole file,
- `Time` in `stateless.time`,
  which [Adding Behavior to an Existing Effect](47_Effects--Stateless_in_Practice.md#adding-behavior-to-an-existing-effect)
  supplies to `retry()`.

All three are concrete classes rather than interfaces.
Being concrete means [a test double for one of them must inherit from it](#supplying-an-interface).

The `read_file()` accessor in `stateless.files` is also the library's own example of both channels at once.
It carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect,
so its type declares an Ability and two failures together.
[The Error Channel](#the-error-channel) introduces that decorator.

This chapter builds a `Console` of its own for illustration rather than using `stateless.console`.
In your own code, first check what the library declares.

## Nothing Runs Yet

Calling `greet()` performs no work.
It returns a `Generator`:

```python
# describe_only.py
from greeter import greet

print(type(greet("Alice")))
#: <class 'generator'>
```

`greet("Alice")` builds a description of a greeting.
This is the [description/execution split](44_Effects--Effect_Management.md#library-effect-management).
A language with built-in Effects intercepts an Effect where it runs.
Stateless is ordinary Python,
so a function body's `console.print()` calls the method,
and no library code runs in between.
A library acts only on objects handed to it,
so the request for a `Console` must be an object the function hands out.
Driving `greet()` with `next()` and `send()` shows that object,
the way [Generators](45_Effects--Generators.md#annotating-a-generator)
drove `interview()`:

```python
# hand_driven.py
from greeter import Console, greet

description = greet("Alice")
request = next(description)
print(f"{type(request).__name__}, {request.t.__name__}")
#: Need, Console
try:
    description.send(Console())
except StopIteration:
    print("greet() finished")
#: Hello, Alice!
#: greet() finished
```

`need(Console)` builds a small generator that yields a `Need[Console]`,
a frozen data class whose `t` field holds the requested class.
`yield from` passes that `Need` out of `greet()`'s body.
The greeting has yet to print at that point,
because `greet()` has suspended inside `need()`,
at the `yield` its `yield from` reaches.

## Supplying the Dependency

`supply()` provides an instance to the `Need` that asked for it:

```python
# supply_console.py
from greeter import Console, greet
from stateless import run, supply

bound = supply(Console())(greet)
run(bound("Alice"))
#: Hello, Alice!
```

Those two lines do three things:

1. `supply(Console())` builds a [handler](44_Effects--Effect_Management.md#native-effect-management),
   an object that answers `Need[Console]` with that instance.
2. Calling the handler on `greet` returns a new function `bound` that answers the requests `greet()` makes.
3. Calling that function with `"Alice"` builds a fully supplied Effect,
   which `run()` then executes.

Supplying the `Console` changes the type:

```python
# reveal_bound.py
from typing import reveal_type
from greeter import Console, greet
from stateless import supply

bound = supply(Console())(greet)

if __name__ == "__main__":
    reveal_type(greet)
    reveal_type(bound)
```

`reveal_type()` is a message to the type checker.
At runtime it prints only the class of its argument (`function`, here)
to standard error, so the answer comes from `ty check reveal_bound.py`:

```text
info[revealed-type]: Revealed type
 --> reveal_bound.py:9:17
  |
9 |     reveal_type(greet)
  |                 ^^^^^ `def greet(name: str) ->
  |                       Generator[Need[Console], Any, None]`

info[revealed-type]: Revealed type
  --> reveal_bound.py:10:17
   |
10 |     reveal_type(bound)
   |                 ^^^^^ `(name: str) -> Generator[Never, Any, None]`
```

`ty` shows `greet` as a `def` with its name.
`bound` is a function that `supply()` built,
so `ty` shows its signature with no name.
The two revealed types are the expanded forms of `Depend[Need[Console], None]` and `Success[None]`.
`Need[Console]` sits in the first type parameter of `greet` and disappears from `bound`,
leaving the `Never` from the alias table.

Handling an Ability *subtracts* it from the type.
Here the subtraction empties the Ability channel.
`greet()` declares one Ability and cannot fail, so `bound` produces a `Success`.
That `Success` follows from `greet()`'s signature rather than from anything `run()` requires.
`run()`'s parameter type rejects every unanswered Ability except `Async`.
`run()` accepts an Effect that can still fail,
and [raises the failure as an ordinary exception](#the-error-channel).
Binding an implementation and satisfying the type checker are the same act.

## Layering Handlers

A handler answers the Abilities `supply()` gave it and re-yields the rest to the next handler out.
A second `supply()` wrapped around the first answers what the inner one re-yielded.

A dependency injection container often lets you register a fallback for a type nobody else provides.
Stateless has no such registration, and `need()` takes no default argument.
Layering handlers produces the fallback.
Here, `Console` carries a tag so the output says which handler answered:

```python
# default_console.py
from record import record
from stateless import Depend, Need, need, run, supply

@record
class Console:
    tag: str
    def print(self, message: str) -> None:
        print(f"[{self.tag}] {message}")

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

fallback = supply(Console("default"))
run(fallback(greet)("Alice"))
#: [default] Hello, Alice!
chosen = supply(Console("chosen"))(greet)
run(fallback(chosen)("Bob"))
#: [chosen] Hello, Bob!
```

`fallback` is an ordinary handler, applied at the edge.
The second run wraps `greet()` in its own `supply()` first,
and that inner `supply()` empties the Ability channel before any request reaches `fallback`.
The handler nearest the Effect answers first,
and the outer one handles the requests that remain.
The type records which handler answered.
`chosen` is already `(str) -> Success[None]`,
so `fallback(chosen)` keeps that type.

A function declares its `Need` so the type checker reports a missing binding.
A default removes that check.
An Effect missing its `Console` now passes the type check and runs.
A forgotten binding then shows up as the default `Console`'s output rather than as an error.
Use a fallback for a genuine default, a null logger or a no-op console,
not to silence a type error that reports a missing binding.

## An Effect Runs Once

A description you can hold as a value looks like one you can run twice.
In Stateless you cannot, because that description is a generator,
and driving a generator consumes it:

```python
# effect_runs_once.py
from greeter import Console, greet
from stateless import run, success, supply

bound = supply(Console())(greet)
description = bound("Alice")
run(description)  # [1]
#: Hello, Alice!
print(repr(run(description)))  # [2]
#: None
run(bound("Bob"))
#: Hello, Bob!
constant = success(42)
print(run(constant), run(constant))
#: 42 42
```

The `run()` at `[1]` exhausts the generator.
The `run()` at `[2]` drives that same exhausted object and gets an immediate `StopIteration` whose value is `None`.
Calling `bound("Bob")` builds a fresh description, and that one runs.
A second `bound("Alice")` builds a fresh one too.

An Effect from `success()` can run more than once,
because `success()` builds no generator.
A `SuccessEffect`'s `send()` reports the value every time,
so a constant Effect replays.

Here Stateless differs from Effect systems in other languages.
A ZIO or Effect-TS value is an immutable description that you can interpret as often as you like,
so their combinators are operations on that value.
ZIO writes `action repeat policy`, repeating the effect the value describes.
Stateless has `repeat()` and `retry()` too,
but each takes a schedule and returns a decorator of type `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`.
They decorate the function,
because the function can produce a second description.
`catch()`, `throws()`,
and `supply()` return decorators over functions for the same reason.

<!-- The "---" below is the author's own em-dash. Leave it. House.EmDash
     exists to catch em-dashes the author did not write. -->
<!-- vale House.EmDash = NO -->
So pass the function rather than the Effect.
A Stateless Effect runs once: build it, run it, discard it.
Storing one in a registry to run later, handing the same one to two consumers,
or keeping one around to retry after a failure---each of these returns `None` on the second run instead of raising an exception.
Other Effect systems let you describe the work once and decide later how many times to perform it.
In Stateless, that decision belongs to whoever still holds the function.
<!-- vale House.EmDash = YES -->

`memoize()` is the one decorator that gives a second `run()` a result,
and it caches rather than replays.
It wraps the Effect in an object that records the result and hands that same result back on a second `run()`.
Like `repeat()` and `retry()`, `memoize()` decorates the function.
[`repeat()` and `memoize()`](47_Effects--Stateless_in_Practice.md#repeat-and-memoize)
shows it in use.

## Forgetting to Supply

Give `run()` an Effect that still needs a `Console`:

```python
# unsupplied.py
from exceptions import expected
from greeter import greet
from stateless import run
from stateless.errors import MissingAbilityError

with expected(MissingAbilityError):
    run(greet("Alice"))  # type: ignore
#: [MissingAbilityError] Need(t=<class 'greeter.Console'>)
```

If you remove the `# type: ignore`, `ty` rejects the program before it runs:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
 --> unsupplied.py:8:9
  |
8 |     run(greet("Alice"))
  |         ^^^^^^^^^^^^^^ Expected
  |         `Generator[Async | Exception, Any, Unknown]`, found
  |         `Generator[Need[Console], Any, None]`
```

In Stateless, an unsupplied dependency is a type error,
not a production incident.
The type checker finds the omission,
so you need no test that exercises the path and no reviewer who happens to notice it.

The expected type in that message names `Async` and `Exception`:

- `Async` is a built-in [Ability for asynchronous work](#waiting-on-a-coroutine),
  which `run()` handles on its own.
- `Exception` is the error channel,
  the subject of [The Error Channel](#the-error-channel)
  and everything after it.

`run()` accepts an Effect whose yield channel has narrowed to those two,
which is all that remains once you supply every other Ability.
`greet("Alice")` still has `Need[Console]`, so it fails type checking.

## Swapping the Implementation

`Need` creates a delayed binding,
so different runs can bind different implementations.
For example, a test can bind to a `Console` that records instead of printing:

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

The test captures nothing from stdout and mocks nothing.
It supplies a different `Console`.
`greet()` stays as written,
since its body names `Console` and leaves the choice of implementation to `supply()`.
`supply()` answers every matching request in the Effect's run with the same instance,
so the test reads the messages back out of `recorder` afterward.

`as_type(Console)` is the only extra call in that test.
It says "treat this recorder as a `Console`,"
and at runtime it returns the object it received.
`supply()` requires `as_type()` because it reads the Ability from the static type of its argument.
At runtime, `supply()` matches the request with `isinstance()`,
which accepts `recorder` because `Recorder` derives from `Console`.
[Supplying an Interface](#supplying-an-interface) explains both halves,
along with what changes when the Ability is an interface rather than a class.

## Effects Propagate, and the Type Checker Verifies It

A function that calls an effectful function becomes effectful.
`greet_all()` must declare the `Console` even though no `Console` appears in its body:

```python
# greet_all.py
from stateless import Depend, Need, need, run, supply

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_all(
    names: list[str]
) -> Depend[Need[Console], None]:
    for name in names:
        yield from greet(name)

if __name__ == "__main__":
    run(supply(Console())(greet_all)(["Alice", "Bob"]))
#: Hello, Alice!
#: Hello, Bob!
```

The listing repeats `Console` and `greet()` rather than importing them from `greeter.py`,
so one listing holds every function between the request and `supply()`.

Effects propagate the way `async` does.
An `async` function's callers must also be `async`,
all the way to `asyncio.run()`.
A `Depend` function's callers must also declare the Ability,
all the way to `supply()`.
The difference is that you can declare as many Abilities as you like.

The `yield from` inside `greet_all()` relays `greet(name)`'s request to the driver.
If you write that loop body as a bare `greet(name)`,
`ty` reports an `invalid-return-type`:
"Function always implicitly returns `None`."
That looks like protection, but it is an accident.
That `yield from` is the only `yield` in `greet_all()`,
so deleting it turns `greet_all()` into an ordinary function.
The type checker reports the changed shape rather than the discarded Effect.

A function with a second `yield` stays a generator function after the deletion.
`greet_logged()` in [Retrofitting an Effect](#retrofitting-an-effect)
makes two requests, one for the greeting and one for the log.
If you write its first line as a bare `greet(name)`, every check passes.
The type checker and `ruff` accept the code, the program runs,
the log gains both entries, and no greeting prints.
The call still builds a description, and the body discards it unrun.

ZIO allows the same mistake for the same reason.
An Effect written as a bare statement is a discarded value there too.
In ZIO Direct the fix is `.run`,
and in a `for` comprehension it is the `<-` binding.
In Python it is `yield from`.
The description/execution split causes the hazard, not generators.
When an Effect appears to do nothing, look for a missing `yield from`.

You declare the Ability in the annotation,
and the type checker verifies the declaration.
If you annotate `greet_all()` as pure, the checker reports the mismatch:

```python
# undeclared_need.py
from greet_all import greet
from stateless import Success

def greet_all(names: list[str]) -> Success[None]:
    for name in names:
        yield from greet(name)  # type: ignore
```

If you remove the `# type: ignore`, `ty` reports:

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

An annotation cannot declare a function pure while its body yields from an impure one.
Compare that to `ask_tell.py` in [Effect Management](44_Effects--Effect_Management.md#effects-by-hand),
where `greet(ask, tell)` takes its dependencies as arguments.
There, an intermediate function is free to construct its own `Console` and perform an Effect,
with every signature and every check silent about it.
Here, the signature and the body must agree.

## Retrofitting an Effect

The second exercise in [Effect Management](44_Effects--Effect_Management.md#exercises)
has you add a `Log` Effect alongside `greet()` and count how many of the edited signatures use it.
Here is that exercise in Stateless:

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

if __name__ == "__main__":
    log = Log()
    run(supply(Console(), log)(greet_all)(["Alice", "Bob"]))
    print(log.entries)
#: Hello, Alice!
#: Hello, Bob!
#: ['greeted Alice', 'greeted Bob']
```

The new Effect is the `Log` write inside `greet_logged()`.
Every function on the path to it gains a `Need[Log]`,
here `greet_logged()` and its caller `greet_all()`,
while `greet()` keeps its signature.

Stateless still requires those edits.
The type checker names each place that needs changing,
and the check passes once you have fixed the last one.
To see that, delete `| Need[Log]` from either annotation.
If you remove it from `greet_all()`,
`ty` reports an `invalid-yield` at `yield from greet_logged(name)`,
since that `yield from` produces a `Need[Log]` and the signature now declares `Need[Console]` alone.

The type checker covers dependencies passed as parameters too.
If you forget the new argument at a call, `ty` reports a `missing-argument`.
The difference is how many places you edit.
A new parameter changes every call site along with every signature,
and each function in between accepts the object and hands it onward.
A new Ability changes the signatures alone.
`yield from greet_logged(name)` stays as it is.
The instance appears once, at `supply()`.

Multiple Abilities combine with `|` because the union describes one request at a time.
Each `yield` in `greet_all()` produces either a `Need[Console]` or a `Need[Log]`.
Over the whole run, `greet_all()` makes both kinds of request,
so `supply()` must provide a `Console` and a `Log`.

`supply()` can also provide them one layer at a time.
`supply(Log())(greet_all)` still has the type `(list[str]) -> Depend[Need[Console], None]`,
and wrapping that in `supply(Console())` leaves `(list[str]) -> Success[None]`.
You can bind some Abilities near the Effect and the others at the edge.
The type records which Abilities each layer leaves open.

The repeated union is the shape a `type` alias normally shortens.
Elsewhere the book writes one.
Under `ty` 0.0.91 the alias checks the same as the written-out signature.
An undeclared Ability behind `type Greeting = Depend[...]` draws the same `invalid-yield`.
This book still writes Effect signatures out in full,
because the union is the information.
Every channel a function uses stays visible at the point of use.
Before you shorten one with an alias,
confirm that your type checker reports an undeclared Ability through it.

## One Effect, Many Environments

`audit_log.py` supplies two Abilities at one call site.
A test suite usually needs many such call sites, one per environment.
Because dependencies live in the return type rather than the argument list,
varying the environment means varying data:

```python
# nailer.py
from record import record
from stateless import Depend, Need, need

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
```

`Material` and `Nailer` are distinct types,
so `supply()` matches each request to one of them.
[When Two Implementations Match](#when-two-implementations-match)
covers the case where two supplied objects fit one Ability.
Here the test varies both the `Material` and the `Nailer`:

```python
# test_nailer.py
from typing import Final
import pytest
from nailer import Material, Nailer, holds
from stateless import run, supply

WOOD: Final[Material] = Material(strength=5)
PLASTIC: Final[Material] = Material(strength=10)
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
    assert run(
        supply(material, nailer)(holds)()) is expected
```

One test function covers four environments.
`supply()` binds `material` and `nailer`,
so the table reads as a matrix of environments rather than a list of arguments.
A new `Material` adds one row for each nailer.

Dependencies as parameters serve this test as well,
because `holds(material, nailer)` is easy to call four times.
The two styles differ when a function three calls deep requests the dependency.
The parameter version then adds two parameters to every function on the path.
This version changes the table row alone.
`audit_log.py`'s `greet_all()` is that depth.
The test calls `greet_all()`, `greet_all()` calls `greet_logged()`,
and `greet_logged()` requests `Need[Log]` and calls `greet()`,
which requests `Need[Console]`.
Varying the environment there again touches the table row alone:

```python
# test_audit_log.py
import pytest
from audit_log import Log, greet_all
from greeter import Console
from recorder import Recorder
from stateless import as_type, run, supply

@pytest.mark.parametrize("console", [
    Console(), as_type(Console)(Recorder())])
def test_greet_all(console: Console) -> None:
    log = Log()
    run(supply(console, log)(greet_all)(["Alice"]))
    assert log.entries == ["greeted Alice"]
```

`greet_all()` and `greet_logged()` keep their parameter lists.
The parameter-passed version adds a `console` argument to both,
although `greet()`, one level further down, is the one function that uses it.

## Supplying an Interface

[Swapping the Implementation](#swapping-the-implementation)
substitutes a `Recorder` for a `Console` but postpones the reason for using `as_type(Console)`.
The substitution poses two questions,
one for the type checker and one for the runtime check.

### What the Type Checker Reads

`supply()` reads the Ability from the declared type of its argument.
Handing `recorder` to `supply()` therefore builds a handler for `Need[Recorder]`,
a different Ability from the `Need[Console]` that `greet()` requests.
`as_type(Console)(recorder)` converts the argument's static type into `Console`,
so `supply()` builds the handler type `greet()` needs.

At runtime `as_type(Console)` returns an identity function,
which hands back the object it receives.
Only the static type changes.

`typing.cast(Console, recorder)` produces the same static type,
but the two differ in what they check.
`cast()` is an unchecked assertion.
The type checker accepts it whatever the object's type.
`as_type(Console)` returns a function annotated `(Console) -> Console`,
so the type checker verifies that the object it receives is a `Console`.
`as_type()` widens to a supertype.
`cast()` replaces one type with any other.

### What `isinstance()` Checks

The library decides the runtime question with `isinstance()`.
`supply()` builds a handler that checks each request with `isinstance(instance, ability.t)`,
where `ability.t` is the class inside the `Need`.
In `test_greeter.py`, `ability.t` is `Console` and `instance` is `recorder`.
`isinstance(recorder, Console)` succeeds because `Recorder` inherits from `Console`.
So two separate things make that test work:
`as_type(Console)` satisfies the type checker,
and the inheritance satisfies the runtime check.

Through the inheritance,
`Recorder` also receives every method `Console` gains later.
`Recorder` overrides everything it inherits from `Console`,
so today the parent contributes only the name `isinstance()` matches.
If you add a `read_line()` method to `Console` tomorrow,
`Recorder` inherits the real one,
and a test meant to record performs live console I/O.
No check reports it.

### An Interface Instead of a Base Class

Stateless's own `Console` is the concrete class [Built-in Dependencies](#builtin-dependencies)
lists.
Only a subclass can replace it.
Its accessors request that class with `need(Console)`,
so `isinstance()` accepts an instance of the class or a subclass.
A structurally identical double fails twice.
`as_type(Console)` rejects it,
because the type checker compares a concrete class by name.
If a `cast()` forces the static type,
the run fails with a `MissingAbilityError`.
A double for the built-in `Console` must therefore inherit from it.

The built-in `Console` implements `input()` as well as `print()`,
so a double that overrides `print()` and inherits `input()` reads live stdin.
An interface has no implementation to inherit by accident:

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

A full EMS does [three things](44_Effects--Effect_Management.md#tracking-and-management),
and the second is to separate each Effect's interface from its implementation.
`Console` as a `Protocol` holds no implementation.
`Terminal` is one implementation and `Recorder` is another.
`greet()` refers to neither.
`Recorder` qualifies as a `Console` without inheriting from `Console`,
because a `Protocol` matches on structure.

`supply()` matches requests with `isinstance()`.
`isinstance()` accepts a `Protocol` marked `@runtime_checkable` and raises a `TypeError` on any other,
so the Protocol carries that decorator.

You still need `as_type()`.
Here, `supply()` receives a `Terminal` both ways, bare and through `as_type()`:

```python
# protocol_supply.py
from console_protocol import Console, Terminal, greet
from stateless import as_type, run, supply

run(supply(Terminal())(greet)("Alice"))  # type: ignore
#: Hello, Alice!
run(supply(as_type(Console)(Terminal()))(greet)("Bob"))
#: Hello, Bob!
```

Both lines print, because `isinstance()` accepts a `Terminal` as a `Console` by structure.
If you remove the `# type: ignore`, `ty` rejects the first one:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
 --> protocol_supply.py:5:5
  |
5 | run(supply(Terminal())(greet)("Alice"))
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Expected
  |     `Generator[Async | Exception, Any, Unknown]`, found
  |     `Generator[Need[Console], Any, None]`
```

Structural matching decides what `isinstance()` accepts,
not what the type checker accepts.
`supply(Terminal())` still builds a handler for `Need[Terminal]`,
which leaves `greet()`'s `Need[Console]` in place.
The unhandled request stays in the type that reaches `run()`.
That call is the line the type checker reports.
An interface needs the `as_type()` upcast more than a base class does.
You can instantiate a concrete `Console` and supply it with no upcast,
but an interface reaches `supply()` only through an implementation.

`console_protocol.py` is the form to write in production.
Most listings in these two chapters use a concrete `Console`,
because an interface adds an `as_type()` call wherever an implementation goes straight to `supply()`.
[Composing a Program](47_Effects--Stateless_in_Practice.md#composing-a-program)
declares its dependencies as `Protocol`s and shows the annotation that replaces that call.

Write one boundary function whose parameter annotations specify the interface types,
and call `supply()` inside it.
The parameter annotation upcasts the argument,
so every call site passes its implementation bare.
The functions between that boundary and the Effect keep the same signatures whether the Ability is a `Protocol` or a concrete class.
An annotated local variable is different.
`screen: Console = Terminal()` narrows back to `Terminal` at the assignment,
so `supply(screen)` builds a `Need[Terminal]` handler again.

## When Two Implementations Match

A structural check matches on method names alone,
so two supplied objects that both define `print()` are indistinguishable.
If you supply both, argument order decides which one answers the request:

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

screen = as_type(Console)(Terminal())
capture = Capture()
memory = as_type(Console)(capture)
run(supply(screen, memory)(greet)("Alice"))
#: Hello, Alice!
print(capture.messages)
#: []
run(supply(memory, screen)(greet)("Bob"))
print(capture.messages)
#: ['Hello, Bob!']
```

`Terminal` and `Capture` share no base class, and neither names the other.
Both satisfy `Console` structurally, so `isinstance()` accepts either.
`supply()` hands over whichever it examines first.
`greet()` runs the same body in both runs.
The type checker accepts both runs alike,
because both bindings have the same type.
Both instances go through `as_type(Console)`,
since each is a `Console` by structure alone.

Here Stateless lacks a check ZIO performs.
ZIO reports two implementations of one requirement as a compile-time error naming both candidates,
because its `provide` resolves the dependency graph during compilation.
`supply()` resolves at runtime by scanning its arguments,
so the same mistake produces a program that runs and hands each request to whichever instance comes first in the argument list.
Give Abilities distinct method names when that ambiguity is possible,
and supply one implementation per Ability.

## Dependency Injection

Dependency injection (DI) has one goal:
separate a function from the choice of what it uses.
A function that constructs its own `Console` can use only that class,
while a function handed a `Console` can receive a recorder in a test,
a terminal in production, and a scripted one in a demo.

Conventional DI meets that goal with a container.
The container maps each type to the instance that satisfies it,
and hands those instances out during execution:

```python
# dependency_injection.py
from typing import Any, Final
from exceptions import expect
from greeter import Console

class NotRegistered(Exception):
    pass

DI_CONTAINER: Final[dict[type, Any]] = {}

def register[T](t: type[T], instance: T) -> None:
    DI_CONTAINER[t] = instance

def get[T](t: type[T]) -> T:
    try:
        return DI_CONTAINER[t]
    except KeyError as e:
        raise NotRegistered(t.__name__) from e

def greet(name: str) -> None:
    console: Console = get(Console)
    console.print(f"Hello, {name}!")

expect(NotRegistered, greet, "Alice")  # [1]
#: [NotRegistered] Console
register(Console, Console())
greet("Alice")  # [2]
#: Hello, Alice!
```

The type is the registration key,
so `register(Console, Recorder())` binds an implementation to the type the caller requests.
A dictionary matches the key exactly,
so `get(Console)` never returns a subclass registered under its own name.
`supply()` takes bare instances and matches a request with `isinstance()`,
so two instances that satisfy one `Need` are [ambiguous](#when-two-implementations-match).

The DI registration key also sets the type an instance answers for,
as `as_type(Console)` does for `supply()`.
`supply()` [reads each Ability from its argument's static type](#supplying-an-interface),
so `supply(recorder)` is a `Handler[Need[Recorder]]`,
and no `Need[Console]` matches it.

`DI_CONTAINER` holds instances of unrelated types.
A `dict` gives every value the same type.
The key carries the type information.
With `object` as the value type,
the type checker rejects `get()`'s `return DI_CONTAINER[t]`,
because an `object` is not a `T`.
`Any` passes as a `T`, so the values are `Any`.
`register()`'s signature therefore states the invariant the container's type cannot:
the value under key `type[T]` is a `T`.

`greet()`'s body matches `greeter.py`'s `greet()` line for line,
apart from `console: Console = get(Console)` in place of `console = yield from need(Console)`.
Its signature matches the `untyped_greet.py` version in [Declaring a Dependency](#declaring-a-dependency).
Both read `(str) -> None`, and neither names the `Console` it uses.

The `greet("Alice")` call at `[1]` fails at runtime because it runs before `register()` binds a `Console`.
The second, at `[2]`, succeeds because the binding now exists.
The two calls are identical, and registration sits outside the types,
so the type checker accepts both.

DI meets its goal.
The `Console` is swappable.
But DI relocates a [side cause](44_Effects--Effect_Management.md#what-is-an-effect)
rather than declaring one, so the type checker does not validate the dependency.

`dependency_injection.py` demonstrates one shape of DI, a service locator:
a body reads the container with `get(Console)`.
Constructor injection is the stronger, more common shape,
and frameworks such as FastAPI's `Depends` build on it.
Constructor injection answers the complaint that the type checker does not validate the dependency.
The dependency arrives as a parameter,
so a static type checker validates every call that supplies one.
You bind the dependency once, at the endpoint or the constructor.
Every function that boundary calls passes the dependency onward as a parameter,
the same parameter an EMS replaces with a channel in the return type.

An EMS requires more than the service locator does.
The dependency must appear in the signature so the type checker can verify it.
That is why the EMS `greet()` returns `Depend[Need[Console], None]` while `dependency_injection.py`'s `greet()` returns `None`.
An EMS tracks every dependency,
so the type checker reports errors that a programmer's memory or an exhaustive test suite must otherwise find.

### No Container, Three Consequences

Stateless has no container.
`supply()` is a function call, and its arguments are the bindings.
Having no container has three consequences:

1. Stateless checks come before the program runs.
   A DI container reports a missing registration at the moment a lookup runs,
   at startup or much later, on an untested path.
   If you remove the `# type: ignore` from `unsupplied.py`,
   the type checker reports the [unsupplied `Need[Console]`](#forgetting-to-supply).

2. Stateless bindings are per call rather than per process.
   DI usually holds one type binding for the life of the program.
   `supply()` binds for one execution of one Effect,
   so two bindings for the same type can be live at once,
   as the screen and memory `Console`s are in [When Two Implementations Match](#when-two-implementations-match).
   Test cases need no reset between them.
   A typical DI container has one flat registry and no equivalent to [handler layering](#layering-handlers).

3. Stateless Abilities live in the function type.
   DI leaves that information in the bodies that ask for it.
   You must read the implementation to learn what a DI function needs.
   `holds()` declares `Need[Material] | Need[Nailer]` in its signature.
   A caller that does not supply them inherits both Abilities.

### Churn in Every Signature

An Ability that every caller inherits is also a drawback.
[Adding an Ability](#retrofitting-an-effect)
such as `Need[Log]` to a working function rewrites the return type of every function above it.
Under DI, the same change leaves every signature as it was.

Type checking is the earliest practical time to discover a forgotten dependency,
so the objection concerns churn and coupling rather than correctness.
A pass-through function such as `greet_all()` still declares `Need[Log]` in its type.
Taking that Ability back out later changes every signature on the path a second time.
People made the same complaint against [Java's checked exceptions](44_Effects--Effect_Management.md#catch-the-exception-you-expect),
where an exception added three levels down meant editing every signature above it.
That complaint is why [Effects Propagate, and the Type Checker Verifies It](#effects-propagate-and-the-type-checker-verifies-it)
compares the propagation to `async`.

## Waiting on a Coroutine

So far `Async` has appeared in one place: the type `run()` expects.
That type names `Async` because `run()` answers `Async` requests.
`wait()` makes an `Async` request,
so a function that calls it declares `Async` in its signature.
`wait()` accepts any awaitable,
and `yield from wait(...)` produces the value that awaitable produces:

```python
# stateless_coroutine.py
import asyncio
from stateless import Async, Depend, run, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched {url}"

def report(url: str) -> Depend[Async, str]:
    body = yield from wait(fetch(url))
    return f"{body = }"

if __name__ == "__main__":
    print(run(report("http://example.com")))
#: body = 'fetched http://example.com'
```

Every `Depend` signature so far reads `Depend[Need[...], ...]`,
while this one writes the Ability bare.
One rule covers both cases: the channel holds Abilities.
`Async` is an Ability, so it sits there bare.
`Console` is an ordinary class,
and `Need[Console]` is the Ability that asks for it.
The first type parameter's bound is `Ability`,
so the type checker rejects `Depend[Console, None]` at the annotation.
[Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
writes an Ability from scratch and explains what that type bound rejects.

An `Async` request carries an awaitable and asks the driver to await it.
`run()` does that with the event loop it starts.
So the driver, rather than a `supply()`, answers `Async`.
`supply()` answers `Need` requests and passes every other Ability outward.

`report()` is not an `async def` and contains no `await`,
yet its result comes from a coroutine.
`wait()` yields the coroutine as a request, and the driver awaits it.
Because the one `await` runs in the driver,
neither `report()` nor anything that calls it needs `async`.

### `sleep()` Carries Two Abilities

You need `wait()` at the point where an Effect requests a coroutine's result.
A function that already returns an Effect needs no `wait()`,
because `yield from` composes the returned Effect into the caller's Effect.
`stateless.time.sleep()` is such a function,
and it pairs an `Async` request with a `Need[Time]` Ability.
Here, `delayed_sum()` composes `sleep()` with a bare `yield from`:

```python
# sleep_effect.py
from stateless import Async, Depend, Need
from stateless.time import Time, sleep

def delayed_sum(
    values: list[int],
) -> Depend[Need[Time] | Async, int]:
    total = 0
    for value in values:
        yield from sleep(0.01)
        total += value
    return total
```

`sleep()` returns `Depend[Need[Time] | Async, None]`,
so `delayed_sum()` inherits both Abilities.

Supplying the library's own `Time` waits for real time:

```python
# real_clock.py
import time
from sleep_effect import delayed_sum
from stateless import run, supply
from stateless.time import Time

start = time.perf_counter()
result = run(supply(Time())(delayed_sum)([1, 2, 3]))
elapsed = time.perf_counter() - start
print(result)
#: 6
print(f"{elapsed >= 0.03 = }")
#: elapsed >= 0.03 = True
```

The Stateless `sleep()` makes two requests,
`need(Time)` for the clock and `wait()` for the await:

```python
def sleep(
    seconds: float
) -> Depend[Need[Time] | Async, None]:
    time = yield from need(Time)
    yield from wait(time.sleep(seconds))
```

The local `time` is the supplied `Time` instance,
not the standard library's `time` module,
so `time.sleep(seconds)` is the coroutine that `Time.sleep()` returns.
`Time.sleep()` is the only `async def` here.
`wait()` hands its coroutine to the driver, which awaits it,
so `delayed_sum()` needs no `async` and no `await` of its own.

`Time` has no special status in Stateless.
It is an ordinary class whose one method is `async def sleep()`.
`supply(Time())` binds an instance the way `supply(Console())` does.

### A Clock That Never Waits

Reading a clock is a [side cause](44_Effects--Effect_Management.md#what-is-an-effect).
`Need[Time]` moves that side cause into the Ability channel.
A test can then supply a clock that never waits:

```python
# test_instant_clock.py
from dataclasses import field
from typing import override
from record import record
from sleep_effect import delayed_sum
from stateless import as_type, run, supply
from stateless.time import Time

@record(slots=False)
class Instant(Time):
    waited: list[float] = field(default_factory=list)
    @override
    async def sleep(self, seconds: float) -> None:
        self.waited.append(seconds)

def test_clock_never_waits() -> None:
    clock = Instant()
    supplied = supply(as_type(Time)(clock))
    assert run(supplied(delayed_sum)([1, 2, 3])) == 6
    assert clock.waited == [0.01, 0.01, 0.01]
```

The same three sleeps take at least 30 milliseconds in `real_clock.py`.
Here `Instant` answers each one at once.

`delayed_sum()` runs the same body with either clock.
The subclass goes through [`as_type(Time)`](#supplying-an-interface),
as `Recorder` goes through `as_type(Console)`.

`Instant` is a record because `Time` is a frozen data class,
and a data class that inherits from a frozen one must be frozen too.
The record drops its slots because `Time` declares none.
Freezing prevents rebinding `waited`.
`sleep()` can still append to the list it holds.

## Where to Call `run()`

`run()` starts an event loop and drives the Effect inside it.
Its entire body is `return asyncio.run(run_async(effect))`.
Building and tearing down that loop takes time,
even for an Effect with no `Async` in it.
On Windows, `run(success(42))` measured about 650 microseconds
(about 75 on Linux),
three to four orders of magnitude above a plain function call.
That is the cost behind ["a synchronous program calls it once, at the outermost edge"](#the-simplest-effect).
`test_nailer.py` starts a loop once per parametrized case,
which is fine for four rows and adds up over a much longer parametrized list.

The event loop has a second consequence when you incorporate Stateless into an existing application.
`asyncio.run()` cannot start a second event loop inside a running one,
so you cannot call `run()` from any `async def`:

```python
# inside_a_loop.py
import asyncio
from exceptions import expect
from greeter import Console, greet
from stateless import run, run_async, supply

bound = supply(Console())(greet)

async def main() -> None:
    expect(RuntimeError, run, bound("Alice"))
    await run_async(bound("Bob"))

asyncio.run(main())
#: [RuntimeError] asyncio.run() cannot be called from a
#: running event loop
#: Hello, Bob!
```

`run()` builds the `run_async()` coroutine and hands it to `asyncio.run()`,
which raises a `RuntimeError` because a loop is already running.
Nothing awaits the coroutine,
so the run also prints a `RuntimeWarning` to standard error.
The output above shows standard output alone, so it leaves the warning out.
The warning is harmless, and a reliable sign of this mistake.
It appears whenever asynchronous code calls `run()`.

`run_async()` is the same driver packaged as a coroutine, so you `await` it.
A synchronous program calls `run()` once at its outermost edge.
An asynchronous program such as a web service or a bot awaits `run_async()` at the edge of each request.

Calling `run()` inside a coroutine is a runtime error rather than a type error,
because no type records whether an event loop is running.
The opposite mistake, calling `run_async()` without `await` in synchronous code,
draws `ty`'s `unused-awaitable` warning.

## The Error Channel

Dependencies are one half of the `Effect` type.
The other half is failure.

### Declaring a Failure with `@throws`

`@throws` converts a raised exception into a yielded one:

```python
# scores.py
from typing import Final, reveal_type
from stateless import throws

SCORES: Final[dict[str, int]] = {"Alice": 42, "Bob": 7}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name]

if __name__ == "__main__":
    reveal_type(score)
```

`score()` looks like an ordinary function that raises a `KeyError`,
but `@throws` changes its type, as `ty check scores.py` shows:

```text
info[revealed-type]: Revealed type
  --> scores.py:12:17
   |
12 |     reveal_type(score)
   |                 ^^^^^ `(name: str) ->
   |                       Generator[KeyError, Any, int]`
```

The revealed type is `Try[KeyError, int]` with [the alias](#the-effect-type)
expanded.
The `Generator`'s first parameter carries [`A | E`](#the-effect-definition).
`Try` fills `A` with `Never`, so `Never | KeyError` reduces to `KeyError`.

`Try` carries the same idea as the [`Result` type](42_Functional--Error_Handling.md#a-result-type)
in a different form.
A `Result` is a wrapper the function returns at once,
and the caller matches on it.
A `Try` is a description that runs when something drives it,
and its failure is a yielded value rather than a returned one.
A `Result`-shaped value appears in Stateless only after [`stateless.catch()`](#turning-an-error-into-a-value),
and there it is the bare union `int | KeyError` rather than a wrapper object.

For `Result`, you either rewrite the body to return an `Ok` or an `Err`,
or wrap the function in [`@safe`](42_Functional--Error_Handling.md#turning-exceptions-into-results),
which turns every exception into an `Err`.
`@throws` likewise leaves the body alone,
but it specifies the exception types it lifts and puts them in the signature rather than in a returned wrapper.

### A Failure Travels as a Value

Calling `score()` defers the lookup and returns an `Effect`.
If you advance the `Effect` one step with `next()`,
`next()` returns the `KeyError` as a value instead of raising it:

```python
# error_is_yielded.py
from scores import score

effect = score("Carol")
print(repr(next(effect)))
#: KeyError('Carol')
```

The body raises the exception.
`@throws` wraps that body in an ordinary `try`/`except`,
so the wrapper catches the `KeyError` and yields the exception object over the same channel that carries Ability requests.
That is why `Effect`'s alias puts `A | E` in the `Generator`'s first parameter.
Requests and failures are both values a description yields to its driver.

### Errors Propagate

A failure propagates through `yield from` the way an Ability request does,
so the caller's `Effect` type declares it too:

```python
# announce.py
from greeter import Console
from scores import score
from stateless import Effect, Need, need

def announce(
    name: str
) -> Effect[Need[Console], KeyError, None]:
    value: int = yield from score(name)
    console = yield from need(Console)
    console.print(f"{name}: {value}")
```

If you drop the `KeyError` from the annotation,
the type checker reports an error at the `yield from score(name)` line.
Every function on the path must declare the `KeyError`.

### Declaring Is Not Handling

Declaring an error leaves handling it up to you.
`run()` accepts an Effect with a failure still in its error channel.
The driver throws the failure back into the generator,
and when no `catch()` wraps the function,
the failure propagates out of `run()` as an ordinary exception:

```python
# error_escapes.py
from announce import announce
from exceptions import expect
from greeter import Console
from stateless import run, supply

expect(KeyError, run, supply(Console())(announce)("Carol"))
#: [KeyError] 'Carol'
```

The error channel records which failures can occur.
`run()` turns any that reach it back into ordinary Python exceptions.

The channel carries the failures `@throws` lifted into it.
`@throws` lifts the exception types it specifies.
An exception of any other type passes through the decorator as an ordinary raised exception.
The exception stays out of every signature,
so the type checker accepts the code that raises it.
An exception raised from a body without `@throws` stays outside the type the same way.
[Nothing stops an undeclared Effect](47_Effects--Stateless_in_Practice.md#nothing-stops-an-undeclared-effect)
examines that limit.

### Catching Is Not Handling

The driver throws a failure back into the generator,
so an ordinary `try`/`except` around a `yield from` catches it,
provided no handler sits between `run()` and that Effect.
The generator yields the exception as a value,
`run()` receives it and calls the generator's `throw()` method,
and `throw()` raises the exception at the [innermost suspended `yield`](45_Effects--Generators.md#throw-and-close-reach-the-innermost-generator).
That `yield` belongs to the Effect to which the `yield from` delegates.
The exception propagates out of that Effect as any raised exception does,
and the `except` clause around the `yield from` catches it.

Catching is different from handling.
The `KeyError` stays in the channel,
so the signature keeps declaring a failure that can no longer escape.
`catch()` alone moves an error out of the error channel and into the result.
A `catch()` further out takes the `KeyError` before an inner `except` can catch it.
One listing shows an `except`, a `catch()`,
and a `catch()` wrapped around an `except`:

```python
# except_vs_catch.py
from typing import assert_never
from scores import score
from stateless import Success, Try, catch, run

def guarded(name: str) -> Try[KeyError, str]:
    try:
        value = yield from score(name)
    except KeyError:
        return f"{name}: unknown"
    return f"{name}: {value}"

def moved(name: str) -> Success[str]:
    value: int | KeyError = yield from (
        catch(KeyError)(score)(name))
    match value:
        case KeyError():
            return f"{name}: unknown"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

if __name__ == "__main__":
    print(run(guarded("Carol")), run(moved("Carol")))
    print(repr(run(catch(KeyError)(guarded)("Carol"))))
#: Carol: unknown Carol: unknown
#: KeyError('Carol')
```

`run()` returns `Carol: unknown` from both `guarded()` and `moved()`,
and the two differ in their types.
`guarded()` must keep declaring a `KeyError` it can no longer emit,
while `moved()` is a `Success`.
Wrapping `guarded()` in a `catch()` makes its inner `except` dead code,
because `catch()` matches the yielded value before the driver gets it,
returns that value as the result, and never resumes the inner generator.

`supply()` returns a [`Handler`](#supplying-the-dependency),
and that `Handler` breaks the condition that no handler sits between `run()` and the Effect.
Its loop passes an error outward instead of throwing that error back into the Effect it wraps,
so the driver's `throw()` raises that error in the `Handler`'s own stack frame,
not `guarded()`'s stack frame.
The error propagates out of `run()`, and the inner `except` never runs:

```python
# handler_blocks_except.py
from except_vs_catch import guarded
from exceptions import expect
from greeter import Console
from stateless import run, supply

expect(KeyError, run, supply(Console())(guarded)("Carol"))
#: [KeyError] 'Carol'
```

This `guarded()` is the one that returned `Carol: unknown` in `except_vs_catch.py`.
It requests no `Console`, so the `supply(Console())` around it does one thing:
pass the `KeyError` outward.
Wrapping `guarded()` in that `supply()` is enough to keep the `KeyError` out of its `except` clause.

## Turning an Error Into a Value

`catch()` empties the error channel the way `supply()` empties the Ability channel,
but the two do different things with what they remove.
`supply()` provides the Ability inside the Effect,
so [the Ability parameter becomes `Never`](#supplying-the-dependency)
and the result type stays as it was.
`catch()` takes out the exception that `@throws` put into the channel and returns it as a value in the result:

```python
# catch_score.py
from collections.abc import Callable
from typing import assert_never
from greeter import Console
from scores import score
from stateless import (Depend, Need, Success, catch,
                       need, run, supply)

def report(name: str) -> Depend[Need[Console], None]:
    value: int | KeyError = yield from (
        catch(KeyError)(score)(name))
    console = yield from need(Console)
    match value:
        case KeyError():
            console.print(f"{name}: unknown")
        case int():
            console.print(f"{name}: {value}")
        case _:
            assert_never(value)

reporter: Callable[[str], Success[None]] = supply(
    Console())(report)
run(reporter("Alice"))
#: Alice: 42
run(reporter("Carol"))
#: Carol: unknown
```

The signature for `score()` is `(str) -> Try[KeyError, int]`.
`catch(KeyError)(score)` changes it to `(str) -> Success[int | KeyError]`.
`catch()` removes the error from the error type parameter,
which becomes `Never`, and adds it to the result type parameter.
That makes `value` something to `match` on rather than an exception to catch.

`Success` describes the Effect rather than the lookup.
Both channels are empty,
with every request answered and the `KeyError` moved into the result.
The Effect "succeeds" at producing either a score or a `KeyError` that reports the missing score.
A raised `KeyError` is a failure.
A returned `KeyError` is data.

`catch_score.py` has the same shape as `handler_blocks_except.py`.
`supply()` wraps a function `run()` drives.
The `catch()` here still works,
because it matches the yielded value rather than relying on the driver to throw it back in.

Moving the error into the result forces every caller to match on it.
If you drop the `match` and use `value` as a number,
the type checker reports an error:

```text
error[unsupported-operator]: Unsupported `+` operation
  --> catch_score.py:13:30
   |
13 |     console.print(f"{name}: {value + 1}")
   |                              -----^^^-
   |                              |       |
   |                              |       Has type `Literal[1]`
   |                              Has type `int | KeyError`
```

That rejection is the same guarantee the `Result` type gives in [Error Handling](42_Functional--Error_Handling.md#reaching-the-answer),
and `catch()` provides it without rewriting the body of `score()`.

## Multiple Errors

`catch()` tracks multiple error types.
`SCORES` stores its values as `int`s,
so looking up a name is the only step and `KeyError` is the only failure.
`RAW` stores the scoreboard as text, before anyone interprets it:

```python
# read_score.py
from typing import Final
from stateless import throws

RAW: Final[dict[str, str]] = {"Alice": "42", "Bob": "seven"}

@throws(KeyError, ValueError)
def read_score(name: str) -> int:
    text = RAW[name]  # KeyError
    return int(text)  # ValueError
```

The lookup raises a `KeyError` for an unknown name,
and the conversion raises a `ValueError` for text `int()` rejects,
like Bob's `"seven"`.

`@throws(KeyError, ValueError)` makes `read_score()`'s signature:

```python
(str) -> Try[KeyError | ValueError, int]
```

You can catch both errors or only one:

```python
# catch_subset.py
from typing import assert_never
from read_score import read_score
from stateless import Success, Try, catch

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from (
        both(name))
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
```

`both` is `(str) -> Success[int | KeyError | ValueError]`.
Every failure moves into the result, so the error channel is empty.
Each failure reaches the `match` in `all_handled()` as a value.

`one` is `(str) -> Try[ValueError, int | KeyError]`.
The caught error moves to the result.
The uncaught one remains in the channel.
`one_unhandled()` leaves `ValueError` in the channel,
so its signature must declare that failure.
Calling it on `"Bob"` propagates that failure to the `run()` call at the program's edge,
which raises it as an ordinary exception,
like `error_escapes.py` does for a single error.

```python
# test_catch_subset.py
import pytest
from catch_subset import all_handled, one_unhandled
from stateless import run

@pytest.mark.parametrize("name, expected", [
    ("Alice", "Alice: 42"),
    ("Bob", "Bob: unreadable"),
    ("Carol", "Carol: unknown"),
])
def test_all_handled(name: str, expected: str) -> None:
    assert run(all_handled(name)) == expected

def test_one_unhandled() -> None:
    assert run(one_unhandled("Alice")) == "Alice: 42"
    assert run(one_unhandled("Carol")) == "Carol: unknown"
    with pytest.raises(ValueError):
        run(one_unhandled("Bob"))
```

The failure the signature declares is the one the caller sees.
A failure leaves the error channel in one of two ways:
`catch()` moves it into the result, or `run()` raises it at the edge.

## Emptying the Channels

A channel empties in one of three ways,
two of which take a vocabulary of their own:

1. A dependency is an object created elsewhere.
   `need()` records the request as a `Need` in the type,
   and `supply()` answers it with an instance.
2. A failure is an exception.
   `@throws` lifts it into the type, and `catch()` takes it back out as a value.
3. An Ability that the driver answers on its own needs no vocabulary.
   `Async` sits in the same channel as a `Need`,
   and `run()` answers it by awaiting the request's awaitable in the event loop it starts.

The vocabularies differ, but the operation underneath them is the same:
each subtracts from the type.
`supply()` removes an Ability from the union,
and the channel reads `Never` once a handler answers the last Ability.
`catch()` removes an error and moves it into the result,
where a `match` must account for it.
An Effect with both channels emptied is a `Success`.
`run()` accepts more than that.
Its parameter is `Effect[Async, Exception, R]`,
so an `Async` request or a declared failure can still remain in its type when you call it.

The channels resolve differently:

- `unsupplied.py` shows the type checker rejecting a `run()` call whose Effect still declares an Ability,
  before the program starts.
- `error_escapes.py` shows `run()` accepting an Effect that still declares a failure,
  then raising that failure at the edge.

The difference follows from what each channel holds.
An unbound dependency has no answer anywhere in the program,
so a driver that receives one has one response, `MissingAbilityError`.
An unhandled failure has a clear meaning at the edge: raise the exception,
which Python does with or without the Effect type.
So the two channels guarantee different things.
You must resolve a dependency before anything runs,
while a declared failure stays in the type until you choose where to handle it.
The type checker covers both declarations.
Forgetting to declare either is a type error.

Every Ability in this chapter comes from the library.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md)
writes Abilities of your own and the handlers that answer them.

## Exercises

Try each exercise before opening its [solution](../Solutions/46_Effects--Stateless/).

1.  Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
    an Effect that asks for a name and greets the result.
    Supply a scripted `Console` in a test and a real one in a demo,
    and confirm `ask_and_greet()` stays unchanged between them.
2.  Take `undeclared_need.py`, remove the `# type: ignore`,
    and run `ty check` on it.
    Fix the error by changing only the annotation,
    then check what `greet_all()`'s callers must now declare.
3.  Apply `reveal_type()` to `catch(ValueError)(one_unhandled)` and run `ty check`.
    Explain why its result type differs from `all_handled()`'s result type,
    given that both have handled every error `read_score()` declares.
4.  Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
    then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.
5.  Add a `Metal` material to `test_nailer.py` with a strength that survives the robotic nailer,
    and add its two rows to the table.
    Then explain why the test function body needs no change.
6.  This one looks ahead to `handle()`,
    which [Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
    covers.
    `default_console.py` defaults by supplying an instance.
    Write the other kind of default, one that builds the type the request names.
    `handle()` reads its handler's parameter annotation to decide what it answers,
    so a function annotated `Need[Console]` and returning `ability.t()` hands back a default-constructed instance of the requested class.
    Run it against `greeter.py`'s `greet()`,
    whose `Console` constructs with no arguments,
    and confirm the greeting prints.
    Then declare a second Ability and request that one too,
    and report which requests your handler answered at runtime and which ones the type checker believes it answered.
    Account for the difference,
    using `handle()`'s `t = get_origin(t) or t` as the evidence.
7.  Break `audit_log.py` by removing the `yield from` in front of `greet(name)` in `greet_logged()`.
    Run `ty check`, `ruff check`, and the script,
    and record what each reports and what the program prints.
    Explain where the greetings went and why no tool reports an error.
    Then restore that `yield from`,
    and instead remove the `yield from` in front of `need(Console)` in `greeter.py`'s `greet()`.
    This time the type checker produces two diagnostics.
    Explain what each one catches,
    and why the checker catches assigning a dropped request but not discarding one.
8.  Build a registry of Effects:
    a `dict[str, Success[None]]` that maps each of two names to `supply(Console())(greet)(name)`.
    Run every entry, then run every entry a second time,
    and record what prints on each pass.
    Change the values to functions that build the Effect when called,
    and run both passes again.
    Explain which of the two shapes `retry()` requires,
    and why it takes a schedule and returns a decorator of type `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`,
    rather than being an operation on an Effect.
9.  Write `report_all()`,
    which calls `stateless_coroutine.py`'s `report()` for three URLs with `yield from` and returns the three results.
    Work out what `report_all()`'s annotation must be,
    and confirm it with the type checker.
    Then call it from inside an `async def`,
    once with `run()` and once with `await run_async()`,
    and record what each one does.
    Explain why the type checker accepts both.
10. `announce()` declares `Effect[Need[Console], KeyError, None]`.
    Give it a second failure:
    a helper that formats the score and raises a `ValueError` on a negative one,
    lifted with `@throws(ValueError)`.
    Follow the type checker until the program builds,
    add a negative score to `scores.py`'s `SCORES` so the new failure can occur,
    then run it on a name that produces each failure and on one that succeeds,
    and say where the program reported each failure.
    Then delete `ValueError` from `announce()`'s annotation and record what the type checker reports and at which line.
11. `ambiguous_supply.py` picks its `Console` by argument order.
    Add a third implementation and predict, before running it,
    which of the six orderings send Alice's greeting where.
    Then follow the advice in [When Two Implementations Match](#when-two-implementations-match):
    give the recording implementation a method name the screen one does not have,
    declare each as its own `Protocol`,
    and show that handing the wrong implementation to an Effect is now a type error rather than a silent choice.
    Two implementations sharing one method name stay ambiguous under both `Protocol`s,
    so say what the technique does and does not prevent.
