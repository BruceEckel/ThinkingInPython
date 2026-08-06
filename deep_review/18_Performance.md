# Deep review: 18_Performance.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show what a profile actually looks like

**Kind:** teaching
**Where:** section "Profilers" (lines 42-81)

**Problem:** The chapter's whole argument rests on "measure first, a profiler tells you where the time goes,"
and the section gives four command lines but never shows a single line of profiler output.
A reader who has never profiled cannot picture "a table of hot functions ranked by sample count,"
and, more importantly, cannot read one when they get it.
The column that trips up every first-time user is `tottime` against `cumtime`:
the top row of a cumulative-sorted profile is always `exec`/`<module>`, which is not the hot spot,
and the function to attack is the one with high `tottime`.
Nothing in the chapter tells them that.
This is the biggest hole in the chapter: the reader can run the tool but cannot act on the result.

**Proposal:** After the `cProfile` command line, add a short indented sample of real output plus two sentences reading it.
Real output from this machine, trimmed:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.010    0.010 {built-in method builtins.exec}
        1    0.000    0.000    0.010    0.010 prof_demo.py:1(<module>)
        1    0.008    0.008    0.008    0.008 prof_demo.py:1(slow)
        1    0.000    0.000    0.001    0.001 prof_demo.py:11(helper)
        1    0.001    0.001    0.001    0.001 {built-in method builtins.sum}
    10001    0.001    0.000    0.001    0.000 prof_demo.py:12(<genexpr>)
```

with prose along these lines:

> `tottime` is the time spent inside that function alone.
> `cumtime` adds the time spent in everything it called.
> Sorting by `cumtime` puts `exec` and `<module>` on top, which tells you nothing:
> they call everything, so they contain everything.
> Scan down to the first row where `tottime` is large.
> That is the function to attack.
> `ncalls` decides how to attack it:
> one call burning eight milliseconds needs a better algorithm,
> ten thousand calls burning a microsecond each need fewer calls.

An indented (untested) block is right here, since the numbers cannot be gate-checked.

**Alternative:** show output from `profiling.sampling` instead, since that is the tool the chapter recommends for new code.
I prefer `cProfile` for the sample because its column layout is the one every reader will meet in existing tutorials and CI output,
and the `tottime`/`cumtime` lesson transfers.

**Cost:** roughly 20 lines in the chapter's second-most-important section. No listings depend on it. Touches nothing else.

---

## 2. Give the reader the magnitude, not just `True`

**Kind:** teaching
**Where:** sections "Benchmark Alternatives with `timeit`" (line 201) through "Heap" (line 418)

**Problem:** Six timing listings all print a boolean, and the chapter says why (line 209: portability).
That decision is right for the gate, but the side effect is that a reader finishes the algorithms half of the chapter
without ever seeing a number.
"set at least 100x faster: True" leaves them unable to tell whether the real gap is 100x or 20,000x,
and the difference matters: it decides whether swapping a container is worth the edit.
The chapter proves it does not have to choose. The memory sections already give both,
"one machine measured 344 bytes against 48" and "325,176 bytes against 80,080",
and those are the two passages where the scale actually lands.

**Proposal:** Add one observed ratio in prose after each timing listing, in the same "one machine measured" voice already used twice.
Measured on this machine (min of 5 repeats, pinned 3.15 beta):

- `membership.py`: `set` beat the `list` scan by about 22,000x.
- `builtin_sum.py`: `sum()` beat the hand-written loop by about 5x.
- `search_comparison.py`: `bisect` beat the scan by about 2,000x, and hashing beat `bisect` by about 5x.
- `heap_vs_hash.py`: the heap beat repeated `min()` on a set by about 50x.

Leave every listing and every threshold exactly as it is; this is prose only.

**Cost:** none. The booleans and their markers stay untouched, so no gate is affected.

---

## 3. Teach `timeit.repeat()` where the chapter argues about noise

**Kind:** teaching
**Where:** section "Write Idiomatic Python" (lines 320-327), and the `timeit` section that precedes it

**Problem:** The hoisting listing's prose makes the chapter's sharpest methodological point:
"Timing noise on a busy machine easily reaches ten or twenty percent,
so a claim about a small difference measures the machine's mood."
That is correct, and the chapter's answer to it is to widen the threshold until noise cannot flip the verdict.
But the standard answer is to reduce the noise, and `timeit` ships it: `timeit.repeat()` runs the whole
measurement several times, and taking the `min()` of those runs discards the runs that were interrupted.
The chapter uses `timeit.timeit()` six times and never mentions `repeat()`, so a reader who wants a
number rather than a boolean has no tool for getting a trustworthy one.

**Proposal:** Three or four sentences in the `timeit` section, after the paragraph explaining `number`:

> A single measurement includes whatever else the machine was doing.
> `timeit.repeat(f, number=100, repeat=5)` returns a list of five such totals,
> and the smallest of them is the run that was interrupted least.
> Report `min(...)`, not the mean:
> a slow run means something stole the CPU, so averaging folds that theft into your answer,
> while the fastest run is the closest you got to measuring only your code.

**Cost:** none, if it stays prose. Converting the listings to `repeat()` would be a larger change and I do not recommend it: the booleans are already stable across 8 runs here.

---

## 4. Warn that `timeit` disables the garbage collector

**Kind:** teaching
**Where:** section "Benchmark Alternatives with `timeit`" (around line 240)

**Problem:** `Timer.timeit()` calls `gc.disable()` around the timed loop and restores it afterward (verified in the 3.15 source).
That is a deliberate design choice for repeatability, but it means an allocation-heavy benchmark reports a time
production will never see, because production pays the collection pauses the benchmark suppressed.
A reader benchmarking two object-heavy designs against each other can pick the wrong one.
The chapter's closing advice, "Do your benchmarks using data that is shaped like production data," is exactly
the concern, and this is the one way `timeit` silently violates it.

**Proposal:** Two sentences after the "production data" paragraph:

> `timeit` also turns the garbage collector off while it measures, so its runs stay repeatable.
> For a benchmark that allocates heavily, that hides a cost production pays,
> so pass `setup="gc.enable()"` when collection pauses are part of what you are comparing.

**Cost:** none. Verify the `setup="gc.enable()"` idiom before shipping it; it is the documented workaround, but it is worth re-running.

---

## 5. Warn that `@cache` on a method keeps every instance alive

**Kind:** teaching
**Where:** section "Caching" (after line 677)

**Problem:** The section's caveat is purity, which is correct but not the mistake readers make.
The common one is decorating a method: `functools.cache` stores the argument tuple, `self` is the
first argument, so the cache holds a strong reference to every instance it ever saw.
Verified here: an instance whose cached method has been called once survives `del` and `gc.collect()`.
In a chapter whose surrounding sections are about *reducing* memory, an unqualified recommendation
of `@cache` points readers at an unbounded leak.

**Proposal:** Add to the purity paragraph:

> A method is the usual trap.
> `@cache` keys on every argument including `self`,
> so the cache holds a reference to each instance it has seen and none of them can be collected.
> For a value computed once per object, use `functools.cached_property`,
> which stores the result on the instance and dies with it.

The chapter already names `cached_property` two paragraphs earlier, so this closes the loop rather than introducing a term.

**Cost:** none. Reinforces an existing cross-reference to [Classes](07_Classes.md#properties).

---

## 6. Exercises miss the chapter's largest sections

**Kind:** exercise
**Where:** section "Exercises" (line 1183)

**Problem:** Seven exercises cover `timeit` (1, 2), laziness (3), caching (4), heaps (5), slots (6), and `sys.monitoring` (7).
Nothing touches profilers, `bisect`, `array`/`memoryview`, or the whole NumPy/Numba/Rust arc,
which together are about a third of the chapter and its most involved material.
The set clusters on the small executable listings and skips the sections a reader is most likely to get wrong.

**Proposal:** Add two, keeping the total under ten:

> 8.  Profile a script of your own with `python -m cProfile -s cumulative`.
>     Name the function with the largest `tottime` and the one with the largest `cumtime`,
>     and explain why they are usually not the same function.
> 9.  `compact_array.py` compares an `array` against a `list` of the same floats.
>     Time an element-by-element sum over each with `timeit`.
>     The `array` uses a quarter of the memory: is it also faster to iterate, and why not?

Exercise 9's answer is the chapter's own NumPy lesson arriving early:
reading an `array` element boxes a fresh Python `float` on every access,
so the compact layout buys memory and buys back nothing until the loop leaves Python.

**Alternative:** an exercise on the Rust crate instead of the `array` one, but that needs a toolchain the book deliberately does not require.

**Cost:** Exercise 9 needs its answer checked against a real run before shipping. Neither exercise adds a listing.

---

## 7. "A profiler is the only way to discover hot spots" contradicts the `sys.monitoring` section

**Kind:** prose
**Where:** section "Choosing a Strategy" (line 1152)

**Problem:** The chapter spends 60 lines teaching `sys.monitoring` as the narrow instrument for exactly this job,
and closes by saying a profiler is the only way to do it.
The two claims cannot both hold, and the summary is the passage a reader will remember.

**Proposal:** Replace with:

> A profiler is how you find them without guessing.

That keeps the force of the original (the point is *don't guess*) without excluding the tool the chapter just taught.

**Cost:** none.

---

## 8. The memory-cliff paragraph denies the middle ground it just described

**Kind:** prose
**Where:** section "Lazy Evaluation with Generators" (lines 616-624)

**Problem:** The paragraph describes three regimes: full speed, swapping at a thousandfold slowdown, then outright failure.
It then closes "There is no middle ground between full speed and failure,"
which contradicts the swapping regime described two sentences earlier.
The intended point is that the transition is a cliff rather than a slope, and the sentence as written says something else.

**Proposal:** Replace the closing sentence with:

> The slowdown is a cliff, not a slope:
> nothing warns you as the data approaches the limit,
> and everything changes the moment it crosses.

**Cost:** none.

---

## 9. "the four ways this chapter speeds up the same computation"

**Kind:** prose
**Where:** section "Converting a Slow Function to Rust" (lines 1121-1126)

**Problem:** Two small things are off. The next sentence calls plain Python "the baseline," so it is not one of four
*speedups*, and NumPy alone never ran this computation: it was demonstrated on `3x + 1`, while the paragraph's
subject is `count_primes` and `collatz_lengths`, neither of which vectorizes.

**Proposal:** Replace the opening sentence with:

> That closes the arc this chapter has been building:
> one baseline and three ways past it.

and leave the four sentences that follow as they are, since they already say which is which.

**Cost:** none.

---

## 10. Say when Numba compiles, in one place instead of three

**Kind:** teaching
**Where:** section "JIT Compilation with Numba" (lines 900 and 925)

**Problem:** The chapter states the compilation moment three times with three different framings:
"compiles such a function to machine code on its first call, in place" (line 900),
"`njit(count_primes)` compiles the same function `@njit` would decorate" (line 925),
and "Calling it once first pays the compilation and warm-up cost" (line 926).
The middle one says `njit()` compiles, which contradicts the other two.
"in place" is also doing no work: `njit()` returns a new object and modifies nothing in place.

**Proposal:** Cut "in place" from line 900, and change line 925 to:

> `njit(count_primes)` wraps the same function `@njit` would decorate,
> and returns something that compiles itself the first time it is called.

That leaves one consistent story and makes the warm-up line that follows read as a consequence rather than a repetition.

**Cost:** none. The parallel `fast_collatz_lengths` passage (line 976) uses the same warm-up idiom and needs no change.

---

## 11. `rust/README.md` is not at the repository root

**Kind:** prose
**Where:** section "Converting a Slow Function to Rust" (line 1115)

**Problem:** "`rust/README.md` at the repository root" reads as a claim about where the file sits.
It is in `rust/`. The directory is at the root; the README is not.

**Proposal:** "The repository's `rust/README.md` explains how to build and run it yourself."

**Cost:** none.

---

## 12. The comprehension bullet no longer clears the chapter's own noise bar

**Kind:** teaching
**Where:** section "Write Idiomatic Python" (the bullet list after line 279)

**Problem:** Measured on the pinned 3.15 beta, a list comprehension beats an equivalent `append()` loop by
about 1.1x in function scope and about 1.02x at module scope (min of 7 repeats).
The chapter's own standard, stated 40 lines later, is that "timing noise on a busy machine easily reaches ten
or twenty percent," which this gap does not clear.
A reader who follows exercise 2's spirit and measures this bullet will find the chapter fails its own test.
The bullet is still true and the comprehension is still the right thing to write, but for readability, not speed.
(I fixed the related error above it directly; see "Already fixed" below.)

**Proposal:** Say the size out loud rather than dropping the bullet:

> - A comprehension is faster than an `append()` loop,
>   though the margin is now small (one bytecode appends the element,
>   instead of an attribute lookup and a call).
>   Write it for the readability; the speed is a rounding error.

**Alternative:** cut the bullet and let `hoist_attribute_lookup.py` carry the "some classic optimizations stopped mattering" lesson alone. I prefer keeping it, since a reader will otherwise assume the gap is large.

**Cost:** none. Interacts with proposal 3, which supplies the measurement discipline this bullet needs.

---

## 13. Upgrading CPython is missing from "Try a Faster Platform"

**Kind:** teaching
**Where:** section "Try a Faster Platform" (lines 32-41)

**Problem:** The section offers two options, PyPy and hardware, and PyPy currently tracks Python 3.11
while the book targets 3.15. A reader on the book's own version cannot take step 2 of the chapter's ladder.
The cheapest platform change of all is missing: CPython itself got substantially faster from 3.10 onward,
and moving a project forward two or three point releases costs a test run rather than a rewrite.
It belongs above both existing options in a section ordered by cost.

**Proposal:** Open the section with a short paragraph placing a CPython upgrade first,
before the PyPy paragraph, noting that it is the only entry on the whole ladder that requires no code change at all.
Verify the specific version-to-version claim against current benchmarks before writing a number;
"substantially faster since 3.10" is safe, a specific multiple is not.

**Cost:** touches the ordered list in "Choosing a Strategy" (step 2), which would need the same addition.

---

## 14. `lazy_pipeline.py` is the only listing with a bare uppercase constant

**Kind:** code
**Where:** section "Lazy Evaluation with Generators" (line 573)

**Problem:** `N = 1_000_000` is `UPPER_CASE` with no `Final[...]`, against the house rule that a named constant
gets the full typed form. Every sibling listing in this chapter uses lowercase `n` for the same role
(`membership.py`, `search_comparison.py`, `heap_vs_hash.py`, `hoist_attribute_lookup.py`, and the NumPy snippet).

**Proposal:** Rename to lowercase `n`, matching the five siblings. Two uses in the file (`range(N)` twice).

**Alternative:** `N: Final[int] = 1_000_000`, which satisfies the rule but leaves this listing the odd one out stylistically.

**Cost:** touches one listing's code, so it needs a sync and a re-run. Output and markers are unaffected.

---

## 15. `slots_dataclass.py` demonstrates two exceptions two different ways

**Kind:** code
**Where:** section "Slots" (lines 728-751)

**Problem:** Within one listing, the slots violation uses `try` / `except AttributeError` / `print(type(e).__name__)`
and prints `AttributeError`, while the frozen violation uses `with ignore(AttributeError):` and prints
`FrozenInstanceError("cannot assign to field 'z'")`.
The reader sees two idioms for the same job in twelve lines, with no stated reason,
and the two outputs are not comparable: one shows a bare class name, the other a full repr with a message.
That undercuts the very comparison the listing exists to make.
`slots.py` immediately above uses the first form, so the listing is inconsistent with its neighbor too.

**Proposal:** Use `with ignore(AttributeError):` for both, so both violations print a full repr and the difference
between them (a plain `AttributeError` against a `FrozenInstanceError`) becomes the visible lesson rather than an artifact.
Requires updating two `#:` markers.

**Alternative:** leave it and add one sentence of prose explaining why the frozen case shows the message. Cheaper, but keeps two idioms in one listing.

**Cost:** two `#:` markers change; needs a sync and a re-run. `slots.py` above would stay on `try`/`except`, or change with it, which would also mean adding the `exceptions` import there.

---

## 16. "Is It Actually Too Slow?"

**Kind:** prose
**Where:** section heading (line 11)

**Problem:** "actually" is on the watch list, and here it is carrying the section's whole rhetorical weight in a heading.

**Proposal:** "Is It Too Slow?" The rest of the section supplies the skepticism; the heading does not need to.

**Cost:** changes the anchor `#is-it-actually-too-slow`. `heading_links.py` reports nothing pointing at it today, but re-run the gate after the change.

---

## Already fixed directly (no decision needed)

- line ~35: PyPy's claimed speedup was "4x to 10x". pypy.org currently says "On average, PyPy is about 3 times faster than CPython 3.11", so the chapter now says "about a 3x speedup on average." The neighbouring sentence about PyPy trailing CPython's newest version is still accurate: PyPy 7.3.22 supports 3.11 and 2.7.
- line ~253: "Built-in functions and comprehensions run their loops in C" was wrong about comprehensions. A comprehension's loop is bytecode (`FOR_ITER` / `LIST_APPEND` / `JUMP_BACKWARD`, confirmed by `dis`), not a C loop, which is why it beats an `append()` loop by ~1.1x while `sum()` beats a hand-written loop by ~5x. Changed to "A built-in like `sum()` runs its loop in C".
- line ~281: that correction removed the only explanation the comprehension bullet had, so the bullet now carries its real mechanism, matching the parenthetical style of the bullet above it: "(one bytecode appends the element, instead of an attribute lookup and a call)". See proposal 12 for the remaining question of whether to state how small the margin is.

## Verified, no change needed

Recorded so a later pass does not re-check these:

- Every listing runs clean and every `#:` marker matches stdout on the pinned 3.15 beta. `ruff` and `ty` pass.
- The six threshold booleans are stable: 8 runs each of `builtin_sum.py`, `hoist_attribute_lookup.py`, `membership.py`, and 6 runs each of `search_comparison.py`, `heap_vs_hash.py`, `lazy_pipeline.py`, all `True` every time. None is near its margin.
- Both quoted byte counts reproduce exactly on this machine: frozen 344 against slotted 48, and list 325,176 against array 80,080.
- The Rust crate builds and its demo reproduces the quoted sample numbers (12.5x and 34.8x here, against 12.2x and 34.3x in the chapter).
- `profiling`, `profiling.tracing`, and `profiling.sampling` all exist on 3.15.0b4; `cProfile` is a compatibility wrapper re-exporting from `profiling.tracing`; both `profiling.sampling run` and `attach` are real subcommands.
- Claiming an in-use `sys.monitoring` tool id raises `ValueError`, as the chapter states.
- `heapq.heapify_max`, `heappush_max`, `heappop_max`, `heapreplace_max`, and `heappushpop_max` are all public on this build.
- `frozendict` is a builtin on 3.15 (PEP 814), and the equal-speed claim holds: frozendict/dict, frozenset/set, and tuple/list membership all measure within noise of each other.
- Exercise 7's answer is correct: switching to `set_events()` adds exactly one new `Counter` entry, `square`.
