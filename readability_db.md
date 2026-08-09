# Readability carry-forward

Distilled 2026-08-09 from `readability/` (84 files, ~6,700 lines) before that
directory was deleted.
Every file was tracked, so any review is recoverable:
`git show ce118d4:readability/~30_Observer.r2.md`.

**What a fresh readability pass should do with this file.** Read it first. The
readability skill hunts AI-writing tells and watch-list vocabulary, which makes
it the pass most likely to re-flag something a previous run already examined
and kept. Everything below survived that examination. Re-raising any of it is
churn.

---

## Standing rejection

**08_Static_Typing: keep the two sentences after "the same idea checked at
different moments".** The review proposed cutting "Dynamic typing trusts the
object once the code is running, while structural typing proves the shape
beforehand" as §70 restatement, since the paragraph states the timing contrast
three times. Declined. Both sentences stay.

---

## Considered and declined

These are watch-list hits and pattern matches that a mechanical sweep will find
again. Each was judged and kept.

**27_Factory, "Factory might be the most common design pattern."** An
unsupported superlative by shape, and the deep review did remove a similar
claim elsewhere in the chapter. Kept: it is hedged with "might", it opens the
chapter, and it is first-edition voice.

**28_Function_Objects, "Python's best-known closure trap."** A superlative by
shape, but "best-known" orients the reader toward the trap they have heard of,
and the late-binding loop variable is the one closure trap with a reputation.

**28_Function_Objects, "to say what one list of functions says directly."** Not
a finding at all: recorded as the sharpest sentence in the chapter and the
reason the *Command* section works. Do not "tighten" it.

**30_Observer, "It is simply a callable."** "Simply" is an empty adverb by the
deletion test, but this is the deflating beat in the two-sentence pair carrying
the chapter's central move, and the word supplies that spoken rhythm.

**30_Observer, "amounts to nothing more than a list of callbacks."** On the
watch list, but the global rule's own carve-out names this exact construction:
a comparative where the diminishing is the point. The rule's illustrative
example *is* this sentence.

**30_Observer, "a lambda equals only itself."** Both watched words are
load-bearing: the claim is identity-equality, and "a lambda equals itself"
without "only" is trivially true of everything.

**31_State_Machines, "a bug you want flagged."** "Want" is addressed to the
reader, which the rule's carve-out covers. The alternative ("a bug the machine
should report") is a change for its own sake.

**31_State_Machines, "The conditions and actions are plain methods."** "Plain"
draws a real contrast: against the `Condition` and `Transition` class
hierarchies the Java version needed, named a few paragraphs earlier.

**33_Visitor, the `## The Price of the Empty Base` heading covering two
paragraphs.** The heading names only the first paragraph. Retitling
(`## What the Classic Shape Costs`) and splitting were both considered and
declined: the second paragraph ends on the line that motivates the whole
`singledispatch` section, so it sits last regardless; a retitle makes the
heading vaguer, and a new heading adds an anchor for two paragraphs.

**33_Visitor, "The output above shows results, not mechanism."** Flagged as §70
metadiscourse. Declined by the block's own criterion: "mechanism" is
established book vocabulary, thirty-plus uses across the chapters, including
"the open-method mechanism that *Visitor* fakes" later in the same chapter.

**33_Visitor, "a framework you do not own already calls that…"** "Already" is on
the avoid-if-possible list but earns its place: the call site exists whether
you want it or not. (The noun after it was later changed from "hook" to
"method" during annealing; the "already" is the part that was cleared.)

**35_Flyweight, the four-way `If X, do Y` parallelism in `## Which Pool Should
You Use?`** Flagged under sentence-length uniformity: three `If` sentences and
an `Otherwise`, identical in shape. Declined: the section is a decision table
written as prose, the deep review asked for exactly four sentences organized by
the deciding question, and the parallelism is what makes them scannable.

**40_Functional_Foundations, "Choose `match` when the set of cases is fixed …
and a table when the set is meant to grow from outside."** §70 by shape, since
the two sentences above draw the same distinction concretely. Kept: the
abstraction is short, it is the sentence a reader returns for, and what precedes
it are examples rather than a statement of the rule.

---

## Conventions confirmed clean

Recorded so a sweep does not read them as defects:

- **Colon reveals in 40_Functional_Foundations** ("A `match` is code: … The
  table is data: …") are §69 by shape, twice. Both colons introduce a
  definition rather than staging a surprise, and the parallel structure is the
  point of the contrast.
- **Conditions, not imperative-plus-consequence.** "If you delete either
  `total = 0`, the second assertion fails" was deliberately written as a
  condition rather than the banned "Delete either … and …" form. Several such
  rewrites landed during the 2026-08-09 annealing pass across chapters 31, 36,
  40, 41, 42 and 47; they are the corrected form, not candidates for reversal.
- **Imperatives in exercises are exempt.** Exercise text instructs the reader,
  which the global rules carve out. Do not convert exercise imperatives to
  conditions.

---

## What was deliberately not carried

- **Applied-directly lists** (the bulk of these files). Each entry describes an
  edit already in `Chapters/`.
- **Live blocks**, which were applied when Bruce handed each file back.
- **`!Notes.md`.** Both directories had one. `deep_review/!Notes.md` was an
  empty scratch file; `readability/!Notes.md` held only the skill's own
  how-the-workflow-works explainer. Neither contained anything of Bruce's, so
  nothing personal was lost.
- **The r1/r2 split.** Most chapters had two rounds; r2 findings supersede r1,
  and only r2's declined items were durable.
