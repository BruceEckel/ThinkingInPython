# Effect Tracking

[Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
asks whether Python could gain Effect tracking.
It answers that the annotation syntax could carry the information and that propagation is the hard part.
This appendix states the tracking problem apart from any one language,
says why a language that tracks Effects natively solves the problem best,
and then builds the carrier Python has today,
the `Annotated` type from [PEP 593](https://peps.python.org/pep-0593/).
The last part analyzes the tool that would check those annotations and shows how much of a type checker the tool would contain.
[An Effect Checker](B_An_Effect_Checker.md)
builds the part of that tool that works from names and written types.

## The Tracking Problem

[Tracking and Management](44_Effects--Effect_Management.md#tracking-and-management)
separates tracking from management.
Tracking tells you which Effects a function can perform.
Management lets you replace what those Effects do.
This appendix concerns tracking.

A function's Effects come from two sources.
The body performs some of them directly, as a call to `print()` does.
The function inherits the rest from the functions it calls.
Handling removes Effects.
A function that runs `greet()` inside a handler for `Ask` passes its own callers every Effect of `greet()` except `Ask`.
The [Effect row](44_Effects--Effect_Management.md#native-effect-management)
of a function `f` therefore follows one rule:

```text
row(f) = the Effects f performs directly
       + row(g) for every g that f calls
       - the Effects f handles
```

The `row(g)` line makes the rule recursive,
and that recursion is the propagation [Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
calls the hard part.

Koka and the other native systems compute this rule as part of algebraic effects,
the design [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
names.
In algebraic effects, you declare each Effect as an interface.
A handler gives the Effect its meaning.
Handling removes the Effect from the row.
The design has two halves, the row and the handlers.
A language can have one without the other.
OCaml 5 has handlers and records no row in a function's type.
*Algebraic effect tracking* is the row half: the `row(f)` rule,
computed and checked for every function.

A system that tracks Effects needs three things:

1. **A place to write the row.**
   The row must sit in the signature,
   beside the argument list and the return type,
   as the third part of a signature in [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management).
2. **Something that computes the rule's right side.**
   That means finding every call in a body and the row of every callee.
3. **Something that compares the computed row with the declared one,** and rejects the program when they differ.

Every approach in the Effects chapters fills those three roles:

| Approach | Where the row lives | Who computes it | Who checks it |
|---|---|---|---|
| Parameters, as in `ask_tell.py` | The parameter list | You | The type checker, for the parameters you remembered |
| Java's checked exceptions | The `throws` clause | You | The compiler, for one Effect |
| `async` | The `async` keyword | You | The compiler, for one Effect |
| Stateless | The generator's yield type | You | The type checker, at every `yield from` |
| Koka | The Effect row | The compiler | The compiler |

Down the table, computing the row moves from you to the compiler.
The open question is whether a tool can compute and check a row written in `Annotated`.

## Why a Native System Tracks Best

Native algebraic effect tracking has four properties.
A tool built on the `Annotated` design must supply each one.
The first four problems in [What a Checker for the Row Must Do](#what-a-checker-for-the-row-must-do)
take them in the same order.

**The compiler infers the row.**
Because Koka computes a function's row from its body,
most functions leave their row to inference.
You write a row when you want a constraint,
such as requiring that a function stay pure.
[Effects by Hand](44_Effects--Effect_Management.md#effects-by-hand)
counts five signatures to edit when a helper four calls below `main()` needs a `Log` Effect.
In Koka the same change leaves every inferred signature as it was.

**A row can contain a variable.**
Here is the signature of Koka's `map()`:

```koka
fun map(xs : list<a>, f : a -> e b) : e list<b>
```

The `e` is an *Effect variable*.
It says `map()` performs whatever `f` performs, for any `f`.
That property is *Effect polymorphism*.

A tracking system without Effect polymorphism must either forbid effectful callbacks or exempt them from tracking.
Java's standard functional interfaces forbid them.
`Function.apply()` declares no exception,
so a lambda passed to `Stream.map()` cannot throw a checked one.
Programmers wrap the exception in an unchecked one, which the compiler accepts.

**Handling subtracts.**
In the Koka greeting program of [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management),
`main()` handles `ask` and `tell`, so neither appears in its row,
`<console,exn>`.
The handler syntax and the subtraction are one construct,
so the row drops exactly the Effects a handler handles.

**Every function has a row.**
Koka's `println()` carries `console` in its type,
as does every function that calls it, in your code and in the standard library.
The compiler tracks all code, so every Effect appears in some function's row.

All four properties follow from one fact.
The three roles belong to one compiler,
and that compiler analyzes every function in the program.

## A Row Inside `Annotated` {#a-row-inside-annotated}

PEP 593 added `Annotated[T, x, y, ...]` to `typing` in Python 3.9.
`T` is a type.
The arguments after it are *metadata*, and `Annotated` requires at least one.
Each piece of metadata is an ordinary expression,
and `Annotated` keeps its value.
The type checker treats a class in the metadata as a value, not as a type.
`Annotated[int, "meters", range(0, 100)]` carries two pieces of metadata,
a string and a `range` object.

The PEP gives tools one rule.
A tool with no logic for a piece of metadata ignores that piece and treats the annotation as `T`.
Each tool can therefore put its own object in the list,
and every other tool ignores it.
A type checker is one of those other tools, so it sees the annotation as `T`.
At runtime, your code reads the metadata back with `get_type_hints()`.
Those two facts make `Annotated` a candidate for the first role,
a place to write the row:

```python
# utils/effect_rows.py
from collections.abc import Callable
from typing import get_type_hints
from record import record

@record
class Performs:
    effects: frozenset[type]

def performs(*effects: type) -> Performs:
    return Performs(frozenset(effects))

def row(f: Callable[..., object]) -> list[str]:
    hints = get_type_hints(f, include_extras=True)
    annotation = hints.get("return")
    return sorted(
        effect.__name__
        for piece in getattr(annotation, "__metadata__", ())
        if isinstance(piece, Performs)
        for effect in piece.effects
    )
```

The listing lives in `utils/` because [An Effect Checker](B_An_Effect_Checker.md)
imports it too.
`Performs` wraps the row in a type that `row()` can recognize,
because every tool shares the metadata.
A validation library may put its own objects in the same `Annotated`.
The PEP directs every consumer to act on the objects it recognizes and ignore the rest.

`get_type_hints()` strips the metadata unless you pass `include_extras=True`.
`Annotated` stores the metadata in its `__metadata__` tuple.

A function has two places for annotations, its parameters and its return value.
A row describes a call.
A function with no parameters, such as `greet()`, has one place to hold the row:
its return annotation.
Every function returns a value,
so `row()` reads the row from the return annotation.
Stateless and ZIO put their rows in the return type too.
A Stateless `Depend[A, R]` is a `Generator`,
and its row `A` is that generator's yield type.

Here is the greeting program with its rows declared:

```python
# tracked_greeting.py
from typing import Annotated
from effect_rows import performs, row

class Ask: ...
class Tell: ...

def ask(prompt: str) -> Annotated[str, performs(Ask)]:
    return input(prompt)

def tell(message: str) -> Annotated[None, performs(Tell)]:
    print(message)

def greet() -> Annotated[None, performs(Ask, Tell)]:
    name: str = ask("What is your name? ")
    tell(f"Hello, {name}!")

def shout(message: str) -> None:
    tell(message.upper())

def quiet() -> Annotated[None, performs()]:
    shout("hi")

for f in ask, tell, greet, shout, quiet:
    print(f.__name__, row(f))
#: ask ['Ask']
#: tell ['Tell']
#: greet ['Ask', 'Tell']
#: shout []
#: quiet []
```

The bodies are ordinary eager code, with no generators and no `yield from`.
The type checker follows the PEP's rule.
`reveal_type(ask)` reports `def ask(prompt: str) -> str`,
and `name: str = ask(...)` checks against that `str`.
Existing callers stay as they are,
so a codebase could adopt rows one function at a time.

That same rule is the design's weakness.
`shout()` calls `tell()` under a bare `None` return annotation.
The type checker accepts `shout()`,
because the PEP instructs every type checker to ignore metadata,
including the `Tell` in the return annotation of `tell()`.
Compare `undeclared_need.py` in [Stateless](46_Effects--Stateless.md#effects-propagate-and-the-type-checker-verifies-it),
where the type checker reports the same mistake as an `invalid-yield` error.
A row inside `Annotated` is a structured comment until a tool reads it.
`greet()`'s row lists `Ask` and `Tell` because I typed them,
and no tool compares them with the calls in its body.

`shout()`'s empty row has a second reading.
`quiet()` declares `performs()` with no arguments, which states that it is pure.
`row(quiet)` returns the same empty list,
so an empty list can mean either a function declared pure or [one that declares nothing](#decide-what-untracked-code-performs).

`quiet()`'s declaration is also wrong.
`quiet()` calls `shout()`, which calls `tell()`.
`row()` reads each declaration alone,
so it returns the empty row `quiet()` declares.

`Ask` is a label here, an empty class,
so `input()` stays the one implementation `ask()` can run.
The row tracks the Effect.
[Tracking Is Not Management](#tracking-is-not-management)
explains why a row alone cannot manage it.

## What a Checker for the Row Must Do

`Annotated` fills the first role, a place to write the row,
and `row()` reads it back.
To fill the second and third roles, computing the row and checking it,
a tool must solve five problems.

### Resolve Every Call

To compute a row, the tool lists every call in a body and finds each callee's declaration.
A direct call to a module-level function is the easy case.
The `ast` module finds `tell(message.upper())` in `shout()` and leaves name binding to the tool.
The tool looks `tell` up in `shout()`'s local names,
then at the module's top level, where it finds `tell()`.

A method call is the ordinary case, and it is hard.
For `console.print(message)` the tool needs the type of `console`.
That type may come from a parameter annotation, an assignment,
a narrowing `isinstance()`, a generic, or an overload.
A subclass may also override the method.
An override needs its own rule.
The overriding method's row must fit inside the row of the method it replaces,
or a caller holding the base type performs Effects the base row omits.

Working all of that out is type inference,
which the type checker performs on every run.
The tool therefore belongs inside the checker.
Of the three checkers this book names,
mypy alone has a plugin interface at this writing.
That rules out `ty` and Pyright as hosts for the tool.
A tool that runs outside the checker has two choices.
It can repeat the checker's inference,
or it can check the calls it resolves and treat the others as unknown.

### Propagate Through Callbacks

Consider a function that calls its argument:

```python
def each[T](
    action: Callable[[T], None], items: list[T]
) -> None:
    for item in items:
        action(item)
```

The row of `each()` is the row of `action`, and that row differs at every call.
Koka writes such a row with the Effect variable `e`.
Python's type variables cannot help,
because a type variable placed inside metadata is one more object the checker ignores.
The tool would require its own notation,
something like `performs(RowOf("action"))`,
and its own solver for that notation.
At each call of `each()` the solver must find the argument and then the argument's row.
The argument may be a `partial()`, a bound method,
a callable pulled from a dictionary, or a lambda, which has no annotations.
Effect variables amount to a second type system beside the first.

Stateless gets Effect variables from Python's existing type system,
because its row is an ordinary type:

```python
# effect_variable.py
from collections.abc import Callable
from typing import Any
from stateless import (Ability, Depend, Need, need, run,
                       supply)

class Console:
    def print(self, message: str) -> None:
        print(message)

def hello() -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print("Hello!")

def twice[A: Ability[Any]](
    effect: Callable[[], Depend[A, None]],
) -> Depend[A, None]:
    yield from effect()
    yield from effect()

def hello_twice() -> Depend[Need[Console], None]:
    yield from twice(hello)

run(supply(Console())(hello_twice)())
#: Hello!
#: Hello!
```

`A` stands for the row the argument carries.
`reveal_type(twice(hello))` reports `Generator[Need[Console], Any, None]`.
The type checker solves `A` as `Need[Console]`,
with the solver it uses for every other generic.
`hello_twice()` must then declare that row,
or the checker rejects its `yield from`.

### Subtract What a Handler Discharges

Without subtraction a row grows at every level of the call stack.
`main()` would carry every Effect in the program.
A row that lists everything tells you nothing.
The tool therefore needs a construct that marks a handler's scope:

```python
with handling(Ask, Scripted()):
    greet()
```

`Scripted`, the test stand-in from `ask_tell.py`,
answers every prompt with the same name.
Inside that block the tool would remove `Ask` from the row.
The subtraction is sound if the handler intercepts the Effect.
Interception requires `ask()` to consult the installed handler instead of calling `input()`.
Consulting an installed handler takes a runtime mechanism,
such as the `ContextVar` in [Effects by Hand](44_Effects--Effect_Management.md#effects-by-hand).
Now the design has two halves, a static tool and a runtime library.
The tool cannot ensure that the library intercepts the Effect that the `handling` block removes from the row.
In Koka one construct installs the handler and subtracts from the row.
In Stateless the `Handler` that `supply()` returns does the subtracting.
Its type removes the `Need` from the row of the function it wraps,
and the type checker verifies the result.

### Decide What Untracked Code Performs

`print()`, `open()`, and nearly every function on PyPI carry no row.
The tool must assume something about them,
and each assumption creates its own problem:

- **Undeclared means pure.**
  The row becomes a lower bound.
  It lists the Effects someone wrote down.
  A direct call to `print()` leaves the row as it was.
  [Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
  finds the same limit in Stateless.
- **Undeclared means `Unknown`.**
  `Unknown` propagates into the row of every caller,
  the way `Any` propagates into every type computed from it.
  Nearly every row then reads `Unknown` until someone declares the libraries your code calls.
- **Declare the libraries separately.**
  Gradual typing declares them with stub files and typeshed.
  The C functions under `print()` and `open()` need separate declarations regardless,
  since they have no Python body to analyze.
  [Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
  says how long gradual typing took to cover the ecosystem: a decade.

Dynamic code adds to the unknowns: `getattr(obj, name)()`,
a decorator that returns a wrapper with a different row,
a module-level `__getattr__()`, a function replaced at runtime by a test.
A type checker infers `Any` or `Unknown` for most of the same constructs.
The Effect tool would answer `Unknown` for them too.
Every row that includes `Unknown` would be incomplete.

### Find a Place to Run

The tool could run in three places.
The first is inside the type checker,
a place [Resolve Every Call](#resolve-every-call) rules out for `ty`.

The second is a separate static tool, run beside `ty` and `ruff`.
The four problems before this section apply in full to a separate tool.
[An Effect Checker](B_An_Effect_Checker.md) builds a small one.
That checker reports `Unknown` for a call it cannot resolve.
That appendix's [closing section](B_An_Effect_Checker.md#what-the-checker-resolves-and-what-it-cannot-see)
lists the cases where the checker passes over a call or misreads it as pure,
so the row looks complete.

The third is the runtime.
A decorator reads each function's row once with `row()`,
and a `ContextVar` holds the Effects the running code may perform:
the running function's row, plus the Effect of each enclosing `handling` block.
On each decorated call,
the decorator raises an exception when the callee's row holds an Effect outside that set,
and otherwise sets the `ContextVar` to the callee's row until the call returns.
Setting the `ContextVar` that way bounds each function the callee calls by the callee's row,
not by the caller's wider set.
A function that handles `Ask` leaves `Ask` out of its own row.
That function's `handling(Ask, Scripted())` block puts `Ask` back in the set,
so the `greet()` call inside the block passes.

The runtime check leaves call resolution to Python,
which resolves each call by running it.
Its limit is coverage.
A runtime check covers the paths a run executes,
so it verifies what your tests exercise and stays silent about the rest.
It stands to the static tool as `isinstance()` assertions stand to the type checker.

## Tracking Is Not Management

If the static tool existed, complete and correct,
it would fill all three roles and give you algebraic effect tracking.
`ask()` would still call `input()`.
Every test of `ask()` would run that call.
The row names an Effect,
but `ask()` holds both the Effect's interface and its implementation,
bound together when you write `ask()`.
Interface separation and delayed binding are the second and third properties of a full EMS.
The tool supplies neither.

Metadata is data, and its reader decides what it means.
A static reader can treat it as a row.
A runtime reader can treat it as a binding.
FastAPI's [`Depends`](46_Effects--Stateless.md#dependency-injection)
goes in `Annotated` metadata in the form FastAPI recommends,
and the framework supplies the dependency when a request arrives.
No check confirms that the row a static tool verified matches the dependencies FastAPI binds.

[The Tracking Problem](#the-tracking-problem)
divides algebraic effects into a row half and a handler half.
`Annotated` can carry the row, so PEP 593 could give Python the row half,
algebraic effect tracking.
No metadata can supply the handler half.
A native handler receives the continuation and can resume it once,
several times, or never.
In Python the handler half would come from a library.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md#handlers-cannot-capture-the-continuation)
shows the limit Python puts on that half.
A Python generator is one-shot, so a handler can resume a computation once.

Stateless gets tracking, interface separation,
and delayed binding with no new tool.
The reason is where it puts the row.
The generator's yield type is a type the checker verifies on every run.
You declare the row there,
and the checker verifies the propagation by checking every `yield from` in the body against it.
The `Handler` that `supply()` returns subtracts the supplied Abilities from the row,
so a caller declares the Abilities that remain.
A type variable gives Effect polymorphism, as `effect_variable.py` shows.
Stateless requires the generator syntax and the description/execution split that [Library Effect Management](44_Effects--Effect_Management.md#library-effect-management)
describes.

`Annotated` keeps the code ordinary and eager.
The type checker ignores the row.
A native system keeps ordinary code and a verified row,
because the compiler that compiles the code also computes and checks its rows.
That is the case for putting algebraic effect tracking in the language,
and it is why [Effects Are the Next Barrier](44_Effects--Effect_Management.md#effects-are-the-next-barrier)
expects the tracking to move into the language or its toolchain.
