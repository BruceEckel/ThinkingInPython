> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/39_Pattern_Catalog.md`

Second review of this chapter.
The first (`readability/~39_Pattern_Catalog.md`) found nothing and recorded no
rejections, so nothing is carried forward.
Since then the deep review added three new pieces of prose: two sentences in the
intro paragraph, a lead-in for the new "Finding a Pattern by Problem" section,
and the whole "Patterns Python Absorbed" closing section.
Every finding sat in that new prose.
The chapter's original fourteen lines still read clean.

The clear-cut fixes were applied to the chapter directly (listed below);
one block remains for your judgment.

## Applied directly

- Ordering sentence: "Within each table, GoF's own order is kept for the
  classic patterns; the rest are alphabetical." → "Rows are alphabetical
  within each table, which for the classic patterns is also GoF's own
  order." (GoF's order *is* alphabetical in all three classic tables, so the
  old sentence set up a contrast that resolves to no visible difference; the
  new one states the reader-facing fact first and quietly answers whether
  the classic tables were reshuffled).
- "Finding a Pattern by Problem" lead-in: "This one is grouped by the
  question you arrive with, for when you know the problem but not the name."
  → "This one is for when you know the problem but not the name." (§70: the
  two halves said the same thing; the kept half names the reader's situation,
  which is what a lookup aid should be introduced by).
- "Patterns Python Absorbed" column header: "What Python supplies instead" →
  "What Python gives you instead" (three forms of "supply" in four lines;
  the sentence's own echo is deliberate and stays, including its "already,"
  which carries real timing).
- Intro: "the *Creational*/*Structural*/*Behavioral* split that chapter
  questions" → "questioned there" (the demonstrative "that" read for a
  moment as a relative pronoun, making "questions" a noun; the passive is
  fine here because the actor is the chapter named one line up).

***

**Intro, second paragraph: it now does five jobs in thirteen lines.**

The paragraph was already carrying three ideas, and the deep review added two
more. It now runs:

1.  what an entry gives you,
2.  that listing is not endorsement, and why,
3.  that this book argues many are unnecessary,
4.  how the tables are grouped, and why, despite chapter 21,
5.  how rows are ordered inside a table,
6.  what a link and a missing link mean.

Items 1 to 3 tell the reader how to take the catalog.
Items 4 to 6 tell them how to read it.
Those are two different jobs, and one paragraph doing both is the
paragraph-length uniformity problem in reverse: a single block where the reader
needs a breath.

Proposed change: break it after the chapter-21 sentence, so the second
paragraph becomes the caveat and the third becomes the reading instructions.

> The body of this book argues that a number of them are unnecessary in Python
> ([The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves) says why).
>
> The tables still follow each source's own grouping,
> including the [*Creational*/*Structural*/*Behavioral* split](21_The_Pattern_Concept.md#pattern-taxonomy)
> questioned there, so each name sits where its source puts it.
> Rows are alphabetical within each table,
> which for the classic patterns is also GoF's own order.
> When this book covers a pattern, its name links to that coverage.
> An unlinked name means the pattern appears only in this catalog.

(The quoted lines reflect the sentence fixes already applied above.)
Nothing else moves; this is one blank line.
Reported rather than applied because paragraph shape is your call.

[] Reject

***

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables. The new
  prose introduced none.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes anywhere in the file, and no spaced ` -- `.
- No curly quotes. The only non-ASCII character in the file is the `ç` in
  Façade, which is correct.
- No boldface, emojis, slot-fill placeholders, or chatbot artifacts.
- The new closing line, "What survives the subtraction is the intent, not the
  structure," has the shape of a §32 aphorism, but it is a near-verbatim
  callback to chapter 21's own "it is usually the intent rather than the
  structure," and it names a claim the table above it just demonstrated nine
  times. Deliberate echo, not a manufactured punchline. Not flagged.
- "Several entries above are in the catalog because the literature documents
  them, not because you need to write them" is a §9 negative parallelism by
  shape. Both halves carry distinct information and the contrast is the
  section's actual thesis. Not flagged.
