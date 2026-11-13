# Generators

> A generator is a *resumable function*: it can pause partway, hand out a value,
> and continue with its state intact when its driver sends back a value.
> An Effect system runs on that conversation.

A function's position in its body is state.
An ordinary call keeps that state for the caller alone.
The called function starts at its first line every time,
so a function that hands out one result per call must record its progress in variables and find its place again on each call.
A generator hands a value to its caller and keeps its position and its local variables,
which lets it stop in the middle of a loop, or of a conversation,
and continue from that point.

[Iterators](22_Patterns--Iterators.md#generators)
presents generators as a way to produce values lazily:
a function containing `yield`,
driven by a `for` loop that takes one value at a time.
Producing values is half of what a generator does.

`yield` is an expression,
which means a generator can receive a value as well as hand one out,
and it can return a final result when it finishes.
Thus, a generator is not a sequence but a conversation.
It yields a request, suspends, and continues when a caller sends the answer.
This gives a generator three *channels*:

- Values go out through `yield`
- Values come in through `send()`
- One value goes out through `return`

This chapter covers:

- The full three-channel annotation
- The *driver* (the loop that runs such a conversation)
- `yield from`, which composes generators that run under any driver
- `throw()` and `close()`,
  which raise an exception at a suspended generator's `yield`
- Expanded drivers: a state machine with one generator per state,
  a scheduler that runs many generators, and the event loop behind `await`
- Why a Python generator is half a coroutine,
  and why the other half is the driver you write

[Stateless](46_Effects--Stateless.md)
builds an Effect system on the three channels, the driver, `yield from`,
and `throw()`.

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
`Iterator` has the yield channel alone,
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
query1: Question = next(conversation)
print(f"{query1 = }")
#: query1 = 'name'
query2: Question = conversation.send(Answer("Alice"))
print(f"{query2 = }")
#: query2 = 'town'
query3: Question = conversation.send(Answer("Wonderland"))
print(f"{query3 = }")
#: query3 = 'friend'
print(inspect.getgeneratorlocals(conversation))
#: {'name': 'Alice', 'town': 'Wonderland'}
try:
    conversation.send(Answer("Rabbit"))
except StopIteration as stop:
    result: Result = stop.value
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
print(inspect.getgeneratorstate(conversation))
#: GEN_CLOSED
print(inspect.getgeneratorlocals(conversation))
#: {}
```

The last `send()` resumes `interview()`'s body,
which encounters `return` instead of another `yield`,
so the generator returns its `Result`.
The caller receives that `return` as a `StopIteration`,
and the `Result` arrives as the exception's `value`.
The listing catches `StopIteration` in a `try` statement because a `for` loop would discard the exception.
A `for` loop treats `StopIteration` as the normal end of the loop and drops the `Result` along with the exception.

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
shows, calling `next()` on an exhausted iterator raises `StopIteration`.
When that call sits inside a generator body,
the `StopIteration` it raises is the body's own,
so the driver receives a `RuntimeError` rather than a finished generator.

## What a Suspended Generator Holds

A suspended generator preserves two things:

- Every local variable
- The `yield` at which its body suspended

Resuming runs the body from that `yield`, with every local variable intact.
In `drive_by_hand.py`,
`inspect.getgeneratorlocals()` shows the values of `name` and `town` that the generator keeps while it waits for the third answer.
After the body returns,
`inspect.getgeneratorstate()` reports `GEN_CLOSED` and `inspect.getgeneratorlocals()` reports `{}`.
At `return`, Python discards the generator's [execution frame](05_Foundations--Functions.md#names-inside-a-function)
and every local variable stored in it.
The `yield` and the locals together are the generator's state.

A [closure](40_Functional--Foundations.md#closures)
keeps its captured variables between calls,
but each call runs its body from the top.
The generator keeps its locals and the `yield` at which it stopped,
so a `yield` inside a `for` loop resumes in the iteration that suspended it,
with the loop variable still bound.
The generator is an ordinary object,
so that state lasts until the body finishes or the program drops its last reference to the generator.

The suspended generator is what [Native Effect Management](44_Effects--Effect_Management.md#native-effect-management)
calls a continuation: the rest of the computation from the `yield` forward.
A [handler](44_Effects--Effect_Management.md#native-effect-management)
can do three things with a continuation: resume it once, discard it,
or resume it several times for a retry or a backtracking search.
A generator's driver can do the first two.
It resumes the continuation once with `send()`.
To discard it, the driver drops the last reference to the generator.
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

### The Driver

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

`show_state=True` adds the generator's state to each line of the trace.

The type checker verifies each `Question` the generator yields and each `Answer` that `drive()` sends.
The built-in `StopIteration.value` has type `Any`,
so the type checker cannot ensure that `drive()` returns a `Result`.

Each `try` wraps a call that resumes the generator, `next()` or `send()`,
because a `StopIteration` from either means the conversation finished.
The `try` around the priming call catches a conversation that returns before it asks anything.
Any other call that can raise `StopIteration` belongs outside both `try` blocks.
A driver that reads its answers from an iterator, for example,
gets `StopIteration` from `next()` on the answers when they run out.
If the `next()` on the answers sits inside one of the `try` blocks,
the `except StopIteration` clause catches that exception as the end of the conversation,
so the driver returns `None` as the result.

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
`next()` runs `watch()`'s body after `watched = watch()` binds the name.

The annotation is `Generator[str]` rather than `Iterator[str]`,
because `inspect.getgeneratorstate()` takes a `Generator` and the type checker rejects an `Iterator` argument.

### Why a Generator and Not a Coroutine

Every answer `interview()` receives comes from its driver.
Swapping `drive()`'s dictionary for a database, or for `input()`,
changes `drive()` and leaves `interview()` as it is.

For managing Effects,
a generator is more useful than a coroutine because you write the driver.
A coroutine's requests go to an event loop,
whether `asyncio`'s loop or one you write yourself.
Each request must be an awaitable object built for that loop.
A generator's requests go to the code that calls `next()` and `send()`,
and a request can be any value.

A generator yields a request out, and the driver sends the answer back in.
The driver chooses each answer,
so the same generator runs unchanged under different drivers.
That separation of a request from its fulfillment is the core of an [Effect Management System](44_Effects--Effect_Management.md#effect-management-systems)
(EMS).

`interview()` and `drive()` form an EMS in miniature.
The generator declares requests.
The driver interprets them.

### A Request Built from an Answer

`interview()` asks the same three questions no matter what answers it receives.
A generator can build its next request from the answer it receives:

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

`Question(f"pet of {name}")` carries the `Answer` to `name` into the next request.
The first table answers `name` with `Alice`,
so the generator asks `pet of Alice`, and the table holds that question.
The second table answers `name` with `Bob`, so the generator asks `pet of Bob`.
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
which wraps the generator function so that each generator it creates serializes the threads' calls.

## `yield from` Delegates to an Inner Generator {#yield-from-composes-descriptions}

An EMS needs a request made deep inside a program to reach the driver at its edge.
Generators provide that path because they nest.
`yield from` delegates to an inner generator until that generator finishes.
During that delegation,
the outer generator sits suspended at the `yield from` expression,
and the driver's calls on the outer generator reach the inner one.
Every request the inner generator yields passes out to the driver,
and every answer the driver sends passes back down to the `yield` where the inner generator waits.
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

"To exhaustion" means each `yield from` stays with its target,
through every `next()` call, until that generator finishes.
Exhaustion is transitive.
`top()`'s single `yield from` finishes when every generator beneath it finishes,
so `list(top())` receives one flat sequence.

If `outer()` wrote `yield one()` without `from`,
it would yield the generator object as a single value,
and `list(outer())` would show `<generator object one at ...>` in place of `'only'`.

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
    yield f"{size} characters"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '12 characters']
```

The yield channel and the return channel end in different places.
Each item `emit()` yields passes through `report()` to `list()`.
The `Size` that `emit()` returns stops one level up, in `report()`,
as the value of the `yield from` expression.
A `yield from` therefore works like a function call:
`report()` calls `emit()` and gets its result back,
while the values `emit()` yields go to the driver.

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
so the `Returned` appears as the last output line.
`report()`'s annotation widens to `Iterator[Yielded | Returned]`,
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
The outermost `visit()` returns the `Counter` for the whole garden.

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
Inside the same `send()` call,
`both()` continues to `[2]` and `collect("beta")` runs to its first prompt.
One `send()` therefore ends one inner generator and produces the first prompt of the next,
so `alpha got 1 and 2` and `beta needs a value` sit on adjacent output lines.
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
`Answer` as the `SendType` goes from the driver to the `yield` inside `ask()`.
`Answer` as the `ReturnType` goes from `ask()` up to `interview()`,
which binds it to `name`, `town`, or `friend`.

This listing imports `drive()` unchanged.
The requests now come from `ask()`, one generator below `interview()`,
and `yield from` passes each one up to the driver,
so `drive()` sees the same `Question`s it saw in `interview_generator.py` and prints the same trace.
`ask()` yields a `Question` and receives an `Answer`,
so `ask()` runs unchanged under any driver that answers `Question`s.
A single loop at the edge of the program interprets requests yielded at any depth.

### Relaying, Not Answering

`drive()` and `yield from` both run a generator's body one `yield` at a time and both finish at `StopIteration`,
so they are easy to confuse.
In `yield_from_delegates.py`, `drive()` receives `interview()`'s `Result`.
Here, a `yield from` in `survey()` receives that `Result`:

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

`interview()`'s `Result` arrives as the value of `yield from interview()` instead of as `stop.value` in the driver.
`interview()`'s questions reach `drive()` through three generators rather than two.

![Requests reach the one driver; results stop one level up.](_images/yield_from_relay)

Each `yield from` passes the `Question` up and the `Answer` down unchanged,
so the trace repeats the three request lines of `yield_from_delegates.py` before the new one.
The `Result` goes one level up and stops,
as the value of `survey()`'s `yield from`.

`survey()` composes `interview()` and `ask()`.
Both come from `yield_from_delegates.py` unchanged,
and neither refers to `survey()` or to the driver.
That is what the Effects chapters mean by composing:
a conversation assembled from conversations written before it.

The outermost generator still needs code that calls `next()` and `send()`,
so the listing ends with a `drive()` call.
At any depth of delegation, the program has one driver.

`drive()` and `yield from` differ in how they respond to a request.
`drive()` answers it.
The generator yields a `Question`, `drive()` looks it up,
and the request stops there.
`yield from` relays the request upward and passes the answer back down.

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
`proxy()` has the same annotation as `interview()`, so `drive()` accepts either:

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
in Stateless, where a handler answers the requests `supply()` gives it and re-yields the rest to the handler outside it.

The priming call to `next()` sits in a `try` because `proxy()` is a generator,
and a `StopIteration` that propagates out of a generator's body becomes a `RuntimeError`.
`next(inner)` runs `inner`'s body up to its first `yield`.
How much code runs before that point depends on the generator.
A generator that opens with a `yield from` continues into its delegate and stops at the delegate's first `yield`.
When a generator returns before its first `yield`,
`next(inner)` raises `StopIteration`.
`sequence()` in `yield_from_arguments.py` does that when its `steps` tuple is empty.

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

- `throw(exc)` raises `exc` at the `yield`.
- `close()` is `throw(GeneratorExit)` followed by a runtime test,
  inside `close()`, of how the body responded.
  A body that lets the exception propagate finishes on its own,
  and `close()` returns.
  A body that catches the exception must then return instead of yielding again,
  or `close()` raises a `RuntimeError` in the driver.

Both methods are called by the driver that holds the generator object.

After `close()`, the generator returns,
or it lets `GeneratorExit` propagate out of its body.
Either way, the generator finishes,
and `inspect.getgeneratorstate()` reports `GEN_CLOSED`.
`close()` then returns to the driver, and the driver's next statement runs.
If the cleanup raises a different exception, the generator still closes,
and that exception comes out of `close()`.

Why does the driver need methods to raise exceptions inside the generator,
when Python has a `raise` statement?
`raise` produces its exception in the function that executes it,
and the exception then propagates up through that function's callers.
While the driver runs, the generator waits at its `yield`, off the call stack.
A `raise` in the driver therefore propagates to the driver's callers and never reaches the generator's `except` and `finally` clauses.
`throw()` and `close()` resume the generator at its `yield`,
then raise an exception there.
The generator's `except` clauses catch it and its `finally` clauses run.

### An Exception at the `yield`

A generator body chooses what to do with an exception that arrives at its `yield`.
It can handle the exception and yield again, clean up,
or let the exception end the generator:

```python
# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def worker() -> Generator[str, None, str]:
    try:
        try:
            yield "ready"
            print("resumed")
        except ValueError as e:
            print(f"caught: {e}")
            yield "recovered"
        finally:
            print("cleanup")
    except GeneratorExit:
        return "closed"
    return "done"

g = worker()
print(next(g))
#: ready
print(g.throw(ValueError("bad input")))  # [1]
#: caught: bad input
#: recovered
print(g.close())  # [2]
#: cleanup
#: closed
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = worker()
print(next(g))
#: ready
expect(TypeError, g.throw, TypeError("stop"))  # [3]
#: cleanup
#: [TypeError] stop
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = worker()
print(next(g))
#: ready
expect(StopIteration, next, g)  # [4]
#: resumed
#: cleanup
#: [StopIteration] done
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
```

At `[1]`, `[2]`, and `[3]` the exception arrives in place of a value,
so the body goes from the `yield` straight to an `except` or `finally` clause,
skipping `print("resumed")`.

At `[1]`, `g.throw(ValueError("bad input"))` resumes `worker()`,
and `yield "ready"` raises `ValueError` instead of returning a value.
The `except ValueError` clause catches it and yields `"recovered"`.
The generator waits again, now at `yield "recovered"`.
`throw()` returns that yielded value to the driver, as `next()` and `send()` do,
so `print()` shows `recovered`.

At `[2]`, `g.close()` raises `GeneratorExit` at `yield "recovered"`.
That `yield` sits inside the `except ValueError` handler.
An exception raised inside a handler skips the sibling `except` clauses of its own `try`,
so the clause for `GeneratorExit` wraps the whole statement.
The exception leaves the inner `try` through its `finally` block,
which prints `cleanup`.
The outer `except GeneratorExit` clause then catches it and returns `"closed"`.
`close()` hands the driver the value the generator returns while handling `GeneratorExit`,
so the driver prints `closed`,
and the call returns the way an ordinary method call does.

At `[3]`, a fresh `worker()` waits at `yield "ready"`,
and `g.throw(TypeError("stop"))` raises `TypeError` there.
No `except` clause specifies `TypeError`,
so the exception leaves the inner `try` through its `finally` block,
which prints `cleanup`,
and passes the outer `except GeneratorExit` clause unmatched.
Leaving the body ends the generator, as a `return` would.
The `TypeError` then comes out of the driver's `throw()` call,
where `expect()` reports it.

At `[4]`, the driver calls `next(g)` instead of `throw()`,
so the body resumes after `yield "ready"`, prints `resumed`,
and leaves the inner `try` through its `finally` block.
The body then reaches `return "done"`,
and that value arrives in the driver as `StopIteration.value`,
which `expect()` prints.
All three generators end in `GEN_CLOSED`.

A generator yields a request and waits while the driver carries out the request.
When the attempt succeeds, the driver calls `send()` with the answer.
When the attempt fails, say the file the generator asks for is missing,
the driver calls `throw()` with the exception the attempt raises,
so the generator learns which failure occurred and chooses what to do about it.
The generator either handles the exception and yields again,
or lets it propagate.
An exception that propagates out of a generator ends that generator.

`throw()` and `close()` differ in who chooses the exception.
With `throw()`, the driver chooses it,
and the exception's class tells the generator which failure occurred.
The body's `except` clauses specify the failures the generator handles.
A clause that handles one yields the next request,
as `worker()` does at `[1]` in `throw_close_basics.py`.
`close()` always produces `GeneratorExit`, so the exception carries one meaning:
finish the generator.
A generator that catches `GeneratorExit` runs its cleanup and must then end.

Most conversations end when the generator returns.
When the driver finishes first, with the generator still waiting at a `yield`,
it calls `close()`, and `GeneratorExit` arrives at that `yield`.
The cleanup that runs is the generator's own code,
a `finally` clause or an `except GeneratorExit` around the `yield`.
Then the generator ends.

### An Exception Raised in the Generator

`throw()` and `close()` deliver an exception from the driver into the generator.
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
The `send()` call at `[2]` then raises that `ValueError` in the driver.
`GEN_CLOSED` shows that the exception shut down the generator.

In both directions, an exception passes through a method call that the driver made on the generator object.

### Stopping Early with `close()` {#stopping-early-with-close}

To end a generator early, a driver calls `close()`.
A generator paused at a `yield` still holds the resources it acquired before the pause:
a file or a lock inside a `with` statement, a connection, a transaction.
Here we see the typical case of a driver that has the answer it needs before the generator yields its last value:

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
print(inspect.getgeneratorstate(sensor))
#: GEN_CLOSED
```

`first_above()` returns at `[1]` with the first reading over the limit.
`readings()` stays paused at its `yield`,
with the sensor on and two readings still in `pending`.
`sensor` still holds the generator,
which `inspect.getgeneratorstate()` reports as `GEN_SUSPENDED`.
`close()` at `[2]` raises `GeneratorExit` at that `yield`.
The `except GeneratorExit` clause runs when the driver stops early,
and reports what the stop left unread.
The `finally` clause runs on every ending and turns off the sensor.

A generator may catch `GeneratorExit` as long as it then finishes,
as `readings()` does by reaching the end of its body.

A driver that stops without calling `close()` leaves the generator paused.
When Python's garbage collector reclaims a paused generator,
it calls that generator's `close()` method.
`GeneratorExit` arrives at the paused `yield` as it does at `[2]`,
and the `finally` block runs at collection time.
Calling `close()` yourself runs the `finally` block at a point you choose.

A second `close()` is safe.
On a `GEN_CLOSED` generator,
`close()` returns `None` and leaves the generator as it is.
A generator the driver closed is `GEN_CLOSED` at collection time,
so its `finally` block runs once.

A generator's body starts when the driver calls `next()`.
Until then, the generator is `GEN_CREATED`.
`close()` changes that generator's state from `GEN_CREATED` to `GEN_CLOSED`,
and the body never starts.
Closing `readings()` before its first `next()` prints nothing:
the sensor never turns on,
and execution never enters the `try` statement whose `finally` clause turns it off.

### `close()`: The Generator Must Finish {#close-requires-the-generator-to-finish}

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

If a generator yields inside a `finally` clause,
`close()` also raises a `RuntimeError` with the message `generator ignored GeneratorExit`.
As `GeneratorExit` propagates out of that generator,
Python runs the `finally` clause.
The `yield` there suspends the generator again before it can finish.

When the driver calls `close()`, the `RuntimeError` arrives in the driver,
as in `throw_and_close_gotcha.py`.
When the garbage collector [calls `close()` on a paused generator it reclaims](#stopping-early-with-close),
the `RuntimeError` arrives in the collector.
Python displays it as an "Exception ignored" message and continues.

A generator for a driver must therefore finish when `GeneratorExit` arrives,
by cleaning up and returning.

### Through `yield from` to the Innermost Generator {#throw-and-close-reach-the-innermost-generator}

A `yield from` forwards `throw()` and `close()` to the generator paused at the innermost `yield`:

```python
# throw_through.py
from collections.abc import Generator

def innermost() -> Generator[str]:
    try:
        yield "innermost ready"
    except ValueError as e:
        print(f"innermost caught: {e}")
        yield "innermost recovered"
    finally:
        print("innermost cleanup")

def outer() -> Generator[str]:
    try:
        yield from innermost()
    finally:
        print("outer cleanup")

g = outer()
print(next(g))
#: innermost ready
print(g.throw(ValueError("bad input")))
#: innermost caught: bad input
#: innermost recovered
g.close()
#: innermost cleanup
#: outer cleanup
```

The driver calls `g.throw()`, but `innermost()` prints the `caught` line.
`outer()` is paused at its `yield from` expression,
and `innermost()` is paused at its `yield`.
`yield from` forwards the exception to that innermost `yield`.
`innermost()`'s `except` clause handles it and yields `"innermost recovered"`.
`yield from` relays that value to the driver, as it relays every yielded value.
If the exception propagates out of `innermost()`, it propagates into `outer()`,
as if `outer()`'s `yield from` expression had raised it.
`outer()`'s `finally` block then runs as the exception leaves.

`g.close()`, like `throw()`, reaches `innermost()` through the `yield from`.
Python raises `GeneratorExit` in `innermost()` first, then in `outer()`,
so the two cleanup lines print from the inside out.
One `close()` call on the outermost generator stops that generator and every generator beneath it,
and each one runs its cleanup.

### Sagas with Generators {#sagas-with-generators}

A [*Saga*](39_Patterns--Pattern_Catalog.md#distributed-and-cloud)
runs a long transaction as a series of steps.
When a later step fails, each earlier step undoes what it did,
most recent first.
Each step is an undoable [*Command*](27_Patterns--Function_Objects.md#a-callable-object-as-a-command):
an action paired with the operation that reverses it.
We can create a saga using one generator per step,
each delegating to the steps after it.
A failure is an exception that starts in the generator of the step that failed.
The exception propagates outward through the generators of the earlier steps,
and a step's undo is an `except` clause around its `yield from`:

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

def book() -> Generator[str]:
    return step(
        "flight", step("hotel", step("taxi", step("card")))
    )

print(list(book()))
#: ['do flight', 'do hotel', 'do taxi', 'do card']
booking = book()
print(next(booking))
#: do flight
print(next(booking))
#: do hotel
print(next(booking))
#: do taxi
expect(Failed, booking.throw, Failed("no taxi"))
#: undo hotel
#: undo flight
#: [Failed] no taxi
```

Each step yields its command, then delegates inside a `try`.
In `list(book())` every step succeeds, so each `yield from` finishes normally.

Three `next()` calls leave `booking` paused in the taxi step,
at the `yield` that produced `do taxi`.
To report the taxi's failure, the driver calls `booking.throw()`,
raising `Failed` at that `yield`.
That `yield` comes before the taxi step's `try`,
so `Failed` leaves the taxi step, and the card step never starts.
The exception then propagates up through the `yield from` in the hotel step and the one in the flight step.
Each `except` clause prints its step's undo line.
The [bare `raise` re-raises the exception the clause caught](04_Foundations--Control_Flow.md#errors-and-exceptions),
so `Failed` continues out to the enclosing step.
The hotel step prints its undo line before the flight step does.
The nesting of the `try` blocks is the undo stack.

A step's action and its undo are often several commands each.
Here both are generators that yield their commands to the driver,
and `step()` delegates to them:

```python
# saga_generators.py
from collections.abc import Generator
from exceptions import expect

class Failed(Exception):
    pass

type Commands = Generator[str]

def commands(*names: str) -> Commands:
    yield from names

def step(
    *, do: Commands, undo: Commands,
    rest: Commands | None = None,
) -> Commands:
    yield from do
    if rest is None:
        return
    try:
        yield from rest
    except Failed:
        yield from undo  # [1]
        raise

def book() -> Commands:
    return step(
        do=commands("reserve seat", "issue ticket"),
        undo=commands("void ticket", "release seat"),
        rest=step(
            do=commands("hold room"),
            undo=commands("release room"),
            rest=step(
                do=commands("book taxi"),
                undo=commands("cancel taxi"),
                rest=step(
                    do=commands("charge card"),
                    undo=commands("refund card"),
                ),
            ),
        ),
    )

print(*book(), sep="\n")
#: reserve seat
#: issue ticket
#: hold room
#: book taxi
#: charge card
booking = book()
print([next(booking) for _ in range(4)][-1])
#: book taxi
print(booking.throw(Failed("no taxi")))  # [2]
#: release room
print(next(booking))
#: void ticket
print(next(booking))
#: release seat
expect(Failed, next, booking)  # [3]
#: [Failed] no taxi
```

In `saga.py`, `throw()` raises `Failed` in the driver.
At `[2]`, `throw()` returns a command.
`Failed` starts in the taxi step's `do`, which is outside that step's `try`,
so the exception leaves the taxi step and the card step never starts.
The hotel step's `except` clause catches `Failed` and delegates to its `undo` at `[1]`.
The `undo` yields `release room`,
and `throw()` returns that command to the driver.
The driver carries it out and calls `next()` for the following ones.
When the hotel step's `undo` finishes,
the bare `raise` sends `Failed` to the flight step,
whose `undo` yields `void ticket` and `release seat`.
`Failed` reaches the driver at `[3]`, after the last undo command.

`book()` creates every `undo` generator, and an `undo` body starts at `[1]`.
The successful run finishes without reaching `[1]`,
and Python discards the four unstarted generators.

[A generator must finish when `GeneratorExit` arrives](#close-requires-the-generator-to-finish),
and a `yield` in an `except` clause looks like a risk to that rule.
The `except Failed` clause in `step()` lets `GeneratorExit` pass,
so `booking.close()` skips `[1]` and finishes each started step.

## One Generator per State

[State Machines](31_Patterns--State_Machines.md)
builds its mousetrap from an `Enum` of rows,
each holding a state's entry message and a transition function.
The engine calls the current state's function on every input.

Every resumption of a generator is a decision point.
From the value that `send()` delivers, the body chooses what to do next:
yield again, or return and finish.
`proxy()` in `answering_proxy.py` chooses with an `if`:
it answers a request found in `known`,
and it yields any other request to the driver.
A `match` on the received input chooses with one `case` per input.
A generator that returns from a `case` moves to a new state.

A generator offers a third design.
Each state is a generator function:

- The entry action is the code before the first `yield`
- Each `yield` reports the state's name and receives the next input
- A transition is a `return` whose value is the next state

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

`Mouse` is the input enum from [Each State Decides](31_Patterns--State_Machines.md#each-state-decides).
`Machine` is a recursive alias: a state yields its name, receives a `Mouse`,
and returns the next state, or `None` to halt.
The `type` statement evaluates its right side lazily,
so the alias can name itself.

Each state's `while True` loop keeps the machine in that state.
An input that matches a `case` returns the next state, which ends the loop.
After any other input,
the loop runs its `yield` again and reports the state's name.
The entry action sits above the loop, so it runs once, on entry.
`holding()`'s entry action is two `print()` calls, the message and the chime.

`return luring()` creates `luring()`'s generator object and hands it out as `waiting()`'s result.
`luring()`'s body starts when an engine delegates to it.
Here, `trampoline()` is the engine and `run_all()` is its driver:

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
        try:
            new_state = machine.send(input_)  # [3]
        except StopIteration:
            return  # [4]
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

run_all(waiting(), [Mouse.ESCAPES])  # [5]
#: Broadcasting cheese smell
#: Waiting mouse escapes -> Waiting
```

The loop at `[1]` is the whole engine.
PEP 342 calls such a loop a *trampoline*: each state returns to the loop,
which bounces into the next state.
`yield from` runs the current state,
relaying each of its `yield`s up to `run_all()` and each `send()` back down.
When the state returns, the loop takes the returned generator as the next state.
Apart from its return type, `trampoline()` has a state's annotation,
so `run_all()` drives it as it drives any generator.

`[2]` primes the machine,
which runs `waiting()`'s entry action and stops at its first `yield`.
Each `send()` at `[3]` delivers one input and returns the name of the state the machine then occupies.
A state that returns `None` ends `trampoline()`'s loop,
so that `send()` raises `StopIteration` and `run_all()` returns at `[4]`.

For `MOVES`, this trace and the trace in `trap_states_demo.py` have the same lines in a different order.
Each entry message prints before the transition line that leads to it.
The entry action runs inside `send()`, in the new state's body,
and `run_all()` prints its line after `send()` returns.
In `state_machine.py` the engine prints the transition line and then calls the new state's `run()`,
so the engine chooses the order.
Here, each state's body runs its entry action.

At `[5]`, `run_all()` sends `Mouse.ESCAPES` to a machine in `Waiting`.
`waiting()`'s one `case` matches `Mouse.APPEARS`,
so its loop yields `Waiting` again, and the trace line ends `-> Waiting`.
The entry message prints once.

[Which Design Should You Use?](31_Patterns--State_Machines.md#which-design-should-you-use)
asks whether an action belongs to the state or to the transition.
Here the choice is between two places in one function rather than between two designs.
Code before the first `yield` is the state's entry action, the Moore shape,
where the action belongs to the state.
Code before a `return` runs on that transition alone, the Mealy shape,
where the action belongs to the transition.
A `print("Door latched")` added above `return holding()` in `trapping()` runs when the mouse is trapped and at no other time.
The Moore shape and the Mealy shape both fit one function with no `action` field.

A state's local variables are its data.
[`VendingMachine`](31_Patterns--State_Machines.md#a-vending-machine)
keeps `amount` on the machine object because every machine shares the enum members.
A generator state keeps such a value in a local and passes it to the next state as an argument.
In a vending machine with one generator per state,
the state that takes the money ends with `return selecting(amount)`,
and `selecting()` receives the amount as a parameter.
In that design, parameters and locals hold the data that `VendingMachine` keeps in attributes.

Exercise 8 writes the vending machine as one generator,
with each state a position in a single generator body.
That design suits a machine that is mostly a sequence.
One generator per state suits a machine like the trap,
whose transitions form a graph.

Chapter 31's `Enum` makes the states a closed set.
Here the set is open: any function that returns a `Machine` is a state.
`test_trap_states.py` iterates over `TrapState` and checks every state against every move;
to reach a state, a test of the generator design drives the machine to it.
If a test must enumerate a machine's states, use chapter 31's `Enum` design.

The generator design has a second limit.
`copy.deepcopy()` and `pickle.dumps()` raise a `TypeError` for every generator,
started or not.
A machine in this design is a generator, so a program cannot copy it or save it.
In the enum designs, the current state is an `Enum` member,
which a [*Memento*](36_Patterns--Memento.md#the-classic-memento)
can store in a field.

### Why a Trampoline

In `trap_generators.py`,
a state returns the next state and `trampoline()` delegates to it.
The alternative is for each state to delegate to the next state itself,
with `return (yield from luring())` in place of `return luring()`.
`tick()` and `tock()` are two states written that way:

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

`trampoline()` keeps the chain one level deep.
`yield from state` finishes when the state returns,
and the loop takes up the next state at the same depth.
[The Restriction Behind the Driver](#the-restriction-behind-the-driver)
says why a driver exists.
Exercise 9 puts the shape at `[1]` into `proxy()` as `return (yield from inner)`,
where it relays every request instead of answering one.

## Many Generators, One Driver

This chapter rests on three ideas:

- Calling a generator function returns a generator object that holds the body and its state.
  A driver runs that body one `yield` at a time with `next()` and `send()`.
- `yield` carries a request out of the body and `send()` carries the answer back in,
  so the body can ask for something and receive the answer.
- `yield from` composes those conversations.
  Each generator in the chain yields to the code that resumed it,
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

`[1]` takes the job at the front of the queue,
and `next()` runs it to its next `yield`.
`[3]` puts that job at the back of the queue, behind the other job,
so the two jobs alternate.
For a finished job, `next(job)` raises `StopIteration`,
and the `continue` at `[2]` skips `[3]`.
`[1]` takes each job out of the queue before `next()` runs,
so a finished job stays out.

We can modify `task_runner()` so that jobs can make requests:

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

The `for` loop primes each job and pairs it with its first request.
When a job finishes before its first `yield`,
`next(job)` raises `StopIteration`.
`next(job)` is inside the argument to `append()`,
so the exception arrives before `append()` runs,
and that job stays out of `ready`.
When a job finishes in the `while` loop, its `send()` raises `StopIteration`.
`popleft()` takes each job out of `ready` before `send()` runs,
and the `continue` skips the `append()` that puts a job back.

`index()` discards what it receives.
It yields only to take turns.

## The Driver You Already Use

`asyncio.run()` starts the `asyncio` event loop.
The event loop is a driver like `task_runner()` in `task_runner_send.py`.
A coroutine object has `send()`, `throw()`, and `close()`, as a generator does.
A coroutine object is not an iterator, so `next()` on it raises a `TypeError`,
so `send(None)` both starts and resumes it.
The event loop keeps a queue of the tasks that are ready to run,
as `task_runner()` keeps `ready`.
The event loop runs the task at the front of the queue.
Each task holds one coroutine, calls `send(None)` on it,
and receives the value the coroutine yields.

[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
describes `await` as suspending a task until the event loop resumes it.
In this chapter's terms, that suspension is a `yield`.
If a coroutine awaits a `Future` that is still waiting for its result,
the coroutine pauses at the `await`,
and the task's `send(None)` call returns the `Future`.
The `Future` is the request, and its result is the reply.
When the result arrives, the event loop puts the task back in the queue,
and the task calls `send(None)` again,
which resumes the coroutine at the `await`.
If the `Future` has its result when the coroutine reaches the `await`,
the coroutine keeps running.
In both cases the `await` expression evaluates to the `Future`'s result.

The event loop is the single driver at the edge of the program.
An `await` on a coroutine delegates to that coroutine,
as `yield from` delegates to an inner generator,
and it evaluates to the coroutine's return value.
Each request the inner coroutine yields passes through every awaiting caller on its way to the event loop,
so an `await` in a function makes each of those callers `async` in turn.

### Asynchronous Generators

An `async def` function can contain `yield`.
The result is an *asynchronous generator*, which has two drivers at once:
the `asyncio` event loop for its `await`s and an `async for` loop for its `yield`s.
Each `await` passes a request up to the event loop,
while each `yield` hands a value to the `async for` loop:

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

`async for` uses the iteration protocol from [Iterators](22_Patterns--Iterators.md#iteration-comes-built-in)
with two other methods.
When the loop starts,
`async for` makes one `__aiter__()` call in place of `__iter__()`,
on the generator that `countdown(5)` returns.
That generator's `__aiter__()` returns the generator itself.
For each value, `async for` awaits `__anext__()` in place of `__next__()`.
`async for` contains an `await`, so it must be inside an `async def`,
and the `async for` loop and the comprehension are both in `main()`.
The *asynchronous comprehension* `[n * n async for n in countdown(5)]` creates a second `countdown(5)` generator and awaits its `__anext__()` for each value.

A class can supply `__anext__()`,
the way `Fibonacci` in [Iterators](22_Patterns--Iterators.md#generators)
supplies `__next__()`:

```python
# async_iterator_class.py
import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import override

@dataclass(eq=False)
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
    it = Countdown(5)
    print(await it.__anext__())
    print(await it.__anext__())
    async for n in it:
        print(f"{n = }")

asyncio.run(main())
#: 5
#: 4
#: n = 3
#: n = 2
#: n = 1
```

`AsyncIterator` supplies an `__aiter__()` that returns `self`.
`Countdown` inherits that method and defines `__anext__()`.
`__anext__()` is a coroutine function,
so `async for` must await what it returns.
`main()` makes the first two `__anext__()` calls,
and the `async for` makes the rest.
The `async for` ends when `__anext__()` raises `StopAsyncIteration`,
the asynchronous counterpart of `StopIteration`.

`Countdown(5)` produces the same sequence as `countdown(5)` in `async_generator.py`.
`Countdown` keeps `n` in an attribute, defines `__anext__()`,
and raises `StopAsyncIteration` itself.
`countdown()` keeps `n` in a local variable and yields in a `while` loop.
Python gives every asynchronous generator an `__aiter__()` and an `__anext__()`,
and that `__anext__()` raises `StopAsyncIteration` when the generator's body ends.

An asynchronous generator has a yield channel and a send channel and no return channel,
so `AsyncGenerator[YieldType, SendType]` takes two parameters where `Generator` takes three.
Writing `return` with a value in an asynchronous generator is a `SyntaxError`,
as is `yield from`.
In place of `send()`, `throw()`, and `close()`,
an asynchronous generator has `asend()`, `athrow()`, and `aclose()`.
The caller must `await` a call to any of those three.

## Half a Coroutine by Design

The chapter's opening treats a function's position in its body as state.
Halfway through a loop, a function has done part of its work.
Its position determines what it does next.

A call preserves the caller's position and locals.
The caller waits in the middle of its body and continues from that point when the call returns.
An ordinary function on the called side starts at its first line on every call and loses its position and its locals when it returns.

That difference matters when a producer computes a series of values and a consumer uses them one at a time.
The producer and the consumer are each simplest to write as its own loop.
One of the two must call the other.
Without generators, the called function restarts at its first line on every call,
so you cannot write the called side as a loop.
You write it as a state machine:
variables that hold the loop's locals and its position,
and code that reads them on every call to find where to continue.
A generator is a called function that keeps its position and its locals,
so you write the called side as a loop too.

### Conway's Switch

Melvin Conway described the state-machine rewrite in 1963,
in [a paper](https://www.melconway.com/Home/pdf/compiler.pdf)
on the design of a one-pass COBOL compiler.
His example is a subroutine, the "asterisk squasher,"
that reads punched cards and delivers their characters one per call.
The squasher replaces each pair of adjacent asterisks,
the exponentiation operator of FORTRAN and COBOL,
with a single up-arrow character.
Asterisks pair off from the left,
so three in a row become an arrow and an asterisk.
Here is that subroutine as an iterator class, with `^` standing for the arrow:

```python
# squasher_switch.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass
class Squasher(Iterator[str]):
    chars: Iterator[str]
    _held: str = field(default="", init=False)

    @override
    def __next__(self) -> str:
        if self._held:  # [1]
            held, self._held = self._held, ""
            return held
        char = next(self.chars)
        if char != "*":
            return char
        match next(self.chars, ""):
            case "*":
                return "^"
            case "":
                return "*"
            case following:
                self._held = following  # [2]
                return "*"

print(list(Squasher(iter("a**b*c***"))))
#: ['a', '^', 'b', '*', 'c', '^', '*']
```

In Conway's flowchart the cards keep coming.
A Python iterator ends,
so the `next()` call in the `match` statement takes a default of `""`.
When the input ends on a single asterisk,
`case "":` matches that default and delivers the asterisk.

`__next__()` must read the character after an asterisk to tell a single asterisk from a pair.
At `[2]` the call holds a single asterisk and the character after it,
two characters to deliver with one return value.
The call stores the second character in `_held` and returns the asterisk.
The test at `[1]` begins every call and chooses between returning a stored character and reading a new one.
Conway calls that test "a switch which bifurcates the subroutine and selects the part to be used at each call depending on the situation at the last call."
A harder task, he notes, "would necessitate an absurd arrangement of switches."

Conway's alternative is the coroutine:
a routine that passes control to another routine and later continues "at the point where it left off."
Coroutines, he writes, are "subroutines all at the same level,
each acting as if it were the master program when in fact there is no master program."

Written as a generator,
the squasher delivers a single asterisk and the character after it with two statements in a row:

```python
# squasher_generator.py
from collections.abc import Iterator

def squash(chars: Iterator[str]) -> Iterator[str]:
    for char in chars:
        if char != "*":
            yield char
            continue
        match next(chars, ""):
            case "*":
                yield "^"
            case "":
                yield "*"
            case following:
                yield "*"  # [1]
                yield following  # [2]

print(list(squash(iter("a**b*c***"))))
#: ['a', '^', 'b', '*', 'c', '^', '*']
```

The generator suspends at `[1]` with the asterisk delivered and the second character in the local variable `following`.
When the consumer asks for another character,
the body continues from that point and delivers `following` at `[2]`.
A generator suspended at `[1]` has a character waiting,
so its position replaces the switch.
Conway's flowchart of the coroutine version has those two steps in a row:
a write of the asterisk, then a write of the character after it.

### Three Ways to Write the Producer

PEP 255 added generators to Python 2.2 in 2001 so that a called function can hand a value to its caller and keep its position and its locals.
The PEP's motivating example is the standard library's `tokenize()`,
which keeps its place in the source text from one token to the next.
A recursive tree walk keeps a whole recursion in progress between one node and the next.
The consumer needs its own local variables and loops to track what it has seen,
and it may stop early.

Without generators, you have three ways to write such a producer in a single thread.
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
Under the `nonlocal` statement, `consume()` assigns to the captured `total`.

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

The third way is an iterator class whose `__next__()` returns one value per call,
the shape of `Squasher` in `squasher_switch.py`:

```python
# fibonacci_class.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass(eq=False)
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

The class moves the locals `a` and `b` into the attributes `_a` and `_b`,
and each `__next__()` call computes one value,
as one pass of the `for` loop in `fibonacci_callback.py` does.
In that listing, the running function's stack frame holds the `for` loop's count of values.
In `Fibonacci`, that count is the attribute `remaining`,
which `__next__()` decrements and tests on every call.

Each approach gives up one side's loop or the alternation between the two loops:

- The callback turns the consumer inside out:
  the body of its loop becomes `consume()`,
  a function the producer's loop calls.
- The list keeps both loops but runs the producer's loop to completion before the consumer's loop starts.
- The class turns the producer inside out:
  its loop becomes the `remaining` count that `__next__()` decrements and tests.

All three approaches work around the same missing ability:
pausing `fibonacci()` in the middle of its loop, handing out a value,
and resuming where it stopped.
With a generator, the producer and the consumer each keep their own loop.

A pair of loops passing values in both directions resembles the queues in [Coordinating Threads with Queues](19_Techniques--Concurrency.md#coordinating-threads-with-queues),
with three differences:

1. A generator holds no items.
   A value goes out, the generator stays suspended until the driver sends a value,
   and the next value goes out.
2. Control moves with the value,
   so at any moment either the driver or the generator body is running.
3. The generator cannot start an exchange.
   It runs when its driver resumes it, and it answers that driver alone.

### The Suspended Frame

PEP 255's authors wanted the useful part of a coroutine without the whole mechanism.
The useful part is that a suspended generator keeps its [execution frame](05_Foundations--Functions.md#names-inside-a-function)
alive, and a later call resumes it.
Python discards a function's stack frame when the function returns.
At `yield`, Python unlinks the generator's execution frame from the call stack,
so the frame stops being a stack frame.
The execution frame lives on the heap inside the generator object,
which exposes it as `gi_frame`, with its locals and position intact.
The call that resumes the generator links that frame back into the call stack.

The PEP cites the "pleasant solutions" of three earlier languages:
iterators in CLU and Sather, and generators in Ralph Griswold's Icon.
Icon's `suspend` produces a value and leaves the procedure ready to produce another.
CLU and Sather use the word `yield` for the same step inside an iterator,
which hands one element at a time to a loop.

Many languages now have generators.
JavaScript adopted Python's design first,
in Mozilla's JavaScript 1.7 for Firefox 2 (2006):
Python-inspired generators with `send()`, `throw()`, and `close()`.
ES2015 made generators standard, with `yield*` for `yield from`.
TypeScript types the three channels as `Generator<T, TReturn, TNext>`.
PHP and Dart follow the same design,
with delegation as `yield from` and `yield*`.
The languages differ in where the suspended frame lives.
Python keeps the execution frame on the heap.
C# and Kotlin compile the body into a state-machine class,
which holds a field per local and an integer for the suspension point in place of a frame.
Ruby runs an external enumerator's block on a `Fiber`, a full coroutine.
Go 1.23 reverses the protocol.
The loop body becomes a `yield` function that the iterator calls once per value,
so the iterator keeps its frame on the call stack while the body runs.
CLU's iterators, designed in 1975, work the same way.[^clu-history]
In CLU a `yield` calls the loop body,
which returns to the iterator when it finishes.
CLU allows an iterator only in a `for` statement,
so that a program needs a single stack.

### The Restriction Behind the Driver

PEP 255 kept the suspended frame and left out a coroutine's ability to hand control to any other coroutine.
Each `yield` hands control back to the caller of `next()` or `send()`.
In 2001, handing control anywhere else meant preserving part of the C stack along with the frame,
because CPython ran each Python call inside a nested call of its interpreter.
Stackless Python allows such a transfer by keeping Python's state off the C stack.
The PEP calls Stackless "a controversial rethinking of the Python core."

The suspended generator is the one-shot continuation that [What a Suspended Generator Holds](#what-a-suspended-generator-holds)
describes.
PEP 255's restriction says who resumes it:
the code that called `next()` or `send()`.
That restriction requires a driver, the code that calls `next()` and `send()`.
A generator cannot specify its driver, so you write it.

In May 1999, two years before the PEP,
Tim Peters called generators "half a coroutine" on python-dev.
Coroutines, he wrote, are "equal partners," each free to resume any other,
while a generator returns control to its caller.

PEP 342, written in 2005, kept that restriction and added the send channel,
which reached Python 2.5 in 2006.
The PEP calls coroutines "a natural way of expressing" simulations, games,
and asynchronous I/O.
Such programs need to pass a value or an exception into a generator at its suspension point,
which `send()` and `throw()` do.
The PEP also permits `yield` inside `try`/`finally` and adds `close()`,
so that an abandoned generator runs its cleanup code.
The PEP's trampoline combines the loop in `trampoline()` from `trap_generators_demo.py` with a scheduler like `task_runner()` in `task_runner_send.py`.

A generator has a second restriction.
A `yield` suspends one frame,
the frame of the function that contains the `yield`.
A function that the generator calls runs in a frame of its own and cannot suspend the generator's frame,
so a helper that makes a request must be a generator too.
PEP 380 describes the consequence:
"a piece of code containing a `yield` cannot be factored out and put into a separate function in the same way as other code."
The PEP's answer is `yield from`, which reached Python 3.3 in 2012.
The helper is still a generator,
and the generator that calls it delegates to it.
`yield from` relays each request out to the driver and each answer back in,
and it evaluates to the helper's return value,
so you can compose a conversation from parts that never refer to their driver.

An event loop is one such driver.
PEP 492 added `async`/`await` to Python 3.5 in 2015.
The new syntax reuses the generator's implementation and marks a function as one the event loop resumes.
`await` uses the implementation of `yield from`,
so the second restriction holds for it.
An `await` suspends the `async` function that contains it,
so a caller that awaits that function suspends at its own `await` and must be `async` too.
[The Driver You Already Use](#the-driver-you-already-use) states the result:
every awaiting caller is `async` in turn.

An Effect system builds on a generator rather than a full coroutine because of PEP 255's restriction.
A generator hands each request to the code that resumed it.
That code is the driver you write.

[Stateless](46_Effects--Stateless.md) builds on this chapter's three ideas:
the driver, the request and its answer, and `yield from`.
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
10. PEP 255 asks its reader to picture a recursive tree walk as an iterator:
    "to cast that into an iterator framework requires removing the recursion manually and maintaining the state of the traversal by hand."
    Write that iterator for `visit()` in `color_count.py`.
    `Paths` is an iterator class, with no `yield` in it,
    that produces the path lines `visit()` yields, in the same order,
    and leaves out the counts.
    Keep the walk's position in a list that you use as a stack.
    Then say what `Paths` stores that `visit()` leaves to Python.
11. `step()` in `saga.py` takes a name and prints its undo.
    Replace `name` with two functions: `action`,
    which the step calls and whose result it yields, and `undo`,
    which the `except` clause calls.
    Build one booking of a flight, a hotel,
    and a card whose three actions succeed,
    and one whose card action raises `Failed`.
    The driver of the second booking calls only `next()`.
    Say where `Failed` starts,
    and why the hotel and the flight are still undone.
12. Drive a booking from `saga_generators.py` to `issue ticket` and throw `Failed` there.
    Say which command the driver has carried out and which undo commands it receives.
    Then change `step()` so that a step that fails partway through its `do` is undone as well.
    Throw `Failed` at `issue ticket` and at `charge card`,
    and say what an `undo` must now tolerate.

[^clu-history]: Barbara Liskov,
[A History of CLU](https://dspace.mit.edu/handle/1721.1/149734),
    MIT Laboratory for Computer Science, 1992, section 3.10.
    In CLU "a yield effectively calls the loop body,
    which returns to the iterator when it is finished."
    The limits on iterators exist
    "so that CLU programs can make do with a single stack."
    The iterator came from Alphard's generators,
    which the CLU group saw at CMU in the summer of 1975.
