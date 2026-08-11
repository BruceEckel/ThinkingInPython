When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first clean-slate deep review of `Chapters/10_Cleanup.md`.
The previous round's review (recoverable at `8660e7c^`) had every block
applied and none rejected, and the chapter shows it: the swallowed-exception
listing, `closable.py`, `finalize_trap.py`, the PEP 442 sentence, the
"Watching Objects Without Holding Them" promotion, and the rebalanced
exercise set are all in place and all still correct. The mechanical layer is
green: every `#:` marker validates, `ty` and ruff pass on
`build/examples/10_Cleanup`, all seven scripts run, and the six exercises
line up with `Solutions/10_Cleanup.md`. The finalizer-timing claims were
re-verified on the pinned 3.15.0b4: three consecutive direct runs of
`cleanup.py` print the shutdown transcript in the order the prose shows
(`Third`, `Second`, `First`), and `validate_output.py` still finalizes the
three objects in the opposite order, so the "one run on one machine"
passage remains true in both directions. The inbound anchor
`#watching-objects-without-holding-them` (used by `35_Flyweight.md`) is
untouched. This run produced no blocks: everything found had one sensible
answer and was applied directly.

## Applied directly

- "Reliable Alternatives", item 2: "`finalize()` runs the callback from
  `atexit`" now reads "from the `atexit` module's exit handlers". The word
  `atexit` appears nowhere else in the book, so a reader met a bare name;
  the gloss says what kind of thing it is.
- `finalize_trap.py` prose: "A `ref()` reports `None` once its object
  disappears" now opens "A `ref()` is a weak reference: it watches its
  object without keeping it alive, and it reports `None` once the object
  disappears." The chapter used "weak-reference machinery" as a section
  transition without ever defining the term; this puts the definition at
  the first concrete weak reference the reader sees.
- "why every `__repr__()` prints `3`" became "reports a count of `3`": the
  repr prints `Counter('First' 3)`, not `3`.
- "and what `__exit__`'s arguments are for" became "and what `__exit__`'s
  arguments mean" (stranded preposition with omitted object).
- "the leak it is watching for" became "the leak it is meant to catch"
  (same stranding, and "catch" needs no preposition).
- "labelled" became "labeled": the book's other chapters use the American
  form ("labeled `break`", "labeled passes").
- Watch-list trims, each verified to keep its meaning: dropped "at all"
  twice ("whether it runs at all", "containing a `__del__()` at all"),
  dropped "already" ("may have already vanished"; the two "already"s inside
  the verbatim docs quote are untouched), "before any deletion happens"
  became "before any deletion", "nothing tells you when it happens" became
  "nothing tells you when the collector runs", "only ever holds live
  objects" became "holds only live objects", "never depends on" became
  "does not depend on", and "which is what Flyweight does" became "which
  Flyweight does".

## Considered and declined

- `closable.py` annotates `__enter__` as `-> Socket` where chapter 15's
  canonical class-based context manager uses `-> Self`. Left alone:
  `Self` is not taught until [Context Managers](15_Context_Managers.md),
  this chapter precedes it, and `-> Socket` reads without new machinery.
- `Node` (`cycle.py`) and `Resource` (`del_swallows.py`) carry hand-written
  field-assigning `__init__` methods, which the house style would make
  dataclasses. Left alone: dataclasses arrive in chapter 12, after this
  chapter, and `Node`'s `peer` field is assigned post-construction, which
  a dataclass would only complicate.
- The HTML comment after the shutdown transcript says "Verified against
  3.15.0rc1" while the repo pins 3.15.0b4. Left alone: if the rc1
  verification was real (on another interpreter), it is the newer data
  point; if it was a typo, nothing downstream depends on it. This run
  re-verified the transcript on the pinned b4, three runs of three.
- The docs quote's first bullet (locks, deadlock, arbitrary threads) is
  never picked up by any listing, only the second bullet is. Kept in full:
  the deadlock hazard broadens the case against `__del__()` beyond what
  the chapter can cheaply demonstrate, and trimming a verbatim warning
  quote to the convenient half would weaken its evidentiary weight.
- "at a line you can point at" (after `closable.py`): a mid-sentence
  phrasal construction, not sentence-final stranding, and it came from the
  previous review's applied wording. Left alone.
