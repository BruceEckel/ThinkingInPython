[[Reviewed]]
# Humanizer candidates: Chapters/05_Functions.md

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

This is a short, clean chapter. Two structural findings, both in
the "propose freely" precedent categories (word echo and staccato
triplet), plus one listing-comment grammar nit and one line-break
drift. No AI-vocabulary hits, no curly quotes, no boldface abuse,
no person problems, no filler phrases. The largest finding is the
"Keyword arguments... Keyword arguments..." subject echo that opens
the Default and Keyword Arguments section.

Both Tier A edits and the listing-comment Housekeeping fix have been
applied (the latter needs `make sync` to reach `Examples/`).

## Housekeeping

1. **Semantic Line Break drift, line 258:** the sentence
   `Calling `make_user("Sue", True)` is an error, because `admin`
   is keyword-only.` sits on one line, while its structural twin two
   lines above (`Calling `divide(a=10, b=2)` is an error, / because
   `a` and `b` are positional-only.`) breaks at the same comma.
   `make reflow CH=05` would even the two out.

## Considered and not flagged

- **Person.** No "we"/"us"/"our" anywhere in the chapter; it stays
  consistently second person and imperative. Nothing to convert.
- **Em dashes.** None present, spaced or otherwise. Nothing to
  preserve, nothing to flag.
- **Italics.** Exactly two uses, `*positional-only*` and
  `*keyword-only*`, both first-use term introductions per the rule.
  No emphasis-italic misuse.
- **AI vocabulary (§7 list).** Zero hits on a direct grep
  (crucial, delve, showcase, tapestry, testament, underscore,
  pivotal, vibrant, etc.).
- **Curly quotes, boldface, inline-header lists, emojis.** None
  found anywhere in the chapter.
- **Rule of Three (§10).** No forced triads; lists in this chapter
  are two items or genuinely as many as the content needs
  (e.g. the three parameter-marker sentences in the Positional-Only
  section explain three distinct, non-redundant facts).
- **The "Calling X is an error, because Y is Z-only" pair (lines
  256-258).** A deliberate, matching parallel that mirrors the two
  marker rules being taught side by side. This is good pedagogy, not
  a broken-parallel tell, so it's left alone apart from the one
  line-break inconsistency already logged in Housekeeping.
- **Other section openers** (Variable Argument Lists, Unpacking
  Arguments, Positional-Only and Keyword-Only Parameters, Lambdas).
  Each opens with a substantive definition or claim, not a vapid
  restatement of its own heading, unlike the Default and Keyword
  Arguments opener flagged in A1.
- **"self-documenting" / "self-describing" (lines 69, 145).** Fixed
  technical compounds, not instances of hyphenated-pair overuse;
  left alone.
- **The "nothing else" family.** No instances in this chapter.

## Scan coverage

Clean with zero hits: AI vocabulary (§7), promotional/notability
language (§1-§5), outline-style "Challenges" sections (§6), negative
parallelisms and tailing negations (§9), false ranges (§12), passive
subjectless fragments (§13), boldface (§15), inline-header lists
(§16), emojis (§18), curly quotes (§19), collaborative/sycophantic
artifacts (§20, §22), knowledge-cutoff disclaimers (§21), filler
phrases and hedging (§23-§24), generic positive conclusions (§25),
persuasive-authority tropes (§27), signposting (§28), aphorism
formulas (§32), conversational rhetorical openers (§33), and
first-person-plural slips. Structural review (echoes, staccato runs,
fragmented headers, parallels) is where both real findings surfaced;
a re-run can skip straight to spot-checking A1/A2's resolution and
the remaining Housekeeping item.
