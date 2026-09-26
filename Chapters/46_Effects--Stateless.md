# Stateless

Two things a function does are the easiest to forget:
what it needs from outside, and how it can fail.
Stateless writes both into the function's type,
and the type checker holds every caller to them.

[Effect Management](44_Effects--Effect_Management.md#library-effect-management)
introduced library Effect systems.
[Stateless](https://github.com/suned/stateless)
implements an Effect Management System (EMS).

Stateless encodes an Effect's dependencies and failures into the return type of a function,
and a type checker verifies that every caller either absorbs the Effects or carries them forward.
If you forget to declare a dependency, the check fails.
If you forget to supply one, the check fails.
Those two checks are the Effect tracking and delayed binding of a full EMS,
with the bookkeeping moved into the type system.

Stateless builds on generators.
[Generators](45_Effects--Generators.md)
covered the three-parameter `Generator` annotation,
a driver that answers a generator's requests one `send()` at a time,
and `yield from`, which composes generators and produces the inner generator's return value.
Every Effect in this chapter is such a generator.
Stateless supplies the vocabulary for the requests and the driver that answers them.

This chapter covers the two channels an Effect declares:
the dependencies it needs and the ways it can fail.
Both channels live in the signature,
and both use the yield channel a generator already carries.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md)
builds examples using those channels.

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

For example:

```python
Effect[Need[Console], KeyError, None]
```

This Effect needs a `Console`, can fail with a `KeyError`, and produces nothing.
The first parameter is `Need[Console]` rather than `Console`:
the Effect asks for a console, and something else supplies one later.
[Nothing Runs Yet](#nothing-runs-yet)
explains why that request must be a value of its own.

Although you can write the full `Effect` signature each time,
the library provides three aliases for the most common cases.
Each one fills in `Never` for an unused type parameter:

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
similar to the `drive()` of [Generators](45_Effects--Generators.md#a-generator-is-a-description).
`run()` primes the generator, drives it to completion, and returns the result.
Nothing the Effect describes runs until you call `run()`.
A synchronous program calls it once, at the outermost edge.

The two names differ only in case:
`success()` is a function that builds an Effect,
and `Success` is the alias from the table, the type of that Effect.
`Success[int]` says `double()` is pure: it cannot read anything,
and it cannot fail.

`double()` contains no `yield`, so it is an ordinary function.
Python decides generator-function status from the body alone:
a `yield` in the body makes a function a generator function,
whatever the return annotation says and whatever object the body returns.
The object that implements the generator protocol is the Effect that `success()` builds.
`double()` calls `success()` and returns that Effect,
the way an ordinary function returns a list.
The annotation describes the object `double()` returns rather than how its body reads.
`run()` drives any object that implements the generator protocol.

`success()` returns a `SuccessEffect`,
a small class implementing that protocol directly:
its `send()` raises `StopIteration` carrying the value,
so `run()` gets the result on its first step.
`success()` exists for yield-free functions like this one.
In a generator function, `return value` sets the Effect's `R` directly.
`return success(value)` there produces a `Success[R]` where the signature expects an `R`,
so the type checker rejects it.

`double()` takes everything it uses as its argument,
so it gains nothing from being an Effect.
The gain appears when a function depends on something created elsewhere,
such as a console, a file, or a network connection.

## Declaring a Dependency

`Need` is how Stateless does dependency injection.
A `Need` is a request for an instance, and something else answers it.
`need(SomeClass)` is an Effect that produces an instance of `SomeClass`,
without saying what supplies that instance:

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

`greet()` needs a `Console`, cannot fail, and produces nothing.
`greeter.py` lives in `utils/` because both this chapter and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
import it.
This chapter builds its own `Console` rather than the one Stateless ships;
[Builtin Dependencies](#builtin-dependencies), below, says why.
Compare `greeter.py`'s `greet()` to the version that calls `print()` directly:

```python
# untyped_greet.py
def greet(name: str) -> None:
    print(f"Hello, {name}!")
```

That signature is incomplete.
`-> None` describes the return value,
and the body also writes to standard output,
a side effect the signature leaves out.
A caller who wants to redirect the output, or to test the function,
must capture stdout.

`Depend[Need[Console], None]` states the dependency.
A caller now has two options: supply a `Console`,
or declare the same need in its own signature and pass the requirement to its own caller.
A caller that does neither fails the type check.

In `greeter.py`, two details deserve attention:

1. `greet()` is a generator function, because it contains `yield from`,
   so calling it builds the Effect its signature declares.
2. `console` is of type `Console`,
   so the type checker treats `console.print()` the same as any other method call.
   Nothing has supplied the dependency yet, and `console` keeps its type.

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

`A` and `E` share the first type parameter, and `R` is the third.
Nothing in the union itself tells a request from a failure;
two bounds on the library's type variables do that instead.
`A`'s bound is `Ability[Any]`, and `E`'s bound is `Exception`.
The two bounds do not exclude each other:
a class that subclasses both would satisfy each at once,
and at runtime it would count as a failure.
No listing here builds one.
[Waiting on a Coroutine](#waiting-on-a-coroutine)
states the `A` bound as the rule for `Depend`.
At runtime, `run()`'s driver tells the two apart with `case Exception() as error`:
whatever the generator yields that matches `Exception` is a failure,
and everything else is an Ability request.
That leaves the second type parameter, `Any`,
which [Generators](45_Effects--Generators.md#annotating-a-generator)
taught you to read as the type the `yield` expression produces inside the generator.
That `Any` is deliberate, and it decides how `greet()` must write its request.

### Why `yield from`

The request in `greet()` reads `console = yield from need(Console)`,
not `console = yield Need(Console)`.
The reason is that `Any`.

A generator has one SendType for its whole life,
and an Effect needs a different answer for each request:

- A `yield` that requests a `Need[Console]` should get back a `Console`.
- A `yield` that requests a `Need[Log]` should get back a `Log`.

What comes back depends on which Ability the `yield` requested,
and one SendType cannot vary from one `yield` to the next.
If you pin it to `Console`,
the type checker reads `yield Need(Log)` as producing a `Console`.
So the SendType is `Any`, which accepts every answer unchecked.

A bare `yield` produces that SendType, `Any`.
`yield from` produces the inner generator's `ReturnType` instead,
so the type checker knows the answer's type.
`need(Console)` builds a small generator that serves one request,
so its `ReturnType` can name a specific type.
`need()` returns `Depend[Need[T], T]`,
which expands to `Generator[Need[T], Any, T]`.
Calling `need(Console)` binds `T` to `Console`,
so `console` takes its type from that `ReturnType`,
not from the `Any` in the SendType.

Taking the type from the `ReturnType` is why every request in this chapter uses `yield from` rather than `yield`,
and why the custom abilities of [Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
get a small function of their own.

## Builtin Dependencies

The `Console` in `greeter.py` is one this chapter defines.
Stateless also ships three dependencies of its own:

- `Console` in `stateless.console`,
  whose `print_line()` and `read_line()` accessors call its `print()` and `input()` methods,
- `Files` in `stateless.files` that reads a whole file,
- `Time` that [Adding Behavior to an Existing Effect](47_Effects--Stateless_in_Practice.md#adding-behavior-to-an-existing-effect)
  supplies to `retry()`.

All three are concrete classes rather than interfaces.
That constrains what a test double for one of them can be;
[Supplying an Interface](#supplying-an-interface) works through the limit.

`read_file()` is also the library's own example of both channels at once:
its accessor carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect,
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
A language with builtin Effects intercepts an Effect where it runs.
Stateless is ordinary Python, so when a function body calls `console.print()`,
the call goes straight to `console` and no library code runs.
A library acts only on objects handed to it,
so the request for a `Console` must be an object the function hands out.
Driving `greet()` by hand shows that object,
the way [Generators](45_Effects--Generators.md#a-generator-is-a-description)
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

`need(Console)` builds a `Need[Console]`,
a frozen data class whose `t` field holds the requested class,
and `yield from` yields that `Need` out of the function body.
`next()` runs `greet()` up to that request and produces it.
Nothing has printed at that point,
because `greet()` has suspended at the `yield` inside `need()`.
`send(Console())` answers the request and resumes the function,
which prints its greeting and finishes, raising `StopIteration`.
[Supplying the Dependency](#supplying-the-dependency)
replaces those `next()` and `send()` calls with `run()` and a handler that decides which object answers each request.

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

1. `supply(Console())` builds a *handler*,
   an object that answers `Need[Console]` with that instance.
2. Calling the handler on `greet` returns a new function `bound` that answers the requests `greet()` makes.
3. Calling that function with `"Alice"` builds an Effect with nothing left to supply,
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

`ty` shows `greet` as the `def` it is, name included;
`bound` is a function `supply()` built, so `ty` shows only its signature.
The two revealed types are the expanded forms of `Depend[Need[Console], None]` and `Success[None]`.
`Need[Console]` sits in the first type parameter of `greet` and disappears from `bound`,
leaving the `Never` from the alias table.

Handling an Ability *subtracts* it from the type.
Here the subtraction leaves nothing behind:
`greet()` declares one Ability and cannot fail, so `bound` produces a `Success`.
That `Success` is a consequence rather than a requirement:
`run()`'s parameter type rejects every unanswered Ability except `Async`.
`run()` accepts an Effect that can still fail,
and raises the failure as an ordinary exception
([The Error Channel](#the-error-channel)).
Binding an implementation and satisfying the type checker are the same act.

## Layering Handlers

A handler answers the Abilities `supply()` gave it and re-yields the rest to the next handler out,
so a second `supply()` wrapped around the first answers what the inner one re-yielded.
`greet_all()` in [Retrofitting an Effect](#retrofitting-an-effect)
declares two Abilities:
`supply(Log())(greet_all)` still has the type `(list[str]) -> Depend[Need[Console], None]`,
and wrapping that in `supply(Console())` leaves `(list[str]) -> Success[None]`.
You can bind some Abilities near the Effect and the others at the edge,
with the type recording what each layer left behind.

A dependency injection container often lets you register a fallback for a type nobody else provides.
Stateless has no such registration, and `need()` takes no default argument.
Layering handlers produces one all the same.
This `Console` carries a tag so the output says which handler answered:

```python
# default_console.py
from dataclasses import dataclass
from stateless import Depend, Need, need, run, supply

@dataclass
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

`fallback` is an ordinary handler, applied at the edge;
`chosen` is a second handler already applied to `greet`.
The first run has `fallback` as its one handler, so the default answers.
The second run wraps `greet()` in its own `supply()` first,
and that inner `supply()` empties the Ability channel before any request reaches `fallback`.
The handler nearest the Effect answers first,
and the outer one answers only what remains.
The type records which handler answered:
`chosen` is already `(str) -> Success[None]`,
so `fallback(chosen)` keeps that type.

A default removes the check that makes `Need` worth declaring.
An Effect that would fail the type check for a missing `Console` now passes it and runs.
A forgotten binding then shows up as a wrong-looking result rather than an error.
Use one for a genuine default, a null logger or a no-op console,
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
run(description)
#: Hello, Alice!
print(repr(run(description)))
#: None
run(bound("Alice"))
#: Hello, Alice!
constant = success(42)
print(run(constant), run(constant))
#: 42 42
```

The first run exhausted the generator,
so the second `run()` of the same object gets an immediate `StopIteration` whose value is `None`.
The function never resumed, so it greets nobody and produces `None`.
Calling `bound("Alice")` again builds a fresh description, and that one runs.
`success()` is the exception because it builds no generator.
Its small object's `send()` reports the value every time,
so a constant Effect replays.

Running once is where Stateless departs from Effect systems in other languages.
A ZIO or Effect-TS value is an immutable description that you can interpret as often as you like,
so their combinators are operations on that value:
ZIO writes `action repeat policy`, repeating the effect the value describes.
Stateless has `repeat()` and `retry()` too,
but each takes a schedule and returns a decorator of type `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`.
They decorate the function,
because the function can produce a second description.
`catch()`, `throws()`, and `supply()` take functions for the same reason.

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
and it caches rather than replays:
it wraps the Effect in an object that records the result and hands that same result back on a second `run()`.
Like `repeat()` and `retry()`, `memoize()` decorates the function;
[`repeat()` and `memoize()`](47_Effects--Stateless_in_Practice.md#repeat-and-memoize)
shows it in use.

## Forgetting to Supply

Give `run()` an Effect that still needs a `Console`:

```python
# unsupplied.py
from greeter import greet
from stateless import run
from stateless.errors import MissingAbilityError

try:
    run(greet("Alice"))  # type: ignore
except MissingAbilityError as e:
    print(e)
#: Need(t=<class 'greeter.Console'>)
```

Running it raises a `MissingAbilityError`.
If you remove the `# type: ignore`, `ty` rejects the program before it runs:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
 --> unsupplied.py:7:9
  |
7 |     run(greet("Alice"))
  |         ^^^^^^^^^^^^^^ Expected
  |         `Generator[Async | Exception, Any, Unknown]`, found
  |         `Generator[Need[Console], Any, None]`
```

In Stateless, an unsupplied dependency is a type error,
not a production incident.
No test needs to exercise the path,
and no reviewer needs to notice the omission.

The expected type in that message names two things that come later in this chapter:

- `Async` is a built-in Ability for asynchronous work,
  which `run()` handles on its own.
  [Waiting on a Coroutine](#waiting-on-a-coroutine) takes it up.
- `Exception` is the error channel,
  the subject of [The Error Channel](#the-error-channel)
  and everything after it.

`run()` accepts an Effect whose yield channel has narrowed to those two,
which is all that remains once you supply every other Ability.
`greet("Alice")` still has `Need[Console]`, so it fails type checking.

## Swapping the Implementation

`Need` creates a delayed binding.
You can therefore select different bindings.
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

The test captures nothing from stdout and mocks nothing:
it supplies a different `Console`, and `greet()` stays as written,
since its body names only `Console`.

`as_type(Console)` is the only extra call in that test.
It says "treat this recorder as a `Console`,"
and at runtime it returns the object it received.
`supply()` requires `as_type()` because it reads the Ability from the static type of its argument.
Inheritance answers the same question at runtime,
since `Recorder` derives from `Console`.
[Supplying an Interface](#supplying-an-interface) explains both halves,
along with what changes when the Ability is an interface rather than a class.

`supply()` binds one instance for every matching request over the Effect's run,
which is why the test reads the messages back out of `recorder` afterward.

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
A `Depend` function's callers must also declare the dependency,
all the way to `supply()`.
The difference is that you can declare as many Abilities as you like.

The `yield from` inside `greet_all()` is what relays `greet(name)`'s request to the driver.
If you write that loop body as a bare `greet(name)`,
`ty` objects with an `invalid-return-type`:
"Function always implicitly returns `None`."
That looks like protection, but it is an accident.
That `yield from` is the only `yield` in `greet_all()`,
so deleting it turns `greet_all()` into an ordinary function.
The type checker reports the changed shape rather than the discarded Effect.

A function with a second `yield` keeps its shape, so every check passes.
`greet_logged()` in [Retrofitting an Effect](#retrofitting-an-effect)
makes two requests, one for the greeting and one for the log.
If you write its first line as a bare `greet(name)`, every check passes.
`ty` and `ruff` report nothing, the program runs, the log gains both entries,
and no greeting prints.
The call still builds a description, and the body discards it unrun.

The same trap exists in ZIO for the same reason.
An Effect written as a bare statement is a discarded value there too.
In ZIO Direct the fix is `.run`,
and in a `for` comprehension it is the `<-` binding.
Python's is `yield from`.
The hazard belongs to deferred execution rather than to generators.
When an Effect appears to do nothing, look for a missing `yield from`.

You declare the Ability by hand, and the type checker verifies the declaration.
If you annotate `greet_all()` as pure, `ty` reports the mismatch:

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
Here it is in Stateless:

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
#: Hello, Alice!
#: Hello, Bob!
print(log.entries)
#: ['greeted Alice', 'greeted Bob']
```

The new Effect is the `Log` write inside `greet_logged()`.
Every function on the path to it gained a `Need[Log]`,
here `greet_logged()` and its caller `greet_all()`,
while `greet()` keeps its signature.
`supply()` now provides both a `Console` and a `Log`.
Stateless leaves you those edits and lists them for you:
the type checker names each place that needs changing,
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
A new Ability changes the signatures alone:
`yield from greet_logged(name)` stays as it is, and the instance appears once,
at `supply()`.

Multiple Abilities combine with `|` because the union describes one request at a time.
Each `yield` in `greet_all()` produces either a `Need[Console]` or a `Need[Log]`,
not both at once.
Over the whole run it makes both kinds of request,
so `supply()` must provide a `Console` and a `Log`.

The repeated union is the shape a `type` alias normally shortens,
and the book normally writes one.
Under `ty` 0.0.82 the alias checks the same as the written-out signature:
an undeclared Ability behind `type Greeting = Depend[...]` draws the same `invalid-yield`.
This book still writes Effect signatures out in full,
because the union is the information:
every channel a function uses stays visible at the point of use.
Before you shorten one with an alias,
confirm that your type checker reports an undeclared Ability through it.

## One Effect, Many Environments

`audit_log.py` supplies two Abilities at one call site.
A test suite usually needs many, one per environment.
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

`holds()` decides whether a nailer's force stays under a material's strength.
`Material` and `Nailer` are distinct types,
so `supply()` matches each request to one of them.
[When Two Implementations Match](#when-two-implementations-match)
picks up the case where two supplied objects fit one Ability.
Here the test varies both:

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
`holds()` takes no arguments; `supply()` binds `material` and `nailer` instead,
so the table reads as a matrix of environments rather than a list of arguments.
A new `Material` is a new row.

Dependencies as parameters serve this test as well,
because `holds(material, nailer)` is easy to call four times.
The two styles diverge when a function three calls deep requests the dependency.
The parameter version then adds two parameters to every function on the path;
this version changes the row alone.
`audit_log.py`'s `greet_all()` is that depth: the test calls `greet_all()`,
`greet_all()` calls `greet_logged()`,
and `greet_logged()` requests `Need[Log]` and calls `greet()`,
which requests `Need[Console]`.
Varying the environment there again touches the row alone:

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

Two rows, two `Console` implementations,
and neither `greet_all()` nor `greet_logged()` gains a parameter.
The parameter-passed version adds a `console` argument to both,
even though only `greet()`, one level further down, uses it.

## Supplying an Interface

[Swapping the Implementation](#swapping-the-implementation)
substituted a `Recorder` for a `Console` but postponed the reason for using `as_type(Console)`.
That call answers two questions, for two audiences: static analysis and runtime.

### What the Type Checker Reads

`supply()` reads the Ability from the declared type of its argument,
so handing `recorder` to `supply()` builds a handler for `Need[Recorder]`,
a different Ability from the `Need[Console]` that `greet()` requests.
`as_type(Console)(recorder)` converts the argument's static type into `Console`,
so `supply()` builds the handler type `greet()` needs.

At runtime `as_type()` is the identity function and returns the object it received.
Only the static type changes.

`typing.cast(Console, recorder)` produces the same static type,
but the two differ in what they check.
`cast()` is an unchecked assertion:
the type checker accepts it whatever the object's type.
`as_type(Console)` returns a function annotated `(Console) -> Console`,
so the type checker verifies that the object it receives is a `Console`.
`as_type()` widens to a supertype; `cast()` replaces one type with any other.

### What `isinstance()` Checks

The library decides the runtime question with `isinstance()`.
`supply()` builds a handler that checks each request with `isinstance(instance, ability.t)`,
where `ability.t` is the class inside the `Need`.
In `test_greeter.py`, `ability.t` is `Console` and `instance` is `recorder`,
and `isinstance(recorder, Console)` succeeds because `Recorder` inherits from `Console`.
So two separate things make that test work:
`as_type(Console)` satisfies the type checker,
and the inheritance satisfies the runtime check.

The inheritance also carries every method `Console` gains later.
`Recorder` overrides everything it inherits from `Console`,
so today the parent contributes only the name `isinstance()` matches.
If you add a `read_line()` method to `Console` tomorrow,
`Recorder` inherits the real one,
and a test meant to record performs live console I/O.
No check reports it.

### An Interface Instead of a Base Class

Stateless's own `Console` is the concrete class [Builtin Dependencies](#builtin-dependencies)
named, and only a subclass can replace it.
Its accessors name that class,
so `isinstance()` accepts an instance of the class or a subclass.
A structurally identical double fails with a `MissingAbilityError` whatever static type `as_type()` gives it,
so a double for the builtin `Console` must inherit from it.
That `Console` implements `input()` as well as `print()`,
so a double that overrides only `print()` reads live stdin.
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
`Terminal` is one implementation and `Recorder` is another,
and `greet()` names neither.
Because a `Protocol` matches on structure,
`Recorder` qualifies as a `Console` without inheriting from `Console`.
`supply()` matches requests with `isinstance()`.
`isinstance()` accepts a `Protocol` marked `@runtime_checkable` and raises a `TypeError` on any other,
so the Protocol carries that decorator.

You still need `as_type()`.
This listing supplies a `Terminal` both ways:

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

Structural matching decides the runtime issue, not the static one.
`supply(Terminal())` still builds a handler for `Need[Terminal]`,
which leaves `greet()`'s `Need[Console]` in place.
The unhandled request stays in the type that reaches `run()`,
and that call is the line `ty` reports.
An interface needs the `as_type()` upcast more than a base class does:
you can instantiate a concrete `Console` and supply it directly,
but an interface reaches `supply()` only through an implementation.

`console_protocol.py` is the form to write in production.
Most listings in these two chapters use a concrete `Console` instead,
because under the interface,
supplying an implementation directly requires `as_type()`.
That call is what an interface adds at each direct supply.
[Composing a Program](47_Effects--Stateless_in_Practice.md#composing-a-program)
declares its Abilities as `Protocol`s and shows the annotation that replaces that call:
write one boundary function whose parameter annotations name the interface types,
and call `supply()` inside it.
The parameter annotation upcasts the argument,
so every call site passes its implementation bare,
and every function between that boundary and the Effect reads the same under either form.
An annotated local variable is different:
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
`Terminal` prints Alice's greeting and `capture` stays empty.
Swapping the two arguments appends Bob's greeting to `capture` and prints nothing.
`greet()` runs the same body in both runs.
The type checker accepts both runs alike,
because both bindings have the same type.
Both instances go through `as_type(Console)`,
since each is a `Console` by structure alone.

Here Stateless lacks a check ZIO performs.
ZIO reports two implementations of one requirement as a compile-time error naming both candidates,
because its `provide` resolves the dependency graph during compilation.
`supply()` resolves at runtime by scanning its arguments,
so the same mistake produces a program that runs and does the wrong thing.
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

expect(NotRegistered, greet, "Alice")
#: [NotRegistered] Console
register(Console, Console())
greet("Alice")
#: Hello, Alice!
```

`register()` puts an instance in, and `get()` looks up an instance by type,
at the point where the program needs it.
The type is the registration key,
so `register(Console, Recorder())` binds an implementation to the type the caller requests.
A dictionary matches the key exactly,
so `get(Console)` never returns a subclass registered under its own name.
`supply()` takes bare instances and matches a request with `isinstance()` instead,
which is why two instances that satisfy one `Need` are ambiguous
([When Two Implementations Match](#when-two-implementations-match)).
The DI registration key also does the work `as_type(Console)` does for `supply()`.
`supply()` reads each Ability from its argument's static type,
so `supply(recorder)` is a `Handler[Need[Recorder]]`,
and no `Need[Console]` matches it
([Supplying an Interface](#supplying-an-interface)).

`DI_CONTAINER` holds instances of unrelated types,
so `Any` is the one type its values share.
The key carries the type information,
but a homogeneous `dict` types every value alike.
The invariant "the value under key `type[T]` is a `T`" therefore lives in `register()`'s signature rather than in the container.

`greet()`'s body matches `greeter.py`'s `greet()` line for line,
apart from `console: Console = get(Console)` in place of `console = yield from need(Console)`.
Its signature matches the `untyped_greet.py` version in [Declaring a Dependency](#declaring-a-dependency):
both read `(str) -> None`, and neither names the `Console` it uses.

The first `greet("Alice")` fails at runtime because nothing has registered a `Console` yet;
the second succeeds because the binding now exists.
The two calls are identical, and the types say nothing about registration,
so the type checker accepts both.

DI meets its goal: the `Console` is swappable.
But it relocates a [side cause](44_Effects--Effect_Management.md#what-is-an-effect)
rather than declaring one, so the type checker never validates the dependency.

`dependency_injection.py` demonstrates one shape of DI, a service locator:
a body reads the container directly, with `get(Console)`.
Constructor injection is the stronger, more common shape,
and frameworks such as FastAPI's `Depends` build on it.
Constructor injection answers the complaint that the type checker never validates the dependency:
the dependency arrives as a parameter,
so a static type checker validates every call that supplies one.
The binding happens once, at the endpoint or the constructor.
Every function that boundary calls passes the dependency onward as a parameter,
the same parameter an EMS replaces with a channel in the return type.

An EMS requires more:
the dependency must appear in the signature so the type checker can verify it.
That is why the EMS `greet()` returns `Depend[Need[Console], None]` while `dependency_injection.py`'s returns `None`.
An EMS tracks every dependency,
so the type checker reports the errors that a programmer's memory or an exhaustive test suite must otherwise find.

### No Container, Three Consequences

Stateless has no container.
`supply()` is a function call, and its arguments are the bindings.
Having no container has three consequences:

1. Stateless checks come before the program runs.
   A DI container reports a missing registration at the moment a lookup runs,
   at startup or much later, on a path no test exercised.
   If you remove the `# type: ignore` from `unsupplied.py`,
   `ty` reports the unsupplied `Need[Console]`
   ([Forgetting to Supply](#forgetting-to-supply)).

2. Stateless bindings are per call rather than per process.
   DI usually holds one type binding for the life of the program.
   `supply()` binds for one execution of one Effect,
   so two bindings for the same type can be live at once,
   as the screen and memory `Console`s are in [When Two Implementations Match](#when-two-implementations-match).
   Test cases need no reset between them.
   A typical DI container has one flat registry and no equivalent to the handler layering of [Layering Handlers](#layering-handlers).

3. Stateless function requirements live in the function type.
   DI leaves that information in the bodies that ask for it.
   You must read the implementation to learn what a DI function needs.
   `holds()` declares `Need[Material] | Need[Nailer]` in its signature,
   and a caller that does not supply them inherits the requirement.

### Churn in Every Signature

A requirement that every caller inherits is also a drawback.
Adding a dependency to a working function rewrites the return type of every function above it,
as [Retrofitting an Effect](#retrofitting-an-effect) shows with `Need[Log]`;
DI takes the same change with no signature recording it.

Type checking is the earliest practical time to discover a forgotten dependency,
so the objection concerns churn and coupling rather than correctness.
A function that never logs still names `Need[Log]` in its type,
and taking that dependency back out later changes every signature on the path a second time.
People made the same complaint against Java's checked exceptions,
which [Effect Management](44_Effects--Effect_Management.md#catch-the-exception-you-expect)
describes failing this way.
That complaint is why [Effects Propagate, and the Type Checker Verifies It](#effects-propagate-and-the-type-checker-verifies-it)
compares the propagation to `async`.

## Waiting on a Coroutine

`Async` has appeared so far only inside error messages,
where `run()` answers it though no listing requested it.
`wait()` puts it into a signature deliberately.
`yield from wait()` accepts any awaitable and produces the value that awaitable produces:

```python
# stateless_coroutine.py
import asyncio
from stateless import Async, Depend, run, wait

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"fetched {url}"

def report(url: str) -> Depend[Async, str]:
    body = yield from wait(fetch(url))
    return f"{body = }, {len(body) = }"

print(run(report("http://example.com")))
#: body = 'fetched http://example.com', len(body) = 26
```

`Depend[Async, str]` needs `Async`, cannot fail, and produces a `str`.
Every dependency so far read `Depend[Need[...], ...]`,
while this one names the Ability directly.
The rule is the same in both cases: the channel holds Abilities.
`Async` is an Ability, so it sits there bare.
`Console` is an ordinary class,
and `Need[Console]` is the Ability that asks for it.
The first type parameter accepts only `Ability` subclasses,
so the type checker rejects `Depend[Console, None]` at the annotation.
[Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
writes an Ability from scratch and takes that type bound apart.

An `Async` request carries a coroutine and asks the driver to await it.
`run()` does that with the event loop it starts.
So nothing supplies `Async`: the driver answers it,
and `supply()` handles only a `Need`.

`report()` is not an `async def` and contains no `await`,
yet its result comes from a coroutine.
`wait()` yields the coroutine as a request, and the driver awaits it.
The one `await` runs in the driver,
so neither `report()` nor anything that calls it needs `async`.

### `sleep()` Carries Two Abilities

You need `wait()` at the point where an Effect requests a coroutine's result.
A function that already returns an Effect needs no `wait()`,
because `yield from` composes the two Effects directly.
`stateless.time.sleep()` is such a function,
and it pairs an `Async` request with a dependency.
This listing composes `sleep()` with a bare `yield from`:

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

Reading a clock is a [side cause](44_Effects--Effect_Management.md#what-is-an-effect),
and `Need[Time]` moves that into the Ability channel.
A test can then supply a clock that never waits:

```python
# test_instant_clock.py
import time
from dataclasses import dataclass, field
from typing import override
from sleep_effect import delayed_sum
from stateless import as_type, run, supply
from stateless.time import Time

@dataclass(frozen=True)
class Instant(Time):
    waited: list[float] = field(default_factory=list)
    @override
    async def sleep(self, seconds: float) -> None:
        self.waited.append(seconds)

def test_delayed_sum() -> None:
    clock = Instant()
    start = time.perf_counter()
    supplied = supply(as_type(Time)(clock))
    assert run(supplied(delayed_sum)([1, 2, 3])) == 6
    assert clock.waited == [0.01, 0.01, 0.01]
    assert time.perf_counter() - start < 0.5
```

`Instant.sleep()` records the request and returns.
The same three sleeps take at least 30 milliseconds in `real_clock.py`,
and under a few milliseconds here.

`delayed_sum()` stays unchanged and runs the same body with either clock.
The subclass goes through `as_type(Time)`,
for the reason in [Supplying an Interface](#supplying-an-interface).

In `Instant`, `waited` is a field because `Time` is a frozen data class and a subclass must carry `frozen=True` too.
Freezing prevents rebinding `waited`, not appending to the list it holds.

## Where to Call `run()`

`run()` starts an event loop and drives the Effect inside it.
Its entire body is `return asyncio.run(run_async(effect))`.
Building and tearing down that loop takes time,
even for an Effect with no `Async` in it.
On Windows, `run(success(42))` measured about 650 microseconds
(about 75 on Linux),
three to four orders of magnitude above a plain function call.
That is the cost behind "a synchronous program calls it once,
at the outermost edge" ([The Simplest Effect](#the-simplest-effect)).
`test_nailer.py` starts a loop once per parametrized case,
which is fine for four rows and worth remembering for a much longer parametrized list.

The event loop has a second consequence when you incorporate Stateless into an existing application.
`asyncio.run()` refuses to start a second event loop inside a running one,
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
so the run also prints a `RuntimeWarning` to standard error,
which the output above leaves out because it shows standard output alone.
The warning is harmless, and a reliable sign of this mistake:
it appears whenever asynchronous code calls `run()`.

`run_async()` is the same driver packaged as a coroutine, so you `await` it.
A synchronous program calls `run()` once at its outermost edge.
A program that is already asynchronous, a web service or a bot,
awaits `run_async()` at the edge of each request.
Calling `run()` inside a coroutine is a runtime error rather than a type error,
one of the few mistakes in this chapter that the type checker cannot report.
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
but `@throws` changes its type.
`ty check scores.py` reports what it becomes:

```text
info[revealed-type]: Revealed type
  --> scores.py:12:17
   |
12 |     reveal_type(score)
   |                 ^^^^^ `(name: str) ->
   |                       Generator[KeyError, Any, int]`
```

The revealed type is `Try[KeyError, int]` with [the alias](#the-effect-type)
expanded: it needs nothing, can fail with a `KeyError`, and produces an `int`.
The `Generator`'s first parameter carries `A | E`
([The Effect Definition](#the-effect-definition)).
`Try` fills `A` with `Never`, so `Never | KeyError` reduces to `KeyError`.

`Try` carries the same idea as the [`Result` type](42_Functional--Error_Handling.md#turning-exceptions-into-results),
built differently.
A `Result` is a wrapper the function returns at once,
and the caller matches on it.
A `Try` is a description that runs nothing until something drives it,
and its failure is a yielded value rather than a returned one.
A `Result`-shaped value appears in Stateless only after `stateless.catch()`
([Turning an Error Into a Value](#turning-an-error-into-a-value)),
and even then it is the bare union `int | KeyError` rather than a wrapper object.
For `Result`, you either rewrite the body to return an `Ok` or an `Err`,
or wrap the function in `@safe`, which turns every exception into an `Err`.
`@throws` likewise leaves the body alone,
but it names the exception types it lifts and puts them in the signature rather than in a returned wrapper.

### A Failure Travels as a Value

Calling `score()` runs nothing.
It returns an `Effect`.
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
That is why `Effect`'s alias puts `A | E` in the `Generator`'s first parameter:
requests and failures are both values a description yields to its driver.

### Errors Propagate

The `Effect` type carries a failure the same way it carries an Ability:

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

`announce()` uses all three parameters of `Effect[A, E, R]`:
it needs a `Console`, can fail with `KeyError`, and produces nothing.
If you drop the `KeyError` from the annotation,
`ty` points at the `yield from score(name)` line.
Every function on the path has to declare it.

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

The error channel records the failures that can occur,
and leaves handling them to you.
`run()` turns any that reach it back into normal Python exceptions.

The channel carries only the failures `@throws` lifted into it.
An exception raised from a body without `@throws` stays outside the type,
a limit that [Nothing stops an undeclared Effect](47_Effects--Stateless_in_Practice.md#nothing-stops-an-undeclared-effect)
examines.

### Catching Is Not Handling

The driver throws a failure back into the generator,
so an ordinary `try`/`except` around a `yield from` catches it,
provided `run()` drives that Effect directly.
The generator yields the exception as a value,
`run()` receives it and calls `throw()`,
and that `throw()` raises the exception in the innermost suspended frame,
where the `except` clause runs.
Catching is different from handling: the `KeyError` stays in the channel,
so the signature keeps declaring a failure that can no longer escape.
A `catch()` further out changes the outcome again:
it matches the yielded value before the driver sees it and returns that value as the result,
so the inner `except` never runs.
`catch()` alone moves an error in the type,
and it is the next section's subject.
One listing shows all three facts:

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

print(run(guarded("Carol")), run(moved("Carol")))
#: Carol: unknown Carol: unknown
print(repr(run(catch(KeyError)(guarded)("Carol"))))
#: KeyError('Carol')
```

The two functions behave identically at the edge and differ in their types.
`guarded()` must keep declaring a `KeyError` it can no longer emit,
while `moved()` is a `Success`.
Wrapping `guarded()` in a `catch()` makes its inner `except` dead code,
because `catch()` matches the yielded value before the driver gets it and never resumes the inner generator.

`supply()` returns a `Handler`
([Supplying the Dependency](#supplying-the-dependency)),
and that `Handler` breaks the condition that `run()` drives the Effect directly.
Its loop passes an error outward instead of throwing that error back into the Effect it wraps,
so the driver's `throw()` raises in the `Handler`'s own frame,
not `guarded()`'s.
The error escapes before the inner `except` runs:

```python
# handler_blocks_except.py
from exceptions import expect
from greeter import Console
from scores import score
from stateless import Effect, Need, need, run, supply

def guarded(
    name: str
) -> Effect[Need[Console], KeyError, str]:
    try:
        value = yield from score(name)
    except KeyError:
        return f"{name}: unknown"
    console = yield from need(Console)
    console.print(f"{name}: {value}")
    return f"{name}: {value}"

expect(KeyError, run, supply(Console())(guarded)("Carol"))
#: [KeyError] 'Carol'
```

`guarded()` here is the same function as before,
except that it also needs a `Console`, which this path never reaches.
Wrapping it in `supply(Console())` is enough to send the `KeyError` past the `except`.
`catch_score.py`, ahead in [Turning an Error Into a Value](#turning-an-error-into-a-value),
has the identical shape: `supply()` wraps a function `run()` drives.
The `catch()` there still works,
because it matches the yielded value itself rather than relying on the driver to throw it back in.

## Turning an Error Into a Value

`catch()` empties the error channel the way `supply()` empties the Ability channel,
but the two do different things with what they remove.
`supply()` provides the Ability inside the Effect,
so the Ability parameter becomes `Never` and the result type stays as it was
([Supplying the Dependency](#supplying-the-dependency)).
`@throws` puts a raised exception into the channel,
and `catch()` takes it back out as a value in the result:

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

`Success` describes the Effect rather than the lookup: both channels are empty,
with nothing left to supply and no failure for `run()` to raise.
The Effect "succeeds" at producing either a score or a `KeyError` that reports the missing score.
A raised `KeyError` is a failure.
A returned `KeyError` is data.

`reporter` is a function that builds an Effect,
as its `Callable[[str], Success[None]]` annotation states:
give it a `str` and it produces an Effect that needs nothing and cannot fail.
`run()` drives that Effect,
so `reporter("Alice")` comes first and `run()` second.

Moving the error into the result forces every caller to match on it.
Drop the `match` and use `value` directly as a number,
and the type checker reports an error:

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
and `catch()` reaches it without rewriting the body of `score()`.

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

`read_score()` takes two steps, with one potential failure in each.
The lookup raises a `KeyError` for an unknown name,
and the conversion raises a `ValueError` for text `int()` rejects,
like Bob's `"seven"`.

`@throws(KeyError, ValueError)` makes the `read_score` signature:

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
Every failure moves into the result, so nothing remains in the error channel.
`all_handled()` returns `Success[str]`:
no failure can escape as a thrown exception.

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
    with pytest.raises(ValueError):
        run(one_unhandled("Bob"))
```

`one` is `(str) -> Try[ValueError, int | KeyError]`.
The caught error moves to the result and the uncaught one remains.
`one_unhandled()` leaves `ValueError` in the channel,
so its signature must declare that failure.
Calling it on `"Bob"` carries that failure up to the `run()` call at the program's edge,
which raises it as an ordinary exception,
like `error_escapes.py` does for a single error.
The test's assertion for Bob is `pytest.raises(ValueError)`:
the failure the signature declares is the one the caller sees.
Failures never vanish.
They only relocate.

## Emptying the Channels

The two halves of this chapter taught two vocabularies,
and a third case that needs none:

1. A dependency is an object created elsewhere.
   `need()` records the request as a `Need` in the type,
   and `supply()` answers it with an instance.
2. A failure is an exception: `@throws` lifts it into the type,
   and `catch()` takes it back out as a value.
3. An Ability that the driver answers on its own needs no vocabulary.
   `Async` sits in the same channel as a `Need`, and nobody supplies it,
   because `run()` owns the event loop that answers it.

The vocabularies differ, and the operation underneath them is the same:
both subtract from the type.
`supply()` removes an Ability and leaves `Never` in its place.
`catch()` removes an error and moves it into the result,
where a `match` must account for it.
An Effect with both channels emptied is a `Success`.
`run()` accepts more than that: its parameter is `Effect[Async, Exception, R]`,
so an `Async` request or a declared failure can still remain in its type when you call it.

The channels resolve differently:

- `unsupplied.py` shows `run()` refusing an Effect that still declares an Ability,
  before the program starts.
- `error_escapes.py` shows `run()` accepting an Effect that still declares a failure,
  then raising that failure at the edge.

The difference follows from what each channel holds.
An unbound dependency has no answer anywhere in the program,
so a driver that receives one has one response, `MissingAbilityError`.
An unhandled failure has a clear meaning at the boundary: raise the exception,
which Python does with or without the Effect type.
So the two guarantees differ:
you must resolve a dependency before anything runs,
while a declared failure stays in the type until you choose where to handle it.
The type checker covers both declarations,
and forgetting to declare either is a type error.

## Exercises

1.  Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
    an Effect that asks for a name and greets the result.
    Supply a scripted `Console` in a test and a real one in a demo,
    and confirm `ask_and_greet()` stays unchanged between them.
2.  Take `undeclared_need.py`, remove the `# type: ignore`,
    and run `ty check` on it.
    Fix the error by changing only the annotation,
    then check what `greet_all()`'s callers must now declare.
3.  Apply `reveal_type()` to `catch(ValueError)(one_unhandled)` and run `ty check`.
    Explain why its result type differs from `all_handled()`'s,
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
    Write the other kind of default, one that builds whatever the request names.
    `handle()` reads its handler's parameter annotation to decide what it answers,
    so a function annotated `Need[Console]` and returning `ability.t()` hands back a default-constructed instance of the requested class.
    Run it against `greeter.py`'s `greet()`,
    whose `Console` constructs with no arguments,
    and confirm the greeting prints.
    Then declare a second Ability and request that one too,
    and report which requests your handler answered at runtime and which ones `ty` believes it answered.
    Account for the difference,
    using `handle()`'s `t = get_origin(t) or t` as the evidence.
7.  Break `audit_log.py` by removing the `yield from` in front of `greet(name)` in `greet_logged()`.
    Run `ty check`, `ruff check`, and the script,
    and record what each reports and what the program prints.
    Explain where the greetings went and why no tool objects.
    Then restore it, and instead remove the `yield from` in front of `need(Console)` in `greeter.py`'s `greet()`.
    This time `ty` produces two diagnostics.
    Explain what each one catches,
    and why `ty` catches assigning a dropped request but not discarding one.
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
    Importing that module runs its own unguarded `print(run(...))`,
    so expect one line of its output before yours.
    Work out what its annotation must be, and confirm it with `ty`.
    Then call it from inside an `async def`,
    once with `run()` and once with `await run_async()`,
    and record what each one does.
    Explain why `ty` accepts both.
10. `announce()` declares `Effect[Need[Console], KeyError, None]`.
    Give it a second failure:
    a helper that formats the score and raises a `ValueError` on a negative one,
    lifted with `@throws(ValueError)`.
    Follow `ty` until the program builds,
    add a negative score to `scores.py`'s `SCORES` so the new failure can occur,
    then run it on a name that produces each failure and on one that succeeds,
    and say where each failure surfaced.
    Then delete `ValueError` from `announce()`'s annotation and record what `ty` reports and at which line.
11. `ambiguous_supply.py` picks its `Console` by argument order.
    Add a third implementation and predict, before running it,
    which of the six orderings send Alice's greeting where.
    Then follow the advice in [When Two Implementations Match](#when-two-implementations-match):
    give the recording implementation a method name the screen one does not have,
    declare each as its own `Protocol`,
    and show that handing the wrong implementation to an Effect is now a type error rather than a silent choice.
    Two implementations sharing one method name stay ambiguous under both `Protocol`s,
    so say what the technique does and does not prevent.
