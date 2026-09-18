# Effect Tracking

[Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
asks whether Python could gain Effect tracking.
Its answer is that the annotation syntax could carry the information,
and that propagation is the hard part.
This appendix works through that answer.
It states the tracking problem apart from any one language,
says why a language that tracks Effects natively solves the problem best,
and then builds the carrier Python has today,
the `Annotated` type from [PEP 593](https://peps.python.org/pep-0593/).
The last part analyzes the tool that would check those annotations,
showing how much of a type checker the tool would contain.
The appendix stops short of building that tool.

## The Tracking Problem

[Effect Management Systems](44_Effects--Effect_Management.md#effect-management-systems)
separates tracking from management.
Tracking tells you which Effects a function can perform,
and management lets you replace what those Effects do.
This appendix concerns tracking.

A function's Effects come from two sources.
The body performs some of them directly, as a call to `print()` does.
The function inherits the rest from the functions it calls.
Handling removes Effects.
A function that runs `greet()` inside a handler for `Ask` passes no `Ask` to its own callers.
The *Effect row* of a function `f` therefore follows one rule:

```text
row(f) = the Effects f performs directly
       + row(g) for every g that f calls
       - the Effects f handles
```

The second line makes the rule recursive,
and that recursion is the propagation [Effect Management](44_Effects--Effect_Management.md#native-effect-management)
describes.

Koka and the other native systems follow this rule because they implement algebraic effects,
the design [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
names.
An algebraic effect is a set of operations declared as an interface.
A handler gives those operations their meaning,
and handling removes the effect from the row.
The design has two halves, the row and the handlers.
*Algebraic effect tracking* is the row half: the rule above,
computed and checked for every function.
That half is this appendix's subject, and "tracking" means it from here on.

A system that tracks Effects needs three things:

1. **A place to write the row.**
   The row must sit in the signature without occupying the argument list,
   the second channel of [Effects by Hand](44_Effects--Effect_Management.md#effects-by-hand).
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

As you read down the table, the work moves from you to the compiler.
The rest of this appendix asks how far `Annotated` can move it.

## Why a Native System Tracks Best

Native algebraic effect tracking has four properties,
and each later section finds one of them missing from the `Annotated` design.

**The compiler infers the row.**
Koka computes a function's row from its body,
so most functions need no written row.
You write a row when you want a constraint,
such as requiring that a function stay pure.
[Effects by Hand](44_Effects--Effect_Management.md#effects-by-hand)
counts five signatures to edit when a `Log` Effect appears three levels down.
In Koka the same change edits no signature you left to inference.

**A row can contain a variable.**
Here is the signature of Koka's `map()`:

```koka
fun map(xs : list<a>, f : a -> e b) : e list<b>
```

The `e` is an *Effect variable*.
It says `map()` performs whatever `f` performs, for any `f`.
That property is *Effect polymorphism*,
and a tracking system without it must either forbid effectful callbacks or exempt them from tracking.
Java's standard functional interfaces forbid them.
`Function.apply()` declares no exception,
so a lambda passed to `Stream.map()` cannot throw a checked one.
Programmers wrap the exception in an unchecked one, which the compiler accepts.

**Handling subtracts.**
In the Koka greeting program of [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management),
`main()` handles `ask` and `tell`, so its row is `<console,exn>`.
The handler syntax and the subtraction are one construct,
so they cannot disagree.

**Every function has a row.**
Koka's `println()` carries `console` in its type,
as does every function that calls it, in your code and in the standard library.
The compiler tracks all code, so every Effect appears in some function's row.

All four follow from one fact: the three roles belong to one compiler,
and that compiler analyzes every function in the program.

## A Row Inside `Annotated` {#a-row-inside-annotated}

PEP 593 added `Annotated[T, x, y, ...]` to `typing` in Python 3.9.
`T` is a type.
The arguments after it are *metadata*, and they are values, not types.
Each one is an ordinary expression,
and `Annotated` keeps whatever it evaluates to.
`Annotated[int, "meters", range(0, 100)]` carries two pieces of metadata,
a string and a `range` object.
One piece of metadata is required, and any number can follow it.
The PEP gives tools one rule:
a tool with no logic for a piece of metadata ignores that piece and treats the annotation as `T`.
Each tool can therefore put its own object in the list,
and every other tool reads past it.
So metadata changes nothing for a type checker,
and the runtime can read it back with `get_type_hints()`.
That makes `Annotated` a candidate for the first role, a place to write the row:

```python
# effect_rows.py
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
    result = hints.get("return")
    return sorted(
        effect.__name__
        for extra in getattr(result, "__metadata__", ())
        if isinstance(extra, Performs)
        for effect in extra.effects
    )
```

`Performs` wraps the row because every tool shares the metadata.
A validation library may put its own objects in the same `Annotated`,
and the PEP directs every consumer to act only on the objects it recognizes.
The `isinstance()` test in `row()` does that.
`include_extras=True` keeps the metadata,
which `get_type_hints()` otherwise strips.
`__metadata__` is the tuple where `Annotated` stores it.

An annotation belongs to a parameter or to the return value,
and no annotation belongs to the function as a whole.
A row describes a call, and every call produces the return value,
so `row()` reads the row from the return annotation.
Stateless and ZIO put their rows in the same place.

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

for f in ask, tell, greet, shout:
    print(f.__name__, row(f))
#: ask ['Ask']
#: tell ['Tell']
#: greet ['Ask', 'Tell']
#: shout []
```

The bodies are ordinary eager code, with no generators and no `yield from`.
`ty` follows the PEP's rule:
`reveal_type(ask)` reports `def ask(prompt: str) -> str`,
and `name: str = ask(...)` checks against that `str`.
Existing callers need no change,
so a codebase could adopt rows one function at a time.

That same rule is the design's weakness.
`shout()` calls `tell()` and declares nothing.
Its row reads as empty, and `ty` reports nothing,
because the PEP instructs `ty` to ignore the one fact that matters here.
Compare `undeclared_need.py` in [Stateless](46_Effects--Stateless.md#effects-propagate-and-the-type-checker-verifies-it),
where the same mistake draws an `invalid-yield` error.
Until a tool reads it, a row inside `Annotated` is a structured comment.
`greet()`'s row is right because I typed it correctly.

Notice also that `ask()` calls `input()` directly.
`Ask` is a label here.
It has no methods, and nothing can substitute another implementation for it.

## What a Checker for the Row Must Do

`row()` fills the first role.
A tool that fills the second and third must solve five problems,
and each one is larger than it first appears.

### Resolve Every Call

To compute a row, the tool lists every call in a body and finds each callee's declaration.
A direct call to a module-level function is the easy case.
The `ast` module finds `tell(message.upper())` in `shout()`,
and the name `tell` resolves in the module's scope.

A method call is the ordinary case, and it is hard.
For `console.print(message)` the tool needs the type of `console`.
That type may come from a parameter annotation, an assignment,
a narrowing `isinstance()`, a generic, or an overload.
A subclass may also override the method.
An override needs its own rule:
the overriding method's row must fit inside the row of the method it replaces,
or a caller holding the base type performs Effects the base row omits.

Working all of that out is type inference, which `ty` performs on every run.
The tool therefore belongs inside the type checker.
Of the three checkers, mypy has a plugin interface;
`ty` and Pyright have none at this writing.
A tool that runs outside the checker has two choices.
It can repeat the checker's inference,
or it can check the calls it is able to resolve and treat the others as unknown.

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
Koka writes that with the Effect variable `e`.
Python's type variables cannot help,
because a type variable placed inside metadata is one more object the checker ignores.
The tool would require its own notation,
something like `performs(RowOf("action"))`,
and its own solver for that notation.
At each call of `each()` the solver must find the argument and then the argument's row.
The argument may be a `partial()`, a bound method,
a callable pulled from a dictionary, or a lambda, which has no annotations.
Effect variables amount to a second type system beside the first.

Stateless has Effect variables without building a second type system,
because its row is an ordinary type:

```python
# effect_variable.py
from collections.abc import Callable
from typing import Any
from stateless import (
    Ability,
    Depend,
    Need,
    need,
    run,
    supply,
)

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

`A` stands for whatever row the argument carries.
`reveal_type(twice(hello))` reports `Generator[Need[Console], Any, None]`.
`ty` solved `A` as `Need[Console]`,
with the solver it uses for every other generic.
`hello_twice()` must then declare that row, or `ty` rejects its `yield from`.

### Subtract What a Handler Discharges

Without subtraction a row grows at every level of the call stack.
`main()` would carry every Effect in the program,
and a row that lists everything tells you nothing.
The tool therefore needs a construct that marks a handler's scope:

```python
with handling(Ask, Scripted()):
    greet()
```

Inside that block the tool would remove `Ask` from the row.
The subtraction is sound if the handler intercepts the Effect,
and that interception requires `ask()` to consult the installed handler instead of calling `input()`.
That takes a runtime mechanism,
such as the `ContextVar` in [Effects by Hand](44_Effects--Effect_Management.md#effects-by-hand).
Now the design has two halves, a static tool and a runtime library,
and the tool cannot check that the library does what the metadata says.
In Koka one construct installs the handler and subtracts from the row.
In Stateless the `Handler` that `supply()` returns does the subtracting.
Its type removes the `Need` from the row of the function it wraps,
and `ty` verifies the result.

### Decide What Untracked Code Performs

`print()`, `open()`, and nearly every function on PyPI carry no row.
The tool must assume something about them,
and each assumption creates its own problem:

- **Undeclared means pure.**
  The row becomes a lower bound.
  It lists the Effects someone wrote down.
  A direct call to `print()` stays invisible to the tool,
  the limit [Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
  found in Stateless.
- **Undeclared means `Unknown`.**
  An unknown Effect spreads into every caller the way `Any` spreads through types,
  so nearly every row reads `Unknown` until someone declares the libraries below your code.
- **Declare the libraries separately.**
  Gradual typing took this route with stub files and typeshed.
  The C functions under `print()` and `open()` need it regardless,
  since they have no Python body to analyze.
  [Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
  says how long that took: a decade.

Dynamic code adds to the unknowns: `getattr(obj, name)()`,
a decorator that returns a wrapper with a different row,
a module-level `__getattr__()`, a function replaced at runtime by a test.
A type checker meets the same constructs and infers `Any` or `Unknown`.
The Effect tool would give the same answer, with the same loss.

### Find a Place to Run

The tool could run in three places.
The first is inside the type checker,
a place [Resolve Every Call](#resolve-every-call) ruled out for `ty`.

The second is a separate static tool, run beside `ty` and `ruff`.
Every problem above applies to it in full.

The third is the runtime.
A decorator reads each function's row once with `row()`,
and a `ContextVar` holds the row of the function now running.
On each decorated call,
the decorator compares the two rows and raises an exception when the callee's is not a subset of the caller's.
Call resolution disappears as a problem, because running a call resolves it.
The loss is coverage.
A runtime check covers the paths a run executes,
so it verifies what your tests exercise and reports nothing about the rest.
It stands to the static tool as `isinstance()` assertions stand to `ty`.

## Tracking Is Not Management

Suppose the static tool existed, complete and correct.
It would fill all three roles, and you would have Effect tracking.
`ask()` would still call `input()`.
No test could replace that call,
because the row names an Effect without separating its interface from its implementation,
and nothing binds an implementation later.
Interface separation and delayed binding are the second and third properties of a full EMS,
and the tool supplies neither.

Metadata is data, and its reader decides what it means.
A static reader can treat it as a row.
A runtime reader can treat it as a binding.
FastAPI's `Depends` from [Dependency Injection](46_Effects--Stateless.md#dependency-injection)
goes in `Annotated` metadata in the form FastAPI recommends,
and the framework supplies the dependency when a request arrives.
Nothing connects the two readers.
No check confirms that the row one tool verified is the set of dependencies the other one binds.

[The Tracking Problem](#the-tracking-problem)
divided algebraic effects into a row half and a handler half.
`Annotated` can carry the row, and no metadata can supply a handler.
A native handler receives the continuation and decides what to do with it.
[Stateless in Practice](47_Effects--Stateless_in_Practice.md#handlers-cannot-capture-the-continuation)
shows the ceiling Python puts on that half: a Python generator is one-shot,
so a handler can resume a computation once.
What PEP 593 could give Python is algebraic effect tracking, the row half.
The handler half would still come from a library, under that ceiling.

Stateless gets tracking, interface separation,
and delayed binding with no new tool.
The reason is where it puts the row:
the generator's yield type is a place the type checker examines on every run.
You declare the row there,
and `ty` verifies the propagation by checking every `yield from` in the body against it.
The `Handler` that `supply()` returns subtracts.
A type variable gives Effect polymorphism, as `effect_variable.py` shows.
Stateless requires the generator syntax and the description/execution split that [Library Effect Management](44_Effects--Effect_Management.md#library-effect-management)
describes.

`Annotated` keeps the code ordinary and eager, and nothing verifies the row.
A native system keeps ordinary code and a verified row,
because the compiler that runs the code is the one that tracks it.
That is the case for putting Effect tracking in the language,
and it is why [Effects Are the Next Barrier](44_Effects--Effect_Management.md#effects-are-the-next-barrier)
expects the tracking to move into the language or its toolchain.
