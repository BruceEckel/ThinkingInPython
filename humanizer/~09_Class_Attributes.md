[[Reviewed]]
# Humanizer candidates: Chapters/09_Class_Attributes.md

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

Short chapter, mostly clean. Two real findings: one first-person-plural
slip in second-person prose, and two uses of "promise" as a metaphor for
an annotation's declaration, which is a word Bruce's style rules ban
outright. One mild announcement-style lead-in into the first example is
arguable. No word-vocabulary hits, no curly quotes, no boldface lists, no
fragmented headers, no SLB drift, no double-blank-heading issue. The
largest single finding is the "promise" metaphor: it appears twice,
describing the same idea (a bare annotation's declared-but-unset type),
so both sites should probably move together.

All Tier A and Tier B edits have been applied.

## Housekeeping

None found. No `[[ ]]` draft notes, no spaced ` -- `, no curly quotes, no
stray em dashes, no trailing whitespace. Heading spacing is a single
blank line before each `##`, which matches neighboring chapters (08, 10),
so it is not drift. Ran `tools/reflow_prose.py --diff` against the
chapter directly (read-only, no `--write`): zero paragraphs changed, so
no Semantic Line Break drift despite a few individual lines running past
80 characters, since those lines are single clauses with no internal
comma left to break on.

## Considered and not flagged

- **"actually" (lines 99, 132, 236).** Each draws a real contrast: what
  `display_object()` shows versus what you'd expect to be there, what an
  annotation states versus what actually gets set, what an assignment
  seems to do versus what it actually creates. This chapter's whole
  point is exactly this kind of surprise, so the word is earning its
  place each time, not padding.
- **"only" (lines 107, 144, 186).** All restrictive ("only records,"
  "only way," "only tells"), not intensifiers. Cutting them would change
  the meaning, so they stay.
- **Italics (lines 7, 14, 123).** `*class attribute*`, `*shadows*`,
  `*bare annotation*` are each the first use of a new term, per
  convention. No emphasis-only italics found in the chapter.
- **"tells a different story" (line 113).** A near miss: a small bit of
  personification could read as a "manufactured punchline," but it's a
  single instance, not a run of them, and the surrounding prose is
  otherwise precise and technical. Left alone.
- **Word echo, "shows" / "showed above" (lines 99, 102).** Both refer to
  the same demonstrated fact across two examples; a legitimate
  cross-reference, not repetition for its own sake.
- **Passive constructions (e.g. line 144, "an attribute is set from
  outside the class").** Advisory only per the local override; each
  keeps the actual subject (the attribute, the class) in focus rather
  than hiding an actor the reader needs.

## Scan coverage

Clean on: AI vocabulary (§7), copula avoidance (§8), negative
parallelism and tailing negation (§9), rule-of-three (§10), elegant
variation (§11), false ranges (§12), boldface overuse (§15),
inline-header vertical lists (§16), emojis (§18), curly quotes (§19),
collaborative-communication artifacts (§20), knowledge-cutoff
disclaimers and speculative gap-filling (§21), sycophantic tone (§22),
filler phrases (§23), excessive hedging (§24), generic positive
conclusions (§25), hyphenated-pair overuse (§26), persuasive-authority
tropes (§27), fragmented headers (§29), diff-anchored writing (§30),
staccato/manufactured-punchline runs (§31), aphorism formulas (§32), and
conversational rhetorical openers (§33). Person consistency and the
"promise" metaphor are the only structural hits.
