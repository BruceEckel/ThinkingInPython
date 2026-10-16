When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability sweep of `Chapters/21_Patterns--Design_Patterns.md`, 2026-10-16.
The chapter has been through many passes and carries few AI-writing tells:
no Tier 1A vocabulary, no curly quotes, no spaced ` -- `,
and the watch-list words that remain are reflexive or temporal uses the
`readability_db.md` keeps cover.
One fix was applied directly.
One block asks whether a first-edition closing sentence still fits the list it closes.
The rest are recorded as declined.

## Applied directly

- Line 506-507 (Orthogonality bullet), global rule on "and" joining clauses with different subjects:
  "...in the same place, and changing a tightly coupled part means..." -> two sentences,
  "...in the same place. Changing a tightly coupled part means...".
  Each clause is a separate claim about one side of the low-coupling, high-cohesion pair,
  and "whereas" would fit where the "and" sat.

## Line 554, after the Design Principles list: §25 generic closer

> You can hold this handful of fundamental ideas in your head while analyzing a design.

This sentence dates from the first edition (it predates the 2026-07-10 move to `Chapters/`).
Two things make it read as a send-off rather than a claim.
The list above it now holds fourteen principles, more than a handful.
And the paragraph before the list says "The list is a reference",
which pulls against "hold ... in your head".
Proposed: cut the sentence, so the section ends on its last principle
and the "reference" framing stands alone.
The alternative, if the sentence is deliberate voice, is to keep it and change "handful" to "set".

[] Reject

## Considered and declined

- Line 8, "an important step forward in object-oriented design": unsupported significance by shape (§1).
  Kept under `readability_db.md`, where 21's superlative rides on the Factory precedent
  and was confirmed on the 2026-10-04 Sweep Decisions page.
- Line 50, "One of the most compelling motivations": a single Tier 3 word in first-edition voice.
- Line 60-61, "A good abstraction does more than hide those details. It erases them.":
  a negative-parallelism beat by shape (§9, §31).
  Kept: the hide/erase distinction is the paragraph's subject,
  and the next sentence ("cannot recover information the boundary discards") cashes it out.
- Line 82, "the focal point around which to structure your design": a §1 watch word, the only one, in first-edition voice.
- Line 84-85, "You discover a vector of change. You do not predict it.": a short contrast beat among longer sentences, not a staccato run.
- Line 138, "The stages are a history, not a ranking.": aphorism shape (§32), but it states a real claim the next sentence acts on.
- Line 198, "a case with a real motivation": §34, with the contrast named (this listing's `max()`/`sum()` shape, which "Nobody designs ... around").
- Line 250, "Certainly, the *Creational* patterns are straightforward.": the chapter's only §42 cue, in a first-person passage; a `readability_db.md` keep.
- Line 258, "(I'll readily admit that I may be missing something here)": a genuine self-correcting aside, a sign of human writing.
- Line 291, "Read this way, the catalog is one idea applied twenty-three times.": summary punchline by shape, but it is the claim the Coupling section argues.
- Line 327, "The rung a dependence sits on decides...": a preposition before the verb, mid-sentence, not at a sentence end; `tip stranded` does not flag it.
- Line 336-339, the four parallel sentences on what each rung requires: deliberate parallelism that makes the contrast scannable.
- Line 459-460, "One question serves for every pattern chapter." followed by the question: the question is the content (`readability_db.md` rhetorical-question keep).
- Line 530-537, "A common problem we find in frameworks...": Kevlin Henney's wording, quoted, as the vale comment above the list says.
- Line 541-542, "Also goes by Isomorphism.": a subjectless fragment (§13) in first-edition voice.
- Line 560-566, the three self-answered questions: the questions are the method the chapters ahead apply (`readability_db.md` rhetorical-question keep).
- Line 565, "That remainder is worth learning": §53 by shape; the sentence weighs the remainder against the structure Python supplies, so the "worth" keep applies.
- Line 568, "A pattern that subtracts to nothing is not a mistake.": the negation is the claim, answering the reader's likely conclusion.
