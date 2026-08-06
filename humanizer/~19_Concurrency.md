[[Reviewed]]
# Humanizer candidates: Chapters/19_Concurrency.md

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

This chapter is close to clean: zero em dashes anywhere in it, no curly
quotes, no promotional or notability language, and not one hit on the
§7 AI-vocabulary list. The one real pattern was person: ten sites slipped
from the book's second person into a first-person-plural "we," none of
them matching the two exceptions Bruce kept in 46/47. The rest was small
polish (two italics used for emphasis rather than term introduction, an
`is what` construction, a banned "lands" metaphor, one `in order to`)
plus two structural calls (a fragmented header, a broken parallel in a
numbered list) that were genuinely arguable.

All Tier A and Tier B edits have been applied.

## Housekeeping

1. **Semantic Line Break drift, line 1887.** Two sentences share one
   source line: `` raising `RuntimeError: Lock is not acquired.` An
   over-released `Semaphore` quietly raises its own limit instead, ``.
   The sentence boundary after `` acquired.` `` should start a new
   source line. `make reflow CH=19` fixes it (or a hand edit splitting
   at that point). Line numbers will have shifted after the edits above.

## Considered and not flagged

- **Em dashes.** None appear anywhere in this chapter, so there is
  nothing to protect and nothing to strip.
- **`only` / `never`.** Both appear often, but every instance states a
  real technical constraint (one core, one GIL, one coroutine at a
  time) rather than serving as filler emphasis. Not a cluster.
- **`already` / `even`.** Frequent but ordinary connective use, never
  piled up with other AI-vocabulary words.
- **Line 2172, "actually."** "are where STM actually succeeded" carries
  a genuine contrast against the failed attempts described just before
  it. Single instance, left alone.
- **Line 612, "has to."** "every new caller has to remember to pass it
  along" states a real necessity; not a tell, and a single instance.
- **Line 2064, "pierced to tatters."** A vivid, slightly mixed metaphor
  ("comfortable abstraction ... pierced to tatters"), but this reads as
  an authorial idiosyncrasy, specific and a little odd in the way
  genuine human writing is, not a smoothed-over AI phrase. Left alone.
- **`### Are Threads Still Necessary?` (line 1625).** The section opens
  with two sentences of real content, then a rhetorical question that
  echoes the heading, answered in the next paragraph ("It does, but
  not for the reason..."). This is a near-miss for the fragmented-header
  pattern but reads as a deliberate Socratic setup rather than a padded
  opener, so it's left alone.
- **The `Guidelines` list (2011-2049) and the concurrency-topics
  footnote list (2086-2109).** Both use bold-label list items, but
  they're genuine claims and glossary-style term definitions, not the
  mechanical "Label: filler restatement" shape §16 targets.
- **`### Why Python Has a GIL`'s opening aside (line 1027).** The
  personal PyCon reference is a specific, dated, defensible detail:
  a sign of human authorship, not AI.

## Scan coverage

Clean on: §1-2 (significance/notability puffery), §4-6 (promotional
language, vague attribution, challenges/future-outlook sections), §7
(AI vocabulary), §8-11 (copula avoidance, negative parallelism, rule of
three, elegant variation), §12 (false ranges), §15-19 (boldface
overuse, inline-header lists, title case, emoji, curly quotes), §20-22
(collaborative artifacts, knowledge-cutoff disclaimers, sycophancy),
§23-25 (filler phrases beyond the one flagged, excessive hedging,
generic positive conclusions), §27-28 (authority tropes, signposting),
§32-33 (aphorism formulas, rhetorical openers). Double blank lines
before headings, spaced ` -- `, and `[[ ]]` draft notes: none found.
Word-echo and staccato-drama scans turned up nothing beyond ordinary
variation.
