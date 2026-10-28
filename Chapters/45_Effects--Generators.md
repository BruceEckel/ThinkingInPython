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
- `yield from`, which composes generators that do not refer to their driver

[Stateless](46_Effects--Stateless.md) builds an Effect system on these,
but generators are useful on their own.

## Annotating a Generator

Earlier chapters annotate their generators using the short form `Iterator[int]` in [Iterators](22_Patterns--Iterators.md#generators),
and `Generator[str]` in [Context Managers](15_Techniques--Context_Managers.md#a-basic-context-manager).
The short form fits a generator that yields values, receives `None`,
and returns `None`.

A generator that receives and/or returns values needs the full annotation,
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
`Iterator[int]` describes the same one-way generator without relying on the defaults.
It describes the yield channel alone,
so the type checker rejects `send()` on anything annotated `Iterator`.
The long form is necessary when the send and return channels carry a value other than `None`,
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
`NewType` gives each channel a distinct type which makes the logic easer to follow.
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

The `NewType` definitions let the type checker report any annotation mistakes.

The last `send()` resumes `interview()`'s body,
which encounters `return` instead of another `yield`,
so the generator returns its `Result`.
The caller sees that `return` as a `StopIteration`,
and the `Result` arrives as the exception's `value`.
A `for` loop treats `StopIteration` as a normal end-of-loop so it discards the exception and loses the return value.
To read the `ReturnType`, catch the exception yourself,
as `drive_by_hand.py` does.

When the body finishes with `return`,
Python raises `StopIteration` on the generator's behalf.
If a `StopIteration` propagates out of the body instead,
Python converts it into a `RuntimeError`
([PEP 479](https://peps.python.org/pep-0479/)).
As [Asking Consumes an Item](22_Patterns--Iterators.md#asking-consumes-an-item)
shows, calling `next()` on an exhausted iterator raises `StopIteration`,
so a `next()` call inside the body can trigger that conversion.

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
The body runs later, one `yield` at a time,
when the driver calls `next()` or `send()`.
The new generator is suspended before its first statement,
so no `yield` expression is waiting to receive a value.
The first call, which runs the body to its first `yield`,
*primes* the generator.
The priming call must be `next()` or `send(None)`,
otherwise you get `TypeError: can't send non-None value to a just-started generator`.

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
The `# type: ignore` silences that correct report so the listing can show the equivalence.
`interview()` declares `Answer` as its `SendType`,
and `None` is not an `Answer`.
The interpreter accepts `send(None)` as the priming call,
but the type checker rejects it,
because the annotation applies one `SendType` to every call, the first included.
A driver therefore primes with `next()`,
which sends no value and passes the check.

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

For managing Effects,
a generator is more useful than a coroutine because you write the driver.
A coroutine's requests go to an event loop,
`asyncio`'s or one you write yourself.
Each request must be an awaitable object built for that loop.
A generator's requests go to whatever code calls `next()` and `send()`,
and a request can be any value.
The generator yields a request out, and the driver sends the answer back in.
The driver chooses each answer,
so the same generator runs unchanged under different drivers.
That separation of a request from its fulfillment is the core of an [Effect Management System](44_Effects--Effect_Management.md#effect-management-systems)
(EMS).

A driver function runs the generator from start to finish.
It starts the body with `next()`, sends each answer back with `send()`,
and returns the generator's result when the body ends.
`drive()` looks up each answer in a table:

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
    request = next(conversation)
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

The `try` holds only the `send()` call,
because a `StopIteration` inside it means the conversation finished.
Another call that can raise `StopIteration` belongs outside the `try`.
A driver that reads its answers from an iterator, for example,
gets `StopIteration` from `next()` when the answers run out.
Inside the `try`, that exception would look like the end of the conversation.
The driver would then return `None` as the result.

`drive()` runs the conversation.
`show_state=True` puts the generator's state on each line of the trace:

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
That `StopIteration` carries no value,
so `expect()` prints the exception's class name with no message.

The generator and `drive()` take turns.
While the body runs, `drive()` waits inside `send()`,
so only code inside the body can see `GEN_RUNNING`.
That code needs a reference to its own generator,
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
`next()` runs the body after `watched = watch()` has bound the name.

Every answer `interview()` receives comes from its driver.
Swapping `drive()`'s dictionary for a database, or for `input()`,
changes `drive()` and leaves `interview()` as it is.

`interview()` and `drive()` form an EMS in miniature.
The generator declares requests.
The driver interprets them.

Each generator has one driver at a time.
The runtime enforces that pairing, though no annotation expresses it.
If a second thread resumes a generator while another thread is running its body,
the second thread gets `ValueError: generator already executing`.
[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
reproduces the `ValueError` with several threads.
It also shows `threading.synchronized_iterator()`,
which lets those threads share one generator by serializing their calls.

## `yield from` Composes Generators {#yield-from-composes-descriptions}

An EMS needs a request made deep inside a program to reach the driver at its edge.
Generators provide that path because they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down.

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

"To exhaustion" means each `yield from` runs its target until that generator finishes,
and exhaustion is transitive.
`list(top())` receives one flat sequence,
and `top()`'s single `yield from` finishes when the last generator beneath it finishes.

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

The items `emit()` yields pass through `report()` to `list()`,
but its `return Size(total)` goes to `report()` alone,
as the value of the `yield from` expression.
A `yield from` therefore works like a function call:
`report()` calls `emit()` and gets its result back,
while the values `emit()` yields still go to the driver.

`drive_by_hand.py` and `drive()` read a generator's result by catching `StopIteration` and taking its `value`.
`report()` has no `try`, because `yield from` manages the result for you.
When `emit()` finishes,
`yield from` catches the `StopIteration` and evaluates to the exception's `value`.

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
    yield (yield from outer())

for yielded in report():
    print(yielded)
#: Yielded(text='outer')
#: Yielded(text='middle')
#: Yielded(text='inner')
#: Returned(text='Message from inner!')
```

A `Yielded` travels the yield channel and a `Returned` the return channel.
The output traces the descent, and the `Returned` comes back up the same path.
`return (yield from ...)` passes the result through unchanged.

`report()` yields the value of its own `yield from`.
Its annotation widens to `Iterator[Yielded | Returned]`,
because the loop receives both types.
The last output line is the one record that arrived through the return channel.

Because each `yield from` hands a result back to its caller,
a recursive generator can combine results on the way back up a tree.
This example walks a nested dictionary of plants, yields the path to each plant,
and returns a count of each color:

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
    counts: Counter = yield from visit(tree)
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
Note that [`Counter`](03_Foundations--Containers.md#counter)
objects can be added together.
A `visit()` returns its subtree's `Counter` to the `visit()` that called it,
and the `Counter` for the whole garden reaches `census()`.

`yield from` delegates to any iterable, not just a generator;
here it takes a list:

```python
# yield_from_list.py
from collections.abc import Iterator

def relay() -> Iterator[int | None]:
    v: None = yield from [1, 2, 3]
    yield v

print(list(relay()))
#: [1, 2, 3, None]
```

A list's iterator ends with a bare `StopIteration`,
whose `value` defaults to `None`,
so a `yield from` over a list evaluates to `None`.

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
as `Question` and `Result` are in `interview_generator.py`,
so the type checker tells a prompt from a total.
`Value` is a `type` alias,
so the driver's `g.send(value)` passes a bare `int` and still matches the send type.

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
    print(f"send({value}) -> {g.send(value)}")
#: send(1) -> alpha needs another
#: alpha got 1 and 2
#: send(2) -> beta needs a value
#: send(3) -> beta needs another
#: beta got 3 and 4
#: send(4) -> total 10
```

`both()` declares the same yield (`Prompt`) and send (`Value`)
types as `collect()`,
because `yield from` passes both channels through to the driver.
Its return type stays at the default, since `both()` returns `None`.

`g.send(2)` supplies `second`,
so `collect("alpha")` finishes and the `yield from` at `[1]` completes.
`both()` starts the `yield from` at `[2]` in the same call.
One `send()` therefore ends one inner generator and produces the first prompt of the next,
which is why `alpha got 1 and 2` and `beta needs a value` sit on adjacent output lines.
The `yield` at `[3]` gives `send(4)` a value to return.
Without it, `send(4)` would finish `both()` and raise `StopIteration` in the loop.

### All Three Channels

This version of `interview()` makes each request through a helper, `ask()`,
and delegates to it with `yield from`:

```python
# yield_from_delegates.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer: Answer = yield question
    print(f"  ask() received {answer}")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    friend: Answer = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#:   ask() received Alice
#: request = 'town', answer = 'Wonderland'
#:   ask() received Wonderland
#: request = 'friend', answer = 'Rabbit'
#:   ask() received Rabbit
#: Alice of Wonderland, friend Rabbit
```

`Answer` fills two of `ask()`'s three positions, in two roles.
As the `SendType` it is the value of the `yield` inside `ask()`,
sent by the driver.
As the `ReturnType` it is the value of the whole `yield from` expression in `interview()`.

`drive()`, imported unchanged,
answers a request yielded two generators deep the same way it answers one from `interview()`'s own body.
`ask()` works with a `Question` and an `Answer` alone,
so the same `ask()` runs under any driver.
A single loop at the edge of the program interprets requests yielded at any depth.

### Composing Is Not Interpreting

`drive()` and `yield from` both run a generator's body one `yield` at a time and both finish at `StopIteration`,
so they are easy to confuse.
In `yield_from_delegates.py`, `drive()` receives `interview()`'s `Result`.
`yield from` can take over that job:

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
#:   ask() received Alice
#: request = 'town', answer = 'Wonderland'
#:   ask() received Wonderland
#: request = 'friend', answer = 'Rabbit'
#:   ask() received Rabbit
#: request = 'color', answer = 'blue'
#:   ask() received blue
#: Alice of Wonderland, friend Rabbit, color blue
```

Here `interview()`'s `Result` arrives as the value of `yield from interview()` instead of as `stop.value` in the driver.
`interview()`'s questions reach `drive()` through three generators rather than two.

The outermost generator still needs code that calls `next()` and `send()`,
so the listing ends with a `drive()` call.
However deeply the delegations nest, the program has one driver.

`drive()` and `yield from` differ in how they respond to a request.
`drive()` answers it.
The generator yields a `Question`, `drive()` looks it up,
and the request stops there.
`yield from` relays the request upward and passes the answer back down intact,
so `survey()` contains no code that reads a `Question`.

`drive()` and `yield from` also differ in what they do at `StopIteration`.
Both catch it and both take `stop.value`,
but they hand that value to different places.
`drive()` returns the `Result` to its own caller, ending the conversation.
`yield from` makes the `Result` the value of the expression in the enclosing generator,
after which that generator keeps running.

A generator between the two can do both:
answer the requests it knows and relay the rest.
`proxy()` has the same annotation as `interview()`, so `drive()` accepts either,
and `survey()` could delegate to either with `yield from`:

```python
# answering_proxy.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import (
    Answer, Question, Result, interview
)

def proxy(
    inner: Generator[Question, Answer, Result],
    known: dict[Question, Answer],
) -> Generator[Question, Answer, Result]:
    request = next(inner)
    while True:
        if request in known:
            answer = known[request]  # [1]
            print(f"  proxy answers {request}")
        else:
            answer: Answer = yield request  # [2]
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

`proxy()` drives `inner` the way `drive()` does, with `next()` and `send()`,
and relays a request with a `yield` of its own at `[2]` instead of a `yield from`,
because `yield from` would relay every request.
In the second run, `drive()` sees two requests instead of three.
The proxy answers `town` at `[1]`, so the driver sees no request for it,
and the result changes while `interview()` and `drive()` stay the same.
`proxy()` is a [*Proxy*](25_Patterns--Surrogate.md#proxy):
the same interface as the object it wraps, with a forwarding loop of its own.
It is also the shape of [layering handlers](46_Effects--Stateless.md#layering-handlers)
in Stateless, where a handler answers the requests `supply()` gave it and re-yields the rest to the handler outside it.

### `throw()` and `close()` Reach the Innermost Generator

A driver can `throw()` an exception into a generator or `close()` it.
`yield from` relays both calls.
`throw()` raises its exception inside the innermost generator rather than in the delegating one.
`close()` ends every generator in the chain.

In [A Basic Context Manager](15_Techniques--Context_Managers.md#a-basic-context-manager),
`@contextmanager`'s `__exit__()` calls the generator's `throw()` method,
"which resumes the generator by raising the block's exception at the `yield`."
A driver can make the same call from its own code:

```python
# throw_and_close.py
from collections.abc import Generator

def worker() -> Generator[str]:
    try:
        yield "ready"
        yield "still going"
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

`g.throw(ValueError("bad input"))` raises that exception at the suspended `yield "ready"`,
inside `worker()`'s body, the same way the `with` block's exception does.
Like `send()`, `throw()` returns the next value the generator yields.
An exception that escapes the generator's body ends the generator and propagates out of `throw()` into the driver.

`g.close()` raises `GeneratorExit` at the `yield` on which the generator now waits,
`yield "recovered"`.
`worker()` has no matching `except`, so `GeneratorExit` propagates,
the `finally` block runs, and the generator ends.
`close()` catches the `GeneratorExit` and returns `None` once the generator finishes,
so no traceback appears.

Through a `yield from`, the same two calls reach the innermost generator:

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

The driver calls `throw()` on the generator `outer()` returned,
but `inner()` prints the `caught` line.
`yield from` passes the exception down to the `yield` where `inner()` waits.
`g.close()` raises `GeneratorExit` in `inner()` first,
so the cleanup lines print from the inside out.
A driver that holds the outermost generator can stop and clean up every generator beneath it.

A generator can catch `GeneratorExit` and yield again instead of ending.
Doing so makes `close()` raise a `RuntimeError`:

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

`close()` requires the generator to finish.
When a driver stops using a live generator before the generator finishes,
the driver shuts it down with `close()`.
Python also calls `close()` on a live generator when it reclaims the generator's memory.
When Python reclaims a generator like `stubborn()`,
the `RuntimeError` has no caller to reach,
so Python prints it as an "Exception ignored" message and continues.
A generator written for others to drive must therefore let `GeneratorExit` end it.

## The Driver You Already Use

This chapter rests on three ideas:

- Calling a generator function returns a generator object that holds the body and its state.
  A driver runs that body one `yield` at a time with `next()` and `send()`.
- `yield` carries a request out of the body and `send()` carries the answer back in,
  so the body can ask for something and receive the answer.
- `yield from` composes those conversations.
  Each generator in the chain yields to whatever code resumed it,
  so one chain serves every driver.

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
The loop ends when the queue is empty.

We can modify `task_runner()` to allow jobs to make requests:

```python
# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable
from typing import Final

type Request = str
type Reply = str

REPLIES: Final[dict[Request, Reply]] = {
    "download: headers?": "200 OK, 512 bytes",
}

def answer(request: Request) -> Reply:
    return REPLIES.get(request, "ok")

def download() -> Generator[Request, Reply]:
    reply: Reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Generator[Request, Reply]:
    # Discard the send() argument:
    yield "index: build"
    yield "index: merge"

def task_runner(
    jobs: Iterable[Generator[Request, Reply]]
) -> None:
    ready = deque((job, next(job)) for job in jobs)
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

`ready` uses a generator expression to pair every `job` with `next(job)`,
that job's next request.
When sending the last request for that `job` fails,
the `while` loop continues without appending the `job` to `ready`,
de-scheduling that `job`.

`index()` discards what it receives; it yields only to take turns.

`asyncio.run()` starts an event loop,
a driver like the one in `task_runner_send.py`.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
describes `await` as suspending a task until the event loop resumes it.
The event loop gives each task a turn and answers the request each task yields.
Like a generator, a coroutine object offers `send()`, `throw()`, and `close()`.
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

A class can supply that `__anext__()` directly,
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
`main()` makes the first two calls itself, and the `async for` makes the rest,
ending when `__anext__()` raises `StopAsyncIteration`,
the asynchronous counterpart of `StopIteration`.
The asynchronous generator `countdown()` writes the same loop as a body with `yield` and leaves the two methods to Python.

An asynchronous generator has no return channel,
so `AsyncGenerator[YieldType, SendType]` takes two parameters where `Generator` takes three.
Writing `return` with a value in one is a `SyntaxError`, as is `yield from`.
The send channel remains as `asend()`, alongside `athrow()` and `aclose()`.
Each of the three returns an awaitable for the caller to `await`.

[Stateless](46_Effects--Stateless.md)
builds on all three of this chapter's ideas.
It describes a function by what it requests and writes those requests into its return type.

## Half a Coroutine by Design

PEP 255 added generators to Python 2.2 in 2001 so that a function can produce values one at a time.
The function pauses after each value.
When the caller asks for the next value,
it resumes from the point where it paused.
The problem appears whenever the producer keeps state from one value to the next while the consumer has a loop of its own.
The PEP's example, the standard library's `tokenize()`,
keeps its place in the source text,
and a recursive tree walk keeps a whole recursion in progress between one node and the next.
The consumer needs its own local variables and loops to track what it has seen,
and it may stop early.

In a single thread, Python had three ways to write such a producer.
Each comes with an undesirable compromise.

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

`fibonacci()` is in charge of how many times `consume()` runs and when the sequence ends.
`consume()` receives one value per call and has no way to ask for the next value or to stop the loop early.

The second way is for `fibonacci()` to return a list containing every computed value:

```python
# fibonacci_list.py
from collections.abc import Iterator
from itertools import accumulate, islice, repeat

def fibonacci(n: int) -> list[int]:
    pairs: Iterator[tuple[int, int]] = accumulate(
        repeat(None),
        lambda pair, _: (pair[1], pair[0] + pair[1]),
        initial=(0, 1),
    )
    return [a for a, _ in islice(pairs, n)]

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

Because the list holds all the values,
the sequence must be finite and fit in memory.

This is a functional version of the generator `fibonacci()` in `iterators.py`.
[`accumulate()`](41_Functional--Toolkits.md#accumulate)
is a `reduce()` that keeps every intermediate result.
[`repeat(None)`](41_Functional--Toolkits.md#repeat)
is an iterator that produces `None` every time something asks it for an element.
With no count argument it produces `None` forever.
Each step of `accumulate()` takes one element from the first argument,
so here each step takes a `None`.
It calls the lambda,
passing the current pair together with `None` to get the next pair.
It hands out the new pair as the `yield` value from the `pairs` iterator.
The lambda's second parameter always receives that `None`,
so the lambda ignores it with the parameter `_`.
The pair holds the same state as `a` and `b` in `fibonacci_callback.py`.
There, the stack frame of the running `fibonacci()` keeps `a` and `b` between calls of `consume()`.
Here, `accumulate()` passes the pair into each lambda call and takes the new pair out,
so the state travels as a value instead of living in a stack frame.

In `itertools_accumulate.py` from [Toolkits](41_Functional--Toolkits.md#accumulate),
the iterable is `[1, 2, 3, 4]` and each step adds its element to the running total.
`fibonacci()` folds `repeat(None)`, whose elements carry no information:
each step needs the previous pair alone.
The iterable's one job here is to decide how many steps `accumulate()` takes,
and `repeat(None)` is endless, so the chain of pairs is endless too.
[`islice()`](41_Functional--Toolkits.md#islice) takes the first `n` pairs,
and the comprehension keeps the first number of each pair.

Needing `repeat(None)` as a placeholder shows that `itertools` lacks the right operation.
A fold like `accumulate()` consumes an input.
A sequence built from a start value and a step needs the opposite operation,
an *unfold*, and `itertools` has no function for it.
The third-party `more-itertools` package supplies one as `iterate(func, start)`,
which produces `start`, `func(start)`, `func(func(start))`,
and so on without end.
`toolz` has an `iterate()` of the same shape.
Each is a generator:
a loop that yields the current value and then applies the step to it.
A generator is the direct way to write an unfold,
and before PEP 255 Python had no generator.

The third way is an iterator class with a `__next__()` that returns one value per call:

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
pausing `fibonacci()` in the middle of its own loop, handing out a value,
and resuming where it stopped.
A generator lets the producer and the consumer each keep their own loop.

Two loops passing values in both directions resembles a queue like the ones in [Coordinating Threads with Queues](19_Techniques--Concurrency.md#coordinating-threads-with-queues),
with three differences:

1. A generator holds no items: a value goes out,
   the generator stays suspended until the driver sends a value,
   and only then does the next value go out.
2. Control moves with the value,
   so at any moment either the driver or the generator body is running.
3. The generator cannot start an exchange.
   It runs when its driver resumes it, and it answers that driver alone.

The PEP's authors wanted the useful part of a coroutine without the whole mechanism.
The useful part is that a suspended generator keeps its [execution frame](05_Foundations--Functions.md#names-inside-a-function)
alive and resumes it on the next call.
Python discards a function's stack frame when the function returns.
At `yield`, Python unlinks the generator's execution frame from the call stack,
so it stops being a stack frame.
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
Handing control anywhere else would mean carrying the C stack as well,
which is why the PEP calls Stackless Python, whose coroutines do that,
"a controversial rethinking of the Python core."
The suspended generator is the one-shot continuation that [Annotating a Generator](#annotating-a-generator)
describes, and the restriction says who resumes it:
the code that called `next()` or `send()`.
That restriction is why a driver exists.
Something must call `next()` and `send()`,
and since a generator cannot name that something, you write it.

In May 1999, two years before the PEP,
Tim Peters called generators "half a coroutine" on python-dev.
The other half came in 2005, when PEP 342 added the send channel to Python 2.5.
Simulations, games, and asynchronous I/O need to pass a value or an exception into a generator at its suspension point,
so `send()`, `throw()`, and `close()` arrived together,
and the PEP describes a scheduler that runs many generators as a "trampoline,"
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
5.  `report()` in `yield_from_return.py` yields its lines and returns `None`.
    Rewrite it to return the character count as well,
    and give it the full annotation.
    Then write a caller that delegates to it with `yield from` and yields that count in a line of its own,
    and say which type parameter carries each of the two values.
6.  Explain why a driver must prime with `next()` rather than `send(None)`,
    given that the two are equivalent at runtime.
    `send_none_is_next.py` has the answer.
    State it in terms of the `SendType`.
7.  [A Vending Machine](31_Patterns--State_Machines.md#a-vending-machine)
    keeps its current state in an attribute and looks up each transition in a table.
    Write a simplified version as a single generator instead.
    It collects money, takes two digits, then dispenses or refuses.
    It yields its current state and receives each event with `send()`,
    so the position in the generator's body carries the state.
    This generator's `yield` runs the opposite direction from `interview()`'s `yield`.
    Here `yield` reports the state the machine reached instead of requesting something the machine needs.
    Say which of the two versions you would rather extend with another state,
    and why.
