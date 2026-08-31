# Confidence

Introductions to functional programming usually call it "programming with functions,"
and functions really are a central part of the practice.
But after (slowly) studying it for over ten years,
I have started to wonder whether it's more about "functionality."
One definition of science is "what works."
Science has theories that fit the data, are predictive, and are falsifiable.
If "computer science" is to live up to its name,
some of its ideas and practices should fit that definition,
and perhaps some should even be mathematically provable.
This seems to me to be the broader challenge that functional programming takes on,
and what this chapter explores.

The preceding chapters built the machinery.
[Foundations](40_Functional--Foundations.md)
established pure functions and immutable values,
[Toolkits](41_Functional--Toolkits.md) supplied the standard library's support,
and [Error Handling](42_Functional--Error_Handling.md)
made failure an ordinary value.
This chapter asks what that machinery lets you claim about your code,
and how far those claims can go.

## Referential Transparency

An expression is *referentially transparent* when you can replace it with its value without changing the program's behavior.
Pure functions give you this property, which is the reason purity matters:

```python
# referential_transparency.py
def add(a: int, b: int) -> int:
    return a + b

# The call add(2, 3) always equals 5, so the call and the
# value 5 are interchangeable everywhere in the program.
x = add(2, 3) + add(2, 3)
y = 5 + 5
print(x, y, x == y)
#: 10 10 True
```

Because `add(2, 3)` and `5` are interchangeable,
an implementation is free to cache the call, evaluate it in any order,
or skip a repeat.
CPython does none of these on its own,
because nothing in the language marks `add()` as pure,
so you ask for the reuse yourself.
You can also reason about the code by substitution,
the same move you make in algebra.
This property lets you check parts of a program,
and sometimes prove them correct.

Substitution stops working the moment a function reads or writes outside itself.
`withdraw()` from [Foundations](40_Functional--Foundations.md#pure-functions)
does both, reading and writing the module-level `balance`:

```python
# not_transparent.py
balance = 100

def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(withdraw(30) + withdraw(30))
#: 110
balance = 100
print(70 + withdraw(30))
#: 140
```

The first `withdraw(30)` evaluates to `70`,
so substituting `70` for it ought to change nothing.
It changes `110` into `140`.
`withdraw()` is not referentially transparent,
and neither is any expression containing it,
which is why the substitution reasoning above stops at the first impure call.

This property is also the reason [`lru_cache`](41_Functional--Toolkits.md#lru_cache)
is quietly safe.
A memoizer may hand back a stored result only because the call is interchangeable with its value.
Every optimization that skips or reuses work,
from a cache to a database query planner,
benefits from referential transparency.
The more your program is referentially transparent, the more of it a machine,
or a proof, can verify.

## Automatic Parallelism

A pure function is automatically parallelizable.
Each call depends only on its arguments, so no call can affect another.
The calls can run in any order, on any schedule, on any number of cores,
and the answers do not change.

Impure code has no such freedom.
Two parallel `withdraw()` calls could both read `balance` before either writes it back,
and one withdrawal vanishes.
Making that safe means adding a lock,
and the lock serializes the work you wanted to overlap.
Purity removes the problem instead of managing it.
With nothing shared, nothing needs a lock.

`count_primes()` is pure, and each call does enough work to spread across cores:

```python
# parallel_pure.py
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n**0.5) + 1)):
            count += 1
    return count

if __name__ == "__main__":
    limits = [10_000, 20_000, 30_000, 40_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    assert parallel == serial
    print(parallel)
```

`list(map(...))` runs the four calls one at a time, on one core.
`pool.map()` sends the same calls to worker processes,
which the operating system places on separate cores.
Run as a script, this prints `[1229, 2262, 3245, 4203]`.
The `assert` passes on every run,
because a pure call returns the same answer no matter which process ran it,
or when.
No locks, no queues, no shared state:
a pure function is ready to run in parallel, unchanged.

Purity makes the calls safe to run together.
It does not make them easy to move.
Each argument and each result pickles to cross the process boundary,
and the function travels by name,
so `count_primes()` must live at the top level of a module a worker can import.
A `lambda` or a closure fails with a `PicklingError`,
which rules out two shapes these chapters favor.
A `functools.partial` survives,
because it pickles as its wrapped function plus its bound arguments.
The `if __name__ == "__main__"` guard exists for the same reason:
each worker imports this module to find `count_primes()`,
and without the guard every worker would build a pool of its own.
[Concurrency](19_Concurrency.md#parallelism) covers all of this,
along with the reasons Python parallelism uses processes rather than threads.

## Declarative Style

*Declarative* code states the result you want.
*Imperative* code spells out each step to produce it.
A comprehension is the everyday example
(see [Comprehensions](16_Comprehensions.md)).
`squares = []`, then `for n in numbers:`, then `if n % 2 == 0:`,
then `squares.append(n * n)` says *how*.
`[n * n for n in numbers if n % 2 == 0]` says *what*,
which is "the squares of the even numbers."
It leaves the looping to Python.
A description of the result is also easier to check than a sequence of steps,
because less of it can be wrong.
By naming the result instead of the steps,
you hand the reader your intent and give the runtime freedom to choose how to deliver it.
That freedom is why a SQL query, a NumPy expression,
or a dataframe operation can run on an optimized or parallel engine you do not see.
You describe the what, not a fixed sequence of moves.

`match` applies the same idea to taking data apart
(see [Pattern Matching](13_Pattern_Matching.md)).
You describe the shapes you expect and Python binds the pieces,
so one `match` replaces a stack of `isinstance()` tests, length checks,
and key or index lookups,
with no gap between confirming a shape and pulling out its parts.
[Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
put that to work, taking a `Result` apart with one branch per kind of failure.
The win is in the reading rather than in what a type checker can prove.
On a `Result[float, Exception]`,
`match` and a chain of `isinstance()` tests narrow equally well,
both reaching `float` inside the `Ok`,
because `@final` on the two classes lets either one narrow to a single class.
Destructuring merges the shape test and the extraction into one step.
It does not extend what the type checker knows.

## A Confidence Spectrum

The chapter opened by asking whether programming can make the kind of provable claims a science makes.
Functional programming's answer is not one guarantee but a spectrum.
The properties these chapters built, purity, immutability,
and referential transparency, provide confidence at every level.
You decide how far to take it.

1. The cheapest rung is local reasoning.
   Pure functions and immutable values let you understand one piece at a time,
   with no hidden state to carry in your head.
   Most code needs no more.
2. Next are tests over chosen examples, the subject of [Testing](11_Testing.md).
   Each one pins a single input to a single answer,
   so what you learn is no wider than the examples you invent.
3. Next is type checking.
   A type signature is a small theorem, and the function body is its proof.
   This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence).
   Python's version of it is partial.
   An `Any`, a `cast()`,
   or data arriving from outside the program leaves a gap no type checker can close,
   so the theorem holds only as far as the annotations do.
   Running `ty` over the examples in this book still rules out a useful class of mistakes,
   which is most of what this rung offers.
4. Above that is [*property-based testing*](#property-based-testing).
   You state a law the code must obey,
   then check it against many generated inputs.
   It does not prove the law.
   It searches for a counterexample,
   which is the falsifiability the opening required of a science.
5. At the top is formal proof.
   In a dependently-typed language such as Lean, Idris, or Rocq (formerly Coq),
   you prove a program correct for every possible input,
   and a machine checks the proof.
   This is real, but rare outside specialized work.

## Property-Based Testing

You can write a property check by hand,
looping over random inputs and asserting the law.
A tool like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
does the same thing with sharper inputs,
and shrinks any failure to a minimal counterexample:

```python
# property_check.py
import random

def encode(text: str) -> str:
    # Reversible, and not its own inverse:
    return text.encode().hex()

def decode(text: str) -> str:
    return bytes.fromhex(text).decode()

random.seed(42)  # A failing search must be reproducible
alphabet = "abcde"
for _ in range(1000):
    size = random.randint(0, 8)
    sample = "".join(random.choice(alphabet)
                     for _ in range(size))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
```

The law is "decoding an encoding returns the original,"
and it holds for every input the loop tries.
A property test states what must always be true.
The machine searches for a counterexample.

Hypothesis turns the hand-written loop into a declaration.
You describe the inputs with a *Strategy* and state the law once,
as a normal `test_` function.
The framework supplies the cases,
drawing on the whole of `str` rather than the five-letter alphabet chosen above,
so it reaches inputs the loop cannot produce, such as unusual Unicode:

```python
# test_property.py
from hypothesis import given, strategies

def encode(text: str) -> str:
    return text.encode().hex()

def decode(text: str) -> str:
    return bytes.fromhex(text).decode()

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
```

The listing repeats the two functions rather than importing them,
because importing `property_check.py` would run its thousand-iteration loop inside the test run.

`@given(strategies.text())` feeds `test_roundtrip()` a stream of generated strings.
By default Hypothesis generates a hundred of them,
a tenth of the hand-written loop's thousand, and they still cover more ground,
because it aims at boundaries and oddities instead of sampling evenly.
When a law fails, Hypothesis reports the failing input and shrinks it to the smallest example that still fails,
so the bug surfaces as the clearest case rather than a random one.
The framework automates falsification.

The two listings above both pass, so nothing has shrunk yet.
This codec has a bug:

```python
# shrinking.py
from hypothesis import given, settings, strategies

def encode(text: str) -> str:
    return text.replace(" ", "_")

def decode(text: str) -> str:
    return text.replace("_", " ")

@settings(derandomize=True, database=None)
@given(strategies.text())
def roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample

try:
    roundtrip()
except AssertionError as e:
    print(e.__notes__[0])
#: Failing test case: roundtrip(
#:     sample='_',
#: )
```

An underscore in the input comes back as a space.
Hypothesis finds a failing string and then keeps cutting it down until removing anything more makes the test pass again,
so it reports `'_'` rather than the longer string that failed first.
That single character is the whole bug statement.
`derandomize=True` fixes the search so this book gets the same answer every run,
the job `random.seed(42)` does in the hand-written loop.
`database=None` keeps it from replaying a case an earlier run saved.
A real test needs neither.
The function's name drops the `test_` prefix,
and the listing calls it directly inside a `try`:
a failing `test_` function should fail the build, and this one exists to fail.

The *roundtrip* law is one member of a small family of reusable property shapes,
and knowing the family is most of the skill.
An *invariant* states a fact about every output:
sorting produces an ordered list.
*Idempotence* states that repeating changes nothing:
sorting a sorted list leaves it alone.
An *oracle* states that two implementations agree:
the simple version you can check by reading matches the fast one,
which `parallel_pure.py`'s `assert parallel == serial` claims.
The trap to avoid is a property that restates the implementation:
asserting `encode(text) == text.encode().hex()` tests nothing,
because the test and the code share any bug.
A good law, like the roundtrip,
constrains the function's behavior without repeating its body.
All of these lean on purity.
Hypothesis can rerun and shrink freely only because each call is independent of every other.

## Affordable Proof

Two caveats keep the chapter's argument from overreaching.
First, proof is not exclusive to functional code.
Hoare logic and tools like Dafny verify imperative programs too.
What purity changes is the cost.
With no mutable state to track, each step of the reasoning is shorter.
Functional programming does not make correctness provable so much as it makes the proof affordable.
Second, most functional code stops well below the top rung.
Haskell programmers rarely prove a program correct.
They lean on types and on reasoning by substitution,
and save full proof for the few places that earn it.

The thread running through these chapters is not that functions are special.
It is that purity, immutability,
and referential transparency shrink the distance between "I believe this is correct" and "I can show why."
Proof is the far end of that distance.
The everyday win is everything below it: code you can read, check,
and test as statements about what is true.
That, more than the presence of functions,
is the "functionality" the introduction set out to find.

Part V takes the same discipline one step further and asks the type checker to enforce it:
[Effect Management](44_Effect_Management.md)
puts a function's effects in its signature,
and the chapters after it build a checked system on that idea.

## Exercises

1.  Change `count_primes()` to return `(count, os.getpid())` and print the distinct process IDs alongside the counts.
    Compare that number to `os.process_cpu_count()`,
    and run it three times before deciding what it means.
2.  Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous exercise and explain the IDs you see instead.
3.  Write Hypothesis properties for `sorted()` using two shapes from the family above:
    an invariant (every adjacent pair of the output is in order) and idempotence
    (sorting a sorted list changes nothing).
    Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.
4.  State a law that is false and watch Hypothesis falsify it:
    `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
    Report the minimal counterexample Hypothesis finds,
    and explain what it reveals about Unicode case mapping.
5.  Write a property test for `group_rounds()` from [Toolkits](41_Functional--Toolkits.md#case-study-pairing-rotations):
    for any roster and any group size,
    every student appears in exactly one group per round.
    Use a strategy that generates rosters of distinct names.
    Then break `group_rounds()` on purpose, run the test twice,
    and confirm the same counterexample arrives both times:
    Hypothesis records a failing case under `.hypothesis/` and replays it first on the next run.
6.  Write two functions that are *not* referentially transparent without using `global`:
    one that reads `datetime.now()`, and one that reads an environment variable.
    For each, name the substitution that would change the program's behavior,
    then rewrite it so the value arrives as an argument.
7.  Take the `describe()` function from [Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
    and rewrite its `match` as `isinstance()` tests.
    Count the lines, then run `ty` on both and compare what each one knows about the value inside the `Ok`.
