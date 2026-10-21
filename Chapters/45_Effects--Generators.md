# Generators

> Some computations pause partway, ask for something,
> and continue when the answer arrives.
> Python's generators can do that, and an Effect system is built on it.

[Iterators](22_Patterns--Iterators.md#generators)
presents generators as a way to produce values lazily:
a function containing `yield`,
driven by a `for` loop that takes one value at a time.
Producing values is half of what a generator does.

The other half is the return path.
`yield` is an expression,
so a generator can receive a value as well as hand one out,
and it can return a final result when it finishes.
Used that way, a generator is not a sequence but a conversation.
It yields a request, suspends, and continues when a caller sends the answer.

This chapter covers the full three-channel annotation, the *driver*
(the loop that runs such a conversation), and `yield from`,
which composes generators that do not name their driver.
[Stateless](46_Effects--Stateless.md) builds an Effect system on the annotation,
the loop, and `yield from`, but generators are useful on their own.

## Annotating a Generator

Earlier chapters annotate their generators with a short form:
`Iterator[int]` in [Iterators](22_Patterns--Iterators.md#generators),
and `Generator[str]` in [Context Managers](15_Techniques--Context_Managers.md#a-basic-context-manager).
A short form fits a generator that yields values and receives `None`.

A generator that also receives values needs the full annotation:

    Generator[YieldType, SendType, ReturnType]

This annotation specifies the three things a generator exchanges with its caller:

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
`Iterator[int]` describes the same one-way generator and reads better.
It describes the yield channel alone,
so a type checker rejects `send()` on anything annotated `Iterator`.
The long form is necessary when the other two channels carry something,
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
    name = yield Question("name")
    town = yield Question("town")
    friend = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")
```

Although `Generator[str, str, str]` describes `interview()` accurately,
it does not say which `str` is which.
`NewType` gives each channel a distinct type,
so the annotation states the arrangement and a type checker enforces it.
`Question` fills the `YieldType` position, `Answer` the `SendType`,
and `Result` the `ReturnType`.
The distinction exists for the type checker.
At runtime, `Question("name")` returns the same `str` you passed in.

Driving the generator by hand sends one `Answer` at a time:

```python
# drive_by_hand.py
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
try:
    conversation.send(Answer("Rabbit"))
except StopIteration as stop:
    result: Result = stop.value
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
```

The `NewType` definitions let the type checker report a transposed annotation.
If you mistakenly annotate the generator in `interview_generator.py` as `Generator[Answer, Question, Result]`,
`ty` reports nine errors in three groups of three.
All three `yield Question(...)` expressions yield a `Question` where the annotation declares an `Answer`.
In `drive_by_hand.py`,
all three `send(Answer(...))` calls pass an `Answer` where `send()` expects a `Question`.
All three `question` variables also receive an `Answer` where their declarations say `Question`.
`Generator[str, str, str]` accepts the reversal.

`next(conversation)` starts the generator and produces a `Question`.
`conversation.send(Answer("Alice"))` provides an answer and produces the next question.
The last `send()` resumes the body,
which reaches `return` instead of another `yield`,
so the generator returns its `Result`.

The caller sees that `return` as a `StopIteration`,
and the `Result` arrives as the exception's `value`.
A `for` loop loses that value,
because it catches the `StopIteration` and discards the exception.
To read the `ReturnType`, catch the exception yourself,
as `drive_by_hand.py` does.

When the body finishes with `return`,
Python raises the `StopIteration` on the generator's behalf.
If a `StopIteration` propagates out of the body instead,
Python converts it into a `RuntimeError`
([PEP 479](https://peps.python.org/pep-0479/)).
Calling `next()` on an exhausted iterator raises `StopIteration`,
as [Asking Consumes an Item](22_Patterns--Iterators.md#asking-consumes-an-item)
shows, so a `next()` call inside the body can trigger that conversion.

A newly created generator pauses at the top of the function body,
before any code runs, so no `yield` expression is waiting to receive a value.
The first call must therefore be `next()` or `send(None)`.
`conversation.send(Answer("Alice"))` at that point raises `TypeError: can't send non-None value to a just-started generator`.

A suspended generator holds its frame:
the position in the body and every local variable.
Resuming continues the existing computation.
`interview()`'s local `name` keeps its value through the next two `send()` calls,
and `town` keeps its value through the last one.
The frame holds them, and the frame is the generator's state.

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

The `# type: ignore` marks a real mismatch.
`interview()` declares `Answer` as its `SendType`,
and `None` is not an `Answer`.
The interpreter accepts the priming `send()`, but the type checker rejects it.
The annotation applies one `SendType` to every call, the first included.
A driver therefore primes with `next()`.

## A Generator Is a Description

[Effect Management](44_Effects--Effect_Management.md#effect-management-for-python)
shows that calling an `async def` function runs nothing.
The call returns a coroutine: a description of work.
A coroutine's annotation is `Coroutine[YieldType, SendType, ReturnType]`,
the same three-part shape as a `Generator`.
The match is deliberate.
`async def` and generator functions both build descriptions that something else drives.
Calling `interview()` returns a generator object but runs nothing in the function body.
`next()` and `send()` do that work, one `yield` at a time.

A generator is more useful than a coroutine here because you write the driver.
A coroutine's requests go to the event loop.
A generator's requests go to whatever code calls `next()` and `send()`.
The generator yields a *request* out,
and whatever drives it sends the *answer* back in.
That conversation makes an [Effect Management System](44_Effects--Effect_Management.md#effect-management-systems)
(EMS) possible.
Typically, a driver function steps the generator.
`drive.py` holds one, along with a table of answers:

```python
# drive.py
from collections.abc import Generator
from typing import Final
from interview_generator import Answer, Question, Result

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value
```

`two_way_generator.py` runs `interview()` under that driver:

```python
# two_way_generator.py
import inspect
from drive import ANSWERS, drive
from interview_generator import interview

conversation = interview()
print(inspect.getgeneratorstate(conversation))
#: GEN_CREATED
result = drive(conversation, ANSWERS)
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
```

`two_way_generator.py` imports `interview()` unchanged.
The driver is new.
The first line of output shows the state of the generator `interview()` returned.
`inspect.getgeneratorstate()` reports `GEN_CREATED`:
the generator exists and waits to start its body.

`drive()` uses all three type parameters:
`next()` produces the first `Question`,
`send()`'s argument supplies the `Answer`,
and `stop.value` in the `except` clause becomes the `Result` that `drive()` returns.
The `answers` map stores each `Answer` under its `Question`.

The type checker verifies two of those three parameters.
`StopIteration.value`'s type is `Any`,
so a type checker accepts `return stop.value` under any return type `drive()` declares.
The `Result` in `drive()`'s signature states the intent.
Nothing verifies it.

Inside the `try`, `StopIteration` means the conversation finished,
so only the `send()` call sits there.
Any other call that can raise `StopIteration` belongs outside the `try`,
such as `next()` on an exhausted answer source.

`interview()` accepts its answers from any driver that calls `send()`.
Its body is three questions and a `return`,
with no dictionary and no `input()` call.
It yields each question and suspends until `send()` supplies the answer.
`drive()` decides how to answer those questions,
and it receives the answers through its `answers: dict[Question, Answer]` parameter.
Swapping the dictionary for a database changes a single argument.

`interview()` and `drive()` form an EMS in miniature.
The generator declares requests.
The driver interprets them.

Each generator has one driver.
No annotation states that pairing, but the runtime enforces it.
A generator resumed from two threads at once raises `ValueError: generator already executing` rather than interleaving.
[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
shows that error and `threading.synchronized_iterator()`,
which serializes the conversation.

## `yield from` Composes Descriptions

Generators can support an EMS because they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down.

### Running to Exhaustion

The simplest `yield from` targets generators that use the yield channel alone:

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

Each `yield from` runs its target until that generator finishes,
so the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three.
"Exhausted" describes where the delegation ends.
In between, the inner generator yields its values one at a time,
as the driver requests each one.

Without `from`, a bare `yield one()` yields the generator object as a single value,
so `list(outer())` would show `<generator object one at ...>` in place of `'only'`.

Exhaustion is transitive.
`top()` delegates to `outer()`, which delegates to `one()` and `three()`.
The driver still receives one flat sequence.
`top()`'s single `yield from` finishes only after every generator beneath it has finished.

### The Return Channel

A `yield from` expression passes the inner generator's yielded values through to the driver and evaluates to the inner generator's return value.
Here, `report()` captures the return value from `yield from emit(items)` into `size`.
`report()` is a one-way generator,
annotated with the short `Iterator[str]` form:

```python
# yield_from_return.py
from collections.abc import Generator, Iterator

def emit(items: list[str]) -> Generator[str, None, int]:
    total = 0
    for item in items:
        yield item
        total += len(item)
    return total

def report(items: list[str]) -> Iterator[str]:
    size: int = yield from emit(items)
    yield f"({size} characters)"

print(list(report(["red", "green", "blue"])))
#: ['red', 'green', 'blue', '(12 characters)']
```

`emit()` is a `Generator[str, None, int]`.
It yields strings, receives `None`,
and returns the `int` total it accumulates while iterating over `items`.

The return channel delivers a value from a generator to the generator that delegated to it.
`report()` receives the total `emit()` computed.
Neither function names the driver.

Any iterable can follow `yield from`.
The expression takes its value from the `StopIteration` that ends the iteration.
A generator's `return` sets that value.
A list's iterator ends with a bare `StopIteration`,
whose `value` defaults to `None`,
so `v = yield from [1, 2, 3]` yields the three items and sets `v` to `None`.

### The Send Channel

The `SendType` is the type of the value a driver sends back into the generator.
A generator that receives values and returns `None` can leave the `ReturnType` at its default:

```python
# yield_from_send.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"  # [1]
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")  # [2]
    yield from collect("beta")  # [3]

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3]:
    print(f"send({value}) -> {g.send(value)}")
#: send(1) -> alpha needs another
#: alpha got 1 and 2
#: send(2) -> beta needs a value
#: send(3) -> beta needs another
try:
    g.send(4)
except StopIteration:
    print("both() is exhausted")
#: beta got 3 and 4
#: both() is exhausted
```

`collect()` yields prompts, receives numbers, and returns `None`,
so its type is `Generator[str, int, None]`.
Because the `ReturnType` defaults to `None`,
the annotation shortens to `Generator[str, int]`.
`both()` declares that same type,
because `yield from` passes the inner generator's yield and send channels through to the driver.

`yield from` delivers each number to the `yield` that produced the prompt.
The value from `g.send(1)` becomes the result of the `yield` at `[1]` inside `collect("alpha")`,
two frames below the driver.
`yield from` does the forwarding,
so the body of `both()` is its two delegations.

`g.send(2)` supplies alpha's second value, so `collect("alpha")` finishes.
That finish completes the `yield from` at `[2]`,
so `both()` starts the `yield from` at `[3]`.
A single `send()` therefore ends one inner generator and produces the first prompt of the next.
The output shows it on adjacent lines:
`alpha got 1 and 2` prints during `send(2)`,
and `send(2)` returns `beta needs a value`.
The driver sees `StopIteration` only when `both()` finishes its last delegation.

The natural first attempt is to write the forwarding as a loop by hand.
That loop silently discards every sent value:

```python
# manual_forwarding.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def manual() -> Generator[str, int]:
    for prompt in collect("alpha"):  # noqa: UP028
        yield prompt

g = manual()
print(next(g))
#: alpha needs a value
try:
    for value in [1, 2, 3]:
        print(f"send({value}) -> {g.send(value)}")
except StopIteration:
    print("manual() is exhausted")
#: send(1) -> alpha needs another
#: alpha got None and None
#: manual() is exhausted
```

Each `send()` delivers its value to `manual()`'s own `yield`, which discards it.
The `for` loop then resumes `collect()` with `next()`,
so both of `collect()`'s `yield` expressions produce `None`.
The type checker reports nothing,
because `manual()` is a valid `Generator[str, int]`.
The send channel appears in the declaration and goes unused.
`yield from` is not shorthand for this loop.

### All Three Channels

`yield from` restructures the `interview()` example:

```python
# yield_from_delegates.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer = yield question
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

The listing imports `drive()` unchanged from `drive.py`,
and nothing in `drive()` refers to `ask()`.
The new code is all on the generator side.

`ask()` uses `Answer` in two of the three positions, for two different reasons.
As the `SendType` it is the value the driver sends in,
which arrives as the value of the `yield` expression and binds to `answer`.
As the `ReturnType` it is the value `ask()` returns when it finishes.
That value becomes the value of the whole `yield from` expression,
so `interview()`'s three assignments read like ordinary ones.
The inner generator receives one answer and returns it,
so its send and return channels both carry an `Answer`.
`interview()` keeps `Result` as its `ReturnType`,
because it returns a sentence built from all three answers,
a different kind of value from the answer to any one question.

`drive()` receives a request that `ask()` yielded two frames down,
and treats it the same as one that `interview()` yielded in its own body.
The answer `drive()` sends back becomes the value of the `yield` inside `ask()`.
Nothing in `ask()` names the driver that sent it.
A single loop at the edge of the program interprets requests yielded anywhere inside it.

### Composing Is Not Interpreting

`drive()` and `yield from` both step a generator and both finish at `StopIteration`,
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

The listing imports `interview()` unchanged from `yield_from_delegates.py`,
where `drive()` drives it.
Now `survey()` delegates to `interview()`.
`interview()`'s `Result` arrives as the value of an expression instead of as `stop.value` in the driver.
`interview()`'s questions reach `drive()` through three frames rather than two.

`survey()` then asks about a color,
so the argument to `drive()` uses the dictionary union operator to add one more pair to a copy of `ANSWERS`.
The driver receives one more question and the same shape of trace.

`yield from` replaces `drive()` as the consumer of `interview()`,
but not as its runner.
Something must still call `next()` and `send()` at the top,
so the example ends with a `drive()` call.
However deep you stack delegations, the number of drivers stays at one.

`drive()` and `yield from` differ in how they respond to a request.
`drive()` answers it.
The generator yields a `Question`, `drive()` looks it up,
and the request stops there.
`yield from` answers nothing.
It relays the request upward and passes the answer back down intact,
so `survey()` contains no code that reads a `Question`.

`drive()` and `yield from` also differ in what they do at `StopIteration`.
Both catch it and both take `stop.value`,
but they hand that value to different places.
`drive()` returns the `Result` to its own caller, ending the conversation.
`yield from` makes the `Result` the value of the expression in the enclosing generator,
after which that generator keeps running.

### `throw()` and `close()` Reach the Innermost Generator

A driver can `throw()` an exception into a generator or `close()` it,
and `yield from` relays both.
`throw()` raises its exception inside the innermost generator rather than in the delegating one.
`close()` unwinds every frame in the chain.

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

`g.throw(ValueError("bad input"))` raises that exception at the suspended `yield`,
inside `worker()`'s frame, the same way the `with` block's exception does.
`worker()` catches it, prints, and yields again,
so the generator keeps running when its `except` clause handles the thrown exception.
Like `send()`, `throw()` returns the next value the generator yields,
here `"recovered"`.
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

The driver calls `throw()` on `outer()`, but `inner()` prints the `caught` line.
`yield from` passes the exception down to the `yield` where `inner()` waits.
`inner()`'s `except` clause handles it,
so the `ValueError` stays inside `inner()`.
`g.close()` raises `GeneratorExit` in `inner()` first,
so the cleanup lines print from the inside out.
Holding the outermost generator is enough for a driver to stop and clean up every frame beneath it.

A generator can catch `GeneratorExit` and yield again instead of letting it end the frame.
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
`stubborn()` instead answers `GeneratorExit` with another `yield`,
so `close()` raises `RuntimeError: generator ignored GeneratorExit`.

A driver that abandons a live generator shuts it down with `close()`.
Python also calls `close()` on a live generator when it reclaims the generator's memory.
When Python reclaims a generator like `stubborn()`,
the `RuntimeError` has no caller to reach,
so Python prints it as an "Exception ignored" message and continues.
A generator written for others to drive must therefore let `GeneratorExit` end it.

## The Driver You Already Use

[Stateless](46_Effects--Stateless.md) builds on three ideas from this chapter.
A generator function builds a description instead of doing work.
`yield` makes that description two-way,
so the description can ask for something.
`yield from` composes those conversations,
and no generator in the chain names its driver.

Those ideas are enough to build a task runner.
A queue keeps the live generators.
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

def task_runner(ready: deque[Iterator[str]]) -> None:
    while ready:
        job = ready.popleft()
        try:
            print(next(job))
        except StopIteration:
            continue
        ready.append(job)

task_runner(deque([download(), index()]))
#: download: headers
#: index: build
#: download: body
#: index: merge
#: download: checksum
```

`task_runner()` gives the front job one `next()` per turn.
When a job yields, the runner appends it to the back of the queue.
When a job finishes, `next()` raises `StopIteration`,
and the runner drops the job.
Each `yield` suspends its job and returns control to `task_runner()`,
which then runs the next job.
The output interleaves the two jobs in a single thread,
although neither names the other.

`task_runner()` calls `next()` and takes turns.
`drive()` calls `send()` and answers questions.
Letting each job make a request combines turn-taking and answering in one loop:

```python
# task_runner_send.py
from collections import deque
from collections.abc import Generator, Iterable
from typing import Final

REPLIES: Final[dict[str, str]] = {
    "download: headers?": "200 OK, 512 bytes",
}

def answer(request: str) -> str:
    return REPLIES.get(request, "ok")

def download() -> Generator[str, str]:
    reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

def index() -> Generator[str, str]:
    yield "index: build"
    yield "index: merge"

def task_runner(
    jobs: Iterable[Generator[str, str]]
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

The queue holds each job paired with its latest request.
`task_runner()` primes every job with `next()`, as a driver must.
On each turn it prints the request and sends back the answer.
That `send()` resumes the job until the job yields its next request.
`answer()` looks the request up in `REPLIES` and returns `"ok"` for any request missing from the table.

`download()` reads what it receives, into `reply`.
`index()` discards what it receives,
as a job that yields to take turns is free to do.
The queue still rotates job to job.
Now the runner also does `drive()`'s work,
answering each request before the next turn.

You have run a driver like `drive()` many times.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
describes `await` as suspending a task until the event loop resumes it.
The protocol underneath is the two halves `task_runner_send.py` combines:
`task_runner()`'s turn-taking and `drive()`'s question-answering, in one loop.
A coroutine object offers `send()`, `throw()`, and `close()`,
as a generator does.
`await` suspends the coroutine and yields a request, a `Future`,
to the task that drives it.
When the `Future` has a result, the loop resumes the coroutine,
and the `await` expression evaluates to that result.

`asyncio.run()` is the single driver at the edge of the program.
Every request must travel up to that loop,
so an `await` in a function makes every caller `async` in turn.

A function can contain both `async def` and `yield`.
The result is an *asynchronous generator*, which talks to two drivers at once.
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
    async for n in countdown(3):
        print(f"{n = }")
    print([n * n async for n in countdown(3)])

asyncio.run(main())
#: n = 3
#: n = 2
#: n = 1
#: [9, 4, 1]
```

`asyncio.sleep(0)` stands in for real I/O.
In `countdown()`, the `await` goes to the event loop.
The `yield` goes to `main()`.
On each pass, `async for` awaits the generator's `__anext__()`,
so the loop must sit inside an `async def`.
The *asynchronous comprehension* `[n * n async for n in countdown(3)]` collects the values the same way,
and it also requires an enclosing `async def`.

`AsyncGenerator[YieldType, SendType]` takes two parameters,
where `Generator` takes three.
An asynchronous generator has no return channel.
Writing `return` with a value in one is a `SyntaxError`, as is `yield from`.
The send channel remains as `asend()`, alongside `athrow()` and `aclose()`.
Each of the three returns an awaitable for the caller to `await`.

Once you see a program that way,
the question stops being what a function does and becomes what it requests.
The next chapter writes those requests into a function's return type.

## Exercises

Try each exercise before opening its [solution](../Solutions/45_Effects--Generators/).

1.  Write `tally()`, a generator that yields a prompt string,
    receives an `int` for each prompt, and returns the total once it has three.
    Give it the full three-parameter annotation,
    then drive it by hand with `next()` and `send()` and read the total off `StopIteration`.
2.  `drive()` answers from a `dict`.
    Write a second driver that answers from an `Iterator[Answer]`, in order,
    and run `interview()` under both.
    Explain what, if anything, needed to change in `interview()`, and why.
    Give your driver fewer answers than questions and say what it returns.
    `StopIteration` now means two different things in the same loop.
    Keep them apart.
3.  Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()`,
    extending the loop to `[1, 2, 3, 4, 5]`,
    and changing the final `g.send(4)` after the loop to `g.send(6)`.
    Write down the sequence of printed lines before running it.
4.  Remove `yield from` in `yield_from_nested.py`,
    leaving `profile: Result = interview()`.
    Run `ty check` and the script, and explain both results.
    Which one told you more,
    and what does the type checker say once you remove `profile`'s annotation?
5.  `report()` in `yield_from_return.py` yields but returns nothing.
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
