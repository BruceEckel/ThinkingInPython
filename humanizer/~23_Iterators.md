[[Reviewed]]
# Humanizer candidates: Chapters/23_Iterators.md

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

This chapter is close to clean. The word-level AI-vocabulary list,
boldface lists, curly quotes, emoji, hedging, rule-of-three, signposting,
fragmented headers, aphorism formulas, false ranges, and em-dash misuse
all came back empty. Two real findings: a single first-person-plural
slip ("we force"), and two spots where italics mark emphasis rather
than a first-use term, one of them a matched pair in the same sentence.
The largest finding was the "we" at line 421, the only person slip in
the whole chapter.

All Tier A and Tier B edits have been applied.

## Housekeeping

None found. No double blank line before a heading, no `[[ ]]` draft
note, no spaced ` -- `, and no em dash at all in this chapter (author
or otherwise) to accidentally disturb.

## Considered and not flagged

- **"infinite" italicized at line 112.** Read this as a first-use term
  introduction, matching the chapter's own pattern for *iterator*,
  *iterable*, and *generator*: italicized once, then used plain in
  every later occurrence (lines 324, 326, 344, 345, 349, 353, 355,
  410). Unlike the "skips"/"stops" pair, there is no earlier plain use
  that would mark it as emphasis instead.
- **"*GoF Design Patterns*" at line 497.** This is a book title, not a
  term introduction; italics are the ordinary convention for a title
  and unrelated to the A2 finding two paragraphs later.
- **"The protocol is free, and quiet." (line 657).** A single short
  closing sentence ending a section. The false-positive guidance
  explicitly protects one clipped sentence used to land a point; this
  is that, not a run of them.
- **Four-sentence run at lines 578-581** ("Look at the last line of
  output." through "It rebuilt the list."). Considered as a possible
  staccato-drama cluster (§31), but each sentence has a full
  subject and verb, none are the clipped noun-fragments the skill's
  example shows ("No aesthetic prior. No nostalgia for human taste."),
  and the pacing matches the book's terse house style elsewhere. Not
  flagged as a cluster; see B1 for the narrower call on the last two
  sentences alone.
- **"has to" at lines 590 and 634.** On the CLAUDE.md watch list, but
  both uses are literal necessity claims about what the code must do,
  not filler modality. Reads the same with or without more direct
  phrasing; not worth the churn.
- **`# noqa` comment at line 259 ("Spelled out").** Checked all inline
  `#` comments in every listing for editorial "we" or watch-list words.
  All are terse and factual; none qualify for the Listing Comments
  housekeeping category.

## Scan coverage

Zero hits on: the full §7 AI-vocabulary list, copula avoidance (§8),
negative-parallelism formula and tailing negations (§9) other than the
B1 borderline, rule-of-three (§10), elegant variation (§11), false
ranges (§12), boldface overuse (§15), inline-header lists (§16), title
case (n/a for book headings), emojis (§18), curly quotes (§19),
collaborative artifacts (§20), knowledge-cutoff/speculative filler
(§21), sycophancy (§22), filler phrases (§23), excessive hedging (§24),
generic positive conclusions (§25), hyphenated-pair overuse (§26),
persuasive-authority tropes (§27), signposting/announcements (§28),
fragmented headers (§29), diff-anchored writing (§30), and aphorism
formulas (§32). No em dash, spaced en dash, or `[[ ]]` note anywhere in
the file. Person consistency and italics-for-emphasis were the only
categories that found anything.
