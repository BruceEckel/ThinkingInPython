> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 18_Techniques--Performance (2026-09-29)

This run is part of the book-wide sweep of chapters 01-29 and the appendices.
I checked each claim against its listing, the sections the chapter links (3, 7, 14, 16, 17, 19, 20, 23, 40, 41, 43), the installed interpreter (uv's managed 3.15.0rc2 and the python.org 3.15.0rc2 build), the 3.15 branch of the What's New, PEP 836, PEP 799, the `configure` documentation, Nelson Elhage's post, and PyPI for Numba.
Every measured listing ran three times with `--numbers`; the machine was loaded by the parallel sweep, so I changed no threshold, loop size, or timing marker.
`tip verify-ch CH=18` passes 24 of 24, and `tip verify` passes in the worktree.
One block needs your decision.

## Applied directly

Chapter, corrections:

- "The CPython JIT": the `pyperformance` figures were 8-9% (x86-64 Linux) and 12-13% (AArch64 macOS). The What's New on the 3.15 branch now reports 7-8% and 11-12%, linked to a run dated 2026-09-25. Updated both.
- Same paragraph: "the What's New marks them as not yet final" described a caveat the JIT section does not carry. The document's own header note calls the whole page a draft, so the sentence now says that.
- Same section: "pays in single-digit percentages" contradicted the macOS figure two paragraphs up. Now "pays in percentages".
- "Converting a Slow Function to Rust": "`cd rust && make`" names a Makefile that no longer exists. `rust/README.md` gives `tip rust-all`, so the sentence now reads "`uv run tip rust-all`".
- "Measuring One Function with `sys.monitoring`": `sys.settrace()` "slows every Python function in the process". The trace function is per thread. Now "every Python function its thread runs".
- Same section: "the callback ran once" is true of `used()` and false of the run, since the generator expression draws one `PY_START` too. Now "the callback ran for it once".
- `heap_vs_hash.py` is now `heap_vs_sort.py`. The section is "Heap Versus Sort" and the listing times a heap against `sorted()`; the old name survived from the version that compared against a hash. `tools/data/timing.txt` and `Examples/` follow.
- "Bisect": "Under heavy insert traffic consider the heap below instead" offered the heap as a general replacement for a sorted list. A heap replaces it only when the smallest item is all you read, and the sentence now says so.

Chapter, order and pointers:

- "The Tail-Calling Interpreter" opened with "The first of those speedups has no switch", a pointer to a sentence three paragraphs back, with PyPy, free threading, and hardware between, and with "switch" about to mean the C statement. The opener now names the interpreter and says the build chooses it. "The build decides." went, since the opener says it.
- The same section said "The payoff is again a percentage, and a larger one than the JIT's" before the JIT's payoff had been stated. The tail-calling section now states its payoff without the comparison, and the JIT section carries it: "again a percentage, and a smaller one than the tail-calling interpreter's on Windows."
- "The two speedups stack" used the JIT before its section. Now "The JIT in the next section stacks on top of this speedup."
- "Profilers": the paragraph named the first profiler, then the second, then returned to the first. `cProfile`'s cost now follows `cProfile`, and the command has a lead-in sentence.
- "A single lookup costs little either way. A million lookups is the difference between instant and minutes." sat in "Trusting a Measurement", between the `min()` advice and the command-line form. It is the consequence of the `membership.py` result, so it now follows the 14,000x sentence.
- "The failed assignment prints through `expected()`, which wraps the long slotted message" followed `slots_dataclass.py`, the second listing to show the wrapped message. It now follows `slots.py`, the first.
- "Caching": "which stores the result on the instance and dies with it, unless the class also declares `__slots__`" let "unless" attach to "dies with it". Split into two sentences; the second says a slotted class cannot use `cached_property`.
- "### Comparison" is now "### Scan, Bisect, or Hash". No link in the book targets the old anchor.

Chapter, teaching:

- "The Sampling Profiler": the chapter reads a `cProfile` report line by line and said of the sampling report only that it is a table. Four sentences now give the differences a reader meets on the first run: rows are source lines, `tottime` and `cumtime` are estimates, and no `ncalls` column exists, because a sampler cannot count calls. Checked against `python -m profiling.sampling run prof_demo.py`.
- "Lazy Evaluation with Generators": `get_traced_memory()` was used and never explained. Two sentences say it returns the current and peak byte counts and why each function gets its own `start()`/`stop()` pair.
- "Caching": `cache_info().misses` was printed and never explained. One sentence says what a miss is and why there are 26.
- "When Slots Does Not Fit": the `"__weakref__"` advice applies to a hand-written `__slots__`, and every class in the listing is a data class. Added "(`weakref_slot=True` adds it to a data class)".

Chapter, prose:

- "measures the machine's mood" is now "is a claim about the noise".
- "Push further and the process fails outright" (imperative plus consequence) is now "Past that point the process fails outright".
- "What Rust buys instead is..." is now "Rust offers something else: ...".
- "and even then, turning it on by default would need..." is now two sentences without "even".
- "the rare listing that reads the instance dict on purpose" spoke of the book's listings to a reader choosing a decorator for a class. Now "the rare class whose code reads the instance dict on purpose".
- Dropped "entirely" ("removes that `__dict__` entirely"), "itself" twice (the view, `data`), "exact" ("this exact top-N question"), and two "never"s in the Rust build paragraph.

Solutions:

- Exercise 3 asks "How close can an eager version get to the lazy one?" and the solution measured only the two eager versions. The listing now includes the lazy pipeline and prints `lazy peak under 1% of one list: True`. The functions are annotated, renamed `two_lists()`, `one_list()`, and `lazy()`, and `N` is `n` as in the chapter listing. The prose is rewritten around the measurement.
- Exercise 7's listing had no `# exercise_7.py` line, so nothing extracted or validated it and its two `#:` markers were unchecked. It has the line now, and the markers pass. I also ran the `set_events()` variant the prose describes: it prints `Counter({'fib': 177, 'square': 1})`, as the prose says.
- Exercise 9: `best(f: object)` with a `# type: ignore` is now `best(f: Callable[[], float])` with no suppression. "about 1.3 times" is "about 1.4 times", the ratio three runs gave.
- Exercise 12: "the two runs differ in the individual timings and agree on the ratio" did not match a run on the python.org 3.15.0rc2 build, where `PYTHON_JIT=0` and `PYTHON_JIT=1` gave `list_scan` times two percent apart and ratios five to ten percent apart, the same spread as two runs under one setting. The sentence now says the lines differ by no more than two runs under the same setting do.
- Exercises 1 and 4: added the missing annotations (`-> None`, `n: int`, `-> int`).
- Exercise 4: "A cache is a promise... breaks that promise" is now "A cache assumes... breaks that assumption."
- Exercise 5: "a heap never promises sorted order" is now "does not guarantee". "every element is smaller than its two children" is now "no larger than", which holds for duplicates.
- Exercise 6: "pays for both the slot descriptors and a dictionary": the descriptors live on the class, and the instance pays for the slots. Removed the blank line after the listing's name line.
- Exercise 8: the command is now `uv run python -m cProfile ...`, as in the chapter. I ran it: the `cumtime` and `tottime` orders match the prose.
- Dropped "exactly" (exercise 2), "actually" (exercise 8), "at all" (exercise 9), "only ever" and "buys" (exercise 5).

`tools/data/timing.txt`:

- Registered `hoist_attribute_lookup.py`, Solutions `exercise_1.py`, and Solutions `ch18_join_vs_concat.py`. Each prints a wall-clock threshold boolean and was unregistered, so a flip would have rewritten the marker silently.

## For other chapters

- "Numbers on Your Machine" says every measured listing prints its measurements under `--numbers`, and "Benchmark Alternatives with `timeit`" says "run any measured listing in this book with `--numbers`". Two measured listings print a threshold and never call `report()`: chapter 44's `pure_and_pointless.py` and chapter 47's `run_cost.py`. The fix that keeps this chapter's sentence true is a `report()` call in each.

---

## Move the measurement sections ahead of the platform sections

The chapter's epigraph is "Performance work is finding that place before changing anything", and "Choosing a Strategy" opens with "Measure first".
The chapter's order is "Is It Too Slow?", then three platform sections ("Try a Faster Platform", "The Tail-Calling Interpreter", "The CPython JIT"), and only then "Profilers", `sys.monitoring`, and `timeit`.
So the reader meets about 130 lines on interpreter builds before the first measuring tool.
Two passages in those sections already lean on the later material: the JIT section tells the reader to "time the workload with `PYTHON_JIT` set to `1` and to `0`", and the tail-calling footnote points forward to "Numbers on Your Machine".

Proposed order: "Is It Too Slow?", "Profilers", "Measuring One Function with `sys.monitoring`", "Benchmark Alternatives with `timeit`", then the three platform sections, then "Write Idiomatic Python" and the rest unchanged.
That is the order of the strategy list: measure, run the straightforward version, try a faster platform, write idiomatic Python.
The price is small.
The last paragraph of "Is It Too Slow?" ("If it is too slow, try the simplest remedy first") moves to open "Try a Faster Platform".
No heading changes, so no anchor changes, and no exercise moves.

I recommend the move.
The case against it: a platform change speeds up the whole program, so it needs no profiler to find a place, and putting it first says "try this before you study anything".
Both orders are defensible, and the choice changes how the chapter opens, so it is yours.

[] Reject

---

## Considered and declined

- **The Numba and Rust multiples use different Python baselines for `collatz_lengths`.** Numba's baseline loops over a NumPy array with `int(values[i])`, and Rust's loops over a list. I timed both baselines: 0.180 s against 0.175 s. The three percent gap does not change "Numba matches or beats Rust".
- **Module-level `n = 100_000` is not `Final`.** Every measured listing in the chapter writes its size this way, and the Solutions copies follow.
- **"Timsort detects the existing run".** CPython's merge policy has been Powersort since 3.11, but run detection is the same and the docs still use the name. On descending data `sorted()` beat the heap three to one here.
- **The Numba listings stay indented.** Numba 0.67.0 has wheels through cp314 and none for 3.15.
- **The hoist threshold (`t_local * 2 > t_attr`) is loose.** The prose says so and says why. Three runs gave the hoisted version between one percent faster and six percent slower.
- **Solutions listings named `ch18_*.py`.** Six Solutions files use the `chNN_` form; renaming three here would break the set.
- **`slots.py` hand-writes `__init__()`.** Standing exemption in `deep_review_db.md`.
