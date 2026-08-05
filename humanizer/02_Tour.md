[[Reviewed]]
# Humanizer candidates: Chapters/02_Tour.md

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

This chapter is close to clean. It has no em dashes at all (not even
authorial ones), no curly quotes, no boldface-header lists, no AI
vocabulary hits, no signposting, no fragmented headers, and no person
slips ("we"/"our"/"us" never appear; the chapter is consistently
second person). The one real finding is a textbook case of the "is
what" cleft the style guide calls out by name. A code comment has a
tailing-negation fragment worth a Housekeeping note. Everything else
that looked promising on a first pass (parallel constructions,
short-sentence pairs, a relative clause attributing significance)
held up as legitimate technical prose on a closer read.

## Tier A

### A1 — line 342 — "is what" cleft

Deleting "is what" leaves the same meaning with a verb right after it
("reports"), the exact pattern `CLAUDE.md` names for cutting.

CURRENT
```text
An `Interpolation` also remembers the source text of the expression that produced it,
which is what `piece.expression` reports.
```

PROPOSED
```text
An `Interpolation` also remembers the source text of the expression that produced it,
which `piece.expression` reports.
```

## Tier B

None. Nothing else in this chapter cleared the bar for a genuinely
arguable finding; see "Considered and not flagged" for the near-misses.

## Housekeeping

1. **Listing comment** (line 108, `multiple_assignment.py`): the
   comment `# Swap, no temporary needed` is a tailing-negation
   fragment ("no X needed" tacked on rather than written as a clause,
   §9). A plainer form would be `# Swap without a temporary`. This is
   inside a fenced Python block, so applying it needs a re-sync
   (`make verify` does it); the code itself is unchanged.

## Considered and not flagged

- **"Assignment binds a name. It does not copy."** (lines 74-75) is a
  short-sentence pair, but only two, and they carry real conceptual
  weight (the name/copy distinction the rest of the section depends
  on) rather than manufacturing drama. The "signs of human writing"
  guidance flags staccato only at "several fragments in a row"; two
  plain declaratives making one point don't clear that bar.
- **"The language aims to aid you as much as possible. It tries to
  hinder you as little as possible."** (lines 12-13) is an intentional
  antithetical parallel (aid-as-much / hinder-as-little), not a broken
  parallel and not padding. Left alone.
- **"The language forces everyone to indent code the same way, which
  is one of the main reasons for Python's consistent readability."**
  (lines 64-65) has the shape of an §1 significance-emphasis tail, but
  the claim is specific and defensible (forced indentation really is
  a commonly cited reason for cross-codebase readability in Python),
  not a vague "marks a pivotal moment" flourish. Left alone.
- **"# A 31-digit int, no overflow"** (line 141, `numbers.py`) has the
  same "no X" shape as the flagged listing comment above, but it
  reports a concrete fact directly tied to the surrounding prose
  ("Integers have unlimited precision, so they never overflow"),
  not a marketing-style reassurance. Left unflagged; close enough to
  the flagged comment that a re-read is worth it if this chapter is
  revisited.
- **"Examples often include Python-esque references."** (line 266)
  reads a little generic in isolation but does real work: it explains
  why the surrounding examples quote Monty Python. Not signposting or
  filler.
- **Rule-of-three-shaped lists** throughout (the format-spec trio
  "width, precision, and alignment," the naming-convention categories,
  the triple-quote use cases "an embedded template, a SQL query, or a
  chunk of HTML") were checked against §10. Each names three genuinely
  distinct, real things rather than padding a list to look thorough.
- **Fragmented headers (§29)** were checked at every heading. None of
  this chapter's headings are followed by a generic restating sentence
  before the real content; the first sentence under each heading is
  already substantive.
- **Italics** (*dynamic typing*, *immutable*, *mutable*, *truthiness*,
  *f-strings*) were all checked against the first-use rule. Every one
  introduces a term at its first occurrence; none is used for bare
  emphasis.

## Scan coverage

Clean on: em dashes (none in the chapter, so nothing to flag either
way), spaced ` -- `, curly quotes, emoji, boldface-header lists,
inline-header vertical lists, promotional/AI-vocabulary word list
(§7), vague attributions, "challenges and future prospects" sections,
false ranges, hedging, generic positive conclusions, hyphenated-pair
overuse, aphorism formulas, conversational rhetorical openers,
collaborative-communication artifacts, knowledge-cutoff disclaimers,
person consistency (no "we"/"our"/"us"), and `[[ ]]` draft notes (none
present). Structural checks (fragmented headers, broken parallels,
staccato runs, significance-tail clauses, listing comments) were done
by hand across the whole chapter, not by keyword search.
