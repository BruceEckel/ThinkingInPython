[[Reviewed]]
# Humanizer candidates: Chapters/29_Changing_the_Interface.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

## How to use this

Each edit is a `###` block with a CURRENT and a PROPOSED fence.
Delete any block you don't want, save the file, and hand it back to me.
I apply what survives, verbatim, and run `make verify`.

The CURRENT fences are exact copies from the chapter,
so don't hand-edit inside them or the match will fail.
If you want a different wording, edit the PROPOSED fence instead
and I will use yours.

Tier A is what I'd apply. Tier B is genuinely arguable, delete freely.
Housekeeping is not humanizer output; separate list at the end.

## Verdict

This chapter is short and largely clean.
Word-level AI vocabulary (§7), curly quotes, boldface-header lists,
sycophancy, hedging, and first-person-plural slips are all absent,
consistent with the pattern found in chapters 46-47.
The one confident finding is a hit on Bruce's own banned-word list:
"load-bearing" describing the `/` in `WhatIUse.op()`.
Three more small, defensible edits round out Tier A
(a participle tail, an emphasis italic, one word echo),
and three genuinely arguable calls sit in Tier B.

## Tier A

### A1 — line 104 — banned word ("load-bearing")

"load-bearing" is on the CLAUDE.md "Don't use" list.
Naming the real thing (what breaks, and where) reads just as well
and drops the metaphor.

CURRENT
```text
The `/` in `WhatIUse.op()` makes its parameter positional-only,
and it is load-bearing: `WhatIUse2.op()` renames the parameter to `what_i_have`,
and renaming a keyword-callable parameter in an override breaks substitutability,
so the checker rejects it without the `/`.
```

PROPOSED
```text
The `/` in `WhatIUse.op()` makes its parameter positional-only,
and removing it breaks the override below: `WhatIUse2.op()` renames the parameter to `what_i_have`,
and renaming a keyword-callable parameter in an override breaks substitutability,
so the checker rejects it without the `/`.
```

### A2 — line 6 — participle tail

The `providing` clause tacked onto the sentence is the pattern chapters 46
and 47 flagged freely. A colon states the same content as one tightly
linked clause instead of a trailing "-ing" phrase.

CURRENT
```text
*Façade* creates an interface to a set of classes,
providing a more comfortable way to deal with a library or bundle of resources.
```

PROPOSED
```text
*Façade* creates an interface to a set of classes.
This is a more comfortable way to deal with a library or bundle of resources.
```

### A3 — line 108 — emphasis italic

`*type*` isn't a term being introduced, the word appears elsewhere in this
same passage with no italics. It's used to stress the contrast with the
earlier "rename," which is the emphasis-italic pattern chapters 46/47
proposed freely.

CURRENT
```text
The rename is the smaller half of that story.
`WhatIUse2.op()` also changes the parameter's *type*.
Its base accepts a `WhatIWant`, and it accepts a `WhatIHave`.
```

PROPOSED
```text
The rename is the smaller half of that story.
`WhatIUse2.op()` also changes the parameter's type.
Its base accepts a `WhatIWant`, and it accepts a `WhatIHave`.
```

### A4 — line 249 — word echo

"already" appears at line 242 ("A module already presents...") and again
seven lines later. The first instance is doing real work (a module gives
you this for free, unlike a `Facade` class); the second just echoes it.
Dropping the second occurrence keeps the point without the repeat.

CURRENT
```text
A `Facade` class full of static methods only reproduces, with more ceremony,
what a module already gives you.
```

PROPOSED
```text
A `Facade` class full of static methods only reproduces, with more ceremony,
what a module gives you.
```

## Tier B

### B1 — line 11 — emphasis italics on ordinary pronouns

`*this*` and `*that*` aren't terms, they're italicized for rhetorical
effect at the section's opening hook. That fits the letter of the
emphasis-italic finding. But there's a real counter-argument: without the
italics, "produce a that" loses the signal that "that" is standing in for
a noun (the wanted interface) rather than functioning as an ordinary
pronoun, so removing them costs some clarity. I lean toward keeping this
one; flagging it because the pattern matches and the call is genuinely
arguable.

CURRENT
```text
When you've got *this*, and you need *that*, *Adapter* solves the problem.
The only requirement is to produce a *that*,
```

PROPOSED
```text
When you've got "this", and you need "that", *Adapter* solves the problem.
The only requirement is to produce a "that",
```

### B2 — line 169 — "precisely because" intensifier

CLAUDE.md calls out "exactly because" by name as a reach-for intensifier;
"precisely because" is the same construction with a different word. The
sentence means the same without it. Mild, and "precisely" is doing
legitimate technical work two sentences earlier (line 110, "annotate both
precisely"), so this isn't a chapter-wide tic, just this one instance.

CURRENT
```text
an adapter as a frozen dataclass with two properties,
built precisely because the handed-to-you type did not fit.
```

PROPOSED
```text
an adapter as a frozen dataclass with two properties,
built because the handed-to-you type did not fit.
```

## Housekeeping

No housekeeping issues found. Checked and clean:
no double blank lines, no `[[ ]]` draft notes, no spaced ` -- `,
and no em dashes at all in this chapter (nothing to preserve, nothing to fix).
No visible Semantic Line Break drift.

## Considered and not flagged

- **Italicized pattern names (`*Adapter*`, `*Façade*`) on every occurrence,
  not just first use.** Looks like a violation of the "italics only on
  first use" rule at first glance, but chapter 26 (`*Proxy*`, `*State*`)
  confirms this is a book-wide typographic convention for GoF pattern
  names, closer to italicizing a book title than emphasis. Left every
  instance alone.
- **`## Adapter`'s opening sentence** ("When you've got *this*, and you
  need *that*, *Adapter* solves the problem") restates the heading's term
  but carries real content (the shape of the problem Adapter solves), not
  a vapid "Adapters solve problems." Distinguished from B3, which is
  closer to pure restatement.
- **The four-sentence parallel in "Telling the Wrappers Apart"** (Proxy
  keeps/controls, Decorator keeps/layers, Adapter changes, Façade fronts)
  varies its structure for Façade specifically because Façade is
  structurally different, fronting many objects instead of one. Not a
  broken parallel, the variation matches a real distinction.
- **"comfortable" (line 7, 265) and "tangle" (line 242, 264)** recur across
  the chapter but far apart and thematically, tying the Façade opener to
  its synthesis in the closing section. Read as intentional callbacks, not
  echoes.
- **Nine occurrences of "only."** Each is a genuine restrictive qualifier
  doing real technical work (e.g. "only calls `f()`," "only for attributes
  Python does not find normally"), not filler. Left alone.
- **"Two details in the listing repay attention" is followed by an
  unlabeled first detail, then "Second, ..."** Missing an explicit "First,"
  but the proximity keeps it readable. Copyediting nit, not an AI tell or
  a housekeeping item; not included as either.
- **Lines 202-203** (the Façade definition: "a confusing collection of
  classes and interactions that the client programmer doesn't really need
  to see") reads like Bruce's established voice from the *Thinking in
  Java*/*Thinking in C++* era ("client programmer" is his long-standing
  term). Left alone as authorial continuity, not AI-generated.

## Scan coverage

Clean, no hits: §7 AI vocabulary, curly quotes, boldface/inline-header
lists, emojis, sycophancy and chatbot artifacts, knowledge-cutoff
disclaimers, hedging, false ranges, rule-of-three padding, hyphenated
word-pair overuse, negative parallelism/tailing negation, vague
attributions, "Challenges" sections, aphorism formulas, stranded
prepositions, the "nothing else" family, and first-person-plural slips
(no "we"/"us"/"our" anywhere in the chapter). Em dashes: none present, so
nothing needed preserving or flagging either way.
