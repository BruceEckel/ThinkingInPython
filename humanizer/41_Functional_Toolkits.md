# Humanizer candidates: Chapters/41_Functional_Toolkits.md

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

The chapter is close to clean: no promotional language, no rule-of-three
padding, no vague attribution, no curly quotes, no emoji, no boldface-header
lists, and only one em-dash-adjacent item to check (there are no em dashes
at all in this chapter, so nothing to preserve). The real findings are two
words banned outright in your style list ("ships," "spelling"), two spots
where italics land on a term that isn't new, one genuine three-paragraph
restatement in the Recursion section, and a single first-person-plural slip
inside a code comment. Nothing here suggests wholesale AI phrasing; it reads
as your own prose with a handful of specific slips.

## Tier A

### A1 — line 15 — banned word "ships"

"Ships" is on the "Don't use" tier in your style list (jargon for
"comes bundled with"). Mechanical swap, no meaning lost.

CURRENT
```text
The standard library ships the building blocks of functional Python under `functools`,
from a single fold to an alternate dispatch mechanism.
```

PROPOSED
```text
The standard library provides the building blocks of functional Python under `functools`,
from a single fold to an alternate dispatch mechanism.
```

### A2 — line 37 — banned word "spelling"

Same list, same rule: "spelling" standing in for "name/form" instead of
naming the real thing.

CURRENT
```text
For addition specifically, `sum()` is the built-in spelling,
and `math.prod()` covers multiplication.
```

PROPOSED
```text
For addition specifically, `sum()` is the dedicated built-in,
and `math.prod()` covers multiplication.
```

### A3 — line 64 — italics used for emphasis, not a new term

"Method" was introduced back in the Classes chapter; every other italic in
this chapter marks a term's first use (*base case*, *circle method*,
*Kirkman's schoolgirl problem*...). This one doesn't fit that pattern.

CURRENT
```text
One trap: decorating a *method* with `@cache` keys every entry on `self`,
```

PROPOSED
```text
One trap: decorating a method with `@cache` keys every entry on `self`,
```

### A4 — line 248 — italics on an already-linked term

The same sentence links to `[Visitor](33_Visitor.md#...)` for this exact
term, and the chapter's other pattern reference
([Observer](30_Observer.md), line 66) isn't italicized either.
The italics here read as decoration, not introduction.

CURRENT
```text
uses `singledispatch()` as an alternative to the *Visitor* pattern,
```

PROPOSED
```text
uses `singledispatch()` as an alternative to the Visitor pattern,
```

## Tier B

### B1 — lines 612-615 — restates a point already made twice

Three consecutive-ish paragraphs land on the same claim: recursion pays off
on self-similar, tree-shaped data. Line 602 says it obliquely ("once the
problem branches"), line 605 says it directly ("naturally self-similar,
such as walking a tree"), and this paragraph says it a third time before
finally moving to new material (the code walkthrough). I lean toward
cutting the redundant opening sentence; the tree/nested-data point already
lives in the paragraph above it.

CURRENT
```text
Recursion is beneficial when the data is recursive.
Code that walks a tree, nested data,
or a directory reads most clearly when its shape matches the data's shape.
The function handles one node and trusts itself for the rest:
```

PROPOSED
```text
Code that walks a tree, nested data,
or a directory reads most clearly when its shape matches the data's shape.
The function handles one node and trusts itself for the rest:
```

### B2 — lines 602-603 — passive tail

Minor; §13 is advisory here, and this is a small one. Active voice names
the actor instead of leaving it to a dangling "which."

CURRENT
```text
Its payoff shows up once the problem branches, not just repeats,
which is shown in the next example.
```

PROPOSED
```text
Its payoff shows up once the problem branches, not just repeats,
as the next example shows.
```

### B3 — lines 689-693 — case-study opener restates its own heading

The heading is "Case Study: Pairing Rotations"; the first sentence just
announces "here comes a problem" before the problem is actually stated.
Precedent (ch46/47) calls this a per-instance judgment, declined once,
accepted once. The paragraph reads fine starting one sentence later.

CURRENT
```text
Here is a recurring practical problem.
Pair up participants for an activity across several rounds,
and avoid repeating a pairing until every possible pairing has had a turn.
This is a good place to see these chapters' ideas working together on one small,
real program instead of one at a time.
```

PROPOSED
```text
Pair up participants for an activity across several rounds,
and avoid repeating a pairing until every possible pairing has had a turn.
This is a good place to see these chapters' ideas working together on one small,
real program instead of one at a time.
```

## Housekeeping

1. **Listing comment, line 658** — the code comment
   `# count() is infinite; islice() pulls only what we ask for:` uses "we,"
   which is the same first-person-plural slip flagged in chapters 46/47
   (the book is second person). A rewrite like
   `# count() is infinite; islice() pulls only what's needed:` avoids the
   pronoun without changing the code it sits next to. Applying this needs
   a re-sync (`make verify` does it).

## Considered and not flagged

- **Duplicate transition sentence** ("What follows starts with the simplest
  tools and works up to the ones with the most moving parts," lines 22 and
  303) — appears verbatim in both the `functools` and `itertools` section
  intros. Read as deliberate mirroring between the chapter's two parallel
  tours rather than templated repetition; the two intro paragraphs share
  the same shape throughout (description, "already X, already Y," this
  sentence), which looks intentional rather than careless.
- **"Already ... already" anaphora** (lines 20 and 298, "already written,
  already correct" / "already tuned ... already correct") — same mirrored-
  intro device as above, not filler repetition.
- **Frequent "only"** — appears roughly a dozen times, but each instance is
  a real restrictive qualifier ("only works correctly for pure functions,"
  "only merges neighbors," "use only the returned iterators"), the kind
  your style list says to keep rather than an unearned intensifier.
- **"Plain"** (lines 237, 245, 627: "the plain class," "a plain function,"
  "a plain number") — each draws a genuine contrast (plain class vs. the
  dataclass that replaces it; plain function vs. one wired for dispatch;
  plain number vs. a sublist), matching the carve-out in your style rules.
- **Reflexive "itself"** (lines 578, 615, 634, 801) — all four describe an
  actual reflexive relationship (recursion calling itself, a function
  trusting itself, an RNG not reaching outside itself), not flourish.
- **Rule-of-three lists** (lines 18-19: caching logic / eviction policy /
  dispatch table; lines 298-300: empty iterable / single element / uneven
  lengths) — both are concrete, specific, and map directly to material the
  chapter actually covers, not padding to sound comprehensive.
- **Fragmented headers (§29)** — every one of the 27 `###` subsections opens
  with a substantive definition sentence, never a generic restatement of
  the heading before the real content. No instances here.
- **Em dashes** — none appear anywhere in this chapter, so there was
  nothing to check for removal or spaced ` -- ` mishandling.

## Scan coverage

Clean on: AI vocabulary (§7: delve, crucial, underscore, showcase,
testament, tapestry, landscape, vibrant...), promotional/advertisement
language (§4), vague attribution and weasel words (§5), copula avoidance
(§8), negative parallelisms and tailing negations (§9), elegant variation
beyond the mirrored intros noted above (§11), false ranges (§12), boldface
overuse (§15), inline-header vertical lists (§16), emoji (§18), curly
quotes (§19), collaborative/sycophantic artifacts (§20, §22),
knowledge-cutoff disclaimers (§21), filler phrases and hedging (§23-24),
generic positive conclusions (§25, and the chapter's actual closer ties
back to the Recursion chapter with a specific claim rather than a send-off),
hyphenated-pair overuse (§26), persuasive-authority tropes (§27), aphorism
formulas (§32), conversational rhetorical openers (§33), stranded
prepositions, "raise" without an object, "is what," and the "nothing else"
family. Person (we/us/our) is clean outside the one listing comment noted
in Housekeeping.
