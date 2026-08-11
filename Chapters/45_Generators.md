# Generators

[Iterators](23_Iterators.md#generators)
presented generators as a way to produce values lazily:
a function containing `yield`,
driven by a `for` loop that takes one value at a time.
That is half of what a generator does.

The other half is the return path.
`yield` is an expression,
so a generator can receive a value as well as hand one out,
and it can return a final result when it finishes.
Used that way, a generator is not a sequence but a conversation.
It states what it needs, pauses, and continues once someone answers.

This chapter covers the full three-channel annotation,
the loop that carries such a conversation, and `yield from`,
which composes generators without any of them learning who drives.
The next chapter builds an Effect system on all three,
but nothing here depends on it.

## Annotating a Generator

Earlier examples annotate every generator with the short `Iterator` form.
That fits a generator that only produces values.

A generator that also receives values needs the full annotation:

    Generator[YieldType, SendType, ReturnType]

This names the three things a generator exchanges with its caller:

- `YieldType` is the type `yield` hands out,
  thus the type `next(generator)` returns.
- `SendType` is the type `send()` accepts,
  thus the type the `yield` expression produces inside the generator.
- `ReturnType` is the type of the generator's `return` value,
  delivered as `StopIteration.value`.

The default value for the last two type parameters is `None`.
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
`Iterator[int]` describes the same one-way generator and reads better,
at the cost of saying nothing about the other two channels:
a checker rejects `send()` on anything annotated `Iterator`.
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
    name = yield Question("name")  # Ask the world for the name
    town = yield Question("town")  # Ask the world for the town
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
so the annotation states the arrangement and a checker enforces it.
`Question` fills the `YieldType` position, `Answer` the `SendType`,
and `Result` the `ReturnType`.
The distinction exists only for the checker.
`Question("name")` produces the plain `str`.

Driving the generator by hand sends one `Answer` at a time.
`next(i)` starts the generator and produces a `Question`.
`i.send(Answer("Alice"))` provides an answer and produces the next question.
This is the two-way channel in a single expression.
The last `send()` finds no further `yield`,
so the generator returns its `Result`.
A returning generator also raises `StopIteration`,
and the `Result` arrives as that exception's `value`.
A `for` loop never sees that value,
because `for` catches the `StopIteration` and discards it along with its `value`.
Getting at the `ReturnType` means catching the exception yourself,
as this listing does.

The first call on a new generator object cannot carry a value.
A newly created generator pauses at the top of the function body,
before any code runs,
so there is no suspended `yield` expression to receive a sent value.
If you call `i.send(Answer("Alice"))` at that point,
it raises `TypeError: can't send non-None value to a just-started generator`.

A suspended generator holds its frame:
the position in the body and every local variable.
`interview()` remembers `name` and `town` across two `send()` calls with no storage of its own,
because resuming continues an existing computation rather than starting a new one.
The frame is the generator's state.

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
The checker rejects the priming `send()` even though the interpreter accepts it.
The equivalence is a runtime fact the annotation cannot express,
which is the practical reason a driver primes with `next()`.

The `NewType` definitions prevent accidental transposition.
If you mistakenly annotate the generator as `Generator[Answer, Question, Result]`,
`ty` reports nine errors in three groups of three.
All three `yield Question(...)` expressions offer a `Question` where the annotation declares an `Answer`.
All three `send(Answer(...))` calls pass an `Answer` where `send()` expects a `Question`.
All three `question` variables receive an `Answer` where their declarations say `Question`.
`Generator[str, str, str]` accepts the reversal without complaint.

## A Generator Is a Description

[Effect Management](44_Effect_Management.md#effect-management-for-python)
showed that calling an `async def` function runs nothing.
It returns a coroutine: a description of work.
A coroutine's annotation is `Coroutine[YieldType, SendType, ReturnType]`,
the same three-part shape as a `Generator`, and the match is deliberate.
`async def` and generator functions both build descriptions that something else drives.
Calling `interview()` returns a generator object but doesn't run anything in the function body.
`next()` and `send()` do that work, one `yield` at a time.

A generator is the more useful of the two here because the driver can be yours.
A coroutine's requests go to the event loop;
a generator's go to whatever code calls `send()`.
The generator yields a value out, and the caller sends a value back in.
That conversation makes an EMS possible.
The generator yields a *request*, and whatever drives it supplies the *answer*.
Typically, a driver function does the stepping:

```python
# two_way_generator.py
from collections.abc import Generator
from typing import Final
from interview_generator import Answer, Question, Result, interview

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
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
```

The generator arrives by import, unchanged; only the driver is new.
The first line of output is `interview()`'s product:
an ordinary `generator` object that still carries the function's name.
That `__name__` exists on the object at runtime but not in the `Generator` type,
so the `# type: ignore` on that line suppresses the checker's complaint.

`drive()` touches all three type parameters:
`next()` produces the first `Question`,
`send()`'s argument supplies the `Answer`,
and `stop.value` in the `except` clause becomes the `Result` that `drive()` returns.
The `answers` map keys on `Question` and holds `Answer`s.
Only the `send()` call sits inside the `try`.
Here `StopIteration` means the conversation finished,
so any other code that could raise it, such as an exhausted answer source,
belongs outside.

The checker verifies only two of those three parameters.
`StopIteration.value`'s type is `Any`,
so a checker accepts `return stop.value` whatever `drive()` declares it returns.
The `Result` in `drive()`'s signature states the intent; nothing verifies it.

`interview()` does not know where the answers originate.
It has no dictionary, no `input()` call, and no network connection.
It states what it needs and waits.
`drive()` decides how to meet those needs,
and it takes the answers as a parameter.
Swapping the dictionary for a database changes a single argument.

That is an EMS in miniature.
The generator declares Effects, the driver interprets them.

One generator, one driver.
Nothing states that pairing, but the runtime protects it:
a generator resumed from two threads at once raises `ValueError: generator already executing` rather than interleaving.
[Concurrency](19_Concurrency.md#sharing-an-iterator-between-threads)
shows the failure and `threading.synchronized_iterator()`,
which serializes the conversation.

## `yield from` Composes Descriptions

The reason generators can carry an EMS is that they nest.
`yield from` runs an inner generator to exhaustion,
passing every yielded request out to the outer driver and every sent answer back down.
Each of the three channels crosses that boundary differently.

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

Each `yield from` runs its target until that generator runs out,
so the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three.
The number of contributions is a property of the target.
The `from` makes this delegation:
`yield one()` would hand the generator object itself to the driver as one value.
"Exhausted" describes where the delegation ends, not when.
Each value still leaves the inner generator only when the driver asks for the next one.

Exhaustion is transitive.
`top()` delegates to `outer()`, which delegates to `one()` and `three()`,
and the driver still receives one flat sequence.
`top()`'s single `yield from` does not finish until every generator beneath it has.

### The Return Channel

A `yield from` expression evaluates to the inner generator's return value,
not its yielded values.
The yielded values pass through to whoever is driving.
Here, `report()` captures the return value from `yield from emit(items)` into `size`.
`report()` returns nothing and only yields:

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

`emit()` is a `Generator[str, None, int]`: it yields strings,
is never sent anything,
and returns the `int` total it accumulates while iterating.

The return channel is how a generator reports to whichever generator delegated to it,
so `report()` learns something `emit()` computed while neither of them knows who is driving.

Any iterable can follow `yield from`,
but only a generator can answer with a value.
A list has no return channel,
so `v = yield from [1, 2, 3]` yields the three items and sets `v` to `None`.

### The Send Channel

The `SendType` is the type of the information a caller sends back into the generator.
A generator that receives values but produces no final result needs no `ReturnType`:

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

`collect()` yields prompts, receives numbers, and returns nothing,
so its type is `Generator[str, int, None]`.
An omitted `ReturnType` defaults to `None`,
so the annotation shortens to `Generator[str, int]`.
`both()` declares that same type,
because `yield from` passes the inner generator's yield and send channels through to the driver.

The numbers travel down to the `yield` that asked for them.
`g.send(1)` arrives inside `collect("alpha")`, two frames below the driver.
`both()` contains no code that forwards the value because `yield from` does that forwarding.

`g.send(2)` supplies alpha's second value, which lets `collect("alpha")` finish,
which completes the first `yield from`, which starts the second one.
A single `send()` therefore ends one inner generator and produces the first prompt of the next.
The driver sees `StopIteration` only when `both()` runs out of delegations.

Writing the loop by hand is the natural first attempt, and it fails quietly:

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

Each `send()` delivers its value to `manual()`'s own `yield`,
which throws it away.
The `for` loop then resumes `collect()` with `next()`,
so both of `collect()`'s `yield` expressions produce `None`.
The checker says nothing, because `manual()` is a valid `Generator[str, int]`:
the send channel appears in the declaration and goes unused.
`yield from` is not shorthand for this loop.

### All Three Channels

You can apply `yield from` to the `interview()` example:

```python
# yield_from_delegates.py
from collections.abc import Generator
from interview_generator import Answer, Question, Result
from two_way_generator import ANSWERS, drive

def ask(question: Question) -> Generator[Question, Answer, Answer]:
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

`drive()` never learns that `ask()` exists.
Only the generator portion changed.

`ask()` uses `Answer` in two of the three positions, for two different reasons.
As the `SendType` it is the value the driver sends in,
which arrives as the value of the `yield` expression and binds to `answer`.
As the `ReturnType` it is the value `ask()` hands back when it finishes,
which `yield from` produces as the value of the whole `yield from` expression.
The inner generator asks one question and hands back one answer,
so both channels carry an `Answer`.
`interview()` keeps `Result` as its `ReturnType`,
because the sentence it builds from three answers is not an answer to any one question.

The trace shows both directions of travel.
A request yielded two frames down inside `ask()` surfaces at `drive()`,
which knows nothing about where it originated.
The answer `drive()` sends back arrives inside `ask()`,
which also knows nothing about where it originated.
A single loop at the edge of the program interprets Effects yielded anywhere inside it.
`yield from` also returns the inner generator's value,
which is why `name` and `town` read like ordinary assignments.

### Composing Is Not Interpreting

`drive()` and `yield from` both step a generator and both finish at `StopIteration`,
which makes them easy to confuse.
Delegation can take over the job the previous listing gave to `drive()`:

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

`interview()` arrives unchanged from the previous example.
It was the generator `drive()` drove; now `survey()` delegates to it.
Its `Result` arrives as the value of an expression instead of as `stop.value` in the driver,
and its questions surface three frames up rather than two.
The driver sees one more question and the same shape of trace.
`survey()` asks about a color,
so the call merges one more pair into `ANSWERS` with the dictionary union operator.

`yield from` replaced `drive()` as the consumer of `interview()`,
but not as its runner.
Something must still call `next()` and `send()` at the top,
which is why the example ends with a `drive()` call.
However deep you stack delegations, the number of drivers stays at one.

What separates them is the response to a request.
`drive()` answers it: a `Question` comes out, the driver looks it up,
and the request stops there.
`yield from` answers nothing.
It relays the request upward and passes the reply back down untouched,
so `survey()` has no idea what a `Question` means.
A driver can also `throw()` an exception into a generator or `close()` it,
and `yield from` relays both:
a thrown exception surfaces inside the innermost generator rather than at the delegating one,
and a `close()` unwinds every frame in the chain.
`StopIteration` splits the same way.
Both catch it and both take `stop.value`, but they hand it to different places.
`drive()` returns the `Result` to its own caller, ending the conversation.
`yield from` feeds it to the enclosing generator as the value of the expression,
after which that generator keeps running.

`yield from` composes descriptions and a driver interprets them.
A program can hold any number of the first and needs one of the second,
at its outermost edge.

## The Driver You Already Use

Three ideas from this chapter carry into the next one.
A generator function builds a description instead of doing work.
`yield` makes that description two-way,
so the description can ask for something.
`yield from` composes those conversations without any participant learning who drives.

None of this is exotic, and you have run a driver like `drive()` many times.
[Concurrency](19_Concurrency.md#asyncio-mechanics)
presented `await` and the event loop as a way to overlap waiting,
and left the mechanism alone.
The mechanism is this one.
A coroutine object offers `send()`, `throw()`, and `close()`,
as a generator does.
`await` suspends the coroutine and hands a request out to the loop,
which supplies the answer once it has one and resumes the coroutine by sending it back.
`asyncio.run()` is the single interpreter at the edge of the program,
which is why an `await` in a function makes every caller `async` in turn:
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
    Give your driver fewer answers than there are questions and say what it returns.
    `StopIteration` now means two different things in the same loop;
    keep them apart.
3.  Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()` and extending the loop to `[1, 2, 3, 4, 5]`.
    Write down the sequence of printed lines before running it.
4.  Remove `yield from` in `yield_from_nested.py`,
    leaving `profile: Result = interview()`.
    Run `ty check` and the script, and explain both results.
    Which one told you more,
    and what would the checker have said if `profile` carried no annotation?
5.  `report()` in `yield_from_return.py` yields but does not return.
    Rewrite it to also return the character count,
    and give it the full annotation.
    Then write a caller that delegates to it with `yield from` and prints that count,
    and say which type parameter each of the two values traveled through.
6.  Explain why a driver must prime with `next()` rather than `send(None)`,
    given that the two are equivalent at runtime.
    `send_none_is_next.py` has the answer; state it in terms of the `SendType`.
7.  [A Vending Machine](31_State_Machines.md#a-vending-machine)
    keeps its current state in an attribute and looks up each transition in a table.
    Write a simplified version as a single generator instead: it collects money,
    takes two digits, then dispenses or refuses,
    yielding its current state and receiving each event with `send()`,
    so the position in the generator's body carries the state.
    This generator's `yield` reports the state the machine reached rather than requesting something the machine needs,
    the opposite direction from `interview()`.
    Say which of the two versions you would rather extend with a sixth state,
    and why.
