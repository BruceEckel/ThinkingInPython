# Humanizer candidates: Chapters/43_Functional_Assurance.md

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

This chapter is clean of nearly every AI-vocabulary and content-padding
tell: no §1-§12 language, no boldface-header lists, no curly quotes, no
emoji, no filler phrases, no hedging, no signposting, no aphorism
formulas, no stranded prepositions. There are no em dashes anywhere in
the chapter, so §14 has nothing to preserve or flag. Three small,
solid findings survived a full read: one person-consistency slip
("we" leaking into the book's second-person voice), one flourish
"itself" that matches the exact CLAUDE.md example, and two stray
emphasis italics that don't introduce a term the way the chapter's
other five italicized terms do. Tier B is empty; nothing else rose to
a genuine "he could go either way" call. The largest single finding
is the "itself" flourish, since it is a verbatim match to the rule's
own worked example.

## Tier A

### A1 — line 69 — person consistency (we -> you)

The book is second person throughout. This is the only first-person-plural
slip in the chapter; the "I" in the opening paragraph is the author's own
voice and stays.

CURRENT
```text
This is the broader "functionality" we want.
```

PROPOSED
```text
This is the broader "functionality" you want.
```

### A2 — line 139 — "itself" as flourish

Dropping "itself" changes nothing: the sentence already lists what needed
no changes, and `count_primes()` is the only candidate for the pronoun to
refer back to. This is the same shape as CLAUDE.md's own "the class
itself" example.

CURRENT
```text
Notice there are no locks, no queues, no shared state,
and no changes to `count_primes()` itself.
```

PROPOSED
```text
Notice there are no locks, no queues, no shared state,
and no changes to `count_primes()`.
```

### A3 — lines 251, 283 — emphasis italics

The chapter correctly italicizes five terms on first use (*referentially
transparent*, *Declarative*/*Imperative*, *Strategy*, *invariant*,
*Idempotence*, *oracle*), each followed by a definition. These two don't
fit that pattern: neither word is a term being introduced, and each is
doing ordinary contrastive emphasis instead (behavior vs. implementation;
false vs. true).

**line 251**

CURRENT
```text
constrains the function's *behavior* without repeating its body.
```

PROPOSED
```text
constrains the function's behavior without repeating its body.
```

**line 283**

CURRENT
```text
3.  State a law that is *false* and watch Hypothesis falsify it:
```

PROPOSED
```text
3.  State a law that is false and watch Hypothesis falsify it:
```

Delete individual rows you want left alone.

## Tier B

None. Nothing here rose to a genuine judgment call once the Tier A
patterns above were pulled out. The chapter's other candidate-looking
spots (see Considered and not flagged) all resolved cleanly one way on
inspection rather than sitting on a fence.

## Housekeeping

1. The *roundtrip* law is never italicized, unlike its siblings
   *invariant*, *Idempotence*, and *oracle* in the same family (line
   238 names it "The roundtrip law," line 250 says "like the
   roundtrip"). Not a humanizer finding, just a naming inconsistency
   worth a look for consistency with the other three.
2. Semantic Line Break outlier at line 26: a single 124-character
   sentence with no internal comma or clause boundary to break at
   ("An expression is *referentially transparent* when you can replace
   it with its value without changing the program's behavior."),
   noticeably longer than the rest of the chapter's wrapped prose
   (mostly 70-110 characters). `make reflow CH=43` would need a clause
   inserted or the line left as is; no gate catches this either way.
3. No `[[ ]]` draft notes, no double blank line before any heading
   (every heading in this chapter uses a single blank line,
   consistently), no spaced ` -- `, and no em dash at all in this
   chapter.

## Considered and not flagged

- **"we" in the opening paragraph is absent; "I" is not.** "I have
  started to wonder whether it's actually more about 'functionality'"
  (line 6) and the rest of the opening are first-person singular, the
  author's own reflective voice, complete with the parenthetical
  "(slowly)" aside. This is not the "we"/"our" pattern the person-
  consistency rule targets, and it reads as genuine authorial voice,
  not a chatbot slip. Left alone.
- **"actually" (line 6).** On the CLAUDE.md watch list, but it draws a
  real contrast here: the sentence is pushing back against the
  chapter's own opening framing ("programming with functions") in
  favor of "functionality." Earns its place.
- **Italics on *how* and *what* (lines 65-66).** These look like
  emphasis at first, but the chapter reuses "the what" unitalicized
  later ("You described the what, not a fixed sequence of moves,"
  line 76), matching the book's first-use-then-plain convention for
  every other italicized term. Read as a legitimate first-use pair,
  not a flourish.
- **"Automatic Parallelism" section opens with "A pure function is
  automatically parallelizable"** (line 95), which echoes its own
  heading. Considered as a possible §29 fragmented header, but the
  sentence states the actual technical claim, not an empty restatement
  ("Speed matters"-style), and the next sentence immediately explains
  why. Not the tell.
- **"from a cache to a database query planner" (lines 53-54).**
  Considered as a possible §12 false range, but the two examples are
  real instances of "optimizations that skip or reuse work," not an
  invented spectrum standing in for substance. Left alone.
- **The three-sentence run "Notice there are no locks... The function
  needed no preparation... It was ready the day it was written,
  because it was pure"** (lines 138-141, after the A2 fix). Each
  sentence carries a distinct, real technical claim rather than
  padding for rhythm, and it lands as the section's payoff line. Kept,
  the same call made for a comparable closing passage in chapter 47.
- **"buy assurance at every level" (line 151) and "makes the proof
  affordable" (line 260).** "Buy" is on the CLAUDE.md watch list, but
  it is part of a deliberate cost metaphor that runs through the whole
  Assurance Spectrum section: "the cheapest rung," "buy assurance,"
  "affordable." A real, sustained device, not filler.
- **"honest" x2** ("Functional programming's honest answer," "Two
  caveats keep this honest"). Neither is the "let's be honest"
  rhetorical opener §33 targets; both are literal and support the
  chapter's actual thesis that assurance is a spectrum, not an
  overclaim.
- **"already" (line 246, "already claimed") and "never" (line 75,
  "you never see").** Both mark a real prior state or a genuine,
  literal absence, not filler.
- **"is exactly what `parallel_pure.py`'s ... already claimed" (line
  246).** Looks like the "is what" cleft, but the words after it are a
  full noun clause that the sentence can't be built without; deleting
  "is what" breaks the grammar rather than tightening it. "Exactly" is
  also earned here: it is a genuine identity claim between this law
  and the earlier `assert parallel == serial`.
- **Rule-of-three-looking lists** ("cache the call, evaluate it in any
  order, or skip a repeat"; "isinstance() tests, length checks, and
  key or index lookups"; "on any order, on any schedule, on any number
  of cores"). All are real, distinct technical items, not padding to
  hit a count of three.
- **The recurring "machine" thread** ("let the machine arrange the
  steps," "the machine searches for a counterexample," "checked by
  machine"). A deliberate callback tying declarative code, property
  testing, and formal proof together, not elegant variation.
- **No fragmented headers elsewhere.** Every other heading (Referential
  Transparency, Declarative Style, Pattern Matching as Destructuring,
  An Assurance Spectrum, Property-Based Testing) is followed directly
  by substantive content, not a restatement.

## Scan coverage

Clean on every word-level list checked: the §7 AI-vocabulary set,
§1-§6 content-padding tropes, §8 copula avoidance, §9 negative
parallelism and tailing negation, §10 rule-of-three overuse, §11
elegant variation, §15 boldface, §16 inline-header lists, §19 curly
quotes, §18 emojis, §20-§22 chatbot/servile communication artifacts,
§23-§25 filler and hedging, §27 persuasive authority tropes, §28
signposting, §31 staccato drama (beyond the one passage discussed
above), §32 aphorism formulas, §33 rhetorical openers, and CLAUDE.md's
stranded-preposition and "nothing else" rules (no hits on either). No
em dashes appear anywhere in this chapter, so §14 has nothing to
check. A rerun can skip all of the above and focus on the roundtrip
naming and the line-26 wrap length if the chapter changes.
