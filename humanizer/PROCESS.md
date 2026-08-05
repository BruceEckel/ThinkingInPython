# The humanizer pass: process and format

How to produce a `humanizer/NN_Name.md` file for one chapter.
Read this before starting. It carries the format, the accumulated
precedents from chapters 46 and 47, and the things that are off limits.

## What you are doing

Run the `humanizer` skill against one chapter of *Thinking in Python*
and write a review document that Bruce edits by deletion.
He deletes the blocks he doesn't want, hands the file back, and
someone else applies what survives.

**You do not edit the chapter.** Not one character.
Your only output is `humanizer/NN_Name.md`, matching the chapter's own
filename under `Chapters/`.
If you think a change is obviously right, it still goes in the document.

## Inputs

1. `C:\Users\bruce\.claude\skills\humanizer\SKILL.md` is the pattern list.
   It is adapted from blader/humanizer and already carries Bruce's
   local overrides. Read it in full.
2. `C:\Users\bruce\.claude\CLAUDE.md` is Bruce's writing style.
   Where it and the skill disagree, it wins. Read it in full.
3. The chapter itself, `Chapters/NN_Name.md`. Read the whole thing.
   Do not review from a partial read; findings depend on context that
   can sit hundreds of lines away.

## Hard rules

- **Never edit the chapter.**
- **Never propose a change to code inside a fenced block.** Every ```python
  block is extracted to `Examples/` and gated by the build. Statements,
  names, and structure are off limits. So are `#:` output markers and
  ```text blocks holding compiler or checker output, which must match real
  tool output verbatim.
  One exception: a `#` comment inside a listing is prose and follows the
  same rules as the surrounding text, so a watch-list word or an editorial
  "we" in a comment is a real finding. Report those in a separate
  Housekeeping item titled "Listing comments," never as a Tier A or B
  block, and note that applying one needs a re-sync (`make verify` does
  it). Never change the code the comment sits next to.
- **Never touch a `[[ ]]` draft note.** Those are Bruce's unresolved-content
  placeholders. Report one if you find it; do not rewrite around it.
- **Never remove or reword around an em dash.** He writes them as `---`
  and they are authorial. Do not treat one as evidence of AI authorship.
  You may flag a spaced ` -- ` (renders as an en dash, usually not intended).
- **Never propose a heading change.** Headings are title-case by
  convention and their anchors are gated by `heading_links.py`,
  so editing one breaks cross-references. §17 does not apply here.
  This covers the heading text itself, nothing more. Prose sitting under
  a heading, or a sentence that repeats a word the heading also uses, is
  ordinary reviewable prose: propose the edit and note that the heading
  keeps its wording. Only put the finding in Housekeeping when fixing it
  would actually require retitling.
- **CURRENT fences must be exact copies**, character for character,
  including line breaks. They are used as literal match strings when the
  edits are applied. Copy, don't retype.
- **Never invent a fact.** No claim, name, number, or reference may appear
  in a PROPOSED fence that isn't already in the chapter.

## Document format

Write `humanizer/NN_Name.md` with these sections.

    # Humanizer candidates: Chapters/NN_Name.md

    Run date: YYYY-MM-DD. Source: `humanizer` skill (blader/humanizer, adapted).

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

    [Two to six lines. What the scan found and what it didn't.
    Say plainly if the chapter is clean. Name the largest single finding.]

    ## Tier A

    ### A1 — line N — short category

    [One or two lines saying why. Not a lecture.]

    CURRENT
    ```text
    [exact copy]
    ```

    PROPOSED
    ```text
    [replacement]
    ```

    ## Tier B

    [Same block shape. Things you'd understand him declining.
    Say which way you lean and why.]

    ## Housekeeping

    [Non-humanizer findings: stray blank lines, Semantic Line Break drift,
    `[[ ]]` notes, anything structural. Numbered list, not edit blocks.]

    ## Considered and not flagged

    [Bulleted. Patterns you looked at and deliberately left alone, with the
    reason. This section is why a later pass doesn't re-litigate the same
    call, so it earns its space. Include near-misses.]

    ## Scan coverage

    [One short paragraph: which categories found nothing. Lets a rerun
    skip what has already been checked.]

If a finding covers several sites of one pattern (the classic case is
person consistency), make it one block with a row per site: a bolded
`**line N**` label, then a CURRENT fence and a PROPOSED fence, and say
"Delete individual rows you want left alone."

If a chapter is genuinely clean, say so and keep the file short.
An empty Tier A is a real and useful result. Do not pad.

## Precedents from chapters 46 and 47

These were decided with Bruce and should shape your calls.

**Applied, so propose them freely.** §28 signposting and announcements
("Let's see what happens", "The trace shows two things worth noticing").
§33 theatrical openers ("but look closer"). §31 staccato pairs. §3
participle tails. Word echoes in adjacent clauses. Emphasis italics
(see below). Broken parallels. First-person-plural slips (see below).

**Declined at least once, so mark them Tier B.** §29 fragmented headers,
where a section opens by restating its own heading. He declined this in
46 and accepted it in 47, so it is a per-instance judgment call, not a
rule. Do not treat either chapter as the precedent.

**Person.** The book is second person. Both chapters had clusters of "we"
/ "us" / "our" that were converted to "you" or to an impersonal subject.
Two exceptions survived deliberately: a genuine first person plural in an
acknowledgment ("as we created *Effect Oriented Programming*"), and one
"Let's see what happens when we don't supply" that he chose to keep.
Flag the pattern, note real exceptions, and don't assume every hit is one.

**Italics.** Only for introducing a term on first use. An italic used for
emphasis is a finding. Check the whole chapter before flagging one, since
the surrounding italics usually show which kind this is.

**The "nothing else" family** now has a dedicated rule in `CLAUDE.md`,
and chapters 01-47 were swept for it in August 2026. If you find a
surviving instance, apply the rule there rather than re-deriving it.

**Word-level scanning is usually a dead end here.** Neither 46 nor 47 had
a single hit on the §7 AI-vocabulary list, and neither had curly quotes,
emoji, boldface-header lists, promotional language, or filler phrases.
Run the checks, report that they were clean, and spend your effort on
structure: fragmented headers, announcements, echoes, parallels, person.

## Housekeeping worth reporting

- A double blank line before a heading (every other heading has one).
- Semantic Line Break drift. Prose breaks by sentence and clause, not at
  a column. `make reflow CH=NN` fixes it; no gate catches it. Report that
  it drifted, don't enumerate every line.
- A `[[ ]]` draft note.
- A spaced ` -- `.

## Finishing

Write the file and stop. Do not run `make verify`, do not sync
`Examples/`, do not touch git. Nothing you do should change any file
other than your own `humanizer/NN_Name.md`.

In your final report, give the counts (Tier A, Tier B, housekeeping),
name the single most important finding in one sentence, and say whether
the chapter was clean. Keep it under ten lines.
