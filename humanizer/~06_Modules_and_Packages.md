[[Reviewed]]
# Humanizer candidates: Chapters/06_Modules_and_Packages.md

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

This chapter is close to clean. The word-vocabulary lists (§7 AI
vocabulary, promotional language, hedging, filler phrases, rule of
three, boldface/emoji/curly-quote scans) came back with zero hits, same
as chapters 46 and 47. The one real finding is person consistency: four
"we'll"/"we" sites in the packages section break the book's second-person
voice, exactly the pattern flagged and converted in the two prior chapters.
One minor same-sentence word echo rounds out Tier A;
one milder echo in the Lazy Imports intro is Tier B.
No housekeeping issues turned up (no double blank lines, no `[[ ]]`
notes, no spaced ` -- `, and `tools/reflow_prose.py` reports zero
Semantic Line Break drift for this file).

All Tier A and Tier B edits have been applied.

## Considered and not flagged

- **Italics for term introduction.** Every italic in the chapter
  (`*module*` line 3, `*namespace*` line 26, `*qualify*` line 28,
  `*packages*` line 104, `*namespace package*` line 112) introduces a
  term on its first use in flowing prose, matching the skill's own
  exception. None are emphasis-only.
- **Bolded category headers in "File Names."** `**Modules**`,
  `**Packages**`, and `**Tests**` (lines 220, 228, 234) resemble §16's
  inline-header list on the surface, but each names a real, distinct
  category with substantive, non-circular content behind it (unlike
  the "User Experience: The user experience has been improved" pattern
  the rule targets), and they aren't formatted as bullet items. Left
  alone as a near miss, not a hit.
- **Rhetorical question opening the `PYTHONPATH` section.** "What if
  your module or package isn't placed in the same directory..." poses
  the real problem the section solves next; it isn't a "let's dive in"
  announcement or a heading restatement. Near miss on §29, not flagged.
- **Repeated technical terms** ("program"/"imports" around lines 67-69,
  "`PYTHONPATH`"/"paths" in the `PYTHONPATH` section, "dict" in the
  `globals()` paragraph, "dunder" in its own definition, "`if`" through
  the `__name__` discussion). These are proper nouns or the exact
  subject under discussion with no natural synonym; varying them would
  be elegant variation (§11), a different tell, not a fix for this one.
- **"To demonstrate" openers and the historical PYTHONPATH-to-uv
  compare/contrast.** Read at first as possible signposting or
  diff-anchored writing, but both do real teaching work (introducing a
  concrete walkthrough, contrasting a still-valid mechanism with modern
  practice) rather than announcing intent or narrating a change for its
  own sake.
- **Footnote on `__init__.py` naming (line 111).** "In hindsight, it
  might have been better..." reads as a genuine authorial aside, not
  hedging or a disclaimer.

## Scan coverage

Zero hits across: §7 AI vocabulary (crucial, delve, showcase, testament,
tapestry, etc.), §1/§2 undue significance/notability language, §4
promotional language, §5 vague attributions, §6 "Challenges and Future"
sections, §8 copula avoidance, §9 negative parallelisms/tailing
negations, §10 rule of three, §11 elegant variation, §12 false ranges,
§15 boldface overuse, §17 heading case (exempt anyway), §18 emoji, §19
curly quotes, §20-22 chatbot/sycophantic artifacts, §21 knowledge-cutoff
disclaimers, §23 filler phrases, §24 hedging, §25 generic positive
conclusions, §26 hyphenation drift, §27 persuasive authority tropes,
§28 signposting, §30 diff-anchored writing, §31 staccato drama, §32
aphorism formulas, §33 conversational openers. Em dashes: none appear
in this chapter at all (no `---`), so no em-dash calls were needed
either way.
