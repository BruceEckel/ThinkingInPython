---
name: bruce-edit-apply
description: Apply the promoted rules in `bruce_edit_db.md` to chapter prose, with per-rule firing counts and a report-first default for wide targets. Use when asked to apply Bruce's captured editing practices to a chapter or to the book. The argument names chapters by number or name, or `all` for every chapter; no argument means ask.
---

# Applying captured editing practice

`/bruce-edit-capture` induces editing practices from Bruce's own edits and
stores them in `bruce_edit_db.md`. This pass applies them.

Deducing a rule is cheap and reversible. Applying one across 47 chapters is
where the damage is, and prose damage here is invisible to tooling: `make
prose`, `banned_phrases.py`, and Vale catch none of "a half-right rule fired
on 300 sentences", and a book-wide prose diff is too large to read honestly.
The structure below exists to keep every sweep small enough to review.

## What is eligible

Apply the **Rules** section of `bruce_edit_db.md` and nothing else.
Candidates have one sighting, which is not enough evidence to rewrite prose;
Retired entries were rejected. Neither is eligible, however plausible.

A rule whose `Home` is the global CLAUDE.md watch list still gets applied
here. Sitting in a style guide loaded each session governs new writing; it
does nothing to the 47 chapters written before it existed, and this sweep is
what reaches them.

Read the rule's `Sightings` before applying it, not just its wording. The
verbatim pairs show the shape of the edit; the one-line rule is a summary and
is the part most likely to be slightly wrong.

## Scope and the report-first default

The argument names the target: a chapter number or name, several of them, or
`all`. With no argument, ask rather than guessing.

- **One to three chapters:** apply directly.
- **More than three, or `all`:** produce the report first and write nothing
  until Bruce says go. The report lists, per rule, how many sites it would
  change and in which chapters, with a sample of three actual before/after
  pairs per rule.

Never sweep the book in one pass. Go chapter by chapter, and stop at each
chapter boundary for Bruce to look at the diff. A rule that is subtly wrong
shows up in the first chapter's diff, and stopping there costs one chapter
rather than forty-seven.

**Prefer the chapter Bruce is about to edit next.** Applying there turns the
whole loop into a measurable one: his edits to that chapter score the rules
directly, and `/bruce-edit-capture` on the result says which rules were right.
Suggest this when the target is open.

## Applying a rule at a site

For each rule, at each candidate site:

1. Run the rule's **test** against that sentence. The test decides, not the
   rule's title.
2. Check the rule's **keep when** exception against that site. A rule reading
   "none seen yet" for its exception needs more care, not less: it has never
   met a case that stopped it, so it may be one site away from its first.
3. Apply only where the answer is clear. Skip where it is not, and count the
   skip. A reported skip is a finding; a forced edit is a defect.

When a rule's fix admits several reasonable wordings, make the one the
sightings show Bruce making.

## Boundaries

- **Prose only.** Fenced code blocks, `#:` output markers, and the comments
  inside listings stay untouched. A changed marker in the final diff means an
  edit strayed into code.
- **Bruce's em-dashes stay.** Rewriting a sentence around one is fine;
  deleting or replacing the dash is not.
- **Quoted material stays.** An epigraph, a quoted error message, a citation,
  and anything inside a block quote are not this pass's prose.
- **Standing records outrank rules.** Check `readability_db.md` and
  `deep_review_db.md` before editing a site. A construction recorded there as
  a standing keep was examined and kept on purpose; a rule firing on it is a
  conflict to report, not an edit to make.
- **Headings have their own rule.** Renaming one changes its pandoc anchor, so
  grep all of `Chapters/` for the old slug and fix every cross-reference.
  `heading_links.py` in `make verify` catches a missed one.

## Firing counts, and when to stop

Count every rule's firings per chapter and report them. The count is the main
signal that a rule is wrong, and it is available before Bruce reads a word of
the diff.

Stop and report instead of writing when any of these holds:

- One rule fires more than **forty** times in a single chapter.
- One rule fires more than about **fifteen times its own per-chapter average**
  in one chapter.
- One rule accounts for more than half of all edits in the sweep.

A rule that fires that often is usually stated too broadly, and the honest
move is to hand it back for narrowing rather than to apply it a hundred and
forty times and let Bruce find out from the diff.

Report the reverse too. A rule that has never fired across several sweeps is
either dead or unusably worded, and belongs in a retirement proposal to
`/bruce-edit-capture`.

If applying a rule repeatedly feels wrong at the sites, say so and stop. That
judgment is worth more than the rule, because the rule is an induction from
two examples and the sites are the population it was induced about.

## Verify

Prose edits break Semantic Line Breaks, and prose-only changes still touch
cross-references and banned phrases:

1. `make reflow CH=NN` for each chapter touched.
2. `make verify`.
3. Read `git diff Chapters/`. A changed `#:` marker means an edit reached
   code; investigate it rather than accepting it.

Then report, per chapter: the rules that fired with their counts, the sites
skipped for an exception, any conflict with a standing record, and any rule
proposed for narrowing or retirement.

Bruce reviews the diff and commits himself.
