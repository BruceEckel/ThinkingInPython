# Humanizer candidates: Chapters/29_Changing_the_Interface.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied, what was declined, and what
was never flagged. This is a changelog now, not a worklist.

## Applied

Six prose edits:

- A1, "load-bearing" at line 104 replaced with what actually breaks
  ("removing it breaks the override below").
- A2, the `providing` participle tail in the Façade definition at line 6,
  split into two sentences using Bruce's wording ("This is a more
  comfortable way..."), not the drafted colon form.
- A3, the emphasis italic on *type* at line 108.
- A4, the second "already" at line 249, seven lines after the first.
- B1, the emphasis italics on *this* and *that* at line 11. Bruce's
  wording again: straight quotes rather than dropping the markup outright,
  which keeps the signal that the words stand in for nouns.
- B2, "precisely because" at line 169.

The review leaned toward keeping B1. It stayed in the file with a rewritten
PROPOSED fence, so it was applied in that form.

## Declined

Recorded so a later pass doesn't re-flag it.

- **B3**, line 201, "That is what *Façade* accomplishes." Flagged as a §29
  fragmented header restating the `## Façade` heading after its epigraph.
  Deleted from the file before hand-back. The sentence bridges the epigraph
  to the pattern name and stays.

## Housekeeping

None found, and none outstanding. No double blank lines, no `[[ ]]` draft
notes, no spaced ` -- `, no em dashes anywhere in this chapter, and no
visible Semantic Line Break drift.

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
