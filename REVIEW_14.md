# Review: Chapter 14 (Comprehensions)

A review pass over `Markdown/14_Comprehensions.md`. The chapter is in good shape
technically; the items below are mostly editorial judgment calls for you.

## Verified OK (no action)

- **All 14 examples run** (`run_examples 14_Comprehensions`: 14 passed) and **all
  `##` output markers validate** (`validate_output.py Markdown/14_Comprehensions.md`:
  1 ok, 0 failed). Note: running the validator on the extracted `.py` *directory*
  reports false failures (`ModuleNotFoundError: a_list`) because the per-file path
  does not add the chapter dir to `sys.path`. That is a tool limitation, not a
  chapter bug; the Markdown-based validation is the real test and passes.
- **Images resolve.** `_images/listComprehensions` and `_images/idMatrix` map to
  `resources/images/listComprehensions.gif` and `idMatrix.png`, both present, and
  the site build copies them. Chapter 14 is the only chapter with images.
- **Cross-links resolve**: ch03 Comprehensions (intro back-reference) and ch24
  Iterators#generators (forward reference).
- House style: no em-dashes; sentences are mostly short.

## Changes applied

- **Missing comma** (Set Comprehensions): "Instead of `` [] ``**,** a set comprehension uses `{}`."
- **Item 1 — `os_walk_comprehension.py` now produces output.** Rewrote it to build a
  small temp tree (`tempfile.TemporaryDirectory`) with two `.py` files and one to
  skip, keep a real two-level list comprehension over `Path.walk()`, and print the
  matches sorted via `as_posix()` (deterministic and cross-platform). Output is now
  `main.py` / `pkg/util.py`, validated by the `##` markers. Added a one-line note
  after it explaining the outer/inner `for` clauses.
- **Item 2 — dict-comprehension intro reworded.** Replaced the confusing
  "the following is inefficient:" lead-in with a clearer setup that names the
  redundant-work caveat directly.
- **Item 3 — the four "parts" bullets are now sentence-cased** (List Comprehensions),
  matching the parallel bullets below the first example and house style.
  NOTE: if the Title Case deliberately mirrored the labels in the
  `listComprehensions` figure, the figure and bullets now differ in case — check
  the figure.
- All re-validated: examples run, markers validate, `make verify` passes.

## Still needs your eye (priority order)

### 4. "## Techniques" heading is vague
It covers `zip()`, tuple unpacking in the iterator, and the nested `Path.walk()`
comprehension. Consider a more descriptive name, or folding these into the
relevant comprehension sections. It currently sits between Nested and Set
comprehensions, i.e. before set/dict comprehensions are introduced.

### 5. Minor wording (optional, apply if you agree)
- Intro: "build one **sequence** from another" — sets and dicts aren't sequences;
  "collection" is more precise.
- List Comprehensions: "the list comprehension is enclosed within **a list**" reads
  more clearly as "enclosed in brackets `[]`".
- "We reuse **the** `ints` from `filtering.py`" → "We reuse `ints` …".
- The `filtering.py` → `mapping.py` chain reuses `ints` across files via `import`,
  a slightly unusual teaching device. Fine, just flagging.

## Suggested next step
Items 1 and 2 are the substantive ones. Say which you want applied (and how, for
the `os_walk` example) and I'll make the edits and re-validate.
