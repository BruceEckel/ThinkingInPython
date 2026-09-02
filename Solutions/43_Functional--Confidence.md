# Confidence: Solutions

## 1. Which process ran each call

```python
import os
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit: int) -> tuple[int, int]:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count, os.getpid()

def main() -> None:
    limits = [10_000, 20_000, 30_000, 40_000]
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(count_primes, limits))
    print([count for count, _ in results])
    print("distinct process IDs:",
          len({pid for _, pid in results}))
    print("cores:", os.process_cpu_count())

if __name__ == "__main__":
    main()
```

`ProcessPoolExecutor` needs `count_primes` picklable and importable
from `__main__` in a worker process. Only a real script file meets
that requirement, not a fenced block executed in place.

The counts stay the same, `[1229, 2262, 3245, 4203]`: the same pure
function gives the same answers wherever it ran, which is the point
of the original listing. The interesting number is the second line.
Three consecutive runs on one 32-core machine reported `2`, `3`, and
`3` distinct process IDs.

Two things follow, and neither is the one most people predict. The
count is greater than one, so the work genuinely left the main
process. The exercise set out to show exactly that, and
`assert parallel == serial` alone could never prove it. But the count
also sits far below thirty-two, and it moves between runs.
`ProcessPoolExecutor` allows one worker per core and starts a new one
only when every existing worker is busy. Each of these four tasks is
short enough that a free worker takes the next one before the pool
has any reason to grow. The pool never needed thirty-two processes,
so it never started them. A distinct-ID count is evidence that
parallelism is available, not a measure of how much the pool used.

The number depends on the core count and on scheduling, so it is
reproducible on your machine and nowhere else. That is why it does
not belong in a `#:` marker in the book.

## 2. Which thread ran each call

```python
import os
from concurrent.futures import ThreadPoolExecutor

def count_primes(limit: int) -> tuple[int, int]:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count, os.getpid()

def main() -> None:
    limits = [10_000, 20_000, 30_000, 40_000]
    with ThreadPoolExecutor() as pool:
        results = list(pool.map(count_primes, limits))
    print([count for count, _ in results])
    print("distinct process IDs:",
          len({pid for _, pid in results}))

if __name__ == "__main__":
    main()
```

The thread pool reports exactly `1`. Threads share their process, so
`os.getpid()` returns the same value in every one of them. Counting
distinct process IDs revealed process parallelism in the previous
exercise, and it says nothing at all about thread parallelism.
`threading.get_ident()` is the equivalent for threads. The two pools
present the identical `map()` interface and differ this fundamentally
underneath. That contrast is the substitutable-backend point from
[Concurrency](../Chapters/19_Techniques--Concurrency.md#one-task-many-backends).

## 3. Three property shapes for `sorted()`

```python
# test_sorted_laws.py
from hypothesis import given, strategies

def insertion_sort(xs: list[int]) -> list[int]:
    ("The obviously correct version, "
     "for the oracle property.")
    result: list[int] = []
    for x in xs:
        position = 0
        while (position < len(result)
               and result[position] <= x):
            position += 1
        result.insert(position, x)
    return result

numbers = strategies.lists(strategies.integers())

@given(numbers)
def test_output_is_ordered(xs: list[int]) -> None:
    ("Invariant: every adjacent pair "
     "of the output is ordered.")
    output = sorted(xs)
    assert all(a <= b for a, b in zip(output, output[1:]))

@given(numbers)
def test_sorting_is_idempotent(xs: list[int]) -> None:
    "Idempotence: sorting a sorted list changes nothing."
    once = sorted(xs)
    assert sorted(once) == once

@given(strategies.lists(strategies.integers(), max_size=8))
def test_agrees_with_insertion_sort(xs: list[int]) -> None:
    "Oracle: the fast version matches the simple one."
    assert sorted(xs) == insertion_sort(xs)
```

The invariant is the weakest of the three, and the interesting part is
how weak. A function that ignores its argument and returns `[]` passes
`test_output_is_ordered()` on every input, and so does one that returns
the first element alone. "Ordered" says nothing about the elements
being the same ones you handed in.

Idempotence is weaker still on its own: the same `[]`-returning
function passes it too. Idempotence buys a different kind of check,
one about the operation rather than the output. It catches a sort
that shuffles equal elements on the second pass, where the ordering
invariant sees nothing wrong.

The oracle closes the gap. `insertion_sort()` is slow and obviously
correct, so asserting that it agrees with `sorted()` pins down the
elements, their multiplicities, and their order at once. The oracle
earns its place because it repeats no part of `sorted()`'s
implementation. It arrives at the same answer by a different route.
That independence is what makes an oracle worth having, and what
makes `assert sorted(xs) == sorted(xs)` worthless. Capping the list
length keeps the quadratic oracle cheap, since the bugs it would
catch show up on short inputs.

## 4. A law that is false

```python
from hypothesis import given, strategies

@given(strategies.text())
def test_upper_lower_agrees_with_lower(s: str) -> None:
    assert s.upper().lower() == s.lower()
```

Hypothesis falsifies it in well under a second and shrinks to a
one-character string:

```text
s = 'µ'

    @given(strategies.text())
    def test_upper_lower_agrees_with_lower(s: str) -> None:
>       assert s.upper().lower() == s.lower()
E       AssertionError: assert 'μ' == 'µ'
E         - µ
E         + μ
E       Failing test case: test_upper_lower_agrees_with_lower(
E           s='µ',
E       )
```

The two sides print almost identically, so the failure hides until
you look at the code points. That is the first lesson.

```python
# test_case_mapping.py
import unicodedata

MICRO = "µ"

def test_upper_leaves_the_micro_sign_in_the_greek_block(
) -> None:
    assert unicodedata.name(MICRO) == "MICRO SIGN"
    assert (unicodedata.name(MICRO.upper())
            == "GREEK CAPITAL LETTER MU")
    assert (unicodedata.name(MICRO.upper().lower())
            == "GREEK SMALL LETTER MU")
    # Already lowercase, so unchanged
    assert MICRO.lower() == MICRO
    assert MICRO.upper().lower() != MICRO.lower()
```

`µ` is U+00B5 MICRO SIGN, a character Latin-1 kept separate from the
Greek letter it looks like. `µ` is already lowercase, so `.lower()`
returns it unchanged. But it has no uppercase form of its own, so
`.upper()` maps it to U+039C GREEK CAPITAL LETTER MU, and lowering
that gives U+03BC GREEK SMALL LETTER MU. The round trip lands one
block away from where it started.

Unicode case mapping is not a pair of inverse functions. It is a
many-to-one mapping in each direction, over a repertoire containing
characters that are lowercase without being the lowercase of
anything. `ß` breaks the same law from the other side: `"ß".upper()`
is `"SS"`, two characters, so uppercasing can change a string's
length. One rule survives. `str.casefold()`, rather than
`str.lower()`, is the operation intended for case-insensitive
comparison, and even `casefold()` promises no reversibility.

A hand-written loop over `"abcde"` would never have reached `µ`. The
generated strings reach the parts of the repertoire nobody thinks to
type, and that reach is the argument for property testing in one
example.

## 5. A property test for `group_rounds()`

```python
# test_group_rounds.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice
from hypothesis import given, strategies

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()
    rng = random.Random(seed)
    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[str]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                closest = min(pool, key=lambda c: sum(
                    history[frozenset((m, c))]
                    for m in group))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        for extra in pool:
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

rosters = strategies.lists(
    strategies.text("abcdefghij", min_size=1, max_size=3),
    min_size=2, max_size=12, unique=True)

@given(rosters,
       strategies.integers(min_value=2, max_value=5))
def test_every_student_appears_once_per_round(
        names: list[str], size: int) -> None:
    for grouping in islice(group_rounds(names, size), 3):
        placed = [*group for group in grouping]
        assert sorted(placed) == sorted(names)
```

The `unique=True` on the roster strategy is doing real work.
`group_rounds()` keys its history by `frozenset` of names, so two
students sharing a name are one student to the algorithm. The
property would then fail for a reason that says nothing about the
code.
Generating distinct names states that precondition where the test can
see it.

The two lines guarding an empty `groups` are the interesting part,
because the property test found the need for them. Against the
version without them, Hypothesis reports `names=['a', 'aa'], size=3`
and a `ValueError: min() iterable argument is empty`. With fewer
students than the group size, the `while len(pool) >= size` loop
never runs and `groups` stays empty. The leftover loop then asks
`min()` for the smallest of nothing.

The crash is a real defect rather than an unstated precondition, and
the distinction is worth drawing. `group_rounds()` already keeps
everyone in a group when a roster divides unevenly, folding the
leftovers into existing groups, so the answer for a roster of two and
a size of five is one group of two. Crashing is the one answer
inconsistent with what the function does everywhere else. The chapter
carries the fix now, so the test above passes with no `assume()`.

Finding the defect took no cleverness and no thought about edge
cases. The strategy generates small rosters because Hypothesis
prefers small examples, so a size of `3` against a roster of `2` came
up on its own. The property said what should have been true for every
roster.

Breaking the function on purpose is the other half of the exercise.
Delete the loop that places leftovers:

```python
        for extra in pool:
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
```

`group_rounds()` now drops the students who do not fill a whole
group, and the property reports the loss at once:

```text
E           AssertionError: assert ['a', 'b'] == ['a', 'b', 'c']
E             Right contains one more item: 'c'
E           Failing test case: test_every_student_appears_once_per_round(
E               names=['a', 'b', 'c'],
E               size=2,
E           )
```

Three students in groups of two is the smallest roster that leaves
anyone over, and `['a', 'b', 'c']` is the simplest such roster the
alphabet allows. The report therefore shows the shrunk case, not
whatever wide random roster failed first.

A second run reports the identical counterexample, and reports it
noticeably faster. Hypothesis writes each failing case into
`.hypothesis/examples/` and replays that database before generating
anything new, so it re-finds the failure you are in the middle of
fixing instead of leaving it to chance. The shrunk case therefore
behaves like a regression test you never had to write. It keeps
failing until you fix the bug, then rejoins the pool of examples and
comes up again on every later run.

## 6. Two impure functions with no `global` in sight

```python
# opaque_inputs.py
import os
from collections.abc import Mapping
from datetime import datetime, timedelta

def stale(created: datetime, limit: timedelta) -> bool:
    return datetime.now() - created > limit

def timeout() -> int:
    return int(os.environ.get("TIMEOUT", "30"))

def stale_pure(
    created: datetime, limit: timedelta, now: datetime
) -> bool:
    return now - created > limit

def timeout_pure(env: Mapping[str, str]) -> int:
    return int(env.get("TIMEOUT", "30"))

made = datetime(2020, 1, 1)
noon = datetime(2020, 1, 1, 12)
print(stale_pure(made, timedelta(days=1), noon))
#: False
print(timeout_pure({"TIMEOUT": "5"}), timeout_pure({}))
#: 5 30
```

Neither impure function assigns to anything, which is the lesson.
`global` is the loud way to break referential transparency.
`stale()` and `timeout()` are quiet ones: both *read* state the
caller cannot see.

The substitution that breaks `stale()` is replacing a call with the
answer it just gave. `stale(made, timedelta(hours=12))` returns
`False` at 11:00 and `True` at 13:00, so writing down `False` and
substituting it changes the program the moment the clock passes noon.
Nothing in the signature warns you, because `datetime.now()` is an
argument the function takes without declaring.

`timeout()` breaks the same way across a boundary that is easier to
miss, since the environment usually holds still during a run.
Substituting `30` for `timeout()` is correct until someone sets
`TIMEOUT`, and then the substituted version and the original disagree
while both still look right. Tests show the problem first: one test
that sets the variable changes the answer for every test after it, in
a way no argument list records.

The repair is the same for both, and it is the one this part of the
book keeps making. Move the hidden input into the parameter list.
`stale_pure()` takes the current time, and `timeout_pure()` takes the
mapping to read. Both are now referentially transparent, and both are
testable without a clock or a monkeypatched environment. The caller
that does read the real clock or the real `os.environ` becomes one
line at the edge of the program instead of a dependency buried in the
middle of it. [Testing](../Chapters/11_Techniques--Testing.md#random-numbers)
makes the same move for a random source.

## 7. `match` against `isinstance()` on the same function

```python
# describe_isinstance.py
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

def reciprocal(text: str) -> Result[float, Exception]:
    try:
        return Ok(1 / int(text))
    except (ValueError, ZeroDivisionError) as e:
        return Err(e)

def describe(text: str) -> str:
    result: Result[float, Exception] = reciprocal(text)
    if isinstance(result, Ok):
        return f"{text}: {result.answer}"
    if isinstance(result.error, ValueError):
        return f"{text}: Not a number"
    if isinstance(result.error, ZeroDivisionError):
        return f"{text}: Cannot divide by zero"
    return f"{text}: {type(result.error).__name__}"

for sample in ("4", "0", "OOPS"):
    print(describe(sample))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

The two versions produce identical output, and the `match` is the
shorter of the two by a few lines, but length is not what separates
them. The `match` reads as one description of four shapes while the
`isinstance()` version reads as four separate questions.
The difference shows in what each version repeats: `result.error`
appears three times in `describe_isinstance.py` and never in the
`match`, because each `case` matches on the error directly instead of
reading it back off `result`. The final `return` is also weaker than
the `match`'s `case Err(error)`. It is a fallthrough that happens to
be correct rather than a branch stating what it matches, so a reader
has to reconstruct that `result` must be an `Err` by ruling out the
`Ok` branch above.

`ty` reports the same thing about both. Inside the `Ok` it knows
`float` either way, and in the error branches it knows `Exception`
narrowed to `ValueError` or `ZeroDivisionError`. That agreement is
recent, and it rests on one decorator: both `Ok` and `Err` carry
`@final`, in the listing above and in `utils/result.py`. Without that
decorator a type checker must allow for a class inheriting from both,
so a positive `isinstance()` leaves the intersection of the two alive
and `result.answer` comes back as `float | Unknown` under `ty` 0.0.77
rather than plain `float`. The measurement the
exercise asks for therefore has two answers depending on one
decorator, and that is a more useful finding than either version
winning.

The choice is about reading, not about proving. Neither form tells
the type checker anything the other cannot, so pick the one that
states the shapes you expect: the `match`.
