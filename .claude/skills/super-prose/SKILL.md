---
name: super-prose
description: Run every prose pass over a chapter or one section of it, in order, and commit the result. The eleven passes are literal, positive, straighten, cohesion, antecedents, ambiguity, activate, bruce-edit-apply, elements-of-style, alternative, and stutter, each read from its own SKILL.md and applied in one read of the prose. Use when asked for "all the prose passes", "the prose reviews and corrections", or "/super-prose" on a chapter or a section. The argument names the chapter by number or name, optionally followed by `section "<heading>"`; no argument means the chapter whose editing pass is open.
---

# Super-prose: the eleven prose passes as one request

`/super-prose 45` or `/super-prose 45 section "The Driver's Exception Channel"`
means: apply every prose pass the project defines, over that scope,
in the order below, in one session, and commit.
It is the in-session form of `tip rewrite CH=NN`, which runs the
passes headless, one model call per pass, over a whole chapter.
This form keeps the conversation's context (what Bruce has already
ruled on, the listing just edited) and can scope to one section,
which `tip rewrite` cannot.

## The order

Load all eleven skills with the `Skill` tool before touching the
prose, then read the scope once and apply them together.
The order is the order the skills' own boundary notes give:
each pass hands the next one less to do.

1. `literal`: a figure or a vague description becomes the mechanism.
2. `positive`: a negation that is an accident of phrasing turns around.
3. `straighten`: a buried actor, a subject held open, an overloaded
   sentence, a colon or "and" carrying a second claim.
4. `cohesion`: old before new, one topic string per paragraph, R29's
   one primary concept per paragraph.
5. `antecedents`: every pointer with two candidates gets its noun.
6. `ambiguity`: every sentence that counts, compares, coordinates,
   modifies, or limits keeps one reading: a count with two units, a
   word with two senses, a modifier with two heads, an open scope, a
   definite noun the listing has several of, a missing comparand.
7. `activate`: passives with a natural actor, nominalizations,
   metadiscourse, empty frames, tense drift.
8. `bruce-edit-apply`: the Rules section of `bruce_edit_db.md`.
9. `elements-of-style:writing-clearly-and-concisely`: Strunk's rules,
   mostly needless words and emphatic words at the end.
10. `alternative`: a sentence in a listing walkthrough that describes
    the road not taken in the walkthrough's own register ("A `for`
    loop treats `StopIteration` as the normal end of the loop" under
    a `try`-driven listing; "`C().show()` then runs `B`'s version"
    after a framed opener) gets the lightest frame that carries over
    ("In that version", "If `__init__()` assigns `_value_`"), R57.
    It runs after the passes above because a split or a reframed
    sentence can strand an alternative's continuation from its
    opener, and before `stutter`, since a frame is new words.
11. `stutter`: a word beside its own code-span form ("The next
    `next()`"), one verb said of two things in a sentence, a prose
    noun and a code variable of one spelling naming different things.
    It runs last because the ten passes above write new sentences,
    and a rewrite can put a word beside its code span.

## Before the read

Run the survey tools over the chapter and keep the hits inside the
scope's line range:

- `tip negatives CH=NN` (for `positive`)
- `tip pointers CH=NN` (for `antecedents`)
- `tip positional CH=NN ARGS=--survey` (for `ambiguity`: `count+unit`,
  the survey hits on `call` and `time`, `construct xN`, `ordinal+span`;
  for `alternative`: `survey alternative`, a sentence in a walkthrough
  paragraph naming a construct the listing lacks with no marker word,
  the opener shape only; the continuation shape is read by hand)
- `tip sentence-shapes CH=NN ARGS=--survey` (for `straighten` and
  `cohesion`: `[AND]`, `[COLON]`, `[ADD]`, `[TWO]`, `[CAN]`, `[SAME]`,
  and the default `[PRT]`, a phrasal verb split around a noun phrase,
  "carries the request out" -> "carries out the request", R56;
  `ambiguity` reads `[SAME]`, `[PAIR]`, `[TWO]`, and `[AND+REL]` too,
  and `[SAME+NEW]`, a "same" on a noun the 30 lines above never use,
  "`safe()` uses the same separation" -> "`safe()` checks each value
  while it is still separate from the literal text", R63; the survey
  prints only the `[ADD]`, `[CAN]`, `[SAME]`, `[SAME+NEW]`, and `[TWO]`
  hits not yet judged, with `[AND]` and `[COLON]` in full, and a read
  keep goes into the survey baseline with
  `tip sentence-shapes CH=NN ARGS=--survey-accept`; `activate` reads
  `[CAUS]`, a causative with the actor in object position, R61, judged
  the same way)
- `tip watch-words CH=NN` (for `ambiguity`: `however`, Tier 2 since
  2026-11-08, the concessive "however many" that reads first as a
  contrast and is a universal over a count or a manner, R58; the
  contrastive "However," is skipped; `ARGS="--tier 1"` adds the
  negated subjects; for `literal`: `draws` with an exception or a
  diagnostic as its object, Tier 2 since 2026-11-09, "A `yield`
  inside a `finally` clause draws the same `RuntimeError`" -> "If a
  generator yields inside a `finally` clause, `close()` raises a
  `RuntimeError` with the
  message shown for `stubborn()`", the actor named with the verb the book
  taught, raises or reports, R62)
- `tip past-tense CH=NN ARGS=--survey` (for `activate`: `[PAST-SUB]`,
  and `[PERFECT]`, a present perfect in a time clause, "before the
  generator has yielded" -> "before the generator yields", C57)
- `tip stutter CH=NN` (for `stutter`: `[CODE!]`, `[CODE]`, `[STEM~]`,
  `[STEM=]`, and `[MIXED]`, one spelling in prose and in a code span
  in one paragraph; no baseline, so every hit prints, and most are
  keeps: the 2026-11-07 sweep reworded 56 of 1,311, and the `[MIXED]`
  survey that day found 5 in 177; run it again over the scope after
  the other passes' edits, since they can create the shape)
- `tip overclaims CH=NN ARGS=--survey` (for the claim check every
  pass makes: `[LEAD]`, a list lead-in that bounds every item above
  an item that exempts itself, "Each approach gives up one side's
  loop:" over "The list keeps both loops", 2026-11-07; it prints
  only lead-ins not yet judged, and a read keep goes into its own
  baseline with `tip overclaims CH=NN ARGS=--survey-accept`)

Read `deep_review_db.md` and the chapter's most recent
`deep_review/~NN...` file for standing exemptions, and the Rules
section of `bruce_edit_db.md` for the rules in force.

## Scope

A section runs from its heading to the next heading of the same or
a higher level.
Edit prose only: fenced blocks, `#:` markers, quoted material, and
headings stay, and a heading changes only when the section is being
restructured anyway, with every link to its anchor updated.
Every claim a rewrite touches is checked against the listing it
describes before the new sentence is written.
Bruce's "we" and his em-dashes stay.

## After the edits

1. `uv run tip verify-ch CH=NN` (reflows, syncs, gates).
2. `uv run tip prose CH=NN`: read each `NEW` and each `stale` pair.
   A `NEW` hit on a sentence the pass wrote is a sentence to fix or a
   keep to accept; a `stale` entry paired with a `NEW` whose flagged
   word is unchanged is a re-keyed keep, accepted with the scoped
   `tip <check>-accept CH=NN`.
3. The survey rules with a judged list, `[ADD]`, `[CAN]`, `[CAUS]`,
   `[SAME]`, `[SAME+NEW]`, `[TWO]`, and `[LEAD]`: run
   `tip sentence-shapes CH=NN ARGS=--survey` and
   `tip overclaims CH=NN ARGS=--survey` again. A kept sentence the
   pass edited prints as `survey` beside its `stale` entry, so reread
   it. Then record the keeps with `ARGS=--survey-accept` on each. The
   accept takes in every unjudged hit in the chapter and its Solutions
   file, so a pass over one section reads the hits outside its
   section before accepting.
4. Read `git diff Chapters/`: a changed `#:` marker means an edit
   strayed into code.
5. Commit the chapter and any baseline files together, one commit,
   with the message listing the passes and what each changed
   (per [[commit-without-asking]], Bruce pushes).

## Report

One paragraph per pass that changed something, with before/after
pairs for the figures replaced, the sentences split, the pointers
named, the sentences cut and why, and the paragraphs split.
Name the passes that found nothing.
List the hits kept and baselined, with the reason each is the claim.
