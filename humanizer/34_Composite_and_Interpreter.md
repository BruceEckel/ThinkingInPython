# Humanizer candidates: Chapters/34_Composite_and_Interpreter.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

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

The chapter is clean on every word-level AI tell: no §7 vocabulary,
no curly quotes, no em-dash issues, no emoji, no boldface-header lists,
no signposting, no person drift (no "we"/"us"/"our" at all), no false
ranges, no weasel words. The two Tier A findings aren't humanizer
patterns at all: they're `CLAUDE.md`'s imperative-plus-consequence rule,
tripped twice in the same explanatory register ("Add a `Symlink`
class... [it] now fails type checking" and "Represent each construct...
and evaluation becomes a tree walk"). Tier B has one italics
re-emphasis and one metaphor family adjacent to the banned "rides on."
No housekeeping issues: no double blank lines, no `[[ ]]` notes,
no spaced ` -- `.

## Tier A

### A1 — line 136 — imperative-plus-consequence

Commands the reader to add a `Symlink` class, then reports what breaks,
instead of stating the condition. Textbook match for the banned pattern
in `CLAUDE.md` ("Remove `frozen=True` and the pattern fails").

CURRENT
```text
Add a `Symlink` class to the `Node` union.
Every function whose `case _` calls `assert_never()` now fails type checking,
because `entry` could be a `Symlink` that no case handles.
```

PROPOSED
```text
If you add a `Symlink` class to the `Node` union,
every function whose `case _` calls `assert_never()` fails type checking,
because `entry` could be a `Symlink` that no case handles.
```

### A2 — line 192 — imperative-plus-consequence

Same shape, one sentence: "Represent X, and Y becomes true." `CLAUDE.md`
gives the gerund-subject fix for exactly this case
("Invoking it repeatedly gives you backtracking and search").

CURRENT
```text
Represent each construct as a node type, and evaluation becomes a tree walk.
```

PROPOSED
```text
Representing each construct as a node type turns evaluation into a tree walk.
```

### A3 — line 551 — stranded preposition

Sentence ends on "depends on," its object moved to the front of the
relative clause. The only stranded-preposition hit in the chapter.

CURRENT
```text
A finished string has thrown away the distinction that the safety decision depends on.
```

PROPOSED
```text
A finished string has thrown away the distinction on which the safety decision depends.
```

## Tier B

### B1 — line 191 — italics used for re-emphasis, not introduction

`Interpreter` is properly italicized once, at its true first use (line 5).
This is the second use, at the top of the chapter's own `## Interpreter`
section, and `Composite` in the same clause (also a repeat use) stays
plain. Could be a deliberate re-anchor at the section's opening line;
I lean toward dropping the italics for consistency with every other
repeat use in the chapter, but this is the kind of call Bruce makes,
not me.

CURRENT
```text
*Interpreter* is Composite applied to language.
```

PROPOSED
```text
Interpreter is Composite applied to language.
```

### B2 — lines 258, 480 — "ride" as a stand-in for "depend on"/"apply"

`CLAUDE.md`'s third-tier "don't use" list bans "rides on" by name as a
metaphor standing in for a literal statement. Neither instance here is
that exact phrase, but both use the same verb for the same move: saying
something figuratively carries or travels instead of naming what it
actually does. Marginal enough that I'd understand leaving it; delete
individual rows you want left alone.

**line 258**

CURRENT
```text
The reflected methods ride the operator dispatch from [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many):
```

PROPOSED
```text
The reflected methods depend on the operator dispatch from [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many):
```

**line 480**

CURRENT
```text
One practical limit rides along:
```

PROPOSED
```text
One practical limit applies:
```

## Housekeeping

None found. No double blank line before a heading, no Semantic Line
Break drift on inspection, no `[[ ]]` draft note, no spaced ` -- `, no
em dash of any form, no curly quotes.

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
