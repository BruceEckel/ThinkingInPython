# Readability carry-forward

Two generations of `readability/` have existed. Both are gone from the working
tree; both are recoverable from git.

- **First generation**, 84 files and roughly 6,700 lines, distilled 2026-08-09
  and deleted in `8660e7c1`. Recover any file with
  `git show 8660e7c1^:readability/~30_Observer.r2.md`.
- **Second generation**, 47 chapter files written 2026-08-11 (`7f165a08`,
  "readability on the whole deep-review") over the fresh deep-review round.
  Every finding was applied to `Chapters/` at the time, though the files were
  not renamed with the `~` completion prefix until 2026-08-13. Distilled into
  this file 2026-08-13 and deleted. Recover any file with
  `git show bb81711a:readability/14_Decorators.md`, with **no** `~` on the
  path: the rename and the deletion landed in the same change, so the committed
  second-generation files carry the bare chapter name even though every one of
  them had been applied.

**What a fresh readability pass should do with this file.** Read it first. This
skill hunts AI-writing tells and watch-list vocabulary, which makes it the pass
most likely to re-flag something a previous run already examined and kept.
Everything below survived that examination. Re-raising any of it is churn.

---

## Standing rejection

**08_Static_Typing: keep the two sentences after "the same idea checked at
different moments".** The review proposed cutting "Dynamic typing trusts the
object once the code is running, while structural typing proves the shape
beforehand" as §70 restatement, since the paragraph states the timing contrast
three times. Declined. Both sentences stay.

---

## The recurring keeps

The second generation's declined lists run to roughly 200 entries, and almost
all of them are instances of the dozen judgments below. A mechanical sweep
re-finds every one. Read this section as the answer to "why does the book keep
doing X", not as a list of exceptions.

**A watch-list absolute stays when it states a guarantee.** *never, ever, only,
already, even* are the words this pass flags most, and the book keeps them
wherever the word carries a universal or temporal claim rather than emphasis.
The test: does weakening it to "does not" trade a guarantee for a report? If so,
keep it. "Assignment never copies" is a claim about every case; "hands out
references, never copies" is the contrast that explains the leak; "a lazily
imported name nobody touches never loads" is the silent-side-effect point;
"`Circle` and `Square` never mention `Drawable`" is a fact about the source. The
same reasoning keeps "only" wherever it marks a real restriction ("Only the
checker sees it, and only at edit time" is two parallel restrictions, not
filler) and "already" wherever it is temporal or marks work the reader does not
have to do.

**"want" addressed to the reader is the carve-out.** The don't-use entry targets
anthropomorphized objects ("the function wants a string"). "A bug you want
flagged", "the broad catch you want instead", "if you really want many handles
sharing one set of state" all address the reader's intent and stay. This
precedent is cited by a dozen chapters.

**"is what" survives when its complement cannot attach without it.** The global
rule states its own carve-out and the book leans on it: "The yielded value is
what `as` binds", "`f3()` is what forgetting looks like", "The rest is what
`SimpleNamespace` adds", "The counts, not a stopwatch, are what this listing
measures". Apply the deletion test; where deleting breaks the sentence rather
than tightening it, stop.

**"worth" stays where the frame weighs a real cost.** §53 flags the endorsement
family, and its carve-out covers most of the book's uses: "a separate factory
class is worth writing when …", "the hand-rolled `Messenger` is worth writing
only to show …", "`Blob` is the case worth watching:". Each weighs an effort
against a stated condition, with the payoff delivered in the same sentence.

**§34 real/actual/genuinely/truly stays where the contrast is named.** "the
caller's copy of the list still holds your actual `Bob`s", "It uses genuinely
separate functions per type", "When a program truly needs an object", "the real
class that does the work". In each the sentence itself names what the word
contrasts with, which is the rule's own exception.

**"plain" stays against a named alternative.** Against `defaultdict`, against a
generator function, against a descriptor, against a bound method, against an
`async` function. The book uses it as a contrast marker, not a filler qualifier.

**"itself" stays when reflexive and load-bearing.** "The `list` automatically
resizes itself", "A sub-pattern is itself a pattern" (without it the sentence is
a tautology), "a container holding an unhashable object is itself unhashable"
(the word marks propagation).

**A rhetorical question stays when the question is the content.** §43 targets
stalling transitions. "How does `with` know what to run?", "What should the type
annotation be?", "What happens if `gather()` encounters a failure?" each name
the genuine problem the section then solves, and each is its chapter's only one.

**Rule-of-three stays when the prose then uses the items.** §10 flags the shape;
the book's triples are usually inventories the following sentences pick apart
one at a time ("`Tally.total` is the first of these. For the third…"). Padding
to reach three is the defect, not three real items.

**Predicate-position hyphens stay on terms of art.** §26 would drop them, but
*thread-safe*, *black-box*, *I/O-bound*, *type-blind*, *positional-only*, and
*keyword-only* are hyphenated in standard usage regardless of position, and
several are terms the chapter defines and its headings use.

**A single Tier 1A or Tier 2 vocabulary hit is not a cluster.** The tiers fire
on density. "daunting", "myriad", "compelling", "valuable", "Notably",
"Certainly" each survived as the sole occurrence in their chapter, inside
first-person or first-edition passages.

**A short emphatic fragment is a beat, not a staccato run.** "It has a sharp
edge.", "No class, no ceremony.", "`seen` is how.", "I hardly do." Each sits
among long sentences and does deliberate work.

**An expletive "there is" belongs to `/activate`, not here.** "Unlike C, there
is no fall-through", "For event-heavy programs there are mature libraries". The
register pass owns that category; flagging it in a readability pass duplicates
work and invites conflicting rewrites.

**"hook" is the literal term, not a metaphor.** Chapter 17 uses it throughout
(including a `hook_order.py` listing and a "Which Hook for Which Job" heading),
chapter 25 introduces it in italics as GoF's term, and chapter 26 names
`__getattr__()` the fallback hook, which exercise 4 then depends on. Renaming it
anywhere breaks terminology with the chapter that owns it.

---

## Conventions confirmed clean

Recorded so a sweep does not read them as defects:

- **Colon reveals in 40_Functional_Foundations** ("A `match` is code: … The
  table is data: …") are §69 by shape, twice. Both colons introduce a
  definition rather than staging a surprise, and the parallel structure is the
  point of the contrast. The same call covers 06's "The underscore changes one
  mechanical thing:" and 02's "not a matter of taste: it is the structure".
- **Contrastive italics introducing a thing in its new role**: "is a *module*",
  "is a *closure*", "is a *hook*", "is a *handler*", the "*what*"/"*how*" pair.
  Book-wide convention across chapters 14, 25, 28, 29, 40, and 44, not
  italics-for-emphasis.
- **"which is why" as the causal connector.** Chapter 06 alone has seven. Each
  ties a listing's observed output to the mechanism behind it, which is the
  book's standard move. Only genuinely adjacent pairs were varied.
- **Conditions, not imperative-plus-consequence.** "If you delete either
  `total = 0`, the second assertion fails" was deliberately written as a
  condition rather than the banned "Delete either … and …" form. Several such
  rewrites landed during the 2026-08-09 annealing pass across chapters 31, 36,
  40, 41, 42 and 47; they are the corrected form, not candidates for reversal.
- **Imperatives in exercises are exempt.** Exercise text instructs the reader,
  which the global rules carve out. Do not convert exercise imperatives to
  conditions.
- **Parallel prose decision tables.** 35_Flyweight's four-way `If X, do Y` block
  and 27_Factory's bullet list under "Which Factory Should You Use?" are
  decision tables written as prose; the uniformity is what makes them scannable.
  25_Template_Method's four-way "Structure fixes it… Discipline fixes the rest"
  anaphora is the same call.

---

## Considered and declined, still binding

These are watch-list hits and pattern matches a mechanical sweep will find
again. Each was judged and kept.

**27_Factory, "Factory might be the most common design pattern."** An
unsupported superlative by shape. Kept: it is hedged with "might", it opens the
chapter, and it is first-edition voice. 11_Testing's "One of the most valuable
habits in modern programming is unit testing", 01_Introduction's "one of the
most useful things this book can give you", and 21's "An important step forward
in object-oriented design" all ride on this precedent.

**28_Function_Objects, "Python's best-known closure trap."** A superlative by
shape, but "best-known" orients the reader toward the trap they have heard of,
and the late-binding loop variable is the one closure trap with a reputation.

**28_Function_Objects, "to say what one list of functions says directly."** Not
a finding at all: recorded as the sharpest sentence in the chapter and the
reason the *Command* section works. Do not "tighten" it.

**30_Observer, "It is simply a callable."** "Simply" is an empty adverb by the
deletion test, but this is the deflating beat in the two-sentence pair carrying
the chapter's central move, and the word supplies that spoken rhythm.
11_Testing's "The `4` here is simply what `Random(0)` produces first" and
09's "annotations that merely describe one to come" are the same call.

**30_Observer, "amounts to nothing more than a list of callbacks."** On the
watch list, but the global rule's own carve-out names this exact construction:
a comparative where the diminishing is the point. The rule's illustrative
example *is* this sentence. 20's "costs nothing more than having the three
methods" rides on it.

**30_Observer, "a lambda equals only itself."** Both watched words are
load-bearing: the claim is identity-equality, and "a lambda equals itself"
without "only" is trivially true of everything. 22's "equals only its own kind"
is the same shape.

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
established book vocabulary, thirty-plus uses across the chapters.

**33_Visitor, "a framework you do not own already calls that…"** "Already" is on
the avoid-if-possible list but earns its place: the call site exists whether
you want it or not. This is the precedent a dozen other "already" keeps cite.

**26_Surrogate, "in order to implement the *copy-on-write* idiom."** The one
Tier 1B "in order" in the book, and the deep review deliberately restored it:
the bare comma version read as two unrelated purposes, losing the causal link
that counting references is how copy-on-write knows when to copy. Binding.

**40_Functional_Foundations, "Choose `match` when the set of cases is fixed …
and a table when the set is meant to grow from outside."** §70 by shape, since
the two sentences above draw the same distinction concretely. Kept: the
abstraction is short, it is the sentence a reader returns for, and what precedes
it are examples rather than a statement of the rule.

---

## What was deliberately not carried

- **Applied-directly lists**, the bulk of both generations. Each entry describes
  an edit already in `Chapters/`. Verified by spot-check across chapters 03, 14,
  and 44 before the second generation was deleted.
- **Chapter-local declined judgments** that are instances of the recurring keeps
  above rather than separate rulings.
- **Live blocks**, which were applied when Bruce handed each file back.
- **`!Notes.md`.** Both directories had one, in both generations.
  `deep_review/!Notes.md` was an empty scratch file; `readability/!Notes.md`
  held only the skill's own how-the-workflow-works explainer, then nothing at
  all. Neither contained anything of Bruce's, so nothing personal was lost.
- **The r1/r2 split** (first generation only). Most chapters had two rounds; r2
  findings supersede r1, and only r2's declined items were durable.
