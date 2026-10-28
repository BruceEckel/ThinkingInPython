# Effect Management: Solutions

## 1. Production bindings for `ask_tell.py`

> Write the production bindings for `ask_tell.py`:
> a `Console` class whose `ask()` calls `input()` and whose `tell()` calls `print()`.
> Then run `greet(Console(), Console())` interactively.
> Confirm `greet()` runs unchanged.
> Serving a new context without edits is what delayed binding provides.

<details>
<summary>Where to look</summary>

[Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
shows `greet()` taking its `Ask` and `Tell` Effects as parameters.
The `Ask` and `Tell` protocols are structural,
so `Console` needs only methods with matching signatures.
Pass one `Console` for both parameters, or pass a double for either.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

def greet(ask: Ask, tell: Tell) -> None:
    ...

class Console:
    def ask(self, prompt: str) -> str:
        ...

    def tell(self, message: str) -> None:
        ...

class Scripted:
    def ask(self, prompt: str) -> str:
        ...
```

<details>
<summary>Done when</summary>

`greet(Console(), Console())` prompts `What is your name? ` and prints `Hello, ` plus the name you type,
with `greet()` identical to the one in `ask_tell.py`.
`uv run ty check` passes,
and changing `Console.tell()` to return a `str` makes it report `invalid-argument-type` at the `greet(...)` call.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

def greet(ask: Ask, tell: Tell) -> None:
    name = ask.ask("What is your name? ")
    tell.tell(f"Hello, {name}!")

class Console:
    def ask(self, prompt: str) -> str:
        return input(prompt)

    def tell(self, message: str) -> None:
        print(message)

class Scripted:
    def ask(self, prompt: str) -> str:
        return "Alice"

greet(Scripted(), Console())  # Real tell, scripted ask
#: Hello, Alice!
```

An interactive run of `greet(Console(), Console())` looks like this:

```text
What is your name? Alice
Hello, Alice!
```

`exercise_1.py` binds the real `Console` for `tell` and keeps the scripted `ask`,
because a book listing that calls `input()` runs with no terminal attached.
The substitution is the point either way.
One `Console` instance satisfies both protocols,
so you can pass the same object for both parameters.
You can also replace either parameter with a double,
and the other parameter keeps its binding.

**Declare what the function needs.**
`greet()` runs unchanged, as it must.
Its body names only its parameters, `ask` and `tell`,
so changing the binding leaves that body as it is.
Delayed binding moves the choice of implementation to the call site,
where a test can choose differently from production.

**Satisfy the protocols structurally.**
After the choice moves, the type checker still enforces the protocols.
`Console` inherits from `object` rather than from `Ask` or `Tell`,
but it has the two methods with the right signatures,
so it satisfies both protocols structurally.
If you give `Console` a `tell()` that returns a `str`,
`ty` reports `invalid-argument-type` at the `greet(...)` call,
not at the class definition.
The checker compares `Console` with `Tell` where `greet()` receives the `Console` as `tell`,
the one place the class meets the protocol.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Threading a `Log` Effect through every signature

> Do the bookkeeping the chapter describes.
> Starting from `bookkeeping_scales.py`, add a `Log` Effect
> (a protocol with `log(message)`) used by a new helper that `greet()` calls,
> and log from `greet()` too.
> The chapter counts five signatures for that version.
> Say how many of the five use the `Log` they declare,
> and then what an EMS would do instead.

<details>
<summary>Where to look</summary>

[Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
shows the bookkeeping that each new Effect adds to every signature on the path.
Add a `Log` protocol, give the new helper and `greet()` a `log` parameter,
and count which functions use the `Log` and which forward it to the next call.
Compare that count with what [Tracking and Management](../../Chapters/44_Effects--Effect_Management.md#tracking-and-management)
says an EMS declares instead.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from dataclasses import dataclass, field
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

class Log(Protocol):
    def log(self, message: str) -> None: ...

def format_greeting(name: str, log: Log) -> str:
    ...

def greet(ask: Ask, tell: Tell, log: Log) -> None:
    ...

def session(ask: Ask, tell: Tell, log: Log) -> None:
    ...

def menu(ask: Ask, tell: Tell, log: Log) -> None:
    ...

def main(ask: Ask, tell: Tell, log: Log) -> None:
    ...

class Scripted:
    def ask(self, prompt: str) -> str:
        ...

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)

    def tell(self, message: str) -> None:
        ...

    def log(self, message: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

`main(Scripted(), ...)` prints your log messages and then `Hello, Alice!`,
and `uv run ty check` passes.
You can sort the five signatures into those that call `log()` and those that only pass `log` along,
and say which of your edits an EMS would remove.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
from dataclasses import dataclass, field
from typing import Protocol

class Ask(Protocol):
    def ask(self, prompt: str) -> str: ...

class Tell(Protocol):
    def tell(self, message: str) -> None: ...

class Log(Protocol):
    def log(self, message: str) -> None: ...

def format_greeting(name: str, log: Log) -> str:
    log.log(f"formatting greeting for {name}")
    return f"Hello, {name}!"

def greet(ask: Ask, tell: Tell, log: Log) -> None:
    log.log("greet started")
    name = ask.ask("What is your name? ")
    tell.tell(format_greeting(name, log))

def session(ask: Ask, tell: Tell, log: Log) -> None:
    greet(ask, tell, log)

def menu(ask: Ask, tell: Tell, log: Log) -> None:
    session(ask, tell, log)

def main(ask: Ask, tell: Tell, log: Log) -> None:
    menu(ask, tell, log)

class Scripted:
    def ask(self, prompt: str) -> str:
        return "Alice"

@dataclass
class Capture:
    messages: list[str] = field(default_factory=list)

    def tell(self, message: str) -> None:
        self.messages.append(message)

    def log(self, message: str) -> None:
        self.messages.append(f"LOG: {message}")

captured = Capture()
main(Scripted(), captured, captured)
for line in captured.messages:
    print(line)
#: LOG: greet started
#: LOG: formatting greeting for Alice
#: Hello, Alice!
```

Five signatures declare the new Effect.
Only two of them use it.

**Log at the point of use.**
One of the five is new rather than edited: `format_greeting()`,
the helper that uses the `Log`.
The other four are existing signatures you must edit.
The first of them, `greet()`, both uses a `Log` and accepts one,
to hand down to `format_greeting()`.

**Hand the Effect down the call chain.**
The other three of the five, `session()`, `menu()`, and `main()`,
each gain a `log` parameter whose one use is passing it to the next function.
Their signatures now declare an Effect they do not perform,
so a reader of `menu()` learns something false about what `menu()` does.

The forwarding also grows with the program.
Adding a fourth Effect later means editing every signature on the same chain again.
In a real program that chain is longer than this one.

Most codebases avoid the forwarding with a module-level logger.
The logger removes the parameter by removing the choice.
The function's signature hides that it logs.
Every test runs with the logger the module chose.

A library EMS removes the forwarded parameters and the call-site edits,
and keeps the signature edits.
`format_greeting()` declares in its return type that it needs a `Log`,
and so does every function on the path to `format_greeting()`.
Their parameter lists and their call sites stay as they were.
The type checker reports each declaration you miss.
You supply the binding at one place near the top,
where the program decides what a `Log` means.
[Stateless](../../Chapters/46_Effects--Stateless.md)
shows that shape with a real library.
In that chapter's `audit_log.py`,
`greet_logged()` and its caller `greet_all()` both carry a `Need[Log]` in the `Depend` return type,
while `greet()` stays as it was.

A native EMS removes the signature edits as well.
Koka infers the Effect row of a function you leave unannotated.
Adding a `log` Effect therefore leaves the signatures of `greet()`, `session()`,
`menu()`, and `main()` as they were.
The compiler adds `log` to each of their rows.
You write the new helper and the one handler that binds `log`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Classifying three Effects

> Classify every Effect in `slope_catch.py`,
> `withdraw()` from [Functional Foundations](../../Chapters/40_Functional--Foundations.md#pure-functions),
> and the `Thermometer` that keeps a `_celsius` from [*Observer*](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer):
> side effect, side cause, or exception.
> Which of the three conversions from [Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure)
> applies to the exceptions,
> and which technique from [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
> applies to the rest?

<details>
<summary>Where to look</summary>

[Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure)
covers the exception Effects,
and [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
covers the rest.
For each piece of code, ask whether it writes something outside its result
(a side effect), reads something that can change (a side cause),
or signals failure with an exception.
Then match each kind to the conversion or technique that manages it.

<details>
<summary>Done when</summary>

every Effect in `slope_catch.py`, `withdraw()`,
and `Thermometer` carries one of the three labels,
`withdraw()` and `Thermometer` each carry two,
and every exception points to a conversion from Converting Effectful to Pure.
Each remaining Effect points to the technique from Effects by Hand.

<details>
<summary>Solution</summary>

| Code | Effect | Kind | Conversion |
| --- | --- | --- | --- |
| `slope_catch.py` | `validate()` raises a `ValueError` | Exception | Catch the expected exception, or make the bad value impossible |
| `slope_catch.py` | `rise / 0` raises a `ZeroDivisionError` | Exception | Catch the expected exception, or make the bad value impossible |
| `withdraw()` | writes the `balance` global | Side effect | Pass the implementation in as a parameter |
| `withdraw()` | reads the `balance` global | Side cause | Pass the implementation in as a parameter |
| `Thermometer` | `announce()` calls every subscribed responder | Side effect | Pass the implementation in as a parameter |
| `Thermometer` | `_celsius` read by `celsius` | Side cause | Pass the implementation in as a parameter |

Neither function in `slope_catch.py` has a side effect or a side cause.
Both read their arguments alone and leave everything outside themselves as it was.
The two Effects are both exceptions.

The chapter demonstrates both conversions the table lists for those exceptions.
`slope()` catches the `ZeroDivisionError`,
and in `slope_nonzero.py` a restrictive type makes a zero `run` unconstructable.
The third conversion, a `Result`, applies to both exceptions as well.
`slope_result.py` returns the `ZeroDivisionError` as an `Err`.
In `slope_catch.py`,
the `ValueError` from `validate()` propagates out of `slope()`,
so `@safe` on that `slope()` returns the `ValueError` as an `Err` too.
Exercise 4 moves `validate()`'s check from `slope()` into the constructor of a `PositiveInt`.

`withdraw()` holds both a side cause and a side effect in three lines.
`balance -= amount` reads the global and writes it back.
The read makes the function's result depend on the global `balance` rather than on its arguments.
The write changes `balance`,
which lies outside both the arguments and the return value.
Because each call rewrites the global,
`withdraw(30)` returns `70` the first time and `40` the second.
The [Functional Foundations](../../Chapters/40_Functional--Foundations.md#pure-functions)
chapter uses that pair of calls to show purity failing.
[Confidence](../../Chapters/43_Functional--Confidence.md#referential-transparency)
reuses `withdraw()` to show referential transparency failing.

All three conversions in [Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure)
manage the exception Effect.
For a side cause and a side effect,
the technique from [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
applies instead: pass in what the function would otherwise read or write.
For `withdraw()`, that means taking the balance as a parameter and returning the new one.
The same inputs then give the same answer.
The caller holds the state.

`Thermometer` has the same pair inside a design pattern.
The `celsius` setter writes `_celsius`,
an instance attribute rather than a global.
Then the setter calls `announce()`,
which invokes arbitrary code in every subscribed responder.
The write is a side effect on the object.
The notification is a side effect on the world, since a responder may print,
record, or fail.
Reading `celsius` is a side cause for the same reason `withdraw()` reading `balance` is one.
The value of `celsius` can change between calls,
so the answer depends on earlier assignments to `celsius` rather than on arguments.

The functional conversion makes the temperature source return each reading as a value.
The caller folds new readings into the state it keeps.
The chapter quotes the common name for that conversion,
[pushing the Effects to the edges](../../Chapters/44_Effects--Effect_Management.md#a-program-can-never-be-pure).

Across `withdraw()` and `Thermometer`,
the classification depends on what the code does,
not on the language feature it uses.
A global, an instance attribute,
and a responder list are three storage mechanisms for one idea:
something outside the call participates in the result.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. `PositiveInt` in place of both checks

> `NonZero` guards zero but not negative values,
> while `validate()` in `slope_catch.py` rejects negatives but not zero.
> Build a `PositiveInt` that makes both bad values unconstructable,
> rewrite `slope()` to take it,
> and note which checks disappear from `slope()` as a result.

<details>
<summary>Where to look</summary>

[Make the Bad Value Impossible](../../Chapters/44_Effects--Effect_Management.md#make-the-bad-value-impossible)
builds `NonZero`, whose `__post_init__()` rejects an invalid value.
Write `PositiveInt` with a `__post_init__()` that checks one predicate covering both bad values.
Then give `slope()` a `PositiveInt` parameter and see which guards now always pass.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from exceptions import expect
from record import record

@record
class PositiveInt:
    value: int

    def __post_init__(self) -> None:
        ...

def slope(rise: int, run: PositiveInt) -> float:
    ...
```

<details>
<summary>Done when</summary>

`slope(10, PositiveInt(2))` prints `5.0`,
and `expect(ValueError, PositiveInt, bad)` prints a `[ValueError]` line for both `0` and `-1`.
Your `slope()` body is the division alone: no `try`, no call to `validate()`.
`uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

If you keep `NonZero`'s `self.value == 0` test under the new name,
`PositiveInt(-1)` constructs successfully,
and `slope(10, PositiveInt(-1))` returns `-10.0`.
The demo's `expect()` loop then raises an `AssertionError`
("no exception raised") on `-1`.
The type checker accepts the file, because every argument has the right type.
The solution's `__post_init__()` tests `value <= 0`,
which rejects both bad values.

```python
# exercise_4.py
from exceptions import expect
from record import record

@record
class PositiveInt:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(
                f"PositiveInt needs a positive value: "
                f"{self.value}")

def slope(rise: int, run: PositiveInt) -> float:
    return rise / run.value

print(slope(10, PositiveInt(2)))
#: 5.0
for bad in (0, -1):
    expect(ValueError, PositiveInt, bad)
#: [ValueError] PositiveInt needs a positive value: 0
#: [ValueError] PositiveInt needs a positive value: -1
```

**Cover both bad values with one predicate.**
The original `slope_catch.py` splits the guarding in a way that is easy to miss.
`validate()` rejects negatives but lets zero through.
The `try` catches zero but lets negatives through.
Two mechanisms in two places cover the two bad values independently.
`NonZero` covers one half of that split, the zero.
One predicate, `value <= 0`, covers both,
because "positive" is a single idea and "not zero,
and also not negative" is the same idea described as two exclusions.

**Trust the parameter's type.**
Both checks disappear from `slope()`, and so does the code each one needed.
A `PositiveInt` holds a value of 1 or more.
Dividing by it always succeeds, so the `try`/`except ZeroDivisionError` goes.
The same value always passes `validate()`, so the call to `validate()` goes,
and `validate()` along with it.

**Fail at the construction site.**
The failure now comes from the constructor rather than from `slope()`.
`PositiveInt(bad)` still raises an exception,
at the boundary where an untrusted number enters the program.
A caller reading from a file or a form handles the exception there.

The count of checks changes:
one at the construction site instead of one in every function that uses the value.
Every function downstream of a `PositiveInt` is pure with respect to this failure.
Its signature says which values it accepts,
instead of leaving that to a docstring.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. What `async` tracks, and what it does not

> `coroutines_are_descriptions.py` shows that `async` tracks one Effect.
> Write a synchronous `total_price()` that calls a helper,
> then make the helper `async` and follow what the type checker and the interpreter force you to change,
> all the way up to `asyncio.run()`.
> Name the two properties of a full EMS that `async` lacks,
> using the three-item list in [Tracking and Management](../../Chapters/44_Effects--Effect_Management.md#tracking-and-management).

<details>
<summary>Where to look</summary>

[Effect Management for Python](../../Chapters/44_Effects--Effect_Management.md#effect-management-for-python)
shows that calling an `async` function returns a coroutine,
a description of work.
Make the helper `async`,
then change each caller to `async` with `await` until `asyncio.run()` ends the chain.
Weigh what you get against the list in [Tracking and Management](../../Chapters/44_Effects--Effect_Management.md#tracking-and-management).

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import asyncio

PRICES = {"apple": 1.5, "pear": 2.0}

def price_of(item: str) -> float:
    ...

def total_price(items: list[str]) -> float:
    ...

async def price_of_async(item: str) -> float:
    ...

async def total_price_async(items: list[str]) -> float:
    ...
```

<details>
<summary>Done when</summary>

`total_price()` and `asyncio.run()` on its `async` version print the same total,
and `uv run ty check` passes.
Deleting the `await` in front of the helper call makes the type checker report an error.
You can name the two items of the three-item list in Tracking and Management that `async` lacks.

<details>
<summary>Solution</summary>

Because calling an `async` function builds a coroutine that runs its body when awaited,
the solution awaits each call to get its `float`.

```python
# exercise_5.py
import asyncio

PRICES = {"apple": 1.5, "pear": 2.0}

def price_of(item: str) -> float:
    return PRICES[item]

def total_price(items: list[str]) -> float:
    return sum(price_of(item) for item in items)

async def price_of_async(item: str) -> float:
    await asyncio.sleep(0)
    return PRICES[item]

async def total_price_async(items: list[str]) -> float:
    return sum(
        [await price_of_async(item) for item in items])

basket = ["apple", "pear"]
print(total_price(basket))
#: 3.5
print(asyncio.run(total_price_async(basket)))
#: 3.5
description = price_of_async("apple")
print(type(description).__name__)  # [1]
#: coroutine
description.close()  # Never awaited, so close it explicitly
```

If you leave out the `await` in the list comprehension,
`sum()` receives a list of coroutines rather than prices.
`ty` reports `no-matching-overload` at the `sum()` call.
The `asyncio.run()` call raises a `TypeError` for adding an `int` and a `coroutine`,
with a `RuntimeWarning` that `price_of_async` was never awaited.

Making the helper `async` forces four changes.

**Await the helper from a coroutine.**
`price_of_async("apple")` now returns a coroutine instead of a `float`,
as `[1]` shows, so `total_price()` must await each call before it can sum the results.
Only an `async def` may contain `await`,
so `total_price()` becomes `total_price_async()`.

**Collect the results before summing.**
The argument to `sum()` gains brackets,
because a generator expression with an `await` inside it is an asynchronous generator,
and `sum()` requires a synchronous iterable.
Without the brackets, `ty` reports `no-matching-overload`,
and the `sum()` call raises a `TypeError`.

**Run the coroutine at the edge.**
The callers of `total_price_async()` must then become `async` in turn,
and the propagation continues up to `asyncio.run()`,
the boundary that discharges the Effect.

That propagation is Effect tracking.
The Effect appears in the type.
`ty` reports the return type of `price_of_async()` as `CoroutineType[Any, Any, float]`,
not `float`.
If a caller forgets `await`,
the type checker reports the coroutine where the caller expected a `float`.
Each caller in turn must become `async`,
as the chapter says an Effect propagates.
The chain ends at the edge of the program,
where one `asyncio.run()` call runs the coroutine.
`async` satisfies property 1 of the three-item list without anyone calling it an Effect system.

`async` satisfies neither of the other two.

`async` does not **separate the interface from the implementation**.
`await price_of_async(item)` names an implementation, not an interface.
It says "run this particular coroutine."
The coroutine's body defines what awaiting it does.
Compare `Ask` in `ask_tell.py`,
where `greet()` specifies the interface and leaves the implementation to the caller.
`async` has no equivalent of writing a function against "something awaitable that yields a price" and choosing the implementation later.

`async` does not **bind the implementation later**.
`asyncio.run()` chooses an event loop.
That choice sounds like late binding until you ask what it lets you swap.
A different loop runs the same awaits on a different schedule.
You settle what those awaits mean when you write the coroutine,
so a test that needs fake prices must inject `price_of_async` through every signature,
the threading this chapter's exercise 2 measures.
The event loop is a scheduler, not a handler.

So `async` is an Effect-tracking system rather than a full EMS,
in the same sense as most of the AI languages in [Custom AI Languages with Effects](../../Chapters/44_Effects--Effect_Management.md#custom-ai-languages-with-effects).
It tracks one Effect, chosen by the language,
with the implementation set at the call site.
Setting the implementation there also explains why the propagation feels like a nuisance rather than a benefit.
You do the bookkeeping of Effect tracking,
an `await` and an `async def` in every caller,
without the delayed binding that makes that bookkeeping useful.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
