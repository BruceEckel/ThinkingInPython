# Humanizer candidates: Chapters/19_Concurrency.md

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

This chapter is close to clean: zero em dashes anywhere in it, no curly
quotes, no promotional or notability language, and not one hit on the
§7 AI-vocabulary list. The one real pattern is person: ten sites slip
from the book's second person into a first-person-plural "we," none of
them matching the two exceptions Bruce kept in 46/47. The rest is small
polish (two italics used for emphasis rather than term introduction, an
`is what` construction, a banned "lands" metaphor, one `in order to`)
plus two structural calls (a fragmented header, a broken parallel in a
numbered list) that are genuinely arguable.

## Tier A

### A1 — lines 17, 127, 812, 1284, 1680, 1685, 1747, 1905, 2059, 2063 — person ("we" cluster)

Ten sites drift from the book's second person into first-person-plural
narration. None resemble the two exceptions kept in chapters 46/47 (a
real acknowledgment, and one deliberate "Let's see..."). Delete
individual rows you want left alone.

**line 17**

CURRENT
```text
We say that each task (unit of work) is allocated its own thread,
```

PROPOSED
```text
Each task (unit of work) is allocated its own thread,
```

**line 127**

CURRENT
```text
Later in this chapter, we show two other approaches,
```

PROPOSED
```text
Later in this chapter, two other approaches follow,
```

**line 812**

CURRENT
```text
We can test the claim that wall-clock time falls toward a single task's time as we add more cores.
```

PROPOSED
```text
You can test the claim that wall-clock time falls toward a single task's time as you add more cores.
```

**line 1284**

CURRENT
```text
the first two of which we've already seen:
```

PROPOSED
```text
the first two of which already appeared in this chapter:
```

**line 1680**

CURRENT
```text
We can support the claim that a thread costs real memory while a task costs much less.
```

PROPOSED
```text
You can support the claim that a thread costs real memory while a task costs much less.
```

**line 1685**

CURRENT
```text
We can calculate the ratio between the two:
```

PROPOSED
```text
You can calculate the ratio between the two:
```

**line 1747**

CURRENT
```text
We see a similar difference in time:
```

PROPOSED
```text
A similar difference shows up in time:
```

**line 1905**

CURRENT
```text
which means we can also produce deadlock with `asyncio`.
```

PROPOSED
```text
which means `asyncio` can also produce deadlock.
```

**line 2059**

CURRENT
```text
As we've seen in this chapter,
```

PROPOSED
```text
As this chapter has shown,
```

**line 2063**

CURRENT
```text
Also, notice how much we've talked about the OS in this chapter.
```

PROPOSED
```text
Also, notice how much this chapter has talked about the OS.
```

### A2 — lines 793, 1480 — italics used for emphasis, not term introduction

Both italicize an ordinary word for stress rather than introducing a
new term. The chapter's other italics are all first-use terminology, so
these two stand out. Delete individual rows you want left alone.

**line 793**

CURRENT
```text
A queue carrying bulky data must be drained *before* joining:
```

PROPOSED
```text
A queue carrying bulky data must be drained before joining:
```

**line 1480**

CURRENT
```text
a `concurrent_tee()` iterator is safe to hand to *one* thread,
```

PROPOSED
```text
a `concurrent_tee()` iterator is safe to hand to one thread,
```

### A3 — line 1389 — "is what" cleft

Deleting "is what" changes nothing here; the giveaway is the verb
right after it ("is what makes"), per the CLAUDE.md rule.

CURRENT
```text
The count of distinct values is still 200, which is what makes this dangerous:
```

PROPOSED
```text
The count of distinct values is still 200, which makes this dangerous:
```

### A4 — line 1112 — banned metaphor "lands"

"Lands" is on the don't-use list (name the real thing instead of the
tech-slang metaphor).

CURRENT
```text
A typical run lands near 50.
```

PROPOSED
```text
A typical run settles near 50.
```

### A5 — line 2066 — filler phrase "in order to"

Exactly the §23 example ("In order to achieve this goal" becomes "To
achieve this").

CURRENT
```text
all the way to hardware, in order to understand a particular bug.
```

PROPOSED
```text
all the way to hardware, to understand a particular bug.
```

## Tier B

### B1 — lines 2051-2055 — fragmented header

`## Concurrency is Not Easy` is followed by a one-line paragraph
("Concurrency is neither simple nor solved.") before the real content
starts. This is the classic §29 shape, but the line does add one real
distinction (simple vs. solved are two different claims), so it isn't
pure restatement the way the skill's own example is. Bruce declined this
pattern once and accepted it once; I lean toward cutting it, since the
heading already carries "not easy" and the next paragraph stands fine
on its own.

CURRENT
```text
## Concurrency is Not Easy

Concurrency is neither simple nor solved.

There are ongoing arguments about what the term even means.
```

PROPOSED
```text
## Concurrency is Not Easy

There are ongoing arguments about what the term even means.
```

### B2 — lines 1898-1901 — broken parallel in the deadlock conditions

Items 1, 3, and 4 are noun phrases naming a condition. Item 2 is a full
clause describing behavior instead. I lean toward fixing it, since the
other three make the parallel obvious by contrast, but it's a small
enough wobble that leaving it is defensible too.

CURRENT
```text
1. Exclusive access to each resource
2. A task holds one resource while it waits for another
3. No way to force a task to give up what it holds
4. A cycle of tasks each waiting on the next
```

PROPOSED
```text
1. Exclusive access to each resource
2. Holding one resource while waiting for another
3. No way to force a task to give up what it holds
4. A cycle of tasks each waiting on the next
```

## Housekeeping

1. **Semantic Line Break drift, line 1887.** Two sentences share one
   source line: `` raising `RuntimeError: Lock is not acquired.` An
   over-released `Semaphore` quietly raises its own limit instead, ``.
   The sentence boundary after `` acquired.` `` should start a new
   source line. `make reflow CH=19` fixes it (or a hand edit splitting
   at that point).

## Considered and not flagged

- **Em dashes.** None appear anywhere in this chapter, so there is
  nothing to protect and nothing to strip.
- **`only` / `never`.** Both appear often, but every instance states a
  real technical constraint (one core, one GIL, one coroutine at a
  time) rather than serving as filler emphasis. Not a cluster.
- **`already` / `even`.** Frequent but ordinary connective use, never
  piled up with other AI-vocabulary words.
- **Line 2172, "actually."** "are where STM actually succeeded" carries
  a genuine contrast against the failed attempts described just before
  it. Single instance, left alone.
- **Line 612, "has to."** "every new caller has to remember to pass it
  along" states a real necessity; not a tell, and a single instance.
- **Line 2064, "pierced to tatters."** A vivid, slightly mixed metaphor
  ("comfortable abstraction ... pierced to tatters"), but this reads as
  an authorial idiosyncrasy, specific and a little odd in the way
  genuine human writing is, not a smoothed-over AI phrase. Left alone.
- **`### Are Threads Still Necessary?` (line 1625).** The section opens
  with two sentences of real content, then a rhetorical question that
  echoes the heading, answered in the next paragraph ("It does, but
  not for the reason..."). This is a near-miss for the fragmented-header
  pattern but reads as a deliberate Socratic setup rather than a padded
  opener, so it's left alone.
- **The `Guidelines` list (2011-2049) and the concurrency-topics
  footnote list (2086-2109).** Both use bold-label list items, but
  they're genuine claims and glossary-style term definitions, not the
  mechanical "Label: filler restatement" shape §16 targets.
- **`### Why Python Has a GIL`'s opening aside (line 1027).** The
  personal PyCon reference is a specific, dated, defensible detail:
  a sign of human authorship, not AI.

## Scan coverage

Clean on: §1-2 (significance/notability puffery), §4-6 (promotional
language, vague attribution, challenges/future-outlook sections), §7
(AI vocabulary), §8-11 (copula avoidance, negative parallelism, rule of
three, elegant variation), §12 (false ranges), §15-19 (boldface
overuse, inline-header lists, title case, emoji, curly quotes), §20-22
(collaborative artifacts, knowledge-cutoff disclaimers, sycophancy),
§23-25 (filler phrases beyond the one flagged, excessive hedging,
generic positive conclusions), §27-28 (authority tropes, signposting),
§32-33 (aphorism formulas, rhetorical openers). Double blank lines
before headings, spaced ` -- `, and `[[ ]]` draft notes: none found.
Word-echo and staccato-drama scans turned up nothing beyond ordinary
variation.
