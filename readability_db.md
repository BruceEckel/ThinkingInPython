# Readability carry-forward

Three generations of `readability/` have existed. All three are gone from the
working tree; all three are recoverable from git.

- **First generation**, 84 files and roughly 6,700 lines, distilled 2026-08-09
  and deleted in `8660e7c1`. Recover any file with
  `git show 8660e7c1^:readability/~30_Patterns--Observer.r2.md`.
- **Second generation**, 47 chapter files written 2026-08-11 (`7f165a08`,
  "readability on the whole deep-review") over the fresh deep-review round.
  Every finding was applied to `Chapters/` at the time, though the files were
  not renamed with the `~` completion prefix until 2026-08-13. Distilled into
  this file 2026-08-13 and deleted. Recover any file with
  `git show bb81711a:readability/14_Techniques--Decorators.md`, with **no** `~` on the
  path: the rename and the deletion landed in the same change, so the committed
  second-generation files carry the bare chapter name even though every one of
  them had been applied.
- **Third generation**, 92 files written 2026-10-16, one per chapter and one
  per Solutions README. Distilled 2026-10-16 into "The 2026-10-16 generation"
  at the end of this file, which gives the recovery command.

**What a fresh readability pass should do with this file.** Read it first. This
skill hunts AI-writing tells and watch-list vocabulary, which makes it the pass
most likely to re-flag something a previous run already examined and kept.
Everything below survived that examination. Re-raising any of it is churn.

---

## Standing rejection

**08_Foundations--Static_Types: keep the two sentences after "the same idea checked at
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
(2026-10-04, Sweep Decisions: Bruce split the `Blob` sentence at its colon;
the "worth" stays. Chapter 11's "worth the small effort" became "justifies
the effort", his wording.)

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
among long sentences and does deliberate work. (2026-10-04, Sweep
Decisions: Bruce cut two fragments that stated a verdict on output already
on the page, chapter 18's "Same answer, from 242,785 calls against 26." and
chapter 47's "Four implementations, one Ability, one running program."; the
keep covers a beat, not a verdict.)

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

- **Colon reveals in 40_Functional--Foundations** ("A `match` is code: … The
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
- **Parallel prose decision tables.** 35_Patterns--Flyweight's four-way `If X, do Y` block
  and 26_Patterns--Factory's bullet list under "Which Factory Should You Use?" are
  decision tables written as prose; the uniformity is what makes them scannable.
  (2026-10-04, Sweep Decisions: within that uniformity Bruce cut 35's trailing
  "which is the least machinery for the job" as awkward, and gave 27's "When
  a name maps to a class" bullet a comma, matching its siblings.)
  24_Patterns--Template_Method's four-way "Structure fixes it… Discipline fixes the rest"
  anaphora is the same call.

---

## Considered and declined, still binding

These are watch-list hits and pattern matches a mechanical sweep will find
again. Each was judged and kept.

**26_Patterns--Factory, "Factory might be the most common design pattern."** An
unsupported superlative by shape. Kept: it is hedged with "might", it opens the
chapter, and it is first-edition voice. 11_Techniques--Testing's "One of the most valuable
habits in modern programming is unit testing", 01_Introduction's "one of the
most useful things this book can give you", and 21's "An important step forward
in object-oriented design" all ride on this precedent.

**27_Patterns--Function_Objects, "Python's best-known closure trap."** A superlative by
shape, but "best-known" orients the reader toward the trap they have heard of,
and the late-binding loop variable is the one closure trap with a reputation.

**27_Patterns--Function_Objects, "to say what one list of functions says directly."** Not
a finding at all: recorded as the sharpest sentence in the chapter and the
reason the *Command* section works. Do not "tighten" it. (Superseded
2026-10-04, Sweep Decisions: Bruce, "sentence can be simpler"; the "directly"
went and the sentence was simplified at his ruling.)

**30_Patterns--Observer, "It is simply a callable."** "Simply" is an empty adverb by the
deletion test, but this is the deflating beat in the two-sentence pair carrying
the chapter's central move, and the word supplies that spoken rhythm.
11_Techniques--Testing's "The `4` here is simply what `Random(0)` produces first" and
09's "annotations that merely describe one to come" are the same call.

**30_Patterns--Observer, "amounts to nothing more than a list of callbacks."** On the
watch list, but the global rule's own carve-out names this exact construction:
a comparative where the diminishing is the point. The rule's illustrative
example *is* this sentence. 20's "costs nothing more than having the three
methods" rides on it.

**30_Patterns--Observer, "a lambda equals only itself."** Both watched words are
load-bearing: the claim is identity-equality, and "a lambda equals itself"
without "only" is trivially true of everything. 22's "equals only its own kind"
is the same shape. (2026-10-04, Sweep Decisions: 30's stays, with "bound to
the same lambda" nearby at his note; 22's sentence he ruled "too long and
complex" and had split, the restriction kept in words. He also had the
"only" dropped from 42's "`None` says only 'no answer'" and 46's "only its
signature" sentence rewritten as shorter sentences, so the watch-list-
absolute keep does not cover those two.)

**31_Patterns--State_Machines, "The conditions and actions are plain methods."** "Plain"
draws a real contrast: against the `Condition` and `Transition` class
hierarchies the Java version needed, named a few paragraphs earlier.

**33_Patterns--Visitor, the `## The Price of the Empty Base` heading covering two
paragraphs.** The heading names only the first paragraph. Retitling
(`## What the Classic Shape Costs`) and splitting were both considered and
declined: the second paragraph ends on the line that motivates the whole
`singledispatch` section, so it sits last regardless; a retitle makes the
heading vaguer, and a new heading adds an anchor for two paragraphs.
(Retitled 2026-10-13 to `## Two Departures from the Classic Shape`, which
names both paragraphs; the commerce rule R2 settled the "Price" question.)

**33_Patterns--Visitor, "The output above shows results, not mechanism."** Flagged as §70
metadiscourse. Declined by the block's own criterion: "mechanism" is
established book vocabulary, thirty-plus uses across the chapters.

**33_Patterns--Visitor, "a framework you do not own already calls that…"** "Already" is on
the avoid-if-possible list but earns its place: the call site exists whether
you want it or not. This is the precedent a dozen other "already" keeps cite.

**25_Patterns--Surrogate, "in order to implement the *copy-on-write* idiom."** The one
Tier 1B "in order" in the book, and the deep review deliberately restored it:
the bare comma version read as two unrelated purposes, losing the causal link
that counting references is how copy-on-write knows when to copy. Binding.

**40_Functional--Foundations, "Choose `match` when the set of cases is fixed …
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

**2026-10-04, Sweep Decisions page: cost tallies Bruce had cut.** Chapter
20's "Satisfying three of them costs nothing more than having the three
methods" and chapter 22's "The price of an ad-hoc attribute bag is that
..." lost their cost frames at his ruling (R2); 22 keeps the words "no
type checker knows your attribute names" verbatim for the 22 -> 33 thread
in `deep_review_db.md`. The twelve keeps he confirmed on that page (01's
and 11's and 21's superlatives, 03's "assignment never copies", 06's
underscore colon, 08's structural-typing restatement, 20's "truly", 31's
"stored directly", 33's "results, not mechanism", 34's three-walker
paragraph, 40's two-colon parallel and its "Choose `match`" sentence)
stand as recorded.

---

## The 2026-10-16 generation

The third generation reviewed the whole book on 2026-10-16,
one Opus agent per file.
It held 92 files:
48 chapter and appendix reviews named `readability/<stem>.md`,
and 44 Solutions reviews named `readability/<stem>.solutions.md`.
Together they list 650 direct fixes and 833 declined items,
counted as list entries;
a few entries bundle several hits of one kind.
Eight files carried one block each.
Bruce rejected none.
All eight were applied the same day,
which gave those files a leading `~`.
`~31_Patterns--State_Machines.md`, a 2026-10-15 review of chapter 31 by the same pass
(two direct fixes, five declines, no blocks),
was deleted with them.
The applied-directly lists stay out of this file, for the reason given above.

Recover any of these files with
`git show <hash>^:readability/~44_Effects--Effect_Management.md`,
where `<hash>` is the commit "Readability: distill the 2026-10-16 generation and clear readability/",
the one that deleted them.
`git log --diff-filter=D -1 --format=%h -- readability/~44_Effects--Effect_Management.md`
prints that hash.
The nine closed files keep the `~` in their recovery path;
every other file has the bare stem.

### The eight blocks, all applied

None of these is a standing rejection.
Each sentence was decided on 2026-10-16,
so a fresh pass treats the current wording as settled.

- **10_Foundations--Cleanup, the last sentence of "The Rule".**
  "the leak it exists to catch" gave the registry a leak-detection purpose,
  where the chapter presents it as a live-instance counter.
  It now reads "so the registry leaves each object's lifetime as it was."
- **10 Solutions, exercise 4.**
  "The registry now causes the leak it exists to detect" became
  "The registry now leaks every `Counter` it tracks," decided together with the chapter's sentence.
- **20_Patterns--Rethinking_Objects, line 140.**
  The sentence now reads "Substitutability is the part of polymorphism that no tool can check."
  The proposed wording went in, over the alternative that made substitutability a separate guarantee.
- **21_Patterns--Design_Patterns, after the Design Principles list.**
  The first-edition send-off "You can hold this handful of fundamental ideas in your head while analyzing a design" was cut,
  so the section ends on its last principle.
- **23_Patterns--Singleton, the mutate-versus-rebind passage.**
  The middle statement of three, "Mutation makes the sharing work. Rebinding is the mistake that quietly ends it.", was cut.
  The figure paragraph, the code walk, and the refrain "Mutate through any name. Rebind only through the module." stay.
- **25_Patterns--Surrogate, the `weakref` cross-reference paragraph.**
  Cut whole, since the paragraph above it closes the topic.
- **29 Solutions, exercise 3.**
  The causal "so" before `@staticmethod` is gone,
  and the passage now reads "None of these functions uses `self`. `@staticmethod` makes Python call each one with the caller's arguments alone, even through an instance."
- **44_Effects--Effect_Management, line 75.**
  The "because" clause now gives the reason in place of the definition:
  "because the operation that changes the environment sits in that function's body."

### Keeps this round confirms

Most of the 833 declines are instances of the recurring keeps above.
A sweep that re-finds them should stop at the same place.
The 2026-10-16 instances of each:

- **A watch-list absolute that states a guarantee.**
  08's "The Python runtime never acts on a type hint",
  42 Solutions' "so it never propagates to the top-level handler",
  34's "even with a case for every node" (the concession is the claim).
- **"only" marking a restriction.**
  The six shapes ruled fine on 2026-10-04 account for most `only` hits,
  among them 05 Solutions' "Only `clear_by_method()` empties the caller's list",
  35's "Only identity proves sharing",
  and 41 Solutions' "accepts only an integer" (an open-ended alternative).
- **"want" for the reader's intent or a human subject.**
  16 Solutions' "whether you want the list",
  32 Solutions' "Which behavior you want",
  37's "the safety officer wants".
- **"is what" with a complement that needs it.**
  03 Solutions' "The rest is what `Counter` supplies",
  46 Solutions' "That is what structural typing means".
  A cleft with a noun-phrase complement, repeated to answer an exercise's question, stays too,
  as in 29 Solutions' "What you lose is the log."
- **"worth" weighing an effort against a condition.**
  07 Solutions' "is worth writing when a tool reads it",
  27 Solutions' "The second assertion is the one worth writing",
  47's "worth retrying", where retrying is the program's own vocabulary.
- **real/actual/genuine with the contrast named.**
  19's "A real deadlock has no `timeout`" (against the demo's bounded run),
  45's "The `# type: ignore` marks a real mismatch",
  47's six uses of "real clock" against the handled clock.
- **"plain" against a named alternative.**
  30 Solutions' "A plain `except`" against `except*`,
  37's "an alias for a plain `dict`" against `defaultdict`,
  B's "a plain assignment" against the annotated one.
- **A reflexive "itself".**
  07's "keeps each method from calling itself",
  47's "It prints nothing itself" (against the supplied `Narrator`),
  33's idiom "the end in itself".
- **A rhetorical question that names the section's problem.**
  15's "What does `with` call?",
  19's "How does `gather()` respond to a failure?",
  21 Solutions' "What stops working? Nothing.", which repeats the exercise's own question.
- **A rule of three that is an inventory.**
  13 Solutions' "an `is` test like this one, a membership test, or a call",
  34's "SymPy, Polars, and SQLAlchemy" (the next sentence uses each),
  36's "rewind, rollback, or restore".
- **A single tier hit.**
  13's "valuable", 21's "One of the most compelling motivations", 01's "daunting" and "myriad".
- **A short beat.**
  30's "It is not.", 32's "It works.", 43's "looks safe. It is not."
  19's "Three unrelated kinds of worker produce one set of answers." was weighed against the 2026-10-04 cut of verdict fragments and kept,
  because it is a full sentence stating the section's point beside a listing with no `#:` markers.
- **A superlative that orients the reader.**
  The Factory precedent and 28's "best-known closure trap" cover
  02's "one of the main reasons for Python's consistent readability",
  04's "the classic control-flow bug",
  and 41's "The best-known case is *Kirkman's schoolgirl problem*".
- **The book's own term, generalizing the "hook" keep.**
  A watch-list word or figure stays when it names a chapter's term or a listing,
  as in 25 Solutions' `near_miss.py` (a listing name that holds a don't-use phrase),
  39's "dissolve in Python" (chapter 21's heading "When a Pattern Dissolves"),
  and 43's "spectrum" and "rung", which the heading and the numbered list share.

### New recurring keeps

These judgments recur across files and are new to this file.

- **A negation that is the claim, or half of a named contrast.**
  The positive-statement rule keeps these, and §9 fires on the "not X but Y" shape.
  09's "The bug is not the class attribute. It is writing one where you meant a per-object default.",
  33's "Nothing edits `Flower`.",
  18's "The goal is not the fastest possible program."
  A silent failure takes a negative too,
  as in 16's "prints nothing and raises no exception".
- **An additive "and" across a change of subject.**
  The split rule fires on the subject change.
  The substitution test decides.
  Where no "but", "so", "while", or "whereas" fits, the "and" stays:
  two links of one chain (29's "Turning the key primes the pump, and priming starts the engine"),
  joint premises of a following "so" or "because"
  (07 Solutions' "The lookup starts at the class of the object, and `self` is a `MoreDerived`, so ..."),
  or two outcomes of one run (46's "`Terminal` prints Alice's greeting and `capture` stays empty").
  Two splits were tried and reverted because they left a run of short sentences:
  03's "`in` and `len()` work on all of them, and slicing works on the sequences"
  and 13's "Cases do not fall through ..., and `match` has no `break` to forget".
- **Bold step labels are the Solutions convention.**
  §15 and §16 fire on every Solutions README.
  The labels walk a solution's steps in prose (commit 85f6ce4d),
  as in 02 Solutions' "**Tell values from literal text.**"
  and 05 Solutions' "**Accumulate in the shared default.**".
  A first sentence that echoes its label and then goes further stays,
  as in 17 Solutions' "**Inherit the base's arithmetic.** `Celsius` inherits `float`'s arithmetic", which continues to the result type.
  A sentence whose whole content is its label was cut (see the last subsection).
  The same call covers the bold-label bullets of each chapter's Guidelines section (19)
  and A's numbered list, whose bold leads are full sentences.
- **A repeat that a collapsed step needs.**
  The hint, the shape, and the solution open one at a time,
  so a reader may see one step alone.
  A fact stated in the hint and again in the solution stays,
  as in 12 Solutions' 2000 as the one century year `Year` accepts,
  35 Solutions' "`record()` forwards `slots=False` alone",
  and 47 Solutions' "Without the guard, each worker builds another pool."
- **The trap-first opening.**
  A Solutions section opens on the wrong version failing,
  and the labeled steps then walk the repair.
  The overlap is the file's shape, not a treadmill.
  This round's instances are 02 Solutions' solutions 1 and 5,
  12 Solutions' solutions 2, 3, and 8,
  and 34 Solutions' `RecursionError` in exercise 2.
- **A restatement that adds a step.**
  §70 fires on the shape.
  The keep holds in three cases:
  when the second statement names the misreading
  (05's "The default looks like an expression each call evaluates, but Python evaluates it once, at the `def`."),
  applies the rule to a new subject (23's `Collection` requirement applied to `Countdown`),
  or re-establishes a frame after a digression
  (34's "*Interpreter* is *Composite* applied to language" after the `pathlib` digression).
- **A refrain or a parallel repeated by design.**
  18's "The 3x threshold sits far below any multiple you should see." in both the NumPy and the Numba sections,
  44's "An Effect Management System replaces ..." closing three separate arguments,
  29's introduction previewing a section that other chapters link by its anchor,
  so the section restates the point for a reader who arrives there directly.
- **An aphorism that states the mechanism.**
  §32 fires on the shape.
  The keep holds when the sentence is concrete and true of the listing beside it,
  as in 22's "An immutable type needs immutable fields.",
  A's "A row that lists everything tells you nothing.",
  and 46 Solutions' "a value nobody uses is a value nobody checks".
  44's "a space heater with extra steps" is a joke that carries the claim.
- **A colon that passes the "namely" test.**
  §69 fires on the shape.
  The colon rule keeps each of these:
  12's "Nothing objects: not the annotation, not the type checker, not the running program" (the style guide's own example),
  13's "It also has a name: the *expression problem*",
  A's "says how long that took: a decade".
- **A count lead-in.**
  31's "Two consequences follow from the mixin",
  04 Solutions' "Two things follow from that control.",
  46's "Two details in `greeter.py` matter:".
  Each count is exact.
  The items follow at once.
- **First-edition and first-person voice.**
  Beyond the superlatives above, this round kept
  17's "It is a fascinating tool and tempting to use",
  25's "At the heart of a framework is the *Template Method*",
  and 21's "(I'll readily admit that I may be missing something here)".
  Epigraphs belong here (16, 28, 45, and 10, whose different-subject "and" stays as epigraph voice).
  The author's "we" stays wherever it appears (27, 30, 31, 44).
- **The author's framing of common practice.**
  §5 fires on an unsourced generalization.
  The book keeps these as the author's claims:
  32's "Most programmers first write a third version.",
  34's "Textbooks usually present the *Interpreter* pattern as ...",
  44 Solutions' "Most codebases avoid the forwarding with a module-level logger."
- **An adverb that carries content.**
  §23's deletion test fails when the adverb states something the sentence needs,
  as in 22's "automatically creates" (Python builds the `dict` with no code from the class),
  38's "works entirely in rooms" (no grid coordinates),
  and "silently" or "quietly" marking an error the reader would expect (12, 16).
- **A commerce word for a measured quantity or the program's money.**
  R2's carve-out covers 03 Solutions' "the whole loop costs O(n²)",
  36's "cost about two million pointers",
  and 13's "a rough cost to send a message", money in the program's domain.
- **"exactly" for a precise match.**
  19 Solutions' "Exactly half the increments survive" (200 of 400),
  41's "exactly once", a combinatorial count, three times,
  39's "exactly one receiver".
- **Past tense for an event on the page.**
  38 Solutions' "the default kick was down to `0.00` by step 400",
  45 Solutions' "The type checker told you more.",
  46 Solutions' "`greet_all()` did the right thing all along."
- **A sharper rewrite that would add a claim.**
  The vaguer sentence stays when every sharper version states a fact the file lacks,
  as in 04's "the `KeyboardInterrupt` you press" (naming the key),
  12's "Copying instead of mutating reduces errors.",
  and 24 Solutions' "where ruff expects every import".
- **A paragraph's position answers the question its listing raises.**
  Moving the paragraph was weighed and declined in three cases:
  10's `WeakSet` aside, which answers "why a dictionary?" right after the listing,
  32 Solutions' `Origami(Paper)` paragraph,
  and 19 Solutions' paragraph about the `return` in solution 10.

### Conventions confirmed clean, 2026-10-16

- **Review naming.**
  A Solutions README review is `readability/<chapter stem>.solutions.md`,
  beside the chapter's `readability/<chapter stem>.md`.
  The readability skill names the chapter form alone.
  A completed file takes the `~` prefix on either name.
- **Bold step labels** and the six ruled-fine `only` shapes held across all 92 files.
- **Hand-wrap width.**
  Solutions READMEs are hand-wrapped near 70 columns,
  and an edited paragraph is rewrapped to that width.
  Hint paragraphs carry one sentence per line, in every Solutions file.
  Long or ragged lines left by an earlier edit,
  most often where a bold label went in,
  render the same,
  so a pass rewraps them when it edits the paragraph
  or when a line broke after one or two words.
- **"The test file confirms that:"**
  is the book-wide lead-in for test bullets
  (chapters 11, 23, 28, 29, 30, 34, 35, 36, and B).
- **"Here," and a colon introducing a listing.**
  B's four "Here," openers and 42's listing colons point at the listing that follows.
- **A chapter roadmap in an opening paragraph** (04, 40, 41, 45) orients the reader,
  so §28 and §70 leave it alone.
- **Exercise wording.**
  Exercise imperatives and questions stay,
  including 23's "What has `first()` cost you on an infinite source?",
  whose cost is the memory the listing reports.

### Superseded, confirmed, and left open

- 26's "in order to implement the *copy-on-write* idiom" keep, above, has lapsed.
  The smart-reference item now reads "which makes *copy-on-write* possible",
  with the causal link intact.
- 08's standing rejection was confirmed again.
- Three declines were left for an editing pass rather than ruled on:
  47 Solutions' "The same distribution is why the chapter uses a factory function rather than more `supply()` arguments"
  (the reason that follows is the nine-actor ceiling),
  42's sentence pairing a deleted `e` with `sum_type.py`'s kept results,
  and 23's closing list naming a peekable wrapper that exercise 8 builds.

### What a fresh pass should still look for

The 650 fixes clustered on a few shapes.
A fresh pass will find more of each.
Roughly 170 split an "and" that joined clauses with different subjects where "but", "so", or "while" fit.
Two keeps in 15 Solutions pass the "whereas" test,
"Entering is outside-in ..., and exiting is inside-out ..." and
"A truthy value suppresses the exception, and a falsy value lets it continue",
so a fresh pass should split them too.
About 100 cut a restatement,
most often a Solutions sentence that repeated its own bold label
("**Make the hidden input a parameter.**" followed by "Move the hidden input into the parameter list.").
Smaller clusters trimmed empty intensifiers (a bare "real", "truly", or "really"),
"worth" frames that rated a list in place of introducing it ("The cases worth testing are:"),
and pointers with two candidates,
where a "This" or an "it" could name either of two nouns in the sentence before.
Checking each rewritten claim against its listing turned up a few inaccuracies along the way,
so a pass that rewrites a sentence reads the listing first.

---

## The 2026-10-22 generation

A fourth pass ran on 2026-10-22, six days after the third and one day
after the whole-book technical and prose review, as 49 Opus agents, one
per chapter with its Solutions file, from a brief that set the
annealing disposition: apply every fix that clears the bar, discard the
rest, write a review file only for a finding only Bruce can decide.
No agent wrote one. The pass made about 70 edits across 41 chapter
commits, one to six per chapter, and found nothing to change in 01, 28,
29, 35, 36, 39, 40, and 43. `tip verify` was green afterwards with no
marker drift, and the prose tools reported four re-keyed baseline
entries and one new subject gap, all settled the same day.

The edits clustered on the same shapes as the third generation:
a sentence restating the paragraph before it or its own bold step
label (about 30), a "worth" frame with no cost weighed (21's "worth
learning", 08's "worth annotating precisely", 46's "worth declaring"),
a §70 "X matters" or "note that" frame (15, 25, 31, 47), an aphorism or
closer that would fit any chapter (17's "Choose the lightest tool", 24's
"only as secure as its anchor", 31 Solutions' "Both model a thing that
changes behavior over time", 45's "the question stops being what a
function does"), a bare "real" or "really" or "much more" (14
Solutions, 32 Solutions, 34 Solutions), a trailing participle (17, 31,
A), and a passive with a by-phrase (44). Three agents rewrapped a
Solutions paragraph whose lines broke after one word.

### Keeps this round adds

- **A deliberate repetition in 01's AI-disclosure section.** Lines 60
  to 69 say three times that Claude made the work faster without
  replacing it; the last sentence was added on its own on 2026-09-30.
  Treat the passage as settled. Vale's one standing warning, "excellent"
  at line 69, is in that sentence and is Bruce's own.
- **"Real" against the exercise or the demo.** "In a real codebase" (07
  Solutions), "A real module" (29 Solutions), "has a real adapter" (29),
  "Real programs chain steps" (42), "a real rock-paper-scissors
  tournament" (32 Solutions). The contrast is the listing on the page,
  named by context rather than in the sentence. It joins the §34 keep.
- **The chapter's own term, again.** 24's "faithful substitute" and the
  Solutions heading "faithless substitutes" fire §35 and stay: they are
  tied to the listing name `faithless_step.py`. 24's "starts the engine"
  matches its heading. The convention entry above for 24's "Structure
  fixes it ... Discipline fixes the rest" anaphora is stale: that section
  is now a bullet list.
- **A test-list lead-in.** "The tests cover:" (31) and "The tests
  confirm that:" (37, B) are the same book-wide lead-in as "The test
  file confirms that:", and the bare-noun bullets under them are the
  file's convention, not §59.
- **"X matters" with the reason in the next sentence is a claim.** 10's
  "That ordering matters when `__init__()` fails", 30 Solutions'
  "Keeping the exceptions matters as much as catching them", 37's "The
  deeper skill is spotting the *vector of change*". Each is followed by
  the sentences that make it specific. The frame to cut is the one with
  nothing after it (15's "The parentheses matter", cut this round).
- **A known-before-new chain is not synonym cycling.** 35 Solutions'
  "serializes every miss" followed by "Serializing every miss" opens
  the next sentence on the fact just stated.
- **Three short claims in a row stay when each is a separate claim with
  its example following.** 47's "Each is reasonable alone. None composes
  with another. Some pairs allow no conversion." and 40's five
  properties of a composition under "Composing Functions".
- **"brand-new" in 09 Solutions** (three uses) stresses that the
  instance is fresh and is not an intensifier.
- **A restatement that closes an exercise's own question.** 27
  Solutions' "The exercise's closing question turns on that", 38
  Solutions' "That interleaving breaks the guarantee", 26's chapter
  closer restating line 691 with the static `factory()` half added.

### Tool notes

- `reflow_prose.py` does not split after a sentence that starts with a
  lowercase code name: 29's "(see exercise 5). mypy accepts it," stays
  on one line. The rendered text is the same.
- `tip grounding-triage` needs `TYPESAFE_API_KEY`, which the agent
  environment lacks. The sweep left three untriaged SR002 findings for
  Bruce: 25:209 (the reshaped mangling sentence, from this pass),
  25:779 and 44:1006 (untouched by this pass).
