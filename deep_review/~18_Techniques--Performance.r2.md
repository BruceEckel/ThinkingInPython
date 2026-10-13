> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 18_Techniques--Performance (2026-10-13)

I read the chapter and its Solutions file against the 2026-09-29 review (`~18_Techniques--Performance.md`), whose one block (measurement sections before the platform sections) is already in the chapter, and against `deep_review_db.md`.
Tools: `uv run python` 3.15.0, `ty` 0.0.86.
Every measured listing ran three times with `--numbers` and every "one machine measured" figure still holds (13,000x set lookup, about 6x `sum()`, hoist 5-11% slower, about 1,700x and 6x for scan/bisect/hash, about 3.4x heap, 344 against 48 bytes, 325,176 against 80,080 bytes, about 10-11x NumPy); the Solutions measurements hold too.
I ran `prof_demo.py` under `cProfile` and `profiling.sampling` and checked the sampling report's columns against the prose.
I checked PEP 836, the released 3.15 What's New, pypy.org, and PyPI for Numba, and installed Numba 0.68.0 in a scratch 3.15.0 venv to run both Numba snippets.
`tip verify-ch CH=18 ISOLATED=1` passes 27 of 27 before and after.
No live blocks; the one large finding (Numba now supports 3.15) needs `pyproject.toml`, so it is under "For the session".

## Applied directly

Chapter:

- "Try a Faster Platform": "PyPy ... claims about a 3x speedup on average" is now what pypy.org says, about four times faster than CPython 3.11, and the vague "typically trails CPython's newest language version" names the gap (it supports 3.12).
- "The CPython JIT": "the What's New that reports them is still a draft" is stale; 3.15 shipped on 9 October and the page carries no draft note. The figures are unchanged. The sentence now credits the 3.15 What's New, and "The report sets aside" became "That report", which keeps its antecedent.
- "Heap": "a heap keeps that item reachable in O(log n)" mixed up the read and the removal. Now "at the front, where reading it is O(1) and removing it is O(log n)".
- "Caching": "Every avoided call is work the cached version skips" restated the premise. It now reads the output: `fib_plain()` ran 242,785 times, each step in `n` multiplies that by about 1.6 (2F(n+1) - 1 calls) and adds one miss.
- "When Slots Does Not Fit": "It removes everything that dict would have held" was false for two of the three cases, since `__weakref__` and the layout conflict have nothing to do with the dict. Now names the three changes (no `__dict__`, no `__weakref__` slot, a set layout) that the listing's three cases show.
- "JIT Compilation with Numba": "`njit(count_primes)` wraps the same function `@njit` decorates" now says it is the call `@njit` would make, and that calling it directly keeps the original as the Python baseline.
- "`sys.monitoring`": "makes coverage measurement affordable" (R2 commerce) and "the second answer is worthless" are now "keeps coverage measurement fast" and "a second report from the same location adds nothing".
- "Trusting a Measurement" (teaching, near-miss): the reader's likely alternative to `timeit`, a pair of `time.time()` calls around one call, was never addressed. Added a paragraph: the wall clock can jump, one call is one sample, `timeit` uses `time.perf_counter()`, and hand timing uses that clock and repeats.
- "Choosing a Strategy" step 7: "Cut per-object memory" did not fit `memoryview`, which saves copies, not per-object overhead. Now "Reduce memory overhead", the section's own title.

Solutions:

- Exercise 8: "the two rankings can name the same function only at the bottom of a call chain" did not follow from the leaf-function point (`prof_demo.py`'s `slow()` tops both columns below `exec`). Now: the columns hold the same value only for a leaf, and the top of `cumtime` is the outermost frame, so the two rankings usually open on different functions. Dropped a filler "only".
- Exercise 12: "times two lookups" is "times two kinds of lookup"; the listing times each a hundred times.

## Considered and declined

- **"turning microseconds into milliseconds, a thousandfold slowdown"** for swapping. An order-of-magnitude statement that holds for SSD paging; left alone.
- **"`@record` is `model()` from `kept_transform.py`"** names a chapter 17 listing without a link. The sentence before it links that section, and listing names become links at build time.
- **The Rust demo's sample numbers** come from an older run. I did not build `rust/` (outside the gate); see "For the session".
- **The 3.11 "1.25x" and "10-60%" figures** match the 3.11 What's New.
- **Exercise 2's "the set wins starting at size 2"** reproduced here (size 1 list, every other size set).

## For the session

- **Numba now supports Python 3.15.** Numba 0.68.0 (PyPI, 30 September 2026) ships cp315 wheels for win_amd64, manylinux x86-64/aarch64, and macOS arm64. In a scratch venv (`build/deep-review-scratch/18/venv315`, uv's 3.15.0) `numba==0.68.0`, `llvmlite==0.50.0`, and `numpy==2.5.4` (the project's NumPy) installed cleanly, and both indented snippets ran correctly (results asserted equal to the Python versions): `count_primes` 11.5x, 11.5x, 11.9x; `collatz_lengths` 37.0x, 37.3x, 38.0x. The chapter now says three false things: Numba "does not yet support the book's Python 3.15 target" (twice, in the parentheticals after each snippet) and, by its own TODO comments, both snippets should become fenced, tested listings. The conversion needs `numba` in `pyproject.toml`, which this agent may not edit. Steps: add the dependency, fence both blocks with `# numba_primes.py`/`# numba_collatz.py` lines, replace the `# Sample run:` comments with `report()` calls and threshold booleans (3x for primes, 10x for Collatz leave wide margins), register both in `tools/data/timing.txt`, drop the two parentheticals and the two TODO comments, and remove the "numba still blocked" note from `pyproject.toml`'s comment and from project memory `numpy-numba-blocked-on-py315`. The `deep_review_db.md` line "Numba stays an indented illustration (numba 0.66.0 tops out at cp314)" goes stale too.
- **The Rust comparison depends on that change.** "On both sample runs above, Numba matches or beats Rust (15.9x against 12.2x on `count_primes`, 54.4x against 34.3x on `collatz_lengths`)" quotes Numba numbers that today's 3.15.0 does not reproduce (11.5x and 37x). With 12.2x for Rust, Numba no longer beats it on `count_primes`. The Rust figures come from an older run too, so the sentence needs a fresh `uv run tip rust-all` on the same interpreter before it can say which is faster. The third TODO (time the NumPy+Numba Collatz version in `demo.py`) becomes doable at the same time.
- **Solutions exercise 7's generated shape block** drops `monitoring = sys.monitoring`, so its `TOOL: Final[int] = monitoring.PROFILER_ID` names an undefined `monitoring`. The block is owned by `tools/solution_steps.py`, which seems to keep `Final` constants and drop other module-level assignments; it should keep an assignment that a kept line reads.
