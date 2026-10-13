> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 10_Foundations--Cleanup (2026-10-13)

No live blocks: every finding had one sensible answer, so it is applied or declined below.
I ran every chapter listing and every solution directly on Python 3.15.0 (`uv run`), with stderr visible,
and all output matches the `#:` markers.
The standalone shutdown transcript (`Third`, `Second`, `First`) still holds on 3.15.0,
and a simulation of the output checker (exec into a namespace dict, drop it, `gc.collect()`) still finalizes in the opposite order, as the prose says.
`ty` 0.0.86 still reports `invalid-return-type` for the solution 7 near-miss.
Removing `gc.disable()` from solution 6 prints the same transcript over three runs, as that solution claims.
I reread the five inbound references (chapters 4, 15, 26, 30, 35); all still hold after the edits.
`tip verify-ch CH=10 ISOLATED=1` passes 27 of 27 before and after.

## Applied directly

Chapter, teaching:

- `finalizer.py`: "strong reference" appeared before any definition, and "weak reference" was defined two sections after `finalize()` first depended on one.
  The paragraph after the listing now defines both, as a lookalike pair, where `finalize()` first needs them; the callback-separation half became its own paragraph.
- `finalize_trap.py`: added the near-miss a reader writes after learning to avoid `self.close`, a lambda that uses `self`.
  Probed: `finalize(self, lambda: print(self.name, "closed"))` keeps the object alive the same way.
- `finalize_trap.py`: "A `ref()` is a weak reference. It watches its object ... reports `None`" now says what calling the weak reference returns, since the listing calls `leaky()` and `safe()`.

Chapter, prose:

- `finalizer.py` paragraph on `[1]`/`[2]` and `del b` held two concepts (at-most-once, and destruction plus `atexit`); split at the seam.
  "the only reference" is now "the only strong reference", which the new definition makes precise.
- `finalize_trap.py` paragraph held four concepts (what `ref()` is, `Safe` reclaimed early, why `Leaky` survives, the `atexit` switch); split into three.
  Past tense on the listing's standing behavior ("printed", "reclaimed", "ran") is now present.
  "because its callback did not run and nothing failed" is now "since its callback has not run, and no error reports the leak".
- "The same `TypeError` meets `ref()`" (a figure) now says these calls raise the same `TypeError`, and names the `__weakref__` slot where "there" pointed back a sentence.
- "Two approaches are more reliable:" ended on a colon with a heading after it; now "more reliable than `__del__()`."
- `weak_value.py`: "last ordinary reference" is now "last strong reference", the term the chapter now defines.

Solutions:

- Exercise 1: "it (and every reference it held) becomes collectible immediately" said references become collectible. Now CPython frees the old list at once, which drops its reference to the remaining `Counter`.
- Exercise 1: an over-long hand-wrapped line rewrapped at about 70 columns.
- Exercise 6: the label "Pause the automatic collector" headed a paragraph about removing the pause; now "Let the collector run on its own."
- Exercise 6: "a demonstration whose entire subject is the absence of determinism" overstated `cycle.py`'s subject; now "a demonstration about unpredictable timing".

## Considered and declined

- **The `# Number of objects of this class` comment in `cleanup.py` stays.**
  It explains code, which new listings put in prose, but it is a pre-existing comment, and the listing-design pass that touched this listing on 2026-10-13 left it.
- **The PEP 442 history sentence, the `try`/`except` that prints in `closable.py`, `faulty_init.py`, and `exercise_7.py`, and the output-checker sentence** were declined in the 2026-09-29 review and still hold.
- **"the call destroys nothing" after `gc.get_referrers()`** stays: it tells the reader that the probe leaves the cycle in place for the `gc.collect()` below it.
- **No exercise for `slotted_no_weakref.py` or `resource_warning.py`.** Seven exercises already cover the chapter's main claims, and each of these listings makes its point in one call.

## For the session

- `tip watch-words` reports one stale baseline entry for chapter 10, "`only`: CODE holds the only reference to its CODE". The sentence now reads "holds the only strong reference", so the entry matches nothing; drop it from the baseline.
- No NEW `exercise_refs` or `quoted_diagnostics` hits, and no edits outside chapter 10's two files.
