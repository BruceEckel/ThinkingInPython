# Effect Management

In numerous places throughout this book,
we have emphasized the benefits of pure functions:

- [Functional Programming](40_Functional_Programming.md#pure-functions)
  contrasts `double()`, a pure function, with `withdraw()`,
  which depends on state left over from earlier calls.
- [Performance](18_Performance.md#caching)
  turns naive recursive Fibonacci from 242,785 calls into 26 with `functools.cache`.
  Caching only works because the cached function is pure.
- [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance)
  turns shapes into immutable data,
  so one pure function replaces a method on each class.
- [Observer](30_Observer.md#a-visual-example-of-observers)
  has `recolored()` return a new grid instead of mutating the one it received,
  so a test checks the change with no GUI in sight.
- [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
  reduces competition between items to pure logic,
  a dictionary lookup with nothing to mock.
- [Composite and Interpreter](34_Composite_and_Interpreter.md#simplification-rewrites-the-tree)
  has `simplify()` return a new tree instead of editing the one it receives.

There's one important thing these all have in common:
you can verify function purity just by examining the code in that function.

What happens if your potentially-pure function calls other functions?
If one or more of those other functions have side effects,
their impurity causes the calling function to also be impure.
To discover whether a function is impure,
you must either trust the documentation or examine that function's code.

This rapidly becomes tedious and error-prone.
It would be great if the type checking system could perform purity verification for you.
This is called an *Effect Management System*,
and this chapter explores aspects of Effect Management.

## What is an Effect?

An *Effect* is what causes impurity.
We say that a function has *side effects* if calling does anything other than returning a result.
That is, if it modifies the environment outside the function.
For example, it might:

- Display something on the console
- Change a pixel on your screen
- Activate a motor
- Write to a database
- Make a network request
- Modify a non-local variable
- Acquire a lock, or coordinate with another thread

Side effects are relatively easy to spot because they change things in their environment.

But the meaning of "Effect" is broader than just side effects.
It also includes the impact of the environment on the function.
For example, suppose your function reads the time of day, or a random number.
This doesn't change anything in the environment.
However, the result of your function is almost certainly going to be different from one call to the next.
If you incorporate any information other than the function arguments,
your function becomes impure.
This usually involves I/O: the time of day, a random number,
a database or network read.
But it can also be as simple as reading a variable that's global to your function.
These are called *side causes* (corresponding to side effects)
or *implicit inputs*.

Thus, Effects are the union of side effects and side causes.
But there's another factor that doesn't quite fit either category.

## Are Exceptions Impure?

Consider the following:

```python
# divide_by_zero_impurity.py

def slope(rise: int, run: int) -> float:
    return rise / run
```

This always produces the same result for the same inputs,
*except when `run` is zero*.
Because an exception is raised instead of returning a result,
does that break purity?

Two schools of thought exist:

1.  **Pure**: Raising `ZeroDivisionError` instead of returning a number does not break purity.
    The same arguments still produce that same exception every time.
    The function reads nothing outside itself and changes nothing outside itself.
    Purity says the outcome depends on the arguments alone.

    Formal computer science theory backs this up.
    Pure languages like Haskell treat an unhandled runtime exception or crash as a *bottom* value, denoted ⊥.
    A bottom value represents a computation that does not terminate normally or result in a standard value.
    Because ⊥ is a valid theoretical value, throwing an uncatchable error is technically referentially transparent.
    You could replace the function call with the crash itself, and the program's behavior wouldn't change.

2.  **Functional**: Exceptions bypass normal control flow which makes code difficult to reason about.
    To make code easier to reason about,
    functional programming avoids exceptions altogether.
    A *Total Function* doesn't raise exceptions,
    but instead returns errors as data using explicit wrapper types,
    as we saw in [Functional Error Handling](41_Functional_Error_Handling.md).

From an Effect Management standpoint, exceptions are impure.
If you write a function `a()` that calls a function `b()` that raises an exception,
then `a()` also raises that exception unless it is caught within `a()`.
To know the Effects that your function has,
exceptions must be tracked as Effects on all functions.

## A Program can Never be Pure

A perfectly pure program computes something but never lets anyone see it.
It reads nothing from its environment and changes nothing in its environment,
so its result never reaches a screen, a file, a socket,
or even the exit code the operating system checks.
From outside the process,
that program is indistinguishable from a program that computes nothing.

```python
# pure_and_pointless.py
import timeit

def compute_and_discard() -> None:
    total = 0
    for i in range(2_000_000):
        total += i * i

def do_nothing() -> None:
    pass

busy = timeit.timeit(compute_and_discard, number=5)
idle = timeit.timeit(do_nothing, number=5)
print(f"burned real CPU time for nothing: {busy > idle * 100}")
#: burned real CPU time for nothing: True
```

Neither `compute_and_discard()` nor `do_nothing()` produces anything.
No prints, writes, or returns; nothing a caller can act on.
But `compute_and_discard()` still takes measurably longer to run,
because Python cannot tell that the work is worthless, and skip it.
A perfectly pure computation, followed to its logical end,
is a space heater with extra steps.

Effects are not a defect to design away.
They are the entire reason a program exists.
The goal of Effect Management is not to eliminate effects.
It is to isolate Effects so the rest of the program can stay pure
(this is sometimes called "pushing the Effects to the edges").

## A Taxonomy of Benefits

The initial and most obvious reason to track Effects is parallelism.
A function with no Effects touches nothing shared and effortlessly runs in parallel.
The same guarantee makes testing trivial.
A pure function needs no setup, no mocks, and no teardown.
Call it with arguments and check the result.

Isolating Effects produces a cascade of value beyond that first split.
Consider the depth of Effect analysis as a series of phases.
The first phase separates pure from impure.
That phase produces parallelism, caching, and easy testing for the pure part.

### Subdividing the Impure Portion

The next phase subdivides the impure portion,
and each subdivision produces its own benefit:

- **Exceptions** become data,
  via [Functional Error Handling](41_Functional_Error_Handling.md).
  Failures turn into values the type checker can see,
  and a test checks for a `Failure` as easily as a `Success`.
- **Side causes** become replaceable inputs.
  A test substitutes a fixed clock for the real one,
  or a seeded generator for true randomness,
  and the function under test becomes repeatable.
- **Side effects** become replaceable outputs.
  A test swaps the real database or console for a stand-in that records what was written,
  then inspects the recording.

Notice that in almost every case, testing is a benefit of Effect Management.
That is not a coincidence.
A test must run in an environment it completely controls.
Untracked Effects are the parts of the environment a test cannot control.
Every Effect you isolate becomes controllable by your tests.

You only get these benefits if you know where the Effects are.
In a small program you find them by inspection.
As programs grow, inspection stops scaling.
That failure motivates the machinery in the rest of this chapter.

## Converting Effectful to Pure

Let's revisit `slope()` from `divide_by_zero_impurity.py`.
We can transform the exception Effect, which makes the function pure again.
Here are three ways to do it.

### Return a Result Type

Wrap the answer and the failure in a `Result`,
the way [Functional Error Handling](41_Functional_Error_Handling.md#turning-exceptions-into-results)
does.
`result.py` and `safe.py` are shared helpers,
so this chapter imports them directly instead of rebuilding them.
Decorate the original `slope()`, unchanged,
and every exception it raises becomes a value instead of a crash:

```python
# slope_result.py
from result import Failure, Success
from safe import safe

@safe
def slope(rise: int, run: int) -> float:
    return rise / run

for args in [(10, 2), (10, 0)]:
    match slope(*args):
        case Success(answer):
            print(f"slope{args} = {answer}")
        case Failure(error):
            print(f"slope{args}: {type(error).__name__}")
#: slope(10, 2) = 5.0
#: slope(10, 0): ZeroDivisionError
```

`@safe` catches whatever it raises,
so the fix lives entirely outside the function being fixed.
`slope()` is total again, and `match` forces the caller to handle both outcomes.
Nothing escapes through a raised exception.

### Catch the Exception You Expect

If you catch and handle the exception within the function,
it never escapes to become an Effect.
`slope()` can catch the one exception it knows about and fold the failure into an ordinary value of its existing return type,
`float`, instead of introducing a new type:

```python
# slope_catch.py

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
try:
    slope(10, -1)
except ValueError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: ValueError: run cannot be negative: -1
```

This works, and it needs no new type.
But it only guards the exception that `slope()` was written to expect.
`validate()` raises `ValueError` for a negative `run`,
an exception `slope()` never anticipated.
By calling it, `validate()`'s Effect becomes `slope()`'s Effect.
Catching by hand is only as complete as your knowledge of every exception every callee can raise,
which is the tracking problem an Effect Management System exists to solve.

Note that languages like C++ and Java attempted to track exceptions using *exception specifications*,
but did not make those first-class in the function type.
They leaked information and are generally considered a failure
(C++ changed their specifications to a binary indication of whether or not any exceptions are thrown).

### Make the Bad Value Impossible

The third approach removes the failure instead of handling it.
[Data Classes as Types](12_Data_Classes_as_Types.md#a-value-that-must-be-checked-everywhere)
makes illegal values impossible to construct.
Give `run` a type that cannot hold zero,
and `slope()` never needs to check for zero:

```python
# slope_nonzero.py
from dataclasses import dataclass

@dataclass(frozen=True)
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value

print(slope(10, NonZero(2)))
#: 5.0
try:
    NonZero(0)
except ValueError as e:
    print(e)
#: NonZero cannot hold 0
```

The check still happens, but only once, when a `NonZero` comes into existence.
Every function that receives a `NonZero`, including `slope()`,
inherits that guarantee.
`slope()` was never in danger of dividing by zero,
so it needed no `try` and no `Result` to say so.

All three approaches produce a pure `slope()`,
but they push the cost to different places.
A `Result` makes every caller handle failure explicitly, at every call site.
Catching by hand hides the fix inside `slope()`,
at the cost of a blind spot for an exception nobody thought to catch.
A restrictive type pays once, at construction,
and every function downstream is pure by inheritance rather than by discipline.

## Effect Management Systems

Suppose a test starts failing intermittently.
The test calls a function you wrote last week.
By its name and parameters,
that function calculates a total price for a list of items.
The logic looks right.
The math checks out.
But sometimes the test is slow.
Sometimes, run alongside another test, one of the two fails.
Three calls deep, inside a helper that formats currency, you find the problem:
a read from a configuration service, a write to an audit log,
and a network call that fetches the current exchange rate.
None of this appears in the function's signature.
To discover what the function actually does, you had to read every line of it,
and every line of everything it calls.

Most functions in most programs have this hidden life,
and the hidden life makes code hard to understand:

- Can you call this function in a test without mocking half the world?
- If you call it twice with the same arguments, do you get the same result?
- Does it behave differently in a different environment?
- Does it fail silently, loudly, or not at all?

You cannot answer these questions by reading the function's signature.
You must read the implementation,
then trust that you found everything it depends on, everything it changes,
and everything that might go wrong.
In a small codebase you can hold that knowledge in your head.
In a large one you cannot.
A function you understand today gets called by a function written next week,
which gets called by code a colleague writes next month.
Each step adds invisible dependencies, and no one has the full picture.

An Effect Management System (EMS) keeps track of Effects in functions.
If your function calls an effectful function,
the EMS guarantees that your function also reports its Effects.
Then if another function calls your function,
the EMS ensures that the new function also reports whatever Effects it produces.
An EMS allows you to look at the function signature and know for sure whether it is pure or not.
If it is not, the EMS will give details about the kinds of impurities that function involves.

A full EMS does three things:

1. **Tracks Effects.**
   The type system knows which Effects a function may perform.
2. **Separates each Effect's interface from its implementation.**
   A function declares *what* Effects it uses, not *how* they are fulfilled.
3. **Binds the implementation later.**
   Some caller or context supplies the implementation,
   at a point after the function is defined.

The third item is called *delayed binding*, and it has leverage.
Delayed binding exists so that one fixed codebase can serve many contexts
(test, production, retry-wrapped) without being edited.
When a hundred functions declare "I need something that can read from storage,"
none of them contains an opinion about what that storage is.
They all flow up to a single point or edge,
where storage is bound to an implementation.
Changing that one binding changes the behavior of all hundred functions at once.
A test provides an in-memory binding, production provides the real database,
and none of the hundred functions change.
Cross-cutting behavior gets the same treatment.
To add caching, tracing, or retries to every storage access,
you insert a layer at the binding point instead of touching every call site.
The complexity of variation concentrates at the boundary of the program,
while the interior stays simple and uniform.

### Effects by Hand

You have already seen Effect Management by hand.
Every technique in [Converting Effectful to Pure](#converting-effectful-to-pure)
manually manages one Effect, the exception.
A `Result` tracks failure in the return type.
A `try` binds the failure to a handler.
A restrictive type removes the failure at construction.
Each is a hand-built version of something an EMS automates.

Side effects and side causes also have a by-hand technique:
pass the implementation in as a parameter.
Instead of calling `input()` and `print()` directly,
`greet()` declares what it needs:

```python
# ask_tell.py
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

class Capture:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def tell(self, message: str) -> None:
        self.messages.append(message)

captured = Capture()
greet(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
```

`greet()` performs an `Ask` Effect and a `Tell` Effect,
and its signature says so.
This moves the Effects into explicit arguments.
The bindings are delayed.
The demo binds them to test stand-ins, `Scripted` and `Capture`,
and checks the greeting with no console in sight.
A production caller passes objects that read with `input()` and write with `print()`,
and `greet()` never changes.
This is delayed binding by hand,
and it is why "pass in your dependencies" is such durable advice.

The technique works, but the bookkeeping falls entirely on you.
Every function that calls `greet()` must accept an `Ask` and a `Tell` so it can pass them down,
so parameters accumulate at every level of the call stack.
Nothing propagates automatically.
Add a `Log` Effect three levels down, and you edit every signature on the path.
Dependency injection frameworks relocate this bookkeeping into a wiring layer,
but the injector still must be told what every function needs,
and told again when that changes.
Nothing verifies the wiring except a runtime failure.
An EMS moves the bookkeeping into the type system, where it maintains itself.
What that takes is a second channel in the signature,
one that carries Effect information without occupying the argument list.

### Native Effect Management

Ideally, Effect tracking is built into the language.
We'll call this a *native* Effect system.
In a native system, Effects live in the type system alongside ordinary types.
A function's signature carries two pieces of information: what it returns,
and what Effects it performs.
The body looks like ordinary sequential code.
The compiler observes what you call and tracks the Effects,
the same way it tracks whether a value is an integer or a string.

The examples in this section and the next come from my research,
which builds the same small programs in four Effect-managing languages.

Here is the greeting program in [Koka](https://koka-lang.github.io/),
a research language with native Effects:

```koka
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
fun main() : console ()
  with fun ask(prompt)
    print(prompt)
    readline()
  with fun tell(message)
    println(message)
  greet()
```

The angle brackets in `greet()`'s signature hold the *Effect row*,
the set of Effects the function performs.
This is the second channel.
`ask` and `tell` are part of the type without encumbering the argument list.
The compiler infers the row from what the body calls,
so you rarely write one by hand.
You annotate explicitly when you want a constraint,
such as declaring that a function must remain Effect-free.
If another function calls `greet()`,
the compiler adds `ask` and `tell` to that function's row automatically.
This is the propagation that the by-hand version made you perform with parameters.

Every Effect must eventually be fulfilled,
and the construct that fulfills one is a *handler*.
Think of a handler as a generalized `except` block.
An `except` block intercepts exceptions and decides what happens next.
A handler intercepts any Effect operation and decides what it means.
In `main()`, the `with fun ask(prompt)` handler decides that `ask` means "prompt the console and read a line."
A test installs a different handler, one that returns a fixed name,
and `greet()` runs unchanged.
The compiler rejects a program that performs an Effect with no handler in scope,
so no Effect reaches the runtime unaccounted for.

Handlers can do more than `except` blocks can.
When an operation is performed, the handler receives the *continuation*:
the rest of the computation from that point forward.
An `except` block can only catch or propagate,
and either way the continuation is discarded.
A handler can resume the continuation once,
which behaves like a normal function return.
It can discard the continuation, which behaves like an exception.
It can even invoke the continuation several times,
which is how native systems express retries and backtracking as ordinary handlers.

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
If your team is committed to Scala or TypeScript,
native Effects are unavailable,
so designers built *library* Effect systems on top of existing type systems.
In this approach the compiler doesn't track Effects.
Instead, the library encodes Effect information into the return type of every function.
That encoding forces a shift in mechanism.
Instead of writing a computation and letting the compiler observe its Effects,
you build a *description* of a computation, and execute the description later.

Here is "Hello, World!" in Scala using the [ZIO](https://zio.dev/) library:

```scala
import zio._
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
`Nothing` is the error type, meaning this one cannot fail.
`Unit` is what it produces on success.
The signature does the same job as Koka's Effect row.
It tells you what `hello` needs, what can go wrong, and what comes back.

Everything else in the listing is machinery, and there is a lot of it.
A trait for the interface.
A companion object to lift that interface into the `ZIO` type.
A `ZLayer` to package the implementation.
A `provide()` call to bind it.
All of that, to print one string.
The machinery exists because the language cannot intercept an Effect at the point where it is performed,
the way a native handler can.
The library's only power is over values, so every Effect must become a value.
`hello` is not a running program.
It is a data structure describing a program,
and nothing executes until the ZIO runtime interprets that structure at `run`,
the boundary between description and action (sometimes called "the edge").

The TypeScript [Effect](https://effect.website/) library works the same way:

```typescript
import { Context, Effect, Layer } from "effect"

// The Effect's interface, as a service tag
class Tell extends Context.Tag("Tell")<
  Tell,
  { tell: (message: string) => Effect.Effect<void> }
>() {}

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

The description/execution split is not a feature of Effect Management.
It is an artifact of building the system as a library.
Native systems deliver tracking, interface separation,
and delayed binding while the code runs eagerly,
with no description trees and no interpreter.
A library has no other mechanism.
Deferring execution is the price it pays for delayed binding in a language that was not designed for Effects.
That price is a conceptual layer you carry everywhere.
You must always know whether a value is a description or an action.
Code that mixes the two compiles cleanly but misbehaves,
because the imperative part runs while the description is being built,
not when the description is executed.

Libraries in this family include ZIO, Cats Effect, and Kyo in Scala,
polysemy and effectful in Haskell, and Effect in TypeScript.

### Custom AI Languages with Effects

At this writing the world is in the midst of an explosion of experimental languages designed for AI code generation.
Designs attempt to find the right balance between improving code generation for the AI while maintaining human verifiability.
One benefit these new languages have:
there's no human-constrained adoption curve.
AI Effect Languages don't need the extra affordances that benefit humans.
If a language works, an AI can start using it right away.

Most of these only **track** Effects,
because the AI can generate whatever code it needs to solve specialized problems:

- [Vera](https://veralang.dev):
  mandatory contracts checked with Z3 SMT verification.
- [Aria](https://www.aria-lang.com): built for AI code generation,
  not human readability.
- [Aver](https://averlang.dev): effects visible in the type system,
  with a verify block beside each function.
- [Mog](https://moglang.org): small enough to fit in a model's context window;
  effects gated by capabilities.
- [Lumen](https://alliecatowo.github.io/lumen/):
  markdown-native source with algebraic effects;
  `bind effect` rebinds a handler separately from its use, a full-EMS feature.
- [Dream](https://dreamlang.dev):
  pairs formal verification with AI-native code generation.
- [AILANG](https://ailang.sunholo.com): capability-based effects
  (`IO`, `FS`, `Net`, `Clock`, `AI`) granted per run.
- [Pact](https://github.com/KikotVit/pact-lang):
  functions declare a `needs` clause,
  and a separate `using` clause rebinds each implementation,
  so tests can swap effects deterministically, another full-EMS feature.
- [Zero](https://zerolang.ai): capability-based effects,
  with structured JSON diagnostics instead of prose error messages.
- [Boruna](https://github.com/escapeboy/boruna):
  effects declared and policy-gated at the VM level, with tamper-evident replay.

By the definition above,
most of these are Effect-tracking systems rather than full EMSs.
For their purpose the other two parts would be liabilities,
since a host that fixes the implementations can guarantee what generated code is able to do.
Pact and Lumen are exceptions.
Each separates an effect's interface from its implementation and binds the implementation later,
the second and third properties of a full EMS.

## Effect Management for Python?

Python has no Effect Management System, but it does not start from zero.
Python already tracks one Effect in function signatures,
and enforces that tracking virally: `async`.

```python
# coroutines_are_descriptions.py
import asyncio

async def greet() -> str:
    return "Hello"

description = greet()  # Nothing runs
print(type(description).__name__)
#: coroutine
print(asyncio.run(description))
#: Hello
```

Calling `greet()` runs nothing.
It builds a coroutine object, a description of work.
The description executes only when something awaits it or hands it to `asyncio.run()`.
That is the library Effect system model.
Descriptions compose inside `async def` functions,
and `asyncio.run()` is the boundary where description becomes action.
The tracking is enforced the way an EMS would enforce it.
`await` is a syntax error outside an `async def`,
so any function that awaits a coroutine must become `async`,
and so must its callers, all the way up to the edge.
Replace "async" with "network access" or "database write" in that sentence and you have described Effect tracking.
Python demonstrates that the machinery can work.
It just hard-codes the machinery to a single Effect, concurrency,
rather than letting you declare your own.

Third-party libraries supply pieces of the rest.
The [returns](https://github.com/dry-python/returns)
library provides `Result` and `Maybe` containers like those in [Functional Error Handling](41_Functional_Error_Handling.md),
plus an `IO` container that marks a value as having come from input/output,
and a `RequiresContext` container for delayed binding of dependencies.
The [effect](https://pypi.org/project/effect/)
library ports the description/execution split to Python.
Code builds objects describing intents, and separate performers execute them,
swappable for tests.
The [eff](https://github.com/orsinium-labs/eff)
library models Effect handlers directly.
Each of these gives you the discipline of one part of an EMS.
None of them gives you the guarantee,
because the type checker does not participate.
Nothing stops a function from calling `print()` directly,
right next to its carefully declared `IO` container.
In Koka, that call would change the function's Effect row,
and every caller's row.
In Python, it changes nothing that any tool can see.

Could Effect tracking be added to Python's type system?
Nothing in the annotation syntax prevents it.
You can imagine a signature that declares its Effects the way `async def` already declares one.
The hard part is not syntax but propagation.
A type checker would need to compute the Effect row of every function from the functions it calls,
across every library on PyPI, almost all of which would be unannotated.
`async` succeeded because it arrived with the language and split the world visibly.
An Effect row would need to spread through an ecosystem of untracked code.
Gradual typing faced the same problem, and took a decade.
No PEP proposes Effect tracking today.
If one arrives, the ideas in this chapter are what it will contain.

## Effects are the Next Barrier

The history of programming is a history of scaling barriers.
Each time, the pattern is the same.
Something the programmer tracks by hand works fine in small programs.
Systems grow until hand-tracking fails.
The solution moves that tracking into the language or the toolchain,
and a generation later, nobody can imagine doing it by hand.

Namespaces are the clearest example.
Early languages put every name in one global pool,
and the programmer was responsible for preventing collisions.
Collisions often happened quietly, producing hidden bugs,
and third-party libraries made the problem worse.
The solution gave every name a home.
In Python, every module is automatically a namespace,
and the practice is so settled that the Zen of Python ends by celebrating it:
<!-- vale House.EmDash = NO -->
"Namespaces are one honking great idea -- let's do more of those!"
<!-- vale House.EmDash = YES -->
Nobody audits their imports for name collisions anymore.
The language does the bookkeeping.

The same pattern repeats across the field.
Version control made program elements unique across time,
so experimentation stopped being risky.
Automated testing moved "does it still work?" from a manual ritual into the build.
Garbage collection took the tracking of memory ownership out of the programmer's head.
Each of these was resisted as unnecessary overhead, then adopted,
then forgotten as a question.

Effects are the barrier we are inside right now, which is why it is hard to see.
We build programs from other people's code,
and we don't know what that code does.
It might change something in the world.
It might read from an unreliable source.
It might fail and take the system down.
We discover these behaviors by trusting documentation, reading source,
and observing failures.
Then we write compensating code.
An enormous share of professional programming is this activity,
and we have accepted it as normal for so long that we no longer notice ourselves doing it.
Like every hand-tracked concern before it, it does not scale.

An Effect Management System moves the bookkeeping into the type system.
The function signature answers the questions from the beginning of this chapter:
what does this function depend on, what does it change, what can go wrong.
Composition stops being a guess,
because the compiler balances the books at every boundary.
The languages that do this today are young,
and the libraries that retrofit it are demanding.
That was true of every solution to every previous barrier at this stage.
Namespaces once looked like ceremony.
Effect tracking will look obvious in hindsight,
and future programmers will regard a function with hidden Effects the way we regard a program written in one global namespace.
