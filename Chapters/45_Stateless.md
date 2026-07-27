# Stateless

[Effect Management](44_Effect_Management.md#library-effect-management)
introduced library Effect systems and named the Python one.
This chapter builds it.

[Stateless](https://github.com/suned/stateless)
encodes an Effect's dependencies and failures into the return type of a function,
and a type checker verifies that every caller carries them forward.
Forget to declare a dependency and the check fails.
Forget to supply one and the check fails.
That is delayed binding, the third property of a full Effect Management System,
with the bookkeeping moved into the type system.

This chapter builds up to that one step at a time.
Each step adds a single idea, and every listing runs.
Install the library with:

```text
pip install stateless
```

## A Generator Is a Description

Stateless is built on generators,
so the mechanism is worth seeing before the library appears.
[Effect Management](44_Effect_Management.md#effect-management-for-python)
showed that calling an `async def` function runs nothing.
It returns a coroutine: a description of work.
A generator function behaves the same way.

A generator is more interesting than a coroutine here because `yield` is a two-way channel.
The generator yields a value out, and the caller sends a value back in.
That reversal is what makes an Effect system possible.
The generator yields a *request*,
and whoever is driving it supplies the *answer*:

```python
# two_way_generator.py
from collections.abc import Generator

def interview() -> Generator[str, str, str]:
    name = yield "name"
    town = yield "town"
    return f"{name} of {town}"

answers = {"name": "Alice", "town": "Portland"}
conversation = interview()
request = next(conversation)
while True:
    try:
        request = conversation.send(answers[request])
    except StopIteration as stop:
        print(stop.value)
        break
#: Alice of Portland
```

Read `interview()` and notice what is missing.
It does not know where answers come from.
It has no dictionary, no `input()` call, and no network connection.
It states what it needs and waits.
The loop underneath decides how those needs are met.
Swap the dictionary for a database and `interview()` does not change.

That is Effect Management in miniature.
The generator declares Effects, the driver interprets them.
The `Generator[str, str, str]` annotation even reports the arrangement.
The first parameter is what goes out, the second is what comes back,
and the third is the final result.

## `yield from` Composes Descriptions

One generator alone is a curiosity.
The reason generators can carry an Effect system is that they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down:

```python
# yield_from_delegates.py
from collections.abc import Generator

def ask(question: str) -> Generator[str, str, str]:
    answer = yield question
    return answer

def interview() -> Generator[str, str, str]:
    name = yield from ask("name")
    town = yield from ask("town")
    return f"{name} of {town}"

answers = {"name": "Alice", "town": "Portland"}
conversation = interview()
request = next(conversation)
while True:
    try:
        request = conversation.send(answers[request])
    except StopIteration as stop:
        print(stop.value)
        break
#: Alice of Portland
```

The driver is unchanged, and it never learns that `ask()` exists.
Requests from any depth surface at the top,
so a single loop at the edge of the program interprets Effects raised anywhere inside it.
`yield from` also returns the inner generator's value,
which is why `name` and `town` read like ordinary assignments.

Every Effect in this chapter travels this path.
Stateless supplies the vocabulary for the requests and the driver that answers them.

## The Effect Type

Stateless defines one type, and everything else is built from it:

```python
type Effect[A: Ability, E: Exception, R] = Generator[A | E, Any, R]
```

An `Effect` is a generator that yields either an *ability* or an exception,
and eventually returns a result.
The three parameters answer the three questions from the previous chapter:

- `A` is what the computation *needs*.
- `E` is how it can *fail*.
- `R` is what it *produces*.

Three aliases name the common cases,
each one filling in `Never` for a parameter that is not used:

| Alias | Meaning |
|---|---|
| `Success[R]` | Needs nothing, cannot fail, produces `R` |
| `Depend[A, R]` | Needs `A`, cannot fail, produces `R` |
| `Try[E, R]` | Needs nothing, can fail with `E`, produces `R` |

`Never` is the type with no values,
so `Success[R]` promises there is no ability it can request and no error it can yield.
The signature is the entire claim.

Start with the smallest of them.
`success()` wraps a value in an Effect, and `run()` executes one:

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
Nothing is gained yet, because `double()` was already pure.
Effects become useful when a function needs something it should not create for itself.

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
This one is not, and the rest of the chapter is about who enforces the difference.

Two details deserve attention.
`greet()` is a generator function, because it contains `yield from`.
That is what makes it an Effect.
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
This is the description/execution split from the previous chapter,
and the reason a library Effect system has to have one.
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

The interesting part is what happens to the type.
`greet` is `(str) -> Depend[Need[Console], None]`.
`bound` is `(str) -> Success[None]`.
Handling an ability *subtracts* it from the type.
An Effect with every ability subtracted is a `Success`,
and `run()` accepts nothing else.
Binding an implementation and satisfying the type checker are the same act.

## Forgetting to Supply

Now break it.
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

## Swapping the Implementation

Delayed binding earns its keep when the binding changes.
A test binds a `Console` that records instead of printing:

```python
# recorder.py
from typing import override
from greeter import Console

class Recorder(Console):
    def __init__(self) -> None:
        self.messages: list[str] = []
    @override
    def print(self, message: str) -> None:
        self.messages.append(message)
```

```python
# test_greeter.py
from greeter import greet
from recorder import Recorder
from stateless import run, supply

def test_greet() -> None:
    recorder = Recorder()
    run(supply(recorder)(greet)("Alice"))
    assert recorder.messages == ["Hello, Alice!"]
```

There is no `capsys`, no monkeypatching of `print`, and no mock.
The test supplies a different `Console` and reads what the code produced.
`greet()` is unchanged and unaware.

`supply()` matches an instance to a `Need` by `isinstance()`,
which is why `Recorder` inherits from `Console`.
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

`Console` is now the second property of an Effect Management System:
an Effect's interface, separate from any implementation.
`Terminal` is one implementation and `Recorder` would be another,
and neither is named anywhere in `greet()`.
`@runtime_checkable` is required because `supply()` uses `isinstance()`.
Structural checks match on method names alone,
so two supplied objects that both define `print()` are indistinguishable,
and the first one wins.
Give abilities distinct method names when that ambiguity is possible.

## Effects Propagate, and the Checker Verifies It

A function that calls an effectful function becomes effectful.
`greet_all()` has to declare the `Console` it never touches:

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
Compare that to the by-hand version in the previous chapter,
where `greet(ask, tell)` took its dependencies as arguments.
Nothing there stopped an intermediate function from constructing its own `Console` and quietly performing an undeclared Effect.
Here, the signature and the body cannot disagree.

## Adding an Effect Deep in the Stack

The previous chapter's second exercise asks you to add a `Log` Effect underneath `greet()` and count the signatures you had to edit.
Do that here:

```python
# audit_log.py
from greeter import Console, greet
from stateless import Depend, Need, need, run, supply

class Log:
    def __init__(self) -> None:
        self.entries: list[str] = []
    def write(self, entry: str) -> None:
        self.entries.append(entry)

type Greeting = Depend[Need[Console] | Need[Log], None]

def greet_logged(name: str) -> Greeting:
    yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")

def greet_all(names: list[str]) -> Greeting:
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
What it removes is the *searching*.
The checker names every file and line that needs the change,
and the program does not build until the last one is fixed.
With dependencies passed as parameters,
a missed thread produces a runtime `TypeError` in whatever code path happens to reach it.

Multiple abilities combine with `|`, which reads correctly.
`greet_all()` needs a `Console` or a `Log` at each individual request,
and both over its lifetime.

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

The error travels the same channel as an ability, so it propagates the same way:

```python
# announce.py
from greeter import Console
from scores import score
from stateless import Effect, Need, need

def announce(name: str) -> Effect[Need[Console], KeyError, None]:
    value = yield from score(name)
    console = yield from need(Console)
    console.print(f"{name}: {value}")
```

Here is where the full `Effect[A, E, R]` earns its three parameters.
`announce()` needs a `Console`, can fail with `KeyError`, and produces nothing.
Every question the previous chapter asked about a function is answered by its first line.
Drop the `KeyError` from the annotation and `ty` reports the same class of error it did before,
this time pointing at the `yield from score(name)` line.
Declared exceptions cannot be dropped by forgetting them.

## Turning an Error Into a Value

`catch()` handles an error the way `supply()` handles an ability.
It removes the error from the type and moves it into the result:

```python
# catch_score.py
from greeter import Console
from scores import score
from stateless import Depend, Need, catch, need, run, supply

def report(name: str) -> Depend[Need[Console], None]:
    value = yield from catch(KeyError)(score)(name)
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
The error left the error parameter and joined the result parameter,
so `value` is something you `match` on rather than an exception you catch.

That relocation is what makes the failure impossible to ignore.
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

`catch()` takes as many error types as you want to handle,
and handling all of them is the case to aim for.
`catch(KeyError, ValueError)` applied to a function that declares both produces `Success[int | KeyError | ValueError]`,
with every failure moved into the result and nothing left in the error channel.
Handling only some of them is where the checking thins out,
which the next section covers.

## Abilities Are Not Special

`Need` looks built-in, but it is an ordinary class, and you can write your own.
An ability subclasses `Ability[T]`, where `T` is what handling it produces.
Here is the `Ask` and `Tell` program from the previous chapter, rebuilt:

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

def greet() -> Depend[Ask | Tell, None]:
    name = yield from Ask("What is your name? ")
    yield from Tell(f"Hello, {name}!")

messages: list[str] = []

def scripted(ask: Ask) -> str:
    return "Alice"

def capture(tell: Tell) -> None:
    messages.append(tell.message)

effect = handle(scripted)(handle(capture)(greet))
run(effect())
print(messages)
#: ['Hello, Alice!']
```

`yield from Ask("What is your name? ")` yields the ability object and returns whatever the handler sends back,
typed as `str` by `Ability[str]`.
`handle()` reads the annotation on its argument to decide which ability it answers,
which is why `scripted` and `capture` must annotate their parameters.

Now compare this listing to `ask_tell.py` in the previous chapter.
The by-hand version threaded two objects through every signature.
This one threads nothing.
`greet()` takes no arguments at all,
and the two Effects live in the return type where a checker can follow them.
That second channel in the signature is what the previous chapter said an EMS needs.

Return to `two_way_generator.py` and the whole library is visible.
`yield` sends a request out, `handle()` is the driver loop that answers it,
and `run()` is the one at the bottom.

## Where the Guarantee Stops

An honest accounting needs the limits,
and there are three worth knowing before you commit a codebase to this.

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
A native Effect system computes a function's Effects from its body.
A library can only check the ones you wrote down.
The guarantee is about consistency, not completeness.

The second limit is that *partial* handling loses the type.
Handle everything an Effect declares and the result is precise,
as `supply(Console())(greet)` and `catch(KeyError)(score)` both were.
Handle some of it and `ty` (version 0.0.58) infers the result as `Unknown`,
because subtracting one member from a union inside a higher-order function is beyond what it can solve.
This applies to `supply()`, `handle()`, and `catch()` alike.
The stacked handlers in `ask_tell_effect.py` are an instance.
The intermediate `handle(capture)(greet)` already yields `Unknown`,
so the checker stops tracking whether `Ask` was ever answered.
That listing is correct, but the correctness is yours to maintain,
not the checker's.
This program passes the check and fails at runtime:

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
    run(half())
except MissingAbilityError as e:
    print(type(e).__name__)
#: MissingAbilityError
```

The practical rule is to handle everything at one edge,
which is the architecture the previous chapter recommended anyway.
One `supply()` call at the boundary of the program keeps the checking intact.
Splitting bindings across layers is where it goes quiet.

The third limit is the cost.
Every effectful function becomes a generator function,
which means it cannot also be a plain function,
and calling it returns a description that somebody has to run.
Type errors from a library this generic are long and mention internals.
And a third-party function that knows nothing about Effects has to be wrapped in `@throws` or reached through a `need()` before it can participate.
An Effect system is a decision about a whole codebase,
not a utility you import for one module.

## What This Costs and What It Buys

The previous chapter argued that Effects are the next scaling barrier,
and that the tracking will eventually move into the language.
Stateless shows what that looks like inside Python today,
which is the value of studying it even if you never ship it.

Read the signatures once more, in order:

- `Success[int]`: pure.
- `Depend[Need[Console], None]`: prints, somehow,
  through something supplied later.
- `Effect[Need[Console], KeyError, None]`: prints, might not find the name.

Each one answers what a function depends on, what it can produce,
and how it can fail, before you read a single line of the body.
That is the property this book has been circling since [Foundations](40_Functional_Foundations.md#pure-functions).
Purity is valuable because it is *verifiable*,
and verification you have to perform by reading code does not scale.

What Stateless charges for that property is the generator discipline,
the description/execution split, and an ecosystem that has never heard of it.
For most Python code that price is too high, which is the honest recommendation.
The techniques from the previous chapter, returning a `Result`,
restricting a type so bad values cannot exist,
and passing dependencies in rather than constructing them,
capture much of the benefit at a fraction of the cost.
Use Stateless when a system is large enough that hidden Effects have already cost you a production incident,
and when the team will hold the line at every boundary.
Below that scale, the discipline is what matters and the machinery is optional.

But the direction is worth watching.
Python got one Effect tracked into its type system with `async`,
and nobody now argues that was a mistake.
The languages in the previous chapter's list track all of them.
Stateless is the demonstration that Python's type system is expressive enough to do it,
given a library willing to encode everything into return types.
What is missing is not the capacity.
It is a language that does the encoding for you.

## Exercises

1.  Add a `read()` method to the `Console` protocol in `console_protocol.py` and write `interview()`,
    an Effect that asks for a name and greets the result.
    Supply a scripted `Console` in a test and a real one in a demo,
    and confirm `interview()` is unchanged between them.
2.  Take `undeclared_need.py`, remove the `# type: ignore`,
    and run `ty check` on it.
    Fix the error by changing only the annotation,
    then check what `greet_all()`'s callers now have to declare.
3.  Write `parse_score()`, which reads a `dict[str, str]` and returns an `int`,
    decorated with `@throws(KeyError, ValueError)`.
    Print the type of `catch(KeyError, ValueError)(parse_score)` with `reveal_type()`,
    then the type of `catch(KeyError)(parse_score)`.
    Explain which of the two the chapter calls safe, and why.
4.  Rewrite `audit_log.py` so `Log` is a `Protocol` rather than a concrete class,
    then write a test that supplies a recording `Log` and a recording `Console` at once and asserts on both.
5.  Write a `Clock` ability as an `Ability[datetime]` subclass,
    with a handler function that returns a fixed time,
    and an Effect that stamps a greeting with it.
    Explain why a fixed clock in a test is the same technique as `Recorder`,
    and which of the three Effect categories from the previous chapter a clock belongs to.
6.  `leaky_effect.py` type-checks while lying about its purity.
    Describe a review rule or a lint check that would catch it,
    and explain why a type checker cannot.
