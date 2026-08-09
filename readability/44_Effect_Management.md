> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/44_Effect_Management.md`

Second review of this chapter.
The findings in `readability/~44_Effect_Management.md` were all accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one moved "Converting Effectful to
Pure" up ahead of "A Program Can Never Be Pure", renamed "A Taxonomy of
Benefits" to "Two Phases of Effect Analysis", opened the chapter with the
failing-test story, rewrote two sentences in the first paragraph, added a
generators aside, a `print()`-is-still-invisible qualification, a closing
handoff to Part V, and a fifth exercise. Every finding was in that new
prose or in a seam the moves opened.

Every finding was resolved directly and applied (listed below).
No blocks remain.

## Applied directly

- Opening: cut "What happens when a function you believe is pure calls other
  functions?" and joined the seam: "...settle the question by reading one
  function. That stops working as soon as the function calls others."
  (the new cold open already asks that question in a form the reader felt,
  so the abstract restatement twenty lines later was the second telling;
  "causes the calling function to also be impure" also tightened to "makes
  the calling function impure too").
- "Effects by Hand": the `print()`-is-still-invisible qualification moved
  from mid-paragraph to its own paragraph after the delayed-binding point
  lands, now opening "The signature says what `greet()` needs..." (a caveat
  placed after the claim reads as a boundary on it; placed inside, it read
  as a retraction of a claim the reader had not finished hearing).
- Generators aside: "Python has a construct that suspends a computation and
  hands control to whoever is driving it, then resumes it with a value: the
  generator." → "A Python generator suspends a computation, hands control to
  whoever is driving it, and resumes it with a value." (§69 reveal
  withholding a name every reader has known since chapter 23; naming it
  first also connects the aside to the continuation sentence above it).
- Closing handoff: "Python cannot give you the language half of that today.
  It can give you the library half. The next three chapters build one:" →
  "Python offers no native version of this, and will not soon. The next
  three chapters build the library version:" (the halved contrast restated
  a section the chapter already spent on native versus library systems).
- "Two Phases of Effect Analysis" no longer opens on the parallelism/testing
  paragraph. That paragraph moved to the end of the preceding section, "A
  Program Can Never Be Pure" (with a new bridging sentence, "So why track
  them at all?"), which argues Effects are the point rather than a defect
  and had no closing beat of its own. "Two Phases of Effect Analysis" now
  opens on "Think of Effect analysis as a series of phases," which is what
  its renamed heading actually names; the parallelism/testing content was
  the benefit the section's old name promised, not the phases material its
  new name describes. No text changed beyond the move and the one bridging
  sentence, and the heading text itself, and therefore its anchor, is
  unchanged.

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface outside the
  existing EMS property list, no emojis, no slot-fill placeholders.
- The cold open is a §45 speculative scenario by shape ("A test you wrote last
  week starts failing"). The carve-out applies: it is a concrete instructional
  case with a stated payoff two sentences later, not a "picture a world where"
  opener standing in for an argument. Not flagged.
- The AI-languages restructure moved the reason into the lead-in as the review
  asked. The resulting sentence ("and for their purpose the other two parts are
  liabilities: a host that pins the implementations itself can guarantee what
  generated code is able to do") uses a colon to introduce an explanation rather
  than to stage a reveal, so §69 does not apply.
- Exercise 2's rewrite and its solution were checked against each other: the
  exercise now asks for three wrapping callers and the solution builds
  `session()`, `menu()`, and `main()`, so the counts it reports (five signatures
  edited, three of them mentioning an Effect they never use) are the counts a
  reader will actually get.
- The new "no relation to the TypeScript library of the same name" aside was
  checked for tone against the surrounding catalog of Python libraries; it
  matches the register and answers the double-take the review predicted.
