# Humanizer candidates: Chapters/34_Composite_and_Interpreter.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Every block survived review, Tier A and Tier B alike, and no PROPOSED fence
was rewritten. Six prose edits:

- A1, the imperative-plus-consequence at line 136 ("Add a `Symlink`
  class... now fails type checking") restated as a condition.
- A2, the same shape in one sentence at line 192, fixed with the
  gerund-subject form `CLAUDE.md` prescribes.
- A3, the stranded "depends on" at line 551, fronted to "on which."
- B1, the re-emphasis italics on *Interpreter* at line 191. The heading
  above it keeps its own wording; only the prose changed.
- B2, both "ride" metaphors: "ride the operator dispatch" at line 258 to
  "depend on," and "One practical limit rides along" at line 480 to
  "applies."

The review leaned toward dropping B1's italics and called B2 marginal.
Both stayed in the file and were applied.

Prose-only: no listing changed, so `Examples/` was untouched and the
chapter's `#:` markers still match.

## Housekeeping

None found, and none outstanding. No double blank line before a heading,
no Semantic Line Break drift, no `[[ ]]` draft note, no spaced ` -- `,
no em dash of any form, no curly quotes.

## Considered and not flagged

- **Rule of three.** "Counting files, finding an entry by name, and
  printing the tree" (line 66) and "SymPy expressions, Pandas and
  Polars column arithmetic, and SQLAlchemy filter conditions" (line
  268-269) are both three-item lists, but each item is a distinct,
  verifiable technical claim, not padding to look comprehensive. Left
  alone.
- **Staccato short-sentence pairs.** "They build nodes." (line 249),
  "It built a tree." (line 311), "It can produce another tree." (line
  382). Each is a single short sentence following a longer one, which
  the skill's own detection guidance exempts ("flag staccato drama
  only when several short fragments appear in a row"). No run of them
  anywhere in the chapter.
- **Fragmented header candidate.** "## Evaluation Is a Tree Walk"
  followed by "Evaluation is a recursive `match` function." (line 276)
  restates part of the heading, but it adds real technical
  specificity (which kind of function) rather than empty filler like
  "Speed matters." Not flagged.
- **"Composite is the data... Interpreter is the behavior..."** (lines
  476-477) has the shape of an aphorism formula (§32), but each half
  is immediately cashed out with a colon and a concrete definition,
  which is exactly the fix the rule asks for, not the vague version it
  warns against.
- **"before the interpreter ever runs"** (line 256). "ever" is on the
  tier-1 watch list and is arguably redundant next to "already parsed
  it" earlier in the same sentence. Genuinely marginal, one word, not
  worth a formal block.
- **"themselves" (line 244).** Reflexive and load-bearing ("`Add` and
  `Mul` hold expressions themselves"), pointing at the recursion that
  makes it a composite. Not a flourish use of "itself."
- **Person.** No "we"/"us"/"our" anywhere in the chapter; every
  address is second person or impersonal. Nothing to convert.

## Scan coverage

Clean on: §1-§8 vocabulary and construction lists (significance
inflation, notability, participle-tail padding, promotional language,
weasel attribution, copula avoidance), §9 negative parallelism and
tailing negation, §11 elegant variation, §12 false ranges, §15-§19
boldface/inline-header lists/title-case/emoji/curly quotes, §20-§22
chat artifacts and sycophancy, §21 knowledge-cutoff disclaimers, §23-§25
filler and hedging, §26 hyphen-pair overuse (all hyphenated compounds
present are correctly attributive), §27 persuasive-authority tropes,
§28 signposting, §33 rhetorical openers, and the "nothing else" family
and "is what" cleft (neither has a single instance). Person and italics
were checked chapter-wide, not just at the flagged lines.
