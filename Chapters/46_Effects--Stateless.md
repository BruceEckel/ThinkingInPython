# Stateless

[Effect Management](44_Effects--Effect_Management.md#library-effect-management)
introduced library Effect systems.
[Stateless](https://github.com/suned/stateless)
is a library that implements an Effect Management System (EMS).

Stateless encodes an Effect's dependencies and failures into the return type of a function,
and a type checker verifies that every caller either absorbs the Effects or carries them forward.
If you forget to declare a dependency, the check fails.
If you forget to supply one, the check fails.
That is the Effect tracking and delayed binding of a full EMS,
with the bookkeeping moved into the type system.

Stateless builds on generators.
[Generators](45_Effects--Generators.md)
covered the three-parameter `Generator` annotation,
a driver that answers a generator's requests one `send()` at a time,
and `yield from`, which composes generators and produces the inner generator's return value.
Every Effect here travels that path.
Stateless supplies the vocabulary for the requests and the driver that answers them.

This chapter covers the two channels an Effect declares:
the dependencies it needs and the ways it can fail.
Both channels live in the signature,
riding the yield channel a generator already carries.
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

This particular Effect needs a `Console`, can fail with a `KeyError`,
and produces nothing.
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
`Success[int]` says `double()` is pure.
It cannot read anything, and it cannot fail.

`double()` contains no `yield`, so it is an ordinary function.
Python decides generator-function status from the body alone:
a `yield` in the body makes a function a generator function,
and the return annotation and the returned object play no part.
The object that implements the generator protocol is the Effect that `success()` builds.
`double()` calls `success()` and returns that Effect,
the way an ordinary function returns a list.
The annotation describes the object `double()` returns rather than how its body reads,
and `run()` drives any object that implements the generator protocol.

`success()` returns a `SuccessEffect`,
a small class implementing that protocol directly:
its `send()` raises `StopIteration` carrying the value,
so `run()` gets the result on its first step.
`success()` exists for yield-free functions like this one.
In a generator function, `return value` sets the Effect's `R` directly,
so `return success(value)` there produces a `Success[R]` where the signature expects an `R`,
and the type checker rejects it.

`double()` needs nothing beyond its argument,
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
It lives in `utils/` because both this chapter and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
import it.
Compare that to the version that calls `print()` directly:

```python
# untyped_greet.py
def greet(name: str) -> None:
    print(f"Hello, {name}!")
```

That signature omits something.
`-> None` says the function returns nothing,
and the body writes to standard output,
a side effect the signature never mentions.
The caller cannot see the dependency, redirect the output,
or test the function without capturing stdout.

`Depend[Need[Console], None]` states the dependency.
A caller now has two options: supply a `Console`,
or declare the same need in its own signature and pass the requirement to its own caller.
A caller that does neither fails the type check.

In `greeter.py`, two details deserve attention:

1. `greet()` is a generator function, because it contains `yield from`,
   so calling it builds the Effect its signature declares.
2. `console` is of type `Console`,
   so the type checker treats `console.print()` the same as any other method call.
   The dependency waits without becoming untyped.

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
That leaves the second,
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
Pin it to `Console`,
and the type checker reads `yield Need(Log)` as producing a `Console`.
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

This is why every request in this chapter uses `yield from` rather than `yield`,
and why the custom abilities of [Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
get a small function of their own.

## Nothing Runs Yet

Calling `greet()` performs no work.
It simply returns a `Generator`:

```python
# describe_only.py
from greeter import greet

print(type(greet("Alice")))
#: <class 'generator'>
```

`greet("Alice")` builds a description of a greeting.
This is the description/execution split from [Effect Management](44_Effects--Effect_Management.md#library-effect-management).
A language with builtin Effects intercepts an Effect where it runs.
Stateless is ordinary Python, so when a function body calls `console.print()`,
the call goes straight to `console` and the library never sees it.
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
and `yield from` hands it out of the function body.
`next()` runs `greet()` up to that request and produces it.
Nothing has printed at that point,
because `greet()` sits suspended inside `need()`.
`send(Console())` answers the request and resumes the function,
which prints its greeting and finishes, raising `StopIteration`.
[Supplying the Dependency](#supplying-the-dependency)
replaces this loop with `run()` and a handler that decides which object answers each request.

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
   an object that knows how to answer `Need[Console]`.
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
At runtime it only prints the class of its argument (`function`, here)
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

`greet` is a function `ty` knows by name,
while `bound` is a function `supply()` built, described by its signature alone.
These are the expanded forms of `Depend[Need[Console], None]` and `Success[None]`.
`Need[Console]` sits in the first type parameter of `greet` and disappears from `bound`,
leaving the `Never` from the alias table.

Handling an Ability *subtracts* it from the type.
Here the subtraction leaves nothing behind:
`greet()` declares one Ability and cannot fail, so `bound` produces a `Success`.
That `Success` is a consequence rather than a requirement:
`run()` refuses only an unanswered Ability.
It accepts an Effect that can still fail,
and raises the failure as an ordinary exception
([The Error Channel](#the-error-channel)).
Binding an implementation and satisfying the type checker are the same act.

## An Effect Runs Once

A description you can hold as a value invites you to run it twice.
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
so the second `run()` of the same object gets an immediate `StopIteration` whose value is `None`:
the function never resumed, so it greets nobody and produces `None`.
Calling `bound("Alice")` again builds a fresh description, and that one runs.
`success()` is the exception because it builds no generator:
its small object's `send()` reports the value every time,
so a constant Effect replays.

This is where Stateless departs from Effect systems in other languages.
A ZIO or Effect-TS value is an immutable description that you can interpret as often as you like,
so their combinators are operations on that value:
ZIO writes `action repeat policy`, repeating the effect the value describes.
Stateless has `repeat()` and `retry()` too,
but their type is `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`.
They decorate the function,
because the function can produce a second description.
`catch()`, `throws()`, and `supply()` take functions for the same reason.

<!-- The "---" below is the author's own em-dash. Leave it. House.EmDash
     exists to catch em-dashes the author did not write. -->
<!-- vale House.EmDash = NO -->
So pass the function rather than the Effect.
A Stateless Effect is a one-shot token: build it, run it, discard it.
Storing one in a registry to run later, handing the same one to two consumers,
or keeping one around to retry after a failure---these all fail quietly,
returning `None` instead of raising an exception.
Other Effect systems let you describe the work once and decide later how many times to perform it.
In Stateless, that decision belongs to whoever still holds the function.
<!-- vale House.EmDash = YES -->

`memoize()` is the one concession, and it caches rather than replays:
it wraps the Effect in an object that records the result and hands that same result back on a second `run()`,
without performing the work again.
Like the others, `memoize()` decorates the function;
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

Run it and it raises a `MissingAbilityError`.
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

In Stateless, an unsupplied dependency is a type error,
not a production incident.
No test needs to exercise the path,
and no reviewer needs to notice the omission.

The expected type in that message names two things this chapter has not yet covered:

- `Async` is a built-in Ability for asynchronous work,
  which `run()` handles on its own.
  [Waiting on a Coroutine](#waiting-on-a-coroutine) takes it up.
- `Exception` is the error channel,
  the subject of [The Error Channel](#the-error-channel)
  and everything after it.

`run()` accepts an Effect whose Ability channel has narrowed to those two,
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

The test needs no `capsys`, no monkeypatching of `print`, and no mock.
It supplies a different `Console`, while `greet()` stays unchanged and unaware.

`as_type(Console)` is the only ceremony in that test.
It says "treat this recorder as a `Console`,"
and at runtime it returns the object it received.
`supply()` requires it because it reads the Ability from the static type of its argument,
and `Recorder` inherits from `Console` to answer the same question at runtime.
[Supplying an Interface](#supplying-an-interface) takes both halves apart,
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
so one listing holds the whole path a dependency travels.

Effects spread the way `async` does.
An `async` function's callers must also be `async`,
all the way to `asyncio.run()`.
A `Depend` function's callers must also declare the dependency,
all the way to `supply()`.
The difference is that you can declare as many Abilities as you like.

The `yield from` inside `greet_all()` does real work.
Write that loop body as a bare `greet(name)`,
and `ty` objects with an `invalid-return-type`:
"Function always implicitly returns `None`."
That looks like protection and is an accident:
that `yield from` is the only `yield` in `greet_all()`,
so deleting it turns `greet_all()` into an ordinary function,
and the type checker catches the changed shape rather than the discarded Effect.
A function with a second `yield` keeps its shape, so every check stays silent.
`greet_logged()` in [Retrofitting an Effect](#retrofitting-an-effect)
makes two requests, one for the greeting and one for the log.
If you write its first line as a bare `greet(name)`, every check passes:
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

Declaring the Ability is still manual,
but the type checker verifies the declaration.
If you annotate `greet_all()` as pure, `ty` flags the problem:

```python
# undeclared_need.py
from greet_all import greet
from stateless import Success

def greet_all(names: list[str]) -> Success[None]:
    for name in names:
        yield from greet(name)  # type: ignore
```

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

A function cannot claim to be pure while calling something impure.
Compare that to `ask_tell.py` in [Effect Management](44_Effects--Effect_Management.md#effects-by-hand),
where `greet(ask, tell)` takes its dependencies as arguments.
Nothing there stops an intermediate function from constructing its own `Console` and quietly performing an undeclared Effect.
Here, the signature and the body cannot disagree.

## Retrofitting an Effect

The second exercise in [Effect Management](44_Effects--Effect_Management.md#exercises)
has you add a `Log` Effect alongside `greet()` and count the signatures you edit.
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
while `greet()` stays unchanged.
`supply()` now provides both a `Console` and a `Log`.
Stateless leaves you those edits and saves you the hunt for them:
the type checker names each place that needs changing,
and the program builds only when you have fixed the last one.
To see that, delete `| Need[Log]` from either annotation.
If you remove it from `greet_all()`,
`ty` reports an `invalid-yield` at `yield from greet_logged(name)`,
since `Need[Log]` is not assignable to what the signature now declares.

The type checker covers dependencies passed as parameters too.
If you forget the new argument at a call, `ty` reports a `missing-argument`.
The difference is how many places you edit.
A new parameter changes every call site along with every signature,
and each function in between accepts an object it does not use.
A new Ability changes the signatures alone:
`yield from greet_logged(name)` stays as it is, and the instance appears once,
at `supply()`.

Multiple Abilities combine with `|` because the union describes one request at a time.
Each `yield` in `greet_all()` produces either a `Need[Console]` or a `Need[Log]`,
not both at once.
Over the whole run it makes both kinds of request,
so `supply()` must provide a `Console` and a `Log`.

The repeated union invites a `type` alias,
and the book's own habits normally endorse one.
Under `ty` 0.0.77 the alias checks the same as the written-out signature:
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
from dataclasses import dataclass
from stateless import Depend, Need, need

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
The two diverge when the dependency sits three calls deep.
The parameter version then adds two parameters to every function on the path,
while this version still changes only the row.

## Builtin Dependencies

Every dependency so far was one this chapter defined.
Stateless also ships three of its own:

- `Console` in `stateless.console`,
  whose `print_line()` and `read_line()` accessors call its `print()` and `input()` methods,
- `Files` in `stateless.files` that reads a whole file,
- `Time` that [Adding Behavior to an Existing Effect](47_Effects--Stateless_in_Practice.md#adding-behavior-to-an-existing-effect)
  supplies to `retry()`.

All three are concrete classes rather than interfaces,
and the accessors name those classes,
so `isinstance()` accepts an instance of the class or a subclass and nothing else.
A structurally identical double fails with a `MissingAbilityError` no matter what `as_type()` claims.
A double for the builtin `Console` must inherit from it,
and that `Console` implements `input()` as well as `print()`,
so a double that overrides only `print()` reads live stdin.
[Supplying an Interface](#supplying-an-interface), next,
explains the source of that cost and how an interface avoids it.

`read_file()` is also the library's own example of both channels at once:
its accessor carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect,
so its type declares an Ability and two failures together.

For illustration, this chapter builds a `Console` rather than using the one from Stateless.
In your own code, first check what the library declares.

## Supplying an Interface

[Swapping the Implementation](#swapping-the-implementation)
substituted a `Recorder` for a `Console` but postponed the reason for using `as_type(Console)`.
That call answers two questions, for two audiences: static analysis and runtime.

First, the static issue.
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
the type checker believes it even when the object has no relation to `Console`.
`as_type(Console)` returns a function annotated `(Console) -> Console`,
so passing it an object that fails to implement `Console` is a type error.
`as_type()` widens to a supertype; `cast()` replaces one type with any other.

Second, the runtime issue, which the library decides using `isinstance()`.
`supply()` builds a handler that checks each request with `isinstance(instance, ability.t)`,
where `ability.t` is the class inside the `Need`.
In `test_greeter.py`, `ability.t` is `Console` and `instance` is `recorder`,
and `isinstance(recorder, Console)` succeeds because `Recorder` inherits from `Console`.
So two separate things make that test work:
`as_type(Console)` satisfies the type checker,
and the inheritance satisfies the runtime check.

The inheritance has a cost.
`Recorder` overrides everything it inherits from `Console`,
so today the parent contributes only the name `isinstance()` matches.
Add a `read_line()` method to `Console` tomorrow,
and `Recorder` inherits the real one silently,
so a test meant to record performs live console I/O.
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

The second of the three things [a full EMS does](44_Effects--Effect_Management.md#effect-management-systems)
is separate each Effect's interface from its implementation.
`Console` as a `Protocol` holds no implementation.
`Terminal` is one implementation and `Recorder` is another,
and `greet()` names neither.
Because a `Protocol` matches on structure,
`Recorder` qualifies as a `Console` without inheriting from `Console`.
`supply()` matches requests with `isinstance()`,
and `isinstance()` accepts only a `@runtime_checkable` Protocol,
so the Protocol carries that decorator;
without it the first request raises a `TypeError`.

`as_type()` is still needed.
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

Both lines print, because `isinstance()` accepts that `Terminal` matches `Console` structurally.
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
which leaves `greet()`'s `Need[Console]` in place;
the unhandled request passes through to `run()`, where the error appears.
An interface needs the `as_type()` upcast more than a base class does:
a concrete `Console` you can instantiate and supply directly,
while an interface reaches `supply()` only through an implementation.

`console_protocol.py` is the form to write in production.
Most listings in these two chapters use a concrete `Console` instead,
because under the interface,
supplying an implementation directly requires `as_type()`.
That is a real cost of using an interface.
[Composing a Program](47_Effects--Stateless_in_Practice.md#composing-a-program)
declares its Abilities as `Protocol`s and shows how to avoid that cost:
write one boundary function whose parameter annotations name the interface types,
and call `supply()` inside it.
The parameter annotation upcasts the argument,
so no call site needs `as_type()`.
An annotated local variable gets no such upcast:
`screen: Console = Terminal()` narrows back to `Terminal` at the assignment,
so `supply(screen)` builds a `Need[Terminal]` handler again.
Every function between that boundary and the Effect reads the same under either form.

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

`Terminal` and `Capture` share no base class and know nothing of each other.
Both satisfy `Console` structurally, so `isinstance()` accepts either,
and `supply()` hands over whichever it examines first.
Alice's greeting reaches the screen and leaves `capture` empty.
Swapping the two arguments sends Bob's greeting into `capture` and prints nothing.
`greet()` and the type checker see the two runs as identical,
because both bindings have the same type.
Both instances go through `as_type(Console)`,
since each is a `Console` only structurally.

Here Stateless gives up something ZIO keeps.
ZIO reports two implementations of one requirement as a compile-time error naming both candidates,
because its `provide` resolves the dependency graph during compilation.
`supply()` resolves at runtime by scanning its arguments,
so the same mistake produces a program that runs and does the wrong thing.
Give Abilities distinct method names when that ambiguity is possible,
and supply one implementation per Ability.

## Dependency Injection

Dependency injection (DI) has one goal:
separate a function from the choice of what it uses.
A function that constructs its own `Console` locks itself to that class,
while a function handed a `Console` can receive a recorder in a test,
a terminal in production, and a scripted one in a demo.

Conventional DI meets that goal with a container.
The container maps each type to the instance that satisfies it,
and hands those instances out during execution:

```python
# dependency_injection.py
from typing import Any, Final
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

try:
    greet("Alice")
except NotRegistered as e:
    print(f"{type(e).__name__}: {e}")
#: NotRegistered: Console
register(Console, Console())
greet("Alice")
#: Hello, Alice!
```

`register()` puts an instance in, and `get()` looks up an instance by type,
at the point where the program needs it.
The type is the registration key,
so `register(Console, Recorder())` binds an implementation to the type the caller requests.
A dictionary matches the key exactly,
so a subclass registered under its own name is invisible to `get(Console)`.
`supply()` takes bare instances and matches a request with `isinstance()` instead,
which is why two instances that satisfy one `Need` are ambiguous
([When Two Implementations Match](#when-two-implementations-match)).
The DI registration key also does the work `as_type(Console)` does for `supply()`,
which reads each Ability from its argument's static type:
`supply(recorder)` is a `Handler[Need[Recorder]]`,
and no `Need[Console]` matches it
([Supplying an Interface](#supplying-an-interface)).

`DI_CONTAINER` holds instances of unrelated types,
so `Any` is the only type its values can share.
The key carries the type information,
but a homogeneous `dict` has no way to say "the value under key `type[T]` is a `T`,"
so that invariant lives in `register()`'s signature rather than in the container.

`greet()`'s body matches `greeter.py`'s `greet()` line for line,
apart from `console: Console = get(Console)` in place of `console = yield from need(Console)`.

The first `greet("Alice")` fails at runtime because nothing has registered a `Console` yet;
the second succeeds because the binding now exists.
The two calls are identical, and the types say nothing about registration,
so the type checker has nothing to report.

This `greet()` has the same signature as the `untyped_greet.py` version in [Declaring a Dependency](#declaring-a-dependency).
Both read `(str) -> None`, and both hide a `Console`.

DI meets its goal: the `Console` is swappable.
But it relocates a [side cause](44_Effects--Effect_Management.md#what-is-an-effect)
rather than declaring one, so the type checker never validates the dependency.

An EMS sets a higher bar:
the dependency must appear in the signature so the type checker can verify it,
which is why the EMS `greet()` returns `Depend[Need[Console], None]` while `dependency_injection.py`'s returns `None`.
An EMS tracks every dependency so the type checker catches the errors that would otherwise depend on programmer memory and exhaustive testing.

Stateless has no container.
`supply()` is a function call, and its arguments are the bindings.
This has three consequences:

1. Stateless checks come before the program runs.
   DI discovers a missing registration only when something asks for it.
   That ask can come at startup or much later, on a path no test exercised.
   If you remove the `# type: ignore` from `unsupplied.py`,
   `ty` reports the unsupplied `Need[Console]`
   ([Forgetting to Supply](#forgetting-to-supply)).

2. Stateless bindings are per call rather than per process.
   DI usually holds one type binding for the life of the program.
   `supply()` binds for one execution of one Effect,
   so two bindings for the same type can be live at once,
   as the screen and memory `Console`s were in [When Two Implementations Match](#when-two-implementations-match).
   Test cases need no reset between them.

   Handlers also layer.
   An Ability a handler cannot answer travels further out,
   so `supply(Log())(greet_all)` still has the type `(list[str]) -> Depend[Need[Console], None]`,
   and wrapping that in `supply(Console())` leaves `(list[str]) -> Success[None]`.
   You can bind some Abilities near the Effect and the others at the edge,
   with the type recording what each layer left behind.
   DI has one flat registry and no equivalent layering.

3. Stateless function requirements live in the function type.
   DI leaves that information in the bodies that ask for it.
   You must read the implementation to learn what a DI function needs.
   `holds()` declares `Need[Material] | Need[Nailer]` in its signature,
   and a caller that does not supply them inherits the requirement.

The requirement that callers inherit is also the cost.
Adding a dependency to a working function rewrites the return type of every function above it,
as [Retrofitting an Effect](#retrofitting-an-effect) showed with `Need[Log]`;
DI absorbs the same change in silence, with no signature recording it.

Type checking is the earliest practical time to discover these errors,
so the trade concerns churn and coupling rather than correctness.
A function that never logs still names `Need[Log]` in its type,
and taking that dependency back out later moves every signature on the path a second time.
People made the same complaint against Java's checked exceptions,
which [Effect Management](44_Effects--Effect_Management.md#catch-the-exception-you-expect)
describes failing this way,
and that complaint is why [Effects Propagate, and the Type Checker Verifies It](#effects-propagate-and-the-type-checker-verifies-it)
compares the spread to `async`.

### A Default Binding

A DI container often lets you register a fallback for a type nobody else provides.
Stateless has no such registration, and `need()` takes no default argument.
Layering produces one all the same.
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

`fallback` is an ordinary handler, applied at the edge,
while `chosen` is a second handler already applied to `greet`.
The first run has nothing between `greet()` and that edge,
so the default answers.
The second wraps `greet()` in its own `supply()` first,
which empties the Ability channel before `fallback` sees a request.
The handler nearest the Effect wins,
and the outer one answers only what remains.
The type records this: `chosen` is already `(str) -> Success[None]`,
so `fallback(chosen)` adds nothing the type checker did not know.

A default costs you the guarantee that made `Need` worth declaring.
An Effect that fails the type check for a missing `Console` now compiles and runs,
and a forgotten binding shows up as a wrong-looking result rather than an error.
Use one for a genuine default, a null logger or a no-op console,
not to quiet a type checker that is telling you something.

## Waiting on a Coroutine

`Async` has appeared so far only inside error messages,
where `run()` answers it without anyone asking for it.
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
It reads `Depend[Async, str]`,
where every dependency so far read `Depend[Need[...], ...]`.
The rule is the same in both cases: the channel holds Abilities.
`Async` is an Ability, so it sits there bare.
`Console` is an ordinary class,
and `Need[Console]` is the Ability that asks for it.
The first type parameter accepts only `Ability` subclasses,
so the type checker rejects `Depend[Console, None]` at the annotation.
[Abilities Are Not Special](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
writes an Ability from scratch and takes that type bound apart.

An `Async` request carries a coroutine and asks the driver to await it,
and `run()` does that with the event loop it starts.
So nothing supplies `Async`: the driver answers it,
and `supply()` handles only a `Need`.

`report()` is not an `async def` and contains no `await`,
yet its result comes from a coroutine.
`wait()` hands the coroutine out as a request and the driver awaits it,
so the asynchrony stops at the Ability channel instead of spreading to `report()` and everything that calls it.

You need `wait()` at the boundary where a coroutine enters the Effect world.
A function that already returns an Effect needs no `wait()`,
because `yield from` composes the two directly.
`stateless.time.sleep()` is such a function,
and it pairs an `Async` request with a dependency.
This listing uses `sleep()` without a `wait()`:

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
`supply(Time())` binds an instance the way `supply(Console())` did.

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
and under a millisecond here.

`delayed_sum()` stays unchanged and cannot tell the two clocks apart.
The subclass goes through `as_type(Time)`,
for the reason in [Supplying an Interface](#supplying-an-interface).

In `Instant`, `waited` is a field because `Time` is a frozen data class and a subclass must carry `frozen=True` too.
Freezing prevents rebinding `waited`, not appending to the list it holds.

## Where to Call `run()`

`run()` starts an event loop and drives the Effect inside it:
its entire body is `return asyncio.run(run_async(effect))`.
That has a consequence when you incorporate Stateless into an existing application.
`asyncio.run()` refuses to start a second event loop inside a running one,
so you cannot call `run()` from any `async def`:

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

The run also prints a `RuntimeWarning` to standard error, which the output above
(standard output only) omits.
`run()` builds the `run_async()` coroutine and hands it to `asyncio.run()`,
which raises a `RuntimeError` because a loop is already running,
so the coroutine is never awaited.
The warning is harmless, since that coroutine never started,
and it is a reliable sign of this mistake:
it appears whenever asynchronous code calls `run()`.

`run_async()` is the same driver packaged as a coroutine, so you `await` it.
A synchronous program calls `run()` once at its outermost edge.
A program that is already asynchronous, a web service or a bot,
awaits `run_async()` at the edge of each request.
Picking the wrong one is a runtime error rather than a type error,
one of the few mistakes in this chapter that get past the type checker.

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
`ty check scores.py` reports what it became:

```text
info[revealed-type]: Revealed type
  --> scores.py:12:17
   |
12 |     reveal_type(score)
   |                 ^^^^^ `(name: str) ->
   |                       Generator[KeyError, Any, int]`
```

This is `Try[KeyError, int]` with [the alias](#the-effect-type) expanded:
it needs nothing, can fail with a `KeyError`, and produces an `int`.
The `Generator`'s first parameter carries `A | E`
([The Effect Definition](#the-effect-definition)).
`Try` fills `A` with `Never`, so `Never | KeyError` reduces to `KeyError`.

`Try` carries the same idea as the `Result` type in [Error Handling](42_Functional--Error_Handling.md#turning-exceptions-into-results),
built differently.
A `Result` is a wrapper the function returns at once,
and the caller matches on it.
A `Try` is a description that runs nothing until something drives it,
and its failure arrives as a yielded value rather than a returned one.
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
the `KeyError` arrives as a value, not as a raised exception:

```python
# error_is_yielded.py
from scores import score

effect = score("Carol")
print(repr(next(effect)))
#: KeyError('Carol')
```

The body raised the exception.
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

This uses all three parameters of `Effect[A, E, R]`.
`announce()` needs a `Console`, can fail with `KeyError`, and produces nothing.
If you drop the `KeyError` from the annotation,
`ty` points at the `yield from score(name)` line.
Every function on the path has to declare it.

### Declaring Is Not Handling

Declaring an error leaves handling it up to you.
`run()` accepts an Effect with a failure still in its error channel:
the driver throws the failure back into the generator,
and with no `catch()` in the way it propagates out of `run()` as an ordinary exception:

```python
# error_escapes.py
from announce import announce
from greeter import Console
from stateless import run, supply

try:
    run(supply(Console())(announce)("Carol"))
except KeyError as e:
    print(type(e).__name__, e)
#: KeyError 'Carol'
```

The error channel records the failures that can occur,
without forcing you to handle them.
`run()` turns any that reach it back into normal Python exceptions.

The channel carries only the failures `@throws` lifted into it.
An exception raised where no `@throws` wraps the body bypasses the type,
a hole that [Nothing stops an undeclared Effect](47_Effects--Stateless_in_Practice.md#nothing-stops-an-undeclared-effect)
examines.

Because the driver throws the failure back in,
an ordinary `try`/`except` around a `yield from` catches it.
Catching is different from handling.
The exception leaves as a yielded value, travels out to `run()`,
and comes back down into the innermost suspended frame,
where the `except` clause runs; the `KeyError` stays in the channel,
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
because `catch()` matches the yielded value before the driver gets it and abandons the inner generator where it stands.

## Turning an Error Into a Value

`catch()` empties the error channel the way `supply()` empties the Ability channel,
but the two do different things with what they remove.
`supply()` provides the Ability inside the Effect,
so the Ability parameter becomes `Never` and the result type omits the `Console`
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
The error departs the error type parameter, which becomes `Never`,
and joins the result type parameter.
That makes `value` something to `match` on rather than an exception to catch.

`Success` describes the Effect rather than the lookup: both channels are empty,
with nothing left to supply and no failure for `run()` to raise.
`reporter` is a function that builds an Effect,
as its `Callable[[str], Success[None]]` annotation states:
give it a `str` and it produces an Effect that needs nothing and cannot fail.
`run()` drives that Effect,
so `reporter("Alice")` comes first and `run()` second.
The Effect "succeeds" at producing either a score or a `KeyError` that reports the missing score.
A raised `KeyError` is a failure.
A returned `KeyError` is data.

Moving the error into the result forces every caller to face it.
Drop the `match` and use `value` directly as a number,
and the type checker objects:

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

This is the same guarantee the `Result` type gives in [Error Handling](42_Functional--Error_Handling.md#a-result-type),
and `catch()` reaches it without rewriting the body of `score()`.

### Multiple Errors

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
and the conversion raises a `ValueError` for text that is not a number,
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
`one_unhandled()` does not handle `ValueError`,
so the signature must declare that failure.
Calling it on `"Bob"` carries that failure up to the `run()` call at the program's edge,
which raises it as an ordinary exception,
like `error_escapes.py` did for a single error.
`pytest.raises(ValueError)` is the whole assertion:
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
so an `Async` request or a declared failure can still be in flight when you call it.

The channels resolve differently:

- `unsupplied.py` showed `run()` refusing an Effect that still declares an Ability,
  before the program starts.
- `error_escapes.py` showed `run()` accepting an Effect that still declares a failure,
  then raising that failure at the edge.

The difference follows from what each channel holds.
An unbound dependency has no answer anywhere in the program,
so a driver that meets one can only stop.
An unhandled failure has a clear meaning at the boundary, raise the exception,
which Python does with or without the Effect type.
So the two guarantees differ:
you must resolve a dependency before anything runs,
while a declared failure travels in the type until you choose where to handle it.
The type checker covers both, and forgetting either is a type error.

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
    Then explain why the test function body needed no change.
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
    Explain what each one caught,
    and why `ty` catches assigning a dropped request but not discarding one.
8.  Build a registry of Effects:
    a `dict[str, Success[None]]` that maps each of two names to `supply(Console())(greet)(name)`.
    Run every entry, then run every entry a second time,
    and record what prints on each pass.
    Change the values to functions that build the Effect when called,
    and run both passes again.
    Explain which of the two shapes `retry()` requires,
    and why its type is `Callable[P, Effect[...]] -> Callable[P, Effect[...]]` rather than an operation on an Effect.
9.  Write `report_all()`,
    which calls `stateless_coroutine.py`'s `report()` for three URLs with `yield from` and returns the three results.
    Importing that module runs its own unguarded `print(run(...))`,
    so expect one line of its output before yours.
    Work out what its annotation must be, and confirm it with `ty`.
    Then call it from inside an `async def`,
    once with `run()` and once with `await run_async()`,
    and record what each one does.
    Explain why `ty` accepted both.
10. `announce()` declares `Effect[Need[Console], KeyError, None]`.
    Give it a second failure:
    a helper that formats the score and raises a `ValueError` on a negative one,
    lifted with `@throws(ValueError)`.
    Follow `ty` until the program builds,
    add a negative score to `scores.py`'s `SCORES` so the new failure can fire,
    then run it on a name that triggers each failure and on one that succeeds,
    and say where each failure surfaced.
    Then delete `ValueError` from `announce()`'s annotation and record what `ty` reports and at which line.
11. `ambiguous_supply.py` picks its `Console` by argument order.
    Add a third implementation and predict, before running it,
    which of the six orderings send Alice's greeting where.
    Then follow the section's advice:
    give the recording implementation a method name the screen one does not have,
    declare each as its own `Protocol`,
    and show that handing the wrong implementation to an Effect is now a type error rather than a silent choice.
    Two implementations sharing one method name stay ambiguous under both `Protocol`s,
    so say what the technique does and does not buy.
