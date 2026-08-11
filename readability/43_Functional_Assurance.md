When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability pass over `Chapters/43_Functional_Assurance.md`,
run after the deep review in `deep_review/~43_Functional_Assurance.md` was applied.
That review's style audit had cleared most of the watch-list hits
("buy", "already", "exactly", "never" twice, "actually", several stranded prepositions),
so this pass found a nearly clean chapter.
Typography is clean: no curly quotes, no spaced `--`.
The deep review's "Considered and declined" items
(the `str` overclaim, "smallest example", the `strategies` import style,
`property_check.py`'s module-level loop) were honored and are not re-raised.
No live blocks: every finding either had one defensible answer or was declined as voice.

## Applied directly

- Line 198 (Assurance Spectrum, rung 1), watch list "never":
  "Most code never needs more." is now "Most code needs no more."
- Lines 133-135 (Automatic Parallelism), treadmill restatement:
  the same fact appeared three times in a row
  ("no changes to `count_primes()`",
  "The function needed no preparation for parallel execution",
  "It was ready on day one").
  The middle sentence merged into the third:
  "The function was ready for parallel execution on day one, because it was pure."
  The close alternative was deleting the middle sentence outright,
  but "for parallel execution" says what "ready" means,
  so it moved into the surviving sentence instead.

## Considered and declined

- **"No locks, no queues, no shared state, and no changes to `count_primes()`."**
  §9 by shape (a negation list).
  Kept: it enumerates real absent machinery, each item checkable against the listing,
  and the trim above removed the staccato pile-up that followed it.
- **"The thread running through these chapters is not that functions are special.
  It is that purity, immutability, and referential transparency shrink the distance..."**
  §9's not-X-but-Y shape across two sentences.
  Kept: the contrast is the chapter's thesis
  (properties, not functions, carry the assurance),
  and the paragraph closes the loop the introduction opened.
- **"Two caveats keep the chapter's argument from overreaching."**
  §36-adjacent framing before the disclosure.
  Kept: the frame states why the caveats exist rather than performing candor,
  and the deep review built the "Affordable Proof" section boundary around this sentence.
- **"*Declarative* code states the result you want."**
  "Want" addressed to the reader, which the global rule's carve-out covers
  (same ruling as the 31_State_Machines entry in `readability_db.md`).
- **"the simple, obviously correct version matches the fast one"** (oracle property).
  "Obviously" stays: the obviousness is the property an oracle test relies on,
  and it is the standard description of the pattern.
- **"functions really are a central part of the practice"** (intro).
  "Really" is the concessive beat before the "But" turn; deleting it flattens the turn.
- **"perhaps even some aspects that are mathematically provable"** (intro).
  "Even" marks a real escalation, from "what works" up to provable.
- **"This is automated falsification machinery."**
  A short labeling sentence, but a callback to rung 4 and the opening's science framing,
  and a single emphatic beat rather than a staccato run.
