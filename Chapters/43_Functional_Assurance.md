# Functional Assurance

Introductions to functional programming usually call it "programming with functions,"
and functions are indeed a central part of the practice.
But after (slowly) studying it for over ten years,
I have started to wonder whether it's actually more about "functionality."
One definition of science is "what works."
Science has theories that fit the data, are predictive, and are falsifiable.
If "computer science" is to live up to its name,
there should be some ideas and practices that fit that definition,
and perhaps even some aspects that are mathematically provable.
This seems to me to be the broader challenge that functional programming takes on,
and what this chapter explores.

The preceding chapters built the machinery.
[Functional Foundations](40_Functional_Foundations.md)
established pure functions and immutable values,
[Functional Toolkits](41_Functional_Toolkits.md)
supplied the standard library's support,
and [Functional Error Handling](42_Functional_Error_Handling.md)
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

Because `add(2, 3)` and `5` are interchangeable, a compiler can cache the call,
evaluate it in any order, or skip a repeat.
You can also reason about the code by substitution,
the same move you make in algebra.
This property lets you check parts of a program,
and sometimes prove them correct,
and it connects back to this chapter's opening question about what counts as "what works."

This property is also the quiet reason [`lru_cache`](41_Functional_Toolkits.md#lru_cache)
is safe.
A memoizer may hand back a stored result only because the call is interchangeable with its value.
Every optimization that skips or reuses work,
from a cache to a database query planner,
benefits from referential transparency.
The more your program is referentially transparent, the more of it a machine,
or a proof, can verify.

## Declarative Style

*Declarative* code states the result you want.
*Imperative* code spells out each step to produce it.
A comprehension is the everyday example
(see [Comprehensions](16_Comprehensions.md)).
The loop that filters and appends says *how*.
`[n * n for n in numbers if n % 2 == 0]` says *what*,
which is "the squares of the even numbers."
It leaves the looping to Python.
This is the broader "functionality" we want.
Describe the result, and let the machine arrange the steps.
Declarative code says less and means more.
By naming the result instead of the steps,
you hand the reader your intent and give the runtime freedom to choose how to deliver it.
That freedom is why a SQL query, a NumPy expression,
or a dataframe operation can run on an optimized or parallel engine you never see.
You described the what, not a fixed sequence of moves.

## Pattern Matching as Destructuring

The `match` statement, covered in [Pattern Matching](13_Pattern_Matching.md),
is a declarative tool for taking data apart.
You describe the structures you expect, and Python binds the pieces for you.
One `match` collapses a stack of `isinstance()` tests, length checks,
and key or index lookups into a single readable description of each shape.
The test and the extraction happen together,
so there is no gap where you have confirmed the shape but not yet pulled out its parts.
This pays off most on shaped data, such as parsed JSON, an abstract syntax tree,
or the messages of a protocol,
where the alternative is a thicket of nested conditionals.
[Functional Error Handling](42_Functional_Error_Handling.md#matching-on-the-error)
put this to work, taking a `Result` apart with one branch per kind of failure.

## Automatic Parallelism

A pure function is automatically parallelizable.
Each call depends only on its arguments, so no call can affect another.
The calls can run in any order, on any schedule, on any number of cores,
and the answers do not change.

Impure code has no such freedom.
Recall `withdraw()` from [Functional Foundations](40_Functional_Foundations.md#pure-functions).
Two parallel calls could both read `balance` before either writes it back,
and one withdrawal would vanish.
Making that safe means adding a lock,
and the lock serializes the work you wanted to overlap.
Purity removes the problem instead of managing it.
With nothing shared, there is nothing to lock.

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

def main() -> None:
    limits = [10_000, 20_000, 30_000, 40_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    assert parallel == serial
    print(parallel)

if __name__ == "__main__":
    main()
```

`map()` runs the four calls one at a time, on one core.
`pool.map()` sends the same calls to worker processes,
which the operating system places on separate cores.
Run as a script, this prints `[1229, 2262, 3245, 4203]`.
The `assert` passes on every run,
because a pure call returns the same answer no matter which process ran it,
or when.
Notice there are no locks, no queues, no shared state,
and no changes to `count_primes()` itself.
The function needed no preparation for parallel execution.
It was ready the day it was written, because it was pure.
`ProcessPoolExecutor`,
and the reasons Python parallelism uses processes rather than threads,
are covered in [Concurrency](19_Concurrency.md#parallelism).

## An Assurance Spectrum

The chapter opened by asking whether programming can make the kind of provable claims a science makes.
Functional programming's honest answer is not one guarantee but a spectrum.
The properties built up here, purity, immutability,
and referential transparency, buy assurance at every level.
You decide how far to take it.

1. The cheapest rung is local reasoning.
   Pure functions and immutable values let you understand one piece at a time,
   with no hidden state to carry in your head.
   Most code never needs more.
2. Next is type checking.
   A type signature is a small theorem, and the function body is its proof.
   This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence).
   Types are propositions and programs are their proofs.
   Running `ty` over the examples in this book demonstrates that proof for a useful class of mistakes.
3. Above that is [*property-based testing*](#property-based-testing).
   You state a law the code must obey,
   then check it against many generated inputs.
   It does not prove the law.
   It works to falsify it,
   which is the falsifiability the chapter's opening requests.
4. At the top is formal proof.
   Dependently-typed languages such as Lean, Idris,
   and Rocq prove a program correct for every possible input,
   checked by machine.
   This is real, but rare outside specialized work.

### Property-Based Testing

You can write a property check by hand,
looping over random inputs and asserting the law.
A tool like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)
does the same thing with sharper inputs,
and shrinks any failure to a minimal counterexample:

```python
# property_check.py
import random

def encode(text: str) -> str:
    # A trivial reversible transform:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

random.seed(42)  # A failing search must be reproducible
alphabet = "abcde"
for _ in range(1000):
    size = random.randint(0, 8)
    sample = "".join(random.choice(alphabet) for _ in range(size))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
```

The law is "decoding an encoding returns the original,"
and it holds for every input the loop tries.
A property test states what must always be true.
The machine searches for a counterexample,
instead of forcing you to write one example at a time.

Hypothesis turns the hand-written loop into a declaration.
You describe the inputs with a *Strategy* and state the law once,
as a normal `test_` function.
The framework supplies the cases,
including awkward ones a handwritten loop would miss,
such as the empty string and unusual Unicode:

```python
# test_property.py
from hypothesis import given, strategies

def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

@given(strategies.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
```

`@given(strategies.text())` feeds `test_roundtrip()` a stream of generated strings.
When a law fails, Hypothesis does not only report the failing input.
It shrinks it to the smallest example that still fails,
so the bug surfaces as the clearest case rather than a random one.
This is automated falsification machinery.

The roundtrip law is one member of a small family of reusable property shapes,
and knowing the family is most of the skill.
An *invariant* states a fact about every output:
sorting produces an ordered list.
*Idempotence* states that repeating changes nothing:
sorting a sorted list leaves it alone.
An *oracle* states that two implementations agree: the simple,
obviously correct version matches the fast one,
which is exactly what `parallel_pure.py`'s `assert parallel == serial` already claimed.
The trap to avoid is a property that restates the implementation:
asserting `encode(text) == text[::-1]` tests nothing,
because the test and the code would share any bug.
A good law, like the roundtrip,
constrains the function's *behavior* without repeating its body.
All of these lean on purity.
Hypothesis can rerun and shrink freely only because each call is independent of every other.

Two caveats keep this honest.
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

## Exercises

1.  In `parallel_pure.py`, add a fifth limit, `50_000`, to the `limits` list,
    and confirm `parallel == serial` still holds after the change.
2.  Write Hypothesis properties for `sorted()` using two shapes from the family above:
    an invariant (every adjacent pair of the output is ordered) and idempotence
    (sorting a sorted list changes nothing).
    Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.
3.  State a law that is *false* and watch Hypothesis falsify it:
    `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
    Report the counterexample Hypothesis shrinks to,
    and explain what it reveals about Unicode case mapping.
4.  Write a property test for `group_rounds()` from [Functional Toolkits](41_Functional_Toolkits.md#case-study-pairing-rotations):
    for any roster and any group size,
    every student appears in exactly one group per round.
    Use a strategy that generates rosters of distinct names,
    and note how the seeded generator keeps failures reproducible.
