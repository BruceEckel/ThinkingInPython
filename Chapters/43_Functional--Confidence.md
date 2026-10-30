# Confidence

> A test shows that the code worked on the inputs you tried.
> The functional discipline lets you make claims about the inputs you did not try.

Introductions to functional programming usually call it "programming with functions,"
and functions really are a central part of the practice.
But after (slowly) studying it for over ten years,
I have started to wonder whether it's more about "functionality."
One definition of science is "what works."
Science has theories that fit the data, are predictive, and are falsifiable.
If "computer science" is to live up to its name,
some of its ideas and practices should fit that definition,
and perhaps some should even be mathematically provable.
This seems to me to be the broader challenge that functional programming tackles.

The preceding chapters build the machinery.
[Functional Foundations](40_Functional--Foundations.md)
establishes pure functions and immutable values,
[Functional Toolkits](41_Functional--Toolkits.md)
supplies the standard library's support,
and [Error Handling](42_Functional--Error_Handling.md)
makes failure an ordinary value.
This chapter asks what that machinery lets you claim about your code,
and how far those claims can go.

## Referential Transparency

An expression is *referentially transparent* when you can replace it with its value and the program behaves the same.
Pure functions have this property, and that is the reason purity matters:

```python
# referential_transparency.py
def add(a: int, b: int) -> int:
    return a + b

x = add(2, 3) + add(2, 3)
y = 5 + 5
print(x, y, x == y)
#: 10 10 True
```

`add(2, 3)` always returns `5`,
so the call and the value are interchangeable everywhere in the program.
An implementation may therefore cache the call,
run the two calls in either order, or skip the second.
The language has no way to mark `add()` as pure, so CPython runs both calls,
left to right, and any cache is yours to add.

The same substitution serves your reasoning as well as the machine's optimization.
You can reason about the code by replacing a call with its value,
as you do in algebra.
That substitution lets you check parts of a program,
and sometimes prove them correct.

Substitution breaks the moment a function reads something that can change,
or writes outside itself.
[`withdraw()`](40_Functional--Foundations.md#pure-functions) does both,
reading and writing the module-level `balance`:

```python
# not_transparent.py
type Balance = int

balance: Balance = 100

def withdraw(amount: int) -> Balance:
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
so substituting `70` for it ought to leave the result at `110`.
The substitution changes `110` into `140`.
`withdraw()` is not referentially transparent.
Every expression that calls it fails the same substitution.

A `global` statement is one way to break substitution.
A function that mutates an argument is another:

```python
# mutates_argument.py
def add_item(cart: list[str], item: str) -> list[str]:
    cart.append(item)
    return cart

cart: list[str] = ["milk"]
first = add_item(cart, "eggs")
add_item(cart, "eggs")
print(cart)
#: ['milk', 'eggs', 'eggs']
cart = ["milk"]
first = ["milk", "eggs"]  # [1]
add_item(cart, "eggs")
print(cart)
#: ['milk', 'eggs']
```

Each call to `add_item()` returns the same list the caller passed in,
so replacing the call with that list looks safe.
It is not.
The call also appends to `cart`.
The list put in its place leaves `cart` as it was.
The rest of the listing puts the returned list in place of the `add_item()` call that produced it
(`[1]`).

Referential transparency makes [`lru_cache`](41_Functional--Toolkits.md#lru_cache)
safe.
A memoizer can return a stored result because the call is interchangeable with its value.
Every optimization that skips or reuses work depends on the same interchangeability,
from a cache to a database query planner.
The more of your program is referentially transparent,
the more of it a machine optimizes and a proof covers.

Caching an impure function quietly returns wrong values.
Because `withdraw()` reads and writes `balance`,
decorating it with `lru_cache` leaves `balance` wrong:

```python
# cached_withdraw.py
from functools import lru_cache

type Balance = int

balance: Balance = 100

@lru_cache
def withdraw(amount: int) -> Balance:
    global balance
    balance -= amount
    return balance

print(withdraw(30), withdraw(30))
#: 70 70
print(f"balance: {balance}")
#: balance: 70
print(withdraw.cache_info())
#: CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

Two withdrawals of `30` should leave `balance` at `40`.
The second call is a cache hit, so `lru_cache` answers it with the stored `70`.
The body of `withdraw()` runs once, for the first call, and subtracts one `30`.
The skipped subtraction passes silently.
`lru_cache` returns the stored result for any repeated arguments,
and never checks whether the wrapped function is referentially transparent.

## Automatic Parallelism

A pure function is automatically parallelizable.
Each call's answer comes from its arguments alone, so the calls are independent.
The calls can run in any order, on any schedule, on any number of cores,
and still return the same answers.

Shared state makes the answers depend on the schedule.
Two parallel `withdraw()` calls can both read `balance` before either writes it back.
The second write then overwrites the first, so `balance` records one withdrawal.
A lock makes each call finish its read and write before the other call reads `balance`,
but the lock serializes the work you wanted to overlap.
Purity removes the problem instead of managing it.
With nothing shared, a lock has nothing to guard.

`count_primes()` is pure,
and each call does enough work to be worth sending to a separate core:

```python
# parallel_pure.py
import time
from concurrent.futures import ProcessPoolExecutor
from benchmark import report

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n**0.5) + 1)):
            count += 1
    return count

if __name__ == "__main__":
    limits = [200_000, 400_000, 600_000, 800_000]
    start = time.perf_counter()
    serial = list(map(count_primes, limits))
    serial_time = time.perf_counter() - start
    start = time.perf_counter()
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    parallel_time = time.perf_counter() - start
    assert parallel == serial
    report(serial=serial_time, parallel=parallel_time)
    print(parallel)
    # Sample run: [17984, 33860, 49098, 63951]
    faster = serial_time > 1.3 * parallel_time
    print(f"serial at least 1.3x parallel time: {faster}")
    # Sample run: serial at least 1.3x parallel time: True
```

`list(map(...))` runs the four calls one at a time, on one core.
`pool.map()` sends the same calls to worker processes,
which the operating system places on separate cores.
The `assert` passes on every run,
because a pure call returns the same answer whichever process runs it and whenever it runs.
Like `map()`, `pool.map()` returns the answers in the order of `limits`,
whichever call finishes first, so the two lists match position by position.

The limits in `parallel_pure.py` are large enough for the parallel run to finish sooner.
[`report()`](18_Techniques--Performance.md#numbers-on-your-machine)
prints the two times only when you run the listing with `--numbers`.
On the machine that built this book,
the serial run took a few seconds and the parallel run about half that,
a speedup well over the 1.3x margin `faster` checks.
At small enough limits the serial run finishes before a pool has started its workers.
At those sizes the parallel run takes longer than the serial one.
Purity guarantees that the parallel run returns the serial run's answers.
Whether parallel runs faster at a given size is a separate question,
and the timing answers it.

Sending the calls to a worker adds requirements.
Each argument and each result pickles to cross the process boundary.
The function pickles as its qualified name,
so `count_primes()` must sit at the top level of a module a worker can import.
A `lambda` or a [closure](40_Functional--Foundations.md#closures)
fails with a `PicklingError`.
That rules out two shapes these chapters use often.
By contrast, a `functools.partial` pickles as its wrapped function plus its bound arguments,
so a `partial` of a top-level function carries to a worker the argument a closure captures.

The `if __name__ == "__main__"` guard follows from the same import.
Each worker imports this module to find `count_primes()`.
Without the guard, each worker re-runs the pool-building code,
which fails in the worker with a `RuntimeError` and in the parent with `BrokenProcessPool`.
[Concurrency](19_Techniques--Concurrency.md#parallelism)
covers the pickling boundary and the guard,
along with why CPU-bound work goes to processes rather than threads unless the interpreter is free-threaded.

## A Confidence Spectrum

Can programming make provable claims?
Functional programming answers with a spectrum, not a single guarantee.
These chapters build three properties: purity, immutability,
and referential transparency.
Together they provide confidence at every level.

Style contributes before the first rung of that spectrum.
*Declarative* code states the result you want.
*Imperative* code spells out each step to produce it.
A [comprehension](16_Techniques--Comprehensions.md) describes the result,
"the squares of the even numbers."
[`match`](13_Techniques--Pattern_Matching.md) describes the shapes you expect,
the way [Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
takes a `Result` apart with one branch per kind of failure.
A description of the result is easier to check than a sequence of steps,
because it has no intermediate state, such as an accumulator or a loop counter,
to get wrong.

A description of the result also leaves the steps to the runtime.
A SQL query, a NumPy expression, or a dataframe operation describes its result.
The library chooses an optimized or parallel engine to compute that result.

You decide how far up the spectrum to go.

1. The first rung, local reasoning, takes the least work.
   Pure functions and immutable values let you understand one piece at a time,
   with no hidden state to track.
   For most code, this rung is enough.
2. Next are tests over chosen examples,
   the subject of [Testing](11_Techniques--Testing.md).
   Each test checks a single input against a single answer,
   so the examples you invent bound what you learn.
3. Next is type checking.
   A type signature is a small theorem, and the function body is its proof.
   This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence).
   Python's version of it is partial.
   The type checker takes some types on trust: an `Any`, a `cast()`,
   or the type written for data arriving from outside the program.
   The theorem holds only for the code where the checker verifies every type.
   Running `ty` over the examples in this book reports mistakes such as an argument of the wrong type,
   a misspelled attribute, or a possibly-`None` value used without a check,
   and that is most of what this rung offers.
4. Above that is [*property-based testing*](#property-based-testing).
   You state a law the code must obey,
   then check it against many generated inputs.
   The check searches for a counterexample instead of proving the law.
   That search is the falsifiability the opening requires of a science.
   What this rung adds to rung 3 is expressiveness, not certainty.
   A type states what shape a value has.
   A property can state a fact about a function's behavior,
   but it checks a sample of the inputs.
5. At the top is formal proof.
   In a dependently typed language such as Lean, Idris, or Rocq (formerly Coq),
   you prove a program correct for every possible input.
   A machine checks the proof.
   Formal proof is real, but rare outside specialized work.

## Property-Based Testing

The functions under test are an encoder and its decoder,
in a module of their own so that every test can import them.
`encode()` writes the text's UTF-8 bytes as hexadecimal digits,
and `decode()` turns the digits back into text.
`encode()` is not its own inverse,
so a test that encodes and then decodes exercises two different functions:

```python
# codec.py
def encode(text: str) -> str:
    return text.encode().hex()

def decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode()
```

A hand-written property check loops over random inputs and asserts the *roundtrip* law:
decoding an encoding returns the original.

```python
# property_check.py
import random
from codec import decode, encode

random.seed(42)  # A failing search must be reproducible
alphabet = "abcde"
for _ in range(1000):
    sample = "".join(
        random.choices(alphabet, k=random.randint(0, 8)))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
```

Every property test has this shape: a law that states what must always be true,
and a machine that searches for a counterexample.

A bare `assert` like this one reports a broken law as an `AssertionError`.
The traceback shows the assert's source line and leaves out the value that broke the law.
To find that value, you add a `print()` and rerun.
A tool like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
runs the same search with inputs it chooses at boundaries and unusual values,
and shrinks any failure to a minimal counterexample.

### The Same Law in Hypothesis

Hypothesis replaces the hand-written loop with a declaration.
You describe the inputs with a *strategy*,
Hypothesis's name for an input generator, and state the law once,
as a normal `test_` function.
The framework supplies the cases.
It draws on every character UTF-8 can encode,
so it reaches inputs that `property_check.py`'s five-letter alphabet excludes,
such as unusual Unicode:

```python
# test_property.py
from codec import decode, encode
from hypothesis import given, strategies

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
```

`@given(strategies.text())` wraps `test_roundtrip()`,
and each call to the wrapper runs the original body once per generated string.
By default Hypothesis generates a hundred of them,
a tenth of the hand-written loop's thousand.
Those hundred strings cover more of the input space,
because Hypothesis generates boundary values and unusual characters instead of sampling evenly.

When a law fails, Hypothesis reports the failing input,
which `property_check.py`'s bare `assert` leaves out.
Hypothesis also shrinks that input to the smallest example that still fails,
so the report shows the simplest failing case rather than whichever random one failed first.
The framework automates falsification.

### Shrinking a Failure

Shrinking needs a failure,
but `property_check.py` and `test_property.py` both pass.
The next codec has a bug that Hypothesis exposes with [unusual Unicode](#the-same-law-in-hypothesis):

```python
# shrinking.py
from codec import encode
from hypothesis import given, settings, strategies

def decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode("latin-1")

@settings(derandomize=True, database=None)
@given(strategies.text())
def roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample

try:
    roundtrip()
except AssertionError as e:
    print(e.__notes__[0])
#: Failing test case: roundtrip(
#:     sample='\x80',
#: )
print(repr(decode(encode("\x80"))))  # [1]
#: 'Â\x80'
```

`shrinking.py` imports `encode()` from `codec.py`,
so text still becomes UTF-8 bytes.
But `shrinking.py` defines its own `decode()`,
which reads those bytes back as Latin-1 instead of UTF-8.
UTF-8 and Latin-1 agree on the 128 ASCII code points,
and `property_check.py`'s five-letter alphabet is all ASCII.
Every string its loop builds decodes the same way under both,
so all thousand cases pass.

Hypothesis draws from every character UTF-8 can encode.
It shrinks its failure to `'\x80'`,
the smallest code point on which the two decodings disagree.
`'\x80'` is the first character UTF-8 encodes in two bytes instead of one.
Decoding those two bytes as Latin-1 returns two characters where one went in
(`[1]`), so the round trip returns `'Â\x80'` instead of `'\x80'`.
That code point is the unusual Unicode the hand-written loop's alphabet excludes.
Hypothesis finds it by calling `decode()` and comparing results,
without reading its body.

`derandomize=True` seeds the search from a hash of the test function,
so this book gets the same answer on every run.
`random.seed(42)` makes the hand-written loop draw the same strings on every run.
`database=None` turns off the example database,
so every run searches from scratch.
A real test keeps both defaults,
a randomized search and a database that replays past failures.

`roundtrip()` exists to fail, so the listing calls it inside a `try`.
Its name drops the `test_` prefix,
since it is a demonstration rather than a test for pytest to collect.

### A Family of Property Shapes

The roundtrip law belongs to a small family of reusable property shapes.
Knowing the family is most of the skill.
An *invariant* states a fact about every output.
Sorting produces an ordered list.
*Idempotence* states that running an operation twice gives the same result as running it once.
Sorting a sorted list returns the same order.
An *oracle* states that two implementations agree.
The simple version you can check by reading matches the fast one.
`parallel_pure.py`'s `assert parallel == serial` makes that claim about `map()` and `pool.map()`.

Avoid a law that restates the implementation.
Asserting `encode(text) == text.encode().hex()` compares `encode()` with a copy of its body,
so the test and the code share any bug.
A good law, like the roundtrip law,
constrains what the function computes and leaves the body to decide how.

Every shape in the family requires purity.
Hypothesis can rerun and shrink freely because each call depends on its arguments alone.
A test whose outcome also depends on hidden state can pass when Hypothesis replays the failing input.
Hypothesis then raises a `FlakyFailure` in place of a shrunk counterexample.

## Affordable Proof

Two caveats limit the chapter's argument.
First, proof works on imperative code too.
Hoare logic and tools like Dafny verify imperative code.
Purity changes the length of the proof.
With no mutable state to track, each step of the reasoning is shorter.
Functional programming does not make correctness provable so much as it makes the proof short enough to write.

Second, most functional code stays well below the top rung.
Haskell programmers rely on types and on reasoning by substitution,
and write a full proof for the few places that need one.

The claim these chapters share is that purity, immutability,
and referential transparency reduce the work of turning "I believe this is correct" into "I can show why."
A full proof does all of that work.
The everyday gain comes from doing part of it: code you can read, check,
and test as statements about what is true.
That gain, more than the presence of functions,
is the "functionality" the introduction sets out to find.

Part V extends the same discipline and asks the type checker to enforce it.
[Effect Management](44_Effects--Effect_Management.md)
puts a function's effects in its signature,
and the chapters after it build a checked system on that idea.

## Exercises

Try each exercise before opening its [solution](../Solutions/43_Functional--Confidence/).

1.  Change `count_primes()` to return `(count, os.getpid())` and print how many distinct process IDs appear alongside the counts.
    Narrow `assert parallel == serial` to compare only the counts,
    since the serial run now carries the parent's ID and the parallel one carries the workers' IDs.
    Compare the number of distinct IDs to `os.process_cpu_count()`,
    and run `parallel_pure.py` three times before deciding what that number means.
2.  Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous exercise and explain the IDs you see instead.
3.  Write Hypothesis properties for `sorted()` using two shapes from [A Family of Property Shapes](#a-family-of-property-shapes):
    an invariant (every adjacent pair of the output is in order) and idempotence
    (sorting a sorted list returns an equal list).
    Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.
4.  State a law that is false and watch Hypothesis falsify it:
    `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
    Report the counterexample Hypothesis finds after shrinking.
    Run the test a few times,
    deleting the `.hypothesis/` directory before each run,
    to see which characters Hypothesis reports.
    Then explain what those characters reveal about Unicode case mapping.
5.  Write a property test for `group_rounds()` from [Functional Toolkits](41_Functional--Toolkits.md#groups-of-any-size):
    for any roster and any positive group size,
    every student appears in exactly one group per round.
    Use a strategy that generates rosters of distinct names.
    Then break `group_rounds()` on purpose, run the test twice,
    and confirm Hypothesis reports the same counterexample both times.
    Hypothesis records a failing case under `.hypothesis/` and replays it first on the next run.
6.  Without using `global`,
    write two functions that break referential transparency:
    one that reads `datetime.now()`, and one that reads an environment variable.
    For each, name the substitution that changes the program's behavior,
    then rewrite the function so the value arrives as an argument.
7.  Take the `describe()` function from [Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
    and rewrite its `match` as `isinstance()` tests.
    Count the lines, then run `ty` on both versions and compare the type it infers for the value inside the `Ok` in each.
