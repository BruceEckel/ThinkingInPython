# Effect Management

A test you wrote last week starts failing about one run in five.
The function it calls computes a total price, the math is right,
and three calls down, inside a helper that formats currency,
there is a read from a configuration service and a write to an audit log.
None of that is in any signature on the path.

This book has emphasized the benefits of pure functions in numerous places:

- [Foundations](40_Functional_Foundations.md#pure-functions)
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

In every one of those cases you can settle the question by reading one function.
That stops working as soon as the function calls others.
If one or more of those other functions have side effects,
their impurity makes the calling function impure too.
To discover whether a function is impure,
you must either trust the documentation or examine that function's code.

This rapidly becomes tedious and error-prone.
It would be great if the type checking system could verify purity for you.
A system that does this is called an *Effect Management System*.

## What Is an Effect?

An *Effect* causes impurity.
A function has *side effects* if calling it does anything other than return a result.
That is, if it modifies the environment outside the function.
For example, it might:

- Display something on the console
- Change a pixel on your screen
- Activate a motor
- Write to a database
- Make a network request
- Modify a non-local variable
- Acquire a lock, or coordinate with another thread

Side effects are relatively easy to spot in the function that performs them,
because they change something outside it.

But the meaning of "Effect" is broader than just side effects.
It also includes the impact of the environment on the function.
For example, suppose your function reads the time of day, or a random number.
This doesn't change anything in the environment.
However, the result of your function will almost certainly differ from one call to the next.
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
except when `run` is zero.
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
    Because ⊥ is a valid theoretical value, raising an error that nothing catches
    is technically referentially transparent.
    You could replace the function call with the crash itself, and the program's behavior wouldn't change.

2.  **Functional**: Exceptions bypass normal control flow,
    which makes code difficult to reason about.
    To make code easier to reason about,
    functional programming avoids exceptions altogether.
    A *Total Function* doesn't raise exceptions,
    but instead returns errors as data using explicit wrapper types,
    as you saw in [Error Handling](42_Functional_Error_Handling.md).

From an Effect Management standpoint, exceptions are impure.
If you write a function `a()` that calls a function `b()` that raises an exception,
then `a()` also raises that exception unless it is caught within `a()`.
To know the Effects that your function has,
exceptions must be tracked as Effects on all functions.
Effects therefore come in three kinds: side effects, side causes,
and exceptions.

## Converting Effectful to Pure

Transforming the exception Effect in `slope()` from `divide_by_zero_impurity.py` makes the function pure again.
Here are three ways to do it.

### Return a Result Type

Wrap the answer and the failure in a `Result`,
the way [Error Handling](42_Functional_Error_Handling.md#turning-exceptions-into-results)
does.
`result.py` and `safe.py` are shared helpers,
so this chapter imports them directly instead of rebuilding them.
If you decorate the original `slope()`, unchanged,
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

`@safe` catches whatever `slope()` raises,
so the fix lives outside the function being fixed.
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
Because `slope()` calls it, `validate()`'s Effect becomes `slope()`'s Effect.
Catching by hand is only as complete as your knowledge of every exception that a callee can raise,
which is the tracking problem an Effect Management System exists to solve.

Note that languages like C++ and Java attempted to track exceptions using *exception specifications*,
but did not make those first-class in the function type.
Nothing computed a specification from the functions a body called,
so an exception introduced three levels down had to be written by hand into every signature above it.
The usual escape was to widen the specification until it said nothing.
They leaked information and are generally considered a failure
(C++ changed its specifications to a binary indication of whether or not any exceptions are thrown).

### Make the Bad Value Impossible

The third approach removes the failure instead of handling it.
[Data Classes as Types](12_Data_Classes_as_Types.md#a-value-that-must-be-checked-everywhere)
makes illegal values impossible to construct.
If you give `run` a type that cannot hold zero,
`slope()` never needs to check for zero:

```python
# slope_nonzero.py
from dataclasses import dataclass
from exceptions import ignore

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
with ignore(ValueError):
    NonZero(0)
#: ValueError('NonZero cannot hold 0')
```

The check still runs, but only once, when a `NonZero` comes into existence.
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
None of the three makes the failure disappear.
A `Result` turns it into a value, a `try` consumes it,
and `NonZero` moves it to the one line that builds the value.
What changes is how many functions have to know about it.

## A Program Can Never Be Pure

A perfectly pure program computes something but never lets anyone see it.
It reads nothing from its environment and changes nothing in its environment,
so its result never reaches a screen, a file, a socket,
or even the exit code the operating system checks.
From outside the process,
that program is indistinguishable from a program that computes nothing.

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

busy = timeit.timeit(compute_and_discard, number=5)
idle = timeit.timeit(do_nothing, number=5)
report(busy_loop=busy, empty_function=idle)
print(f"burned real CPU time for nothing: {busy > idle * 100}")
#: burned real CPU time for nothing: True
```

Neither `compute_and_discard()` nor `do_nothing()` prints, writes,
or returns anything a caller can act on.
But `compute_and_discard()` still takes measurably longer to run,
because Python cannot recognize the work as worthless and skip it.
A perfectly pure computation, followed to its logical end,
is a space heater with extra steps.

Effects are not a defect to design away.
They are the reason a program exists.
The goal of Effect Management is not to eliminate Effects but to isolate them so the rest of the program can stay pure
(this is sometimes called "pushing the Effects to the edges").

So why track them at all?
The initial and most obvious reason is parallelism.
A function with no Effects touches nothing shared and runs in parallel.
The same guarantee makes testing trivial.
A pure function needs no setup, no mocks, and no teardown.
Call it with arguments and check the result.

## Two Phases of Effect Analysis

Think of Effect analysis as a series of phases.
The first phase separates pure from impure, and produces parallelism, caching,
and easy testing for the pure part.

### Subdividing the Impure Portion

The next phase produces one benefit per subdivision:

- **Exceptions** become data,
  the move [Converting Effectful to Pure](#converting-effectful-to-pure)
  just made three ways.
  Failures turn into values the type checker can see,
  and a test checks for an `Err` as easily as an `Ok`.
- **Side causes** become replaceable inputs.
  A test substitutes a fixed clock for the real one,
  or a seeded generator for true randomness,
  and the function under test becomes repeatable.
- **Side effects** become replaceable outputs.
  A test swaps the real database or console for a stand-in that records what was written,
  then inspects the recording.

In almost every case, testing is a benefit of Effect Management.
That is not a coincidence.
A test must run in an environment it completely controls.
Untracked Effects are the parts of the environment a test cannot control.
Every Effect you isolate becomes controllable by your tests.

You only get these benefits if you know where the Effects are.
In a small program you find them by inspection.
As programs grow, inspection stops scaling.
That failure motivates the machinery in the rest of this chapter.

## Effect Management Systems

Suppose a test starts failing intermittently.
The test calls a function you wrote last week.
Its name and parameters say it calculates a total price for a list of items.
The logic looks correct.
The math checks out.
But sometimes the test is slow.
Sometimes, run alongside another test, one of the two fails.
Three calls deep, inside a helper that formats currency, you find the problem:
a read from a configuration service, a write to an audit log,
and a network call that fetches the current exchange rate.
None of this appears in the function's signature.
To discover what the function does, you had to read every line of it,
and every line of everything it calls.

Most functions in most programs have this hidden life,
and it makes code hard to understand:

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

What is missing is tracking.
Without it you don't know what a function does.
You don't know whether it is safe to run in parallel with another,
or what happens when you call it twice in a row.
You don't know enough to compose functions, which is how programs grow large.

An Effect Management System (EMS) keeps track of Effects in functions.
If your function calls an effectful function,
the EMS adds that Effect to your function's type.
If another function then calls yours,
the EMS carries the Effect into that function's type as well,
and so on out to the edge of the program.
An EMS allows you to look at the function signature and know whether it is pure.
If it is not, the signature names the kinds of impurity involved.

A full EMS does three things:

1. **Tracks Effects.**
   The type system knows which Effects a function may perform.
2. **Separates each Effect's interface from its implementation.**
   A function declares which Effects it uses, not how they are fulfilled.
3. **Binds the implementation later.**
   Some caller or context supplies the implementation,
   at a point after the function is defined.

The third item is called *delayed binding*.
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

The signature says what `greet()` needs, not everything `greet()` might do:
a `print()` in the body would still be invisible.
[Effect Management for Python?](#effect-management-for-python)
returns to that limit.

The technique works, but the bookkeeping falls on you.
Every function that calls `greet()` must accept an `Ask` and a `Tell` so it can pass them down,
so parameters accumulate at every level of the call stack.
Nothing propagates automatically.
If you add a `Log` Effect three levels down,
you edit every signature on the path.
Dependency injection frameworks relocate this bookkeeping into a wiring layer,
but the injector still must be told what every function needs,
and told again when that changes.
Nothing verifies the wiring except a runtime failure.

Python does have a mechanism that propagates on its own.
A `ContextVar` ([Concurrency](19_Concurrency.md#context-that-follows-the-call-chain))
holds a value for the current task,
and anything below reads it without being handed it,
which is the automatic propagation the parameter list lacks.
It removes the parameter along with the one benefit the parameter provided.
`greet(ask, tell)` states its Effects in its signature,
and a `greet()` that reads two `ContextVar`s states nothing.
Setting the wrong one, or forgetting to set one at all,
surfaces as a failure at the moment of the read,
in whatever frame happened to need it.
The bookkeeping did not disappear.
It stopped being something a checker can see.
An EMS moves the bookkeeping into the type system, where it maintains itself.
What that takes is a second channel in the signature,
one that carries Effect information without occupying the argument list.

### Native Effect Management

Ideally, Effect tracking is built into the language.
This is a *native* Effect system.
In a native system, Effects live in the type system alongside ordinary types.
A function's signature carries two pieces of information: what it returns,
and what Effects it performs.
The body looks like ordinary sequential code.
The compiler observes what you call and tracks the Effects,
the same way it tracks whether a value is an integer or a string.

The examples in this section and the next come from my research,
in which I build the same small programs in four Effect-managing languages.

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

This decoupling is the core of every Effect system.
The code that requests an Effect is separated from the code that performs it,
and a handler sits between them.
`greet()` names `ask` and `tell` without deciding what either one means.
The handler decides, and a different handler decides differently.

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

A Python generator suspends a computation,
hands control to whoever is driving it, and resumes it with a value.
[Generators](45_Generators.md) covers the full two-way form,
and it is the mechanism the Python Effect library in [Stateless](46_Stateless.md)
is built from.

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
`Nothing` is the error type, meaning this one cannot fail.
`Unit` is what it produces on success.
The signature does the same job as Koka's Effect row.
It tells you what `hello` needs, what can go wrong, and what comes back.

Everything else in the listing is machinery: a trait for the interface,
a companion object to lift that interface into the `ZIO` type,
a `ZLayer` to package the implementation, and a `provide()` call to bind it.
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
polysemy and effectful in Haskell, Effect in TypeScript,
and Stateless in Python.
Stateless is built on generators, so [Generators](45_Generators.md)
covers that mechanism first.
[Stateless](46_Stateless.md)
then writes these programs again in the language this book is about,
and [Stateless in Practice](47_Stateless_in_Practice.md#abilities-are-not-special)
rebuilds the `ask`/`tell` pair from [Effects by Hand](#effects-by-hand).

### Custom AI Languages with Effects

At this writing there is an explosion of experimental languages designed for AI code generation.
Their designs try to balance better code generation for the AI against human verifiability.
Adoption is not gated by how long humans take to learn them.
A language written for an AI doesn't need the conveniences that help a person read code,
and if it works, an AI can start using it immediately.

Most of these only **track** Effects rather than providing a full EMS,
and for their purpose the other two parts are liabilities:
a host that pins the implementations can guarantee what generated code is able to do.

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

Pact and Lumen are the exceptions.
Each separates an effect's interface from its implementation and binds the implementation later,
the second and third properties of a full EMS.

## Effect Management for Python?

Python has no Effect Management System in the language,
but it does not start from zero.
Python already tracks one Effect in function signatures,
and enforces that tracking virally: `async`.

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

Calling `greet()` runs nothing.
It builds a coroutine object, a description of work,
and the empty list is the evidence: the body never executed.
The description executes only when something awaits it or hands it to `asyncio.run()`.
This is the same demonstration [Concurrency](19_Concurrency.md#asyncio-mechanics)
opened with.
That is the library Effect system model.
Descriptions compose inside `async def` functions,
and `asyncio.run()` is the boundary where description becomes action.
The tracking is enforced the way an EMS enforces it.
`await` is a syntax error outside an `async def`,
so any function that awaits a coroutine must become `async`,
and so must its callers, all the way up to the edge.
If you replace "async" with "network access" or "database write" in that sentence,
you have described Effect tracking.
Python demonstrates that the machinery can work.
It just hard-codes the machinery to a single Effect, concurrency,
rather than letting you declare your own.

Third-party libraries supply pieces of the rest.
The [returns](https://github.com/dry-python/returns)
library provides `Result` and `Maybe` containers like those in [Error Handling](42_Functional_Error_Handling.md),
plus an `IO` container that marks a value as having come from input/output,
and a `RequiresContext` container for delayed binding of dependencies.
The [effect](https://pypi.org/project/effect/) library,
no relation to the TypeScript library of the same name,
ports the description/execution split to Python.
Code builds objects describing intents, and separate performers execute them,
swappable for tests.
The [eff](https://github.com/orsinium-labs/eff)
library models Effect handlers directly.
Each of these gives you the discipline of one part of an EMS,
but not the guarantee, because the type checker does not participate.

One library goes the rest of the way.
[Stateless](46_Stateless.md)
encodes an Effect's dependencies and failures into the return type of every function that performs them,
and a type checker verifies that each caller carries them forward.
Declaring a dependency you never bind is a type error.
Calling an effectful function from one annotated as pure is a type error.
That is tracking, interface separation, and delayed binding,
the three properties of a full EMS, inside Python's existing type system.
That chapter builds it up one step at a time.

The guarantee has a boundary.
Stateless verifies that the Effects you *declare* propagate consistently.
Nothing stops a function from calling `print()` directly,
adjacent to its carefully declared Effects.
In Koka, that call changes the function's Effect row, and every caller's row.
In Python, it changes nothing that any tool can see.
A library checks the Effects you wrote down.
Only the language can check the ones you didn't.

Could Effect tracking be added to Python itself,
so that declaring Effects stops being manual?
Nothing in the annotation syntax prevents it.
You can imagine a signature that declares its Effects the way `async def` already declares one.
The hard part is not syntax but propagation.
A type checker needs to compute the Effect row of every function from the functions it calls,
across every library on PyPI, almost all of which are unannotated.
`async` succeeded because it arrived with the language and split the world visibly.
An Effect row needs to spread through an ecosystem of untracked code.
Gradual typing faced the same problem, and took a decade.
No PEP proposes Effect tracking today.
If one arrives, it will contain the ideas in this chapter.

## Effects Are the Next Barrier

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
Version control gave every state of the code a name you can return to,
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
You discover these behaviors by trusting documentation, reading source,
and observing failures.
Then you write compensating code.
An enormous share of professional programming is this activity,
and it has been normal for so long that it goes unnoticed.
Like every hand-tracked concern before it, it does not scale.

An Effect Management System moves the bookkeeping into the type system.
The function signature answers the questions raised earlier in this chapter:
what does this function depend on, what does it change, what can go wrong.
Composition stops being a guess,
because the compiler balances the books at every boundary.
The languages that do this today are young,
and the libraries that retrofit it are demanding.
That was true of every solution to every previous barrier at this stage.
Namespaces once looked like ceremony.
Effect tracking will look obvious in hindsight,
and future programmers will regard a function with hidden Effects the way you regard a program written in one global namespace.

Python offers no native version of this, and will not soon.
The next three chapters build the library version:
[Generators](45_Generators.md) supplies the mechanism,
[Stateless](46_Stateless.md) builds the Effect type on top of it,
and [Stateless in Practice](47_Stateless_in_Practice.md) puts it to work.

## Exercises

1.  Write the production bindings for `ask_tell.py`:
    a `Console` class whose `ask()` calls `input()` and whose `tell()` calls `print()`,
    and run `greet(Console(), Console())` interactively.
    Confirm `greet()` itself required no change,
    which is the delayed-binding payoff.
2.  Feel the bookkeeping the chapter describes.
    Wrap `greet()` in three callers, `session()`, `menu()`, and `main()`,
    each calling the next and none of them using `Ask` or `Tell`.
    Now add a `Log` Effect (a protocol with `log(message)`)
    used by a new helper that `greet()` calls.
    Count the signatures you had to edit,
    and note how many of them mention an Effect they never use.
    Then say what an EMS would do instead.
3.  Classify every Effect in `slope_catch.py`,
    `withdraw()` from [Foundations](40_Functional_Foundations.md#pure-functions),
    and `Thermometer` from [Observer](30_Observer.md): side effect, side cause,
    or exception.
    Which of the three conversions from [Converting Effectful to Pure](#converting-effectful-to-pure)
    applies to each?
4.  `NonZero` guards zero but not negative values,
    while `validate()` in `slope_catch.py` rejects negatives but not zero.
    Build a `PositiveInt` that makes both bad values unconstructable,
    rewrite `slope()` to take it,
    and note which checks disappear from `slope()` as a result.
5.  `coroutines_are_descriptions.py` shows that `async` tracks one Effect.
    Write a synchronous `total_price()` that calls a helper,
    then make the helper `async` and follow what the checker and the interpreter force you to change,
    all the way up to `asyncio.run()`.
    Name the two properties of a full EMS that `async` does *not* have,
    using the three-item list in [Effect Management Systems](#effect-management-systems).
