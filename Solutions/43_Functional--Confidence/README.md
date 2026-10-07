# Confidence: Solutions

## 1. Which process ran each call

> Change `count_primes()` to return `(count, os.getpid())` and print the distinct process IDs alongside the counts.
> Narrow `assert parallel == serial` to compare only the counts,
> since the serial run now carries the parent's ID and the parallel one carries the workers'.
> Compare the number of distinct IDs to `os.process_cpu_count()`,
> and run `parallel_pure.py` three times before deciding what that number means.

<details>
<summary>Where to look</summary>

[Automatic Parallelism](../../Chapters/43_Functional--Confidence.md#automatic-parallelism) runs a pure function through `ProcessPoolExecutor.map()`.
Have `count_primes()` return `os.getpid()` with the count, and collect the IDs into a `set`.
Compare its size to `os.process_cpu_count()`, and ask when the pool starts a worker.

<details>
<summary>Solution</summary>

If you keep `assert parallel == serial` from `parallel_pure.py`,
the script stops with a bare `AssertionError` before it prints a line.
Each pair now carries the ID of the process that computed it,
so no parallel result can equal its serial twin.
The solution compares the counts alone, the part a pure function guarantees.

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
    limits = [200_000, 400_000, 600_000, 800_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    counts = [count for count, _ in parallel]
    assert counts == [count for count, _ in serial]
    print(counts)
    print("distinct process IDs:",
          len({pid for _, pid in parallel}))
    print("cores:", os.process_cpu_count())

if __name__ == "__main__":
    main()
```

**Keep the worker function importable.** `ProcessPoolExecutor` needs `count_primes` picklable and importable
from `__main__` in a worker process. Only a real script file meets
that requirement, not a fenced block executed in place.

**Check that the answers agree.** The assertion compares the counts
alone, since the serial run carries the parent's process ID and the
parallel run carries the workers'. The counts stay the same,
`[17984, 33860, 49098, 63951]`. The same pure function gives the same
answers wherever it runs, which is the point of `parallel_pure.py`.

**Count the processes that answered.** The interesting number is the second
line. Three consecutive runs on one 32-core machine reported `4`
distinct process IDs each time.

Two things follow, and neither is the one most people predict. The
count is greater than one, so the work left the main process, and
`assert parallel == serial` alone could not show where the work ran.
But the count also sits far below thirty-two. `ProcessPoolExecutor`
allows one worker per core, but it starts workers on demand. A
submitted task starts a new worker only when no existing worker is
idle. Four tasks therefore start at most four processes, not
thirty-two.

The count can also fall below four. With limits twenty times smaller,
`[10_000, 20_000, 30_000, 40_000]`, the same machine reported `3` on
each of three runs. Starting a process then takes longer than a task
runs, so the first worker up finishes its task and takes the next one
from the queue before the last worker is ready. A distinct-ID count
shows that the work left the main process, not how many processes the
pool started.

The number depends on the core count, the task sizes, and scheduling,
so it is reproducible on your machine and nowhere else. That is why it does
not belong in a `#:` marker in the book.

</details>
</details>

## 2. Which thread ran each call

> Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous exercise and explain the IDs you see instead.

<details>
<summary>Where to look</summary>

In [Concurrency](../../Chapters/19_Techniques--Concurrency.md#one-executor-interface-three-pools), the pools share one `map()` interface.
Swap in `ThreadPoolExecutor`.
The serial comparison and the core count can go, and smaller limits keep the run short.
Think about what threads share that processes do not, and which function reports an identity per thread.

<details>
<summary>Solution</summary>

The listing swaps the executor and trims the previous exercise's
program. It drops the serial comparison and the core count, which the
question about IDs does not need, and it uses the twenty-times-smaller
limits from the end of that exercise, which keep the run short.

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
exercise, and it says nothing about thread parallelism.
`threading.get_ident()` is the equivalent for threads.
`ProcessPoolExecutor` and `ThreadPoolExecutor`
present the identical `map()` interface and differ this fundamentally
underneath. That contrast is the substitutable-backend point from
[Concurrency](../../Chapters/19_Techniques--Concurrency.md#one-executor-interface-three-pools).

</details>
</details>

## 3. Three property shapes for `sorted()`

> Write Hypothesis properties for `sorted()` using two shapes from [A Family of Property Shapes](../../Chapters/43_Functional--Confidence.md#a-family-of-property-shapes):
> an invariant (every adjacent pair of the output is in order) and idempotence
> (sorting a sorted list changes nothing).
> Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.

<details>
<summary>Where to look</summary>

[A Family of Property Shapes](../../Chapters/43_Functional--Confidence.md#a-family-of-property-shapes) names the invariant, idempotence, and oracle shapes.
Write each as its own `@given` test over `strategies.lists(strategies.integers())`.
For the oracle, write an insertion sort slow and simple enough to check by reading, and cap the list length.

<details>
<summary>Solution</summary>

If you write the oracle as `assert sorted(xs) == sorted(xs)`, the test
passes, and it keeps passing for a sort that drops the last element,
because both sides of `==` share the bug. The insertion-sort oracle
fails that broken sort on `xs=[0]`. The solution checks `sorted()`
against `insertion_sort()`, a separate implementation that cannot share
its bugs, because a property that restates the implementation tests
nothing.

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

**State a fact about every output.** The invariant is the weakest of the three, and the interesting part is
how weak. A function that ignores its argument and returns `[]` passes
`test_output_is_ordered()` on every input, and so does one that returns
the first element alone. "Ordered" says nothing about the elements
being the same ones you supplied.

**Check that repeating changes nothing.** Idempotence is weaker still
on its own. The same `[]`-returning function passes it too.
Idempotence adds a different kind of check, one about the operation
rather than the output. It catches a sort that drops the last element.
That sort's output is always ordered, so the invariant passes, but
running it on its own output drops another element, so twice and once
disagree on every list of two or more.

**Compare against an independent version.** The oracle closes the gap.
Because `insertion_sort()` is slow and simple enough to check by
reading, asserting that it agrees with `sorted()` pins down the
elements, their multiplicities, and their order at once. The oracle
earns its place because it repeats no part of `sorted()`'s
implementation. It arrives at the same answer by a different route.
That independence makes an oracle worth having, and makes
`assert sorted(xs) == sorted(xs)` worthless. Capping the list length
keeps the quadratic oracle cheap, since the bugs it catches show up on
short inputs.

</details>
</details>

## 4. A law that is false

> State a law that is false and watch Hypothesis falsify it:
> `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
> Report the counterexample Hypothesis finds after shrinking,
> run the test a few times,
> deleting the `.hypothesis/` directory before each run,
> to see which characters Hypothesis reports,
> and explain what those characters reveal about Unicode case mapping.

<details>
<summary>Where to look</summary>

[Shrinking a Failure](../../Chapters/43_Functional--Confidence.md#shrinking-a-failure) shows Hypothesis reducing a failing input to a minimal one.
Put `s.upper().lower() == s.lower()` under `@given(strategies.text())` and read the shrunk string.
Print its code points with `unicodedata.name()`, since the two sides of the failed assertion look alike.

<details>
<summary>Solution</summary>

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

Because the two sides print almost identically, the failure hides
until you look at the code points.

Runs split between `'µ'` and `'ß'`, since the shrinker does not
always find the smallest failing character. `ß` breaks the law for a
different reason, covered below.
Once a run fails, Hypothesis stores the counterexample in
`.hypothesis/` and replays it first, so later runs report the same
character until you delete that directory.

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

**Trace the round trip.** `µ` is U+00B5 MICRO SIGN, a character Latin-1 kept separate from the
Greek letter it resembles. `µ` is lowercase, so `.lower()`
returns it unchanged. But it has no uppercase form of its own, so
`.upper()` maps it to U+039C GREEK CAPITAL LETTER MU, and lowering
that gives U+03BC GREEK SMALL LETTER MU. The round trip ends in a
different Unicode block from the one where it started.

Unicode case mapping is not a pair of inverse functions. It is a
many-to-one mapping in each direction, over a repertoire containing
characters that are lowercase without being the lowercase of anything.
`ß` breaks the same law from the other side. `"ß".upper()` is `"SS"`,
two characters, so uppercasing can change a string's length. For
case-insensitive comparison Python provides `str.casefold()` rather
than `str.lower()`, and `casefold()` has no inverse either.

A hand-written loop over `"abcde"` does not reach `µ`. The generated
strings reach the parts of the repertoire nobody thinks to type, and
that reach is the argument for property testing in one example.

</details>
</details>

## 5. A property test for `group_rounds()`

> Write a property test for `group_rounds()` from [Toolkits](../../Chapters/41_Functional--Toolkits.md#groups-of-any-size):
> for any roster and any positive group size,
> every student appears in exactly one group per round.
> Use a strategy that generates rosters of distinct names.
> Then break `group_rounds()` on purpose, run the test twice,
> and confirm Hypothesis reports the same counterexample both times.
> Hypothesis records a failing case under `.hypothesis/` and replays it first on the next run.

<details>
<summary>Where to look</summary>

[The Same Law in Hypothesis](../../Chapters/43_Functional--Confidence.md#the-same-law-in-hypothesis) shows how `@given` turns a law into a test.
Build rosters with `strategies.lists(..., unique=True)`, and check that the sorted students in each round equal the sorted roster.
To break the function, remove the step that places leftover students, then rerun to see Hypothesis replay the failure from `.hypothesis/`.

<details>
<summary>Solution</summary>

If you compare `placed == names` without sorting either side,
the property fails against the correct `group_rounds()`,
and Hypothesis shrinks the failure to a two-name roster with
`size=1`, such as `names=['a', 'b']`.
`group_rounds()` shuffles the pool before it forms each round,
so the students come back in an order of their own.
The property concerns which students each round places, not their order, so the solution sorts both sides before comparing them.

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

    def met(group: list[str], candidate: str) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[str]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                stranger = min(pool,
                               key=lambda c: met(group, c))
                pool.remove(stranger)
                group.append(stranger)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        # Too few left for a full group of `size`
        for extra in pool:
            host = min(groups, key=lambda g: met(g, extra))
            host.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

rosters = strategies.lists(
    strategies.text("abcdefghij", min_size=1, max_size=3),
    min_size=2, max_size=12, unique=True)

@given(rosters,
       strategies.integers(min_value=1, max_value=5))
def test_every_student_appears_once_per_round(
        names: list[str], size: int) -> None:
    for grouping in islice(group_rounds(names, size), 3):
        placed = [*group for group in grouping]
        assert sorted(placed) == sorted(names)
```

**Handle a roster smaller than a group.** The two lines guarding an empty `groups` are the interesting part,
because the property test finds the need for them. Against the
version without them, Hypothesis reports a two-name roster with
`size=3`, such as `names=['a', 'b']`, and a
`ValueError: min() iterable argument is empty`. With fewer students
than the group size, the `while len(pool) >= size` loop runs zero times
and `groups` stays empty. The leftover loop then asks `min()` for the
smallest of nothing.

The crash is a real defect rather than an unstated precondition.
`group_rounds()` already keeps
everyone in a group when a roster divides unevenly, folding the
leftovers into existing groups, so the answer for a roster of two and
a size of five is one group of two. Crashing is the one answer
inconsistent with what the function does everywhere else. The
`group_rounds()` in [Toolkits](../../Chapters/41_Functional--Toolkits.md#groups-of-any-size) includes the guard, so
`test_group_rounds.py` passes with no `assume()`.

Finding the defect takes no cleverness and no thought about edge
cases. The strategy generates small rosters because Hypothesis
prefers small examples, so a size of `3` against a roster of `2`
comes up on its own. The property says what should be true for every
roster.

**State the precondition in the strategy.** The `unique=True` on the roster strategy does real work.
`group_rounds()` keys its history by `frozenset` of names, so two
students sharing a name are one student to the algorithm. The
property still passes on such a roster, because every name appears in
one group, but the schedule the property checks counts the two as one
student when `group_rounds()` avoids repeat meetings.
Generating distinct names states `group_rounds()`'s precondition where
the test can see it.

Breaking the function on purpose is the other half of the exercise.
Delete the loop that places leftovers:

```python
        # Too few left for a full group of `size`
        for extra in pool:
            host = min(groups, key=lambda g: met(g, extra))
            host.append(extra)
```

`group_rounds()` now drops the students who do not fill a whole
group, and the property reports the loss at once:

```text
E           AssertionError: assert [] == ['a', 'b']
E             Right contains 2 more items, first extra item: 'a'
E           Failing test case: test_every_student_appears_once_per_round(
E               names=['a', 'b'],
E               size=3,
E           )
```

Two students cannot fill a group of three, so the empty group the
guard adds collects nobody and the left side of the assertion is
`[]`. The report shows that shrunk case rather than whatever wide
random roster failed first.

The names vary from run to run. Hypothesis
shrinks a generated string toward a longer run of `a` before it
reaches a second letter, so `'aa'` arrives as readily as `'b'`. Now
and then a run stops at a different shape, three students in groups
of two, such as `names=['a', 'b', 'c'], size=2`, which leaves one
student over.

A second run reports the identical counterexample, and reports it
noticeably faster. Hypothesis writes each failing case into
`.hypothesis/examples/` and replays that database before generating
anything new, so it re-finds the failure you are in the middle of
fixing instead of leaving it to chance. The shrunk case therefore
behaves like a regression test you did not write. It keeps
failing until you fix the bug. The first run after the fix replays it
once more, sees it pass, and deletes it from the database.

</details>
</details>

## 6. Two impure functions with no `global` in sight

> Write two functions that are *not* referentially transparent without using `global`:
> one that reads `datetime.now()`, and one that reads an environment variable.
> For each, name the substitution that changes the program's behavior,
> then rewrite the function so the value arrives as an argument.

<details>
<summary>Where to look</summary>

[Referential Transparency](../../Chapters/43_Functional--Confidence.md#referential-transparency) tests a function by substituting a call with its value.
A function that reads the clock or `os.environ` takes an input its signature does not declare.
Move each hidden input into the parameter list, a `datetime` for the clock and a `Mapping` for the environment.

<details>
<summary>The shape</summary>

```python
# The shape of opaque_inputs.py
import os
from collections.abc import Mapping
from datetime import datetime, timedelta

def stale(created: datetime, limit: timedelta) -> bool:
    ...

def timeout() -> int:
    ...

def stale_pure(
    created: datetime, limit: timedelta, now: datetime
) -> bool:
    ...

def timeout_pure(env: Mapping[str, str]) -> int:
    ...
```

<details>
<summary>Solution</summary>

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
`global` is the loud way to break referential transparency. `stale()`
and `timeout()` are quiet ones. Both read state the caller cannot
see.

**Take the time without declaring it.** The substitution that breaks `stale()` is replacing a call with the
answer it just gave. `stale(made, timedelta(hours=12))` returns
`False` at 11:00 and `True` at 13:00, so writing down `False` and
substituting it changes the program the moment the clock passes noon.
Nothing in the signature warns you, because `datetime.now()` is an
argument the function takes without declaring.

**Take a setting without declaring it.** `timeout()` breaks the same
way across a boundary that is easier to miss, since the environment
usually holds still during a run. Substituting `30` for `timeout()` is
correct until someone sets `TIMEOUT`, and then the substituted version
and the original disagree while both still look right. Tests show the
problem first. One test that sets the variable changes the answer for
every test after it, and no argument list records the dependency.

**Make the hidden input a parameter.** The repair is the same for both, and it is the one this part of the
book keeps making. Move the hidden input into the parameter list.
`stale_pure()` takes the current time, and `timeout_pure()` takes the
mapping to read. Both are now referentially transparent, and both are
testable without a clock or a monkeypatched environment. The caller
that does read the real clock or the real `os.environ` becomes one
line at the edge of the program instead of a dependency buried in the
middle of it. [Testing](../../Chapters/11_Techniques--Testing.md#random-numbers)
makes the same move for a random source.

</details>
</details>
</details>

## 7. `match` against `isinstance()` on the same function

> Take the `describe()` function from [Error Handling](../../Chapters/42_Functional--Error_Handling.md#matching-on-the-error)
> and rewrite its `match` as `isinstance()` tests.
> Count the lines, then run `ty` on both versions and compare what it knows about the value inside the `Ok` in each.

<details>
<summary>Where to look</summary>

[Error Handling](../../Chapters/42_Functional--Error_Handling.md#matching-on-the-error) shows `describe()` using `match` on an `Ok` or `Err` result.
Rewrite each `case` as an `isinstance()` test on the result, then on its error.
Count lines in both versions, and compare the type `ty` reveals for the value inside `Ok` using `reveal_type()`.

<details>
<summary>The shape</summary>

```python
# The shape of describe_isinstance.py
from typing import final
from record import record

@final
@record
class Ok[A]:
    answer: A

@final
@record
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

def compute(text: str) -> Result[float, Exception]:
    ...

def describe(
    text: str, result: Result[float, Exception]
) -> str:
    ...
```

<details>
<summary>Solution</summary>

```python
# describe_isinstance.py
from typing import final
from record import record

@final
@record
class Ok[A]:
    answer: A

@final
@record
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

def compute(text: str) -> Result[float, Exception]:
    try:
        return Ok(1 / int(text))
    except (ValueError, ZeroDivisionError) as e:
        return Err(e)

def describe(
    text: str, result: Result[float, Exception]
) -> str:
    if isinstance(result, Ok):
        return f"{text}: {result.answer}"
    if isinstance(result.error, ValueError):
        return f"{text}: Not a number"
    if isinstance(result.error, ZeroDivisionError):
        return f"{text}: Cannot divide by zero"
    return f"{text}: {type(result.error).__name__}"  # [1]

for sample in ("4", "0", "OOPS"):
    print(describe(sample, compute(sample)))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

The two versions produce identical output. Counting lines favors the
`isinstance()` version by two. It needs no `match result:` line, and
its final `return` (`[1]`) replaces a `case` line and its body.

Length is not what separates the two versions. The `match` reads as
one description of four shapes while the `isinstance()` version reads
as four separate questions. The difference shows in what each version
repeats. `result.error` appears three times in `describe_isinstance.py`
and nowhere in the `match`, because each `case` matches on the error
instead of reading it back off `result`. The `return` at `[1]` is also
weaker than the `match`'s `case Err(error)`. It is a fallthrough that
happens to be correct rather than a branch stating what it matches, so
a reader must deduce that `result` is an `Err` by ruling out the `Ok`
branch above.

Inside the `Ok`, `ty` knows `float` either way. In the error
branches, the `isinstance()` version narrows `result.error` to
`ValueError` or `ZeroDivisionError`. The `match` patterns bind no
name there, so `result.error` stays `Exception`.

**Rule out a shared subclass.** The precision behind that agreement
rests on one decorator: both `Ok` and `Err` carry `@final`, in the
listing above and in `utils/result.py`. Without that decorator `ty`
0.0.84 allows for a class inheriting from both, so the intersection of
the two stays alive and the value in the `Ok` comes back as
`float | Unknown` rather than plain `float`. The `match` and the
`isinstance()` tests lose that precision together. `result.answer`
after a positive `isinstance()` and `answer` in `case Ok(answer)` read
`float | Unknown` alike. Pyright and mypy do not build that
intersection and report `float` with or without the decorator. The
measurement the exercise asks for therefore comes out even at either
precision, and what the decorator changes is a more useful finding
than either version winning.

The choice is about reading, not about proving. Neither form tells
the type checker anything the other cannot, so pick the one that
states the shapes you expect: the `match`.

</details>
</details>
</details>
