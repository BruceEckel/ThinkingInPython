# Generators

> A generator is a *resumable function*: it can pause partway, ask for something,
> and continue when the answer arrives.
> An Effect system runs on that conversation.

[Iterators](22_Patterns--Iterators.md#generators)
presents generators as a way to produce values lazily:
a function containing `yield`,
driven by a `for` loop that takes one value at a time.
Producing values is half of what a generator does.

`yield` is an expression,
so a generator can receive a value as well as hand one out,
and it can return a final result when it finishes.
Used that way, a generator is not a sequence but a conversation.
It yields a request, suspends, and continues when a caller sends the answer.
A generator therefore has three *channels*:

- Values go out through `yield`
- Values come in through `send()`
- One value goes out through `return`

This chapter covers:

- The full three-channel annotation
- The *driver* (the loop that runs such a conversation)
- `yield from`, which composes generators that run under any driver

[Stateless](46_Effects--Stateless.md) builds an Effect system on these,
but generators are useful on their own.

## Annotating a Generator

Earlier chapters annotate their generators using the short form `Iterator[int]` in [Iterators](22_Patterns--Iterators.md#generators),
and `Generator[str]` in [Context Managers](15_Techniques--Context_Managers.md#a-basic-context-manager).
The short form fits a generator that yields values, receives `None`,
and returns `None`.

A generator that receives or returns values needs the full annotation,
written here with the names the [`typing` documentation](https://docs.python.org/3/library/typing.html#annotating-generators-and-coroutines)
uses:

    Generator[YieldType, SendType, ReturnType]

This annotation specifies the type of each of the three values a generator exchanges with its caller:

- `YieldType` is the type `yield` hands out,
  thus the type `next(generator)` returns.
- `SendType` is the type `send()` accepts,
  thus the type the `yield` expression produces inside the generator.
- `ReturnType` is the type of the generator's `return` value,
  which arrives as `StopIteration.value`.

The last two type parameters default to `None`.
A generator that receives and returns `None` can use either form:

```python
# generator_defaults.py
from collections.abc import Generator, Iterator

def countdown(n: int) -> Generator[int]:
    while n > 0:
        yield n
        n -= 1

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

print(list(countdown(6)), list(squares(6)))
#: [6, 5, 4, 3, 2, 1] [0, 1, 4, 9, 16, 25]
```

`Generator[int]` means `Generator[int, None, None]`.
`Iterator[int]` describes the same one-way generator.
Its type has the yield channel alone,
so the type checker rejects `send()` on anything annotated `Iterator`.
The long form is necessary when the send channel or the return channel carries a value other than `None`,
as they do in this chapter.

Here, the `interview()` generator yields a question, receives an answer,
and returns a result:

```python
# interview_generator.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield Question("name")
    town: Answer = yield Question("town")
    friend: Answer = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")
```

Although `Generator[str, str, str]` works,
`NewType` gives each channel a distinct type,
so a reader tells a question from an answer or a result by its type.
The annotation says which kind of value each channel carries,
and the type checker rejects a value on the wrong channel.
The distinction exists for the type checker.
At runtime, `Question("name")` returns the same `str` you passed in.

Driving the generator with `next()` and `send()` produces one `Question` at a time:

```python
# drive_by_hand.py
import inspect
from interview_generator import (Answer, Question,
                                 Result, interview)

conversation = interview()
question1: Question = next(conversation)
print(f"{question1 = }")
#: question1 = 'name'
question2: Question = conversation.send(Answer("Alice"))
print(f"{question2 = }")
#: question2 = 'town'
question3: Question = conversation.send(
    Answer("Wonderland"))
print(f"{question3 = }")
#: question3 = 'friend'
print(inspect.getgeneratorlocals(conversation))
#: {'name': 'Alice', 'town': 'Wonderland'}
try:
    conversation.send(Answer("Rabbit"))
except StopIteration as stop:
    result: Result = stop.value
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
```

The last `send()` resumes `interview()`'s body,
which encounters `return` instead of another `yield`,
so the generator returns its `Result`.
The caller receives that `return` as a `StopIteration`,
and the `Result` arrives as the exception's `value`.
A `for` loop treats `StopIteration` as the normal end of the loop,
so it discards the exception and loses the return value.
To read the `ReturnType`, catch the exception yourself,
as `drive_by_hand.py` does.

![Each channel carries one type, in one direction.](_images/generator_channels)

The three arrows are the annotation's three positions: `YieldType` on the first,
`SendType` on the second, `ReturnType` on the third.
A `Question` comes back as the value of `next()` or `send()`,
and a `Result` arrives as the `value` of a `StopIteration`,
so the driver tells them apart by how each arrives.

When the generator body finishes with `return`,
Python raises `StopIteration` on the generator's behalf.
If the body raises a `StopIteration` of its own,
Python converts it into a `RuntimeError`
([PEP 479](https://peps.python.org/pep-0479/)).
As [Asking Consumes an Item](22_Patterns--Iterators.md#asking-consumes-an-item)
shows, calling `next()` on an exhausted iterator raises `StopIteration`,
so a `next()` call inside the body can trigger that conversion.

## What a Suspended Generator Holds

A suspended generator preserves two things:
its position in the body and every local variable.
These outlive each `next()` or `send()` that resumes the generator.
Resuming runs the body from that position, with every local variable intact.
In `drive_by_hand.py`,
`inspect.getgeneratorlocals()` shows the values of `name` and `town` that the generator keeps while it waits for the third answer.
The position and the locals together are the generator's state.

A [closure](40_Functional--Foundations.md#closures)
keeps its captured variables between calls,
but each call runs its body from the top.
The generator keeps its locals and its place in the body,
so a loop or a branch in progress survives the suspension.
The generator is an ordinary object,
so that state lasts as long as something holds a reference to the generator.

The suspended generator is what [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
calls a continuation: the rest of the computation from the `yield` forward.
A [handler](44_Effects--Effect_Management.md#native-effect-management)
can do three things with a continuation: resume it once, discard it,
or resume it several times for a retry or a backtracking search.
A generator's driver can do the first two.
It resumes the continuation once with `send()`,
and discards it by dropping the last reference to the generator.
Resuming several times needs a separate copy of the suspended state for each resumption.
Python cannot copy a generator.
`copy.copy()` on a suspended generator raises `TypeError`.
A generator is therefore a *one-shot continuation*.

Calling a generator function creates the generator.
The generator body runs later, one `yield` at a time,
when the driver calls `next()` or `send()`.
The new generator is suspended before its first statement,
so no `yield` expression is waiting to receive a value.
The first call, which runs the body to its first `yield`,
*primes* the generator.
The priming call must be `next()` or `send(None)`.
Any other argument raises `TypeError: can't send non-None value to a just-started generator`.

`next(conversation)` is equivalent to `conversation.send(None)`:

```python
# send_none_is_next.py
from interview_generator import interview

print(f"{interview().send(None) = }")  # type: ignore
#: interview().send(None) = 'name'
print(f"{next(interview()) = }")
#: next(interview()) = 'name'
```

Each `interview()` call creates a new generator,
so both lines start from the beginning and produce the first question.

The type checker is right to reject `interview().send(None)`.
`interview()` declares `Answer` as its `SendType`,
and `None` is not an `Answer`.
The `# type: ignore` silences that correct report so the listing can show the equivalence.
The interpreter accepts `send(None)` as the priming call,
but the type checker rejects it,
because the annotation applies one `SendType` to every call, the first included.
A driver therefore primes with `next()`.
The check applies to `send()`'s argument.
`next()` takes the generator alone.

## A Generator Waits for Its Driver {#a-generator-is-a-description}

[Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
shows that calling an `async def` function leaves its body waiting to run.
The call returns a coroutine object that holds the body.
That chapter calls the object a description of work,
since building it and running it are separate steps.
A `Coroutine[YieldType, SendType, ReturnType]` has the same three-part shape as a `Generator`.
The shapes match because `async def` and generator functions both return an object that holds a body for a driver to run.
Calling `interview()` returns that object.
`next()` and `send()` run the body, one `yield` at a time.

A driver function runs the generator from start to finish.
It starts the generator body with `next()`,
sends each answer back with `send()`,
and returns the generator's result when the body ends.
Here, `drive()` looks up each answer in a table:

```python
# drive.py
import inspect
from collections.abc import Generator
from typing import Final
from interview_generator import Answer, Question, Result

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer],
          *, show_state: bool = False) -> Result:
    try:
        request: Question = next(conversation)
    except StopIteration as stop:
        return stop.value
    while True:
        answer = answers[request]
        line = f"{request = }, {answer = }"
        if show_state:
            state = inspect.getgeneratorstate(conversation)
            line += f", {state}"
        print(line)
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value
```

`show_state` adds the generator's state to each line of the trace.
The default leaves it out,
so an ordinary call shows the requests and the answers.

The type checker verifies each `Question` the generator yields and each `Answer` that `drive()` sends.
`StopIteration.value` has type `Any`,
so the type checker cannot ensure that `drive()` returns a `Result`.

Each `try` wraps one call that resumes the generator, `next()` or `send()`,
because a `StopIteration` from either means the conversation finished.
The `try` around the priming call catches a conversation that returns before it asks anything.
Any other call that can raise `StopIteration` belongs outside both `try` blocks.
A driver that reads its answers from an iterator, for example,
gets `StopIteration` from `next()` on the answers when they run out.
Inside a `try`, the `except StopIteration` clause catches that exception as the end of the conversation.
The driver then returns `None` as the result.

Here, `drive()` runs the conversation with `show_state=True`:

```python
# two_way_generator.py
import inspect
from drive import ANSWERS, drive
from exceptions import expect
from interview_generator import Answer, interview

conversation = interview()
print(inspect.getgeneratorstate(conversation))
#: GEN_CREATED
result = drive(conversation, ANSWERS, show_state=True)
#: request = 'name', answer = 'Alice', GEN_SUSPENDED
#: request = 'town', answer = 'Wonderland', GEN_SUSPENDED
#: request = 'friend', answer = 'Rabbit', GEN_SUSPENDED
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
print(inspect.getgeneratorstate(conversation))
#: GEN_CLOSED
expect(StopIteration, conversation.send, Answer("Bob"))
#: [StopIteration]
```

`GEN_CREATED` shows the generator as `interview()` created it,
before the body starts.
Each line of `drive()`'s trace shows `GEN_SUSPENDED`,
because whenever `drive()`'s code runs, the generator waits at a `yield`.
After the `return`, the generator is `GEN_CLOSED`,
so sending it another answer raises `StopIteration` at once.
That `StopIteration` carries `None` as its value,
so `expect()` prints the exception's class name alone.

The generator and `drive()` take turns.
While the generator body runs, `drive()` waits inside `send()`,
so `inspect.getgeneratorstate()` returns `GEN_RUNNING` only when code inside the body calls it.
That code needs a reference to its generator,
which a module-level name supplies:

```python
# running_state.py
import inspect
from collections.abc import Generator

def watch() -> Generator[str]:
    yield inspect.getgeneratorstate(watched)

watched = watch()
print(inspect.getgeneratorstate(watched))
#: GEN_CREATED
print(next(watched))
#: GEN_RUNNING
print(inspect.getgeneratorstate(watched))
#: GEN_SUSPENDED
```

`watch()` names `watched` before the module binds it.
As [Names Inside a Function](05_Foundations--Functions.md#names-inside-a-function)
shows, a function looks up a module-level name when its body runs.
`next()` runs `watch()`'s body after `watched = watch()` has bound the name.

The annotation is `Generator[str]` rather than `Iterator[str]`,
because `inspect.getgeneratorstate()` takes a `Generator` and the type checker rejects an `Iterator` argument.

Every answer `interview()` receives comes from its driver.
Swapping `drive()`'s dictionary for a database, or for `input()`,
changes `drive()` and leaves `interview()` as it is.

For managing Effects,
a generator is more useful than a coroutine because you write the driver.
A coroutine's requests go to an event loop,
whether `asyncio`'s loop or one you write yourself.
Each request must be an awaitable object built for that loop.
A generator's requests go to whatever code calls `next()` and `send()`,
and a request can be any value.

A generator yields a request out, and the driver sends the answer back in.
The driver chooses each answer,
so the same generator runs unchanged under different drivers.
That separation of a request from its fulfillment is the core of an [Effect Management System](44_Effects--Effect_Management.md#effect-management-systems)
(EMS).

`interview()` and `drive()` form an EMS in miniature.
The generator declares requests.
The driver interprets them.

`interview()` asks the same three questions whatever answers it receives.
A generator can build its next request from the answer it received:

```python
# follow_up.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def follow_up() -> Generator[Question, Answer, Result]:
    name: Answer = yield Question("name")
    pet: Answer = yield Question(f"pet of {name}")
    return Result(f"{name} keeps a {pet}")

print(drive(follow_up(), ANSWERS | {
    Question("pet of Alice"): Answer("cat"),
}))
#: request = 'name', answer = 'Alice'
#: request = 'pet of Alice', answer = 'cat'
#: Alice keeps a cat
print(drive(follow_up(), {
    Question("name"): Answer("Bob"),
    Question("pet of Bob"): Answer("dog"),
}))
#: request = 'name', answer = 'Bob'
#: request = 'pet of Bob', answer = 'dog'
#: Bob keeps a dog
```

`Question(f"pet of {name}")` carries the `Answer` to `name`,
so the driver's table needs an entry it could not have written before that answer arrived.
Under the second table the generator asks `pet of Bob`,
because the answer to `name` changed.
The driver still chooses every answer.
The generator chooses what to ask next from the answers it has received.
That choice is the conversation.

Each generator has one driver at a time.
The annotation describes the three channels; the runtime enforces the pairing.
If a second thread resumes a generator while another thread is running its body,
the second thread gets `ValueError: generator already executing`.
[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
reproduces the `ValueError` with several threads.
It also shows `threading.synchronized_iterator()`,
which lets those threads share one generator by serializing their calls.

## `yield from` Composes Generators {#yield-from-composes-descriptions}

An EMS needs a request made deep inside a program to reach the driver at its edge.
Generators provide that path because they nest.
`yield from` delegates to an inner generator until that generator finishes.
While it does, the outer generator sits suspended at the `yield from` expression,
and the driver's calls on the outer generator reach the inner one.
Every request the inner generator yields passes out to the driver,
and every answer the driver sends passes back down to the `yield` that is waiting.
The driver still supplies each answer; `yield from` relays it.

In the simplest case,
each generator yields values and leaves its send and return channels at `None`,
so its annotation can be `Iterator[str]` instead of `Generator[str, None, None]`.
The driver is `list()`,
which calls `next()` until the outermost generator finishes:

```python
# yield_to_exhaustion.py
from collections.abc import Iterator

def one() -> Iterator[str]:
    yield "only"

def three() -> Iterator[str]:
    yield "A"
    yield "B"
    yield "C"

def outer() -> Iterator[str]:
    yield "start"
    yield from one()
    yield from three()
    yield "end"

def top() -> Iterator[str]:
    yield "TOP"
    yield from outer()
    yield "END"

print(list(outer()))
#: ['start', 'only', 'A', 'B', 'C', 'end']
print(list(top()))
#: ['TOP', 'start', 'only', 'A', 'B', 'C', 'end', 'END']
```

"To exhaustion" means each `yield from` stays with its target until that generator finishes,
however many `next()` calls that takes.
Exhaustion is transitive.
`top()`'s single `yield from` finishes when the last generator beneath it finishes,
so `list(top())` receives one flat sequence.

Without `from`, a bare `yield one()` yields the generator object as a single value,
so `list(outer())` shows `<generator object one at ...>` in place of `'only'`.

### The Return Channel

A `yield from` expression evaluates to the inner generator's return value:

```python
# yield_from_return.py
from collections.abc import Generator, Iterator
from typing import NewType

Size = NewType("Size", int)

def emit(items: list[str]) -> Generator[str, None, Size]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return Size(total)

def report(items: list[str]) -> Iterator[str]:
    size: Size = yield from emit(items)
    yield f"({size} characters)"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)']
```

The yield channel and the return channel end in different places.
Each item `emit()` yields passes through `report()` to `list()`.
The `Size` that `emit()` returns stops one level up, in `report()`,
as the value of the `yield from` expression.
A `yield from` therefore works like a function call:
`report()` calls `emit()` and gets its result back,
while the values `emit()` yields still go to the driver.

`drive_by_hand.py` and `drive()` read a generator's result by catching `StopIteration` and taking its `value`.
In `report()`, `yield from` takes both steps.
When `emit()` finishes,
`yield from` catches the `StopIteration` and evaluates to the exception's `value`.
The one assignment `size: Size = yield from emit(items)` replaces the `try` and the `except`.

A result passes up through any number of `yield from` levels:

```python
# yield_from_levels.py
from collections.abc import Generator, Iterator
from record import record

@record
class Yielded:
    text: str

@record
class Returned:
    text: str

def inner() -> Generator[Yielded, None, Returned]:
    yield Yielded("inner")
    return Returned("Message from inner!")

def middle() -> Generator[Yielded, None, Returned]:
    yield Yielded("middle")
    return (yield from inner())

def outer() -> Generator[Yielded, None, Returned]:
    yield Yielded("outer")
    return (yield from middle())

def report() -> Iterator[Yielded | Returned]:
    result = yield from outer()
    yield result

for yielded in report():
    print(yielded)
#: Yielded(text='outer')
#: Yielded(text='middle')
#: Yielded(text='inner')
#: Returned(text='Message from inner!')
```

A `Yielded` goes out on the yield channel and a `Returned` on the return channel.
The `Yielded` lines print outermost first, in the order the generators start.
The `Returned` passes back up through `middle()` and `outer()` to `report()`.
`return (yield from ...)` passes the result through unchanged.

`report()` yields the value of its `yield from`,
so the last output line arrives through the return channel.
Its annotation widens to `Iterator[Yielded | Returned]`,
because the loop receives both types.

Because each `yield from` hands a result back to its caller,
a recursive generator can combine results on the way back up a tree.
Here, `visit()` walks a nested dictionary of plants,
yields the path to each plant, and returns a count of each color:

```python
# color_count.py
from collections import Counter
from collections.abc import Generator, Iterator
from enum import StrEnum

class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

type Name = str
type Path = str
type Tree = dict[Name, Tree | Color]

def visit(
    tree: Tree, at: Path = ""
) -> Generator[str, None, Counter[Color]]:
    counts = Counter[Color]()
    for name, node in tree.items():
        if isinstance(node, dict):  # node is a Tree
            counts += yield from visit(node, f"{at}{name}/")
        else:  # node is a Color
            yield f"{at}{name}: {node}"
            counts[node] += 1
    return counts

def census(tree: Tree) -> Iterator[str]:
    counts: Counter[Color] = yield from visit(tree)
    for color, n in counts.items():
        yield f"{n} {color}"

garden: Tree = {
    "rose": Color.RED,
    "beds": {
        "fern": Color.GREEN,
        "tulip": Color.RED,
        "pond": {"iris": Color.BLUE, "reed": Color.GREEN},
    },
    "ivy": Color.GREEN,
}
for line in census(garden):
    print(line)
#: rose: red
#: beds/fern: green
#: beds/tulip: red
#: beds/pond/iris: blue
#: beds/pond/reed: green
#: ivy: green
#: 2 red
#: 3 green
#: 1 blue
```

A yielded path such as `beds/pond/iris: blue` passes through every enclosing `visit()` and through `census()`,
and reaches the `for` loop at the bottom of the listing.
Each `visit()` returns its subtree's [`Counter`](03_Foundations--Containers.md#counter)
to the `visit()` that called it.
`Counter` objects support `+`,
so `counts += yield from visit(...)` merges a subtree's counts into the parent's counts.
The outermost `visit()` returns the `Counter` for the whole garden to `census()`.

`yield from` delegates to any iterable, not just a generator.
Here, it takes a list:

```python
# yield_from_list.py
from collections.abc import Iterator

def relay() -> Iterator[int | None]:
    v: None = yield from [1, 2, 3]
    yield v

print(list(relay()))
#: [1, 2, 3, None]
```

A generator's `return` statement supplies the `value` that its `StopIteration` carries.
A list's iterator raises a bare `StopIteration`,
so the exception's `value` is `None` and a `yield from` over a list evaluates to `None`.

### The Send Channel

`yield from` also forwards each value the driver sends,
delivering it to the `yield` that waits inside the inner generator.
`collect()` asks the driver for two values and returns their sum:

```python
# collect.py
from collections.abc import Generator
from typing import NewType

Prompt = NewType("Prompt", str)
type Value = int
Total = NewType("Total", int)

def collect(name: str) -> Generator[Prompt, Value, Total]:
    first: Value = yield Prompt(f"{name} needs a value")
    second: Value = yield Prompt(f"{name} needs another")
    print(f"{name} got {first} and {second}")
    return Total(first + second)
```

`Prompt` and `Total` are `NewType`s,
like `Question` and `Result` in `interview_generator.py`,
so the type checker distinguishes a prompt from a total.
`Value` is a `type` alias,
so the driver's `g.send(value)` passes a bare `int` and still matches the send type:

```python
# yield_from_send.py
from collections.abc import Generator
from collect import Prompt, Total, Value, collect

def both() -> Generator[Prompt, Value]:
    alpha: Total = yield from collect("alpha")  # [1]
    beta: Total = yield from collect("beta")  # [2]
    yield Prompt(f"total {alpha + beta}")  # [3]

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4]:
    print(f"g.send({value}) -> {g.send(value)}")
#: g.send(1) -> alpha needs another
#: alpha got 1 and 2
#: g.send(2) -> beta needs a value
#: g.send(3) -> beta needs another
#: beta got 3 and 4
#: g.send(4) -> total 10
```

`both()` declares the same yield type (`Prompt`) and send type (`Value`)
as `collect()`, because `yield from` passes both channels through to the driver.
`both()` returns `None`, so its return type is the `None` default.

`g.send(2)` supplies `second`,
so `collect("alpha")` finishes and the `yield from` at `[1]` completes.
Before that `send(2)` returns,
`both()` continues to `[2]` and `collect("beta")` runs to its first prompt.
One `send()` therefore ends one inner generator and produces the first prompt of the next,
which is why `alpha got 1 and 2` and `beta needs a value` sit on adjacent output lines.
The `yield` at `[3]` gives `send(4)` a value to return.
Without it, `send(4)` finishes `both()` and raises `StopIteration` in the loop.

### All Three Channels

Here, a new version of `interview()` makes each request through a helper,
`ask()`, and delegates to it with `yield from`:

```python
# yield_from_delegates.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer: Answer = yield question
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    friend: Answer = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
```

`Answer` fills two of `ask()`'s three positions, in two roles.
As the `SendType` it goes from the driver to the `yield` inside `ask()`.
As the `ReturnType` it goes from `ask()` up to `interview()`,
which binds it to `name`, `town`, or `friend`.

This listing imports `drive()` unchanged.
The requests now come from `ask()`, one generator below `interview()`,
and `yield from` passes each one up to the driver,
so `drive()` sees the same `Question`s it saw in `interview_generator.py` and prints the same trace.
`ask()` yields a `Question` and receives an `Answer`,
so the same `ask()` runs under any driver that answers `Question`s.
A single loop at the edge of the program interprets requests yielded at any depth.

### Composing Is Not Interpreting

`drive()` and `yield from` both run a generator's body one `yield` at a time and both finish at `StopIteration`,
so they are easy to confuse.
In `yield_from_delegates.py`, `drive()` receives `interview()`'s `Result`.
In `yield_from_nested.py`, a `yield from` in `survey()` receives that `Result`:

```python
# yield_from_nested.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import ask, interview

def survey() -> Generator[Question, Answer, Result]:
    profile: Result = yield from interview()
    color: Answer = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")

print(drive(survey(),
            ANSWERS | {Question("color"): Answer("blue")}))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: request = 'color', answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
```

Here `interview()`'s `Result` arrives as the value of `yield from interview()` instead of as `stop.value` in the driver.
`interview()`'s questions reach `drive()` through three generators rather than two.

![Requests reach the one driver; results stop one level up.](_images/yield_from_relay)

Each `yield from` passes the `Question` up and the `Answer` down unchanged,
so the trace repeats the three request lines of `yield_from_delegates.py` before the new one.
The `Result` goes one level up and stops,
as the value of `survey()`'s `yield from`.

The outermost generator still needs code that calls `next()` and `send()`,
so the listing ends with a `drive()` call.
However deeply the delegations nest, the program has one driver.

`drive()` and `yield from` differ in how they respond to a request.
`drive()` answers it.
The generator yields a `Question`, `drive()` looks it up,
and the request stops there.
`yield from` relays the request upward and passes the answer back down,
both intact.
`drive()` does the lookup for a `Question` yielded at any depth.

`drive()` and `yield from` also differ in what they do at `StopIteration`.
Both catch it and both take `stop.value`,
but they hand that value to different places.
`drive()` returns the `Result` to its caller, ending the conversation.
`yield from` hands the `Result` to the enclosing generator,
which continues the conversation.

### A Generator in the Middle

A `yield from` target is an ordinary value.
It can arrive as a parameter, sit in a list,
or be built at the point of delegation.
A generator can receive its targets as arguments,
so the caller decides what the conversation holds:

```python
# yield_from_arguments.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import ask, interview

def sequence(
    *steps: Generator[Question, Answer, str]
) -> Generator[Question, Answer, Result]:
    results: list[str] = []
    for step in steps:
        result = yield from step
        results.append(result)
    return Result(", ".join(results))

print(drive(
    sequence(interview(), ask(Question("color"))),
    ANSWERS | {Question("color"): Answer("blue")},
))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: request = 'color', answer = 'blue'
#: Alice of Wonderland, friend Rabbit, blue
```

A step is any generator that yields `Question`s, receives `Answer`s,
and returns a `str`.
`Result` and `Answer` are both `str`s,
so `interview()` and `ask()` both qualify as steps.
The loop delegates to each step in turn,
and each `yield from` expression collects what its step returns.

A generator that sits between `drive()` and `interview()` can do both:
answer the requests it knows and relay the rest.
`proxy()` has the same annotation as `interview()`, so `drive()` accepts either,
and `survey()` can delegate to either with `yield from`:

```python
# answering_proxy.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import interview

def proxy(
    inner: Generator[Question, Answer, Result],
    known: dict[Question, Answer],
) -> Generator[Question, Answer, Result]:
    try:
        request = next(inner)
    except StopIteration as stop:
        return stop.value
    while True:
        if request in known:
            answer = known[request]  # [1]
            print(f"  proxy answers {request}")
        else:
            answer: Answer = yield request
        try:
            request = inner.send(answer)
        except StopIteration as stop:
            return stop.value

print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
print(drive(
    proxy(interview(), {Question("town"): Answer("Oz")}),
    ANSWERS,
))
#: request = 'name', answer = 'Alice'
#:   proxy answers town
#: request = 'friend', answer = 'Rabbit'
#: Alice of Oz, friend Rabbit
```

`proxy()` is a [*Proxy*](25_Patterns--Surrogate.md#proxy):
the same interface as the object it wraps, with a forwarding loop of its own.
It is also the shape of [layering handlers](46_Effects--Stateless.md#layering-handlers)
in Stateless, where a handler answers the requests `supply()` gave it and re-yields the rest to the handler outside it.

The priming call to `next()` sits in a `try` because `proxy()` is a generator,
and a `StopIteration` that propagates out of a generator's body becomes a `RuntimeError`.
`next(inner)` runs `inner`'s body up to its first `yield`.
How much code runs before that point depends on the generator.
A generator that opens with a `yield from` runs into its delegate and stops at the delegate's first `yield`.
`sequence()` with no steps returns before it yields anything,
so `next(inner)` raises `StopIteration`.

In the second run, `drive()` sees two requests instead of three.
The proxy answers `town` at `[1]`, so that request stops at the proxy,
and the result changes while `interview()` and `drive()` stay the same.

## The Driver's Exception Channel {#the-drivers-exception-channel}

A driver controls a generator through the methods of the generator object:

- `next()` runs the body to its next `yield`, where the generator suspends.
- `send()` resumes the body with a value,
  and that value becomes the result of the `yield` expression where the generator stopped.

Two more methods resume the body at a `yield`.
With these, the `yield` expression raises an exception instead of returning a value:

- `throw(exc)` makes the `yield` raise `exc`.
- `close()` is `throw(GeneratorExit)` plus a rule: the generator must end.

Both methods are called by the driver that holds the generator object.
After `close()`, the generator ends in one of two ways: it returns,
or it lets `GeneratorExit` propagate out of its body.
Either way, the generator has finished,
and `inspect.getgeneratorstate()` reports `GEN_CLOSED`.
`close()` then returns to the driver, and the driver's next statement runs.

### An Exception at the `yield`

Here are the basics of `throw()` and `close()`:

```python
# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def pause() -> Generator[None]:
    try:
        yield
        print("resumed")
    finally:
        print("finished")

g = pause()
next(g)
expect(ValueError, g.throw, ValueError("stop"))  # [1]
#: finished
#: [ValueError] stop
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = pause()
next(g)
g.close()  # [2]
#: finished
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
```

In both `[1]` and `[2]`, the generator body ends at the `yield`,
before it reaches `print("resumed")`.
The exception arrives in place of a value and propagates out through the body,
running the `finally` block on its way, which prints `finished`.
Leaving the body ends the generator, as a `return` would,
and both runs leave the generator `GEN_CLOSED`.

At `[1]`, `pause()` resumes,
and its `yield` raises `ValueError` instead of returning a value.
`pause()`'s `try` has a `finally` clause and no `except`,
so the `finally` block runs as control leaves the `try` statement.
The `ValueError` then propagates out of the generator and comes out of the driver's `throw()` call,
where `expect()` reports it.

At `[2]`, the `yield` raises `GeneratorExit`.
`GeneratorExit` takes the same path out of `pause()`,
running the `finally` block.
This time the driver sees an ordinary return,
because `close()` catches the `GeneratorExit` on its way out.
`GeneratorExit` is the driver's signal that this resumption is the last one.
It tells the generator to finish.

Why does the driver need methods to raise exceptions inside the generator,
when Python has a `raise` statement?
`raise` produces its exception in the function that executes it,
and the exception then propagates up through that function's callers.
While the driver runs, the generator sits paused at its `yield`,
off the call stack.

A `raise` in the driver therefore goes up to the driver's callers.
The generator's `except` and `finally` clauses are nowhere on that path.
`throw()` and `close()` resume the generator at its `yield`,
then raise an exception there.
The generator's `except` clauses catch it and its `finally` clauses run.

`throw()` raises the exception the driver passed.
`close()` raises `GeneratorExit`.
The driver, the code that holds the generator object, calls both methods.
Inside the generator's body, `raise` works as it does anywhere.

A generator yields a request and waits.
When the driver has an answer, it calls `send()` with that answer.
When the driver has a failure, it calls `throw()` with an exception.
Either call replies to the request the generator yielded,
`send()` with a value and `throw()` with an exception.
The generator either handles the exception and yields again,
or lets it propagate.
An exception that propagates out of a generator ends that generator.
`asyncio` calls `throw()` on a coroutine when an awaited operation fails or a cancellation arrives.
`@contextmanager` does the same in [A Basic Context Manager](15_Techniques--Context_Managers.md#a-basic-context-manager):
its `__exit__()` calls the generator's `throw()` method,
"which resumes the generator by raising the block's exception at the `yield`."

`close()` is the `throw()` whose exception Python chooses,
so it sends one message: finish.
`GeneratorExit` says the same thing whatever the driver's reason,
and a generator that catches it must still end.
If the generator yields again, `close()` raises a `RuntimeError`,
as [`close()` Requires the Generator to Finish](#close-requires-the-generator-to-finish)
shows.
`throw()` leaves the decision with the generator.
The exception's class says which failure occurred,
so the body's `except` clauses choose among failures,
and a clause that handles one yields the next request.
`worker()` in [Handle, Clean Up, or Stop Early](#handle-clean-up-or-stop-early)
catches a `ValueError` this way and yields `"recovered"`.

Most conversations end when the generator returns.
When the driver finishes first, with the generator still waiting at a `yield`,
it calls `close()`, and `GeneratorExit` arrives at that `yield`.
The cleanup that runs is the generator's own code,
a `finally` clause or an `except GeneratorExit` around the `yield`.
Then the generator ends.
`close_when_done.py` in [Handle, Clean Up, or Stop Early](#handle-clean-up-or-stop-early)
shows a driver closing a sensor generator when it has the reading it needs.

`throw()` and `close()` deliver an exception from the driver into the generator.
An exception can also propagate from the generator into the driver.
When the generator body raises an exception,
the exception comes out of the `next()`, `send()`,
or `throw()` call that resumed the generator:

```python
# body_raises.py
import inspect
from collections.abc import Generator
from exceptions import expect

def strict() -> Generator[str, int]:
    received = yield "a positive number"
    if received <= 0:
        raise ValueError(f"{received} not positive")  # [1]

g = strict()
print(next(g))
#: a positive number
expect(ValueError, g.send, -3)  # [2]
#: [ValueError] -3 not positive
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
```

`send(-3)` at `[2]` resumes the body with `received` bound to `-3`.
The body rejects the value and raises `ValueError` at `[1]`.
The `ValueError` propagates out of the generator body.
The `send()` call at `[2]` then raises that `ValueError` in the driver,
where `expect()` reports it.
`GEN_CLOSED` shows that the exception shut the generator down,
as `throw()` does.

`throw()` carries an exception from the driver down to the `yield`.
A `raise` in the generator body carries an exception from the generator up to the `next()`,
`send()`, or `throw()` call that resumed the generator.
In both directions, the exception passes through a method call that the driver made on the generator object.

### Handle, Clean Up, or Stop Early

In `throw_close_basics.py`,
`pause()` lets both exceptions propagate and cleans up in a `finally` clause.
A generator body chooses what to do with an exception that arrives at its `yield`:
handle it and yield again, clean up, or let the exception end the generator.
`worker()` does all three with a `try` around its `yield`:

```python
# throw_and_close.py
from collections.abc import Generator

def worker() -> Generator[str]:
    try:
        yield "ready"
    except ValueError as e:
        print(f"caught: {e}")
        yield "recovered"
    finally:
        print("cleanup")

g = worker()
print(next(g))
#: ready
print(g.throw(ValueError("bad input")))
#: caught: bad input
#: recovered
g.close()
#: cleanup
```

`worker()` handles one exception and cleans up after any.
`g.throw(ValueError("bad input"))` raises `ValueError` at `yield "ready"`.
The `except ValueError` clause catches it, prints `caught`,
and yields `"recovered"`.
Like `send()`, `throw()` returns the next value the generator yields,
so the driver prints `recovered`.
An exception that propagates out of the generator body ends the generator and comes back out of `throw()` into the driver,
as in `throw_close_basics.py`.

`g.close()` then raises `GeneratorExit` at `yield "recovered"`,
where the generator now waits.
The `except` clause names `ValueError` alone,
so `GeneratorExit` propagates past it, the `finally` block prints `cleanup`,
and the generator ends.
`close()` catches the `GeneratorExit` on its way out and returns,
so the driver sees an ordinary return.
`close()` returns whatever the generator returned while handling `GeneratorExit`.
Here the return value is `None`,
since `worker()` ends through its `finally` block with no `return` statement.

`close()` is the driver's tool for ending a generator early.
A paused generator keeps open whatever its body opened:
a file or a lock inside a `with` statement, a connection, a transaction.
The common case is a driver that has the answer it needs before the generator has run out:

```python
# close_when_done.py
import inspect
from collections.abc import Generator

def readings() -> Generator[int]:
    print("sensor on")
    pending = [3, 7, 12, 9, 4]
    try:
        while pending:
            yield pending.pop(0)
    except GeneratorExit:
        print(f"stopped with {len(pending)} unread")
    finally:
        print("sensor off")

def first_above(
    source: Generator[int], limit: int
) -> int | None:
    for reading in source:
        if reading > limit:
            return reading  # [1]
    return None

sensor = readings()
print(first_above(sensor, 10))
#: sensor on
#: 12
print(inspect.getgeneratorstate(sensor))
#: GEN_SUSPENDED
sensor.close()  # [2]
#: stopped with 2 unread
#: sensor off
```

`first_above()` returns at `[1]` with the first reading over the limit.
`readings()` stays paused at its `yield`,
with the sensor on and two readings still in `pending`.
The caller still holds the generator,
which `inspect.getgeneratorstate()` reports as `GEN_SUSPENDED`.
`close()` at `[2]` raises `GeneratorExit` at that `yield`.
The two clauses around the `yield` do different jobs.
The `except GeneratorExit` clause runs when the driver stops early,
and reports what the stop left unread.
The `finally` clause runs on every ending and turns the sensor off.
A generator may catch `GeneratorExit` as long as it then finishes,
as `readings()` does by reaching the end of its body;
[`close()` Requires the Generator to Finish](#close-requires-the-generator-to-finish)
shows the generator that yields instead.
If the driver leaves the generator paused,
Python calls `close()` when the garbage collector reclaims the generator,
so the `finally` block runs eventually.
Calling `close()` yourself runs the `finally` block at a point you choose.

### Through `yield from` to the Innermost Generator {#throw-and-close-reach-the-innermost-generator}

A `yield from` passes both calls on, down to the generator that is waiting:

```python
# throw_through.py
from collections.abc import Generator

def inner() -> Generator[str]:
    try:
        yield "inner ready"
    except ValueError as e:
        print(f"inner caught: {e}")
        yield "inner recovered"
    finally:
        print("inner cleanup")

def outer() -> Generator[str]:
    try:
        yield from inner()
    finally:
        print("outer cleanup")

g = outer()
print(next(g))
#: inner ready
print(g.throw(ValueError("bad input")))
#: inner caught: bad input
#: inner recovered
g.close()
#: inner cleanup
#: outer cleanup
```

The driver holds the generator `outer()` returned and calls `throw()` on it,
but `inner()` prints the `caught` line.
`outer()` is paused at its `yield from` expression,
and `inner()` is paused at its `yield`.
The exception belongs at the point where the innermost body stopped,
which is `inner()`'s `yield`,
so `yield from` hands the exception down to `inner()`.
`inner()`'s `except` clause handles it and yields `"inner recovered"`.
That value comes back up through `yield from` to the driver,
as every yielded value does.
If the exception propagates out of `inner()`, it comes back up into `outer()`,
as if `outer()`'s `yield from` expression had raised it.
`outer()`'s `finally` block then runs on the exception's way out.
`g.close()` follows the same path.
Python raises `GeneratorExit` in `inner()` first, then in `outer()`,
so the two cleanup lines print from the inside out.
A driver that holds the outermost generator stops and cleans up every generator beneath it with one call.

A [*Saga*](39_Patterns--Pattern_Catalog.md#distributed-and-cloud)
relies on that inside-out order.
A saga runs a long transaction as a series of steps.
When a later step fails, each earlier step undoes what it did,
latest step first.
With one generator per step,
a step's undo is an `except` clause around its `yield from`:

```python
# saga.py
from collections.abc import Generator
from exceptions import expect

class Failed(Exception):
    pass

def step(
    name: str, rest: Generator[str] | None = None
) -> Generator[str]:
    yield f"do {name}"
    if rest is None:
        return
    try:
        yield from rest
    except Failed:
        print(f"undo {name}")
        raise

booking = step("flight", step("hotel", step("card")))
print(next(booking))
#: do flight
print(next(booking))
#: do hotel
print(next(booking))
#: do card
expect(Failed, booking.throw, Failed("card declined"))
#: undo hotel
#: undo flight
#: [Failed] card declined
```

Each step yields its command,
then delegates to the steps after it inside a `try`.
The driver reports the card's failure by calling `throw()`.
Python raises `Failed` at the innermost `yield`, in the card step.
That `yield` sits before the card step's `try`,
so the exception passes straight out of the card step,
whose own action is the one that failed.
The exception then propagates up through the two `yield from` expressions.
Each `except` prints its compensation and raises `Failed` again,
hotel before flight.
The nesting of the `try` blocks is the undo stack.
When all three commands succeed, the booking runs to its end.

### `close()` Requires the Generator to Finish

If a generator catches `GeneratorExit` and yields again instead of finishing,
`close()` raises a `RuntimeError`:

```python
# throw_and_close_gotcha.py
from collections.abc import Generator
from exceptions import expect

def stubborn() -> Generator[str]:
    try:
        yield "go"
    except GeneratorExit:
        yield "not done"

s = stubborn()
print(next(s))
#: go
expect(RuntimeError, s.close)
#: [RuntimeError] generator ignored GeneratorExit
```

When the driver calls `close()`, the `RuntimeError` arrives in the driver,
as above.
When the garbage collector makes the `close()` call,
the call comes from the collector rather than from code that can catch the exception,
so Python prints the error as an "Exception ignored" message and continues.
A generator written for others to drive therefore lets `GeneratorExit` end it.

## One Generator per State

[State Machines](31_Patterns--State_Machines.md)
builds its mousetrap from an `Enum` of rows,
each holding a state's entry message and a transition function,
and an engine that calls the current state's function on every input.

Every resumption of a generator is a decision point.
The body reads the value that `send()` delivered and chooses what to do next:
yield again, or return and finish.
`answering_proxy.py` makes that choice with an `if`,
between yielding a request to the driver and answering it from its table.
A `match` on the received input makes the same choice with one `case` per input.
A generator that returns from a `case` has moved to a new state.

A generator therefore offers a third design.
Each state is a generator function.
Its entry action is the code before its first `yield`,
each `yield` reports the state's name and receives the next input,
and a transition is a `return` whose value is the next state:

```python
# trap_generators.py
from collections.abc import Generator
from enum import StrEnum

class Mouse(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

type Machine = Generator[str, Mouse, Machine | None]

def waiting() -> Machine:
    print("Broadcasting cheese smell")
    while True:
        match (yield "Waiting"):
            case Mouse.APPEARS:
                return luring()

def luring() -> Machine:
    print("Presenting Cheese, door open")
    while True:
        match (yield "Luring"):
            case Mouse.RUNS_AWAY:
                return waiting()
            case Mouse.ENTERS:
                return trapping()

def trapping() -> Machine:
    print("Closing door")
    while True:
        match (yield "Trapping"):
            case Mouse.ESCAPES:
                return waiting()
            case Mouse.TRAPPED:
                return holding()

def holding() -> Machine:
    print("Mouse caught")
    print("*ding*")
    while True:
        match (yield "Holding"):
            case Mouse.REMOVED:
                return waiting()
```

`Mouse` is the input enum from [Mousetrap States](31_Patterns--State_Machines.md#mousetrap-states).
`Machine` is a recursive alias: a state yields its name, receives a `Mouse`,
and returns the next state, or `None` to halt.
The `type` statement evaluates its right side lazily,
so the alias can name itself.

An input with no `case` leaves the state's `while` loop running,
so the machine stays in that state.
The entry action sits above the loop, so it runs once, on entry.
`trap_states.py`'s `waiting()` returns `TrapState.WAITING` from its `case _`,
and `state_machine.py` re-enters the state and prints its message again.
`HOLDING`'s `chime` is a third field in its row;
here `holding()`'s entry code prints it after the message.

`return luring()` creates `luring()`'s generator object and hands it out as `waiting()`'s result.
`luring()`'s body runs when a driver delegates to it:

```python
# trap_generators_demo.py
from collections.abc import Generator, Iterable
from typing import Final
from trap_generators import Machine, Mouse, waiting

def trampoline(
    state: Machine | None
) -> Generator[str, Mouse]:
    while state is not None:
        state = yield from state  # [1]

def run_all(
    start: Machine, inputs: Iterable[Mouse]
) -> None:
    machine = trampoline(start)
    state = next(machine)  # [2]
    for input_ in inputs:
        new_state = machine.send(input_)  # [3]
        print(state, input_, "->", new_state)
        state = new_state

MOVES: Final[list[Mouse]] = [
    Mouse.APPEARS, Mouse.RUNS_AWAY, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.ESCAPES, Mouse.APPEARS,
    Mouse.ENTERS, Mouse.TRAPPED, Mouse.REMOVED,
]
run_all(waiting(), MOVES)
#: Broadcasting cheese smell
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Broadcasting cheese smell
#: Luring mouse runs away -> Waiting
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Closing door
#: Luring mouse enters trap -> Trapping
#: Broadcasting cheese smell
#: Trapping mouse escapes -> Waiting
#: Presenting Cheese, door open
#: Waiting mouse appears -> Luring
#: Closing door
#: Luring mouse enters trap -> Trapping
#: Mouse caught
#: *ding*
#: Trapping mouse trapped -> Holding
#: Broadcasting cheese smell
#: Holding mouse removed -> Waiting

run_all(waiting(), [Mouse.ESCAPES])
#: Broadcasting cheese smell
#: Waiting mouse escapes -> Waiting
```

`trampoline()` is the engine, the loop at `[1]`.
PEP 342 calls such a driver a *trampoline*: each state returns to the loop,
which bounces into the next state.
`yield from` runs the current state,
relaying each of its `yield`s up to `run_all()` and each `send()` back down.
When the state returns, the loop takes the returned generator as the next state.
Apart from its return type, `trampoline()` has a state's annotation,
so `run_all()` drives it as it drives any generator.
`[2]` primes the machine,
which runs `waiting()`'s entry action and stops at its first `yield`.
Each `send()` at `[3]` delivers one input and returns the name of the state the machine then occupies.

This trace and the trace in `trap_states_demo.py` have the same lines in a different order.
Each entry message prints before the transition line that leads to it.
The entry action runs inside `send()`, in the new state's body,
and `run_all()` prints its line after `send()` returns.
In `state_machine.py` the engine makes both `print()` calls and chooses their order;
here each state's body runs its entry action.

The listing's second run shows a state that stays.
`waiting()` matches `Mouse.APPEARS` alone,
so `Mouse.ESCAPES` leaves the machine in `Waiting`,
and the entry message prints once.

[Which Design Should You Use?](31_Patterns--State_Machines.md#which-design-should-you-use)
asks whether an action belongs to the state or to the transition.
Here the question has two places to put code rather than two designs.
Code before the first `yield` is the state's entry action, the Moore shape,
where the action belongs to the state.
Code before a `return` runs on that transition alone, the Mealy shape,
where the action belongs to the transition.
A `print("Door latched")` above `return holding()` in `trapping()` runs when the mouse is trapped and at no other time.
The Moore shape and the Mealy shape both fit one function with no `action` field.

A state's local variables are its data.
`VendingMachine` keeps `amount` on the machine object because every machine shares the enum members.
A generator state keeps such a value in a local and passes it to the next state as an argument,
`return selecting(amount)`,
so each state receives the data it needs and the machine object disappears.

Exercise 8 writes the vending machine as one generator,
with each state a loop inside a single generator body,
which suits a machine that is mostly a sequence.
One generator per state suits a machine like the trap,
whose transitions form a graph.

Chapter 31's `Enum` makes the states a closed set.
Here the set is open: any function that returns a `Machine` is a state.
`test_trap_states.py` iterates over `TrapState` and checks every state against every move;
a test of the generator design reaches a state by driving the machine to it.
A machine whose states a test must enumerate belongs in chapter 31's table.

The generator design has a second limit.
`copy.deepcopy()` and `pickle` both raise a `TypeError` on a suspended generator,
so a [*Memento*](36_Patterns--Memento.md#the-classic-memento)
belongs to the enum designs, which keep the state in a value a record can hold.

One shape looks like a transition and is a delegation:

```python
# tail_delegation.py
from collections.abc import Generator
from exceptions import expect

def tick() -> Generator[str]:
    yield "tick"
    return (yield from tock())  # [1]

def tock() -> Generator[str]:
    yield "tock"
    return (yield from tick())

def run(steps: int) -> None:
    clock = tick()
    for _ in range(steps):
        next(clock)

run(500)
expect(RecursionError, run, 2000)
#: [RecursionError] maximum recursion depth exceeded
```

`[1]` hands control to `tock()`,
but `tick()` stays suspended at its `yield from` until `tock()` returns.
`tock()` delegates to a new `tick()` in turn instead of returning.
Every transition nests one generator deeper,
and each `next()` passes through every level on its way to the innermost `yield`.
After about a thousand transitions the chain is deeper than Python's recursion limit.
The trampoline keeps the chain one level deep.
`yield from state` finishes when the state returns,
and the loop takes up the next state at the same depth.
[The Restriction Behind the Driver](#the-restriction-behind-the-driver)
says why a driver exists.
Exercise 9 meets the same `return (yield from inner)` in `proxy()`,
where it relays every request instead of answering one.

## Many Generators, One Driver

This chapter rests on three ideas:

- Calling a generator function returns a generator object that holds the body and its state.
  A driver runs that body one `yield` at a time with `next()` and `send()`.
- `yield` carries a request out of the body and `send()` carries the answer back in,
  so the body can ask for something and receive the answer.
- `yield from` composes those conversations.
  Each generator in the chain yields to whatever code resumed it,
  so one chain runs under any driver.

The first two ideas are enough to build a task runner.
A queue holds the live generators.
The runner gives each one a turn:

```python
# task_runner.py
from collections import deque
from collections.abc import Iterator

def download() -> Iterator[str]:
    for part in ("headers", "body", "checksum"):
        yield f"download: {part}"

def index() -> Iterator[str]:
    yield "index: build"
    yield "index: merge"

def task_runner(jobs: deque[Iterator[str]]) -> None:
    while jobs:
        job = jobs.popleft()  # [1]
        try:
            print(next(job))
        except StopIteration:
            continue  # [2]
        jobs.append(job)  # [3]

task_runner(deque([download(), index()]))
#: download: headers
#: index: build
#: download: body
#: index: merge
#: download: checksum
```

`deque([download(), index()])` holds the two generator objects produced by calling `download()` and `index()`.
`[1]` takes the job at the front of the queue,
and `next()` runs it to its next `yield`.
`[3]` puts that job at the back of the queue, behind the other job,
so the two jobs alternate.
A finished job raises `StopIteration` at its `next()`,
and the `continue` at `[2]` skips `[3]`, so the finished job leaves the queue.

We can modify `task_runner()` to allow jobs to make requests:

```python
# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable
from typing import Final

type Request = str
type Reply = str
type Job = Generator[Request, Reply]

REPLIES: Final[dict[Request, Reply]] = {
    "download: headers?": "200 OK, 512 bytes",
}

def answer(request: Request) -> Reply:
    return REPLIES.get(request, "ok")

def download() -> Job:
    reply: Reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Job:
    yield "index: build"
    yield "index: merge"

def task_runner(jobs: Iterable[Job]) -> None:
    ready: deque[tuple[Job, Request]] = deque()
    for job in jobs:
        try:
            ready.append((job, next(job)))
        except StopIteration:
            pass
    while ready:
        job, request = ready.popleft()
        print(request)
        try:
            request = job.send(answer(request))
        except StopIteration:
            continue
        ready.append((job, request))

task_runner([download(), index()])
#: download: headers?
#: download: 200 OK, 512 bytes
#: index: build
#: download: checksum
#: index: merge
```

The `for` loop primes each `job` and pairs it with its first request.
The `except` catches the `StopIteration` from a job that finishes before its first `yield`,
and drops that job.
When a `job` finishes, its `send()` raises `StopIteration`.
The `continue` then skips the `append`, so that `job` leaves `ready`.

`index()` discards what it receives.
It yields only to take turns.

## The Driver You Already Use

`asyncio.run()` starts an event loop,
a driver like the one in `task_runner_send.py`.
The event loop gives each task a turn and answers the request each task yields.
Like a generator, a coroutine object offers `send()`, `throw()`, and `close()`.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
describes `await` as suspending a task until the event loop resumes it.
`await` suspends the coroutine and yields a request, a `Future`,
to the task that drives it.
When the `Future` has a result, the loop resumes the coroutine,
and the `await` expression evaluates to that result.

That event loop is the single driver at the edge of the program.
Each request passes through every awaiting caller on its way to that loop,
so an `await` in a function makes every caller `async` in turn.

An `async def` function can also contain `yield`.
The result is an *asynchronous generator*, which has two drivers at once.
Each `await` sends a request up to the event loop,
while each `yield` hands a value to the `async for` loop that consumes it:

```python
# async_generator.py
import asyncio
from collections.abc import AsyncGenerator

async def countdown(n: int) -> AsyncGenerator[int]:
    while n > 0:
        await asyncio.sleep(0)
        yield n
        n -= 1

async def main() -> None:
    async for n in countdown(5):
        print(f"{n = }")
    print([n * n async for n in countdown(5)])

asyncio.run(main())
#: n = 5
#: n = 4
#: n = 3
#: n = 2
#: n = 1
#: [25, 16, 9, 4, 1]
```

`asyncio.sleep(0)` models a wait for real I/O.

`async for` is an `await` in loop form:
on each pass it awaits the generator's `__anext__()`.
Like any `await`, it belongs inside an `async def`,
which is why the listing's two loops sit in `main()`.
The *asynchronous comprehension* `[n * n async for n in countdown(5)]` collects the values through the same `__anext__()` calls.

A class can supply that `__anext__()`,
the way `Fibonacci` in [Iterators](22_Patterns--Iterators.md#generators)
supplies `__next__()`:

```python
# async_iterator_class.py
import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import override

@dataclass
class Countdown(AsyncIterator[int]):
    n: int

    @override
    async def __anext__(self) -> int:
        if self.n == 0:
            raise StopAsyncIteration
        await asyncio.sleep(0)
        value = self.n
        self.n -= 1
        return value

async def main() -> None:
    it = Countdown(3)
    print(await it.__anext__())
    print(await it.__anext__())
    async for n in it:
        print(f"{n = }")

asyncio.run(main())
#: 3
#: 2
#: n = 1
```

`AsyncIterator` supplies an `__aiter__()` that returns `self`,
so the class writes `__anext__()` alone.
`__anext__()` is a coroutine function,
which is why `async for` must await what it returns.
`main()` makes the first two calls itself, and the `async for` makes the rest.
The loop ends when `__anext__()` raises `StopAsyncIteration`,
the asynchronous counterpart of `StopIteration`.
The asynchronous generator `countdown()` writes the same loop as its body,
with a `yield`, and leaves the two methods to Python.

An asynchronous generator drops the return channel,
so `AsyncGenerator[YieldType, SendType]` takes two parameters where `Generator` takes three.
Writing `return` with a value in an asynchronous generator is a `SyntaxError`,
as is `yield from`.
The send channel remains as `asend()`, alongside `athrow()` and `aclose()`.
Each of the three returns an awaitable for the caller to `await`.

## Half a Coroutine by Design

PEP 255 added generators to Python 2.2 in 2001 so that a function can produce values one at a time.
The function pauses after each value.
When the caller asks for the next value,
the function resumes from the point where it paused.
The need for that pause appears whenever the producer keeps state from one value to the next while the consumer has a loop of its own.
The PEP's example, the standard library's `tokenize()`,
keeps its place in the source text.
A recursive tree walk keeps a whole recursion in progress between one node and the next.
The consumer needs its own local variables and loops to track what it has seen,
and it may stop early.

In a single thread, Python had three ways to write such a producer.
Each comes with a compromise.

The first way is for the function to invoke a callback on each computed value:

```python
# fibonacci_callback.py
from collections.abc import Callable

def fibonacci(
    n: int, callback: Callable[[int], None]
) -> None:
    a, b = 0, 1
    for _ in range(n):
        callback(a)
        a, b = b, a + b

def summing() -> Callable[[int], None]:
    total = 0
    def consume(value: int) -> None:
        nonlocal total
        total += value
        print(f"{value=} {total=}")
    return consume

fibonacci(7, summing())
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
```

The callback needs a variable that survives from one call to the next,
to hold the running `total`.
`summing()` returns the `consume` function,
which captures `total` as a [closure](40_Functional--Foundations.md#closures)
variable, so `total` outlives `summing()`'s call.
The `nonlocal` statement lets `consume()` assign to the captured `total`.

`fibonacci()` controls how many times `consume()` runs and when the sequence ends.
`consume()` receives one value per call and cannot ask for the next value or stop the loop early.

The second way is for `fibonacci()` to return a list containing every computed value:

```python
# fibonacci_list.py
def fibonacci(n: int) -> list[int]:
    values: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        values.append(a)
        a, b = b, a + b
    return values

total = 0
for value in fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
```

This `fibonacci()` is the generator `fibonacci()` in `iterators.py` from [Iterators](22_Patterns--Iterators.md#generators)
with `values.append(a)` in place of `yield a`.
Because the list holds all the values,
the sequence must be finite and fit in memory.

The third way, older than PEP 255's generators,
is an iterator class with a `__next__()` that returns one value per call:

```python
# fibonacci_class.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass
class Fibonacci(Iterator[int]):
    remaining: int
    _a: int = field(default=0, init=False)
    _b: int = field(default=1, init=False)

    @override
    def __next__(self) -> int:
        if self.remaining == 0:
            raise StopIteration
        self.remaining -= 1
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        return value

total = 0
for value in Fibonacci(7):
    total += value
    print(f"{value=} {total=}")
#: value=0 total=0
#: value=1 total=1
#: value=1 total=2
#: value=2 total=4
#: value=3 total=7
#: value=5 total=12
#: value=8 total=20
```

The class moves the locals `a` and `b` into the attributes `_a` and `_b` and turns the control flow inside out.
In `fibonacci_callback.py`,
the running function's stack frame holds the `for` loop's count of values.
In `Fibonacci`, that count is the attribute `remaining`,
which `__next__()` decrements and tests on every call.

Each approach gives up one side's loop:

- The callback turns the consumer inside out:
  the body of its loop becomes `consume()`,
  a function the producer's loop calls.
- The list keeps both loops but runs the producer's loop to completion before the consumer's loop starts.
- The class turns the producer inside out:
  its loop becomes the bookkeeping in `__next__()`.

All three approaches work around the same missing ability:
pausing `fibonacci()` in the middle of its loop, handing out a value,
and resuming where it stopped.
A generator lets the producer and the consumer each keep their own loop.

A pair of loops passing values in both directions resembles a queue like the ones in [Coordinating Threads with Queues](19_Techniques--Concurrency.md#coordinating-threads-with-queues),
with three differences:

1. A generator holds no items.
   A value goes out, the generator stays suspended until the driver sends a value,
   and then the next value goes out.
2. Control moves with the value,
   so at any moment either the driver or the generator body is running.
3. The generator cannot start an exchange.
   It runs when its driver resumes it, and it answers that driver alone.

The PEP's authors wanted the useful part of a coroutine without the whole mechanism.
The useful part is that a suspended generator keeps its [execution frame](05_Foundations--Functions.md#names-inside-a-function)
alive and resumes it on the next call.
Python discards a function's stack frame when the function returns.
At `yield`, Python unlinks the generator's execution frame from the call stack,
so the frame stops being a stack frame.
The execution frame lives on the heap inside the generator object,
which exposes it as `gi_frame`, with its locals and position intact.
The next `next()` links that frame back into the call stack.

The PEP names Ralph Griswold's Icon language, with CLU and Sather,
as the models.
Icon's `suspend` statement produces a value and leaves the procedure ready to produce another.
CLU and Sather use the word `yield` for the same step inside an iterator,
which hands one element at a time to a loop.

### The Restriction Behind the Driver

PEP 255 kept the suspended frame and dropped a coroutine's ability to hand control to any other coroutine.
Each `yield` hands control back to whoever called `next()` or `send()`.
Handing control anywhere else means saving and restoring the C stack as well.
Stackless Python's coroutines do that,
and the PEP calls Stackless "a controversial rethinking of the Python core."
The suspended generator is the one-shot continuation that [What a Suspended Generator Holds](#what-a-suspended-generator-holds)
describes.
The restriction says who resumes it: the code that called `next()` or `send()`.
That restriction is why a driver exists.
Something must call `next()` and `send()`,
and since a generator cannot name that something, you write it.

In May 1999, two years before the PEP,
Tim Peters called generators "half a coroutine" on python-dev.
The other half came with PEP 342, written in 2005,
which added the send channel to Python 2.5 in 2006.
Simulations, games, and asynchronous I/O need to pass a value or an exception into a generator at its suspension point,
so `send()`, `throw()`, and `close()` arrived together.
The PEP describes a scheduler that runs many generators as a "trampoline,"
the shape of `task_runner_send.py`.
`yield from` (PEP 380, Python 3.3, 2012) completes the set.
A delegating generator passes all three channels through to the innermost generator,
so you can compose a conversation from parts that never refer to their driver.

An event loop is one such driver.
`async`/`await` (PEP 492, Python 3.5, 2015)
is the same machinery with a syntax that marks a function as one the event loop resumes.
An Effect system builds on a generator rather than a full coroutine,
for the reason the 2001 design chose the half it did.
A generator hands each request to the code that resumed it.
That code is the driver you write.

[Stateless](46_Effects--Stateless.md)
builds on all three of this chapter's ideas.
It describes a function by what it requests and writes those requests into its return type.

## Exercises

Try each exercise before opening its [solution](../Solutions/45_Effects--Generators/).

1.  Write `tally()`, a generator that yields a prompt string,
    receives an `int` for each prompt, and returns the total once it has three.
    Give it the full three-parameter annotation,
    then drive it with `next()` and `send()` and read the total off `StopIteration`.
2.  `drive()` answers from a `dict`.
    Write a second driver that answers from an `Iterator[Answer]`, in order,
    and run `interview()` under both.
    Explain what, if anything, needed to change in `interview()`, and why.
    Give your driver fewer answers than questions and say what it returns.
    `StopIteration` now means two different things in the same loop.
    Keep them apart.
3.  Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()`,
    adding its sum to the total, and extending the loop to `[1, 2, 3, 4, 5, 6]`.
    Write down the sequence of printed lines before running it.
4.  Remove `yield from` in `yield_from_nested.py`,
    leaving `profile: Result = interview()`.
    Run `ty check` and the script, and explain both results.
    Which one told you more,
    and what does the type checker say once you remove `profile`'s annotation?
5.  Rewrite `sequence()` in `yield_from_arguments.py` as a generic function,
    `sequence[R](*steps: Generator[Question, Answer, R])`,
    returning `Generator[Question, Answer, list[R]]`.
    Run `ty check` and the script,
    and explain why `drive()` rejects the call while the script runs.
    Then write a wrapper that joins the list into a `Result`,
    so `drive()` stays unchanged,
    and say what the type checker infers for `R` at each call.
6.  `report()` in `yield_from_return.py` yields its lines and returns `None`.
    Rewrite it to return the character count as well,
    and give it the full annotation.
    Then write a caller that delegates to it with `yield from` and yields that count in a line of its own,
    and say which type parameter carries each of the two values.
7.  Explain why a driver must prime with `next()` rather than `send(None)`,
    given that the two are equivalent at runtime.
    `send_none_is_next.py` has the answer.
    State it in terms of the `SendType`.
8.  [A Vending Machine](31_Patterns--State_Machines.md#a-vending-machine)
    keeps its current state in an attribute and looks up each transition in a table.
    Write a simplified version as a single generator instead.
    It collects money, takes two digits, then dispenses or refuses.
    It yields its current state and receives each event with `send()`,
    so the position in the generator's body carries the state.
    This generator's `yield` runs in the opposite direction from `interview()`'s `yield`.
    Here `yield` reports the state the machine reached instead of requesting something the machine needs.
    Say which of the two versions you would rather extend with another state,
    and why.
9.  Replace `proxy()`'s loop in `answering_proxy.py` with the single line `return (yield from inner)` and run `drive()` over the same `known` table.
    Explain from the output why this `proxy()` cannot answer `town`,
    and say what a generator must do to answer one request and relay the rest.
