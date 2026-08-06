[[Reviewed]]
# Humanizer candidates: Chapters/08_Static_Typing.md

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

This chapter is close to clean. No AI-vocabulary words, no promotional
language, no signposting, no first-person-plural slips, no em dashes to
worry about (there aren't any), no curly quotes, no emojis. The real
findings are small: one inconsistent emphasis-italic, three
already-introduced terms re-italicized in the summary table, a filler
"actually," a flourish "themselves," a redundant "and no others" tail,
and one staccato pair of matched short sentences worth merging. The
single largest finding is the summary-table italics repeating terms the
prose already used plain elsewhere (Tier A2).

All Tier A and Tier B edits have been applied.

## Housekeeping

1. Semantic Line Break drift: a handful of prose lines run 100-160+
   characters with no internal comma/colon break point to split at
   (lines 160, 194, 201, 255, 258, 266, 436). `make reflow CH=08` would
   confirm whether the tool considers these in need of a break; some
   may be left alone because the sentence has no clause boundary to
   break on.

## Considered and not flagged

- **Rule of Three lists.** Several three-item enumerations ("pass it
  to a function, store it in a variable, and call it"; "a parameter, a
  return value, or a variable"; "the public interfaces, the tricky
  data, the code on which other people depend"). Each lists genuinely
  distinct, concrete items rather than padding for the appearance of
  completeness. Left alone.
- **Italics on "narrows" (line 73) and "shape" (line 153).** Checked
  both against every other use of the word in the chapter; both are
  the true first prose use of the term, correctly italicized, and
  plain everywhere after. Not a finding.
- **"Dynamic typing and structural typing are the same idea checked at
  different moments" (line 155).** Reads like a tight rhetorical
  parallel, but it states a specific, accurate claim rather than a
  vague aphorism ("X is the language of Y"). Left alone; the following
  staccato pair (A4) is the actual finding in this paragraph.
- **"What should the type annotation be?" (line 380).** A rhetorical
  question, but a plain, single one used to set up a real problem, not
  a theatrical "Honestly?" hook. Left alone.
- **Person consistency.** No "we"/"us"/"our" anywhere in the chapter.
  Fully second person throughout. Nothing to flag.
- **Broken parallels.** Checked lists and paired clauses for mismatched
  grammatical shape; found nothing beyond the staccato pair in A4.
- **Fragmented headers elsewhere.** "Type checking discovers mistakes
  before the program runs" (Catching Mistakes), "A type parameter can
  carry a default..." (Type Parameter Defaults), "Type hints do not
  change what the program does" (Hints Are Not Enforced at Run Time),
  and "These are the type hints you will encounter..." (Type Hint
  Summary) all echo their headings somewhat, but each adds real,
  specific content in the same sentence rather than a bare restate.
  Only line 198 (B1) was close enough to the Wikipedia pattern to flag.
- **Heading "Hints Are Not Enforced at Run Time" vs. body "runtime"
  (one word).** The heading spells it as two words, the body
  consistently uses one. Headings are off limits to edit, and this is
  plausibly a deliberate title-case readability choice, not a
  consistency slip, so not flagged.

## Scan coverage

Clean on: §7 AI vocabulary (actually/enhance/delve/etc., none found
except the one flagged "actually"), promotional and advertisement
language, vague attributions and weasel words, "Challenges and Future
Prospects" formula (no such section), false ranges, sycophantic tone,
filler phrases, excessive hedging, generic positive conclusions,
hyphenated-pair overuse, curly quotes, emojis, boldface-header lists,
knowledge-cutoff disclaimers, collaborative-communication artifacts,
first-person-plural slips, and em dashes (none exist in this chapter,
so there was nothing to protect or disturb).
