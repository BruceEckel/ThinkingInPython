> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/39_Pattern_Catalog.md`

Second review of this chapter.
The first (`readability/~39_Pattern_Catalog.md`) found nothing and recorded no
rejections, so nothing is carried forward.
Since then the deep review added three new pieces of prose: two sentences in the
intro paragraph, a lead-in for the new "Finding a Pattern by Problem" section,
and the whole "Patterns Python Absorbed" closing section.
Every finding below sits in that new prose.
The chapter's original fourteen lines still read clean.

---

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
> that chapter questions, so each name sits where its source puts it.
> Within each table, GoF's own order is kept for the classic patterns;
> the rest are alphabetical.
> When this book covers a pattern, its name links to that coverage.
> An unlinked name means the pattern appears only in this catalog.

Nothing else moves; this is one blank line.
Reported rather than applied because paragraph shape is your call, and because
an alternative exists: leave one paragraph and cut item 5 instead
(see the next finding), which brings it back to four jobs.

[] Reject

---

**Intro: the ordering sentence draws a distinction the reader cannot see.**

> Within each table, GoF's own order is kept for the classic patterns;
> the rest are alphabetical.

GoF's own order *is* alphabetical in all three classic tables: Abstract Factory
through Singleton, Adapter through Proxy, Chain of Responsibility through
Visitor. So the sentence sets up a contrast ("GoF's order" against
"alphabetical") that resolves to no visible difference, and a reader who checks
finds the two halves describing the same thing.

The sentence came from the deep-review block that alphabetized the six non-GoF
tables, where the point was to promise findability. That promise is worth
keeping; the false contrast is not.

Proposed change:

> Rows are alphabetical within each table,
> which for the classic patterns is also GoF's own order.

This states the reader-facing fact first and keeps the GoF observation as the
aside it actually is.

An alternative, if you would rather shorten the paragraph:

> Rows are alphabetical within each table.

I recommend the first, because "which is also GoF's own order" quietly answers
the reader who wonders whether the classic tables were reshuffled.

[] Reject

---

**"Finding a Pattern by Problem": the third clause restates the second.**

> The tables below are grouped by source.
> This one is grouped by the question you arrive with,
> for when you know the problem but not the name.

"The question you arrive with" and "when you know the problem but not the name"
say the same thing twice, the second in plainer words.
That is §70, the gloss that explains a sentence which was already clear.

The deletion test decides it: cut the third line and no information is lost.

Proposed change: drop the third line.

> The tables below are grouped by source.
> This one is grouped by the question you arrive with.

If you would rather keep the concrete phrasing and lose the abstract one, the
other direction works too, and is arguably better:

> The tables below are grouped by source.
> This one is for when you know the problem but not the name.

I slightly prefer the second: it names the reader's situation instead of
describing the table's organizing principle, and a lookup aid should be
introduced by what it is for.

[] Reject

---

**"Patterns Python Absorbed": three forms of "supply" inside four lines.**

> Python already supplies the piece they were invented to supply.

and the table's own column header directly beneath it:

> | Pattern | What Python supplies instead |

The repetition inside the sentence is deliberate and reads well: the piece they
were invented to supply is now supplied by the language, which is the argument
in miniature. Adding the column header makes three in four lines, and the third
is the one that turns a rhetorical echo into a tic.

Proposed change: leave the sentence, retitle the column.

> | Pattern | What Python gives you instead |

Alternative: leave the column and cut "already" from the sentence, which does
nothing the tense is not already doing.
I recommend the column change; "already" is carrying real timing here (the
piece exists before you write anything).

[] Reject

---

**Intro: "that chapter questions" puts two different `that`s in one clause.**

> including the [*Creational*/*Structural*/*Behavioral* split](21_The_Pattern_Concept.md#pattern-taxonomy)
> that chapter questions, so each name sits where its source puts it.

The first `that` is a demonstrative pointing back at The Pattern Concept, named
in the previous sentence. It reads for a moment like a relative pronoun
introducing "chapter questions," which briefly makes "questions" a noun.
The sentence resolves on a reread, and a sentence needing a reread is the
prose pass's definition of confusing.

The construction is right in principle: `CLAUDE.md` prefers resolving a second
nearby reference with "that chapter" rather than repeating the hyperlink.
Only the word order needs fixing.

Proposed change:

> including the [*Creational*/*Structural*/*Behavioral* split](21_The_Pattern_Concept.md#pattern-taxonomy)
> questioned there, so each name sits where its source puts it.

`questioned there` is passive, which §13 allows in technical prose when the
actor is obvious, and here the actor is the chapter named one line up.

Alternative, if you would rather keep an active verb: end the previous sentence
at the link, then start a new one.

> The tables still follow each source's own grouping.
> That includes the [*Creational*/*Structural*/*Behavioral* split](21_The_Pattern_Concept.md#pattern-taxonomy)
> that chapter questions, so each name sits where its source puts it.

Moving the demonstrative to the head of its own sentence removes the collision
without the passive. I recommend the first, which is a two-word change.

[] Reject

---

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
