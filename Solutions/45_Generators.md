# Generators: Solutions

## 1. `tally()`, driven by hand

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

The three-parameter annotation names all three channels:
`Generator[Prompt, Amount, Total]` says this generator yields a
`Prompt`, is sent an `Amount`, and finally returns a `Total`. Three
`NewType` aliases over `str`, `int`, and `int` keep the two integer
channels apart, so transposing the `SendType` and the `ReturnType`
would be a type checker error rather than a bug that shows up in arithmetic.

Driving it by hand is three sends for three prompts, and the fourth
value is the one that finishes it. `next(t)` runs the body up to the
first `yield` and produces the first prompt. Each `send()` resumes at
that suspended `yield`, whose value becomes `amount`, then runs to the
next one. The third `send()` finds no fourth `yield`, so the loop ends,
`tally()` returns, and the return value arrives as `StopIteration`'s
`value` rather than as the result of `send()`.

`total` is the generator's own local, and it survives across three
suspensions with no storage anywhere else. The frame is the state.

## 2. A driver that answers from an iterator

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

Nothing in `interview()` changed, and nothing could have. It yields a
`Question` and receives an `Answer`; where the answer came from is a
question it never asks. That is the separation the chapter teaches:
the generator describes the conversation, the driver interprets it, and
swapping one interpreter for another leaves the description untouched.

The two drivers differ in the property they rely on. The dictionary
driver is keyed by the request, so it answers correctly no matter what
order the questions arrive in, and would answer a repeated question the
same way twice. The iterator driver is keyed by position, so it depends
on the generator asking the questions it has replies for, in that
order. Both satisfy the same type. The type says what
travels, not what the driver knows.

One detail in `drive_in_order()` earns its comment. `next(answers)` sits
outside the `try` because a `StopIteration` from an exhausted answer
list would otherwise be caught by the `except StopIteration` meant for
the conversation. Two different iterators raising one exception type is
a real hazard when a driver holds both.

The last two lines show that hazard. Given one answer and
three questions, `drive_in_order()` lets the `StopIteration` escape, so
the caller learns the answer source ran dry. `drive_naive()`, which
differs only in having `next(answers)` inside the `try`, catches that
same exception, reads it as "the conversation finished," and returns
`stop.value`, which is `None`.

`None` is the wrong answer twice over. The interview never finished, so
no `Result` exists, and `None` is not a `Result` in any case. Nothing
catches it: `StopIteration.value` is typed `Any`, so `return stop.value`
satisfies a declared `Result` and `ty` reports nothing. The failure is
silent at the type checker and silent at runtime, and it surfaces later as a
`None` where a string was expected, far from the driver that produced
it.

Keeping the two meanings apart is a one-line discipline: put inside the
`try` only the call whose `StopIteration` you mean to interpret.

## 3. A third delegation in `yield_from_send.py`

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

The prediction to write down is that the five sends do not divide
evenly into three collectors. Each `collect()` consumes two values, so
six are needed, and the loop supplies five. `gamma` is left suspended
at its second `yield`, waiting, and the `send(6)` after the loop
completes it.

The pairs of lines are the tell. A send that supplies a collector's
first value produces one line, the same collector's second prompt. A
send that supplies its second value produces two: the completed
collector's `print()`, then the first prompt of the next one. That is
`send(2)`, `send(4)`, and `send(6)`, so the output alternates between
one-line and two-line responses all the way down.

Nothing in `both()` participates in any of this. It contains three
`yield from` statements and no code that forwards a value, because
`yield from` relays in both directions: prompts up to the driver,
numbers down to whichever `yield` is currently suspended, two frames
below.

## 4. Removing the `yield from`

```python
def survey() -> Generator[Question, Answer, Result]:
    # Was: yield from interview()
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

Both results describe the same mistake, which is that calling a
generator function produces a description rather than a conversation.
`interview()` builds a generator object and stops. Its three questions
are never asked, because nothing ever calls `next()` or `send()` on it,
and the final line interpolates the object's repr into the sentence
where an answer belonged.

The type checker told you more. Its message names the two types and points
at the assignment that mismatches them, which is the defect. The
runtime output shows a consequence three steps downstream, at the one
place the object is stringified, and a reader must work backward from
a `<generator object ...>` in a report to the missing `yield from`.
Worse, the failure is quiet: no exception, an exit code of zero, and
output that a log scraper would happily accept.

Without the annotation, the type checker says nothing. `profile = interview()`
infers `Generator[Question, Answer, Result]`, the expression's own
type, and there is no declared type to contradict. The f-string
then accepts any object, since `str.format` calls `repr()` on anything.
The annotation is doing the whole of the work here, which is the
argument for annotating a local whose value comes from a call whose
return type you want to pin down.

## 5. `report()` with a return value

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

`report()`'s annotation changes from `Iterator[str]` to
`Generator[str, None, int]`, because a generator that returns something
needs the long form: `Iterator` names only the `YieldType`, and a
type checker reading it would reject the assignment in `summarize()`.

The two values travel by different channels, and the listing shows both
at once. Every string, whether yielded by `emit()` or by `report()`,
travels through the `YieldType` and comes out in the list. The count
travels through the `ReturnType`: `emit()` returns it, `yield from`
delivers it into `report()`'s `size`, `report()` returns it again, and
the second `yield from` delivers it into `summarize()`'s `counted`. The
`SendType` is `None` throughout, since nobody sends anything in.

`12` therefore crosses two frames without appearing in the output
sequence, and `'(12 characters)'` appears in the sequence without ever
crossing a frame boundary as a value. The same number can be sent
either way, and the choice decides who can see it: a yielded value goes
to the driver, a returned value goes to the delegating generator.

## 6. Why a driver primes with `next()`

`next(g)` and `g.send(None)` do the same thing at runtime, and the
`SendType` is where they stop being interchangeable.

`send()` is declared as `send(self, value: _SendT_contra) -> _YieldT_co`,
so its parameter type is whatever the generator's `SendType` is. For
`interview()` that is `Answer`, and `None` is not an `Answer`, so the
priming call is a type error. `send_none_is_next.py` carries a
`# type: ignore` to suppress it; removing that comment draws:

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

The mismatch is real rather than a type checker limitation. A generator's
`SendType` describes what a suspended `yield` expression can receive,
and a just-started generator has no suspended `yield`, so the value
handed to the first `send()` is not received by anything. The runtime
enforces this from the other side: `send()` with a non-`None` value on a
fresh generator raises `TypeError: can't send non-None value to a
just-started generator`. So the first call is special in both
directions, and `None` is the only value it accepts.

An annotation cannot express "`None` for the first call, `Answer`
afterward", because a single `SendType` covers every call. Widening it
to `Answer | None` would state the exception in the type, at the price
of forcing every `yield` expression inside the generator to handle a
`None` that arrives only once. Priming with `next()` sidesteps the
whole question: the one call that cannot carry a value is made by the
one function that cannot pass one.

## 7. A vending machine as a single generator

```python
# exercise_7.py
from collections.abc import Generator
from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class Coin:
    cents: int

@dataclass(frozen=True)
class Digit:
    value: str

type Event = Coin | Digit

PRICES: Final[dict[str, int]] = {"11": 25, "12": 75}
STOCK: Final[dict[str, int]] = {"11": 0, "12": 3}

def machine() -> Generator[str, Event]:
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

The machine holds no `state` attribute and consults no table. Where the
generator is suspended is the state: paused in the coin loop means
COLLECTING, paused after `yield "SELECTING"` means a first digit has
arrived and a second is expected. `amount`, `row`, and `stock` are
locals that survive because the frame does. Two lines of the table-driven
version, the state attribute and the transition lookup, have no
counterpart here.

The `yield` runs the opposite direction from `interview()`, and the
signature does not say so. Both are `Generator[str, X, ...]`, but
`interview()` yields a request the driver must satisfy, while this
yields a report the driver may ignore. The reply the driver sends is
unrelated to what was yielded: `send(Coin(25))` answers no question,
it delivers an event. A generator's type describes the traffic, not
who is in charge, and both arrangements fit the same annotation.

For a sixth state, take the table. The generator's compactness comes
from the states forming a line, so control flow can express the
sequence, and the two states here that break the line already cost
something: `UNAVAILABLE` and `WANT_MORE` are reached by an `if` chain
and returned from by looping back to the top, which is a `goto` written
as a `while True`. A sixth state that is reachable from three others,
as the table's `Quit` handling is from every state, has no position in
the body to correspond to. It becomes a flag, or a check repeated at
several `yield`s, and the correspondence between position and state,
the one thing making this version readable, is gone.

The table pays a fixed cost instead. Adding a state is a new `Enum`
member and new rows, and the rows sit next to the existing ones where
you can read the whole machine at once. The generator is the better
choice for a conversation with a beginning and an end, like
`interview()`. The table is the better choice for a machine that runs
forever and can go anywhere from anywhere.
