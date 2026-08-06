[[Reviewed]]
# Humanizer candidates: Chapters/25_Template_Method.md

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

This chapter is close to clean.
The word-level scan (§7 AI vocabulary, hedging, filler, rule of three,
aphorism formulas, curly quotes, emojis, boldface lists) found nothing.
There are no em dashes at all in the file, no `[[ ]]` draft notes,
and no double-blank-line drift.
The one real finding is an italic used for emphasis rather than to
introduce a term, on `*shape*` at line 19, and it stands alone: nothing
else in the chapter needed a second look after it.

## Tier A

### A1 — line 19 — italic used for emphasis, not term introduction

`*Template Method*` (line 5) and `*Hollywood Principle*` (line 73) are
both italicized on first use and never again, the correct pattern.
`*shape*` breaks that pattern: it isn't a named term, and the same word
recurs unitalicized at line 140 ("still fits the algorithm's shape"),
which is the giveaway that the first instance was emphasis, not a
definition.

CURRENT
```text
The defining trait of a Template Method is that the base class fixes the *shape* of the algorithm.
```

PROPOSED
```text
The defining trait of a Template Method is that the base class fixes the shape of the algorithm.
```

## Tier B

None. Nothing else surfaced was strong enough to include without
padding the section; see below for the near-misses and why they were
left out.

## Housekeeping

None found. Blank-line spacing before headings, Semantic Line Breaks,
and the listing comments inside all four ```python blocks (checked all
six comments) are all clean.

## Considered and not flagged

- **"At the heart of a framework is the *Template Method*" (line 5).**
  Superficially resembles a §1 significance flourish
  ("stands as," "serves as," "represents a shift"),
  but it states a literally true structural fact about how a Template
  Method sits in a framework, appears once, and isn't clustered with
  other flourish language. Left alone.
- **"don't call us, we'll call you" (lines 73-74).**
  Reads as first-person plural, but it's the idiomatic wording of the
  Hollywood Principle itself, quoted content rather than the author's
  voice slipping into "we." Falls under the secondhand-text exception,
  not the person-consistency pattern.
- **"engine" reused verbatim across the chapter** (lines 62, 91, 95,
  127-129: "starts the engine," "the engine runs," "the engine calls").
  This is the opposite of elegant variation: the same word every time,
  which is the human-natural choice, not the AI tell. Left alone.
- **`*shape*` recurring unitalicized at line 140.**
  Considered fixing the inconsistency by italicizing the second
  occurrence instead of de-italicizing the first, but line 19 is the
  one that reads as emphasis, and "shape" is never established as
  chapter terminology anywhere else. The fix goes the other direction
  (see A1).

## Scan coverage

Checked and clean: the full §7 AI-vocabulary list (delve, crucial, key,
landscape, showcase, tapestry, testament, underscore, vibrant, etc.),
curly quotes, emoji, boldface-header lists, hedging (§24), filler
phrases (§23), rule-of-three (§10), false ranges (§12), aphorism
formulas (§32), manufactured punchlines (§31), conversational
rhetorical openers (§33), collaborative-communication artifacts (§20),
knowledge-cutoff disclaimers (§21), hyphenated-pair overuse (§26), and
"Challenges"/"Future Outlook" outline sections (§6). Em dashes: none
exist in this chapter at all, spaced or otherwise. Fragmented headers
(§29): both section openers were checked against their headings and
neither restates one. Person consistency: one "we" hit, addressed
above as a quotation, not a slip. Semantic Line Breaks: spot-checked
throughout, breaks consistently land on sentence and clause
boundaries. Listing comments inside the four ```python blocks: all six
read clean, no watch-list words, no editorial "we."
