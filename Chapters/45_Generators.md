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
but nothing here is specific to that library.

## Annotating a Generator

Earlier examples annotate every generator using the short form `Iterator[int]`.
That fits a generator that only produces values.

A generator that also receives values needs the full annotation:

    Generator[YieldType, SendType, ReturnType]

This names the three things a generator exchanges with its caller:

- `YieldType` is the value `yield` hands out,
  thus the value `next(generator)` returns.
- `SendType` is the type `send()` accepts,
  thus the type the `yield` expression produces inside the generator.
- `ReturnType` is the value produced by the `return` statement in the generator,
  delivered as `StopIteration.value`.

The default value for the last two type parameters is `None`.
An `Iterator` is the simplest form of a `Generator`:

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
`Iterator[int]` says the same thing and reads better for a one-way generator.
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
With `NewType` we can give each channel a distinct type,
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

The first call made on a new generator object must be `next()`.
A newly created generator pauses before its first `yield`,
so there is no suspended `yield` expression to receive a sent value.
If you call `i.send(Answer("Alice"))` at that point, it raises a `TypeError`.

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
The `# type: ignore` is interesting.
`interview()` declares `Answer` as its `SendType`,
and `None` is not of type `Answer`.
The checker rejects the priming `send()` even though the interpreter accepts it.
The equivalence is a runtime fact the annotation cannot express,
which is the practical reason a driver primes with `next()`.

The `NewType` definitions prevent accidental transposition.
If you mistakenly annotate the generator as `Generator[Answer, Question, Result]`,
`ty` reports nine errors in three groups of three.
All three `yield Question(...)` expressions offer a `Question` where the annotation promises an `Answer`.
All three `send(Answer(...))` calls pass an `Answer` where `send()` expects a `Question`.
All three `question` variables receive an `Answer` where they are declared `Question`.
Each channel has its own type, so the checker catches every transposition.
`Generator[str, str, str]` would have accepted the reversal without complaint.

## A Generator Is a Description

[Effect Management](44_Effect_Management.md#effect-management-for-python)
showed that calling an `async def` function runs nothing.
It returns a coroutine: a description of work.
A coroutine's annotation is `Coroutine[YieldType, SendType, ReturnType]`,
the same three-part shape as a `Generator`, and the match is deliberate.
`async def` and generator functions both build descriptions that something else drives.
Calling `interview()` returns a generator object but doesn't run anything in the function body.
`next()` and `send()` do that work, one `yield` at a time.

A generator is more interesting than a coroutine here because `yield` is a two-way channel.
The generator yields a value out, and the caller sends a value back in.
That conversation makes an EMS possible.
The generator yields a *request*, and whatever drives it supplies the *answer*.
Typically, that stepping happens in a driver:

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
        try:
            print(f"{request = }, {answers[request] = }")
            request = conversation.send(answers[request])
        except StopIteration as stop:
            return stop.value

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
```

The generator is imported unchanged; only the driver is new.
`drive()` touches all three type parameters:
`next()` produces the first `Question`,
`send()`'s argument supplies the `Answer`,
and `stop.value` in the `except` clause becomes the `Result` that `drive()` returns.
The `answers` map is keyed by `Question` and holds `Answer`s.

Notice that `interview()` does not know where the answers come from.
It has no dictionary, no `input()` call, and no network connection.
It states what it needs and waits.
`drive()` decides how those needs are met,
and it takes the answers as a parameter.
Swapping the dictionary for a database changes a single argument.

That is EMS in miniature.
The generator declares Effects, the driver interprets them.

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

Each `yield from` runs its target until that generator is exhausted,
so the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three.
The number of contributions is a property of the target.

Exhaustion is transitive.
`top()` delegates to `outer()`, which delegates to `one()` and `three()`,
and the driver still receives one flat sequence.
`top()`'s single `yield from` does not finish until every generator beneath it has.

### The Return Channel

A `yield from` expression evaluates to the inner generator's return value,
not its yielded values.
The yielded values pass through to whoever is driving.
Here, `report()` captures the return value from `yield from emit(items)` into `size`.
Note that `report()` returns nothing and only yields:

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

### The Send Channel

The `SendType` is the type of the information a caller sends back into the generator.
A generator that only receives values needs no `ReturnType`:

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
so the return signature becomes `Generator[str, int]`.
`both()` declares that same type,
because `yield from` passes the inner generator's yield and send channels through to the driver.

The numbers travel down to the `yield` that asked for them.
`g.send(1)` arrives inside `collect("alpha")`, two frames below the driver.
`both()` contains no code that forwards the value because `yield from` does that forwarding.

`g.send(2)` is the interesting one.
It supplies alpha's second value, which lets `collect("alpha")` finish,
which completes the first `yield from`, which starts the second one.
A single `send()` therefore ends one inner generator and produces the first prompt of the next.
The driver sees `StopIteration` only when `both()` runs out of delegations.

### All Three Channels

We can apply `yield from` to our `interview()` example:

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
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
```

`drive()` never learns that `ask()` exists.
Only the generator portion changed.

`ask()` uses `Answer` in two of the three positions, for two different reasons.
As the `SendType` it is the value the driver sends in,
which arrives as the value of the `yield` expression and lands in `answer`.
As the `ReturnType` it is the value `ask()` hands back when it finishes,
which `yield from` produces as the value of the whole `yield from` expression.
The inner generator asks one question and hands back one answer,
so both channels carry an `Answer`.
`interview()` keeps `Result` as its `ReturnType`,
because the sentence it builds from three answers is not an answer to any one question.

The trace shows both directions of travel.
A request raised two frames down inside `ask()` surfaces at `drive()`,
which knows nothing about where it came from.
The answer `drive()` sends back arrives inside `ask()`,
which also knows nothing about where it came from.
A single loop at the edge of the program interprets Effects raised anywhere inside it.
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
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: request = 'color', answers[request] = 'blue'
#: ask(question = 'color') -> answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
```

`interview()` is imported unchanged from the previous example.
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
Stack delegations as deep as you like and the number of drivers stays at one.

What separates them is the response to a request.
`drive()` answers it: a `Question` comes out, the driver looks it up,
and the request stops there.
`yield from` answers nothing.
It relays the request upward and passes the reply back down untouched,
so `survey()` has no idea what a `Question` means.
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
the requests have to reach the loop.

Once you see a program that way,
the question stops being what a function does and becomes what it asks for.
That is the question the next chapter puts into the type system.

## Exercises

1.  Write `tally()`, a generator that yields a prompt string,
    receives an `int` for each prompt, and returns the total once it has three.
    Give it the full three-parameter annotation,
    then drive it by hand with `next()` and `send()` and read the total off `StopIteration`.
2.  `drive()` answers from a `dict`.
    Write a second driver that answers from an `Iterator[Answer]`, in order,
    and run `interview()` under both.
    Explain what had to change in `interview()`, and why.
3.  Predict the output of `yield_from_send.py` after adding a third `yield from collect("gamma")` to `both()` and extending the loop to `[1, 2, 3, 4, 5]`.
    Write down the sequence of printed lines before running it.
4.  Remove `yield from` in `yield_from_nested.py`,
    leaving `profile = interview()`.
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
