# Generators

[Iterators](23_Patterns--Iterators.md#generators)
presented generators as a way to produce values lazily:
a function containing `yield`,
driven by a `for` loop that takes one value at a time.
That is half of what a generator does.

The other half is the return path.
`yield` is an expression,
so a generator can receive a value as well as hand one out,
and it can return a final result when it finishes.
Used that way, a generator is not a sequence but a conversation.
It yields a request, suspends, and continues when a caller sends the answer.

This chapter covers the full three-channel annotation,
the loop that carries such a conversation, and `yield from`,
which composes generators that never name their driver.
The next chapter builds an Effect system on all three,
and this chapter stands on its own.

## Annotating a Generator

Earlier examples annotate every generator with the short `Iterator` form.
That form fits a generator that only produces values.

A generator that also receives values needs the full annotation:

    Generator[YieldType, SendType, ReturnType]

This annotation names the three things a generator exchanges with its caller:

- `YieldType` is the type `yield` hands out,
  thus the type `next(generator)` returns.
- `SendType` is the type `send()` accepts,
  thus the type the `yield` expression produces inside the generator.
- `ReturnType` is the type of the generator's `return` value,
  which arrives as `StopIteration.value`.

The last two type parameters default to `None`.
A generator that only produces values can use either form:

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
It says nothing about the other two channels,
so a type checker rejects `send()` on anything annotated `Iterator`.
The long form is necessary when the other two channels carry something,
as they do in this chapter.

This `interview()` generator yields a question, receives an answer,
and returns a result:

```python
# interview_generator.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    # Ask the world for the name
    name = yield Question("name")
    # Ask the world for the town
    town = yield Question("town")
    friend = yield Question("friend")  # Ask for a friend
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    i = interview()
    question1: Question = next(i)
    print(f"{question1 = }")
    question2: Question = i.send(Answer("Alice"))
    print(f"{question2 = }")
    question3: Question = i.send(Answer("Wonderland"))
    print(f"{question3 = }")
    try:
        i.send(Answer("Rabbit"))
    except StopIteration as stop:
        result: Result = stop.value
    print(f"{result = }")
#: question1 = 'name'
#: question2 = 'town'
#: question3 = 'friend'
#: result = 'Alice of Wonderland, friend Rabbit'
```

Although `Generator[str, str, str]` describes `interview()` accurately,
it does not say which `str` is which.
With `NewType` you can give each channel a distinct type,
so the annotation states the arrangement and a type checker enforces it.
`Question` fills the `YieldType` position, `Answer` the `SendType`,
and `Result` the `ReturnType`.
The distinction exists only for the type checker:
`Question("name")` produces the plain `str`.

Driving the generator by hand sends one `Answer` at a time.
`next(i)` starts the generator and produces a `Question`.
`i.send(Answer("Alice"))` provides an answer and produces the next question.
That single expression carries both directions of the channel.
The last `send()` resumes the body,
which reaches `return` instead of another `yield`,
so the generator returns its `Result`.

A returning generator also raises `StopIteration`,
and the `Result` arrives as that exception's `value`.
A `for` loop never sees that value,
because `for` catches the `StopIteration` and discards it along with its `value`.
To read the `ReturnType`, catch the exception yourself,
as `interview_generator.py` does.

A newly created generator pauses at the top of the function body,
before any code runs, so no `yield` expression is waiting to receive a value.
The first call must therefore be `next()`:
`i.send(Answer("Alice"))` at that point raises `TypeError: can't send non-None value to a just-started generator`.

A suspended generator holds its frame:
the position in the body and every local variable.
`interview()`'s locals `name` and `town` survive two `send()` calls,
because resuming continues an existing computation.
The frame holds them, and the frame is the generator's state.

`next(i)` is equivalent to `i.send(None)`:

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
The `# type: ignore` marks a real mismatch:
`interview()` declares `Answer` as its `SendType`,
and `None` is not an `Answer`.
The type checker rejects the priming `send()` even though the interpreter accepts it,
because the annotation has no way to make an exception for the first call.
A driver therefore primes with `next()`.

The `NewType` definitions catch a transposed annotation.
If you mistakenly annotate the generator as `Generator[Answer, Question, Result]`,
`ty` reports nine errors in three groups of three.
All three `yield Question(...)` expressions yield a `Question` where the annotation declares an `Answer`.
All three `send(Answer(...))` calls pass an `Answer` where `send()` expects a `Question`.
All three `question` variables receive an `Answer` where their declarations say `Question`.
`Generator[str, str, str]` accepts the reversal without complaint.

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
The event loop receives a coroutine's requests;
whatever code calls `next()` and `send()` receives a generator's.
The generator yields a *request* out,
and whatever drives it sends the *answer* back in.
That conversation makes an Effect Management System possible,
the EMS of [Effect Management](44_Effects--Effect_Management.md#effect-management-systems).
Typically, a driver function steps the generator:

```python
# two_way_generator.py
from collections.abc import Generator
from typing import Final
from interview_generator import (Answer, Question,
                                 Result, interview)

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

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(conversation)}: {conversation.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
```

The listing imports the generator unchanged; the driver is new.
The first line of output describes what `interview()` produced:
an ordinary `generator` object whose `__name__` is the function's name.
That `__name__` exists on the object at runtime but not in the `Generator` type,
so the `# type: ignore` on that line suppresses the diagnostic.

`drive()` uses all three type parameters:
`next()` produces the first `Question`,
`send()`'s argument supplies the `Answer`,
and `stop.value` in the `except` clause becomes the `Result` that `drive()` returns.
The `answers` map keys on `Question` and holds `Answer`s.

Inside the `try`, `StopIteration` means the conversation finished,
so only the `send()` call sits there.
Any other code that could raise it belongs outside,
such as `next()` on an exhausted answer source.

The type checker verifies two of those three parameters.
`StopIteration.value`'s type is `Any`,
so a type checker accepts `return stop.value` under any return type `drive()` declares.
The `Result` in `drive()`'s signature states the intent.
Nothing verifies it.

`interview()` names no source for its answers.
Its body is three questions and a `return`,
with no dictionary and no `input()` call.
It yields each question and suspends until `send()` supplies the answer.
`drive()` decides how to answer those questions,
and it takes the answers as a parameter.
Swapping the dictionary for a database changes a single argument.

That is an EMS in miniature.
The generator declares Effects, the driver interprets them.

One generator, one driver.
No annotation states that pairing, but the runtime enforces it:
a generator resumed from two threads at once raises `ValueError: generator already executing` rather than interleaving.
[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
shows that error and `threading.synchronized_iterator()`,
which serializes the conversation.

## `yield from` Composes Descriptions

Generators can carry an EMS because they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down.
Each of the three channels crosses a `yield from` differently.

### Running to Exhaustion

The simplest `yield from` targets generators that only yield:

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
so the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three:
the target decides how many values each delegation contributes.
The `from` is what delegates;
a bare `yield one()` yields the generator object itself as a single value.
"Exhausted" describes where the delegation ends; in between,
the inner generator yields each value one at a time, as the driver requests it.

Exhaustion is transitive.
`top()` delegates to `outer()`, which delegates to `one()` and `three()`,
and the driver still receives one flat sequence.
`top()`'s single `yield from` finishes only after every generator beneath it has finished.

### The Return Channel

A `yield from` expression evaluates to the inner generator's return value,
not its yielded values.
The yielded values pass through to the driver.
Here, `report()` captures the return value from `yield from emit(items)` into `size`.
`report()` itself is a one-way generator,
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

`emit()` is a `Generator[str, None, int]`: it yields strings, receives nothing,
and returns the `int` total it accumulates while iterating.

The return channel delivers a value from a generator to the generator that delegated to it:
`report()` receives the total `emit()` computed,
and neither function names the driver.

Any iterable can follow `yield from`,
but only a generator supplies a return value.
A list has no return channel,
so `v = yield from [1, 2, 3]` yields the three items and sets `v` to `None`.

### The Send Channel

The `SendType` is the type of the value a caller sends back into the generator.
A generator that receives values and returns `None` can leave the `ReturnType` at its default:

```python
# yield_from_send.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")
    yield from collect("beta")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3]:
    print(g.send(value))
#: alpha needs another
#: alpha got 1 and 2
#: beta needs a value
#: beta needs another
try:
    g.send(4)
except StopIteration:
    print("both() is exhausted")
#: beta got 3 and 4
#: both() is exhausted
```

`collect()` yields prompts, receives numbers, and returns `None`,
so its type is `Generator[str, int, None]`.
An omitted `ReturnType` defaults to `None`,
so the annotation shortens to `Generator[str, int]`.
`both()` declares that same type,
because `yield from` passes the inner generator's yield and send channels through to the driver.

`yield from` delivers each number to the `yield` that produced the prompt:
the value from `g.send(1)` becomes the result of the first `yield` inside `collect("alpha")`,
two frames below the driver.
`both()` needs no forwarding code of its own,
because `yield from` does the forwarding.

`g.send(2)` supplies alpha's second value, so `collect("alpha")` finishes.
That finish completes the first `yield from`,
so `both()` starts the second `yield from`.
A single `send()` therefore ends one inner generator and produces the first prompt of the next.
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
        print(g.send(value))
except StopIteration:
    print("manual() is exhausted")
#: alpha needs another
#: alpha got None and None
#: manual() is exhausted
```

Each `send()` delivers its value to `manual()`'s own `yield`, which discards it.
The `for` loop then resumes `collect()` with `next()`,
so both of `collect()`'s `yield` expressions produce `None`.
The type checker reports nothing,
because `manual()` is a valid `Generator[str, int]`:
the send channel appears in the declaration and goes unused.
`yield from` is not shorthand for this loop.

### All Three Channels

`yield from` restructures the `interview()` example:

```python
# yield_from_delegates.py
from collections.abc import Generator
from interview_generator import Answer, Question, Result
from two_way_generator import ANSWERS, drive

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    friend: Answer = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
```

`drive()` is the same function as in `two_way_generator.py` and never references `ask()`.
Only the generator portion changed.

`ask()` uses `Answer` in two of the three positions, for two different reasons.
As the `SendType` it is the value the driver sends in,
which arrives as the value of the `yield` expression and binds to `answer`.
As the `ReturnType` it is the value `ask()` returns when it finishes,
which becomes the value of the whole `yield from` expression,
so `name` and `town` read like ordinary assignments.
The inner generator yields one question and returns one answer,
so both channels carry an `Answer`.
`interview()` keeps `Result` as its `ReturnType`,
because the sentence it builds from three answers is not an answer to any one question.

The trace shows both directions.
`drive()` receives a request that `ask()` yielded two frames down,
and nothing in `drive()` distinguishes it from one `interview()` yielded directly.
The answer `drive()` sends back becomes the value of the `yield` inside `ask()`,
and nothing in `ask()` names the driver that sent it.
A single loop at the edge of the program interprets Effects yielded anywhere inside it.

### Composing Is Not Interpreting

`drive()` and `yield from` both step a generator and both finish at `StopIteration`,
so they are easy to confuse.
Delegation can take over the job `yield_from_delegates.py` gives to `drive()`:

```python
# yield_from_nested.py
from collections.abc import Generator
from interview_generator import Answer, Question, Result
from two_way_generator import ANSWERS, drive
from yield_from_delegates import ask, interview

def survey() -> Generator[Question, Answer, Result]:
    profile: Result = yield from interview()
    color: Answer = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")

print(drive(survey(),
            ANSWERS | {Question("color"): Answer("blue")}))
#: request = 'name', answer = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: request = 'color', answer = 'blue'
#: ask(question = 'color') -> answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
```

The listing imports `interview()` unchanged from `yield_from_delegates.py`,
where `drive()` drove it directly.
Now `survey()` delegates to it.
`interview()`'s `Result` arrives as the value of an expression instead of as `stop.value` in the driver.
Its questions reach `drive()` through three frames rather than two,
and `survey()` asks about a color,
so the call merges one more pair into `ANSWERS` with the dictionary union operator.
The driver receives one more question and the same shape of trace.

`yield from` replaces `drive()` as the consumer of `interview()`,
but not as its runner.
Something must still call `next()` and `send()` at the top,
so the example ends with a `drive()` call.
However deep you stack delegations, the number of drivers stays at one.

`drive()` and `yield from` differ in how they respond to a request.
`drive()` answers it.
The generator yields a `Question`, `drive()` looks it up,
and no other code receives it.
`yield from` answers nothing.
It relays the request upward and passes the reply back down intact,
so `survey()` contains no code that reads a `Question`.

`StopIteration` divides `drive()` and `yield from` along that same line.
Both catch it and both take `stop.value`,
but they hand that value to different places.
`drive()` returns the `Result` to its own caller, ending the conversation.
`yield from` makes the `Result` the value of the expression in the enclosing generator,
after which that generator keeps running.

`yield from` composes descriptions, and a driver interprets them.
A program can hold any number of descriptions and needs one driver,
at its outermost edge.

### `throw()` and `close()` Reach the Innermost Generator

A driver can `throw()` an exception into a generator or `close()` it,
and `yield from` relays both.
`throw()` raises its exception inside the innermost generator rather than in the delegating one,
and `close()` unwinds every frame in the chain.
[A Basic Context Manager](15_Techniques--Context_Managers.md#a-basic-context-manager)
already shows an exception raised at a generator's `yield`,
described from the `with` block's side:
"Python resumes the generator by raising the block's exception at the `yield`."
`throw()` is that same resumption, called directly instead of by a `with` block:

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

`g.close()` raises `GeneratorExit` at the `yield` the generator now waits on,
`yield "recovered"`.
`worker()` has no matching `except`, so `GeneratorExit` propagates,
the `finally` block runs, and the generator ends.
Nothing prints the `GeneratorExit` itself,
because `close()` catches it and returns `None` once the generator finishes.

A generator can catch `GeneratorExit` and yield again instead of letting it end the frame.
Doing so makes `close()` raise:

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
so `close()` raises `RuntimeError: generator ignored GeneratorExit` rather than returning quietly.
A driver that abandons a live generator shuts it down with `close()`,
so a generator written for others to drive must let `GeneratorExit` end it.

## The Driver You Already Use

The next chapter builds on three ideas from this one.
A generator function builds a description instead of doing work.
`yield` makes that description two-way,
so the description can ask for something.
`yield from` composes those conversations,
and no generator in the chain names its driver.

Those ideas are enough to build a task runner:
register each generator with a decorator, keep the live ones in a queue,
and take turns:

```python
# task_runner.py
from collections import deque
from collections.abc import Callable, Iterator

type Job = Callable[[], Iterator[str]]

ready: deque[Iterator[str]] = deque()

def task(fn: Job) -> Job:
    ready.append(fn())
    return fn

@task
def download() -> Iterator[str]:
    for part in ("headers", "body", "checksum"):
        yield f"download: {part}"

@task
def index() -> Iterator[str]:
    yield "index: build"
    yield "index: merge"

def task_runner() -> None:
    while ready:
        job = ready.popleft()
        try:
            print(next(job))
        except StopIteration:
            continue  # Finished: never requeued
        ready.append(job)

task_runner()
#: download: headers
#: index: build
#: download: body
#: index: merge
#: download: checksum
```

`@task` is the [registering-decorator shape](14_Techniques--Decorators.md#decorating-classes):
it calls each generator function once at definition time,
queues the generator that call builds, and hands the function back unchanged.
`task_runner()` gives the front task one `next()` per turn.
A task that yields moves to the back of the queue.
One that finishes raises `StopIteration`, and the runner drops it.
Each `yield` suspends its task and returns control to `task_runner()`,
which then runs the next one, so the output interleaves the two tasks,
though neither names the other and no threads exist.

`task_runner()` calls `next()` and takes turns;
`drive()` calls `send()` and answers questions.
Giving each job a question combines turn-taking and answering in one loop:

```python
# task_runner_send.py
from collections import deque
from collections.abc import Callable, Generator

type Job = Callable[[], Generator[str, str]]

ready: deque[Generator[str, str]] = deque()
to_send: dict[Generator[str, str], str | None] = {}

def task(fn: Job) -> Job:
    job = fn()
    ready.append(job)
    to_send[job] = None
    return fn

def answer(request: str) -> str:
    return f"answer to {request}"

@task
def download() -> Generator[str, str]:
    reply = yield "download: headers?"
    print(f"download: {reply}")
    yield "download: checksum"

@task
def index() -> Generator[str, str]:
    yield "index: build"
    yield "index: merge"

def task_runner() -> None:
    while ready:
        job = ready.popleft()
        try:
            request = job.send(to_send.pop(job))  # type: ignore
        except StopIteration:
            continue
        print(request)
        to_send[job] = answer(request)
        ready.append(job)

task_runner()
#: download: headers?
#: index: build
#: download: answer to download: headers?
#: download: checksum
#: index: merge
```

`to_send` holds what each job's next turn will receive:
`None` until the runner has answered that job's most recent request.
`job.send(to_send.pop(job))` primes a fresh job the same way `next(job)` does,
since `send(None)` and `next()` are equivalent.
On every later turn the same call delivers the runner's answer.

`Job`'s `SendType` is `str`, not `str | None`,
so the priming call needs the `# type: ignore` from `send_none_is_next.py` again.
`to_send.pop(job)` returns `str | None`,
and no annotation ties the `None` to a generator's first turn.

`download()` reads what it receives, into `reply`.
`index()` discards what it receives,
as a task that only takes turns is free to do.
The queue still rotates task to task,
and now the runner also does `drive()`'s work,
answering each request before the next turn.

You have run a driver like `drive()` many times.
[Concurrency](19_Techniques--Concurrency.md#asyncio-mechanics)
presents `await` and the event loop as a way to overlap waiting,
and does not describe the mechanism.
The mechanism is the two halves `task_runner_send.py` just combined:
`task_runner()`'s turn-taking and `drive()`'s question-answering, in one loop.
A coroutine object offers `send()`, `throw()`, and `close()`,
as a generator does.
`await` suspends the coroutine and yields a request to the loop.
The loop supplies the answer once it has one and resumes the coroutine by sending it back.
`asyncio.run()` is the single interpreter at the edge of the program.
That is why an `await` in a function makes every caller `async` in turn:
the requests must reach the loop.

Once you see a program that way,
the question stops being what a function does and becomes what it requests.
That is the question the next chapter puts into the type system.

## Exercises

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
3.  Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()` and extending the loop to `[1, 2, 3, 4, 5]`.
    Write down the sequence of printed lines before running it.
4.  Remove `yield from` in `yield_from_nested.py`,
    leaving `profile: Result = interview()`.
    Run `ty check` and the script, and explain both results.
    Which one told you more,
    and what does the type checker say if `profile` carries no annotation?
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
    Write a simplified version as a single generator instead: it collects money,
    takes two digits, then dispenses or refuses.
    It yields its current state and receives each event with `send()`,
    so the position in the generator's body carries the state.
    This generator's `yield` reports the state the machine reached rather than requesting something the machine needs,
    the opposite direction from `interview()`.
    Say which of the two versions you would rather extend with another state,
    and why.
