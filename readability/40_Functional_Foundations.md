> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/40_Functional_Foundations.md`

Second review of this chapter.
All three findings in `readability/~40_Functional_Foundations.md` were accepted
and applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one added a lot of new prose: a
rewritten Part IV/V preview in the intro, a follow-up under `why_pure.py`, a
`match`-versus-table paragraph, follow-ups under `closures.py` and
`composing.py`, and a whole new closing section. Every finding below is in that
new prose. The chapter's older prose is unchanged since the last review and
still reads clean.

Two problems in the new prose were corrected during the apply rather than
recorded here, because they were errors rather than style calls:
"Every idea in the chapter is present and doing work" was false (`pipeline.py`
uses no closure, lambda, `Placeholder`, or `compose()`), and is now
"Five of the chapter's ideas are doing work at once"; and
"`slope()` returns here as well" read as a function return rather than a
reappearance, and is now "`slope()` appears again later in the book".

---

**"Putting the Pieces Together", closing line: "keep spending" is a metaphor
standing in for a literal statement.**

> It is ordinary Python in which each piece depends on its arguments alone,
> and that single property is what the chapters ahead keep spending.

You do not spend a property. The image is presumably of purity as a balance the
later chapters draw down, but nothing earlier in the chapter sets up that
figure, so the verb arrives with no support and the reader has to reconstruct
it. This is the "odd word" case from the deep-review prose pass: technically
placed, but not the word this book would use.

Proposed change:

> and that single property is what the chapters ahead build on.

Alternative, if you want to keep the sense of the later chapters drawing on a
resource this one establishes:

> and that single property is what every chapter ahead depends on.

I recommend the first. It is the plainest statement of the claim, and "build on"
already matches "Purity is the foundation on which everything else in these
chapters builds" from the Pure Functions section, which makes the closing line
an echo of the chapter's own opening thesis rather than a new figure.

[] Reject

---

**"Putting the Pieces Together", lead-in: "They were built to combine" hides
the actor and overstates the design.**

> Every section above showed one construct on its own.
> They were built to combine:

The passive leaves it unclear who built them, and read literally the claim is
about Python's designers rather than about the chapter. §13 allows the passive
in technical prose when the actor is obvious; here it is not, and the active
version is both shorter and truer.

Proposed change:

> Every section above showed one construct on its own.
> Here they work together:

Alternative:

> Every section above showed one construct on its own.
> They compose:

I recommend the first. "They compose" is tempting because composition is the
section immediately above, but it would read as a claim about
`compose()` specifically, which `pipeline.py` does not use.

[] Reject

---

**Intro, second paragraph: the Part V preview is one sentence carrying four
chapters and three clauses.**

> Part V then takes the same discipline further:
> [Effect Management](44_Effect_Management.md)
> tracks a function's effects in its type, [Generators](45_Generators.md)
> supplies the mechanism Python already has for describing a computation without running it,
> and [Stateless](46_Stateless.md)
> and [Stateless in Practice](47_Stateless_in_Practice.md)
> build a checked Effect system on top of it.

The sentence is correct and the information in it is the point of the deep-review
block that added it. The trouble is the tail: "and [Stateless] and [Stateless in
Practice] build" puts two `and`s and two links in a row, and "on top of it" has
two candidate referents (the mechanism generators supply, or generators
themselves).

Proposed change: split after the Generators clause.

> Part V then takes the same discipline further.
> [Effect Management](44_Effect_Management.md)
> tracks a function's effects in its type,
> and [Generators](45_Generators.md) supplies the mechanism Python already has
> for describing a computation without running it.
> [Stateless](46_Stateless.md) and
> [Stateless in Practice](47_Stateless_in_Practice.md)
> then build a checked Effect system on that mechanism.

Naming "that mechanism" removes the ambiguous "it", and the colon becomes a
period so the paragraph does not run to six clauses.

[] Reject

---

**"Functions as First-Class Objects": the new `match` paragraph ends on a rule
the preceding sentences already gave.**

> Choose `match` when the set of cases is fixed and known to the compiler,
> and a table when the set is meant to grow from outside.

The two sentences above it already draw the distinction concretely ("adding an
operator means editing the function" against "adding a row, which another module
can do at import time"). The closing sentence restates that in the abstract, which
is §70: the gloss that tells the reader what to take from a passage that already
said it.

It is a close call, because a "choose X when Y" line is a genuinely useful thing
to be able to scan for, and this book does end several comparisons that way.

Proposed change: cut the sentence.

I lean toward not doing this. The abstraction is short, it is the sentence a
reader will come back for, and the two sentences above it are examples rather
than a statement of the rule. Recorded so the next review does not raise it
again as though it had not been considered.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- "A `match` is code: ... The table is data: ..." is a §69 colon reveal by
  shape, twice. Both colons introduce a definition rather than staging a
  surprise, and the parallel structure is the point of the contrast. Not
  flagged.
- "If you delete either `total = 0`, the second assertion fails" was written as
  a condition rather than the banned imperative-plus-consequence form
  ("Delete either `total = 0` and the second assertion fails"), which is what
  the deep-review block proposed. Already handled during the apply; noted here
  so it is not re-raised.
- The new exercises 6 and 7 use the imperative correctly: they are instructions
  to the reader, which the global rules exempt.
