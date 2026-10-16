> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/18_Techniques--Performance/README.md`,
2026-10-16.
The file carried no AI-vocabulary clusters, no chatbot artifacts, and no
promotional language; its faults were four "and"s joining clauses with
different subjects, one restatement, and one sentence whose claim did not
say what it meant.
Eight fixes went in directly, and no finding needed Bruce's judgment, so
this file holds no live block and serves as the applied-directly record.
The nine-squares count in solution 3 (x = 0 to 8 yields the five even
squares) and the chapter's 325,176-against-80,080 figure quoted in
solution 9 were checked and hold.
`tip verify-ch CH=18 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 72, unclear claim: "The worst case and the average case diverge
  when most real lookups cluster near the front of the list" became "A
  worst-case measurement misrepresents a program whose lookups cluster
  near the front of the list, where a scan finds them quickly." The
  uniform-random average case cannot depend on where real lookups
  cluster, so the sentence can only mean the worst case misleads for
  such a program; "a scan finds them quickly" comes from line 67.
  Alternative: cut the sentence and end on "thousands of times faster in
  this run."
- Line 111, filler: "its advantage grows steadily as `size` increases,
  as the different growth rates ... predict" became "its advantage grows
  with `size`, as the growth rates ... predict", dropping "steadily",
  "different", and the first of two back-to-back "as" clauses.
- Line 274, "and" joining clauses with different subjects: "It prints
  ... on the first call with a given argument, and the cache silently
  skips that side effect" became two sentences.
- Line 337, "and" joining clauses with different subjects: "Sorting the
  whole list on every pop does far more work, and the extra order goes
  unused" became two sentences.
- Line 504, "and" joining clauses with different subjects: "produce the
  same `Counter`, and that agreement is an artifact of the example's
  size" became two sentences.
- Line 641, colon standing in for "because": "Not faster: on one machine
  the `array` took about 1.4 times as long" became "Not faster. On one
  machine ...", keeping the short answer as its own beat.
- Line 871, treadmill: cut "Work done in C runs no bytecode," which
  restated the paragraph's opening "The measured work runs in C, not in
  bytecode"; the next clause's second "the JIT" became "it".
- Line 877, repetition: "and the JIT spends time tracing and compiling
  whatever code crosses that threshold" became "and it spends time
  tracing and compiling every path that gets that far", removing the
  second "the JIT" and the second "threshold" in one sentence.

## Considered and declined

- Lines 736-739, three reasons to write `join()`. A rule-of-three by
  shape, but each item is a distinct reason (length, intent, scaling),
  the recurring keep for real triples.
- Line 728, "The absolute time shrinks instead." The "instead" contrasts
  with "The ratio persists" two sentences up, and the paragraph after it
  depends on that contrast.
- Line 852, "`True True` means the JIT is already running." The
  "already" is temporal: it marks the state in which `PYTHON_JIT=0` has
  something to switch off.
- Line 654, "which is why vectorizing is faster". The book's standard
  causal connector (readability_db.md, conventions confirmed clean).
- Line 800, "A membership test needs that, and `search_comparison.py`
  relies on it." The subjects differ, but the "and" is additive: the
  second clause names the listing that is the case in point.
- Line 512, "which is the question you had when you opened
  `sys.monitoring` instead of a profiler." An aside addressed to the
  reader that closes the solution's argument; voice.
- The prose uses one clause per line rather than hand-wrapping at 70
  columns, apart from solution 4's first paragraph. The edits match the
  surrounding form; rewrapping the file changes no wording.
