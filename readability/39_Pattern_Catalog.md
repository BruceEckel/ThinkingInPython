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

Every finding was resolved directly and applied (listed below).
No blocks remain.

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
- Intro, second paragraph: broken after the chapter-21 sentence (one blank
  line, nothing else moves). The paragraph was doing five jobs in thirteen
  lines; the break separates how to take the catalog (entries, endorsement,
  the book's argument) from how to read it (grouping, ordering, links).

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
