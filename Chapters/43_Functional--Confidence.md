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
This seems to me to be the broader challenge that functional programming takes on,
and what this chapter explores.

The preceding chapters build the machinery.
[Foundations](40_Functional--Foundations.md)
establishes pure functions and immutable values,
[Toolkits](41_Functional--Toolkits.md) supplies the standard library's support,
and [Error Handling](42_Functional--Error_Handling.md)
makes failure an ordinary value.
This chapter asks what that machinery lets you claim about your code,
and how far those claims can go.

## Referential Transparency

An expression is *referentially transparent* when you can replace it with its value without changing the program's behavior.
Pure functions have this property, and that is the reason purity matters:

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
an implementation may cache the call, run the two calls in either order,
or skip the second.
The language has no way to mark `add()` as pure,
so CPython leaves all three to you.
The same substitution serves your reasoning as well as the machine's optimization:
you can reason about the code by replacing a call with its value,
the move you make in algebra, and so check parts of a program,
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
The substitution changes `110` into `140`.
`withdraw()` is not referentially transparent,
and any expression containing it inherits the problem.
Substitution reasoning stops at the first impure call.

A `global` statement is one way to break substitution.
A function that mutates an argument is another:

```python
# mutates_argument.py
def add_item(cart: list[str], item: str) -> list[str]:
    cart.append(item)
    return cart

cart: list[str] = ["milk"]
add_item(cart, "eggs")
add_item(cart, "eggs")
print(cart)
#: ['milk', 'eggs', 'eggs']
```

Each call to `add_item()` returns the same list the caller passed in,
so replacing the call with that list looks safe.
It is not.
The call also appends to `cart`, and the list put in its place appends nothing.
Substitute the list for either call and `cart` ends with one `'eggs'` fewer.

Referential transparency is what makes [`lru_cache`](41_Functional--Toolkits.md#lru_cache)
safe: a memoizer can return a stored result because the call is interchangeable with its value.
Every optimization that skips or reuses work,
from a cache to a database query planner, benefits the same way,
and the more of your program is referentially transparent,
the more of it a machine, or a proof, can verify.

Caching an impure function returns wrong values and raises no exception.
`withdraw()` reads and writes `balance`,
so decorating it with `lru_cache` leaves `balance` wrong:

```python
# cached_withdraw.py
from functools import lru_cache

balance = 100

@lru_cache
def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(withdraw(30), withdraw(30))
#: 70 70
print(f"balance: {balance}")
#: balance: 70
```

Two withdrawals of `30` should leave `balance` at `40`.
The second call is a cache hit, so `withdraw()` runs once, subtracts one `30`,
and hands back the stored `70` the second time.
Nothing reports the skipped subtraction.
`lru_cache` returns the stored result for any repeated arguments,
and nothing in the language checks that the function it wraps is referentially transparent.

## Automatic Parallelism

A pure function is automatically parallelizable.
Each call's answer comes from its arguments alone,
so no call can affect another.
The calls can run in any order, on any schedule, on any number of cores,
and the answers stay the same.

Shared state takes that freedom away.
Two parallel `withdraw()` calls could both read `balance` before either writes it back.
The second write then overwrites the first, so `balance` records one withdrawal.
A lock makes the two calls safe,
and the lock serializes the work you wanted to overlap.
Purity removes the problem instead of managing it: with nothing shared,
a lock has nothing to guard.

`count_primes()` is pure, and each call does enough work to spread across cores:

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
because a pure call returns the same answer whichever process runs it,
and whenever.

The limits above are large enough for the difference to show.
On the machine that built this book,
the serial run took a few seconds and the parallel run about half that,
well over the 1.3x margin `faster` checks.
At smaller limits the serial run finishes before a pool has started its workers,
so if you shrink the limits back down,
the parallel run takes longer than the serial one.
Purity makes parallel safe.
Whether parallel pays at a given size is a separate question,
and the timing answers it.

Sending the calls to a worker adds requirements of its own.
Each argument and each result pickles to cross the process boundary.
The function pickles as its qualified name,
so `count_primes()` must sit at the top level of a module a worker can import.
A `lambda` or a closure fails with a `PicklingError`,
and that rules out two shapes these chapters use often.
A `functools.partial` pickles as its wrapped function plus its bound arguments.
The `if __name__ == "__main__"` guard exists for the same reason:
each worker imports this module to find `count_primes()`,
and without the guard each worker re-runs the pool-building code,
which fails in the worker with a `RuntimeError` and in the parent with `BrokenProcessPool`.
[Concurrency](19_Techniques--Concurrency.md#parallelism)
covers the pickling boundary and the guard,
along with the reasons Python parallelism uses processes rather than threads.

## A Confidence Spectrum

The chapter opens by asking whether programming can make the kind of provable claims a science makes.
Functional programming's answer is not one guarantee but a spectrum.
Purity, immutability, and referential transparency,
the properties these chapters build, provide confidence at every level.

Style contributes before the first rung.
*Declarative* code states the result you want;
*imperative* code spells out each step to produce it.
A [comprehension](16_Techniques--Comprehensions.md) names the result,
"the squares of the even numbers."
[`match`](13_Techniques--Pattern_Matching.md) names the shapes you expect,
the way [Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
takes a `Result` apart with one branch per kind of failure.
A description of the result is easier to check than a sequence of steps,
because less of it can be wrong.
It also leaves the runtime free to choose the steps, so a SQL query,
a NumPy expression, or a dataframe operation can run on an optimized or parallel engine you never call directly.

You decide how far up the spectrum to go.

1. The first rung, local reasoning, takes the least work.
   Pure functions and immutable values let you understand one piece at a time,
   with no hidden state to keep track of.
   Most code needs no more.
2. Next are tests over chosen examples,
   the subject of [Testing](11_Techniques--Testing.md).
   Each one checks a single input against a single answer,
   so the examples you invent bound what you learn.
3. Next is type checking.
   A type signature is a small theorem, and the function body is its proof.
   This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence).
   Python's version of it is partial.
   An `Any`, a `cast()`,
   or data arriving from outside the program leaves a value the type checker takes on trust,
   so the theorem holds exactly as far as the annotations reach.
   Running `ty` over the examples in this book catches a useful class of mistakes,
   and that is most of what this rung offers.
4. Above that is [*property-based testing*](#property-based-testing).
   You state a law the code must obey,
   then check it against many generated inputs.
   The check searches for a counterexample instead of proving the law,
   and that search is the falsifiability the opening requires of a science.
   What this rung adds to rung 3 is expressiveness, not certainty.
   A type states what shape a value has.
   A property can state a fact about the value's behavior,
   at the cost of checking a sample of inputs instead of every one.
5. At the top is formal proof.
   In a dependently-typed language such as Lean, Idris, or Rocq (formerly Coq),
   you prove a program correct for every possible input,
   and a machine checks the proof.
   Formal proof is real, but rare outside specialized work.

## Property-Based Testing

You can write a property check by hand,
looping over random inputs and asserting the law.
A tool like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
does the same thing with inputs it chooses at boundaries and unusual values,
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
That is the shape of every property test:
a law that states what must always be true,
and a machine that searches for a counterexample.
A bare `assert` like this one reports a broken law as an `AssertionError`,
and the traceback shows the assert's source line but not the value that broke it,
so to find that value you add a `print()` and rerun by hand.

### The Same Law in Hypothesis

Hypothesis turns the hand-written loop into a declaration.
You describe the inputs with a *strategy*,
Hypothesis's name for an input generator, and state the law once,
as a normal `test_` function.
The framework supplies the cases.
It draws on every character UTF-8 can encode rather than `property_check.py`'s five-letter alphabet,
so it reaches inputs the loop never tries, such as unusual Unicode:

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
because importing `property_check.py` runs its thousand-iteration loop inside the test run.

`@given(strategies.text())` calls `test_roundtrip()` once per generated string.
By default Hypothesis generates a hundred of them,
a tenth of the hand-written loop's thousand.
Those hundred strings cover more of the input space,
because Hypothesis generates boundary values and unusual characters instead of sampling evenly.
When a law fails, Hypothesis reports the failing input,
the first improvement over `property_check.py`'s bare `assert`.
It also shrinks that input to the smallest example that still fails,
a second improvement,
so Hypothesis reports the bug as the smallest case rather than a random one.
The framework automates falsification.

### Shrinking a Failure

`property_check.py` and `test_property.py` both pass,
and shrinking needs a failure.
The next codec has a bug,
and the bug is the unusual-Unicode case [The Same Law in Hypothesis](#the-same-law-in-hypothesis)
mentions:

```python
# shrinking.py
from hypothesis import given, settings, strategies

def encode(text: str) -> str:
    return text.encode().hex()

def decode(text: str) -> str:
    return bytes.fromhex(text).decode("latin-1")

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
```

`encode()` still turns text into UTF-8 bytes,
but `decode()` now reads those bytes back as Latin-1 instead of UTF-8.
UTF-8 and Latin-1 agree on the 128 ASCII code points,
and `property_check.py`'s five-letter alphabet sits inside those.
Every string its loop builds decodes the same way under both,
so all thousand cases pass.
Hypothesis draws from every character UTF-8 can encode.
It shrinks its failure down to the smallest code point outside that agreement,
`'\x80'`, the first character UTF-8 needs more than one byte to encode.
Decoding those two bytes as Latin-1 returns two characters where one went in,
so the round trip returns a different string.
That code point is the unusual Unicode the hand-written loop's alphabet kept out of reach.
Hypothesis found it by drawing from a wider alphabet,
treating `decode()` as opaque throughout.

`derandomize=True` seeds the search from a hash of the test function so this book gets the same answer every run,
the job `random.seed(42)` does in the hand-written loop.
`database=None` discards the example database,
so every run searches from scratch.
A real test keeps the defaults.

`roundtrip()` exists to fail, and a failing `test_` function fails the build.
`roundtrip()` therefore drops the `test_` prefix from its name,
and the listing calls it directly inside a `try`.

### A Family of Property Shapes

The *roundtrip* law is one member of a small family of reusable property shapes,
and knowing the family is most of the skill.
An *invariant* states a fact about every output:
sorting produces an ordered list.
*Idempotence* states that repeating changes nothing:
sorting a sorted list returns the same order.
An *oracle* states that two implementations agree:
the simple version you can check by reading matches the fast one.
`parallel_pure.py`'s `assert parallel == serial` makes that claim about `map()` and `pool.map()`.

The mistake to avoid is a property that restates the implementation.
Asserting `encode(text) == text.encode().hex()` tests nothing,
because the test and the code share any bug.
A good law, like the roundtrip,
constrains the function's behavior without repeating its body.

Every shape in the family requires purity:
Hypothesis can rerun and shrink freely because each call depends on its arguments alone.

## Affordable Proof

Two caveats limit the chapter's argument.
First, proof works on imperative code too:
Hoare logic and tools like Dafny verify it.
What purity changes is the cost.
With no mutable state to track, each step of the reasoning is shorter.
Functional programming does not make correctness provable so much as it makes the proof affordable.
Second, most functional code stops well below the top rung.
Haskell programmers rely on types and on reasoning by substitution,
and write a full proof for the few places that need one.

The claim these chapters share is not that functions are special.
It is that purity, immutability,
and referential transparency reduce the work of turning "I believe this is correct" into "I can show why."
A full proof does all of that work.
The everyday gain comes from doing part of it: code you can read, check,
and test as statements about what is true.
That gain, more than the presence of functions,
is the "functionality" the introduction sets out to find.

Part V extends the same discipline and asks the type checker to enforce it:
[Effect Management](44_Effects--Effect_Management.md)
puts a function's effects in its signature,
and the chapters after it build a checked system on that idea.

## Exercises

1.  Change `count_primes()` to return `(count, os.getpid())` and print the distinct process IDs alongside the counts.
    Narrow `assert parallel == serial` to compare only the counts,
    since the serial run now carries the parent's ID and the parallel one carries the workers'.
    Compare the number of distinct IDs to `os.process_cpu_count()`,
    and run `parallel_pure.py` three times before deciding what that number means.
2.  Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous exercise and explain the IDs you see instead.
3.  Write Hypothesis properties for `sorted()` using two shapes from [A Family of Property Shapes](#a-family-of-property-shapes):
    an invariant (every adjacent pair of the output is in order) and idempotence
    (sorting a sorted list changes nothing).
    Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.
4.  State a law that is false and watch Hypothesis falsify it:
    `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
    Report the counterexample Hypothesis shrinks to,
    run the test a few times to see which characters Hypothesis reports,
    and explain what those characters reveal about Unicode case mapping.
5.  Write a property test for `group_rounds()` from [Toolkits](41_Functional--Toolkits.md#groups-of-any-size):
    for any roster and any group size,
    every student appears in exactly one group per round.
    Use a strategy that generates rosters of distinct names.
    Then break `group_rounds()` on purpose, run the test twice,
    and confirm Hypothesis reports the same counterexample both times:
    Hypothesis records a failing case under `.hypothesis/` and replays it first on the next run.
6.  Write two functions that are *not* referentially transparent without using `global`:
    one that reads `datetime.now()`, and one that reads an environment variable.
    For each, name the substitution that changes the program's behavior,
    then rewrite the function so the value arrives as an argument.
7.  Take the `describe()` function from [Error Handling](42_Functional--Error_Handling.md#matching-on-the-error)
    and rewrite its `match` as `isinstance()` tests.
    Count the lines, then run `ty` on both versions and compare what it knows about the value inside the `Ok` in each.
