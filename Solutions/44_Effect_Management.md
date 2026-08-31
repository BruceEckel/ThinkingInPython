# Effect Management: Solutions

## 1. Production bindings for `ask_tell.py`

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
    "The production binding: real input, real output."
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

Run interactively as `greet(Console(), Console())`, the session looks
like this:

```text
What is your name? Alice
Hello, Alice!
```

The listing above binds the real `Console` for `tell` and keeps the
scripted `ask`, because a book listing that calls `input()` has no
terminal to read from. The substitution is the point either way: one
`Console` instance satisfies both protocols, so the same object can be
passed for both parameters, and either parameter can be swapped for a
double without the other noticing.

`greet()` required no change, and could not have required one. It
names two capabilities it needs and calls methods on them. It never
mentions `Console`, `input()`, `print()`, `Scripted`, or `Capture`, so
there is nothing in its body for a change of binding to affect. That is
the delayed-binding payoff: the decision about which implementation to
use moved to the call site, where a test can make it differently from
production.

Notice what the type checker still enforces after the decision moved.
`Console` inherits from nothing and declares no relationship to `Ask`
or `Tell`, but it has the two methods with the right signatures, so it
satisfies both protocols structurally. A `Console` whose `tell()`
returned a `str` would be rejected at the `greet(...)` call, not at the
class definition.

## 2. Threading a `Log` Effect through by hand

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

Five signatures had to change, and only two of them wanted to.
`format_greeting()` uses the new Effect. `greet()` uses it and also
has to accept it so it can pass it down. Then `session()`, `menu()`,
and `main()` each gained a `log` parameter they do nothing with except
hand to the next function.

Three of five is the number worth sitting with. The functions that pay
are the ones between the Effect's user and the place the binding is
chosen, and they pay for an Effect they never mention again. Their
signatures now describe a capability they do not exercise, so a reader
of `menu()` learns something false about what `menu()` does.

The cost also scales the wrong way. Adding a fifth Effect later means
walking the same chain again, and the chain is longer in a real
program than in this one. The alternative most codebases pick, a
module-level logger, removes the parameter by removing the choice: the
function no longer says it logs, and a test can no longer bind it
differently.

An Effect Management System collapses this to one edit. `format_greeting()`
declares in its return type that it needs a `Log`, and that requirement
propagates outward through the type system rather than through hand-edited
parameter lists: any function calling it inherits the requirement without
naming it, and the chain of intermediate functions is untouched. The
binding still has to be supplied, but at one place near the top, where
the program decides what a `Log` means. [Stateless](../Chapters/46_Stateless.md)
shows this with a real library, where the requirement rides in the type
and `Depend` is the annotation that carries it.

## 3. Classifying three Effects

| Code | Effect | Kind | Conversion |
| --- | --- | --- | --- |
| `slope_catch.py` | `validate()` raises a `ValueError` | Exception | Catch the expected exception, or make the bad value impossible |
| `slope_catch.py` | `rise / 0` raises a `ZeroDivisionError` | Exception | Catch the expected exception, or make the bad value impossible |
| `withdraw()` | writes the `balance` global | Side effect | Return a result type |
| `withdraw()` | reads the `balance` global | Side cause | Return a result type |
| `Thermometer` | `notify()` calls into every observer | Side effect | Return a result type |
| `Thermometer` | `_celsius` read by `celsius` | Side cause | Return a result type |

`slope_catch.py` has no side effects or side causes at all. It reads
only its arguments and writes nothing outside itself. Its two Effects
are both exceptions, and the chapter's other two conversions both
apply: `slope()` already catches the `ZeroDivisionError`, and
`slope_nonzero.py` shows the version where a restrictive type makes
that value unconstructable. The `ValueError` from `validate()` is the
one still escaping, which exercise 4 removes.

`withdraw()` is both a side cause and a side effect in three lines, and
that pairing is what makes it interesting. `balance -= amount` reads
the global and writes it back, so the function's result depends on
something no caller passed and its execution changes something no
caller can see. This is why `withdraw(30)` twice returns `70` then
`40`, the demonstration the [Foundations](../Chapters/40_Functional--Foundations.md#pure-functions)
chapter uses to show referential transparency failing. The conversion
is to return a result type: take the balance as a parameter and return
the new one, so the same inputs give the same answer and the caller
holds the state.

`Thermometer` is the same pair wearing a design pattern.
The `celsius` setter writes `_celsius`, an instance attribute rather
than a global, and then calls `notify()`, which invokes arbitrary code
in every registered observer. The write is a side effect on the
object. The notification is a side effect on the world, since an
observer may print, record, or fail. Reading `celsius` is a side cause
for the same reason `withdraw()` reading `balance` is one: the answer
depends on history rather than arguments. The functional conversion
turns the reading into a value returned from the temperature source and
lets the caller fold new readings into whatever state it keeps, which
is what [Functional Foundations](../Chapters/40_Functional--Foundations.md)
means by pushing effects to the edges.

Worth noticing across all three: the classification is not a property
of the language feature used. A global, an instance attribute, and an
observer list are three storage mechanisms for one idea, that something
outside the call participates in the result.

## 4. `PositiveInt` in place of both checks

```python
# exercise_4.py
from dataclasses import dataclass

@dataclass(frozen=True)
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
    try:
        PositiveInt(bad)
    except ValueError as e:
        print(e)
#: PositiveInt needs a positive value: 0
#: PositiveInt needs a positive value: -1
```

Both checks disappear from `slope()`, and so does everything they
brought with them. The `try`/`except ZeroDivisionError` is gone,
because a `PositiveInt` cannot hold zero. The call to `validate()` is
gone, and `validate()` along with it, because a `PositiveInt`
cannot hold a negative. What remains is the division, which is the
whole of what `slope()` was ever supposed to do.

The original split the guarding in a way that was easy to miss.
`validate()` rejected negatives but let zero through, and the `try`
caught zero but said nothing about negatives, so the two bad values
were handled by two mechanisms in two places and neither one told you
the other existed. `NonZero` inherited half of that split. One
predicate, `value <= 0`, covers both, which is possible only because
"positive" is a single idea and "not zero, and also not negative" was
the same idea described as two exceptions.

The cost moves rather than vanishing. `PositiveInt(bad)` still raises
an exception, at the boundary where an untrusted number enters the
program, and a caller reading from a file or a form still has to
handle it. What changed is the count: one construction site instead of
every function that touches the value. Every function downstream of a
`PositiveInt` is pure with respect to this failure without writing a
line about it, and its signature says which values it accepts instead
of leaving that to a docstring.

## 5. What `async` tracks, and what it does not

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
optional. `price_of_async("apple")` no longer returns a `float`, it
returns a coroutine, which the last `print()` shows. `total_price()`
therefore cannot sum the results, so every call needs `await`. Only an
`async def` may contain `await`, so `total_price()` becomes
`total_price_async()`. Its callers then face the same choice, and the
propagation stops only at `asyncio.run()`, which is the boundary where
the Effect is discharged.

That propagation is Effect tracking, and it is worth naming as such.
The Effect appears in the type: `ty` reports
`price_of_async`'s return as `Coroutine[Any, Any, float]`, not
`float`, and a caller that forgets `await` gets a type error rather
than a mysterious value. The Effect travels outward automatically,
exactly as the chapter says an EMS should propagate, and it reaches
the edge of the program where a single call binds it. `async` satisfies
property 1 of the three-item list without anyone calling it an Effect
system.

It satisfies neither of the other two.

It does not **separate the interface from the implementation**.
`await price_of_async(item)` names no capability. It says "run this
particular coroutine," and the coroutine's body decides what awaiting
means. Compare `Ask` in `ask_tell.py`, where `greet()` names the
capability and stays silent about how a name is obtained. `async` has
no equivalent of writing a function against "something awaitable
that yields a price" and choosing later which one.

It does not **bind the implementation later**. `asyncio.run()` chooses
an event loop, which sounds like late binding until you ask what it
lets you swap. It does not let a test substitute a different meaning
for the awaits inside. Those are fixed when the coroutine is written.
A test that wants fake prices still has to inject
`price_of_async` itself, by the same hand-threading this chapter's
exercise 2 measures. The event loop is a scheduler, not a handler.

So `async` is an Effect-tracking system rather than a full EMS, in the
same sense as most of the AI languages in
[Custom AI Languages with Effects](../Chapters/44_Effect_Management.md#custom-ai-languages-with-effects).
It tracks one fixed Effect, chosen by the language, with the
implementation welded to the call site. That is also why the
propagation is experienced as a nuisance rather than a benefit: you
get the bookkeeping cost of Effect tracking without the delayed
binding that would repay it.
