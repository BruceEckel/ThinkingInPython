[[Reviewed]]
# Humanizer candidates: Chapters/32_Multiple_Dispatching.md

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

The chapter is clean at the word level: no §7 AI-vocabulary hits, no curly
quotes, no emoji, no promotional language, no hedging, no filler phrases,
no upbeat send-off, and no em dashes anywhere (so §14 had nothing to
protect). It is also short, so the findings are small in number.

The largest finding is person. Two prose sites use editorial "we" (lines
53 and 71), and nine `eval_*()` comments inside `paper_scissors_rock.py`
say "we're in Paper" / "we're in Scissors" / "we're in Rock". The comments
are real findings but sit inside a fenced block, so they are Housekeeping,
not Tier A. Everything else is a handful of emphasis italics and one
redundant sentence.

## Tier A

### A1 — lines 53, 71 — person consistency

The book is second person. Both sites are the author's "we" addressing
the reader, not a genuine plural. Line 71 also reuses italics on *Multiple
Dispatching*, already introduced at line 17, so the rewrite drops the
italics along with the pronoun. Delete individual rows you want left
alone.

**lines 53-54**

CURRENT
```text
We also need two small helper functions, one to generate random pairs of items,
and one to play a pair off and print the result:
```

PROPOSED
```text
You'll also need two small helper functions, one to generate random pairs of items,
and one to play a pair off and print the result:
```

**line 71**

CURRENT
```text
Here we demonstrate *Multiple Dispatching*:
```

PROPOSED
```text
Here is Multiple Dispatching in action:
```

### A2 — line 151 — emphasis italics

*scissors that started the duel* is emphasis, not a term introduction.
The chapter's other italics (*Multiple Dispatching*, *double dispatching*,
*reflected*) all mark first use; this one doesn't.

CURRENT
```text
`Paper.eval_scissors()` returns `WIN`,
and that is the outcome for the *scissors that started the duel*,
not for the `Paper` whose code is running: scissors cut paper.
```

PROPOSED
```text
`Paper.eval_scissors()` returns `WIN`,
and that is the outcome for the scissors that started the duel,
not for the `Paper` whose code is running: scissors cut paper.
```

### A3 — lines 214, 218 — italics and intensifier on "exactly"

Two uses of "exactly" four lines apart. Line 214 italicizes it for
emphasis (not a term introduction, so the italics go). Line 218 is the
CLAUDE.md sense to avoid, "exactly" as a filler intensifier rather than a
precise numeric or logical match. Delete individual rows you want left
alone.

**line 214**

CURRENT
```text
The match is on classes *exactly*,
```

PROPOSED
```text
The match is on classes exactly,
```

**line 218**

CURRENT
```text
which is exactly what you want while adding `Lizard` in exercise 1.
```

PROPOSED
```text
which is what you want while adding `Lizard` in exercise 1.
```

## Tier B

### B1 — lines 27-29 — redundant restatement

The third sentence restates the first two without adding anything; the
"first/second" split already made the point. I lean toward cutting it,
but it also reads as a deliberate one-line recap before the example, so
this is a real judgment call.

CURRENT
```text
To dispatch on two unknown types, you need two method calls.
The first resolves the first type, and the second resolves the second.
Each unknown type needs its own dispatching method call.
```

PROPOSED
```text
To dispatch on two unknown types, you need two method calls.
The first resolves the first type, and the second resolves the second.
```

## Housekeeping

1. **Listing comments.** Nine `eval_*()` comments in
   `paper_scissors_rock.py` use editorial "we" ("Item was Paper, we're
   in Paper", and the same pattern for Scissors and Rock): lines 89, 92,
   95, 103, 106, 109, 117, 120, 123. Same person-consistency issue as
   A1, but these sit inside a fenced ```python``` block, so they are out
   of scope for a prose edit here. Fixing them means rewording the nine
   comments (for example "Item was Paper; this is Paper's own case") and
   re-syncing with `make verify`, and the surrounding code must not
   change.
2. **Clean structurally.** No double blank line before a heading, no
   `[[ ]]` draft note, no spaced ` -- `, and no em dash at all in this
   chapter, so §14 had nothing to preserve.
3. **Semantic Line Breaks look clean.** Spot-checked throughout; breaks
   consistently land on sentence and clause boundaries, including the
   longer sentences in the operator-dispatch section. No `make reflow`
   drift found.

## Considered and not flagged

- **"A tuple serves as a key just as easily as a single object."**
  (line 212). §8's copula-avoidance list includes "serves as," but this
  is a single plain statement of fact, not an inflated substitute for
  "is." Left alone.
- **"Declining is not failing; the error appears only when nobody
  volunteers."** (line 316). Shaped like §9's "not X, it's Y," but it
  draws a real technical distinction the paragraph needs (an operand
  declining a type is not the same as the operation failing), and it's
  a single instance, not a stacked pair. Left alone.
- **"The answer starts with something you probably never consider."**
  (line 11). A mild lead-in hook, but it's one sentence, not a
  standalone theatrical opener ("Honestly?", "Here's the thing") from
  §33, and nothing else near it clusters with it. Left alone.
- **Three forms of polymorphism** (lines 20-24: overloading, generics,
  runtime dispatch). Looks like a rule-of-three (§10) on the surface,
  but each item is a genuinely distinct answer to "what does
  polymorphism mean," not decorative padding. Left alone.
- **"Here is the machinery, with each dispatch traced:"** (line 262).
  A mild announcement before a listing, but it matches how the chapter
  introduces its other listings (e.g. line 160's "like this:") and
  isn't part of a cluster of signposting. Left alone.

## Scan coverage

No hits on §4 promotional language, §5 vague attributions, §6
challenges-and-prospects sections, §7 AI vocabulary, §12 false ranges,
§15/§16 boldface or inline-header lists, §19 curly quotes, §20
collaborative artifacts, §21 knowledge-cutoff disclaimers, §22
sycophantic tone, §23 filler phrases, §24 excessive hedging, §25 generic
positive conclusions, §26 hyphenated-pair overuse, §27 persuasive
authority tropes, §29 fragmented headers, §30 diff-anchored writing, §31
staccato drama beyond one ordinary short sentence, §32 aphorism
formulas, or emoji. Person, italics, and one redundant sentence are the
whole of it.
