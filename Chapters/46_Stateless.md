# Stateless

[Effect Management](44_Effect_Management.md#library-effect-management)
introduced library Effect systems.
[Stateless](https://github.com/suned/stateless)
is a library that implements an Effect Management System (EMS).

Stateless encodes an Effect's dependencies and failures into the return type of a function,
and a type checker verifies that every caller either absorbs the Effects or carries them forward.
Forget to declare a dependency and the check fails.
Forget to supply one and the check fails.
That is the Effect tracking and delayed binding of a full EMS,
with the bookkeeping moved into the type system.

Stateless is built on generators.
[Generators](45_Generators.md)
covered the three-parameter `Generator` annotation,
a driver that answers a generator's requests one `send()` at a time,
and `yield from`, which composes generators and produces the inner one's return value.
Every Effect here travels that path.
Stateless supplies the vocabulary for the requests and the driver that answers them.

This chapter covers the two channels an Effect declares:
the dependencies it needs and the ways it can fail.
[Stateless in Practice](47_Stateless_in_Practice.md)
builds examples using those channels.

My understanding of Effects came from work with Bill Frasure and James Ward as we created [Effect Oriented Programming](https://effectorientedprogramming.com/).
Some of the examples in these two chapters were derived from that book.

## The Effect Type

Stateless builds everything atop a single type with three type parameters:

```python
Effect[A, E, R]
```

Those three parameters answer the three questions [Effect Management](44_Effect_Management.md#library-effect-management)
asked of an Effect signature:

- `A` is what the computation needs, an ability.
- `E` is how it can fail.
- `R` is what it produces.

For example:

```python
Effect[Need[Console], KeyError, None]
```

This particular Effect needs a `Console`, it can fail with a `KeyError`,
and it produces nothing.
`Need[Console]` is a request for a `Console` rather than the `Console` that answers it;
[Nothing Runs Yet](#nothing-runs-yet) explains why the type names the request.

Although you can write the full `Effect` signature each time,
three aliases are provided for the most common cases.
Each one fills in `Never` for a type parameter that is not used:

| Alias | Meaning |
|---|---|
| `Success[R]` | Needs nothing, cannot fail, produces `R` |
| `Depend[A, R]` | Needs `A`, cannot fail, produces `R` |
| `Try[E, R]` | Needs nothing, can fail with `E`, produces `R` |

`Never` is Python's *bottom type*:
it has no values and is a subtype of every other type.
`Success[R]` promises there is no ability it can request and no error it can yield.

## The Effect Definition

`Effect` is an alias for a `Generator`:

```python
Effect: TypeAlias = Generator[A | E, Any, R]
```

The `Generator` yields either an ability `A` or an exception `E`,
and eventually returns a result `R`.
Our example becomes:

```python
Generator[Need[Console] | KeyError, Any, None]
```

`A` and `E` share the first type parameter, and `R` is the third.
That leaves the second,
which [Generators](45_Generators.md#annotating-a-generator)
taught you to read as "what comes back from a `yield` call."
That `Any` is deliberate; [Why `yield from`](#why-yield-from)
explains it after you have seen a request in action.

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
similar to the `drive()` of [Generators](45_Generators.md#a-generator-is-a-description).
`run()` primes the generator, answers each request, and returns the result.
Nothing computes until `run()` is called, and a program calls `run()` only once,
at its outermost edge.

`Success[int]` says `double()` is pure.
It cannot read anything, and it cannot fail.

Notice that `double()` contains no `yield`, so it is not a generator function.
It does not need to be.
Python decides generator-function status from the body alone:
`yield` in the body makes a function a generator function,
and nothing else does, not the return annotation and not the object returned.
The object that implements the generator protocol is the Effect that `success()` builds.
`double()` calls `success()` and returns that Effect,
which no more makes `double()` a generator than returning a list would make it a list.
The annotation promises that calling `double()` produces an Effect,
and `run()` can drive anything that keeps that promise.
`success()` exists for yield-free functions like this one.
In a generator function, an ordinary `return` sets the result;
wrap it in `success()` there and the checker reports a return-type mismatch.

`double()` needs nothing beyond its argument,
so it gains nothing from being an Effect.
The gain appears when a function depends on something created elsewhere,
such as a console, a file, or a network connection.

## Declaring a Dependency

`Need` is how Stateless does dependency injection.
A `Need` is a request for an instance, and something else answers it.
`need(SomeClass)` is an Effect that produces an instance of `SomeClass`,
without saying where that instance comes from:

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
It lives in `utils/` because both this chapter and the next one import it.
Compare that to the version that calls `print()` directly:

```python
# untyped_greet.py
def greet(name: str) -> None:
    print(f"Hello, {name}!")

greet("Alice")
#: Hello, Alice!
```

That signature is a lie by omission.
`-> None` claims the function returns nothing and mentions nothing else.
However, the body writes to standard output, which is a side effect.
That omission matters: printing is everything the function does.
The caller cannot see the dependency, redirect the output,
or test the function without capturing stdout.
`Depend[Need[Console], None]` states the dependency.
A caller now has two options: supply a `Console`,
or declare the same need in its own signature and pass the requirement to its own caller.
A caller that does neither fails the type check.

In `greeter.py`, two details deserve attention:

1. `greet()` is a generator function, because it contains `yield from`,
   so calling it builds the Effect its signature declares.
2. `console` really is a `Console` to the type checker,
   so `console.print()` is checked the same as any other method call.
   The dependency is deferred without becoming untyped.

## Nothing Runs Yet

Calling `greet()` performs no work.
It simply returns a `Generator`:

```python
# describe_only.py
from greeter import greet

description = greet("Alice")
print(type(description).__name__)
#: generator
```

`greet("Alice")` builds a description of a greeting.
This is the description/execution split from [Effect Management](44_Effect_Management.md#library-effect-management).
A language with builtin Effects intercepts an Effect where it is performed.
Stateless cannot, because it is ordinary Python:
when a function body calls `console.print()`,
nothing hands control to the library.
A library can act on objects handed to it, and on nothing else.
For Stateless to see the request for a `Console`,
that request must be an object: the `Need[Console]` that `need(Console)` builds.
`yield from` then hands that object out of the function body.
It suspends `greet()` and passes the `Need[Console]` to whatever is driving the generator,
which provides a `Console` and resumes the function.

## Why `yield from`

The request in `greet()` is written `console = yield from need(Console)`,
not `console = yield Need(Console)`.
The reason is the `Any` in the Effect definition.

A generator has one SendType for its whole life.
An Effect does not:

- Using `yield` to request a `Need[Console]` should get a `Console`.
- Using `yield` to request a `Need[Log]` should get a `Log`.

What comes back depends on which ability the `yield` requested.
One SendType cannot vary from one `yield` to the next.
Pin it to `Console` and the checker reads `yield Need(Log)` as producing a `Console`.
The `send()` channel must be able to carry any type, so the SendType is `Any`.

`yield from` recovers the precision that `Any` gives up,
so a request can produce an answer whose type the checker knows.
A bare `yield` produces the SendType, the parameter forced to `Any`.
`yield from` produces the inner generator's `ReturnType`,
which does not have that conflict.
`need(Console)` builds a small generator that serves one request,
so its `ReturnType` can name a specific type.
`need()` returns `Depend[Need[T], T]`,
which expands to `Generator[Need[T], Any, T]`.
Calling `need(Console)` binds `T` to `Console`,
so `console = yield from need(Console)` takes its value from that final `Console` and never consults the `Any`.

This is why every request in this chapter is written as `yield from` rather than `yield`,
and why the custom abilities of [Abilities Are Not Special](47_Stateless_in_Practice.md#abilities-are-not-special)
get a small function of their own.

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

The `bound` assignment does three things:

1. `supply(Console())` builds a *handler*,
   an object that knows how to answer `Need[Console]`.
2. Calling the handler on `greet` returns a new function `bound` that answers the requests `greet()` makes.
3. Calling that function with `"Alice"` builds an Effect with nothing left to supply,
   which `run()` executes.

Supplying the `Console` changes the type:

```python
# reveal_bound.py
from typing import reveal_type
from greeter import Console, greet
from stateless import supply

bound = supply(Console())(greet)
reveal_type(greet)
reveal_type(bound)
```

`reveal_type()` is a message to the type checker.
Running the script tells you nothing useful,
because at runtime it reports the class of its argument (`function`, here)
on standard error.
The answer comes from `ty check reveal_bound.py`:

```text
info[revealed-type]: Revealed type
 --> reveal_bound.py:7:13
  |
7 | reveal_type(greet)
  |             ^^^^^ `def greet(name: str) ->
  |                   Generator[Need[Console], Any, None]`
  |

info[revealed-type]: Revealed type
 --> reveal_bound.py:8:13
  |
8 | reveal_type(bound)
  |             ^^^^^ `(name: str) -> Generator[Never, Any, None]`
  |
```

`greet` is a function `ty` knows by name, so it reports the definition;
`bound` is a function `supply()` built, described by its signature alone.
Those are the expanded forms of `Depend[Need[Console], None]` and `Success[None]`.
`Need[Console]` sat in the first type parameter of `greet` and is gone from `bound`,
replaced by the `Never` the alias table promised.

Handling an ability *subtracts* it from the type.
Here the subtraction leaves nothing behind:
`greet()` declares one ability and cannot fail, so `bound` produces a `Success`.
That `Success` is a consequence, not a requirement.
What `run()` refuses is an unanswered ability.
It accepts an Effect that can still fail,
and raises the failure as an ordinary exception
([The Error Channel](46_Stateless.md#the-error-channel)).
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

The second `run()` of the same object greets nobody and produces `None`.
The generator is exhausted,
so `run()` gets `StopIteration` immediately and reports the return value of a function that never resumed.
Calling `bound("Alice")` again builds a fresh description, which works.
`success()` is the exception because it is not a generator at all:
it builds a small object whose `send()` reports its value every time,
so a constant Effect replays.

This is where Stateless departs from Effect systems in other languages.
A ZIO or Effect-TS value is an immutable description that can be interpreted as often as you like,
so their combinators are operations on that value:
ZIO writes `action repeat policy`, repeating the effect the value describes.
Stateless has `repeat()` and `retry()` too,
but they are typed `Callable[P, Effect[...]] -> Callable[P, Effect[...]]`.
They decorate the function,
because the function is what can produce a second description.
`catch()`, `throws()`, and `supply()` take functions for the same reason.

The design rule that follows from this is to pass the function rather than the Effect.
A Stateless Effect is a one-shot token: build it, run it, discard it.
Storing one in a registry to run later, handing the same one to two consumers,
or keeping one around to retry after a failure---these all fail quietly,
returning `None` instead of raising an exception.
Other Effect systems let you describe the work once and decide later how many times to perform it.
In Stateless, that decision belongs to whoever still holds the function.

## Forgetting to Supply

Let's see what happens when we break it.
Give `run()` an Effect that still needs a `Console`:

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

This raises a `MissingAbilityError`, but if we remove the `# type: ignore`,
`ty` rejects the program before it runs:

```text
error[invalid-argument-type]: Argument to function `run` is incorrect
 --> unsupplied.py:7:9
  |
7 |     run(greet("Alice"))
  |         ^^^^^^^^^^^^^^ Expected
  |         `Generator[Async | Exception, Any, Unknown]`, found
  |         `Generator[Need[Console], Any, None]`
```

A dependency that was never bound is a type error, not a production incident.
No test had to exercise the path.
No reviewer had to notice the omission.

The expected type in that message names two things this chapter has not yet covered:

- `Async` is a built-in ability for asynchronous work,
  which `run()` handles on its own.
- `Exception` is the error channel.

`run()` accepts an Effect whose ability channel has narrowed to those two,
which is all that remains once every other ability has been supplied.
`greet("Alice")` still carries `Need[Console]`,
so it does not pass type checking.

## Swapping the Implementation

`Need` creates a delayed binding.
This means we can change that binding.
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

There is no `capsys`, no monkeypatching of `print`, and no mock.
The test supplies a different `Console`,
while `greet()` is unchanged and unaware.

At runtime, `as_type()` is the identity function and returns the object it was given.
Its purpose is the annotation.
Handing `recorder` straight to `supply()` would build a handler for `Need[Recorder]`,
but `greet()` asks for `Need[Console]`, a different ability.
`as_type(Console)(recorder)` says "treat this as the `Console` it implements,"
so `supply()` builds the handler that `greet()` is waiting for.
You need `as_type()` when you supply an implementation for a declared interface.
`typing.cast(Console, recorder)` produces the same result here,
but the two are not interchangeable.
`cast()` is an unchecked assertion,
believed by the type checker even when the object has no relation to `Console`.
`as_type(Console)` returns a function annotated `(Console) -> Console`,
so an object that does not implement `Console` is an argument-type error at that call.
It can widen a type to a supertype and nothing more.

When `greet()` yields a `Need[Console]`,
the library decides which supplied instance provides that `Need`.
This pairing happens out of sight of the listing.
The handler that `supply()` builds tests each request with `isinstance(instance, ability.t)`,
where `ability.t` is the class inside the `Need`.
Here `ability.t` is `Console` and `instance` is `recorder`,
so the check is `isinstance(recorder, Console)`.
It succeeds because `Recorder` inherits from `Console`.
So the two moves in the test serve two audiences:
`as_type(Console)` satisfies the type checker,
and the inheritance satisfies the `isinstance()` check.
Every matching request over the Effect's run receives that same instance,
which is why the test can read the results back out of `recorder` afterward.

`Recorder` inherits `Console`'s printing implementation and overrides all of it.
Nothing of the parent survives but the name that `isinstance()` looks for.
The cost arrives later.
Add a `read_line()` method to `Console`,
and `Recorder` inherits the real one without a word of warning,
so a test meant to record instead performs live console I/O. Make the ability an interface and there is no implementation to inherit by accident:

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

The second of the three things [a full EMS does](44_Effect_Management.md#effect-management-systems)
is separate each Effect's interface from its implementation.
`Console` is now that interface and holds no implementation.
`Terminal` is one implementation and `Recorder` is another,
and neither is named anywhere in `greet()`.
Because a `Protocol` matches on structure,
`Recorder` qualifies without inheriting from anything.
`@runtime_checkable` is required because `supply()` uses `isinstance()`.

This is the form to write in production.
The smaller listings that follow continue importing `greeter.py`'s concrete `Console`,
because a supply site for a `Protocol` ability needs help naming the interface:
`supply(Console())` becomes `supply(as_type(Console)(Terminal()))`.
That is a real cost of using the interface, not only a shortcut for the book.
[Composing a Program](47_Stateless_in_Practice.md#composing-a-program)
declares its abilities as `Protocol`s and shows how to stop repeating that cost:
write one boundary function whose parameters are annotated with the interface types,
and call `supply()` inside it.
The parameter annotation performs the upcast, so no call site needs `as_type()`.
Everything in between works the same under either form.

## Builtin Abilities

You might not need to declare an ability.
Stateless includes three of its own:

- `Console` in `stateless.console` with `print_line()` and `read_line()` accessors,
- `Files` in `stateless.files` that reads a whole file,
- `Time` that [Adding Behavior to an Existing Effect](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect)
  supplies to `retry()`.

This chapter builds its own `Console` for illustration.
In your own code, check what the library already declares first.

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
`Console` and `greet()` reappear here from [Declaring a Dependency](#declaring-a-dependency),
with `Console` as the concrete class rather than the `Protocol` shown since.
`greet_all()` must declare the `Console` it never touches:

```python
# greet_all.py
from stateless import Depend, Need, need, run, supply

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_all(names: list[str]) -> Depend[Need[Console], None]:
    for name in names:
        yield from greet(name)

if __name__ == "__main__":
    run(supply(Console())(greet_all)(["Alice", "Bob"]))
#: Hello, Alice!
#: Hello, Bob!
```

This is the same virality `async` has.
An `async` function's callers must also be `async`,
all the way to `asyncio.run()`.
A `Depend` function's callers must also declare the dependency,
all the way to `supply()`.
The difference is that you can declare as many abilities as you like.

The `yield from` is not optional.
Remove it here and `ty` objects with an `invalid-return-type`:
"Function always implicitly returns `None`."
That looks like protection, but read it again.
It was the only `yield` in `greet_all()`,
so deleting it turned `greet_all()` into an ordinary function,
and the checker caught the function's changed shape, not the discarded Effect.
Keep any other request in the body and the same mistake is silent.
`greet_logged()` in [Adding an Effect Deep in the Stack](#adding-an-effect-deep-in-the-stack)
makes two requests.
Strip the `yield from` in front of its `greet(name)` and every check passes:
`ty` and `ruff` report nothing, the program runs, the log gains both entries,
and no greeting is printed.
Each `greet(name)` builds a description, which the loop discards unrun.
The same trap exists in ZIO for the same reason.
An Effect written as a bare statement is a discarded value there too,
and the ZIO fix is `.run` where Python's is `yield from`.
The hazard belongs to deferred execution rather than to generators.
When an Effect appears to do nothing, look for a missing `yield from`.

Declaring the ability is still manual.
The benefit is that the declaration is checked.
Annotate `greet_all()` as pure and `ty` flags the problem:

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
Compare that to `ask_tell.py` in [Effect Management](44_Effect_Management.md#effects-by-hand),
where `greet(ask, tell)` took its dependencies as arguments.
Nothing there stopped an intermediate function from constructing its own `Console` and quietly performing an undeclared Effect.
Here, the signature and the body cannot disagree.

## Adding an Effect Deep in the Stack

The second exercise in [Effect Management](44_Effect_Management.md#exercises)
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
while `greet()` is unchanged.
`supply()` now provides both a `Console` and a `Log`.
Stateless does not save you those edits.
It saves you from hunting for the functions that need them:
the checker names each place that needs changing,
and the program does not build until the last one is fixed.
To see that, delete `| Need[Log]` from either annotation.
Remove it from `greet_all()` and `ty` reports an `invalid-yield` at `yield from greet_logged(name)`,
since `Need[Log]` is not assignable to what the signature now declares.

Dependencies passed as parameters are checked too.
Forget the new argument at a call and `ty` reports a `missing-argument`.
The difference is how many places you edit.
A new parameter changes every call site along with every signature,
and each function in between accepts an object it does not use.
A new ability changes the signatures alone:
`yield from greet_logged(name)` stays as it is, and the instance appears once,
at `supply()`.

Multiple abilities combine with `|` because the union describes one request at a time.
Each `yield` in `greet_all()` produces either a `Need[Console]` or a `Need[Log]`,
not both at once.
Over the whole run it makes both kinds of request,
so `supply()` must provide a `Console` and a `Log`.

The repeated union invites a `type` alias,
and the book's own habits would normally endorse one.
Resist it here.
Under `ty` (0.0.65 at this writing),
a `type` alias as a generator's return annotation turns the yield check off,
and everything this section demonstrated silently stops being verified.
Stateless avoids the trap in its own definitions:
`Effect` and its aliases are older `TypeAlias` assignments rather than `type` statements,
and those keep the check alive.
Write Effect signatures out in full until your checker proves that it sees through the alias.

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
`holds()` takes no arguments, so `material` and `nailer` are not inputs.
`supply()` binds them instead,
so the table reads as a matrix of environments rather than a list of arguments.
A new `Material` is a new row.

Dependencies as parameters would serve this test as well,
because `holds(material, nailer)` is easy to call four times.
The difference appears when the dependency sits three calls deep.
Then the parameter version threads two arguments through every function on the path.
This version changes nothing but the row.

## Dependency Injection

Conventional dependency injection (DI) collects all bindings into a container.
That container maps each type to the instance that satisfies it,
and provides those instances during program execution:

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
    if t not in DI_CONTAINER:
        raise NotRegistered(t.__name__)
    return DI_CONTAINER[t]

def greet(name: str) -> None:
    console: Console = get(Console)  # Exact type
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

`register()` puts an instance in, and `get()` looks one up by type,
at the point where the program needs it.
The type is the registration key,
so `register(Console, Recorder())` binds an implementation to the type its callers request.
In Stateless, `supply()` takes the instances alone and pairs them by `isinstance()`,
which is why two instances that satisfy one `Need` are ambiguous
([When Two Implementations Match](46_Stateless.md#when-two-implementations-match)).
That registration key also does the work `as_type(Console)` does for `supply()`,
which reads each ability from its argument's static type:
`supply(recorder)` is a `Handler[Need[Recorder]]`,
and no `Need[Console]` matches it
([Swapping the Implementation](46_Stateless.md#swapping-the-implementation)).

The `Any` in `DI_CONTAINER` is unavoidable,
because it holds instances of unrelated types.
The type information is now held in the dictionary key,
but a homogeneous `dict` has no annotation for "the value under key `type[T]` is a `T`."
That invariant lives in `register()`'s signature rather than in the container.

`greet()`'s body matches `greeter.py`'s `greet()` line for line,
apart from `console: Console = get(Console)` in place of `console = yield from need(Console)`.

The first call to `greet("Alice")` fails at runtime because nothing has been registered.
The second call succeeds because the binding now exists.
The two calls are identical,
and nothing in their types records whether a `Console` has been registered,
so `ty` accepts the file.

Notice that this `greet()` has the same signature as the `untyped_greet.py` version in [Declaring a Dependency](46_Stateless.md#declaring-a-dependency).
Both read `(str) -> None`, and both hide a `Console`.
DI relocates a side cause instead of declaring it,
so the dependency becomes swappable without becoming visible.

Stateless has no container.
`supply()` is a function call, and its arguments are the bindings.
This produces three consequences:

1. Stateless checks happen before the program runs.
   DI only discovers a missing registration when something asks for it.
   This can be at startup or much later, on a path no test exercised.
   Remove the `# type: ignore` from `unsupplied.py` and `ty` reports the unsupplied `Need[Console]` before the program runs
   ([Forgetting to Supply](46_Stateless.md#forgetting-to-supply)).

2. Stateless bindings are per call rather than per process.
   DI usually holds one type binding for the life of the program.
   `supply()` binds for one execution of one Effect,
   so two bindings for the same type can be live at once,
   as the screen and memory `Console`s were in [When Two Implementations Match](46_Stateless.md#when-two-implementations-match).
   No reset is needed between test cases.

   Handlers also layer.
   An ability a handler cannot answer is yielded further out,
   so `supply(Log())(greet_all)` still has the type `(list[str]) -> Depend[Need[Console], None]`,
   and wrapping that in `supply(Console())` leaves `(list[str]) -> Success[None]`.
   You can bind some abilities near the Effect and the others at the edge,
   with the type recording what each layer left behind.
   DI has one flat registry and no equivalent layering.

3. Stateless function requirements are expressed in the function type.
   DI leaves that information in the bodies that ask for it,
   so learning what a function needs means reading its implementation.
   `holds()` declares `Need[Material] | Need[Nailer]` in its signature,
   and a caller that does not supply them inherits the requirement.

The requirement that callers inherit is also the cost.
Adding a dependency deep in the stack rewrites the return type of every function above it,
which [Adding an Effect Deep in the Stack](46_Stateless.md#adding-an-effect-deep-in-the-stack)
demonstrated with `Need[Log]`.
DI absorbs the same change in silence, and no signature records it.

The checker is the better place to meet an omission,
so the trade is not about correctness, but churn and coupling.
A function that never logs still names `Need[Log]` in its type,
and taking that dependency back out later moves every signature on the path a second time.
This is the same complaint that was made against Java's checked exceptions,
and it is the reason [Effects Propagate, and the Checker Verifies It](46_Stateless.md#effects-propagate-and-the-checker-verifies-it)
compares the spread to `async`.

## Where `run()` Can Be Called

The error message in `unsupplied.py` said `run()` handles `Async` on its own.
It can do that because its entire body is `return asyncio.run(run_async(effect))`.
That has a consequence worth knowing before you incorporate Stateless into an existing application.
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

This also prints a `RuntimeWarning` to standard error,
so it does not appear in the output above, which shows standard output only.
`run()` builds the `run_async()` coroutine before handing it to `asyncio.run()`,
which raises a `RuntimeError` because a loop is already running,
leaving that coroutine un-awaited.
The warning is harmless, because that coroutine never started.
It is also a reliable sign of this mistake,
appearing whenever `run()` is called from asynchronous code.

`run_async()` is the same driver packaged as a coroutine, so you `await` it.
A synchronous program calls `run()` once at its outermost edge.
A program that is already asynchronous, a web service or a bot,
awaits `run_async()` at the edge of each request.
Picking the wrong one is a runtime error rather than a type error,
which makes it one of the few mistakes in this chapter the type checker will not catch.

## Waiting on a Coroutine

`Async` has appeared as something `run()` handles on its own.
`wait()` is what puts it into a type.
`yield from wait()` accepts any awaitable and produces the value that awaitable produces:

```python
# await_coroutine.py
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
There is nothing to supply, because `Async` asks for no object
(there's no `Need`).
A `Need[Console]` asks for a `Console` instance, which someone must bind.
An `Async` request carries the coroutine and asks for it to be awaited,
and `run()` does that with the event loop it already owns.
So `Async` is answered rather than supplied,
and it is the one ability in this chapter that never reaches `supply()`.

Notice what `report()` is not.
It is not an `async def` and it contains no `await`,
yet its result comes from a coroutine.
`wait()` hands the coroutine out as a request and the driver awaits it,
so the asynchrony stops at the ability channel instead of spreading to `report()` and to everything that calls it.

`wait()` is required at the boundary where a coroutine enters the Effect world.
A function that already returns an Effect needs no `wait()`,
because `yield from` composes the two directly.
The library's own `sleep()` is such a function,
and it pairs an `Async` request with a dependency:

```python
# sleep_effect.py
import time
from stateless import Async, Depend, Need, run, supply
from stateless.time import Time, sleep

def delayed_sum(
    values: list[int],
) -> Depend[Need[Time] | Async, int]:
    total = 0
    for value in values:
        yield from sleep(0.01)
        total += value
    return total

start = time.perf_counter()
result = run(supply(Time())(delayed_sum)([1, 2, 3]))
elapsed = time.perf_counter() - start
print(result)
#: 6
print(f"waited 30ms or more: {elapsed >= 0.03}")
#: waited 30ms or more: True
```

`sleep()` returns `Depend[Need[Time] | Async, None]`,
so a function that calls it inherits both abilities.
It declares both because `sleep()` makes both requests,
`need(Time)` for the clock and `wait()` for the await:

```python
def sleep(seconds: float) -> Depend[Need[Time] | Async, None]:
    time = yield from need(Time)
    yield from wait(time.sleep(seconds))
```

The `async def` is `Time.sleep()`, the method on the ability,
so the boundary crosses there rather than in `delayed_sum()`.
`Time` is an ability like `Console`, an object whose method the Effect calls,
and `supply()` binds it the same way.
Reading a clock is a [side cause](44_Effect_Management.md#what-is-an-effect),
and `Need[Time]` moves that reading into the ability channel.
A test can then supply a `Time` subclass whose `sleep()` returns at once,
and check the logic without waiting for real time to pass.
That subclass goes through `as_type(Time)`,
for the same reason `Recorder` went through `as_type(Console)`.
In [Adding Behavior to an Existing Effect](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect),
`retry()` waits between attempts,
so it adds `Need[Time]` and `Async` to whatever it decorates.

## The Error Channel

Dependencies are one half of the type.
The other half is failure.
`@throws` converts a raised exception into a yielded one:

```python
# scores.py
from typing import Final
from stateless import throws

SCORES: Final[dict[str, int]] = {"Alice": 42, "Bob": 7}

@throws(KeyError)
def score(name: str) -> int:
    return SCORES[name]
```

`score()` looks like an ordinary function that raises a `KeyError`,
but the decorator changes its type to `(str) -> Try[KeyError, int]`.
`Try` is the alias from the table in [The Effect Type](#the-effect-type):
it needs nothing, can fail with a `KeyError`, and produces an `int`.
This carries the same idea as the `Result` type in [Error Handling](42_Functional_Error_Handling.md#turning-exceptions-into-results),
though the two are not the same construct.
A `Result` is a wrapper the function returns at once,
and the caller matches on it.
A `Try` is a description that runs nothing until it is driven,
and its failure arrives as a yielded value rather than a returned one.
A `Result`-shaped value appears only after `catch()`,
as the bare union `int | KeyError` in place of a wrapper object.
There, you rewrote the body to return an `Ok` or an `Err`.
Here, you leave the body alone and lift the exception into the signature.

You can watch the failure travel.
Calling `score()` still runs nothing.
Advance the Effect one step with `next()` and the `KeyError` arrives as a value,
not as a raised exception:

```python
# error_is_yielded.py
from scores import score

effect = score("Carol")
print(repr(next(effect)))
#: KeyError('Carol')
```

The body raised the exception.
`@throws` wraps that body in an ordinary `try`/`except`,
so the wrapper catches the `KeyError` and yields the exception object over the same channel that carries ability requests.
That is why `Effect`'s alias puts `A | E` in the `Generator`'s first parameter:
requests and failures are both values a description yields to its driver.

Errors propagate through the `Effect` type, just like abilities:

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

This uses all three parameters of `Effect[A, E, R]`.
`announce()` needs a `Console`, can fail with `KeyError`, and produces nothing.
Drop the `KeyError` from the annotation and `ty` points at the `yield from score(name)` line.
Declared exceptions cannot be forgotten.

Declaring an error does not oblige you to handle it.
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

The error channel records those failures that can occur,
without forcing you to handle them.
`run()` turns any that reach it back into normal Python exceptions.

## Turning an Error Into a Value

`catch()` empties the error channel the way `supply()` empties the ability channel,
but the two do different things with what they remove.
`supply()` provides the ability inside the Effect,
so the ability parameter becomes `Never` and the result type never mentions the `Console`
([Supplying the Dependency](46_Stateless.md#supplying-the-dependency)).
`catch()` hands the error back to you as a value in the result.
`@throws` puts a raised exception into the channel,
and `catch()` takes it back out:

```python
# catch_score.py
from typing import assert_never
from greeter import Console
from scores import score
from stateless import Depend, Need, catch, need, run, supply

def report(name: str) -> Depend[Need[Console], None]:
    value: int | KeyError = yield from catch(KeyError)(score)(name)
    console = yield from need(Console)
    match value:
        case KeyError():
            console.print(f"{name}: unknown")
        case int():
            console.print(f"{name}: {value}")
        case _:
            assert_never(value)

run(supply(Console())(report)("Alice"))
#: Alice: 42
run(supply(Console())(report)("Carol"))
#: Carol: unknown
```

The signature for `score()` is `(str) -> Try[KeyError, int]`.
`catch(KeyError)(score)` changes it to `(str) -> Success[int | KeyError]`.
The error leaves the error type parameter, which becomes `Never`,
and joins the result type parameter.
That makes `value` something you `match` on rather than an exception to catch.

`Success` describes the Effect, not the lookup.
It means both channels are empty: nothing left to supply,
and no failure that `run()` must raise.
The Effect "succeeds" at producing either a score or a `KeyError` indicating there is no score.
A raised `KeyError` is a failure.
A returned `KeyError` is data.

Moving the error into the result makes it impossible to ignore.
If you drop the `match` entirely and use `value` directly as a number,
the checker catches it:

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

This is the same guarantee the `Result` type gives in [Error Handling](42_Functional_Error_Handling.md#a-result-type),
reached without rewriting the body of `score()`.

### Multiple Errors

`catch()` can track multiple error types.
`SCORES` stores its values as `int`s,
so looking up a name is the only step and `KeyError` is the only failure.
`RAW` stores the scoreboard as text, before anyone has interpreted it:

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

There are two steps, and one potential failure in each.
The lookup raises a `KeyError` for an unknown name,
and the conversion raises a `ValueError` for text that is not a number,
like Bob's `"seven"`.

`@throws(KeyError, ValueError)` makes the `read_score` signature `(str) -> Try[KeyError | ValueError, int]`.
We can catch `both` errors or just `one` error:

```python
# catch_subset.py
from typing import assert_never
from read_score import read_score
from stateless import Success, Try, catch, run

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(name)
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

for who in ["Alice", "Bob", "Carol"]:
    print(run(all_handled(who)))
#: Alice: 42
#: Bob: unreadable
#: Carol: unknown
print(run(one_unhandled("Alice")))
#: Alice: 42
try:
    run(one_unhandled("Bob"))
except ValueError as e:
    print(type(e).__name__)
#: ValueError
```

`both` is `(str) -> Success[int | KeyError | ValueError]`.
Every failure has been moved into the result so nothing is left in the error channel.
`all_handled()` returns `Success[str]` which means that no failure can escape as a thrown exception.
The three names exercise its three branches.

`one` is `(str) -> Try[ValueError, int | KeyError]`.
The caught error moved to the result and the uncaught one remains.
`one_unhandled()` never handles `ValueError` so that must be declared.
Calling it on `"Bob"` carries that failure up to the `run()` call at the program's edge,
which raises it as an ordinary exception,
the same escape `error_escapes.py` showed for a single error.
Failures cannot be lost, only relocated.

## Emptying the Channels

The two halves of this chapter taught two vocabularies:

1. A dependency is an object created elsewhere.
   `need()` records the request as a `Need` in the type,
   and `supply()` answers it with an instance.
2. A failure is an exception: `@throws` lifts it into the type,
   and `catch()` removes it from the equation.

The vocabularies differ.
The operation underneath them does not.
Both subtract from the type.
`supply()` removes an ability and leaves `Never` in its place.
`catch()` removes an error and moves it into the result,
where a `match` must account for it.
An Effect with both channels emptied is a `Success`, which `run()` accepts.

The channels do not resolve in the same way:

- `unsupplied.py` showed `run()` refusing an Effect that still declares an ability,
  before the program starts.
- `error_escapes.py` showed `run()` accepting an Effect that still declares a failure,
  then raising that failure at the edge.

The difference is not an inconsistency.
An unbound dependency has no answer anywhere in the program,
so a driver encountering one can do nothing but stop.
An unhandled failure has a clear meaning at the boundary: raise the exception,
which is what Python does without the Effect type.
The two guarantees are therefore different.
A dependency must be resolved before anything runs.
A failure must be declared, and you choose where to handle it.
Both are checked, and neither can be dropped by forgetting it.

## Exercises

1.  Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `ask_and_greet()`,
    an Effect that asks for a name and greets the result.
    Supply a scripted `Console` in a test and a real one in a demo,
    and confirm `ask_and_greet()` is unchanged between them.
2.  Take `undeclared_need.py`, remove the `# type: ignore`,
    and run `ty check` on it.
    Fix the error by changing only the annotation,
    then check what `greet_all()`'s callers must now declare.
3.  Apply `reveal_type()` to `catch(ValueError)(one_unhandled)` and run `ty check`.
    Explain why its result type differs from `all_handled()`'s,
    given that both have handled every error `read_score()` declares.
4.  Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
    then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.
5.  Add a `Metal` material to `test_nailer.py` with a brittleness that survives the robotic nailer,
    and add its two rows to the table.
    Then explain why the test function body needed no change.
6.  Break `audit_log.py` by removing the `yield from` in front of `greet(name)` in `greet_logged()`.
    Run `ty check`, `ruff check`, and the script,
    and record what each reports and what the program prints.
    Explain where the greetings went and why no tool objects.
    Then restore it, and instead remove the `yield from` in front of `need(Console)` in `greeter.py`'s `greet()`.
    This time `ty` produces two diagnostics.
    Explain what each one caught,
    and why assigning a dropped request is caught when discarding one is not.
