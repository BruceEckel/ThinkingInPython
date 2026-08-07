# Assurance: Solutions

## 1. A fifth limit added to the parallel prime count

```python
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit):
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count

def main():
    limits = [10_000, 20_000, 30_000, 40_000, 50_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    assert parallel == serial
    print(parallel)

if __name__ == "__main__":
    main()
```

`ProcessPoolExecutor` needs `count_primes` picklable and importable
from `__main__` in a worker process, which only holds for a real
script file, not a fenced block executed in place; run as a script,
this prints `[1229, 2262, 3245, 4203, 5133]`. The `assert` still passes
with a fifth limit added, for the same reason it passed with four:
`count_primes()` is pure, so calling it with `50_000` returns the
identical result whether the call runs in the main process (as part
of `serial`) or in a worker process (as part
of `parallel`). Growing the input list needed no change to
`count_primes()` itself, no new locks, and no new coordination code,
because purity was the only thing making the original four calls safe
to parallelize, and that property does not weaken as more calls are
added.

## 2. Three property shapes for `sorted()`

```python
# test_sorted_laws.py
from hypothesis import given, strategies

def insertion_sort(xs: list[int]) -> list[int]:
    "The obviously correct version, for the oracle property."
    result: list[int] = []
    for x in xs:
        position = 0
        while position < len(result) and result[position] <= x:
            position += 1
        result.insert(position, x)
    return result

numbers = strategies.lists(strategies.integers())

@given(numbers)
def test_output_is_ordered(xs: list[int]) -> None:
    "Invariant: every adjacent pair of the output is ordered."
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
function passes it too. What idempotence buys is a different kind of
check, one about the operation rather than the output, so it catches a
sort that shuffles equal elements on the second pass while the ordering
invariant sees nothing wrong.

The oracle closes the gap. `insertion_sort()` is slow and obviously
correct, so asserting the two agree pins down the elements, their
multiplicities, and their order at once. It is worth writing precisely
because it repeats no part of `sorted()`'s implementation: it arrives
at the same answer by a different route, which is the property that
makes an oracle worth having and makes
`assert sorted(xs) == sorted(xs)` worthless. Capping the list length
keeps the quadratic oracle cheap, since the bugs it would catch do not
need long inputs to show up.

## 3. A law that is false

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

The two sides print almost identically, which is the first lesson: the
failure is invisible until you look at the code points.

```python
# test_case_mapping.py
import unicodedata

MICRO = "µ"

def test_upper_leaves_the_micro_sign_in_the_greek_block() -> None:
    assert unicodedata.name(MICRO) == "MICRO SIGN"
    assert (unicodedata.name(MICRO.upper())
            == "GREEK CAPITAL LETTER MU")
    assert (unicodedata.name(MICRO.upper().lower())
            == "GREEK SMALL LETTER MU")
    assert MICRO.lower() == MICRO  # Already lowercase, so unchanged
    assert MICRO.upper().lower() != MICRO.lower()
```

`µ` is U+00B5 MICRO SIGN, a character Latin-1 kept separate from the
Greek letter it looks like. It is already lowercase, so `.lower()`
returns it unchanged. But it has no uppercase form of its own, so
`.upper()` maps it to U+039C GREEK CAPITAL LETTER MU, and lowering
that gives U+03BC GREEK SMALL LETTER MU. The round trip lands one
block away from where it started.

What this reveals is that Unicode case mapping is not a pair of
inverse functions. It is a many-to-one mapping in each direction, over
a repertoire containing characters that are lowercase without being
the lowercase of anything. `ß` breaks the same law from the other
side: `"ß".upper()` is `"SS"`, two characters, so uppercasing does not
even preserve length. The rule that survives is that `str.casefold()`,
not `str.lower()`, is the operation intended for case-insensitive
comparison, and even it makes no promise of reversibility.

A hand-written loop over `"abcde"` would never have found this. The
generated strings reach the parts of the repertoire nobody thinks to
type, which is the argument for property testing in one example.

## 4. A property test for `group_rounds()`

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
                    history[frozenset((m, c))] for m in group))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        if pool and not groups:  # Roster smaller than one group
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

@given(rosters, strategies.integers(min_value=2, max_value=5))
def test_every_student_appears_once_per_round(
        names: list[str], size: int) -> None:
    for grouping in islice(group_rounds(names, size), 3):
        placed = [n for group in grouping for n in group]
        assert sorted(placed) == sorted(names)
```

The `unique=True` on the roster strategy is doing real work.
`group_rounds()` keys its history by `frozenset` of names, so two
students sharing a name are one student to the algorithm, and the
property would fail for a reason that says nothing about the code.
Generating distinct names states that precondition where the test can
see it.

The two lines guarding an empty `groups` are the interesting part,
because the property test is what found the need for them. Run against
the version without them, Hypothesis reports `names=['a', 'aa'],
size=3` and a `ValueError: min() iterable argument is empty`: with
fewer students than the group size, the `while len(pool) >= size` loop
never runs, `groups` stays empty, and the leftover loop then asks
`min()` for the smallest of nothing.

That is a real defect rather than an unstated precondition, and the
distinction is worth drawing. `group_rounds()` already declines to
leave anyone out when a roster divides unevenly, folding the leftovers
into existing groups, so the answer for a roster of two and a size of
five is one group of two. Crashing is the one answer inconsistent with
what the function does everywhere else. The fix is in the chapter now,
which is why the test above needs no `assume()` to pass.

Finding it took no cleverness and no thought about edge cases. The
strategy generates small rosters because Hypothesis prefers small
examples, a size of `3` against a roster of `2` came up on its own, and
the property said what should have been true for every roster.

Breaking the function on purpose is the other half of the exercise.
Delete the three lines that place leftovers:

```python
        for extra in pool:
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
```

Students who do not fit a full group are now dropped from the round,
and the property catches it at once:

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
alphabet allows, so this is the shrunk case rather than whatever wide
random roster failed first.

Running it a second time reports the identical counterexample, and
noticeably faster. Hypothesis writes each failing case into
`.hypothesis/examples/` and replays that database before generating
anything new, so a failure you are in the middle of fixing does not
have to be rediscovered by chance on each run. The practical effect is
that the shrunk case behaves like a regression test you never had to
write: it keeps failing until the bug is fixed, then rejoins the pool
of examples and is tried again on every later run.
