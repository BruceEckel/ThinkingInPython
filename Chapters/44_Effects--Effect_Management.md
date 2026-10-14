# Effect Management

> A function does more than its signature says: it reads a clock, writes a log,
> opens a connection.
> Effect Management makes the extra visible to a reader, a test,
> and a type checker.

A test you wrote last week starts failing about one run in five.
The function it calls computes a total price, and the math is right.
Three calls down, a helper that formats currency reads a configuration service and writes to an audit log.
Every signature on the path hides the read and the write.

This book has emphasized the benefits of pure functions in many places:

- [Foundations](40_Functional--Foundations.md#pure-functions)
  contrasts `double()`, a pure function, with `withdraw()`,
  which depends on state left over from earlier calls.
- [Performance](18_Techniques--Performance.md#caching)
  turns naive recursive Fibonacci from 242,785 runs of its body into 26 with `functools.cache`.
  Caching works only because the cached function is pure.
- [Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
  turns shapes into immutable data,
  so one pure function replaces a method on each class.
- [*Observer*](30_Patterns--Observer.md#the-model)
  has `recolored()` return a new grid instead of mutating the one it received,
  so a test checks the change with no GUI in sight.
- [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
  reduces competition between items to pure logic,
  a dictionary lookup with nothing to mock.
- [*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md#simplification-rewrites-the-tree)
  has `simplify()` return a new tree instead of editing the one it receives.

In every one of those cases you can settle the question of purity by reading one function.
One reading stops being enough as soon as the function calls others.
If any of them has a side effect, the calling function is impure too.
To discover whether a function is impure,
you must either trust the documentation or examine the code of every function it calls.

Reading every callee soon becomes tedious and error-prone.
A type system that verified purity would do that reading for you.
A system that does so is an *Effect Management System*.

## What Is an Effect?

An *Effect* is anything a caller takes on by making a call,
beyond receiving the return value.
If you call a function that writes to an audit log,
your function writes to an audit log.
If you call one that reads the time of day,
your result depends on the time of day.
If you call one that raises a `ValueError`, your function raises a `ValueError`.
You inherit each of these by calling,
and ordinarily no signature on the path mentions any of them.

That inheritance is the difficulty.
A behavior confined to one function needs no system to manage it,
because one read of that function settles the question.
An Effect passes from callee to caller instead, one call at a time.
Every signature on the path hides it until something in the types records it.

Three things pass from callee to caller that way.
The first is a *side effect*:
calling the function does something besides return a result,
changing the environment outside the function.
For example, the function might:

- Display something on the console
- Change a pixel on your screen
- Activate a motor
- Write to a database
- Make a network request
- Modify a non-local variable
- Acquire a lock, or coordinate with another thread

A side effect is easy to spot in the function that performs it,
because the side effect changes something outside that function.
One call up, the side effect is invisible.

The second is a *side cause*, the counterpart of a side effect:
what the environment does to the function.
Suppose your function reads the time of day.
The read changes nothing in the environment,
yet the result differs from one call to the next.
Information a function uses beyond its arguments is a side cause whenever it can change between calls.
The usual sources are I/O: the time of day, a random number,
a database or network read.
Reading a global variable that something else can rebind is enough on its own.
A [captured constant](40_Functional--Foundations.md#closures) is not.

The third is an exception,
which propagates from callee to caller the same way and appears in no signature either.
People argue about whether an exception makes a function impure.

## Are Exceptions Impure?

```python
# divide_by_zero_impurity.py

def slope(rise: int, run: int) -> float:
    return rise / run
```

`slope()` produces the same result for the same inputs,
except when `run` is zero,
where it raises an exception instead of returning a result.
Does the exception break purity?

1.  **Pure.**
    Raising `ZeroDivisionError` instead of returning a number does not break purity.
    The same arguments still produce that same exception every time.
    The function reads nothing outside itself and changes nothing outside itself.
    Purity says the outcome depends on the arguments alone.

    Computer science theory backs this view.
    Pure languages like Haskell treat an unhandled runtime exception or crash as a *bottom* value, denoted ⊥.
    A bottom value stands for a computation that never produces an ordinary value.
    Because ⊥ is a value in the theory, raising an error that nothing catches
    is referentially transparent.
    Replacing the function call with the crash leaves the program's behavior the same.

2.  **Functional.**
    Exceptions bypass normal control flow,
    and that bypass makes it difficult to reason about code.
    Functional programming avoids them altogether for that reason.
    A [*Total Function*](42_Functional--Error_Handling.md#total-functions)
    returns errors as data in explicit wrapper types instead of raising them.

This chapter asks a different question:
does the exception pass from callee to caller?
If you write a function `a()` that calls a function `b()` that raises an exception,
then `a()` raises that exception too, unless `a()` catches it.
`a()`'s signature says nothing about the exception.
Whichever school you join, `a()` takes the exception on by calling `b()`.
An exception is therefore an Effect,
alongside the side effect and the side cause.

## Converting Effectful to Pure

You make `slope()` from `divide_by_zero_impurity.py` pure by transforming its exception Effect.

### Return a Result Type

Wrap the answer and the failure in a `Result`,
the way [Error Handling](42_Functional--Error_Handling.md#turning-exceptions-into-results)
does.
If you decorate the original `slope()`, unchanged, with that chapter's `@safe`,
every exception it raises becomes a value instead of a crash:

```python
# slope_result.py
from result import Err, Ok
from safe import safe

@safe
def slope(rise: int, run: int) -> float:
    return rise / run

for args in [(10, 2), (10, 0)]:
    match slope(*args):
        case Ok(answer):
            print(f"slope{args} = {answer}")
        case Err(error):
            print(f"slope{args}: {type(error).__name__}")
#: slope(10, 2) = 5.0
#: slope(10, 0): ZeroDivisionError
```

Because `@safe` catches whatever `slope()` raises, the fix is the decorator,
not a change to the function it wraps.
`slope()` is now total.
Every call returns a `Result`,
and the caller must unpack it to reach the number.

### Catch the Exception You Expect

If you catch and handle the exception within the function,
the exception stays inside that function, so it is not an Effect.
`slope()` can catch `ZeroDivisionError` and turn the failure into an ordinary `float`,
its existing return type, instead of introducing a new type:

```python
# slope_catch.py
from exceptions import expect

def validate(run: int) -> int:
    if run < 0:
        raise ValueError(f"run cannot be negative: {run}")
    return run

def slope(rise: int, run: int) -> float:
    try:
        return rise / validate(run)
    except ZeroDivisionError:
        return float("inf")

print(slope(10, 2))
#: 5.0
print(slope(10, 0))
#: inf
expect(ValueError, slope, 10, -1)
#: [ValueError] run cannot be negative: -1
```

Catching the exception works with the types you have.
But it guards only the exceptions `slope()`'s `try` names.
`validate()` raises `ValueError` for a negative `run`,
and the `try` around it catches `ZeroDivisionError` and lets `ValueError` propagate.
Because `slope()` calls `validate()`,
`validate()`'s Effect becomes `slope()`'s Effect.

`slope_catch.py` puts `validate()` directly above `slope()`,
so the uncaught `ValueError` is easy to spot.
In a real call stack the `raise` is usually in another file, several calls down.
Catching by hand covers only the exceptions you know a callee can raise.
Knowing every one of them means reading every callee,
and an Effect Management System replaces that tedious, error-prone work.

C++ and Java tried to track exceptions with *exception specifications*,
a list of exceptions written by hand on each function.
Java's compiler checks the list,
while C++ checked it at runtime and ended the program on an exception the list left out.
Neither language inferred the list from the functions a body called,
so an exception introduced three levels down meant editing every signature above it by hand.
Programmers usually avoided that work by widening the specification until it permitted every exception.
The specifications exposed implementation details,
and most people now count them a failure.
C++ reduced its version to a single bit: whether a function can throw.

### Make the Bad Value Impossible

The third approach removes the failure from `slope()` instead of handling it there.
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes illegal values impossible to construct.
If you give `run` a type that excludes zero,
the check moves out of `slope()` and into the type:

```python
# nonzero.py
from record import record

@record
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value
```

`slope_nonzero.py` builds a valid `NonZero` and then tries to build one that holds 0:

```python
# slope_nonzero.py
from exceptions import expected
from nonzero import NonZero, slope

print(slope(10, NonZero(2)))
#: 5.0
with expected(ValueError):
    NonZero(0)
#: [ValueError] NonZero cannot hold 0
```

The check runs once, in `__post_init__()`,
when `NonZero(...)` builds the instance.
Every function that receives a `NonZero`, including `slope()`,
inherits that guarantee.
Because `slope()` cannot divide by zero,
it returns `rise / run.value` as a `float` rather than a `Result`.

### Combine the First and Third

All three approaches keep a division by zero from escaping `slope()` as an exception,
but each puts the handling in a different place.
A `Result` makes every caller handle failure explicitly, at every call site.
`@safe` catches `Exception`,
so `slope_result.py`'s `Result[float, Exception]` cannot distinguish `ZeroDivisionError` from a bug.
[Error Handling](42_Functional--Error_Handling.md#turning-exceptions-into-results)
names the same limitation.
Catching by hand puts the fix inside `slope()`,
where the `try` catches the exceptions it names and lets the rest propagate.
A restrictive type checks once, at construction.
Every function downstream is pure because it receives the type,
not because its author remembered a check.

None of the three makes the failure disappear.
A `Result` turns it into a value, a `try` catches it,
and `NonZero` moves it to the one line that builds the `NonZero`.
They differ in how many functions must know about it.

Standard practice combines the first and third,
the `Result` and the restrictive type.
The boundary parses untrusted input into the restrictive type and reports a bad value as a `Result` instead of raising an exception.
Every function past that boundary takes `NonZero` and stays total:

```python
# slope_edge.py
from nonzero import NonZero, slope
from result import Err, Ok
from safe import safe

@safe
def parse_run(text: str) -> NonZero:
    return NonZero(int(text))

for text in ["2", "0"]:
    match parse_run(text):
        case Ok(run):
            print(f"{text!r}: {slope(10, run)}")
        case Err(error):
            print(f"{text!r}: {error}")
#: '2': 5.0
#: '0': NonZero cannot hold 0
```

`parse_run()` is the only place that can fail,
and `@safe` turns that failure into a `Result` its caller must unpack.
Once the `match` unpacks an `Ok`, `slope()` checks nothing.
`NonZero` guarantees `run.value` isn't 0.

## A Program Can Never Be Pure

A perfectly pure program computes something and writes the result nowhere.
It reads nothing from its environment and changes nothing in its environment,
so its result reaches no screen, file, or socket,
not even the exit code the operating system checks.
From outside the process,
that program looks the same as one that computes nothing.

```python
# pure_and_pointless.py
import timeit
from benchmark import report

def compute_and_discard() -> None:
    total = 0
    for i in range(2_000_000):
        total += i * i

def do_nothing() -> None:
    pass

print(compute_and_discard(), do_nothing())
#: None None
busy = timeit.timeit(compute_and_discard, number=5)
idle = timeit.timeit(do_nothing, number=5)
report(busy=busy, idle=idle, ratio=busy / idle)
print(f"burned real CPU time for nothing: "
      f"{busy > idle * 100}")
#: burned real CPU time for nothing: True
```

Both functions return `None` and touch nothing outside themselves,
so a caller sees the same thing from each.
`compute_and_discard()` still takes measurably longer,
because Python runs every loop you write, worthless or not.
A perfectly pure computation, followed to its logical end,
is a space heater with extra steps.

Effects are not a defect to design away.
They are the reason a program exists.
Effect Management keeps the Effects and isolates them,
so the rest of the program can stay pure.
People call this "pushing the Effects to the edges."

What do you gain by keeping the rest pure?
The first and most obvious answer is parallelism.
A pure function reads and writes nothing shared,
so it is safe to run in parallel.
The same guarantee makes testing trivial.
A pure function needs no setup or teardown, and nothing to mock.
Call it with arguments and check the result.

## Two Phases of Effect Analysis

Think of Effect analysis as two phases.
The first phase separates pure from impure, and produces parallelism, caching,
and easy testing for the pure part.

The second phase divides the impure part by kind,
and each kind yields its own benefit:

- **Exceptions** [become data](#converting-effectful-to-pure) in a `Result`.
  Failures turn into values whose type the checker verifies,
  and a test checks for an `Err` as easily as an `Ok`.
- **Side causes** become replaceable inputs.
  A test substitutes a constant clock for the real one,
  or a seeded generator for true randomness,
  and the function under test becomes repeatable.
- **Side effects** become replaceable outputs.
  A test swaps the real database or console for a stand-in that records the writes,
  then inspects the recording.

Each of those benefits is a testing benefit, for one reason.
A test must run in an environment it controls,
and an untracked Effect is part of the environment outside that control.
Every Effect you isolate is one your tests can control.

Every one of those benefits depends on knowing where the Effects are.
In a small program you find them by inspection.
As programs grow, inspection stops scaling.
An Effect Management System replaces it.

## Effect Management Systems

The currency helper from the chapter's opening is the ordinary case.
Most functions in most programs perform Effects their signatures leave out,
and that makes code hard to understand:

- Can you call this function in a test without mocking every service it calls?
- If you call it twice with the same arguments, do you get the same result?
- Does it behave differently in a different environment?
- Can it fail, and does it fail silently or loudly?

The function's signature answers none of these questions.
You must read the implementation, then trust that you found everything it needs,
everything it changes, and everything that might go wrong.
In a small codebase you can hold that knowledge in your head.
In a large one you cannot.
A function you understand today gets called by a function written next week,
which gets called by code a colleague writes next month.
Each step adds dependencies the signatures hide,
until the whole set exceeds what any one person knows.

Tracking supplies that knowledge.
With it you know what a function does:
whether it is safe to run in parallel with another,
and what it does when you call it twice in a row.
That knowledge lets you compose functions,
and composition is how programs grow large.

### Tracking and Management

An Effect Management System (EMS) keeps track of Effects in functions.
If your function calls an effectful function,
that Effect belongs in your function's type.
If another function then calls yours,
the same Effect belongs in that function's type,
and so on out to the edge of the program.
A native system adds each Effect for you.
A library like Stateless has you declare each one,
and the type checker verifies each declaration.
With an EMS, the function signature tells you whether the function is pure,
and for an impure function it names the kinds of impurity.

A full EMS does three things:

1. **Tracks Effects.**
   The type system records which Effects a function may perform.
2. **Separates each Effect's interface from its implementation.**
   A function declares which Effects it uses, not how to fulfill them.
3. **Binds the implementation later.**
   Some caller or context supplies the implementation,
   at a point after the function's definition.

The first item can stand alone.
The difference between it and the whole list matters in the chapters that follow.
*Effect tracking* tells you which Effects a function can perform.
Tracking alone tells you whether a function is pure,
and names the kinds of impurity a caller inherits.
Effect management is tracking plus the second and third items.
Once an Effect is an interface and a caller binds the implementation later,
you can replace what the Effect does and leave the function that performs it as written.
Tracking reports a function's Effects, and management lets you control them.
Tracking alone appears twice later in this chapter:
in most of the languages in [Custom AI Languages with Effects](#custom-ai-languages-with-effects),
and in Python's `async`,
which [Effect Management for Python?](#effect-management-for-python) examines.

The third item names *delayed binding*.
Delayed binding exists so that the same codebase can serve many contexts
(test, production, retry-wrapped) without edits.
When a hundred functions declare "I need something that can read from storage,"
none of them names a storage implementation.
Each declaration propagates to its caller, up to a single point,
usually the edge of the program, where storage binds to an implementation.
Changing that one binding changes the behavior of all hundred functions at once.
A test provides an in-memory binding, production provides the real database,
and the code of all hundred functions stays the same.

Cross-cutting behavior binds at the same point.
To add caching, tracing, or retries to every storage access,
you insert a layer at the binding point instead of touching every call site.
Variation concentrates at the boundary of the program,
and the functions below it stay simple and uniform.

### Effects by Hand

Every technique in [Converting Effectful to Pure](#converting-effectful-to-pure)
manually manages one Effect, the exception.
A `Result` tracks failure in the return type.
A `try` binds the failure to a handler.
A restrictive type moves the failure to construction.
Each is a hand-built version of something an EMS automates.

Side effects and side causes also have a by-hand technique:
pass the implementation in as a parameter.
Instead of calling the built-in `input()` and `print()`,
`greet()` declares what it needs:

```python
# ask_tell.py
from dataclasses import dataclass, field
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

def greet(ask: Ask, tell: Tell) -> None:
    name = ask.ask("What is your name? ")
    tell.tell(f"Hello, {name}!")

class Scripted:
    def ask(self, prompt: str) -> str:
        return "Alice"

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)

    def tell(self, message: str) -> None:
        self.messages.append(message)
```

`greet()` performs an `Ask` Effect and a `Tell` Effect,
and its signature says so, because the parameters are the Effects.
The bindings come later.
`greet_demo.py` binds them to test stand-ins, `Scripted` and `Capture`,
and checks the greeting with no console in sight:

```python
# greet_demo.py
from ask_tell import Capture, Scripted, greet

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
```

A production caller passes objects that read with `input()` and write with `print()`,
and `greet()` stays the same.
Delayed binding by hand explains why "pass in your dependencies" is such durable advice.

The signature says what `greet()` needs, not everything `greet()` might do.
A `print()` in the body is still invisible.

The technique works, but you do the bookkeeping.
Every function that calls `greet()` must accept an `Ask` and a `Tell` so it can pass them down.
Parameters accumulate at every level of the call stack:

```python
# bookkeeping_scales.py
from ask_tell import Ask, Capture, Scripted, Tell, greet

def session(ask: Ask, tell: Tell) -> None:
    greet(ask, tell)

def menu(ask: Ask, tell: Tell) -> None:
    session(ask, tell)

def main(ask: Ask, tell: Tell) -> None:
    menu(ask, tell)

captured = Capture()
main(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
```

`session()`, `menu()`,
and `main()` each name both parameters and use them for one thing:
passing them to the function below.
You propagate every parameter by hand.
If a new helper that `greet()` calls needs a `Log` Effect,
you edit every signature on the path: `greet()`, `session()`, `menu()`,
and `main()`.
With the new helper, that makes five signatures (see exercise 2).

Dependency injection frameworks relocate this bookkeeping into a wiring layer,
but you must tell the injector what every function needs,
and tell it again when that changes.
A mistake in the wiring appears only at runtime, when the program fails.

Python has one mechanism that propagates on its own.
A [`ContextVar`](19_Techniques--Concurrency.md#context-that-follows-the-call-chain)
holds a value for the current task,
and any function the task calls reads the value without receiving it as an argument.
The `ContextVar` supplies automatic propagation,
but it removes the parameter along with the one benefit the parameter provided.
`greet(ask, tell)` states its Effects in its signature,
and a `greet()` that reads two `ContextVar`s hides them.
Setting the wrong one, or forgetting to set one,
raises a `LookupError` at the read, in whatever frame reads it.
A `ContextVar` created with a default returns that default instead,
so the read succeeds and the mistake appears later,
as whatever wrong result the default produces.
The bookkeeping stays, and the type checker can no longer verify it.

An EMS moves the bookkeeping into the type system.
A native system maintains it for you.
With a library like Stateless,
you write the declarations and the type checker verifies each one.
Moving the bookkeeping into the type system takes a second channel in the signature,
one that carries Effect information outside the argument list.

### Native Effect Management

Ideally, Effect tracking comes built into the language,
as a *native* Effect system.
In a native system, the type system holds Effects alongside ordinary types.
A function's signature carries two pieces of information: what it returns,
and what Effects it performs.
The body looks like ordinary sequential code.
The compiler reads what the body calls and infers the Effects,
the same way it tracks whether a value is an integer or a string.

The examples in this section and the next come from my research,
in which I build the same small programs in four Effect-managing languages.
The first is [Koka](https://koka-lang.github.io/),
a research language with native Effects.
Its greeting program has the same `ask` and `tell` as `ask_tell.py`:

```koka
import std/os/readline

// Effect declarations: the interface, not the implementation
effect ask
  fun ask(prompt : string) : string

effect tell
  fun tell(message : string) : ()

// Core logic: the Effect row <ask,tell> is part of the type
fun greet() : <ask,tell> ()
  val name = ask("What is your name? ")
  tell("Hello, " ++ name ++ "!")

// Main binds each Effect to an implementation
fun main() : <console,exn> ()
  with fun ask(prompt)
    print(prompt)
    readline()
  with fun tell(message)
    println(message)
  greet()
```

The angle brackets in `greet()`'s signature hold the *Effect row*,
the set of Effects the function performs.
The row is the second channel.
`ask` and `tell` are part of the type, and the parameter list stays empty.

The compiler infers the row from what the body calls.
If another function calls `greet()`,
the compiler adds `ask` and `tell` to that function's row automatically.
The by-hand version makes you add them yourself, one parameter per signature.
Since the compiler does that work, you rarely write a row by hand.
The listing writes out the rows of `greet()` and `main()` so you can read them.
You annotate explicitly when you want a constraint,
such as declaring that a function must remain Effect-free.

Something must eventually fulfill every Effect,
and the construct that fulfills one is a *handler*.
The compiler rejects a program that performs an Effect with no handler in scope,
so every Effect a running program performs has a handler.
Think of a handler as a generalized `except` block.
An `except` block intercepts exceptions and decides what the program does next.
A handler intercepts any Effect operation and decides what it means.
In `main()`, the `with fun ask(prompt)` handler decides that `ask` means "prompt the console and read a line."

Handling an Effect also discharges it.
`main()`'s row is not `<ask,tell>` but `<console,exn>`.
The handlers remove `ask` and `tell`,
and the row that remains holds the Effects the handler bodies perform:
`console` from the printing and reading, `exn` because `readline()` can fail.

Separating the request from its fulfillment is the core of every Effect system.
The code that requests an Effect is separate from the code that performs it,
and a handler connects the two.
`greet()` names `ask` and `tell`, and the handler decides what each one means.
A different handler decides differently.
A test installs one that returns a known name, and the same `greet()` runs.

Handlers can do more than `except` blocks can.
When an operation runs, the handler receives the *continuation*:
the rest of the computation from that point forward.
An `except` block has two options, catch or propagate,
and both discard the continuation.
A handler can resume the continuation once,
and the operation then behaves like a normal function return.
A handler can discard the continuation,
and the operation then behaves like an exception.
A handler can even invoke the continuation several times,
which is how native systems express retries and backtracking as ordinary handlers.
*Algebraic effects* is the name for this design:
operations declared as an interface,
plus handlers that receive the continuation.

A Python generator suspends a computation,
hands control to whoever is driving it, and resumes it with a value.
That makes a suspended generator a continuation you can resume once or discard,
but not resume twice, because nothing can copy a generator's paused frame.
[Generators](45_Effects--Generators.md) covers the full two-way form,
the mechanism behind the Python Effect library in [Stateless](46_Effects--Stateless.md).

[Flix](https://flix.dev/) expresses the same model with different notation.
The Effect set follows a backslash:

```flix
def greet(): Unit \ {Ask, Tell} =
    let name = Ask.ask("What is your name? ");
    Tell.tell("Hello, ${name}!")
```

Languages in this family include Koka, Flix, Eff, Effekt, and Unison.
OCaml 5 added the handler mechanism,
though it does not yet track Effects in function types.

### Library Effect Management

Changing languages is rarely an option.
A team committed to Scala or TypeScript cannot use native Effects,
so designers built *library* Effect systems on top of existing type systems.
In this approach the library does the tracking instead of the compiler.
The library encodes Effect information into the return type of every function.
That encoding changes the mechanism.
Instead of writing a computation and letting the compiler infer its Effects,
you build a *description* of a computation, and execute the description later.
[ZIO](https://zio.dev/) is such a library, for Scala.
In ZIO, "Hello, World!" is a description first and a run second:

```scala
import zio.*
import zio.Console.printLine

// The Effect's interface
trait Tell:
  def tell(message: String): UIO[Unit]

// Accessor: lifts the interface method into a ZIO description
object Tell:
  def tell(message: String): ZIO[Tell, Nothing, Unit] =
    ZIO.serviceWithZIO[Tell](_.tell(message))

// Core logic: a value, not an action; nothing runs here
val hello: ZIO[Tell, Nothing, Unit] =
  Tell.tell("Hello, World!")

// The implementation, packaged for delayed binding
val consoleTell: ULayer[Tell] = ZLayer.succeed(new Tell:
  def tell(message: String): UIO[Unit] =
    printLine(message).orDie)

// Entry point: bind the implementation, then execute
object Main extends ZIOAppDefault:
  def run = hello.provide(consoleTell)
```

The three type parameters of `ZIO[Tell, Nothing, Unit]` carry the Effect information.
`Tell` is the environment the computation requires.
`Nothing` is the error type, meaning `hello` cannot fail.
`Unit` is what it produces on success.
The signature does the same job as Koka's Effect row.
It tells you what `hello` needs, what can go wrong, and what comes back.

Everything else in the listing is machinery: a trait for the interface,
a companion object to lift that interface into the `ZIO` type,
a `ZLayer` to package the implementation, and a `provide()` call to bind it.
All of that, to print one string.
The machinery exists because the language cannot intercept an Effect at the point where it runs,
the way a native handler can.
A library works with values alone, so every Effect must become a value.
`hello` is a data structure describing a program.
Execution begins when the ZIO runtime interprets that structure at `run`,
the boundary between description and action (sometimes called "the edge").

The TypeScript [Effect](https://effect.website/) library works the same way:

```typescript
import { Context, Effect, Layer } from "effect"

// The Effect's interface, as a service
class Tell extends Context.Service<
  Tell,
  { tell: (message: string) => Effect.Effect<void> }
>()("Tell") {}

// Core logic: still just a description
const hello = Effect.gen(function* () {
  const tell = yield* Tell
  yield* tell.tell("Hello, World!")
})

// The implementation, packaged for delayed binding
const ConsoleTell = Layer.succeed(Tell, {
  tell: (message) => Effect.sync(() => console.log(message)),
})

// The boundary: descriptions above, execution here
Effect.runPromise(hello.pipe(Effect.provide(ConsoleTell)))
```

The description/execution split is an artifact of building the system as a library,
rather than a feature of Effect Management.
Native systems deliver tracking, interface separation,
and delayed binding while the code runs eagerly,
with no description trees and no interpreter.
A library must build descriptions.
In a language not designed for Effects,
a library gets delayed binding by deferring execution.

Deferring execution adds one question to every value you handle:
is it a description or an action?
Code that mixes the two compiles cleanly but misbehaves,
because the imperative part runs when the program builds the description,
not when the runtime executes it.

Libraries in this family include ZIO, Cats Effect, and Kyo in Scala,
polysemy and effectful in Haskell, Effect in TypeScript,
and Stateless in Python.
Stateless builds on generators, so [Generators](45_Effects--Generators.md)
covers that mechanism first.
[Stateless](46_Effects--Stateless.md)
then writes these programs again in the language this book teaches.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md#abilities-are-not-special)
rebuilds the `ask`/`tell` pair from [Effects by Hand](#effects-by-hand).

### Custom AI Languages with Effects

At this writing, experimental languages designed for AI code generation are proliferating.
Their designers try to balance better code generation for the AI against human verifiability.
A language written for an AI can drop the conveniences that help a person read code.
An AI can start using that language as soon as it works,
while people take years to learn a new language written for them.

Most of these languages are tracking systems,
in the sense [Tracking and Management](#tracking-and-management) gives the term.
They provide the first part of a full EMS.
For their purpose the other two parts, interface separation and delayed binding,
are liabilities.
When the host supplies every implementation,
it can guarantee what the generated code does.
Generated code that rebinds an implementation would break that guarantee.

Two go further.
In [Pact](https://github.com/KikotVit/pact-lang),
a function declares a `needs` clause.
A separate `using` clause rebinds each implementation,
so tests can swap Effects deterministically.
[Lumen](https://alliecatowo.github.io/lumen/)
writes source as markdown with algebraic effects,
and its `bind effect` rebinds a handler separately from its use.
Both separate an Effect's interface from its implementation and bind the implementation later,
the second and third properties of a full EMS.

## Effect Management for Python?

The Python language has no Effect Management System, but it has a start.
Python tracks one Effect in function signatures,
and enforces that tracking on every caller: `async`.

```python
# coroutines_are_descriptions.py
import asyncio

ran: list[str] = []

async def greet() -> str:
    ran.append("body")
    return "Hello"

description = greet()  # Nothing runs
print(type(description).__name__, ran)
#: coroutine []
print(asyncio.run(description), ran)
#: Hello ['body']
```

Calling `greet()` builds a [coroutine object](19_Techniques--Concurrency.md#asyncio-mechanics),
a description of work, and `ran` stays empty.
The body runs only when something drives the description: an `await`, a task,
or `asyncio.run()`.
That description/execution split is the library Effect system model.
Descriptions compose inside `async def` functions,
and `asyncio.run()` is the boundary where description becomes action.

Python enforces the tracking the way an EMS does.
`await` is a syntax error outside an `async def`,
so any function that awaits a coroutine must become `async`,
and so must its callers, all the way up to the edge.
If you replace "async" with "network access" or "database write" in that sentence,
you have described Effect tracking.
Python demonstrates that the machinery can work,
and hard-codes it to a single Effect, asynchrony,
rather than letting you declare your own.

Third-party libraries supply pieces of the rest.
The [returns](https://github.com/dry-python/returns)
library provides a `Result` container like the one in [Error Handling](42_Functional--Error_Handling.md),
a `Maybe` container for a value that might be absent,
an `IO` container that marks a value as having come from input/output,
and a `RequiresContext` container for delayed binding of dependencies.
The [effect](https://pypi.org/project/effect/)
library ports the description/execution split to Python.
The name is all it shares with the TypeScript library.
Code builds objects that describe intents.
Separate performers execute them, and a test can swap in its own performers.
The [eff](https://github.com/orsinium-labs/eff) library models Effect handlers.
Each of these supplies part of an EMS, and none supplies all three parts.

One library supplies all three parts.
[Stateless](46_Effects--Stateless.md)
encodes each Effect's dependencies and failures into the return type of every function that performs that Effect.
A type checker verifies that each caller carries them forward.
Leaving a declared dependency unbound is a type error.
Calling an effectful function from one annotated as pure is a type error.
Stateless therefore supplies tracking, interface separation,
and delayed binding, the three properties of a full EMS,
inside Python's existing type system.

The guarantee has a limit.
Stateless verifies that the Effects you declare propagate consistently.
A function can still call `print()`, next to its carefully declared Effects.
In Koka, that call changes the function's Effect row, and every caller's row.
In Python, neither Stateless nor the type checker reports it.
A library checks the Effects you wrote down,
but checking the ones you left out takes the language.

Could Python itself gain Effect tracking,
so that a tool infers every declaration instead of you writing it?
The annotation syntax could carry the Effect row.
Imagine a signature that declares its Effects the way `async def` already declares one.
The hard part is propagation, not syntax.
A type checker must compute the Effect row of every function from the functions it calls,
across every library on PyPI, almost all of which carry no Effect annotations.
`async` succeeded because it arrived as part of the language.
The interpreter enforces it,
and its keyword marks each function that carries the Effect.
An Effect row must instead cover every library in an ecosystem of untracked code.
Gradual typing faced the same problem, and took a decade.

No PEP proposes Effect tracking today.
If one arrives, it will contain the ideas in this chapter.
[Effect Tracking](A_Effect_Tracking.md) works through one candidate design:
an Effect row carried in `typing.Annotated` metadata,
and an analysis of the tool that would propagate and check it.
The appendix calls that design *algebraic effect tracking*:
the row a native system keeps, without the handlers.
[An Effect Checker](B_An_Effect_Checker.md)
builds the part of that tool that needs no type inference.

## Effects Are the Next Barrier

The history of programming is a history of scaling barriers.
Each time, the pattern is the same.
Something the programmer tracks by hand works in small programs.
Systems grow until hand-tracking fails.
The solution moves that tracking into the language or the toolchain,
and a generation later, nobody can imagine doing it by hand.

Namespaces are the clearest example.
Early languages put every name in one global namespace,
and the programmer prevented collisions by hand.
Collisions were often silent, producing hidden bugs,
and third-party libraries made the problem worse.
The solution divided names among separate namespaces.
In Python, every module is automatically a namespace,
and the practice is so settled that the Zen of Python ends by celebrating it:
<!-- vale House.EmDash = NO -->
"Namespaces are one honking great idea -- let's do more of those!"
<!-- vale House.EmDash = YES -->
Nobody audits their imports for name collisions anymore.
The language does the bookkeeping.

The same pattern repeats across the field.
Version control gave every state of the code a name to which you can return,
so experimenting became safe.
Automated testing moved "does it still work?" from a manual ritual into the build.
Garbage collection took the tracking of memory ownership out of the programmer's head.
Each of these met resistance as unnecessary overhead, then won adoption,
then faded as a question.

Effects are the barrier we are inside right now,
and a barrier is hardest to see from inside.
We build programs from other people's code,
and we don't know what that code does.
It might change something in the world.
It might read from an unreliable source.
It might fail and take the system down.
You discover these behaviors by trusting documentation, reading source,
and observing failures.
Then you write compensating code.
An enormous share of professional programming is this activity,
and it has been normal for so long that it goes unnoticed.
Like every hand-tracked concern before it, this one stops scaling.

An Effect Management System moves the bookkeeping into the type system.
The function signature answers the questions from [Effect Management Systems](#effect-management-systems):
what does this function need, what does it change, what can go wrong.
The compiler checks every composition,
comparing each callee's Effects with the caller's declaration at each call.

The languages that track Effects today are young,
and the libraries that retrofit Effect tracking are demanding.
That was true of every solution to every previous barrier at this stage.
Namespaces once looked like ceremony.
Effect tracking will look obvious in hindsight,
and future programmers will regard a function with hidden Effects the way you regard a program written in one global namespace.

Python offers no native Effect tracking beyond `async`, and will not soon.
[Generators](45_Effects--Generators.md) supplies the mechanism a library needs,
[Stateless](46_Effects--Stateless.md)
builds a library Effect system on that mechanism,
and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
puts the library to work.

## Exercises

Try each exercise before opening its [solution](../Solutions/44_Effects--Effect_Management/).

1.  Write the production bindings for `ask_tell.py`:
    a `Console` class whose `ask()` calls `input()` and whose `tell()` calls `print()`,
    and run `greet(Console(), Console())` interactively.
    Confirm `greet()` requires no change.
    Serving a new context without edits is what delayed binding provides.
2.  Do the bookkeeping the chapter describes.
    Starting from `bookkeeping_scales.py`, add a `Log` Effect
    (a protocol with `log(message)`) used by a new helper that `greet()` calls,
    and log from `greet()` too.
    The chapter counts five signatures for that version.
    Say how many of the five use the `Log` they name,
    and then what an EMS would do instead.
3.  Classify every Effect in `slope_catch.py`,
    `withdraw()` from [Foundations](40_Functional--Foundations.md#pure-functions),
    and the `Thermometer` that keeps a `_celsius` from [*Observer*](30_Patterns--Observer.md#the-pythonic-observer):
    side effect, side cause, or exception.
    Which of the three conversions from [Converting Effectful to Pure](#converting-effectful-to-pure)
    applies to the exceptions,
    and which technique from [Effects by Hand](#effects-by-hand)
    applies to the rest?
4.  `NonZero` guards zero but not negative values,
    while `validate()` in `slope_catch.py` rejects negatives but not zero.
    Build a `PositiveInt` that makes both bad values unconstructable,
    rewrite `slope()` to take it,
    and note which checks disappear from `slope()` as a result.
5.  `coroutines_are_descriptions.py` shows that `async` tracks one Effect.
    Write a synchronous `total_price()` that calls a helper,
    then make the helper `async` and follow what the type checker and the interpreter force you to change,
    all the way up to `asyncio.run()`.
    Name the two properties of a full EMS that `async` lacks,
    using the three-item list in [Tracking and Management](#tracking-and-management).
