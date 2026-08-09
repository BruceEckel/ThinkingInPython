> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/37_Pattern_Refactoring.md` (r2)

A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, and
there is no boldface, no curly quote, and no spaced ` -- `.
Everything below is in prose that has never had a readability pass: the deep
review's manifest edits and today's apply.

***

**Section:** `## Choosing the Lightest Construct`, the new middle sentences
**Pattern:** Protect the specific fact (skill step 6): a count the listings do
not support (P2)

Current:
> Here that meant two lines of Python.
> A dictionary keyed by `type(t)` absorbs new materials,
> and a `@singledispatch` function absorbs new operations.

The sentence is doing real work, naming the two constructs the conclusion
previously left unnamed. The number is the problem. `bins[type(t)].append(t)`
is one line, but the `@singledispatch` half is a decorator, a `def`, and a
`return` before any registration, and `recycling_note.py` runs to sixteen. A
reader who counts finds the claim off by an order of magnitude, and this
chapter has taught them to count lines.

Two ways to keep the sentence honest, and this is the one item here I cannot
settle for you.

**Option A: drop the count.** "Here that meant two constructs, not two
patterns." Keeps the contrast with *GoF* that the next sentence makes, and
claims nothing checkable that is false.

**Option B: make the count true by narrowing it.** "Here each vector cost one
line at the point of use: `bins[type(t)]` for a new material, one
`@recycling_note.register` for a new operation." Longer, but it is the claim
the chapter actually proved, and it echoes "cost a line instead of an edit
spread across classes" from the singledispatch section.

I lean toward B, because the per-use cost is the thing the chapter measured and
"two lines" was reaching for it.

[] Reject

***

**Section:** "Adding Operations," the subclass-dispatch paragraph
**Pattern:** Global watch list, "Don't use" tier (P1)

Current:
> so a `CrushedAluminum` derived from `Aluminum` lands in a bin of its own.

Proposed:
> so a `CrushedAluminum` derived from `Aluminum` gets a bin of its own.

Why: `lands` is on the "Don't use" list in `~/.claude/CLAUDE.md`, one of the
metaphors standing in for a literal statement. "Gets" is the literal verb, and
the same paragraph in "Let a Dictionary Do the Sorting" already writes "it
sorts into its own bin," so "gets" keeps the two consistent without repeating.

Nothing gates this word, so it survived the deep review's own checks.

[] Reject

***

**Section:** four places, chapter-wide
**Pattern:** Global watch list, "Consider rewriting" tier: `is what` (P2)

The chapter now carries four `is what` clefts, three of them added by the deep
review's manifest. Each is followed by a verb, which is the giveaway the global
rule names: the cleft only delays the verb.

> which is what [Pattern Matching](...) warned against.

becomes "which [Pattern Matching](...) warned against."

> which is what the next section does.

becomes "which the next section does."

> The `defaultdict(list)` is what creates a bin the first time a material turns up.

becomes "The `defaultdict(list)` creates a bin the first time a material turns
up."

All three pass the deletion test unchanged. The fourth is in the next block,
where the fix is not a deletion.

[] Reject

***

**Section:** "The First Cut," the last paragraph of the new `plastic_dropped.py`
commentary
**Pattern:** §69 Colon Reveals, §9 Negative Parallelisms, and the fourth
`is what` (P2)

Current:
> That is what "silently drop trash on the floor" means:
> not an exception to debug, but a number that is wrong and looks right.

Proposed:
> Nothing raises, and nothing is missing from the output.
> The plant gets a number that is wrong and looks right,
> which is what "drop trash on the floor" costs.

Why: three things stack in two lines. The cleft delays the verb, the colon
stages a reveal rather than introducing a list or a label, and "not X, but Y"
is the negative parallelism the skill flags. The proposed version states the
two facts first and lets the phrase the section opened with close it.

Lower confidence than the rest. The current version has a rhythm the rewrite
loses, and if you want to keep the shape, taking the colon out is enough:
"'Silently drop trash on the floor' means a number that is wrong and looks
right, not an exception to debug."

New with today's apply.

[] Reject
