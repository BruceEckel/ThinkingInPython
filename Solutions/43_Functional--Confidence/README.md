# Confidence: Solutions

## 1. Which process ran each call

> Change `count_primes()` to return `(count, os.getpid())` and print how many distinct process IDs appear alongside the counts.
> Narrow `assert parallel == serial` to compare only the counts,
> since the serial run now carries the parent's ID and the parallel one carries the workers' IDs.
> Compare the number of distinct IDs to `os.process_cpu_count()`,
> and run `parallel_pure.py` three times before deciding what that number means.

<details>
<summary>Where to look</summary>

[Automatic Parallelism](../../Chapters/43_Functional--Confidence.md#automatic-parallelism)
runs a pure function through `ProcessPoolExecutor.map()`.
Have `count_primes()` return `os.getpid()` with the count,
and collect the IDs into a `set`.
Compare its size to `os.process_cpu_count()`,
and ask when the pool starts a worker.

<details>
<summary>Done when</summary>

`parallel_pure.py` runs to the end with your change and still prints the counts `[17984, 33860, 49098, 63951]`.
It also reports more than one distinct process ID,
and you can explain why that number stays well below `os.process_cpu_count()`.

<details>
<summary>Solution</summary>

If you keep `assert parallel == serial` from `parallel_pure.py`,
the script stops with a bare `AssertionError` before it prints a line.
Each pair now carries the ID of the process that computed it,
so every parallel result differs from its serial twin.
The solution compares the counts alone, the part a pure function guarantees.

```python
import os
from concurrent.futures import ProcessPoolExecutor

type Count = int
type ProcessId = int

def count_primes(limit: int) -> tuple[Count, ProcessId]:
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

**Keep the worker function importable.**
`ProcessPoolExecutor` pickles `count_primes()` by name,
and each worker finds it by importing the script,
so the listing must run as a script file.
A fenced block executed in place has no file for a worker to import.

**Check that the answers agree.**
The serial and parallel counts agree, `[17984, 33860, 49098, 63951]`.
The same pure function gives the same answers wherever it runs,
which is the point of `parallel_pure.py`.

**Count the processes that answered.**
Three consecutive runs on one 32-core machine reported `4` distinct process IDs each time.

The number is greater than one,
so some of the work ran outside the main process.
`assert parallel == serial` alone cannot show where the work ran.

The number is also far below thirty-two.
`ProcessPoolExecutor` allows one worker per core but starts workers on demand.
The pool hands a submitted task to an idle worker when one exists and starts a new worker otherwise.
For four tasks it therefore starts at most four processes, not thirty-two.

The number can also fall below four.
With limits twenty times smaller, `[10_000, 20_000, 30_000, 40_000]`,
the same machine reported `3` on each of three runs.
Starting a process then takes longer than a task runs,
so the first worker to start finishes its task and takes the next one from the queue before the last worker is ready.
A distinct-ID count shows that the work ran outside the main process,
not how many processes the pool started.

The number depends on the core count, the task sizes, and scheduling,
so it is reproducible on your machine and nowhere else.
Because of that dependence,
the count appears here in prose rather than in a `#:` marker.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. Which thread ran each call

> Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous exercise and explain the IDs you see instead.

<details>
<summary>Where to look</summary>

In [Concurrency](../../Chapters/19_Techniques--Concurrency.md#one-executor-interface-three-pools),
the pools share one `map()` interface.
Swap in `ThreadPoolExecutor`.
The serial comparison and the core count can go,
and smaller limits keep the run short.
Think about what threads share that processes do not,
and which function reports an identity per thread.

<details>
<summary>Done when</summary>

your `ThreadPoolExecutor` version prints the same counts as the process version for the same limits and reports one distinct process ID.
You can say why `os.getpid()` cannot tell the pool's workers apart.

<details>
<summary>Solution</summary>

The listing drops the serial comparison and the core count,
since the question concerns the IDs.
It also uses the twenty-times-smaller limits from the end of that exercise,
which keep the run short.

```python
import os
from concurrent.futures import ThreadPoolExecutor

type Count = int
type ProcessId = int

def count_primes(limit: int) -> tuple[Count, ProcessId]:
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

The thread pool reports `1`.
Threads share their process,
so `os.getpid()` returns the same value in every one of them.
Counting distinct process IDs reveals process parallelism,
as in the previous exercise, but reports a whole thread pool as one process.
For threads, the equivalent is `threading.get_ident()`.

`ProcessPoolExecutor` and `ThreadPoolExecutor` share [one `map()` interface](../../Chapters/19_Techniques--Concurrency.md#one-executor-interface-three-pools).
Underneath, `ProcessPoolExecutor` runs the calls in separate processes.
`ThreadPoolExecutor` runs them in threads of one process.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. Three property shapes for `sorted()`

> Write Hypothesis properties for `sorted()` using two shapes from [A Family of Property Shapes](../../Chapters/43_Functional--Confidence.md#a-family-of-property-shapes):
> an invariant (every adjacent pair of the output is in order) and idempotence
> (sorting a sorted list returns an equal list).
> Then add the oracle property that `sorted(xs)` agrees with a hand-written insertion sort on short lists.

<details>
<summary>Where to look</summary>

[A Family of Property Shapes](../../Chapters/43_Functional--Confidence.md#a-family-of-property-shapes)
describes the invariant, idempotence, and oracle shapes.
Write each as its own `@given` test over `strategies.lists(strategies.integers())`.
For the oracle, write an insertion sort slow and simple enough to check by reading,
and cap the list length.

<details>
<summary>Done when</summary>

your three properties pass under `uv run pytest`.
When you swap in a sort that returns `[]`,
the oracle fails while the invariant and idempotence pass;
a sort that drops the last element fails idempotence and the oracle and passes the invariant.

<details>
<summary>Solution</summary>

If you write the oracle as `assert sorted(xs) == sorted(xs)`, the test passes,
and it keeps passing for a sort that drops the last element,
because both sides of `==` share the bug.
A property that restates the implementation agrees with every bug in it.
The solution therefore checks `sorted()` against `insertion_sort()`,
a separate implementation that cannot share the bugs of `sorted()`.
The insertion-sort oracle fails the broken sort on `xs=[0]`.

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
    "Idempotence: sorting twice equals sorting once."
    once = sorted(xs)
    assert sorted(once) == once

@given(strategies.lists(strategies.integers(), max_size=8))
def test_agrees_with_insertion_sort(xs: list[int]) -> None:
    "Oracle: the fast version matches the simple one."
    assert sorted(xs) == insertion_sort(xs)
```

**State a fact about every output.**
The invariant is the weakest of the three.
A function that ignores its argument and returns `[]` passes `test_output_is_ordered()` on every input,
and so does one that returns the first element alone.
"Ordered" leaves open whether the elements are the same ones you supplied.

**Check that running twice matches running once.**
Idempotence on its own catches little more.
The same `[]`-returning function passes it too.
Idempotence adds a different kind of check,
one about the operation rather than the output.
It catches a sort that drops the last element.
That sort's output is always ordered, so the invariant passes.
But running the sort on its output drops another element,
so twice and once disagree on every list of two or more.

**Compare against an independent version.**
The oracle fails all three broken sorts: the one that returns `[]`,
the one that returns the first element, and the one that drops the last element.
`insertion_sort()` is slow and simple enough to check by reading,
so asserting that `sorted()` agrees with it checks the elements,
their multiplicities, and their order at once.

The oracle repeats no part of `sorted()`'s implementation.
It computes the same answer by a different algorithm.
That independence makes an oracle useful,
and its absence makes `assert sorted(xs) == sorted(xs)` worthless.

Capping the list length keeps the quadratic oracle fast,
since the bugs it catches appear in short inputs.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. A law that is false

> State a law that is false and watch Hypothesis falsify it:
> `@given(strategies.text())` with `assert s.upper().lower() == s.lower()`.
> Report the counterexample Hypothesis finds after shrinking.
> Run the test a few times,
> deleting the `.hypothesis/` directory before each run,
> to see which characters Hypothesis reports.
> Then explain what those characters reveal about Unicode case mapping.

<details>
<summary>Where to look</summary>

[Shrinking a Failure](../../Chapters/43_Functional--Confidence.md#shrinking-a-failure)
shows Hypothesis reducing a failing input to a minimal one.
Put `s.upper().lower() == s.lower()` under `@given(strategies.text())` and read the shrunk string.
Print each character's Unicode name with `unicodedata.name()`,
since the two sides of the failed assertion look alike.

<details>
<summary>Done when</summary>

Hypothesis shrinks the failure to a one-character `s`,
and printing the code points of both sides of the assertion shows they differ where they look alike.
With `.hypothesis/` deleted between runs you nearly always see one of two characters,
and your explanation covers both.

<details>
<summary>Solution</summary>

```python
from hypothesis import given, strategies

@given(strategies.text())
def test_upper_lower_agrees_with_lower(s: str) -> None:
    assert s.upper().lower() == s.lower()
```

Hypothesis falsifies it in well under a second and shrinks to a one-character string:

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

The two sides print almost identically,
so you need their code points to tell them apart.

Nearly all runs split between `'µ'` and `'ß'`,
since the shrinker sometimes stops at a failing character other than the smallest.
An occasional run stops at a rarer character, such as the ligature `'ﬀ'`,
whose uppercase is `"FF"`.
Once a run fails, Hypothesis stores the counterexample in `.hypothesis/` and replays it first,
so later runs report the same character until you delete that directory.

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

**Trace the round trip.**
`µ` is U+00B5 MICRO SIGN,
a character Latin-1 kept separate from the Greek letter it resembles.
It shares its uppercase form with that Greek letter,
so `.upper()` maps it to U+039C GREEK CAPITAL LETTER MU.
The round trip ends in a different Unicode block from the one where it started.

Unicode case mapping is not a pair of inverse functions.
It is a many-to-one mapping in each direction.
Some characters, like `µ`,
are lowercase without being the lowercase of anything.

`ß` breaks the same law by changing a string's length.
`"ß".upper()` is `"SS"`, two characters.
Lowering `"SS"` gives `"ss"`, which differs from `"ß"`.

For case-insensitive comparison Python provides `str.casefold()` rather than `str.lower()`.
`casefold()` maps `µ` to the Greek `μ` and `ß` to `"ss"`,
the results of their round trips,
so `s.upper().casefold() == s.casefold()` holds for both characters.
Like `upper()` and `lower()`, `casefold()` has no inverse.

A hand-written loop over `"abcde"` never tests `µ`.
The generated strings include characters nobody thinks to type.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. A property test for `group_rounds()`

> Write a property test for `group_rounds()` from [Functional Toolkits](../../Chapters/41_Functional--Toolkits.md#groups-of-any-size):
> for any roster and any positive group size,
> every student appears in exactly one group per round.
> Use a strategy that generates rosters of distinct names.
> Then break `group_rounds()` on purpose, run the test twice,
> and confirm Hypothesis reports the same counterexample both times.
> Hypothesis records a failing case under `.hypothesis/` and replays it first on the next run.

<details>
<summary>Where to look</summary>

[The Same Law in Hypothesis](../../Chapters/43_Functional--Confidence.md#the-same-law-in-hypothesis)
shows how `@given` turns a law into a test.
Build rosters with `strategies.lists(..., unique=True)`,
and check that the sorted students in each round equal the sorted roster.
To break the function, remove the step that places leftover students,
then rerun to see Hypothesis replay the failure from `.hypothesis/`.

<details>
<summary>Done when</summary>

your property passes under `uv run pytest` against the chapter's `group_rounds()`.
With the `for extra in pool` loop deleted it fails on a shrunk roster of two or three names,
and a second run, with `.hypothesis/` kept, reports the same `names` and `size`.

<details>
<summary>Solution</summary>

If you compare `placed == names` without sorting either side,
the property fails against the correct `group_rounds()`.
`group_rounds()` shuffles the pool before it forms each round,
so it returns the students in shuffled order.
Hypothesis shrinks the failure to a two-name roster with `size=1`,
such as `names=['a', 'b']`.
The property concerns which students each round places, not their order,
so the solution sorts both sides before comparing them.

```python
# test_group_rounds.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice
from hypothesis import given, strategies

type Student = str
type Group = tuple[Student, ...]
type Round = list[Group]

def group_rounds(
    students: list[Student], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[Student]] = Counter()
    rng = random.Random(seed)

    def met(
        group: list[Student], candidate: Student
    ) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[Student]] = []
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

**Handle a roster smaller than a group.**
The property test shows that `group_rounds()` needs the two lines guarding an empty `groups`.
Against the version without them,
Hypothesis reports a two-name roster with `size=3`, such as `names=['a', 'b']`,
and a `ValueError: min() iterable argument is empty`.
With fewer students than the group size,
the `while len(pool) >= size` loop runs zero times, so `groups` stays empty.
The leftover loop then calls `min()` on the empty `groups`,
and that call raises `ValueError`.

The crash is a real defect rather than an unstated precondition.
`group_rounds()` keeps everyone in a group when a roster divides unevenly,
folding the leftovers into existing groups.
By that rule, the answer for a roster of two and a size of five is one group of two.
Crashing contradicts what the function does everywhere else.
The `group_rounds()` in [Functional Toolkits](../../Chapters/41_Functional--Toolkits.md#groups-of-any-size)
includes the guard, so `test_group_rounds.py` passes with no `assume()`.

Finding the defect is a mechanical search.
Hypothesis prefers small examples,
so it soon generates a roster of `2` against a size of `3`.
The property states what holds for every roster.
Hypothesis finds the roster that breaks it.

**State the precondition in the strategy.**
The `unique=True` on the roster strategy does real work.
The property passes on a roster with a repeated name,
because every student still appears in one group.
But `group_rounds()` keys its history by `frozenset` of names,
so it records the meetings of two students who share a name under the same keys.
When it avoids repeat meetings, it treats the two students as one.
Generating distinct names writes `group_rounds()`'s precondition into the test.

Breaking the function on purpose is the other half of the exercise.
Delete the loop that places leftovers:

```python
        # Too few left for a full group of `size`
        for extra in pool:
            host = min(groups, key=lambda g: met(g, extra))
            host.append(extra)
```

`group_rounds()` now drops the leftover students,
and the property reports the loss at once:

```text
E           AssertionError: assert [] == ['a', 'b']
E             Right contains 2 more items, first extra item: 'a'
E           Failing test case: test_every_student_appears_once_per_round(
E               names=['a', 'b'],
E               size=3,
E           )
```

Because two students cannot fill a group of three,
the guard adds an empty group.
With the leftover loop deleted, that group stays empty,
so the left side of the assertion is `[]`.

The report shows the shrunk case rather than the wide random roster that failed first.
When each run starts with an empty `.hypothesis/` directory,
the reported names vary from run to run.
Hypothesis shrinks a generated string toward a longer run of `a` before it tries a second letter,
so the report shows `'aa'` as often as `'b'`.
Now and then a run stops at a different shape: three students in groups of two,
such as `names=['a', 'b', 'c'], size=2`, which leaves one student over.

A second run reports the identical counterexample,
and reports it noticeably faster.
Hypothesis writes each failing case into `.hypothesis/examples/` and replays that database before generating anything new.
It therefore re-finds the failure you are in the middle of fixing instead of leaving it to chance.
That replay makes the shrunk case behave like a regression test that Hypothesis wrote for you.
The case keeps failing until you fix the bug.
The first run after the fix replays the case once more, finds that it passes,
and deletes it from the database.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 6. Two impure functions with no `global` in sight

> Without using `global`,
> write two functions that break referential transparency:
> one that reads `datetime.now()`, and one that reads an environment variable.
> For each, name the substitution that changes the program's behavior,
> then rewrite the function so the value arrives as an argument.

<details>
<summary>Where to look</summary>

[Referential Transparency](../../Chapters/43_Functional--Confidence.md#referential-transparency)
tests a function by substituting a call with its value.
A function that reads the clock or `os.environ` takes an input hidden from its signature.
Move each hidden input into the parameter list,
a `datetime` for the clock and a `Mapping` for the environment.

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
<summary>Done when</summary>

each rewritten function names every input it reads in its signature,
so the same arguments give the same answer at any time of day and with any `TIMEOUT` set.
For each original, you can name a call whose recorded answer goes wrong when substituted later.

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

Neither impure function assigns to anything.
`global` breaks referential transparency with a declaration a reader can find.
`stale()` and `timeout()` break it silently,
by reading state hidden from the caller.

**Take the time without declaring it.**
The substitution that breaks `stale()` is replacing a call with the answer it just gave.
`made` is midnight on 1 January 2020,
and on that day `stale(made, timedelta(hours=12))` returns `False` at 11:00 and `True` at 13:00,
so writing down `False` and substituting it changes the program the moment the clock passes noon.

**Take a setting without declaring it.**
`timeout()` breaks the same way.
The break is easier to miss,
since the environment usually stays the same for a whole run.
Substituting `30` for `timeout()` is correct until someone sets `TIMEOUT`,
and then the substituted version and the original disagree while both still look right.
Tests show the problem first.
One test that sets the variable changes the answer for every test after it.
The signature `timeout() -> int` hides the dependency.

**Make the hidden input a parameter.**
The repair is the same for `stale()` and `timeout()`,
and it is the one [Effects by Hand](../../Chapters/44_Effects--Effect_Management.md#effects-by-hand)
describes: pass the implementation in as a parameter.
`stale_pure()` and `timeout_pure()` are now referentially transparent,
and both are testable without a clock or a monkeypatched environment.
The read of the real clock or the real `os.environ` moves out of the middle of the program into one line at its edge,
in the caller.
[Testing](../../Chapters/11_Techniques--Testing.md#random-numbers)
makes the same move for a random source.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. `match` against `isinstance()` on the same function

> Take the `describe()` function from [Error Handling](../../Chapters/42_Functional--Error_Handling.md#matching-on-the-error)
> and rewrite its `match` as `isinstance()` tests.
> Count the lines, then run `ty` on both versions and compare the type it infers for the value inside the `Ok` in each.

<details>
<summary>Where to look</summary>

[Error Handling](../../Chapters/42_Functional--Error_Handling.md#matching-on-the-error)
shows `describe()` using `match` on an `Ok` or `Err` result.
Rewrite each `case` as an `isinstance()` test on the result, then on its error.
Count lines in both versions,
and compare the type `ty` reveals for the value inside `Ok` using `reveal_type()`.

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

def describe(result: Result[float, Exception]) -> str:
    ...
```

<details>
<summary>Done when</summary>

your `isinstance()` version prints the chapter's three `#:` lines,
its `describe()` is two lines shorter than the `match` version,
and `reveal_type()` on the value inside the `Ok` shows `float` in both versions under `uv run ty check`.

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

def describe(result: Result[float, Exception]) -> str:
    if isinstance(result, Ok):
        return str(result.answer)
    if isinstance(result.error, ValueError):
        return "Not a number"
    if isinstance(result.error, ZeroDivisionError):
        return "Cannot divide by zero"
    return type(result.error).__name__  # [1]

for sample in ("4", "0", "OOPS"):
    print(f"{sample}: {describe(compute(sample))}")
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

The two versions produce identical output.
Counting lines favors the `isinstance()` version by two.
The `isinstance()` version drops the `match result:` line,
and its final `return` (`[1]`) replaces a `case` line and its body.

Reading, not length, separates the two versions.
The `match` reads as one description of four shapes while the `isinstance()` version reads as three separate questions and a fallthrough.
The difference shows in what each version repeats.
`result.error` appears three times in `describe_isinstance.py` and nowhere in the `match`,
because each `case` pattern destructures the `Err` and matches the error inside it.

The `return` at `[1]` is also weaker than the `match`'s `case Err(error)`.
That `return` is a fallthrough rather than a branch stating what it matches,
so a reader must deduce that `result` is an `Err` by ruling out the `Ok` branch above.

In the error branches,
the `isinstance()` version narrows `result.error` to `ValueError` or `ZeroDivisionError`.
The `match` patterns bind no name there, so `result.error` stays `Exception`.
Inside the `Ok`, the type checker knows `float` either way.

**Rule out a shared subclass.**
The precision behind that agreement depends on one decorator:
both `Ok` and `Err` carry `@final`,
in `describe_isinstance.py` and in `utils/result.py`.
Without that decorator `ty` 0.0.91 allows for a class inheriting from both,
so it keeps the intersection of the two as a possible type.
The value in the `Ok` then comes back as `float | Unknown` rather than plain `float`.
Pyright and mypy do not build that intersection and report `float` with or without the decorator.

Under `ty`, the `match` and the `isinstance()` tests lose that precision together.
`result.answer` after a positive `isinstance()` and `answer` in `case Ok(answer)` read `float | Unknown` alike.
The exercise's comparison therefore comes out even at either precision.
The decorator's effect is a more useful finding than a win for either version.

The choice is about reading, not about proving.
Either form can tell the type checker what the other does:
a `case Err(ValueError() as error)` narrows the error as the `isinstance()` test does.
So pick the one that states the shapes you expect: the `match`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
