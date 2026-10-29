# Effect Management

> A function does more than its signature says: it might read a clock, write to a log,
> open a connection, modify global state, and more.
> Effect Management puts those actions in the signature, where a reader sees them,
> a type checker verifies them, and a test swaps them for stand-ins.

A test you wrote last week starts failing about one run in five.
The function it calls computes a total price, and the math is right.
Three calls down, a helper that formats currency reads a configuration service and writes to an audit log.
Every signature on the path hides the read and the write.

This book emphasizes the benefits of pure functions:

- [Functional Foundations](40_Functional--Foundations.md#pure-functions)
  contrasts `double()`, a pure function, with `withdraw()`,
  which depends on state left over from earlier calls.
- [Performance](18_Techniques--Performance.md#caching)
  turns naive recursive Fibonacci from 242,785 runs of its body into 26 with `functools.cache`.
  Caching works only when the cached function is pure.
- [Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
  turns shapes into immutable data,
  so one pure function replaces a method on each class.
- [*Observer*'s](30_Patterns--Observer.md#the-model)
  `recolored()` returns a new grid instead of mutating the one it receives,
  so a test checks the change without a GUI.
- [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
  converts competition between items into a dictionary lookup.
- [*Composite* and *Interpreter*'s](34_Patterns--Composite_and_Interpreter.md#simplification-rewrites-the-tree)
  `simplify()` returns a new tree instead of editing the one it receives.

In each case, you can determine purity by reading a single function.
Reading a single function stops working when that function calls other functions.
If any of those other functions interacts with the environment,
it makes the calling function impure.
To determine if a function is impure,
you must either trust the documentation or examine the code of every function it calls.

Reading every callee soon becomes tedious and error-prone.
A type system that verifies purity does the work for you.
That type system is an *Effect Management System*.

## What Is an Effect?

An *Effect* is anything a caller takes on by making a call,
beyond receiving the return value.
If your function calls a function that writes to an audit log,
your function writes to an audit log.
If your function calls a function that reads the time of day,
the result depends on the time of day.
If your function calls a function that raises a `ValueError`,
your function raises a `ValueError`.
The log write, the clock read,
and the exception become your function's Effects too,
and no signature on the path mentions any of them.

A behavior confined to one function is easy to manage,
because one read of that function tells you what's happening.
But an Effect passes from callee to caller, one call at a time.
Every signature on the path hides it.

Three things pass from callee to caller.
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
because the operation that changes the environment sits in that function's body.
In the caller, the side effect is invisible.

The second is a *side cause*, the counterpart of a side effect:
what the environment does to the function.
Suppose your function reads the time of day.
The read leaves the environment as it was,
yet the result of your function differs from one call to the next.
Information a function uses beyond its arguments is a side cause whenever that information changes between calls.
The usual sources are I/O,
such as the time of day or reading from a network connection.
A global variable that something else can rebind is another source.

The third kind of Effect is an exception,
which propagates from callee to caller but doesn't appear in the function signature.

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
The question has two answers:

1.  **Pure.**
    Raising `ZeroDivisionError` instead of returning a number does not break purity.
    Purity says the outcome depends on the arguments alone.
    The same arguments still produce that same exception every time.
    The function reads its arguments alone and leaves everything outside itself as it was.

    Computer science theory backs this view.
    Pure languages like Haskell treat an unhandled runtime exception or crash as a *bottom* value, denoted ⊥.
    A bottom value stands for a computation that never produces an ordinary value.
    Because ⊥ is a value in the theory, raising an error that crashes the program
    is referentially transparent.
    Replacing the function call with the crash leaves the program's behavior the same.

2.  **Functional.**
    Exceptions bypass normal control flow.
    That bypass makes it difficult to reason about code.
    Functional programming avoids them altogether for that reason.
    A [*Total Function*](42_Functional--Error_Handling.md#total-functions)
    returns errors as data in wrapper types instead of raising them.

For Effects, a different question matters more:
does the exception pass from callee to caller?
If you write a function `a()` that calls a function `b()` that raises an exception,
then `a()` raises that exception too, unless `a()` catches it.
`a()`'s signature says nothing about the exception,
but `a()` takes the exception on by calling `b()`.
An exception is therefore an Effect,
alongside the side effect and the side cause.

## Converting Effectful to Pure

You make `slope()` from `divide_by_zero_impurity.py` pure by transforming its exception Effect.

### Return a Result Type

Wrap the answer and the failure in a `Result`,
the way [Error Handling](42_Functional--Error_Handling.md#turning-exceptions-into-results)
does.
If you decorate `slope()` with that chapter's `@safe`,
every exception `slope()` raises becomes a value instead of a crash:

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

Because `@safe` catches every exception `slope()` raises,
`slope()` becomes total.
Every call returns a `Result`,
and the caller must unpack it to reach the number.

### Catch the Exception You Expect

If you catch and handle the exception within the function,
the exception never propagates to the caller, so it is not an Effect.
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

Catching the exception keeps `slope()`'s return type, `float`.
But an `except` clause catches the exceptions it specifies and lets the rest propagate.
Because `slope()` calls `validate()`,
`validate()`'s Effect becomes `slope()`'s Effect.

`slope_catch.py` puts `validate()` directly above `slope()`,
so the uncaught `ValueError` is easy to spot.
In a real call stack the `raise` is usually in another file, several calls down.
A `try`/`except` you write covers the exceptions you know a callee can raise.
The rest reach the caller.
Knowing every exception that can reach the caller means reading the code for every callee.
An Effect Management System replaces that tedious, error-prone work.

*Exception specifications* in C++ and Java track exceptions with a list the programmer writes on each function.
Java's compiler checks the list
(Java calls the listed exceptions *checked exceptions*), while C++,
before C++17 removed them,
checked it at runtime and ended the program on an exception the list left out.
Neither language infers the list from the functions a body calls,
so an exception introduced three levels down means editing every signature above it.
Programmers usually avoid that work by widening the specification until it permits every exception.
The specifications expose implementation details.
Most people now count them a failure.
C++11 reduced its version to a single bit:
whether a function can throw an exception.

### Make the Bad Value Impossible

The third approach removes the failure from `slope()` instead of handling it there.
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes illegal values impossible to construct.
If you give `run` a type that excludes zero,
the type's `__post_init__()` runs the check instead of `slope()`:

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

A `NonZero` that holds 2 passes to `slope()`,
while building one that holds 0 raises a `ValueError`:

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
Every function that takes a `NonZero` receives a value guaranteed to be nonzero.
Because `slope()` cannot divide by zero,
it returns `rise / run.value` as a `float` rather than a `Result`.

### Combine the First and Third

All three approaches keep a division by zero from reaching `slope()`'s caller as an exception,
but each handles it in a different place.
With a `Result`, the place is every call site,
where each caller unpacks the `Result` and decides what a failure means.
With a `try`, the place is inside `slope()`,
where the `except` clause handles `ZeroDivisionError`.
Every other exception propagates through `slope()` to its caller.
With `NonZero`, the place is `__post_init__()`, which runs once,
when `NonZero(...)` builds the instance.
`slope()` trusts its argument,
as does every other function that takes a `NonZero`,
because the check ran when the caller built it.

None of the three makes the failure disappear.
A `Result` turns it into a value.
A `try` catches it.
`NonZero` moves it to the line that builds the argument.
`NonZero(0)` raises a `ValueError` before `slope()` runs.
The three differ in how many functions contain code for the failure.

`slope_result.py` has a drawback that `slope_catch.py` and `nonzero.py` avoid.
`@safe` catches `Exception`,
so the decorated `slope()` returns `Result[float, Exception]`.
That error type covers the `ZeroDivisionError` from a zero `run`,
which the caller can handle,
and a `NameError` from a misspelled name inside `slope()`,
which is a bug the caller cannot handle.
The caller receives both as an `Err` with the same static type,
so the caller's `case Err(error)` must inspect the exception to tell a bad argument from a bug.
[Error Handling](42_Functional--Error_Handling.md#turning-exceptions-into-results)
describes this limitation of `@safe` and the production fix,
a version that catches the exception types you specify and lets the rest propagate.

Standard practice combines the first and third,
the `Result` and the `NonZero` type.
`parse_run()` receives input as text, parses the text into a `NonZero`,
and returns a `Result` instead of raising an exception.
`slope()` takes the `NonZero` that `parse_run()` built and stays total:

```python
# slope_edge.py
from nonzero import NonZero, slope
from result import Err, Ok, Result

def parse_run(text: str) -> Result[NonZero, ValueError]:
    try:
        return Ok(NonZero(int(text)))
    except ValueError as error:
        return Err(error)

for text in ["2", "0", "two"]:
    match parse_run(text):
        case Ok(run):
            print(f"{text!r}: {slope(10, run)}")
        case Err(error):
            print(f"{text!r}: {error}")
#: '2': 5.0
#: '0': NonZero cannot hold 0
#: 'two': invalid literal for int() with base 10: 'two'
```

`int()` rejects `"two"`,
and `NonZero` rejects the `0` that `int()` returns for `"0"`,
each with a `ValueError`.
The error type in `parse_run()`'s `Result` is `ValueError`,
the one failure its caller can handle,
rather than `@safe`'s catch-all `Exception`.
A bug inside `parse_run()` raises some other exception,
and that exception propagates to the caller.

When the `match` unpacks an `Ok`, `slope()` divides at once,
because `NonZero` guarantees that `run.value` is nonzero.

## A Program Can Never Be Pure

A completely pure program computes a result and keeps it in the process's memory.
It takes its inputs from its own source code and leaves its environment as it was,
so no screen, file, or socket ever receives the result.
The exit code the operating system checks is the same regardless of what the program computed.
From outside the process,
that program is indistinguishable from an empty program.

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

`compute_and_discard()` takes measurably longer,
because Python runs every loop you write, worthless or not.
A perfectly pure computation, followed to its logical end,
is a space heater with extra steps.

Effects are not a defect to design away.
They are the reason a program exists.
Effect Management keeps the Effects and isolates them,
so the rest of the program can stay pure.
People call this "pushing the Effects to the edges."

The most obvious gain from purity is parallelism.
Everything a pure function touches lives in its arguments, its local variables,
and its return value,
so the function is safe to run in parallel with any other code.

The same guarantee makes testing trivial.
Calling a pure function with the same arguments produces the same result every time.
No side cause, side effect, or failure can surprise you.

## Two Phases of Effect Analysis

The first phase of Effect analysis separates pure from impure.
The pure part is safe to run in parallel, safe to cache, and simple to test.

The second phase divides the impure part by kind.
Each kind yields its own benefit:

- **Failures** [become data](#converting-effectful-to-pure) in a `Result`.
  The caller handles them as ordinary return values instead of catching exceptions.
- **Side causes** become replaceable inputs.
  A test substitutes a constant clock for the real one,
  or a seeded generator for true randomness.
  The function under test becomes repeatable.
- **Side effects** become replaceable outputs.
  A test swaps the real database or console for a stand-in that records the writes,
  then inspects that recording.

A test must run in an environment it controls.
An untracked Effect is outside that control.
Every Effect you isolate is one your tests can control.

Each benefit depends on knowing where the Effects are.
In a small program you find Effects through inspection.
As programs grow, inspection stops scaling.
An Effect Management System scales.

## Effect Management Systems

Most functions in most programs perform Effects,
and their signatures show only the arguments and the return type.
The hidden Effects make code hard to understand.
A reader who sees only the signature must ask:

- Can you call this function in a test without mocking every service it calls?
- If you call it twice with the same arguments, do you get the same result?
- Does it behave differently in a different environment?
- Can it fail, and does it fail silently or loudly?

The function's signature leaves all four questions open.
You must read the implementation, trusting that you find everything it needs,
everything it changes, and everything that might go wrong.
In a small codebase you can hold that knowledge in your head.
In a large one you cannot.
Callers stack up.
Next week a new function calls the one you read today,
and next month a colleague's function calls that one.
Each layer adds dependencies the signatures hide,
until the whole set exceeds what any one person can know.

Tracking supplies that knowledge.
With it you know what a function does:
whether it is safe to run in parallel with another,
and what it does when you call it twice in a row.
That knowledge lets you compose functions,
and composition is how programs scale.

### Tracking and Management

An Effect Management System (EMS) does three things:

1. **Tracks Effects.**
   The type system records the Effects a function performs.
   If your function calls an effectful function,
   that Effect belongs in your function's type.
   If another function then calls yours,
   the same Effect belongs in that function's type,
   and so on out to the edge of the program.
   The signature then tells you whether the function is pure,
   and for an impure function it specifies the kinds of impurity.
2. **Separates each Effect's interface from its implementation.**
   A function declares which Effects it uses, not how to fulfill them.
   It says "I need something that can read from storage" but doesn't specify a storage mechanism
   (such as a database).
3. **Binds the implementation later.**
   A caller or context supplies the implementation at some point after the function's definition,
   usually the edge of the program.
   The connection between the declaration and its supply is *delayed binding*.

When a hundred functions declare the storage Effect,
one binding point supplies the implementation for all of them.
A test binds an in-memory store, production binds the real database,
while the hundred functions remain untouched.

To add caching, tracing, or retries to every storage access,
you insert a layer at the binding point instead of modifying every call site.
Each swap of an implementation, and each layer added around one,
happens at the edge of the program.

### Effects by Hand

Every technique in [Converting Effectful to Pure](#converting-effectful-to-pure)
manages one Effect, the exception, in code you write.
A `Result` tracks failure in the return type.
A `try` binds the failure to a handler.
A `NonZero` raises a `ValueError` in `__post_init__()`,
before the bad value reaches `slope()`.
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

`greet()` performs an `Ask` Effect and a `Tell` Effect.
Its signature says so, because the parameters are the Effects.

Here, the test binds the Effects to `Scripted` and `Capture`,
so it checks the greeting without using the console:

```python
# greet_demo.py
from ask_tell import Capture, Scripted, greet

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
```

The production version uses objects that read with `input()` and write with `print()`.
Passing those objects instead changes what `greet()` does without changing `greet()`.
The signature says what `greet()` needs, not everything `greet()` might do.

The technique works, but you do the bookkeeping.
Every function that calls `greet()` must accept an `Ask` and a `Tell`.
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
and `main()` each declare both parameters and use them for one thing:
passing them to the function below.
You pass every parameter down at every call.
If a new helper that `greet()` calls needs a `Log` Effect,
you edit every signature on the path: `greet()`, `session()`, `menu()`,
and `main()`.
With the helper's own signature, that makes five (see exercise 2).

Dependency injection frameworks relocate this bookkeeping into a wiring layer,
but you must tell the injector what every function needs,
and tell it again when that changes.
A mistake in the wiring appears only at runtime, when the program fails.

Python has a mechanism that propagates on its own.
A [`ContextVar`](19_Techniques--Concurrency.md#context-that-follows-the-call-chain)
holds a value for the current task,
and any function the task calls reads the value without receiving it as an argument.
The `ContextVar` supplies automatic propagation,
but it removes the parameter along with the two benefits the parameter provided.
`greet(ask, tell)` states its Effects in its signature.
A `greet()` that reads two `ContextVar`s hides them.

Setting the wrong `ContextVar`, or forgetting to set one,
raises a `LookupError` at runtime,
in the stack frame that reads the `ContextVar`.
A `ContextVar` created with a default returns that default,
so the read succeeds and the mistake appears later,
as the incorrect result the default produces.
You must still remember to set every `ContextVar`,
and the type checker cannot verify that you did.

An EMS moves the bookkeeping into the type system.
Either the system infers each Effect from the body,
or you declare it and the type checker verifies the declaration.

### Native Effect Management

Ideally, Effect tracking comes built into the language,
as a *native* Effect system.
In a native system, a function's signature carries three pieces of information:
what it takes, what it returns, and what Effects it performs.
The body looks like ordinary sequential code.
By examining the function calls made in the body,
the compiler infers the Effects made by the function.

The same small program, written four times,
shows how different Effect Management Systems work:

- Two languages with native Effects: Koka and Flix
- Two library Effect systems: ZIO for Scala and Effect for TypeScript

[Koka](https://koka-lang.github.io/) is a research language with native Effects.
Its greeting program has the same `ask` and `tell` as `ask_tell.py`:

```koka
// koka/greet.kk
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
A Koka function type has three parts: the parameter types, the Effect row,
and the result type.
The row sits between the other two.
In `ask_tell.py`, `greet()` receives `ask` and `tell` as parameters.
Here the Effect row carries them, so the parameter list is empty.
The `()` after the row is the return type: Koka's unit type,
the counterpart of Python's `None`.

The compiler infers the row from what the body calls
(this listing writes the rows for `greet()` and `main()` out so you can see them).
If another function calls `greet()`,
the compiler adds `ask` and `tell` to that function's row automatically.
Since the compiler computes each row from the calls in the body,
you rarely write a row yourself.
You write one to specify a constraint,
such as declaring that a function must remain Effect-free.

A *handler* fulfills an Effect.
The compiler rejects a program that performs an Effect with no handler in scope,
so every Effect a program performs must have a handler.
Think of a handler as a generalized `except` block.
An `except` block intercepts exceptions and decides what the program does next.
A handler intercepts an Effect and decides what it means.
In `main()`, the `with fun ask(prompt)` handler says that `ask` means "prompt the console and read a line,"
and the `with fun tell(message)` handler says that `tell` means "print the message."

Handling an Effect also discharges it.
`main()`'s row is not `<ask,tell>` but `<console,exn>`.
The handlers remove `ask` and `tell`,
and the row that remains holds the Effects the handler bodies perform:
`console` for printing and reading, `exn` because `readline()` can fail.

Separating the request from its fulfillment is the core of every Effect Management System.
The code that requests an Effect is separate from the code that performs it,
and a handler connects the two.
`greet()` requests `ask` and `tell`.
The handlers decide what each one means.
Different handlers make different decisions.
A test installs a handler that returns a known name,
so `greet()` produces the same result for each test run.

Handlers do more than `except` blocks.
When an Effect runs, the handler receives a *continuation*:
the rest of the computation from that point forward.
An `except` block has two options, catch or propagate,
and both discard the continuation.
A handler can resume the continuation once,
and the Effect then behaves like a normal function return.
A handler can also discard the continuation,
and the Effect then behaves like an exception.
A handler can even invoke the continuation several times,
which is how native systems express retries and backtracking as ordinary handlers.

*Algebraic effects* is the name for this design:
Effects declared as an interface, plus handlers that receive the continuation.

[Flix](https://flix.dev/) expresses the same model with different notation.
The Effect row follows a backslash,
and a handler receives the continuation as a named parameter:

```flix
// flix/Greet.flix
use Sys.Console

// Effect declarations: the interface, not the implementation
eff Ask {
    def ask(prompt: String): String
}

eff Tell {
    def tell(message: String): Unit
}

// Core logic: the Effect row appears after the backslash
def greet(): Unit \ {Ask, Tell} =
    let name = Ask.ask("What is your name? ");
    Tell.tell("Hello, ${name}!")

// Main binds each Effect to an implementation
def main(): Unit \ Console =
    run {
        greet()
    } with handler Ask {
        def ask(prompt, resume) = {
            Console.print(prompt);
            let line = Console.readln();
            resume(Option.getWithDefault("", line))
        }
    } with handler Tell {
        def tell(message, resume) =
            resume(Console.println(message))
    }
```

The `eff` declares `ask` with one parameter, `prompt`.
The handler's `ask` has two, `prompt` and `resume`,
and `resume` is the continuation.
Koka's `with fun` handler resumes for you when its body returns.
Flix hands you the continuation,
and `resume(value)` returns `value` to the point in `greet()` that performed the Effect.
`Console.readln()` returns an `Option`, `None` at end of input,
so the `Ask` handler supplies an empty name in that case.
`main()` keeps `Console` in its signature,
the Effect its handler bodies perform,
the counterpart of Koka's `<console,exn>`.
Flix installs the `Console` handler when the program starts,
so `main()` installs handlers for `Ask` and `Tell` alone.

Languages in this family include Koka, Flix, Eff, Effekt, and Unison.
OCaml 5 has the handler mechanism,
though it does not yet track Effects in function types.

### Library Effect Management

Changing languages is rarely an option.
A team committed to Scala or TypeScript cannot use native Effects,
so designers build *library* Effect systems on top of existing type systems.
The compiler checks types, not Effects,
so the library encodes Effect information into the return type of every function,
and the compiler's ordinary type checking tracks it from there.
That encoding changes the mechanism.
Instead of writing a computation and letting the compiler infer its Effects,
you build a *description* of a computation, and execute the description later.
[ZIO](https://zio.dev/) is such a library, for Scala.
Here is the greeting program again.
In ZIO it is a description first and a run second:

```scala
// zio/Greet.scala
import zio.*
import zio.Console.{print, printLine, readLine}

// The Effects' interfaces
trait Ask:
  def ask(prompt: String): UIO[String]

trait Tell:
  def tell(message: String): UIO[Unit]

// Accessors: lift each method into a ZIO description
object Ask:
  def ask(prompt: String): ZIO[Ask, Nothing, String] =
    ZIO.serviceWithZIO[Ask](_.ask(prompt))

object Tell:
  def tell(message: String): ZIO[Tell, Nothing, Unit] =
    ZIO.serviceWithZIO[Tell](_.tell(message))

// Core logic: a value, not an action; nothing runs here
val greet: ZIO[Ask & Tell, Nothing, Unit] =
  for
    name <- Ask.ask("What is your name? ")
    _ <- Tell.tell(s"Hello, $name!")
  yield ()

// The implementations, packaged for delayed binding
val consoleAsk: ULayer[Ask] = ZLayer.succeed(new Ask:
  def ask(prompt: String): UIO[String] =
    (print(prompt) *> readLine).orDie)

val consoleTell: ULayer[Tell] = ZLayer.succeed(new Tell:
  def tell(message: String): UIO[Unit] =
    printLine(message).orDie)

// Entry point: bind the implementations, then execute
object Main extends ZIOAppDefault:
  def run = greet.provide(consoleAsk, consoleTell)
```

The three type parameters of `ZIO[Ask & Tell, Nothing, Unit]` carry the Effect information.
`Ask & Tell` is the environment the computation requires,
an intersection type that lists both Effects.
`Nothing` is the error type, meaning `greet` cannot fail.
Each console layer turns the `IOException` a read or write can raise into a defect with `orDie`,
so the signature's error type stays `Nothing`.
`Unit` is what it produces on success.
The signature does the same job as Koka's Effect row.
It tells you what `greet` needs, what can go wrong, and what comes back.

Everything else in the listing is machinery,
and each Effect carries its own copy: a trait for its interface,
a companion object to lift that interface into the `ZIO` type,
and a `ZLayer` to package its implementation,
plus one `provide()` call to bind them all.
Koka declares each Effect in two lines and handles it in one `with` clause.
Even `greet()` grows: it cannot call `ask` and then `tell`,
because each call produces a description, not a value,
so a `for` comprehension chains the two descriptions into one.
The machinery exists because the language cannot intercept an Effect at the point where it runs,
the way a native handler does.
A library works with values alone, so every Effect must become a value.
`greet` is a data structure describing a program.
Execution begins when the ZIO runtime interprets that structure at `run`,
the edge between description and action.

The TypeScript [Effect](https://effect.website/)
library also builds a description and runs it later:

```typescript
// ts/greet.ts
import { Context, Effect, Layer } from "effect"
import * as readline from "node:readline/promises"
import { stdin, stdout } from "node:process"

// The Effects' interfaces, as services
class Ask extends Context.Service<
  Ask,
  { ask: (prompt: string) => Effect.Effect<string> }
>()("Ask") {}

class Tell extends Context.Service<
  Tell,
  { tell: (message: string) => Effect.Effect<void> }
>()("Tell") {}

// Core logic: still just a description
const greet = Effect.gen(function* () {
  // Fetch each service object the layer supplies
  const ask = yield* Ask
  const tell = yield* Tell
  // Each call builds a description; yield* runs it
  const name = yield* ask.ask("What is your name? ")
  yield* tell.tell(`Hello, ${name}!`)
})

// The implementations, packaged for delayed binding
const ConsoleAsk = Layer.succeed(Ask, {
  ask: (prompt) =>
    Effect.promise(async () => {
      const rl = readline.createInterface({
        input: stdin,
        output: stdout,
      })
      const answer = await rl.question(prompt)
      rl.close()
      return answer
    }),
})

const ConsoleTell = Layer.succeed(Tell, {
  tell: (message) => Effect.sync(() => console.log(message)),
})

// The boundary: descriptions above, execution here
const Console = Layer.merge(ConsoleAsk, ConsoleTell)
Effect.runPromise(greet.pipe(Effect.provide(Console)))
```

Here `greet` reads as straight-line code because `Effect.gen` builds the description from a generator,
and each `yield*` hands a sub-description to the library and receives its result back.
Koka's `main()` reads a line with `readline()`.
The `ConsoleAsk` layer must open Node's `readline` interface, await its promise,
close the interface,
and wrap all of that in `Effect.promise` so the result is a description the library can track.

The machinery does not stop at your own code.
A library Effect system tracks Effects only in values of its own type,
so it cannot see an ordinary function that performs an Effect.
Scala's `println` prints, and its signature declares only a `Unit` result.
The library therefore supplies its own copy of every effectful standard-library call,
each returning a description that carries the Effect signature.
`print`, `printLine`,
and `readLine` in the ZIO listing are the wrapped versions of Scala's own console calls.
The TypeScript listing does its own wrapping:
`console.log` goes in `Effect.sync` and Node's `readline` in `Effect.promise`.
Console, file, clock, random, and network calls each get a wrapped version,
and you must wrap a third-party library to make it conform.
The library needs these copies because it tracks Effects without the compiler's help.
A native system's standard library declares its Effects in its own signatures,
written once, so no second copy exists.

The description/execution split is an artifact of building the system as a library,
rather than a feature of Effect Management.
Native systems deliver tracking, interface separation,
and delayed binding while the code runs eagerly,
with no description trees and no interpreter.
A library works with the language's ordinary calls,
which run as soon as you make them.
It can delay the binding of `ask` to an implementation only by delaying the call itself,
so it builds a description now and runs it later.

Deferring execution adds one question to every value you handle:
is it a description or an action?
Code that mixes the two compiles cleanly but misbehaves,
because the imperative part runs when the program builds the description,
not when the runtime executes it.

Libraries in this family include ZIO, Cats Effect, and Kyo in Scala,
Polysemy and Effectful in Haskell, Effect in TypeScript,
and Stateless in Python.
Stateless builds on generators, as TypeScript Effect's `function*` does.
A Python generator suspends a computation,
hands control to whoever is driving it, and resumes with a value.
That makes a suspended generator a continuation you can resume once or discard,
but not resume twice,
because a paused generator holds the one copy of its position and local variables.

### Custom AI Languages with Effects

At this writing, experimental languages designed for AI code generation are proliferating.
Their designers try to balance better code generation for the AI against human verifiability.
A language written for an AI can drop conveniences that help people write and read code.
An AI can start using that language as soon as it works,
while people take years to adopt a new language.

Most of these AI languages are tracking systems.
They provide the first part of a full EMS.
For their purpose the other two parts, interface separation and delayed binding,
are unnecessary.
When the AI generates the implementation,
it can guarantee what the generated code does.
Generated code that rebinds an implementation breaks that guarantee.

Two languages go further.
In [Pact](https://github.com/KikotVit/pact-lang),
a function declares a `needs` clause.
A separate `using` clause rebinds each implementation,
so tests can swap Effects deterministically.
[Lumen](https://alliecatowo.github.io/lumen/)
writes source as Markdown with algebraic effects.
Its `bind effect` rebinds a handler separately from its use.
Both separate an Effect's interface from its implementation and bind the implementation later,
the second and third properties of a full EMS.

## Effect Management for Python

The Python language has the start of an Effect Management System.
Python tracks one Effect in function signatures: `async`.
An `async def` builds a description instead of running its body:

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
a description of work.
The body has not started, so `ran` is still `[]`.
The body runs only when something drives the description: an `await`, a task,
or `asyncio.run()`.
That description/execution split is the library Effect system model.
Descriptions compose inside `async def` functions.
`asyncio.run()` is the edge where description becomes action.

Python enforces the tracking the way an EMS does.
`await` is a syntax error outside an `async def`,
so any function that awaits a coroutine must become `async`,
and so must its callers, all the way up to the edge.
If you replace "async" with "network access" or "database write" in that sentence,
you have described Effect tracking.
Python demonstrates that this tracking can work,
and hard-codes it to a single Effect, asynchrony,
rather than letting you declare your own.

Third-party libraries supply other parts of an EMS.
The [returns](https://github.com/dry-python/returns)
library provides four containers:

- `Result`, like the one in [Error Handling](42_Functional--Error_Handling.md)
- `Maybe`, for a value that might be absent
- `IO`, which marks a value as having come from input/output
- `RequiresContext`, for delayed binding of dependencies

The [effect](https://pypi.org/project/effect/)
library ports the description/execution split to Python.
Code builds objects that describe intents.
Separate performers execute them, and a test can swap in its own performers.
The [eff](https://github.com/orsinium-labs/eff) library models Effect handlers.
Each of these supplies part of an EMS.

One library supplies all three parts.
[Stateless](46_Effects--Stateless.md)
encodes each Effect's dependencies and failures into the return type of every function that performs that Effect.
A type checker verifies that each caller carries them forward.
Leaving a declared dependency unbound is a type error.
Calling an effectful function from one annotated as pure is a type error.
Stateless therefore supplies tracking, interface separation,
and delayed binding, the three properties of a full EMS,
inside Python's existing type system.

Stateless verifies that the Effects you declare propagate consistently.
A function can still call `print()`, next to its carefully declared Effects.
In Koka, that call changes the function's Effect row, and every caller's row.
In Python, neither Stateless nor the type checker reports it.
A library checks the Effects you wrote down.
A language with native Effects checks those and finds the ones you left out,
because its compiler reads every call in the body.

Could Python itself gain Effect tracking,
so that a tool infers every declaration instead of you writing it?
The annotation syntax could carry the Effect row.
Imagine a signature that declares every Effect, as `async def` declares `async`.
The hard part is propagation, not syntax.
A type checker must compute the Effect row of every function from the functions it calls,
across every library on PyPI, almost all of which carry no Effect annotations.
`async` succeeds because it is part of the language.
The interpreter enforces it,
and its keyword marks each function that carries the Effect.
An Effect row must cover every library in an ecosystem of untracked code.
Gradual typing faced the same problem, and took a decade.

No PEP proposes Effect tracking today.
[Effect Tracking](A_Effect_Tracking.md) works through one candidate design:
an Effect row carried in `typing.Annotated` metadata,
and an analysis of the tool that would propagate and check it.
The appendix calls that design *algebraic effect tracking*:
the row a native system keeps, without the handlers.
[An Effect Checker](B_An_Effect_Checker.md)
builds the part of that tool that needs no type inference.

## Effects Are the Next Barrier

The history of programming is a history of barriers that limit how large a program can grow.
Each time, the pattern is the same.
Something the programmer tracks by hand works in small programs.
Systems grow until hand-tracking fails.
The solution moves that tracking into the language or the toolchain,
and a generation later, nobody can imagine doing it by hand.

Namespaces are an example.
Early languages put every name in one global namespace,
and the programmer prevented collisions by choosing distinct names.
Collisions were often silent, producing hidden bugs,
and third-party libraries made the problem worse.
The solution divided names among separate namespaces.
In Python, every module is automatically a namespace.
The practice is so settled that the Zen of Python celebrates it:
<!-- vale House.EmDash = NO -->
"Namespaces are one honking great idea -- let's do more of those!"
<!-- vale House.EmDash = YES -->
Nobody audits their imports for name collisions anymore.
The language does the bookkeeping.

The same pattern repeats across the field.
Version control gives every state of the code a name to which you can return,
so experimenting is safe.
Automated testing moves "does it still work?" from a manual ritual into the build.
Garbage collection takes the tracking of memory ownership out of the programmer's head.
Each meets resistance as unnecessary overhead, then wins adoption,
then fades as a question.

A barrier is hardest to see from inside,
and Effects are the barrier we are inside right now.
We build programs from other people's code,
and we don't know what that code does.
It might change something in the world.
It might read from an unreliable source.
It might fail and take the system down.
You discover these behaviors by trusting documentation, reading source,
and observing failures.
Then you write compensating code.
This activity consumes an enormous part of professional programming,
and it has been normal for so long that it goes unnoticed.
Like every hand-tracked concern before it, this one prevents scaling.

An Effect Management System moves the bookkeeping into the type system.
The function signature answers the questions from [Effect Management Systems](#effect-management-systems):
what does this function need, what does it change, what can go wrong.
The compiler checks every composition,
comparing each callee's Effects with the caller's declaration at each call.

Languages that track Effects today are young.
Libraries that retrofit Effect tracking make you package each Effect's interface and implementation yourself,
and wrap every effectful call.
Effect tracking will look obvious in hindsight.
Future programmers will regard a function with hidden Effects the way you regard a program written in one global namespace.

Python's native Effect tracking stops at `async`,
and it will stay there for some time.
[Generators](45_Effects--Generators.md) shows the mechanism a library needs:
a generator suspends and resumes with a value.
[Stateless](46_Effects--Stateless.md) builds a library EMS on that mechanism,
and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
puts the library to work.

## Exercises

Try each exercise before opening its [solution](../Solutions/44_Effects--Effect_Management/).

1.  Write the production bindings for `ask_tell.py`:
    a `Console` class whose `ask()` calls `input()` and whose `tell()` calls `print()`.
    Then run `greet(Console(), Console())` interactively.
    Confirm `greet()` runs unchanged.
    Serving a new context without edits is what delayed binding provides.
2.  Do the bookkeeping the chapter describes.
    Starting from `bookkeeping_scales.py`, add a `Log` Effect
    (a protocol with `log(message)`) used by a new helper that `greet()` calls,
    and log from `greet()` too.
    The chapter counts five signatures for that version.
    Say how many of the five use the `Log` they declare,
    and then what an EMS would do instead.
3.  Classify every Effect in `slope_catch.py`,
    `withdraw()` from [Functional Foundations](40_Functional--Foundations.md#pure-functions),
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
