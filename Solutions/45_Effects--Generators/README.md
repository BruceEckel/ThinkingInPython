# Generators: Solutions

## 1. `tally()`, driven by hand

> Write `tally()`, a generator that yields a prompt string,
> receives an `int` for each prompt, and returns the total once it has three.
> Give it the full three-parameter annotation,
> then drive it by hand with `next()` and `send()` and read the total off `StopIteration`.

<details>
<summary>Where to look</summary>

[Annotating a Generator](../../Chapters/45_Effects--Generators.md#annotating-a-generator) names the three parameters of `Generator`: what it yields, what it receives, and what it returns.
Give each channel its own type so that a swap is a type error.
After the third `send()`, the generator finishes, and the total is the `value` of the `StopIteration` that `send()` raises.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Generator
from typing import NewType

def tally() -> Generator[Prompt, Amount, Total]:
    ...
```

<details>
<summary>Solution</summary>

If you read the total as the result of the last `send()`,
writing `total: Total = t.send(Amount(12))` with no `try`,
the script prints the three prompts and then stops with `StopIteration: 42`.
`ty` rejects that line before it runs.
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
        amount = yield Prompt(f"amount {n} of 3")
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

**Keep the three channels apart.** The three-parameter annotation
names all three channels. `Generator[Prompt, Amount, Total]` says
this generator yields a `Prompt`, receives an `Amount`, and finally
returns a `Total`. Three `NewType` definitions over `str`, `int`, and
`int` keep the two integer channels apart, so transposing the
`SendType` and the `ReturnType` is a type checker error rather than a
bug that shows up in arithmetic.

**Drive the conversation by hand.** Driving `tally()` by hand takes four calls: one `next()` and three
sends. `next(t)` runs the body up to the first `yield` and produces the
first prompt. Each `send()` resumes at that suspended `yield`, whose
value becomes `amount`, then runs to the next one. The third `send()`
finds no fourth `yield`, so the loop ends and `tally()` returns. The
return value arrives as `StopIteration`'s `value` rather than as the
result of `send()`.

`total` is the generator's own local, and it survives across three
suspensions with no storage anywhere else. The frame is the state.

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

[A Generator Is a Description](../../Chapters/45_Effects--Generators.md#a-generator-is-a-description) explains why `interview()` does not care who answers it.
Write the new driver as a loop that fetches the next answer, then calls `send()`.
Both the answer iterator and the generator signal the end with `StopIteration`, so choose carefully which call sits inside the `try`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Generator, Iterator
from typing import NewType

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
<summary>Solution</summary>

```python
# exercise_2.py
from collections.abc import Generator, Iterator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")
    town = yield Question("town")
    friend = yield Question("friend")
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
        try:  # Both next() calls share one except clause
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

**Reuse the generator unchanged.** Nothing in `interview()` changes, and nothing could have. It yields a
`Question` and receives an `Answer` without asking about the answer's
source. That is the separation the chapter teaches:
the generator describes the conversation, and the driver interprets it.
Swapping one interpreter for another leaves the description untouched.

**Find the answer for each request.** The two drivers differ in the
property on which they rely. The dictionary driver looks each answer
up by the request, so it answers correctly in whatever order the
questions arrive, and it answers a repeated question the same way
twice. The iterator driver goes by position, so it depends on the
generator asking the questions for which the driver has replies,
in that order. Both satisfy the same type. The type says what
travels, not what the driver knows.

**Keep the two endings apart.** One detail in `drive_in_order()` earns its comment. `next(answers)` sits
outside the `try` because the `except StopIteration` meant for the
conversation otherwise catches a `StopIteration` raised by an
exhausted answer list. Two different iterators raising one exception
type is a real hazard when a driver holds both.

**Test a short answer source.** The last two runs show that hazard. Given one answer and three
questions, `drive_in_order()` lets the `StopIteration` escape, so the
caller learns the answer source ran dry. `drive_naive()` differs only
in having `next(answers)` inside the `try`. It catches that same
exception, reads it as "the conversation finished," and returns
`stop.value`, which is `None`.

`None` is the wrong answer twice over. The interview did not finish, so
no `Result` exists, and `None` is not a `Result` in any case. Nothing
catches the mistake. `StopIteration.value` has type `Any`, so
`return stop.value` satisfies a declared `Result` and the checker reports
nothing. The failure is silent at the type checker and silent at
runtime. It surfaces later as a `None` where the caller expects a
string, far from the driver that produced it.

Keeping the two meanings apart is a one-line discipline: put inside the
`try` only the call whose `StopIteration` you mean to interpret.

</details>
</details>
</details>

## 3. A third delegation in `yield_from_send.py`

> Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()` and extending the loop to `[1, 2, 3, 4, 5]`.
> Write down the sequence of printed lines before running it.

<details>
<summary>Where to look</summary>

[The Send Channel](../../Chapters/45_Effects--Generators.md#the-send-channel) follows each sent value to the delegated generator suspended at that moment.
Count how many values one `collect()` consumes, then count how many the loop supplies in total.
Write the printed lines before you run the script, and note which sends produce one line and which produce two.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    ...

def both() -> Generator[str, int]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_3.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")
    yield from collect("beta")
    yield from collect("gamma")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4, 5]:
    print(g.send(value))
#: alpha needs another
#: alpha got 1 and 2
#: beta needs a value
#: beta needs another
#: beta got 3 and 4
#: gamma needs a value
#: gamma needs another
try:
    g.send(6)
except StopIteration:
    print("both() is exhausted")
#: gamma got 5 and 6
#: both() is exhausted
```

**Count the values the collectors need.** The five sends do not divide
evenly among three collectors. Each `collect()` consumes two values, so
the three collectors need six, and the loop supplies five. `gamma`
stays suspended at its second `yield` until the `send(6)` after the
loop completes it.

**Read the output in pairs.** The pairs of lines are the tell. A send that supplies a collector's
first value produces one line, the same collector's second prompt. A
send that supplies a collector's second value produces two: the
completed collector's `print()`, then the first prompt of the next
collector. The two-line sends are `send(2)`, `send(4)`, and `send(6)`,
so the output alternates between one-line and two-line responses all
the way down. The second line of `send(6)`'s pair is the exception. No
collector remains to prompt, so `gamma` finishes, `both()` raises
`StopIteration`, and the `except` prints `both() is exhausted`.

`both()` takes no part in that alternation. It contains three
`yield from` statements and no code that forwards a value. `yield from`
relays in both directions on its own: prompts up to the driver, numbers
down to whichever `yield` is currently suspended, two frames below.

</details>
</details>
</details>

## 4. Removing the `yield from`

> Remove `yield from` in `yield_from_nested.py`,
> leaving `profile: Result = interview()`.
> Run `ty check` and the script, and explain both results.
> Which one told you more,
> and what does the type checker say if `profile` carries no annotation?

<details>
<summary>Where to look</summary>

[Composing Is Not Interpreting](../../Chapters/45_Effects--Generators.md#composing-is-not-interpreting) shows `survey()` delegating to `interview()` with `yield from`.
Without it, the call builds a generator object, and nothing drives it.
Compare the declared type of `profile` with what the call produces, then compare the type checker's report with the script's output.

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
ask(question = 'color') -> answer = 'blue'
<generator object interview at 0x000001C5FB3FDE40>, color blue
```

Both results describe the same mistake: calling a generator function
produces a description rather than a conversation. `interview()` builds
a generator object and stops. Nothing calls `next()` or `send()`
on that object, so the generator asks none of its three questions. The
final line interpolates the object's repr into the sentence where an
answer belonged.

The type checker told you more. Its message names the two types and
points at the assignment that mismatches them, and that assignment is
the defect. The runtime output shows a consequence three steps
downstream, at the one place the f-string formats the object. A reader
must work backward from a `<generator object ...>` in a report to the
missing `yield from`. Worse, the failure is quiet: no exception, an
exit code of zero, and output that a log scraper would happily accept.

Without the annotation, the type checker says nothing. For
`profile = interview()` it infers the expression's own type,
`Generator[Question, Answer, Result]`, and no declared type contradicts
that inference. The f-string then accepts any object, since formatting
one calls `str()` on it, and a generator object's `str()` is its repr.
The annotation does the whole of the work here. That is the argument
for annotating a local whose value comes from a call whose return type
you want to pin down.

</details>
</details>

## 5. `report()` with a return value

> `report()` in `yield_from_return.py` yields but returns nothing.
> Rewrite it to return the character count as well,
> and give it the full annotation.
> Then write a caller that delegates to it with `yield from` and yields that count in a line of its own,
> and say which type parameter carries each of the two values.

<details>
<summary>Where to look</summary>

[The Return Channel](../../Chapters/45_Effects--Generators.md#the-return-channel) shows how `yield from` delivers a delegate's return value to the delegating generator.
`Iterator[str]` cannot declare a return value, so `report()` needs the full `Generator` annotation.
The caller binds the count with `yield from`, then yields it as a string of its own.

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
<summary>Solution</summary>

If you change `report()`'s annotation but leave out `return size`,
the script still runs, and the printed list ends with `'total: None'`.
`report()` returns `None`,
and the second `yield from` delivers that `None` into `counted`.
`ty` reports an `invalid-return-type` on the annotation,
because with no `return` statement `report()` always implicitly returns `None`, and its annotation declares an `int` return value.
The solution returns `size` from `report()`, so the count reaches `summarize()` through a second return.

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

**Declare the return channel.** `report()`'s annotation changes from `Iterator[str]` to
`Generator[str, None, int]`, because a generator that returns something
needs the long form. `Iterator` sets the `ReturnType` to `None`, so
`ty` rejects `report()`'s own `return size` with expected `None`, found
`int`.

**Keep the strings and the count apart.** The strings and the count travel by different channels, and the listing
shows both at once. Every string that `emit()` or `report()` yields
travels through the `YieldType` and comes out in the list. The count
travels through the `ReturnType`: `emit()` returns it, `yield from`
delivers it into `report()`'s `size`, `report()` returns it again, and
the second `yield from` delivers it into `summarize()`'s `counted`. The
`SendType` is `None` throughout, since nobody sends anything in.

`12` therefore reaches `summarize()` through two returns and is not
yielded on its own. `'(12 characters)'` takes the other route:
`report()` yields it, the `yield from` in `summarize()` relays it,
and the driver receives it. No generator binds it to a name. The same number can travel either
way, and the choice decides who can see it: a yielded value goes to the
driver, a returned value goes to the delegating generator.

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

[Annotating a Generator](../../Chapters/45_Effects--Generators.md#annotating-a-generator) defines the `SendType`, and `send_none_is_next.py` calls `send(None)` on a generator whose `SendType` is not `None`.
Read the signature of `send()` and ask what it accepts for `interview()`.
Then ask what `next()` accepts, and whether a generator that has not yet run has anywhere to put a sent value.

<details>
<summary>Solution</summary>

`next(g)` and `g.send(None)` do the same thing at runtime, and the
`SendType` is where they stop being interchangeable.

`send()`'s signature is
`send(self, value: _SendT_contra, /) -> _YieldT_co`, so its parameter
type is whatever the generator's `SendType` is. For `interview()` that
is `Answer`, and `None` is not an `Answer`, so the priming call is a
type error. `send_none_is_next.py` carries a `# type: ignore` to
suppress it. Removing that comment draws:

```text
error[invalid-argument-type]: Argument to bound method
`Generator.send` is incorrect
 --> send_none_is_next.py:4:27
  |
4 | print(f"{interview().send(None) = }")
  |                           ^^^^ Expected `Answer`, found `None`
```

`next()` takes no such argument. It asks for the generator's next
yielded value and has nothing to say about the `SendType`, so priming
with it type-checks for any generator whatsoever.

The mismatch is real rather than a type checker limitation. A
generator's `SendType` describes what a suspended `yield` expression
can receive, and a just-started generator has no suspended `yield`, so
nothing receives the value handed to the first `send()`. The runtime
enforces the same rule from the other side. `send()` with a non-`None`
value on a fresh generator raises `TypeError: can't send non-None value
to a just-started generator`. So the first call is special in both
directions, and `None` is the only value it accepts.

An annotation cannot express "`None` for the first call, `Answer`
afterward," because a single `SendType` covers every call. Widening the
`SendType` to `Answer | None` states the exception in the type, and
every `yield` expression whose value the generator uses as an `Answer`
must then handle a `None` that arrives only once. `interview()` puts
what it receives into an f-string, which formats a `None` as readily
as an `Answer`, so `interview()` passes the check either way. Priming
with `next()` sidesteps the whole question. The one call that cannot
carry a value comes from the one function that cannot pass one.

</details>
</details>

## 7. A vending machine as a single generator

> [A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine)
> keeps its current state in an attribute and looks up each transition in a table.
> Write a simplified version as a single generator instead.
> It collects money, takes two digits, then dispenses or refuses.
> It yields its current state and receives each event with `send()`,
> so the position in the generator's body carries the state.
> This generator's `yield` reports the state the machine reached rather than requesting something the machine needs,
> the opposite direction from `interview()`.
> Say which of the two versions you would rather extend with another state,
> and why.

<details>
<summary>Where to look</summary>

[A Vending Machine](../../Chapters/31_Patterns--State_Machines.md#a-vending-machine) holds its state in an attribute and a transition table.
Here the position inside the generator's body is the state, so use loops and `isinstance()` checks on the event that `yield` returns.
Because `yield` reports the state reached, the driver's `send()` delivers events rather than answers.

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
    "UNAVAILABLE", "WANT_MORE", "DISPENSED"]

PRICES: Final[dict[str, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[str, int]] = {"11": 0, "12": 3}

def machine() -> Generator[Report, Event]:
    ...
```

<details>
<summary>Solution</summary>

If you write `stock = STOCK` instead of copying with `dict(STOCK)`,
each sale changes the module-level table from which every machine starts.
After three `"12"` sales, by any mix of machines,
a fresh `machine()` answers the next `"12"` order with `UNAVAILABLE`.
The `Final` annotation forbids rebinding the name, not changing the dictionary,
so the type checker passes the shared version.
The solution copies `STOCK` into a local, so each generator's frame holds its own stock.

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
    "UNAVAILABLE", "WANT_MORE", "DISPENSED"]

PRICES: Final[dict[str, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[str, int]] = {"11": 0, "12": 3}

def machine() -> Generator[Report, Event]:
    stock = dict(STOCK)
    amount = 0
    event: Event = yield "QUIESCENT"
    while True:
        while isinstance(event, Coin):
            amount += event.cents
            event = yield "COLLECTING"
        row = event.value  # Not a Coin, so a first Digit
        second = yield "SELECTING"
        # A coin instead of a digit
        if isinstance(second, Coin):
            amount += second.cents
            event = yield "COLLECTING"
            continue
        code = row + second.value
        if stock.get(code, 0) == 0:
            event = yield "UNAVAILABLE"
        elif amount < PRICES.get(code, 0):
            event = yield "WANT_MORE"
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
#: Digit(value='2') -> WANT_MORE
#: Coin(cents=50) -> COLLECTING
#: Digit(value='1') -> SELECTING
#: Digit(value='2') -> DISPENSED
```

**Let position carry the state.** The machine holds no `state`
attribute and consults no table. Where the generator pauses is the
state. A pause in the coin loop means COLLECTING, and a pause after
`yield "SELECTING"` means a first digit has arrived and the machine
waits for a second. `amount`, `row`, and
`stock` are locals that survive because the frame does. This version
has no counterpart for two parts of the table-driven version: the state
attribute and the transition lookup.

**Report the state reached.** The `yield` in `machine()` runs the opposite direction from the one in
`interview()`, and neither signature says so. Both yield strings, but
`interview()` yields a request the driver must satisfy, while
`machine()` yields a report the driver may ignore. The driver's event
and the machine's report travel independently. `send(Coin(25))`
delivers an event and answers no question. A generator's type
describes the traffic, not who is in charge. Both arrangements fit
the same `Generator` annotation.

For another state, take the table. The generator's compactness comes
from the states forming a line, so control flow can express the
sequence. The two states here that break the line cost something. An
`if` chain reaches `UNAVAILABLE` and `WANT_MORE`, and each one returns
by looping back to the top, a `goto` written as a `while True`. If you
add a state reachable from three others, the way the table handles
`Quit` from every state but `QUIESCENT`, no position in the body
corresponds to it. The new state becomes a flag, or a check repeated at
several `yield`s, and either one breaks the correspondence between
position and state, the one thing that makes this version readable.

The table pays a fixed cost instead. Adding a state means one new
`Enum` member and a few new rows. Those rows sit next to the existing
ones, where you can read the whole machine at once. The generator is
the better choice for a conversation with a beginning and an end, like
`interview()`. The table is the better choice for a machine that runs
forever and can go anywhere from anywhere.

</details>
</details>
</details>
