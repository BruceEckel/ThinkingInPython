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

Stateless is built on generators,
so we must study the full `Generator` annotation before exploring the library.

## Annotating a Generator

[Iterators](23_Iterators.md#generators)
annotated every generator using the short form `Iterator[int]`.
That fits a generator that only yields values.

A generator that also receives values needs the full annotation:

    `Generator[YieldType, SendType, ReturnType]`

This names the three things a generator exchanges with its caller:

- `YieldType` is the value `yield` hands out, thus the value `next()` returns.
- `SendType` is the value `send()` accepts,
  and the value the `yield` expression produces inside the generator.
- `ReturnType` is the value `return` produces,
  delivered as `StopIteration.value`.

The last two type parameters default to `None`:

```python
# generator_defaults.py
from collections.abc import Generator, Iterator

def countdown(n: int) -> Generator[int]:
    while n > 0:
        yield n
        n -= 1

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

print(list(countdown(6)), list(squares(6)))
#: [6, 5, 4, 3, 2, 1] [0, 1, 4, 9, 16, 25]
```

`Generator[int]` means `Generator[int, None, None]`.
`Iterator[int]` says the same thing and reads better for a one-way generator.
The long form is necessary when the other two channels carry something,
as they do in this chapter.

The `interview()` generator yields a question, receives an answer,
and returns a result:

```python
# generator_interview.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")  # Ask the world for the name
    town = yield Question("town")  # Ask the world for the town
    friend = yield Question("friend")  # Ask for a friend
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    i = interview()
    question1: Question = next(i)
    print(f"{question1 = }")
    question2: Question = i.send(Answer("Alice"))
    print(f"{question2 = }")
    question3: Question = i.send(Answer("Wonderland"))
    print(f"{question3 = }")
    try:
        i.send(Answer("Rabbit"))
    except StopIteration as stop:
        result: Result = stop.value
    print(f"{result = }")
#: question1 = 'name'
#: question2 = 'town'
#: question3 = 'friend'
#: result = 'Alice of Wonderland, friend Rabbit'
```

Although `Generator[str, str, str]` describes `interview()` accurately,
it does not say which `str` is which.
`NewType` gives each channel a distinct type,
so the annotation states the arrangement and a checker enforces it.
`Question` fills the `YieldType` position, `Answer` the `SendType`,
and `Result` the `ReturnType`.
The distinction exists only for the checker.
`Question("name")` produces the plain `str`.

Driving the generator by hand shows one type parameter at a time.
`next(i)` starts the generator and produces a `Question`.
`i.send(Answer("Alice"))` passes an answer in and produces the next question,
the two-way channel in a single expression.
The last `send()` finds no further `yield`,
so the generator returns its `Result`.
A returning generator also raises `StopIteration`,
and the `Result` arrives as that exception's `value`.

The first call must be `next()`.
A newly created generator pauses before its first `yield`,
so a sent value would have nowhere to arrive.
If you call `i.send(Answer("Alice"))` at that point, it raises a `TypeError`.

`next(i)` is equivalent to `i.send(None)`:

```python
# send_none_is_next.py
from generator_interview import interview

print(f"{interview().send(None) = }")  # type: ignore
#: interview().send(None) = 'name'
print(f"{next(interview()) = }")
#: next(interview()) = 'name'
```

Each `interview()` call creates a new generator,
so both lines start from the beginning and produce the first question.
The `# type: ignore` is the interesting part.
`interview()` declares `Answer` as its `SendType`,
and `None` is not an `Answer`,
so the checker rejects the priming `send()` even though the interpreter accepts it.
The equivalence is a runtime fact the annotation cannot express,
which is the practical reason a driver primes with `next()`.

The `NewType` definitions prevent accidental transposition.
If you mistakenly annotate the generator as `Generator[Answer, Question, Result]`,
`ty` reports six errors in three pairs.
Both `yield Question(...)` expressions offer a `Question` where the annotation promises an `Answer`.
Both `send(Answer(...))` calls pass an `Answer` where it expects a `Question`.
Both assignments to `question` receive an `Answer` into a variable declared `Question`.
The checker ensures proper arguments are used because each channel has its own type.
`Generator[str, str, str]` would have accepted the reversal without complaint.

A coroutine intentionally has the same three-part shape:
`Coroutine[YieldType, SendType, ReturnType]`.
`async def` and generator functions both build descriptions that something else drives.

## A Generator Is a Description

[Effect Management](44_Effect_Management.md#effect-management-for-python)
showed that calling an `async def` function runs nothing.
It returns a coroutine: a description of work.
A generator function behaves the same way.
Calling `interview()` returns a generator object but doesn't run anything in the function body.
`next()` and `send()` do that work, one `yield` at a time.

A generator is more interesting than a coroutine here because `yield` is a two-way channel.
The generator yields a value out, and the caller sends a value back in.
That conversation makes an EMS possible.
The generator yields a *request*,
and whoever is driving it supplies the *answer*.
Typically, that stepping happens in a driver:

```python
# two_way_generator.py
from collections.abc import Generator
from typing import Final
from generator_interview import Answer, Question, Result, interview

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        try:
            print(f"{request = }, {answers[request] = }")
            request = conversation.send(answers[request])
        except StopIteration as stop:
            return stop.value

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
```

The generator is imported unchanged; only the driver is new.
`drive()` touches all three type parameters:
`next()` produces the first `Question`,
`send()`'s argument supplies the `Answer`,
and `stop.value` in the `except` clause becomes the `Result` that `drive()` returns.
The `answers` map is keyed by `Question` and holds `Answer`s.
`ANSWERS` fills that role for the rest of the chapter,
so the later examples import it instead of repeating the same three pairs.

Notice what is missing in `interview()`:
it does not know where the answers come from.
It has no dictionary, no `input()` call, and no network connection.
It states what it needs and waits.
`drive()` decides how those needs are met,
and it takes the answers as a parameter.
Swapping the dictionary for a database changes a single argument.

That is EMS in miniature.
The generator declares Effects, the driver interprets them.

## `yield from` Composes Descriptions

The reason generators can carry an EMS is that they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down.
Each of the three channels crosses that boundary differently,
so we take them one at a time.

### Running to Exhaustion

The simplest delegation targets generators that only yield:

```python
# yield_to_exhaustion.py
from collections.abc import Iterator

def one() -> Iterator[str]:
    yield "only"

def three() -> Iterator[str]:
    yield "A"
    yield "B"
    yield "C"

def outer() -> Iterator[str]:
    yield "start"
    yield from one()
    yield from three()
    yield "end"

def top() -> Iterator[str]:
    yield "TOP"
    yield from outer()
    yield "END"

print(list(outer()))
#: ['start', 'only', 'A', 'B', 'C', 'end']
print(list(top()))
#: ['TOP', 'start', 'only', 'A', 'B', 'C', 'end', 'END']
```

Each `yield from` runs its target until that generator is exhausted,
so the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three.
How many a delegation contributes is a property of the target.

Exhaustion is transitive.
`top()` delegates to `outer()`, which delegates to `one()` and `three()`,
and the driver still receives one flat sequence.
`top()`'s single `yield from` does not finish until every generator beneath it has.

### The Return Channel

A `yield from` expression evaluates to the inner generator's return value,
not its yielded values.
The yielded values pass through to whoever is driving.
Here, `report()` captures the return value from `yield from emit(items)` into `size`.
Note that `report()` doesn't return anything, it only yields:

```python
# yield_from_return.py
from collections.abc import Generator, Iterator

def emit(items: list[str]) -> Generator[str, None, int]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Iterator[str]:
    size = yield from emit(items)
    yield f"({size} characters)"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)']
```

`emit()` is a `Generator[str, None, int]`: it yields strings,
is never sent anything,
and returns the `int` total it accumulates while iterating.

The return channel is how a generator reports to whichever generator delegated to it,
so `report()` learns something `emit()` computed while neither of them knows who is driving.

### The Send Channel

The `SendType` is for the user to `send()` information back into the generator.
A generator that only receives values needs no `ReturnType`:

```python
# yield_from_send.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")
    yield from collect("beta")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3]:
    print(g.send(value))
#: alpha needs another
#: alpha got 1 and 2
#: beta needs a value
#: beta needs another
try:
    g.send(4)
except StopIteration:
    print("both() is exhausted")
#: beta got 3 and 4
#: both() is exhausted
```

`collect()` yields prompts, receives numbers, and returns nothing,
so its type is `Generator[str, int, None]`.
An omitted `ReturnType` defaults to `None`,
so the return signature becomes `Generator[str, int]`.
`both()` declares that same type,
because `yield from` passes the inner generator's yield and send channels through to the driver.

The numbers travel down to the `yield` that asked for them.
`g.send(1)` arrives inside `collect("alpha")`, two frames below the driver.
`both()` contains no code that forwards the value because `yield from` does that forwarding.

`g.send(2)` is the interesting one.
It supplies alpha's second value, which lets `collect("alpha")` finish,
which completes the first `yield from`, which starts the second one.
A single `send()` therefore ends one inner generator and produces the first prompt of the next.
The driver sees `StopIteration` only when `both()` runs out of delegations.

### All Three Channels

We can apply `yield from` to our `interview` example:

```python
# yield_from_delegates.py
from collections.abc import Generator
from generator_interview import Answer, Question, Result
from two_way_generator import ANSWERS, drive

def ask(question: Question) -> Generator[Question, Answer, Answer]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name = yield from ask(Question("name"))
    town = yield from ask(Question("town"))
    friend = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
```

`drive()` never learns that `ask()` exists.
Only the generator portion changed.

`ask()` uses `Answer` in two of the three positions, for two different reasons.
As the `SendType` it is the value the driver sends in,
which arrives as the value of the `yield` expression and lands in `answer`.
As the `ReturnType` it is the value `ask()` hands back when it finishes,
which `yield from` produces as the value of the whole `yield from` expression.
The inner generator asks one question and hands back one answer,
so both channels carry an `Answer`.
`interview()` keeps `Result` as its `ReturnType`,
because the sentence it builds from three answers is not an answer to any one question.

The trace shows both directions of travel.
A request raised two frames down inside `ask()` surfaces at `drive()`,
which knows nothing about where it came from.
The answer `drive()` sends back arrives inside `ask()`,
which also knows nothing about where it came from.
A single loop at the edge of the program interprets Effects raised anywhere inside it.
`yield from` also returns the inner generator's value,
which is why `name` and `town` read like ordinary assignments.

### Composing Is Not Interpreting

`drive()` and `yield from` both step a generator and both finish at `StopIteration`,
which makes them easy to confuse.
Delegation can take over the job the previous listing gave to `drive()`:

```python
# yield_from_nested.py
from collections.abc import Generator
from generator_interview import Answer, Question, Result
from two_way_generator import ANSWERS, drive
from yield_from_delegates import ask, interview

def survey() -> Generator[Question, Answer, Result]:
    profile = yield from interview()
    color = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")

print(drive(survey(),
            ANSWERS | {Question("color"): Answer("blue")}))
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: request = 'color', answers[request] = 'blue'
#: ask(question = 'color') -> answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
```

`interview()` is imported unchanged from the previous example.
It was the generator `drive()` drove; now `survey()` delegates to it.
Its `Result` arrives as the value of an expression instead of as `stop.value` in the driver,
and its questions surface three frames up rather than two.
The driver sees one more question and the same shape of trace.
`survey()` asks about a color,
so the call merges one more pair into `ANSWERS` with the dictionary union operator.

`yield from` replaced `drive()` as the consumer of `interview()`,
but not as its runner.
Something must still call `next()` and `send()` at the top,
which is why the example ends with a `drive()` call.
Stack delegations as deep as you like and the number of drivers stays at one.

What separates them is the response to a request.
`drive()` answers it: a `Question` comes out, the driver looks it up,
and the request stops there.
`yield from` answers nothing.
It relays the request upward and passes the reply back down untouched,
so `survey()` has no idea what a `Question` means.
`StopIteration` splits the same way.
Both catch it and both take `stop.value`, but they hand it to different places.
`drive()` returns the `Result` to its own caller, ending the conversation.
`yield from` feeds it to the enclosing generator as the value of the expression,
after which that generator keeps running.

`yield from` composes descriptions and a driver interprets them.
A program can hold any number of the first and needs one of the second,
at its outermost edge.

Every Effect in this chapter travels this path.
Stateless supplies the vocabulary for the requests and the driver that answers them.

## The Effect Type

Stateless builds everything atop a single type.
The library defines it with type variables,
`A` bound to `Ability` and `E` bound to `Exception`:

```python
Effect: TypeAlias = Generator[A | E, Any, R]
```

An `Effect` is a generator that yields either an *ability* `A` or an exception `E`,
and eventually returns a result `R`.
The three type parameters answer the three questions from the previous chapter:

- `A` is what the computation *needs*.
- `E` is how it can *fail*.
- `R` is what it *produces*.

`A` and `E` share the first type parameter, and `R` is the third.
That leaves the second,
which the previous section taught you to read as "what comes back from a `yield` call."
That `Any` is essential, and it explains an idiom the rest of the chapter uses.

A generator has one SendType for its whole life.
An Effect does not.
Use `yield` to request a `Need[Console]` and a `Console` should come back.
Use `yield` to request a `Need[Log]` and a `Log` should come back.
The answer's type depends on which ability was requested,
and no Python annotation can say that.
Thus we cannot pin that type parameter to one concrete type.
Annotate the SendType as `Console`,
and `yield Need(Log)` hands you something the checker calls a `Console`.

The solution is `yield from`.
A bare `yield` produces the SendType,
the type parameter that had to become `Any`.
That is not because any single answer is unknowable,
but because one annotation must cover every request the generator makes.
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

Notice that `double()` contains no `yield`, so it is not a generator function.
It does not need to be.
`success()` returns an object that implements the generator protocol,
and the annotation only promises that calling `double()` produces an Effect.
Functions that request things are generator functions, and they arrive next.

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
This one is not, and the rest of the chapter is about who enforces the difference.

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
This is the description/execution split from the previous chapter,
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
Handling an ability *subtracts* it from the type.
An Effect with every ability subtracted is a `Success`,
and `run()` refuses an unanswered ability.
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
Structural checks match on method names alone,
so two supplied objects that both define `print()` are indistinguishable,
and the first one wins.
Give abilities distinct method names when that ambiguity is possible.

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
Compare that to the by-hand version in the previous chapter,
where `greet(ask, tell)` took its dependencies as arguments.
Nothing there stopped an intermediate function from constructing its own `Console` and quietly performing an undeclared Effect.
Here, the signature and the body cannot disagree.

## Adding an Effect Deep in the Stack

The previous chapter's second exercise has you add a `Log` Effect alongside `greet()` and count the signatures you edit.
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
    value = yield from score(name)
    console = yield from need(Console)
    console.print(f"{name}: {value}")
```

Here is where the full `Effect[A, E, R]` earns its three type parameters.
`announce()` needs a `Console`, can fail with `KeyError`, and produces nothing.
Every question the previous chapter asked about a function is answered by its first line.
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
`catch(KeyError, ValueError)` applied to a function that declares both produces `Success[int | KeyError | ValueError]`,
with every failure moved into the result and nothing left in the error channel.
`catch(KeyError)` on that same function produces `Try[ValueError, int | KeyError]`.
The caught error moved to the result, the uncaught one stayed put,
and the caller inherits it.
Failures cannot be lost, only relocated.

## Abilities Are Not Special

`Need` looks built-in, but it is an ordinary class, and you can write your own.
An ability subclasses `Ability[T]`, where `T` is the type handling it produces.
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

def ask(prompt: str) -> Depend[Ask, str]:
    answer = yield from Ask(prompt)
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
and the previous chapter's ZIO listing had an accessor object doing the same job.
The declared `Depend[Ask, str]` types `name` as `str` inside `greet()`.
You can skip the accessor and yield the ability directly,
and the program still runs,
but under `ty` 0.0.64 the answer comes back as `Unknown` and the checking quietly stops.
The accessor pins it down.

`handle()` reads the annotation on its argument to decide which ability it answers,
which is why `scripted` and `capture` must annotate their parameters.
Each `handle()` subtracts one ability,
so `half` still needs an `Ask` and `full` needs nothing.
Naming the two stages also matters to the checker,
for a reason the next section gives.

Now compare this listing to `ask_tell.py` in the previous chapter.
The by-hand version threaded two objects through every signature.
This one threads nothing.
`greet()` takes no arguments at all,
and the two Effects live in the return type where a checker can follow them.
That second channel in the signature is the one the previous chapter said an EMS needs.

Return to `two_way_generator.py` and the whole library is visible.
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

## Where the Guarantee Stops

A full accounting needs the limits,
and there are four worth knowing before you commit a codebase to this.

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
and the previous chapter's `ZIO[R, E, A]` carries one for the same reason.
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

## What This Costs and What It Buys

The previous chapter argued that Effects are the next scaling barrier,
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

What Stateless charges for that property is the generator discipline,
the description/execution split, and an ecosystem that has never heard of it.
For most Python code that price is too high.
The techniques from the previous chapter, returning a `Result`,
restricting a type so bad values cannot exist,
and passing dependencies in rather than constructing them,
capture much of the benefit at a fraction of the cost.
Use Stateless when a system is large enough that hidden Effects have already cost you a production incident,
and when the team will hold the line at every boundary.
Below that scale, the discipline matters and the machinery is optional.

But the direction is worth watching.
Python got one Effect tracked into its type system with `async`,
and nobody now argues that was a mistake.
The languages in the previous chapter's list track all of them.
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
3.  Write `parse_score()`, which reads a `dict[str, str]` and returns an `int`,
    decorated with `@throws(KeyError, ValueError)`.
    Apply `reveal_type()` to `catch(KeyError, ValueError)(parse_score)` and run `ty check` to see its type,
    then do the same for `catch(KeyError)(parse_score)`.
    Explain which of the two leaves an obligation with the caller,
    and where it went.
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
7.  Break `greet_all.py` by removing the `yield from` in front of `greet(name)`.
    Run `ty check`, `ruff check`, and the script,
    and record what each reports and what the program prints.
    Explain where the greetings went and why no tool objects.
    Then explain why the same mistake in front of `need(Console)` inside `greet()` would be caught,
    and by what.
