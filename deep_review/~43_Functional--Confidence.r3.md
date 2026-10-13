When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Third deep review of chapter 43, run 2026-10-13 in the deep-review sweep.
It carries forward `~43_Functional--Confidence.r2.md` (no rejections),
`~43_Functional--Confidence.md` (no rejections), and `deep_review_db.md`.
Tools: `uv run python` 3.15.0, `ty` 0.0.86, Hypothesis 6.169.0,
Pyright 1.1.414 (mypy is not installed).
`tip verify-ch CH=43 ISOLATED=1` passed 27 of 27 before the edits and
27 of 27 after.
Every listing ran and matched its markers. `parallel_pure.py` ran three
times under `--numbers`: serial 2.78/3.03/2.93 s, parallel 1.72/1.56/1.56 s,
so `faster` held each time with the machine loaded by the parallel sweep.
Probed by scratch scripts: an unguarded pool fails with `RuntimeError` in
each worker and `BrokenProcessPool` in the parent; a `lambda` and a
closure each fail in `pool.map()` with `_pickle.PicklingError` and a
`functools.partial` of a top-level function pickles; a Hypothesis test
over hidden state raises `hypothesis.errors.FlakyFailure`. The ex. 7
`ty` claims were re-probed against the single-argument `describe()`:
`float` in the `Ok` with `@final`, `float | Unknown` without it,
`ValueError` after the `isinstance()` test, `Exception` in the `match`'s
error cases; Pyright reports `float` without `@final`.
`group_rounds()` in Solutions exercise 5 matches chapter 41's listing.

No finding needed a decision only you can make, so this file has no live
blocks.

## Applied directly

- Solutions exercise 7 solved an older chapter 42. Commit 48b2db05
  changed `describe()` in `matching_errors.py` to take `result` alone and
  return the bare message, with the loop adding `f"{text}: "`. The
  solution's `describe()` now has that signature and those returns, so
  the comparison is against the chapter's current function. The line
  count (two fewer) and the three `result.error` reads still hold, and
  the markers are unchanged.
- `referential_transparency.py`: the two-line comment explaining
  interchangeability moved into the prose after the listing, which
  repeated it ("Because `add(2, 3)` and `5` are interchangeable").
- `codec.py`: the comment "Reversible, and not its own inverse:" (a
  fragment ending in a colon) moved into the prose before the listing,
  which now says what `encode()` produces and why it not being its own
  inverse matters (the round trip exercises two functions).
- Property-Based Testing: "asserting the law" came before any law was
  named, and the law was stated only after the listing. The sentence
  before `property_check.py` now names the *roundtrip* law and states it,
  with the italics moved there from A Family of Property Shapes, which
  used the term second. The post-listing sentence drops the restatement.
  "like the roundtrip" became "like the roundtrip law".
- Referential Transparency: "benefits the same way, and the more ... the
  more of it a machine, or a proof, can verify" joined two claims, and a
  proof does not verify. Now two sentences: optimizations "depend on the
  same interchangeability", and "a machine can optimize and a proof can
  cover" more of a transparent program.
- Automatic Parallelism: one paragraph explained both pickling and the
  `__main__` guard; split at the guard, whose opener now says it "follows
  from the same import". "the reasons Python parallelism uses processes
  rather than threads" ignored the free-threaded build that chapter 19
  covers; now "why CPU-bound work goes to processes rather than threads
  unless the interpreter is free-threaded".
- Property-Based Testing: the bare-`assert` sentence carried three
  clauses; split, with "but not the value" stated positively ("leaves
  out the value").
- The Same Law in Hypothesis: "rather than `property_check.py`'s
  five-letter alphabet, so it reaches inputs outside the loop's
  alphabet" said the alphabet twice; now one clause.
- A Family of Property Shapes: "Every shape in the family requires
  purity" gave the reason but not the consequence. Added what Hypothesis
  does when a test depends on hidden state: the replay can pass, and it
  raises a `FlakyFailure` in place of a shrunk counterexample (probed).
- Affordable Proof: the two caveats shared one paragraph; split at
  "Second,".
- Exercise 4: one sentence carried four instructions; now three
  sentences. Exercise 6: "*not*" was italics for emphasis, and "not
  referentially transparent without using `global`" read ambiguously;
  now "Without using `global`, write two functions that break
  referential transparency". Both Solutions quotes regenerated.
- Solutions exercise 1: the "Keep the worker function importable"
  paragraph said "importable from `__main__`" (a worker imports the
  script under another name) and wrote `count_primes` without
  parentheses. Now it says the pool pickles `count_primes()` by name
  and each worker imports the script, which a fenced block cannot offer.
- Solutions exercise 2: cut "exactly" from "reports exactly `1`";
  "present the identical `map()` interface and differ this fundamentally
  underneath" now says how they differ (separate processes against
  threads of one process).

## Considered and declined

- The heading "Affordable Proof" and "makes the proof affordable" use
  a commerce word for a consequence, which R2 discourages. "Affordable"
  is outside the listed family, the heading names the chapter's thesis,
  and the sentence states what it means (shorter reasoning steps). Left
  for Bruce's own eye rather than a block.
- `parallel_pure.py`'s `# Sample run:` comments, "Style contributes
  before the first rung", and Solutions exercise 1 printing a count
  rather than IDs: settled by the earlier reviews.
- "round trip" (noun, in Shrinking a Failure) beside "roundtrip law":
  the noun is ordinary English and the compound names the law.
- `property_check.py`'s inline `# A failing search must be
  reproducible` stays: it is short, and the prose later refers to "the
  job `random.seed(42)` does".

## For the session

- `tip watch-words` now reports two stale baseline entries for
  `Solutions/43_Functional--Confidence/README.md` ("reports exactly",
  "Only a real script file meets that requirement"); both sentences were
  rewritten. The baseline is outside this review's scope.
- The Solutions exercise 7 claim "Pyright and mypy ... report `float`
  with or without the decorator" was confirmed for Pyright only; mypy is
  not installed in the project environment.
- verify-ch regenerated `Examples/43_Functional--Confidence/codec.py`,
  `referential_transparency.py`, and
  `Solutions/43_Functional--Confidence/describe_isinstance.py` from the
  Markdown; they belong in the same commit.
