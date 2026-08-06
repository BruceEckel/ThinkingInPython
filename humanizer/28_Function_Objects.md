[[Reviewed]]
# Humanizer candidates: Chapters/28_Function_Objects.md

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

Mostly clean chapter. Word-level scan found nothing: no AI vocabulary,
no em dashes at all (so nothing to protect there), no curly quotes,
no filler phrases, no boldface-header lists.
The real findings are structural: four first-person-plural slips
("we") in a book written in second person, and two italics used for
emphasis rather than term introduction.
The repeated italicizing of pattern names (*Strategy*, *Command*, *Chain
of Responsibility*) is a deliberate book-wide convention, confirmed
against chapters 30 and 33, and is not flagged.

## Tier A

### A1 — lines 134, 270, 357, 360 — person: "we" in a second-person book

The book addresses the reader as "you" throughout (see lines 8, 272, 395).
These four sentences slip into first-person plural with no exception
like the acknowledgment case noted in prior chapters.
Delete individual rows you want left alone.

**line 134**

CURRENT
```text
For the following examples we will use three real algorithms that find a *root* of a function `f`,
a value where `f(x)` is zero.
```

PROPOSED
```text
The following examples use three algorithms that find a *root* of a function `f`,
a value where `f(x)` is zero.
```

**line 270**

CURRENT
```text
We use strategies-as-functions constantly in Python without naming it as a pattern.
```

PROPOSED
```text
Strategies-as-functions are used constantly in Python without naming it as a pattern.
```

**line 357**

CURRENT
```text
We see the fall-through when bisection cannot bracket a root.
```

PROPOSED
```text
This is the fall-through: bisection cannot bracket a root.
```

**line 360**

CURRENT
```text
We test that the first finder that converges wins,
a later finder rescues one that fails, and an empty chain returns `None`:
```

PROPOSED
```text
These tests confirm that the first finder that converges wins,
a later finder rescues one that fails, and an empty chain returns `None`:
```

### A2 — line 121 — italics used for emphasis, not term introduction

"when" is not a new term; italicizing it is plain emphasis on a
function word, which the italics rule (introduce-a-term-only) doesn't cover.

CURRENT
```text
The two comprehensions look alike and differ in *when* they read `n`.
```

PROPOSED
```text
The two comprehensions look alike and differ in when they read `n`.
```

## Tier B

### B1 — line 315 — italics used for contrast, not term introduction

"class" is an ordinary word used unitalicized dozens of times in this
chapter ("the class version," "FindRoot class," "Command subclass").
Here it's italicized to contrast against "closure" in the next sentence.
That's a real contrastive function, not random emphasis, so I'd
understand keeping it. Lean toward dropping the italics for consistency
with every other plain use of "class" in the chapter.

CURRENT
```text
Save the strategy *class* for an algorithm that carries several related methods or mutable state.
```

PROPOSED
```text
Save the strategy class for an algorithm that carries several related methods or mutable state.
```

### B2 — line 133 — body echoes the heading it sits under

The heading is "Strategy: Choosing the Algorithm at Runtime";
the next line repeats "chosen ... at runtime" almost verbatim before
adding the real definition. This is the fragmented-header pattern
(§29), which was declined once and accepted once in prior chapters —
a per-instance call, not a rule. Unlike the classic §29 case, this
sentence does add content (it defines what a Strategy is), so I lean
toward keeping it as written.

CURRENT
```text
A *Strategy* is an interchangeable algorithm chosen at runtime.
```

PROPOSED
```text
A *Strategy* is an interchangeable algorithm.
```

### B3 — lines 11-12 — chapter-structure preview

This tells the reader how the chapter is organized (function form,
then class form, for each pattern) before the sections deliver it.
It's the same shape as the announcement pattern applied freely in
prior chapters, but it's plain structural information rather than a
"let's dive in" flourish, and the chapter's parallel structure across
three patterns makes the preview genuinely useful. I lean toward
keeping it; flagging per precedent.

CURRENT
```text
The sections below show the function form first,
then the classic object form for contrast.
```

PROPOSED
```text
Each pattern below appears twice: first as a function,
then as the classic class-based form for contrast.
```

## Housekeeping

None found. No double blank line before a heading, no Semantic Line
Break drift, no `[[ ]]` draft note, no spaced ` -- `, and no `#`
listing-comment tells (all comments in code fences are plain
technical notes, e.g. "Endpoints must bracket a root").

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
