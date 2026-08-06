[[Reviewed]]
# Humanizer candidates: Chapters/10_Cleanup.md

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

This chapter is clean. No AI-vocabulary hits, no curly quotes, no
em dashes, no italics, no first-person-plural slips, no signposting,
no forced rule-of-three, no boldface or inline-header lists. The prose
is dense technical exposition and reads that way throughout.
The largest finding is a near-verbatim word echo three lines apart
("destroyed nothing" / "destroys nothing"), an easy Tier A fix.
A second Tier A item fixes a stranded preposition in Exercise 2
under Bruce's own house style, not a humanizer category.

A2 (stranded preposition) has been applied. A1 and B1 both targeted
the same passage (the word echo); B1's full-paragraph rewrite already
resolves what A1 fixed, so B1 was applied and A1 was superseded rather
than applied on top of it.

## Housekeeping

None found. No double blank lines, no `[[ ]]` draft notes, no spaced
` -- `, and no listing comments with watch-list words or editorial
"we." The longest exercise line (134 chars, line 181) has no internal
independent-clause comma to break at, and sibling chapters (07, for
one) carry prose lines just as long, so this does not look like
Semantic Line Break drift.

## Considered and not flagged

- **First-person plural.** Zero hits on "we"/"us"/"our"/"let's."
  The chapter is consistently second-person or impersonal throughout.
- **Em dashes.** None in the chapter, so there is nothing to protect
  and nothing to flag.
- **Italics.** None in the chapter (no first-use terms are italicized
  here at all), so §_emphasis misuse_ does not apply.
- **§7 AI vocabulary** (testament, underscore, showcase, delve,
  crucial, pivotal, tapestry, vibrant, landscape, intricate, garner,
  foster, enhance, valuable, significant, robust, etc.). Zero hits,
  matching the precedent from chapters 46-47.
- **"Order" repeated across lines 69-77** (three uses describing
  finalizer ordering). Each use adds a new claim (unstable, not
  guaranteed, could differ under PyPy) rather than restating the same
  one, so this reads as necessary repetition of the topic word, not
  an echo.
- **Rule of three** ("a file, a socket, a lock," line 4). A genuine
  parenthetical list of resource examples, not a forced triad for the
  appearance of thoroughness.
- **Frequency of "so"** (9 uses as a causal connector across 186
  lines). Within normal range for causal technical exposition; no
  cluster suggests uniform AI cadence.
- **CLAUDE.md watch list** (is what, nothing else/more/but, does it,
  ever, only, exactly, has to, actually, itself, was to, plain,
  promise, reach for, bare "raise"). Grepped for all; the only "plain"
  hits (lines 163, 175) draw a real contrast against the weak-reference
  registry and are legitimate under the rule.
- **Exercise imperatives.** Read against the "no imperative-plus-
  consequence" rule; all four are real instructions to the reader
  ("change," "replace," "add"), not hypothetical-then-consequence
  constructions, so none needed rewording.

## Scan coverage

Clean on: §1-2 significance/notability inflation, §4-5 promotional
language and vague attribution, §6 outline-style challenges sections,
§8 copula avoidance, §9 negative parallelism, §10 rule-of-three
overuse, §11 elegant variation, §12 false ranges, §15 boldface
overuse, §16 inline-header lists, §17 heading case (not applicable to
book headings anyway), §18 emoji, §19 curly quotes, §20-22
collaborative/sycophantic/cutoff-disclaimer artifacts, §23-25 filler
and hedging, §26 hyphenated pairs, §27 authority tropes, §28
signposting, §29 fragmented headers (only one body heading, not
fragmented), §30 diff-anchored writing, §31 staccato drama, §32
aphorism formulas, §33 rhetorical openers. Person, italics, and em
dashes were checked and are non-issues for the reasons above rather
than absent categories.
