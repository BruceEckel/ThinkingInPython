# Generators: Solutions

## 1. `tally()`, driven with `next()` and `send()`

> Write `tally()`, a generator that yields a prompt string,
> receives an `int` for each prompt, and returns the total once it has three.
> Give it the full three-parameter annotation,
> then drive it with `next()` and `send()` and read the total off `StopIteration`.

<details>
<summary>Where to look</summary>

[Annotating a Generator](../../Chapters/45_Effects--Generators.md#annotating-a-generator)
describes the three parameters of `Generator`: what it yields, what it receives,
and what it returns.
Give each channel its own type so that a swap is a type error.
After the third `send()`, the generator finishes.
The total is the `value` of the `StopIteration` that `send()` raises.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Generator
from typing import NewType

Prompt = NewType("Prompt", str)
Amount = NewType("Amount", int)
Total = NewType("Total", int)

def tally() -> Generator[Prompt, Amount, Total]:
    ...
```

<details>
<summary>Done when</summary>

your script prints the three prompts and then the sum of your three sent amounts,
read from the `StopIteration`'s `value`, and `uv run ty check` passes.
If you swap the second and third type parameters of your annotation,
the type checker reports errors on your `send()` calls.

<details>
<summary>Solution</summary>

If you read the total as the result of the last `send()`,
writing `total: Total = t.send(Amount(12))` with no `try`,
the script prints the three prompts and then stops with `StopIteration: 42`.
The type checker rejects that line before it runs.
`send()` returns the `YieldType`,
so `ty` reports an `invalid-assignment` of a `Prompt` to a `Total`.
A generator's return value arrives only on its `StopIteration`,
so the solution catches that exception and reads its `value`.

```python
# exercise_1.py
from collections.abc import Generator
from typing import NewType

Prompt = NewType("Prompt", str)
Amount = NewType("Amount", int)
Total = NewType("Total", int)

def tally() -> Generator[Prompt, Amount, Total]:
    total = 0
    for n in (1, 2, 3):
        amount: Amount = yield Prompt(f"amount {n} of 3")
        total += amount
    return Total(total)

t = tally()
print(next(t))
#: amount 1 of 3
print(t.send(Amount(10)))
#: amount 2 of 3
print(t.send(Amount(20)))
#: amount 3 of 3
try:
    t.send(Amount(12))
except StopIteration as stop:
    total: Total = stop.value
print(total)
#: 42
```

**Keep the three channels apart.**
Three `NewType` definitions over `str`, `int`,
and `int` keep the two integer channels apart,
so transposing the `SendType` and the `ReturnType` is a type checker error.
With bare `int` on both channels, the checker accepts the swap.

**Drive the conversation with `next()` and `send()`.**
The third `send()` resumes the last `yield`,
so the loop ends and `tally()` returns.

`total` is a local of the generator,
and it keeps its value across three suspensions because the suspended generator preserves its locals.
Those locals are the state.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A driver that answers from an iterator

> `drive()` answers from a `dict`.
> Write a second driver that answers from an `Iterator[Answer]`, in order,
> and run `interview()` under both.
> Explain what, if anything, needed to change in `interview()`, and why.
> Give your driver fewer answers than questions and say what it returns.
> `StopIteration` now means two different things in the same loop.
> Keep them apart.

<details>
<summary>Where to look</summary>

[A Generator Waits for Its Driver](../../Chapters/45_Effects--Generators.md#a-generator-is-a-description)
explains why `interview()` accepts answers from any driver.
Write the new driver as a loop that fetches the next answer,
then calls `send()`.
Both the answer iterator and the generator signal the end with `StopIteration`,
so choose carefully which call sits inside the `try`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Generator, Iterator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    ...

def drive_from_dict(
        conversation: Generator[Question, Answer, Result],
        answers: dict[Question, Answer]) -> Result:
    ...

def drive_naive(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    ...

def drive_in_order(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    ...
```

<details>
<summary>Done when</summary>

`interview()` runs the same under both drivers,
and each driver returns `Alice of Wonderland, friend Rabbit` from the chapter's three answers.
Given one answer for three questions,
your iterator driver lets the answers' `StopIteration` reach the caller instead of returning `None`.

<details>
<summary>Solution</summary>

If you put `next(answers)` inside the `try`, as `drive_naive()` does,
a short answer source ends the run quietly.
Given one answer for three questions, `drive_naive()` returns `None`.
The type checker accepts `drive_naive()`.
The `except StopIteration` meant for the conversation catches the one from the exhausted answers and treats it as a finished interview.
The solution's `drive_in_order()` fetches each reply outside the `try`,
so the `StopIteration` from the answers reaches the caller.

```python
# exercise_2.py
from collections.abc import Generator, Iterator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield Question("name")
    town: Answer = yield Question("town")
    friend: Answer = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")

def drive_from_dict(
        conversation: Generator[Question, Answer, Result],
        answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value

def drive_naive(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    request = next(conversation)
    while True:
        try:  # next() and send() share one except clause
            reply = next(answers)
            print(f"{request = }, {reply = }")
            request = conversation.send(reply)
        except StopIteration as stop:
            return stop.value

def drive_in_order(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    request = next(conversation)
    while True:
        # Fetched outside the try on purpose
        reply = next(answers)
        print(f"{request = }, {reply = }")
        try:
            request = conversation.send(reply)
        except StopIteration as stop:
            return stop.value

by_name = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}
print(drive_from_dict(interview(), by_name))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
in_order = iter([Answer("Alice"), Answer("Wonderland"),
                 Answer("Rabbit")])
print(drive_in_order(interview(), in_order))
#: request = 'name', reply = 'Alice'
#: request = 'town', reply = 'Wonderland'
#: request = 'friend', reply = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
# One answer, three questions:
try:
    drive_in_order(interview(), iter([Answer("Alice")]))
except StopIteration:
    print("answer source ran out")
#: request = 'name', reply = 'Alice'
#: answer source ran out
print(repr(drive_naive(interview(),
                       iter([Answer("Alice")]))))
#: request = 'name', reply = 'Alice'
#: None
```

**Reuse the generator unchanged.**
`interview()` stays as it was,
because it yields a `Question` and receives an `Answer`,
whatever the answer's source.
The generator describes the conversation.
The driver interprets it.
Swapping one interpreter for another leaves the description untouched.

**Find the answer for each request.**
The two drivers differ in the property on which they rely.
The dictionary driver looks each answer up by the request,
so it answers correctly in whatever order the questions arrive,
and it answers a repeated question the same way twice.
The iterator driver goes by position,
so it depends on the generator asking its questions in the order the driver holds the replies.
The `conversation` type the two drivers share declares that a `Question` goes out and an `Answer` comes back,
and leaves open how the driver chooses each answer.

**Keep the two endings apart.**
In `drive_in_order()`, `next(answers)` sits outside the `try`,
as its comment says,
because the `except StopIteration` meant for the conversation otherwise catches a `StopIteration` raised by an exhausted answer list.
Two iterators that raise the same exception type are a hazard for a driver that holds both.

**Test a short answer source.**
The last two runs show that hazard.

`None` is wrong twice over.
The interview stopped after one question, before it built a `Result`,
and `None` is not a `Result` in any case.

The type checker accepts `return stop.value` as a declared `Result`,
because `StopIteration.value` has type `Any`.
The runtime raises no exception either.
The program first fails later,
when code that expects a string receives that `None`,
far from the driver that returned it.

Keeping the two meanings apart is a one-line discipline:
put inside the `try` only the call whose `StopIteration` you mean to interpret.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A third delegation in `yield_from_send.py`

> Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()`,
> adding its sum to the total, and extending the loop to `[1, 2, 3, 4, 5, 6]`.
> Write down the sequence of printed lines before running it.

<details>
<summary>Where to look</summary>

[The Send Channel](../../Chapters/45_Effects--Generators.md#the-send-channel)
follows each sent value to the delegated generator suspended at that moment.
Count how many values one `collect()` consumes,
then count how many the loop supplies in total.
Write the printed lines before you run the script,
and note which sends produce one line and which produce two.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int, int]:
    ...

def both() -> Generator[str, int]:
    ...
```

<details>
<summary>Done when</summary>

you wrote the full sequence of lines before running the modified `yield_from_send.py`,
and it matches the run line for line,
including which sends print two lines and what `send(6)` prints.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int, int]:
    first: int = yield f"{name} needs a value"
    second: int = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")
    return first + second

def both() -> Generator[str, int]:
    alpha: int = yield from collect("alpha")
    beta: int = yield from collect("beta")
    gamma: int = yield from collect("gamma")
    yield f"total {alpha + beta + gamma}"

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4, 5, 6]:
    print(f"send({value}) -> {g.send(value)}")
#: send(1) -> alpha needs another
#: alpha got 1 and 2
#: send(2) -> beta needs a value
#: send(3) -> beta needs another
#: beta got 3 and 4
#: send(4) -> gamma needs a value
#: send(5) -> gamma needs another
#: gamma got 5 and 6
#: send(6) -> total 21
```

**Count the values the collectors need.**
Each `collect()` consumes two values, so the three collectors need six,
and the loop supplies six.
The `yield` in `both()` gives `send(6)` a value to return,
so the loop ends with `both()` suspended and no `StopIteration`.

**Read the output in pairs.**
The two-line responses mark where one collector ends and the next begins.
A send that supplies a collector's first value produces one line:
that collector's second prompt.
A send that supplies a collector's second value produces two:
the completed collector's `print()`, then the next prompt.

`yield from` relays in both directions on its own: prompts up to the driver,
numbers down to whichever `yield` is suspended inside the current `collect()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Removing the `yield from`

> Remove `yield from` in `yield_from_nested.py`,
> leaving `profile: Result = interview()`.
> Run `ty check` and the script, and explain both results.
> Which one told you more,
> and what does the type checker say once you remove `profile`'s annotation?

<details>
<summary>Where to look</summary>

[Composing Is Not Interpreting](../../Chapters/45_Effects--Generators.md#composing-is-not-interpreting)
shows `survey()` delegating to `interview()` with `yield from`.
Without `yield from`, the call to `interview()` builds a generator object,
and that object sits suspended before its first line.
Compare the declared type of `profile` with what the call produces,
then compare the type checker's report with the script's output.

<details>
<summary>Done when</summary>

your explanation accounts for both results:
`ty` reports an `invalid-assignment` on the `profile` line,
and the script runs and prints `<generator object interview at ...>, color blue`.
It says which result locates the mistake and why,
and you have confirmed that `ty check` passes once the annotation is gone.

<details>
<summary>Solution</summary>

```python
def survey() -> Generator[Question, Answer, Result]:
    profile: Result = interview()
    color: Answer = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")
```

`ty` rejects it:

```text
error[invalid-assignment]: Object of type
`Generator[Question, Answer, Result]` is not assignable to `Result`
 --> yield_from_nested.py:8:23
  |
8 |     profile: Result = interview()
  |              ------   ^^^^^^^^^^^ Incompatible value of type
  |              |        `Generator[Question, Answer, Result]`
  |              Declared type
```

The script still runs, and produces:

```text
request = 'color', answer = 'blue'
  ask() received blue
<generator object interview at 0x000001C5FB3FDE40>, color blue
```

Both results describe the same mistake.
Calling a generator function produces a description rather than a conversation.
The call `interview()` returns a generator object,
suspended before the first line of its body.
The generator stays suspended for the rest of the run,
so it asks none of its three questions.
The `return` statement in `survey()` interpolates the object's repr into the sentence where the interview's `Result` belonged.

The type checker told you more.
Its message names the two types and points at the assignment that mismatches them.
That assignment is the defect.
The runtime output shows a consequence two lines later,
in the `return` statement, where the f-string formats the object.
A reader must work backward from a `<generator object ...>` in a report to the missing `yield from`.
Worse, the failure is quiet: no exception, an exit code of zero,
and output that a log scraper accepts.
A coroutine that nothing awaits draws a `RuntimeWarning` when Python reclaims it,
as [Concurrency](../../Chapters/19_Techniques--Concurrency.md#asyncio-mechanics)
shows.
Python reclaims a generator that nothing drives, silently.

Once you remove the annotation, the type checker accepts `survey()`.
For `profile = interview()` it infers the expression's own type,
`Generator[Question, Answer, Result]`,
and no declared type contradicts that inference.
The f-string then accepts any object, since formatting one calls `str()` on it.
A generator object's `str()` is its repr, so the output shows the repr.
The annotation alone gives the checker a declared type to compare with the call's type.
So annotate a local whenever you want the checker to verify the type of the call that produces its value.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. `report()` with a return value

> `report()` in `yield_from_return.py` yields its lines and returns `None`.
> Rewrite it to return the character count as well,
> and give it the full annotation.
> Then write a caller that delegates to it with `yield from` and yields that count in a line of its own,
> and say which type parameter carries each of the two values.

<details>
<summary>Where to look</summary>

[The Return Channel](../../Chapters/45_Effects--Generators.md#the-return-channel)
shows how `yield from` delivers a delegate's return value to the delegating generator.
`Iterator[str]` cannot declare a return value,
so `report()` needs the full `Generator` annotation.
The caller binds the count with `yield from`,
then yields it as a string of its own.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Generator

def emit(items: list[str]) -> Generator[str, None, int]:
    ...

def report(items: list[str]) -> Generator[str, None, int]:
    ...

def summarize(items: list[str]) -> Generator[str]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes,
and your caller's output for the chapter's `["red", "green", "blue"]` ends with a line carrying `12`.
Changing `report()`'s annotation back to `Iterator[str]` makes `ty` report `invalid-return-type`,
and you can name the type parameter through which each of your two values travels.

<details>
<summary>Solution</summary>

The solution returns the count from `report()`,
so the count reaches `summarize()` through a second return:

```python
# exercise_5.py
from collections.abc import Generator

def emit(items: list[str]) -> Generator[str, None, int]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Generator[str, None, int]:
    size: int = yield from emit(items)
    yield f"({size} characters)"
    return size

def summarize(items: list[str]) -> Generator[str]:
    counted: int = yield from report(items)
    yield f"total: {counted}"

print(list(summarize(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)', 'total: 12']
```

**Declare the return channel.**
`report()`'s annotation changes from `Iterator[str]` to `Generator[str, None, int]`,
because a generator that returns something needs the long form.
Under `Iterator[str]` a generator must return `None`,
so `ty` rejects `report()`'s `return size` with an `invalid-return-type`:
expected `None`, found `int`.

If you change `report()`'s annotation but leave out `return size`,
the script still runs, and the printed list ends with `'total: None'`.
`report()` returns `None`,
and the `yield from` in `summarize()` delivers that `None` into `counted`.
`ty` reports an `invalid-return-type` on the annotation,
because `report()` declares an `int` and, with no `return` statement,
returns `None`.

**Keep the strings and the count apart.**
The strings and the count travel by different channels.
Every string that `emit()` or `report()` yields travels through the `YieldType` and comes out in the list.
The count travels through the `ReturnType`: `emit()` returns it,
`yield from` delivers it into `report()`'s `size`, `report()` returns it again,
and the second `yield from` delivers it into `summarize()`'s `counted`.
The `SendType` is `None` throughout,
since `list()` drives the chain with `next()`,
the runtime equivalent of `send(None)`.

The count `12` therefore reaches `summarize()` through two returns.
`'(12 characters)'` takes the other route: `report()` yields it,
the `yield from` in `summarize()` relays it, and the driver receives it.
No generator binds it to a name.
A generator can yield a number or return it.
The choice decides which code receives the number:
a yielded value goes to the driver,
and a returned value goes to the delegating generator.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Why a driver primes with `next()`

> Explain why a driver must prime with `next()` rather than `send(None)`,
> given that the two are equivalent at runtime.
> `send_none_is_next.py` has the answer.
> State it in terms of the `SendType`.

<details>
<summary>Where to look</summary>

[Annotating a Generator](../../Chapters/45_Effects--Generators.md#annotating-a-generator)
defines the `SendType`,
and `send_none_is_next.py` calls `send(None)` on a generator whose `SendType` is `Answer`.
Read the signature of `send()` and ask what it accepts for `interview()`.
Then ask what `next()` accepts,
and where a generator that has yet to run would put a sent value.

<details>
<summary>Done when</summary>

your explanation predicts what `ty` reports if you delete the `# type: ignore` in `send_none_is_next.py`
(an `invalid-argument-type` on `None`),
states the parameter type of `send()` in terms of the `SendType`,
and says why priming with `next()` type-checks for any generator.

<details>
<summary>Solution</summary>

`next(g)` and `g.send(None)` do the same thing at runtime.
The `SendType` tells them apart.

`send()`'s signature is `send(self, value: _SendT_contra, /) -> _YieldT_co`,
so its parameter type is the generator's `SendType`.
For `interview()` that is `Answer`, and `None` is not an `Answer`,
so the priming call is a type error.
`send_none_is_next.py` carries a `# type: ignore` to suppress it.
Removing that comment draws:

```text
error[invalid-argument-type]: Argument to bound method
`Generator.send` is incorrect
 --> send_none_is_next.py:4:27
  |
4 | print(f"{interview().send(None) = }")
  |                           ^^^^ Expected `Answer`, found `None`
```

`next()` takes the generator and an optional default to return at exhaustion,
and has no parameter for a value to send.
It asks for the generator's next yielded value and ignores the `SendType`,
so priming with it type-checks for any generator.

The mismatch is real rather than a type checker limitation.
A generator's `SendType` describes what a suspended `yield` expression can receive.
A just-started generator has no suspended `yield`,
so nothing receives the value handed to the first `send()`.
The runtime enforces the same rule.
Sending a non-`None` value to a fresh generator raises `TypeError: can't send non-None value to a just-started generator`.
So at runtime the first `send()` accepts `None` alone,
a value the `SendType` excludes.

An annotation cannot express "`None` for the first call, `Answer` afterward,"
because a single `SendType` covers every call.
Widening the `SendType` to `Answer | None` states the exception in the type,
but the type checker then applies `Answer | None` to every `yield` expression.
The generator must handle a `None` at each `yield` whose value it uses as an `Answer`.
That `None` exists only in the type,
because the priming `None` arrives before the generator reaches its first `yield`.
`interview()` puts what it receives into an f-string,
which formats a `None` as readily as an `Answer`,
so `interview()` passes the check either way.
Priming with `next()` keeps the `SendType` at `Answer`.
The one call that cannot carry a value comes from the one function that cannot pass one.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. A vending machine as a single generator

> [A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine)
> keeps its current state in an attribute and looks up each transition in a table.
> Write a simplified version as a single generator instead.
> It collects money, takes two digits, then dispenses or refuses.
> It yields its current state and receives each event with `send()`,
> so the position in the generator's body carries the state.
> This generator's `yield` runs the opposite direction from `interview()`'s `yield`.
> Here `yield` reports the state the machine reached instead of requesting something the machine needs.
> Say which of the two versions you would rather extend with another state,
> and why.

<details>
<summary>Where to look</summary>

[A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine)
holds its state in an attribute and a transition table.
Here the position inside the generator's body is the state,
so use loops and `isinstance()` checks on the event that `yield` returns.
Because `yield` reports the state reached,
the driver's `send()` delivers events rather than answers.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from collections.abc import Generator
from typing import Final, Literal
from record import record

@record
class Coin:
    cents: int

@record
class Digit:
    value: str

type Event = Coin | Digit
type Report = Literal[
    "QUIESCENT", "COLLECTING", "SELECTING",
    "UNAVAILABLE", "NEED_MONEY", "DISPENSED"]
type Code = str

PRICES: Final[dict[Code, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[Code, int]] = {"11": 0, "12": 3}

def machine() -> Generator[Report, Event]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes, and one driven run reports `COLLECTING` after a coin,
`SELECTING` after a first digit, `UNAVAILABLE` for an item out of stock,
a refusal for too little money, and a sale once the money suffices.
A second, fresh machine starts with the full stock after the first one sells.

<details>
<summary>Solution</summary>

If you write `stock = STOCK` instead of copying with `dict(STOCK)`,
each sale changes the module-level table from which every machine starts.
After three `"12"` sales, by any mix of machines,
a fresh `machine()` answers the next `"12"` order with `UNAVAILABLE`.
The `Final` annotation forbids rebinding the name and permits changing the dictionary,
so the type checker passes the shared version.
The solution copies `STOCK` into a local, so each generator holds its own stock.

```python
# exercise_7.py
from collections.abc import Generator
from typing import Final, Literal
from record import record

@record
class Coin:
    cents: int

@record
class Digit:
    value: str

type Event = Coin | Digit
type Report = Literal[
    "QUIESCENT", "COLLECTING", "SELECTING",
    "UNAVAILABLE", "NEED_MONEY", "DISPENSED"]
type Code = str

PRICES: Final[dict[Code, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[Code, int]] = {"11": 0, "12": 3}

def machine() -> Generator[Report, Event]:
    stock = dict(STOCK)
    amount = 0
    event: Event = yield "QUIESCENT"
    while True:
        while isinstance(event, Coin):
            amount += event.cents
            event = yield "COLLECTING"
        row = event.value  # Not a Coin, so a first Digit
        second: Event = yield "SELECTING"
        # A coin instead of a digit
        if isinstance(second, Coin):
            amount += second.cents
            event = yield "COLLECTING"
            continue
        code = row + second.value
        if stock.get(code, 0) == 0:
            event = yield "UNAVAILABLE"
        elif amount < PRICES.get(code, 0):
            event = yield "NEED_MONEY"
        else:
            amount -= PRICES[code]
            stock[code] -= 1
            event = yield "DISPENSED"

m = machine()
print(next(m))
#: QUIESCENT
for event in [Coin(25), Digit("1"), Digit("1"), Digit("1"),
              Digit("2"), Coin(50), Digit("1"), Digit("2")]:
    print(f"{event} -> {m.send(event)}")
#: Coin(cents=25) -> COLLECTING
#: Digit(value='1') -> SELECTING
#: Digit(value='1') -> UNAVAILABLE
#: Digit(value='1') -> SELECTING
#: Digit(value='2') -> NEED_MONEY
#: Coin(cents=50) -> COLLECTING
#: Digit(value='1') -> SELECTING
#: Digit(value='2') -> DISPENSED
```

**Let position carry the state.**
The machine holds no `state` attribute and consults no table.
Where the generator pauses is the state.
A pause in the coin loop means `COLLECTING`,
and a pause after `yield "SELECTING"` means a first digit has arrived and the machine waits for a second.
`amount`, `row`, and `stock` are locals that keep their values between sends because the suspended generator preserves them.

**Report the state reached.**
The `yield` in `machine()` runs the opposite direction from the one in `interview()`.
Neither signature says so.
Both yield strings, but `interview()` yields a request the driver must satisfy,
while `machine()` yields a report the driver may ignore.
`send(Coin(25))` delivers an event and answers no question.
The `COLLECTING` it returns reports the state that event produced.
A generator's type declares what each channel carries and leaves open whether a yielded value is a request or a report.

For another state, take the table.
The generator stays compact because the states form a line,
so control flow can express the sequence.
The two states here that break the line need extra control flow.
An `if` chain reaches `UNAVAILABLE` and `NEED_MONEY`.
From each one, the machine loops back to the top,
a `goto` written as a `while True`.
Suppose you add a state reachable from several others,
the way the table handles `Quit` from every state but `QUIESCENT`.
No position in the body corresponds to that state.
The new state becomes a flag, or a check repeated at several `yield`s.
Either one breaks the correspondence between position and state,
the one thing that makes this version readable.

With the table, adding any state means one new `Enum` member and a few new rules.
Those rules sit next to the existing ones,
where you can read the whole machine at once.

The generator is the better choice for a conversation with a beginning and an end,
like `interview()`.
The table is the better choice for a machine that runs forever and can go anywhere from anywhere.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
