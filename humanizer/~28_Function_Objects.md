# Humanizer candidates: Chapters/28_Function_Objects.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied, and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Every block in the file survived review, Tier A and Tier B alike.
Eight prose edits:

- A1, four first-person-plural sites converted to second person or to an
  impersonal subject (lines 134, 270, 357, 360). The line-134 and line-360
  rewrites use Bruce's own wording, not the drafted PROPOSED text:
  "three algorithms" rather than "three real algorithms," and
  "These tests confirm" rather than "The tests below confirm."
- A2, the emphasis italic on *when* at line 121.
- B1, the emphasis italic on *class* at line 315, dropped for consistency
  with every other unitalicized use of the word in the chapter.
- B2, "A *Strategy* is an interchangeable algorithm chosen at runtime"
  shortened to drop the phrase the heading already carries.
- B3, the chapter-structure preview at lines 11-12, rewritten to name what
  repeats ("Each pattern below appears twice").

The review leaned toward keeping B2 and B3. Both were kept in the file and
therefore applied; recorded here so a later pass does not read the lean as
the decision.

## Housekeeping

None found, and none outstanding. No double blank line before a heading,
no Semantic Line Break drift, no `[[ ]]` draft note, no spaced ` -- `, and
no `#` listing-comment tells.

## Considered and not flagged

- **Repeated italics on pattern names** (*Command* line 16, *Strategy*
  lines 133/354/526, *Chain of Responsibility* line 320): each is a
  second or later mention, not a first use, which would normally be a
  §-italics finding. Checked chapters 30 and 33 for comparison:
  Observer is italicized 4 times and Visitor 6 times across those
  chapters, always on the bare pattern name and never on a first use
  alone. This is a consistent, deliberate book-wide convention for
  naming a GoF pattern, not stray emphasis, so none of these are
  flagged.
- **`*GoF Design Patterns*`** (lines 10, 87, 321): book-title italics,
  a different convention from term-introduction italics. Not a finding.
- **"You can name it, store it in a list, pass it as an argument, and
  return it."** (line 8): four concrete, distinct verbs describing
  real Python behavior, not a padded rule-of-three list.
- **"just a function" (lines 17, 88), "simply tries" (line 194)**:
  ordinary English, not on the AI-vocabulary watch list.
- **Long unbroken clause lines** (e.g. lines 311-314, up to 115
  characters): each is already broken at every available comma
  boundary; the length is inherent to the clause, not reflow drift.
- **"The generic guards the boundary. The `Any` covers the
  heterogeneous storage behind it."** (lines 468-469): two short
  parallel sentences, not a run of staccato fragments, and each states
  distinct technical content. Not flagged as manufactured punchline
  drama.

## Scan coverage

No hits on: AI vocabulary (§7), copula avoidance (§8), negative
parallelism/tailing negation (§9), rule-of-three padding (§10),
elegant variation (§11), false ranges (§12), overused boldface (§15),
inline-header vertical lists (§16), emojis (§18), curly quotes (§19),
collaborative-artifact phrasing (§20), knowledge-cutoff disclaimers
(§21), sycophantic tone (§22), filler phrases (§23), excessive
hedging (§24), generic positive conclusions (§25), hyphenated-pair
overuse (§26), persuasive authority tropes (§27), aphorism formulas
(§32), conversational rhetorical openers (§33), diff-anchored writing
(§30), and the "nothing else" family. No em dashes appear anywhere in
this chapter, so there was nothing to protect there either.
