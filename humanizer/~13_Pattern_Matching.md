[[Reviewed]]
# Humanizer candidates: Chapters/13_Pattern_Matching.md

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

This chapter is clean. No word-level AI vocabulary, no curly quotes,
no boldface-header lists, no sycophancy, no rule-of-three padding,
no person-consistency slips, and no em dashes to protect (the chapter
has none). What surfaced is small: two italics used for emphasis rather
than term introduction, two short-range word echoes, and one
heading immediately followed by a one-line restatement of itself. The
single largest finding is the "When Not to Match" fragmented header,
and even that is a judgment call Bruce has gone either way on before.

All Tier A and Tier B edits have been applied, along with the
Housekeeping stray-comma fix.

## Considered and not flagged

- **"and nothing else changes" (line 558).** Matches the CLAUDE.md
  exception directly: "nothing else" as a subject/object is ordinary
  English and stays. This is the same construction the rule's own
  example uses.
- **"The channels become plain data," (line 482).** "Plain" draws a
  real contrast here, data versus the behavior-carrying objects of the
  preceding OO paragraph, the same test the CLAUDE.md rule applies to
  "a plain `for` loop." Kept.
- **Asymmetric italics on "open" vs. "closed" (lines 395, 399).**
  `*open*` is italicized as a first-use technical term; its paired
  opposite "closed" two sentences later isn't. Read as an authorial
  choice (only the less obvious member of the pair gets the
  introduction), not a clear tell. Near-miss, left alone.
- **"matches any point" / "matches any `Point` instance" (lines 201,
  204).** Same verb reused to describe what two different patterns
  match. Reads as necessary technical parallelism (both sentences are
  answering "what does this pattern match"), not an accidental echo.
  Near-miss, left alone.
- **"valuable" (line 40).** On the §7 AI-vocabulary watch list, but a
  single ordinary use ("`match` becomes valuable once..."), not part of
  a cluster. Left alone per the false-positive guidance: one hit means
  nothing.
- **"Try growing the system in each direction. First, add a new
  type... Now try adding a new operation..." (lines 554-565).** Reads
  like tutorial narration but is a genuine second-person instruction to
  the reader to work through both directions of the expression-problem
  tradeoff, not a meta-announcement of what the prose is about to do.
  Left alone.

## Scan coverage

Zero hits on: §7 AI vocabulary (delve, crucial, tapestry, testament,
underscore, pivotal, etc.), copula avoidance, negative parallelisms and
tailing negations, rule-of-three padding, elegant variation, false
ranges, hyphenated-pair overuse, boldface/inline-header lists, emoji,
curly quotes, knowledge-cutoff disclaimers, sycophantic tone, filler
phrases, excessive hedging, generic positive conclusions, persuasive-
authority tropes ("at its core," "the real question"), signposting
("let's dive in"), aphorism formulas, manufactured punchlines/staccato
drama, conversational rhetorical openers, stranded prepositions, bare
"raise," and first-person-plural slips (no "we"/"us"/"our" anywhere in
the chapter). The chapter also has no em dashes at all, so there was
nothing to protect. Listing comments: the only inline comment in any
code block is `# Default` on line 27, one word, no finding.
