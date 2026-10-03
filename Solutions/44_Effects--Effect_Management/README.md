# Effect Management: Solutions

## 1. Production bindings for `ask_tell.py`

> Write the production bindings for `ask_tell.py`:
> a `Console` class whose `ask()` calls `input()` and whose `tell()` calls `print()`,
> and run `greet(Console(), Console())` interactively.
> Confirm `greet()` requires no change:
> serving a new context without edits is what delayed binding provides.

<details>
<summary>Where to look</summary>

[Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand) shows `greet()` taking its `ask` and `tell` capabilities as parameters.
The `Ask` and `Tell` protocols are structural, so `Console` needs only methods with matching signatures.
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

An interactive run of `greet(Console(), Console())` looks like
this:

```text
What is your name? Alice
Hello, Alice!
```

`exercise_1.py` binds the real `Console` for `tell` and keeps the
scripted `ask`, because a book listing that calls `input()` runs with
no terminal attached. The substitution is the point either way: one
`Console` instance satisfies both protocols, so you can pass the same
object for both parameters. You can also replace either parameter with
a double, and the other one is unaffected.

**Declare what the function needs.** `greet()` requires no change, and could not have required one. It
names two capabilities it needs and calls methods on them. Its body
names none of `Console`, `input()`, `print()`, or `Scripted`, so
changing the binding affects nothing there. That is the delayed-binding
payoff: the choice of implementation moves to the call site, where a
test can choose differently from production.

**Satisfy the protocols structurally.** The type checker still enforces the protocols after the choice moves.
`Console` inherits from nothing and declares no relationship to `Ask`
or `Tell`, but it has the two methods with the right signatures, so it
satisfies both protocols structurally. If you give `Console` a
`tell()` that returns a `str`, `ty` reports `invalid-argument-type`
at the `greet(...)` call, not at the class definition, because the
class does not declare which protocol it means to satisfy.

</details>
</details>
</details>

## 2. Threading a `Log` Effect through by hand

> Do the bookkeeping the chapter describes.
> Starting from `bookkeeping_scales.py`, add a `Log` Effect
> (a protocol with `log(message)`) used by a new helper that `greet()` calls,
> and log from `greet()` too.
> The chapter counts five signatures for that version;
> say how many of the five use the `Log` they name,
> and then what an EMS would do instead.

<details>
<summary>Where to look</summary>

[Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand) shows the bookkeeping that each new Effect adds to every signature on the path.
Add a `Log` protocol, give the new helper and `greet()` a `log` parameter, and count which functions only pass it along.
Compare that count with what [Tracking and Management](../../Chapters/44_Effects--Effect_Management.md#tracking-and-management) says an EMS declares instead.

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

Five signatures name the new Effect, and only two of them use it.

**Log at the point of use.** One of the five is new rather than edited: `format_greeting()`, the
helper that uses the `Log`. You must edit four existing signatures.
`greet()` both uses a `Log` and accepts one, to hand down to
`format_greeting()`.

**Hand the Effect down the call chain.** `session()`, `menu()`, and `main()` each
gain a `log` parameter that they only hand to the next function.
Three of the five name a `Log` they do not use. Those functions
sit between the Effect's user and the call site that binds it, and
they pay for an Effect whose sole use in their bodies is forwarding
it. Their signatures now describe a capability they do not exercise,
so a reader of `menu()` learns something false about what `menu()`
does.

The cost also scales the wrong way. Adding a fourth Effect later means
walking the same chain again, and the chain is longer in a real
program than in this one. The alternative most codebases pick, a
module-level logger, removes the parameter by removing the choice: the
function no longer says it logs, and a test can no longer bind the
logger differently.

An Effect Management System collapses the parameter lists and the call
sites, not the signatures. `format_greeting()` declares in its return
type that it needs a `Log`, and so does every function on the path to
it, but none of them gains an unused parameter, no call site
changes, and the type checker names each declaration you miss. You
still supply the binding, but at one place near the top, where the
program decides what a `Log` means.
[Stateless](../../Chapters/46_Effects--Stateless.md) shows that shape with
a real library: in its `audit_log.py`, `greet_logged()` and its caller
`greet_all()` both carry a `Need[Log]` in the `Depend` return type,
while `greet()` stays unchanged.

</details>
</details>
</details>

## 3. Classifying three Effects

> Classify every Effect in `slope_catch.py`,
> `withdraw()` from [Foundations](../../Chapters/40_Functional--Foundations.md#pure-functions),
> and the `Thermometer` that keeps a `_celsius` from [*Observer*](../../Chapters/30_Patterns--Observer.md#the-pythonic-observer):
> side effect, side cause, or exception.
> Which of the three conversions from [Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure)
> applies to the exceptions,
> and which technique from [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
> applies to the rest?

<details>
<summary>Where to look</summary>

[Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure) covers the exception Effects, and [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand) covers the rest.
For each piece of code, ask whether it writes something outside its result (a side effect), reads something that can change (a side cause), or signals failure with an exception.
Then match each kind to the conversion or technique that manages it.

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

Neither function in `slope_catch.py` has a side effect or a side
cause. Both read only their arguments and change nothing outside
themselves. The two Effects are both exceptions, and the chapter
demonstrates both conversions the table names for them: `slope()`
catches the `ZeroDivisionError`, and `slope_nonzero.py` shows
the version where a restrictive type makes a zero `run` unconstructable.
The third conversion, a `Result`, applies to both exceptions as well:
`slope_result.py` returns the `ZeroDivisionError` as an `Err`, and
`@safe` on `slope_catch.py`'s `slope()` does the same for the `ValueError`.
The `ValueError` from `validate()` is the one still escaping, and
exercise 4 moves it out of `slope()`.

`withdraw()` is both a side cause and a side effect in three lines. `balance -= amount` reads
the global and writes it back, so the function's result depends on the
global `balance` rather than on its arguments, and the call changes
`balance` where no caller can see it. Reading and rewriting the global
is why `withdraw(30)` twice returns `70` then `40`, the demonstration
the [Foundations](../../Chapters/40_Functional--Foundations.md#pure-functions)
chapter uses to show purity failing;
[Confidence](../../Chapters/43_Functional--Confidence.md#referential-transparency)
reuses `withdraw()` to show referential transparency failing. The three
conversions in [Converting Effectful to Pure](../../Chapters/44_Effects--Effect_Management.md#converting-effectful-to-pure)
all manage the exception Effect, so none of them applies here. The
by-hand technique for a side cause and a side effect comes from
[Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand) instead:
pass in what the function would otherwise read or write.
For `withdraw()`, that means taking the balance as a parameter and returning the new one. The same
inputs then give the same answer, and the caller
holds the state.

`Thermometer` has the same pair inside a design pattern.
The `celsius` setter writes `_celsius`, an instance attribute rather
than a global, and then calls `announce()`, which invokes arbitrary code
in every subscribed responder. The write is a side effect on the
object. The notification is a side effect on the world, since a
responder may print, record, or fail. Reading `celsius` is a side cause
for the same reason `withdraw()` reading `balance` is one: the value
can change between calls, so the answer depends on history rather than
arguments. The functional conversion returns each reading as a value
from the temperature source, and the caller folds new readings into
whatever state it keeps. That is what the chapter calls
[pushing the Effects to the edges](../../Chapters/44_Effects--Effect_Management.md#a-program-can-never-be-pure).

Across `withdraw()` and `Thermometer`, the classification is not a
property of the language feature used. A global, an instance
attribute, and a responder list are three storage mechanisms for one
idea: something outside the call participates in the result.

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

[Make the Bad Value Impossible](../../Chapters/44_Effects--Effect_Management.md#make-the-bad-value-impossible) builds `NonZero`, whose `__post_init__()` rejects an invalid value.
Write `PositiveInt` with a `__post_init__()` that checks one predicate covering both bad values.
Then give `slope()` a `PositiveInt` parameter and see which guards have nothing left to do.

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
<summary>Solution</summary>

If you keep `NonZero`'s `self.value == 0` test under the new name,
`PositiveInt(-1)` constructs without complaint,
and `slope(10, PositiveInt(-1))` returns `-10.0`.
The demo's `expect()` loop then raises an `AssertionError` ("no exception raised") on `-1`,
and the type checker reports nothing, because every argument has the right type.
The solution's `__post_init__()` tests `value <= 0` instead, which rejects both bad values.

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

**Cover both bad values with one predicate.** The original `slope_catch.py` splits the guarding in a way that is
easy to miss. `validate()` rejects negatives but lets zero through,
and the `try` catches zero but says nothing about negatives. Two
mechanisms in two places cover the two bad values, and neither one
tells you the other exists. `NonZero` inherits half of that split.
One predicate, `value <= 0`, covers both, because "positive" is a
single idea and "not zero, and also not negative" is the same idea
described as two exceptions.

**Trust the parameter's type.** Both checks disappear from `slope()`, and so does everything they
brought with them. A `PositiveInt` cannot hold zero, so the
`try`/`except ZeroDivisionError` goes. It cannot hold a negative
either, so the call to `validate()` goes, and `validate()` along with
it. Only the division remains.

**Fail at the construction site.** The cost moves rather than vanishing. `PositiveInt(bad)` still raises
an exception, at the boundary where an untrusted number enters the
program, and a caller reading from a file or a form must still
handle it. The count changes: one construction site instead of every
function that touches the value. Every function downstream of a
`PositiveInt` is pure with respect to this failure, and none of them
spends a line of code on it. Each signature says which values the
function accepts, instead of leaving that to a docstring.

</details>
</details>
</details>

## 5. What `async` tracks, and what it does not

> `coroutines_are_descriptions.py` shows that `async` tracks one Effect.
> Write a synchronous `total_price()` that calls a helper,
> then make the helper `async` and follow what the type checker and the interpreter force you to change,
> all the way up to `asyncio.run()`.
> Name the two properties of a full EMS that `async` does *not* have,
> using the three-item list in [Tracking and Management](../../Chapters/44_Effects--Effect_Management.md#tracking-and-management).

<details>
<summary>Where to look</summary>

[Effect Management for Python?](../../Chapters/44_Effects--Effect_Management.md#effect-management-for-python) shows that calling an `async` function returns a coroutine, a description of work.
Make the helper `async`, then change each caller to `async` with `await` until `asyncio.run()` ends the chain.
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
<summary>Solution</summary>

If you leave out the `await` in the list comprehension,
`sum()` receives a list of coroutines rather than prices.
`ty` reports `no-matching-overload` at the `sum()` call,
and the `asyncio.run()` call raises a `TypeError` for adding an `int` and a `coroutine`,
with a `RuntimeWarning` that `price_of_async` was never awaited.
Calling an `async` function builds a coroutine and runs none of its body,
so the solution awaits each call to get its `float`.

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
print(type(description).__name__)
#: coroutine
description.close()  # Never awaited, so close it explicitly
```

Making the helper `async` forces four changes, and none of them is
optional.

**Await the helper from a coroutine.** `price_of_async("apple")` now returns a coroutine instead of
a `float`, as the last `print()` shows, so `total_price()` cannot sum
the results until each call has an `await`. Only an `async def` may
contain `await`, so `total_price()` becomes `total_price_async()`.

**Collect the results before summing.** The argument to `sum()` gains brackets. A generator expression with
an `await` inside it is an asynchronous generator, which `sum()`
cannot iterate: `ty` reports `no-matching-overload`, and the call
raises a `TypeError`. The list comprehension awaits each price and
hands `sum()` a list.

**Run the coroutine at the edge.** The callers of `total_price_async()` then must
become `async` in turn, and the propagation stops only at `asyncio.run()`,
the boundary that discharges the Effect.

That propagation is Effect tracking.
The Effect appears in the type: `ty` reports `price_of_async`'s return
as `CoroutineType[Any, Any, float]`, not `float`. A caller that
forgets `await` then gets a type error rather than a mysterious value.
The Effect travels outward one caller at a time, as the chapter says
an Effect propagates, and you cannot leave a caller out. It reaches
the edge of the program, where a single call runs it. `async` satisfies property 1 of the three-item
list without anyone calling it an Effect system.

It satisfies neither of the other two.

It does not **separate the interface from the implementation**.
`await price_of_async(item)` names no capability. It says "run this
particular coroutine," and the coroutine's body decides what awaiting
means. Compare `Ask` in `ask_tell.py`, where `greet()` names the
capability and stays silent about the implementation's source. `async`
has no equivalent of writing a function against "something awaitable
that yields a price" and choosing the implementation later.

It does not **bind the implementation later**. `asyncio.run()` chooses
an event loop, and that choice sounds like late binding until you ask
what it lets you swap. Choosing a loop does not let a test substitute
a different meaning for the awaits inside: you settle what those
awaits mean when you write the coroutine. A test that needs fake
prices must still inject `price_of_async`, by the same
hand-threading this chapter's exercise 2 measures. The event loop is a
scheduler, not a handler.

So `async` is an Effect-tracking system rather than a full EMS, in the
same sense as most of the AI languages in
[Custom AI Languages with Effects](../../Chapters/44_Effects--Effect_Management.md#custom-ai-languages-with-effects).
It tracks one fixed Effect, chosen by the language, with the
implementation set at the call site. That is also why the
propagation feels like a nuisance rather than a benefit: you
get the bookkeeping cost of Effect tracking without the delayed
binding that would repay it.

</details>
</details>
</details>
