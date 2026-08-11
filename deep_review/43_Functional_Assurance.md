When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/43_Functional_Assurance.md`
in the clean-slate sweep. The mechanical layer is sound: all `#:`
markers validate, `ty` (0.0.70), ruff, and pytest are clean on
`build/examples/43_Functional_Assurance`, and every runnable script
runs, including `parallel_pure.py`, which prints the exact
`[1229, 2262, 3245, 4203]` the prose quotes (the four values are the
correct prime counts below each limit). The pickling claims were
probe-verified on the pinned 3.15.0b4: a `lambda` and a closure both
fail with `PicklingError` (not the `AttributeError` older Pythons
raised), and a `functools.partial` of a top-level function pickles.
The Hypothesis claims were checked against the installed 6.165.3
source: the default is `max_examples=100` ("a hundred of them"),
`strategies.text()` draws far beyond any hand-chosen alphabet,
`derandomize=True` and `database=None` behave as described (the
shrinking listing's `Failing test case: roundtrip(...)` note is
gate-validated every run), and the failure database default is
`.hypothesis/examples`, matching exercise 5. Hypothesis is an existing
project dependency; nothing was added. The `not_transparent.py`
arithmetic (`110`/`140`) checks out, the `@final` narrowing claim in
Declarative Style matches the chapter 42 review's probes on ty 0.0.70,
and the inbound anchors from 11, 18, and 40 (`#an-assurance-spectrum`,
`#declarative-style`, `#automatic-parallelism`) all point at headings
this review did not rename. The seven exercises match
`Solutions/43_Functional_Assurance.md` in number and content. No live
blocks remain: every finding had one defensible answer.

## Applied directly

- New `## Affordable Proof` heading before "Two caveats keep the
  chapter's argument from overreaching." The last three paragraphs
  (proof caveats, the thread through these chapters, the Part V
  pointer) are the chapter's conclusion, but they sat under
  "Property-Based Testing", which they are not about. The title comes
  from the section's central sentence ("makes the proof affordable");
  "the claim" became "the chapter's argument" so the referent survives
  the new boundary. No inbound links target a conclusion heading.
- Referential Transparency: `not_transparent.py` now credits its
  source at first reuse ("`withdraw()` from
  [Foundations](40_Functional_Foundations.md#pure-functions) does
  both, reading and writing the module-level `balance`"). The chapter
  redefined the function silently, then said "Recall `withdraw()` from
  Foundations" a section later, when the reader had just seen it 30
  lines up. The anchored link moved here, and Automatic Parallelism's
  sentence became "Two parallel `withdraw()` calls could both read
  `balance`...". Chapter 40's forward link to
  `#automatic-parallelism` is unaffected.
- Assurance Spectrum rung 5: "Dependently-typed languages ... prove a
  program correct ... checked by machine" is now "In a
  dependently-typed language ... you prove a program correct for every
  possible input, and a machine checks the proof." The languages do
  not prove; their users write proofs the machine checks.
- Shrinking section: the `test_` naming choice is now explained in
  full ("The function's name drops the `test_` prefix, and the listing
  calls it directly inside a `try`: a failing `test_` function should
  fail the build, and this one exists to fail"). The old sentence made
  the reader infer why the function was not named `test_roundtrip()`.
- Same section, lookalike pair: `derandomize=True` is now tied to the
  hand-written loop's `random.seed(42)` ("the job `random.seed(42)`
  did in the hand-written loop"), and the run-on sentence split into
  three.
- Same section: "the longer string it happened to fail on first" is
  now "the longer string that failed first" (stranded preposition,
  "happen" watch word).
- Rung 2: "the assurance you get is exactly as wide as the examples
  you think of" is now "no wider than the examples you invent"
  ("exactly" plus a stranded preposition).
- Rung 3: "most of what this rung is for" is now "most of what this
  rung offers" (stranded preposition).
- Rung 4: "the falsifiability the opening asked for" is now "the
  falsifiability the opening required of a science" (stranded
  preposition; names what the opening required it of).
- Spectrum intro: "buy assurance at every level" is now "provide
  assurance" ("buy" watch word).
- Oracle sentence: "which is what `parallel_pure.py`'s `assert
  parallel == serial` already claimed" is now "which ... claimed"
  ("is what" cleft plus "already").
- Declarative Style: "because there is less of it to be wrong about"
  is now "because less of it can be wrong" (expletive plus stranded
  preposition); "an optimized or parallel engine you never see" is now
  "you do not see" ("never" watch word).
- test_property paragraph: "inputs the loop can never produce" is now
  "cannot produce" ("never" watch word).
- Intro: dropped "actually" from "whether it's actually more about
  'functionality.'"
- `make reflow CH=43` settled the touched paragraphs.

## Considered and declined

- **"drawing on the whole of `str`"** slightly overclaims:
  `strategies.text()`'s default alphabet excludes surrogate code
  points, so not every `str` is reachable. The sentence's job is the
  contrast with the five-letter alphabet, and hedging it ("essentially
  all of `str`") would blunt that for a technicality no reader hits.
- **"shrinks it to the smallest example that still fails"** describes
  a greedy search, so "smallest it can find" would be strictly more
  accurate. Hypothesis's own documentation uses the same "minimal
  failing example" language, and the neighboring sentence ("keeps
  cutting it down until removing anything more makes the test pass
  again") states the real mechanism, so the claim stands.
- **`from hypothesis import given, strategies` rather than the common
  `strategies as st` alias.** The listings spell the module name out,
  which costs a few characters per call and matches the book's
  explicit-name style; readers meeting Hypothesis in the wild will see
  `st.text()`, but the full name is the clearer first exposure.
- **`property_check.py`'s module-level loop** keeps the hand-written
  version honest (a reader can run it as a script), and the chapter
  already explains why `test_property.py` repeats `encode`/`decode`
  instead of importing them. No restructure needed.
