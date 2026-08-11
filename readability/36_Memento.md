When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/36_Memento.md`.
The chapter is in good shape:
sentence lengths vary, paragraphs build on each other,
and no Tier 1A vocabulary, curly quotes, spaced `--`,
or structural tells appear.
The decisions `deep_review/~36_Memento.md` recorded
(the "already immutable" contrast, "never has to ask",
the hand-written `__init__()`s, the "Snapshots in the Wild" close)
were checked and not re-raised,
and nothing in `readability_db.md` names this chapter.
Three mechanical fixes were applied directly; there are no live blocks.
The remaining watch-list hits were each examined and kept, listed below.

## Applied directly

- Caretaker section: "the bug this chapter opened with" is now
  "the bug that opened this chapter" (stranded preposition;
  the transitive rewrite reads naturally).
- Restoring Part of a State: "The state has to answer it" is now
  "The state must answer it" (watch-list "has to";
  "must" is the chapter's own modal in the neighboring rules,
  "Both `save()` and `restore()` must copy", "states must be immutable").
- Ghost-field paragraph: "The data is just quietly wrong." dropped "just"
  (empty adverb by the deletion test; the deep review made the parallel
  cut of "simply" in "`title` is simply absent").

## Considered and declined

- **The chapter's seven single "never"s**
  ("never reaches `deep`", "never share one", "never calls `__init__()`",
  "the old bytes never had one", "never interprets anything",
  "the bytes never carried", "this one never raises an exception").
  "Never" is on the avoid-if-possible list,
  but each states a categorical guarantee that "does not" would weaken:
  pickle skipping `__init__()` on every load is the claim,
  not an observation about one run.
  The deep review's style pass already trimmed the one doubled use
  ("`repr()` never shows it and `==` never compares it" became
  "omits" and "ignores") and kept the singles; re-raising them is churn.
- **"`undo()` and `redo()` just shuttle the present between the two
  stacks."** "Just" is an empty adverb by shape, but here it means
  "merely" and draws the contrast with `do()`,
  which clears the future and starts a new timeline;
  the next sentences depend on that asymmetry.
- **"so even `repr()` raises `AttributeError`"** (rename drift).
  "Even" is on the avoid-if-possible list.
  Kept: it marks the escalation from the delete case,
  where `repr()` silently omits the ghost,
  to the rename case, where the most basic inspection fails.
- **"since real drift happens between two separate runs of a program"**.
  Watch-list "happen". Kept: this is the literal events-occur sense,
  and every synonym tried ("occurs", "arises") is a swap with no gain.
- **"No `Memento` class exists, no `save()`, no `restore()`, and no
  copying to protect the past."** A negation stack by shape (§9/§31),
  but it is a genuine enumeration of the machinery the frozen design
  deletes, the payoff of the Immutability section, and the items are
  concrete named things, not rhetorical fragments.
- **"a plain tuple it can index, unpack, or build from scratch"**.
  "Plain" draws the real contrast with the wrapped one-field data class
  two sentences later, the keep case in the style rules.
- **"The only way to see the strokes is through `.strokes`"**.
  "Only" is the uniqueness claim, not an intensifier.
- **"Version control is the Memento pattern at industrial scale."**
  Aphorism-shaped (§32), but the claim is concrete and the next sentence
  cashes it out point by point (commit = snapshot, checkout = `restore()`,
  shared content = shared strokes).
- **"Whoever holds `checkpoint` stores it and gives it back. It does not
  reach inside and edit the strokes."** The pronoun shift from "whoever"
  to "it" is slightly loose, but "it" reads as the caretaker named in the
  previous sentence, and the two clipped sentences carry the restraint
  point; merging them costs the rhythm more than the pronoun costs
  clarity. Not an AI-writing pattern; recorded only so a later pass does
  not rediscover it.
