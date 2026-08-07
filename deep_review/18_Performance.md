When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

**Build note before anything else.** The applied edits touch the
` ```python ` block marked `# rust/fastcount/demo.py` (wrapping two lines that
were 71 and 75 characters). No root target regenerates `rust/`, so after
taking the new chapter run:

```
cd rust && make sync     # or: uv run python tools/extract_rust.py --write
```

`tools/extract_rust.py` (check mode) currently reports
`~ rust/fastcount/demo.py` until you do. `make sync`/`make verify` will not
catch this, because the root `Makefile` never enters `rust/`.

---

## Applied in this pass (listed for the record, no action needed)

- **`sys.monitoring` section, "everything reached from monitored code is
  monitored too."** This is wrong: `set_local_events()` arms exactly one code
  object and does not propagate to anything that object calls. Verified on
  3.15.0b2 — a monitored `outer()` that calls an unarmed `inner()` yields
  `Counter({'outer': 1})`, with `inner` absent. As written it teaches a reader
  that `square()` is uncounted only because `fib()` never calls it, which is
  the opposite of the lesson. Replaced with a plain statement that attachment
  does not spread, and that `set_events()` is the global form.
- **"Write Idiomatic Python", "the more of your loop you hand to the
  interpreter."** Handing work to the interpreter is the slow path; the
  sentence means handing it to C, which the previous line just said. Changed
  to "hand to C".
- **`timeit` section:** added that omitting `number` defaults to a million
  calls (`timeit.default_number == 1_000_000`). Every listing in the chapter
  passes `number=`, and a reader who copies the idiom without it onto a
  10 ms function waits nearly three hours.
- **Bisect section:** added the `bisect_left`/`bisect_right` contrast (see the
  standalone finding below for why this was treated as confident).
- **Lazy Evaluation:** added one sentence naming `evens[:5]` as the thing
  `islice()` replaces, and the `TypeError` a reader gets for slicing a
  generator.
- **`rust/fastcount/demo.py` block:** wrapped the two over-70 lines to match
  the wrapped `timeit.timeit(...)` calls already used in the Numba listings.

---

[] Reject

**Section: "Try a Faster Platform" — CPython's own JIT is never mentioned,
and the chapter later primes the reader to ask about it.**

This section is the chapter's only discussion of "a newer CPython," and it
covers point-release speedups, PyPy, and hardware. It never mentions that
CPython has shipped an experimental copy-and-patch JIT since 3.13 (PEP 744).
Forty sections later the chapter has a heading called
"JIT Compilation with Numba," at which point a 2026 reader is almost certain
to think "doesn't CPython have one of those?" and get no answer. Chapter 19
does not cover it either (it covers free threading), so the question is
unanswered book-wide.

The build in this workspace confirms the state: `sys._jit.is_available()` is
`True` and `sys._jit.is_enabled()` is `False`, i.e. built in and off unless
you set `PYTHON_JIT=1`.

Proposed addition after the "cheapest platform change is a newer CPython"
paragraph, two or three sentences:

> CPython itself has an experimental just-in-time compiler, built into the
> official 3.13 and later binaries but switched off. Setting `PYTHON_JIT=1`
> turns it on, currently for a single-digit percentage gain, so it is worth a
> measurement and not worth a plan. Whether it stays is still being settled
> ([PEP 836](https://peps.python.org/pep-0836/)).

**Caveat you should weigh before applying this.** The JIT's status is
genuinely unsettled as of mid-2026: the steering council required a
standards-track PEP within roughly six months or the code leaves `main`, and
PEP 836 (Draft) proposes a multi-year conditional path with a 20% speedup on
free-threaded builds as the year-two survival threshold. Any text here may go
stale within one release. The alternative, which I would also accept, is a
single sentence with no numbers: "CPython also has an experimental JIT, off by
default and still provisional; see PEP 836." A third option is to say nothing
and instead retitle "JIT Compilation with Numba" so it does not invite the
question — but that hides a real thing a reader can try today.

[] Reject

**Section: "Profilers" — "The standard library includes two profilers" leaves
the second one unnamed for thirty lines.**

The sentence promises two, then the next four sentences describe only
`cProfile`. The second is not named until the 3.15 paragraph, and it arrives
worded as a *third* arrival ("Python 3.15 **also adds** a new *sampling*
profiler"). On a first read the reader spends the whole `cProfile` paragraph
holding an unresolved count.

Proposed rewrite of line 54:

> The standard library includes two: a deterministic tracing profiler, and,
> new in Python 3.15, a sampling profiler.

and then, in the 3.15 paragraph, change "Python 3.15 also adds a new
*sampling* profiler named `profiling.sampling`" to "The sampling profiler is
`profiling.sampling`."

Two related facts you may or may not want:

- The pure-Python `profile` module is the historical "second profiler," and
  3.15 starts deprecating it. Verified here: `import profile` raises
  `DeprecationWarning: The profile module is deprecated and will be removed in
  Python 3.17. Use profiling.tracing (or cProfile) for tracing profilers
  instead.` One clause would keep a reader from reaching for it.
- `python -m profiling.sampling` also has `dump <pid>` (one stack snapshot of
  a live process) and a `--live` flag on both `run` and `attach` (an
  interactive top-style view). `--live` in particular is the thing a reader
  would actually use, and it costs half a line to name.

[] Reject

**Section: "Profilers" — the `ncalls` advice does not match the sample table
it sits under.**

"one call burning six milliseconds needs a better algorithm, ten thousand
calls burning a microsecond each need fewer calls."

The first half maps cleanly onto the `prof_demo.py:1(slow)` row (1 call,
`tottime` 0.006). The second half maps onto nothing: the only high-`ncalls`
row is `<genexpr>` at 10001 calls with `tottime` 0.000. A reader who tries to
find the second pattern in the table concludes they have misread the columns.

(I reproduced the table with a real `prof_demo.py` and it is otherwise
accurate down to the line numbers and the 10001 genexpr count — the
resumption-plus-`StopIteration` detail is a nice one. This is only the prose.)

Recommended fix: make the second half explicitly hypothetical rather than
sounding like a reading of the table, e.g. "…and a row with ten thousand calls
and a large `tottime` needs fewer calls, not a faster body." Alternative: swap
the sample program for one whose second hot spot really is call-count-bound,
so both halves are readable off the table. I prefer the prose fix; the table
is doing enough work already.

[] Reject

**Section: "Write Idiomatic Python", `hoist_attribute_lookup.py` — the prose
understates the result, and the mechanism given is not the real one.**

Current text: "Modern CPython already caches a repeated attribute lookup like
`out.append` inside a loop, so it costs little more than the local variable."

Measured here on 3.15.0b2, six independent `min(repeat(..., repeat=5))`
rounds:

```
attr=0.3447 hoisted=0.4100  attr/hoisted=0.841
attr=0.3368 hoisted=0.4103  attr/hoisted=0.821
attr=0.3337 hoisted=0.4043  attr/hoisted=0.825
attr=0.3305 hoisted=0.3982  attr/hoisted=0.830
attr=0.3261 hoisted=0.3969  attr/hoisted=0.822
attr=0.3365 hoisted=0.4056  attr/hoisted=0.830
```

The hoisted version is consistently ~20% **slower**, not "little more." The
spread is under 3%, so this is not the machine's mood; it is also not noise on
2 shared CPUs, since the direction never flipped in 6 rounds plus 8 runs of
the listing itself (all `True`).

The mechanism is not caching. `dis` on the loop shows
`LOAD_ATTR 3 (append + NULL|self)`: the compiler emits the method-load form,
which pushes the function and `self` separately and never materializes a bound
method. `append = out.append` does materialize one, and every call then goes
through that extra object. So hoisting trades a specialized load for a
bound-method call, which is why it loses.

I did **not** edit this, because the sentence may well be true on your Windows
machine and because the fix changes what the section teaches. Proposed
replacement:

> Here the hoist does not just fail to pay off, it costs. `out.append(i)`
> compiles to a method load that pushes the function and its `self` separately,
> with no bound method built; `append = out.append` builds one and every call
> goes through it. Measure it on your own machine before believing either
> direction.

Please run the listing on your machine before applying. If it comes out the
other way there, the honest wording is "the two are within noise of each
other," and the threshold boolean is right either way.

Note that this makes the section *stronger*, not weaker: the surrounding prose
already says the listing exists "because it catches a 'classic' optimization
that no longer works," and a classic optimization that has become a
pessimization is a better version of that point.

[] Reject

**Section: "Bisect", `bisect_search.py` — `grade()` rebuilds its lookup tables
on every call, in the performance chapter.**

```python
def grade(score: int) -> str:
    # Map a score to a letter through its cutoff boundaries:
    cutoffs = [60, 70, 80, 90]
    letters = "FDCBA"
    return letters[bisect.bisect(cutoffs, score)]
```

`cutoffs` and `letters` are constants rebuilt on each call. `thinking-in-python-skill.md`
says module-level lookup tables that act as constants are `UPPER_CASE` with
`Final[...]`, and this is the one chapter where allocating a list per call
inside a demonstration reads as an oversight rather than a simplification.

Proposed:

```python
CUTOFFS: Final[list[int]] = [60, 70, 80, 90]
LETTERS: Final[str] = "FDCBA"

def grade(score: int) -> str:
    return LETTERS[bisect.bisect(CUTOFFS, score)]
```

with `from typing import Final` added to the imports. The alternative is to
leave it and add nothing — the function is a throwaway illustration — but
then it is the only listing in the chapter that spends allocations it does not
need.

Second, smaller point about the same listing: `grade()` is teaching a
different idea (bucketing a value into labelled ranges) from the two lines
above it (find an insertion point, insert while staying sorted). That is two
new things in one listing. If you want them separate, the cleanest split is to
keep `bisect`/`insort` in `bisect_search.py` and move `grade()` into its own
short listing directly after, with one sentence saying that the same
insertion-point answer is also a bucket index. I would not do this unless the
`Final` change above lands anyway.

[] Reject

**Section: "Bisect" — the `bisect_left`/`bisect_right` contrast (already
applied; flagged here so you can reject it as a unit).**

Unlike every other block in this file, this change is already in the chapter.
Marking it `[X] Reject` means deleting the added paragraph, not declining to
add it.

I treated this one as confident and applied it, because the chapter uses both
halves of the pair and the difference is load-bearing:

- `bisect_search.py` calls `bisect.bisect(scores, 78)`.
- `search_comparison.py` calls `bisect.bisect_left(as_list, target)` and then
  checks `as_list[i] == target`.

The second one is only correct with `bisect_left`. Verified:
`bisect_left([0..9], 5)` is 5 and `xs[5] == 5`; `bisect_right([0..9], 5)` is 6
and `xs[6] == 5` is `False`. So a reader who reads the first listing, learns
`bisect`, and then writes the membership test from the second listing gets a
function that returns `False` for every value that is present. Nothing in the
chapter warned them.

Added after the O(log n) sentence:

> `bisect()` is an alias for `bisect_right()`, which returns the position after
> any elements equal to the target, while `bisect_left()` returns the position
> before them (`insort()` is likewise an alias for `insort_right()`). Either
> one answers "where does this go," but only `bisect_left()` lands on an
> existing value, so a membership test must use it, as `search_comparison.py`
> does below.

Verified: `bisect.bisect is bisect.bisect_right` and
`bisect.insort is bisect.insort_right` are both `True` on 3.15.

[] Reject

**Section: "Heap", `heap_queue.py` — the comment above `nsmallest()` is
ambiguous, and the listing carries three lessons.**

The comment is `# Doesn't make a heap from the list:`. Two readings are
available: "this call does not heapify the argument" (what is meant) and
"this does not return a heap" (also true, also not the point). Since the very
next demo in the chapter is `heap_corruption.py`, whose whole subject is what
does and does not preserve heap ordering, the ambiguity lands at the worst
moment.

Suggested: `# Does not reorder the argument` — which is also what the
`heap_corruption.py` listing's own later comment,
`# Not reordered by nsmallest()`, already says, so the two would agree.

Separately, this listing teaches min-heap operations, `nsmallest`/`nlargest`,
and the whole 3.14 max-heap family in one 36-line block. It is the largest
listing in the chapter by some margin. If you want it split, the natural cut
is at `max_nums = [5, 1, 8, 3, 2]`: min-heap plus top-N in one listing, the
max-heap mirror in a second, with the "Through Python 3.13, `heapq` only built
a min-heap" paragraph moving down to sit above the second. That is a pacing
call, so it stays a proposal.

[] Reject

**Section: "Slots" — "speeds attribute access" is the chapter's only
unmeasured performance claim, and it barely holds on 3.15.**

"Declaring `__slots__` replaces that dict with a fixed set of fields, which
shrinks each instance and speeds attribute access."

The shrinking half is measured two listings later and holds decisively (344
bytes against 48). The speed half is asserted and never measured, which is
conspicuous in a chapter that measures everything, and it is the same species
of stale truism the `hoist_attribute_lookup.py` listing exists to debunk.

Measured here, `o.x + o.y + o.z` in a 1000-iteration loop, min-of-5, three
rounds:

```
dict 0.0098  slots 0.0093  ratio 1.053
dict 0.0097  slots 0.0094  ratio 1.037
dict 0.0096  slots 0.0093  ratio 1.028
```

3 to 5%. A simpler two-attribute read came out at 2%. CPython's specializing
interpreter reaches an instance-dict attribute through
`LOAD_ATTR_INSTANCE_VALUE` on a key-sharing dict, which is nearly as fast as
the slot descriptor. By the chapter's own standard, stated forty lines
earlier — "Timing noise on a busy machine easily reaches ten or twenty
percent, so a claim about a small difference measures the machine's mood" —
this claim is under the chapter's own noise floor.

Recommended: cut "and speeds attribute access" and let the memory argument
carry the section, which is what the listings actually demonstrate. If you
would rather keep it, the honest form is "and makes attribute access slightly
faster, though on current CPython the difference is small enough that memory
is the real reason to use it." I prefer the cut; the section is titled
"Reduce Memory Overhead" and the speed aside is the only thing in it that is
not about memory.

[] Reject

**Section: "Slots", `slots_dataclass.py` — two different exception idioms for
the same demonstration, inside one listing.**

```python
try:
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
...
fp = FrozenPoint(1, 2)
with ignore(AttributeError):
    # Frozen prevents new attributes, not just reassignment:
    fp.z = 3  # type: ignore
#: FrozenInstanceError("cannot assign to field 'z'")
```

Both blocks demonstrate "assigning an undeclared attribute fails," ten lines
apart, using different machinery. A reader will look for a reason and not find
one stated.

There *is* a reason, and it is a good one: the slotted case's message varies
(`"'Point' object has no attribute 'z' and no __dict__ for setting new
attributes"` here), so only the type name is safe to assert, while the frozen
case's message is stable and worth showing. That reasoning is invisible.

Recommended: one sentence in the prose after the listing, e.g. "The first
block prints only the exception's type because the slotted message varies
between builds; the frozen message is stable, so `ignore()` shows it whole."

While you are there, a second unremarked fact in the same three lines:
`ignore(AttributeError)` catches a `FrozenInstanceError` because
`FrozenInstanceError` subclasses `AttributeError` (verified: its MRO is
`FrozenInstanceError -> AttributeError -> Exception -> BaseException ->
object`). The output shows a `FrozenInstanceError` arriving from a filter
written for `AttributeError`, which looks like a bug until you know that. Half
a sentence fixes it: "`FrozenInstanceError` is an `AttributeError` subclass,
which is why the filter catches it."

[] Reject

**Section: "Memory View" — the one subsection of "Reduce Memory Overhead"
that never demonstrates the overhead it reduces.**

Slots gets `slots at least 5x smaller: True`. Array gets
`array at least 3x smaller: True`. Memory View gets a six-byte `bytearray`,
one three-byte slice, and no comparison at all. The section's claim — "Slicing
a large `bytes` or `bytearray` through a view avoids duplicating the data" —
has the word "large" doing all the work, and the listing is deliberately tiny.

Worse, the one line that would show the saving does the opposite:

```python
chunk = view[1:4]
print(bytes(chunk))
```

`bytes(chunk)` copies. A reader watching for "no copy" sees a copy on the very
next line, with nothing saying the copy is only for display.

Proposed: add a size comparison in the same shape as its two sibling sections,
so all three subsections argue the same way:

```python
big = bytearray(1_000_000)
copied = big[:500_000]
viewed = memoryview(big)[:500_000]
print(f"view under 1% of copy: "
      f"{sys.getsizeof(viewed) * 100 < sys.getsizeof(copied)}")
#: view under 1% of copy: True
```

Verified on this build: the copy is 500,097 bytes, the view object is 184, and
`viewed.nbytes` is 500,000 — so the view addresses half a megabyte while
occupying 184 bytes, and the 1% threshold clears by three orders of magnitude.
The listing would need `import sys` added, which it does not currently have.

Whether that goes in the existing listing or a second one is a pacing call, so
this stays a proposal. If you would rather not add code, the minimum fix is
one clause on the `bytes(chunk)` line's prose: "`bytes(chunk)` copies, but only
to print it; the view itself never did."

[] Reject

**Section: "Converting a Slow Function to Rust" — the boundary-cost paragraph
argues against itself in three lines.**

> Shipping millions of small Python objects across the boundary loses it too.
> Numbers, strings, bytes, and NumPy arrays cross cheaply, and so does the
> plain list of integers `collatz_lengths()` takes and returns here.

A `list` of 50,000 Python ints converted to `Vec<u64>` and back **is**
shipping many small Python objects across the boundary. The two sentences
land on opposite sides of the same fact, and the second reads as an exemption
granted to the book's own example.

The real reason the example still wins is not that the list is cheap in
absolute terms; it is that the per-element conversion is a handful of
nanoseconds against a Collatz chain averaging a hundred-plus iterations, so
the compute swamps the marshalling. That ratio is the actual rule, and it is
more useful than a list of blessed types.

Proposed replacement for the last sentence:

> The list of integers `collatz_lengths()` takes and returns crosses 50,000
> times, which sounds like exactly the thing to avoid — but each crossing
> buys a hundred-odd loop iterations of real work, so the conversion
> disappears into the win. The question is never the object count on its own,
> it is the work done per object crossed.

[] Reject

**Section: "Choosing a Strategy" — the ladder's last two rungs are in the
opposite order from the chapter.**

The ladder is explicitly ordered by cost ("Work down this list from the
cheapest change to the most involved"), and every rung matches the chapter's
section order except the last pair: the chapter presents Rust
(section 14) before Concurrency (section 15), while the ladder lists
Concurrency as 9 and Rust as 10. A reader using the ladder as an index finds
exactly one item where it disagrees with the chapter.

Recommended: swap ladder items 9 and 10 so the list matches the chapter's
order. The chapter's own arrangement is the defensible one, since the Rust
section's closing paragraph ("That is one baseline and three ways past it")
ties Rust to the NumPy and Numba sections immediately above it, and moving the
section would break that sentence.

Alternative, if you think restructuring for concurrency really is the more
expensive change: leave the ladder alone and move the "Concurrency" section
up, to sit directly after "Combine NumPy and Numba" and before
"Converting a Slow Function to Rust". **Price:** that costs the "one baseline
and three ways past it" paragraph, which currently closes the Rust section by
looking back over the three preceding sections; it would need rewriting to
skip over the interposed Concurrency section. I recommend the ladder swap
instead — it costs two lines.

[] Reject

**Exercises — three sections have listings but no exercise, and the set
clusters on the middle of the chapter.**

Exercise coverage by section: Profilers (8), `sys.monitoring` (7), `timeit`
(1, 2), Idiomatic Python (—), Bisect (—), Heap (5), Lazy (3), Caching (4),
Slots (6), Array (9), Memory View (—), NumPy/Numba/Rust (—, reasonably, since
the reader may not have the dependencies).

The three gaps with runnable code and no exercise are Idiomatic Python,
Bisect, and Memory View. Two candidates, both answerable from the chapter
alone and both short:

> Time `"".join(parts)` against `+=` in a loop for 10,000 short strings, then
> repeat at 100 strings. At which size does the difference stop mattering, and
> which of the two would you write anyway?

> `bisect_search.py` uses `bisect()` and `search_comparison.py` uses
> `bisect_left()`. Build a sorted list with duplicates, run both against a
> value that appears three times, and explain which one you need to find the
> first occurrence and which one you need to insert after the last.

The second one exercises the pair the chapter now contrasts in prose, which is
the usual sign a distinction is worth an exercise. A memoryview exercise
depends on whether the size-comparison finding above lands, so I have not
proposed one.

---

## Cross-chapter

None. I checked the obvious candidates and all of them are consistent:

- Chapter 16 (Comprehensions) makes no speed claim anywhere, so chapter 18's
  "A comprehension is faster than an `append()` loop, though the margin is now
  small" is the only statement on the subject in the book and contradicts
  nothing.
- Chapter 3 (Containers) makes no speed claim about containers, so chapter
  18's "The immutable containers ... are not a speed upgrade" paragraph is
  likewise the sole statement. I verified its claims on 3.15: `frozenset` and
  `set` membership are within a few percent of each other, and `frozendict`
  and `dict` lookup are within 1% when measured with named functions rather
  than lambdas. (A first measurement using lambdas showed `frozendict` at
  twice the speed of `dict`; that was a measurement artifact and does not
  reproduce. Worth knowing if the paragraph is ever re-verified.)
- Chapter 19 (Concurrency) covers free threading and the GIL but not the
  CPython JIT, so the "Try a Faster Platform" gap above is a chapter-18 fix
  and does not need anything from 19.
- All nine outbound cross-references (`03#deque`, `03#immutability`,
  `07#properties`, `16#generator-expressions`, `19`,
  `19#coordinating-threads-with-queues`, `23#reusable-algorithms`,
  `40#pure-functions`, `43#declarative-style`) resolve, and their link-text
  style matches how the rest of the book names those chapters.

---

## Verified and correct — recorded so a later review does not re-check them

Everything below was checked against the 3.15.0b2 toolchain in the workspace,
the library sources, or the web, and needs no change:

- PEP 799 is Final and targets 3.15. `profiling.tracing` and
  `profiling.sampling` both import; `cProfile.Profile is
  profiling.tracing.Profile` is `True`. `python -m profiling.sampling --help`
  lists `run` and `attach` exactly as the chapter shows them.
- The `cProfile` sample table reproduces faithfully. I wrote a matching
  `prof_demo.py` and got the same row set, the same line numbers (1, 1, 7, 8),
  and the same 10001 `<genexpr>` count.
- `heapq`'s `_max` variants are documented "Added in version 3.14," and the
  full family is `heapify_max`, `heappush_max`, `heappop_max`,
  `heappushpop_max`, `heapreplace_max` — so "and friends" is accurate.
- PyPy's homepage claims "about 3 times faster than CPython 3.11" and PyPy
  currently implements 3.11, so both the 3x figure and "trails CPython's
  newest language version" hold.
- NumPy 2.5.1's newest wheels are `cp314` and Numba 0.66.0 classifies through
  3.14, so all three "no Python 3.15 release yet" parentheticals are accurate
  as of this review.
- `setup="gc.enable()"` works with a *callable* `stmt`, which is not obvious:
  `Timer.__init__` inlines a string setup into the template while turning a
  callable stmt into `_stmt()`, and `gc` resolves because the template's
  globals are the `timeit` module's own. Confirmed the timed calls see
  `gc.isenabled() == True` with the setup and `False` without.
- `sys.getsizeof` numbers in the prose are exact on this build: frozen
  dataclass 48 + dict 296 = 344 against a slotted 48 (7.2:1, "roughly seven to
  one"), and list 325,176 against array 80,080 (4.06:1, "roughly a
  four-to-one difference").
- `fib_plain(25)` really makes 242,785 calls (`2*fib(26)-1`) and
  `fib_cached(25)` really takes 26 misses.
- The Rust listing's `count_primes` and the Python one agree at the edges that
  usually differ: `n=2` and `n=3` are counted by both (`range(2, 2)` is empty;
  `while 2*2 <= 3` never runs), `n=4` is rejected by both, and
  `count_primes(1)` is 0 in both (`range(2, 1)` and `2..1` are both empty).
  The crate pins `pyo3 = "0.29.0"`, and the `#[pymodule] fn fastcount(m:
  &Bound<'_, PyModule>) -> PyResult<()>` plus `wrap_pyfunction!(f, m)?`
  signatures are the current PyO3 forms, not the deprecated ones. Nothing in
  `rust/` is buildable in this workspace (no toolchain, by design per
  `rust/CLAUDE.md`), so this is source review, not a compile.
- Every timing-comparison boolean is stable here. Eight standalone runs each
  of `membership.py`, `builtin_sum.py`, `hoist_attribute_lookup.py`,
  `search_comparison.py` (both booleans), `heap_vs_hash.py`, and
  `lazy_pipeline.py` produced `True` 8 times out of 8, on 2 shared CPUs. The
  measured margins also match the "One machine measured…" figures in the
  prose: set/list 16,022x against the stated ~22,000x, `sum()` 5.4x against
  ~5x, scan/bisect 1,683x against ~2,000x, bisect/hash 4.7x against ~5x, heap
  50x-ish (54.7x measured) against ~50x. No marker was touched.
- The chapter is already reflow-compliant, `heading_links.py` and
  `banned_phrases.py` are clean, no fenced line exceeds 70 characters after
  the two `demo.py` wraps, and `grep "def __init__(self" ` finds only
  `slots.py`'s, which is a deliberate teaching case (the very next listing is
  the `@dataclass(slots=True)` version).
