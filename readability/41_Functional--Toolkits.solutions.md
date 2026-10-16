> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/41_Functional--Toolkits/README.md`, 2026-10-16.
The file carries few AI-writing tells. One sentence had a logic slip, and I
fixed it directly. No finding needed Bruce's judgment, so this file holds no
live block and serves as the applied-directly record. I checked the claims
about listings against the chapter before deciding: the two-line length
difference against `nested_sum.py`, the eviction comment against
`functools_lru_cache.py`, the quoted `@cache` sentence against the chapter's
`cache` entry, the first round against `pair_rounds.py`'s output, and the
dependency-injection pointer against chapter 11's Random Numbers section. All
of them hold.

## Applied directly

- Line 493, logic slip: "The `rng` parameter lets the caller choose the seed"
  -> "choose the random source". The `seed: int = 0` version also lets the
  caller choose the seed. What `rng` adds is the choice of `Random` object,
  which the rest of the paragraph covers: a shared program-wide stream, or
  `random.Random()` seeded from the operating system.

## Considered and declined

- Line 60, "The rewrite changes something else: how much of the bookkeeping
  is yours." This is §69 by shape, but "something else" announces the one
  thing the colon delivers, so the global colon rule keeps it.
- Lines 66-68, "**Protect the caller's list.**" repeats the mutation point from
  the solution's opening paragraph (lines 32-37). Kept. The opening follows
  the Solutions convention of leading with the failing attempt, and the
  bold list has to name all three mistakes for "safe from all three
  mistakes" to land.
- The bold step labels (§15/§16) are the Solutions files' book-wide
  convention for walking a solution, and I did not treat them as boldface
  overuse.
- Line 214, "`count()` yields exactly fifteen integers in all." "Exactly"
  states a precise count, and it carries the laziness claim (no sixteenth
  integer is pulled). That is the case the watch-list rule allows.
- Lines 189-190, "forever ... forever". Rewording the second one to "never
  receives its argument" swaps one repeated word for a watch-list negative.
  The repetition matches the hang it describes.
- Line 256, "Python raises no exception, and the type checker accepts the
  function." The silence is the claim, and the two clauses are parallel
  reports of it, so the negative and the "and" both stay.
- Line 495, "accepts only an integer". The alternative it rules out is open
  ended, which is the `only` keep the global rule names.
