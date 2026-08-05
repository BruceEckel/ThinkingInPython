# Humanizer candidates: Chapters/33_Visitor.md

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

Short chapter, mostly clean. The §7 AI-vocabulary list, curly quotes,
emoji, boldface-header lists, promotional language, signposting, and the
"Challenges" formula all came back empty. The one finding worth acting on
is a direct hit against your own banned-words list: "load-bearing" at
line 117. Past that, the opening paragraph (lines 6-11) repeats
"hierarchy" and "unchangeable" enough to read mechanical, and there's one
stray emphasis italic. Two listing-comment issues (a first-person "we"
and a three-times-repeated comment template) go in Housekeeping, not
Tier A/B, per the fenced-block rule.

## Tier A

### A1 — line 6-11 — word echo

"Hierarchy" appears three times and "unchangeable" twice in five short
sentences, bookending the paragraph with the same word. Reads repetitive
rather than emphatic.

CURRENT
```text
The *Visitor* assumption is that you have a primary class hierarchy that is unchangeable.
Perhaps it's from another vendor and you can't make changes to that hierarchy.
However, you'd like to add new polymorphic methods to that hierarchy.
Normally you'd need to add something to the base class interface,
but that's unchangeable.
How do you get around this?
```

PROPOSED
```text
The *Visitor* assumption is that you have a primary class hierarchy you cannot change.
Perhaps it's from another vendor and you can't touch its source.
However, you'd like to add new polymorphic methods to it.
Normally you'd add something to the base class interface,
but that's off the table.
How do you get around this?
```

### A2 — line 117 — banned word "load-bearing"

"Load-bearing" is on the CLAUDE.md "Don't use" list. Name the real thing
instead of the construction metaphor.

CURRENT
```text
One annotation in the listing is load-bearing.
```

PROPOSED
```text
One annotation in the listing is required for the code to type-check.
```

### A3 — line 110-113 — emphasis italic

"*which*" is italicized for emphasis, not to introduce a term. Every
other italic in this chapter marks a pattern name or a first-use term
(see Considered and not flagged); this one is the outlier.

CURRENT
```text
`Chrysanthemum` overrides `eat()`
(chrysanthemums really do produce a natural insecticide),
so that line depends on both unknown types at once:
the worm's type chose `eat()`, and the flower's type chose *which* `eat()` runs.
```

PROPOSED
```text
`Chrysanthemum` overrides `eat()`
(chrysanthemums really do produce a natural insecticide),
so that line depends on both unknown types at once:
the worm's type chose `eat()`, and the flower's type chose which `eat()` runs.
```

## Tier B

### B1 — line 118-120 — watch-list word "honest"

"Honest" is on the global "Avoid if possible" watch list. It works as a
personifying flourish here (an annotation that "tells the truth"), so
I'd understand keeping it, but the concrete version says the same thing
without the metaphor.

CURRENT
```text
`accept()` types its visitor as `Any`,
because the `Visitor` base class declares no `visit()` method,
so `visitor.visit(self)` fails the type checker under an honest `Visitor` annotation.
```

PROPOSED
```text
`accept()` types its visitor as `Any`,
because the `Visitor` base class declares no `visit()` method,
so declaring that parameter as `Visitor` instead of `Any` fails the type checker.
```

### B2 — line 132-135 — repeated sentence opener

Two consecutive sentences both start with "This." Minor on its own; I'd
lean toward fixing it since it sits right next to the paragraph in A1,
but it's a much weaker case than that one.

CURRENT
```text
This turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
This is how *Visitor* works,
but without the `accept()` hook or the `Visitor` class hierarchy:
```

PROPOSED
```text
It turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
That's how *Visitor* works,
but without the `accept()` hook or the `Visitor` class hierarchy:
```

## Housekeeping

1. **Listing comments, repeated template.** `flower_visitors.py` at
   lines 62, 67, 72 has three near-identical comments: `# Add the
   ability to do "Bee" activities:`, `... "Fly" ...`, `... "Worm" ...`.
   Same formula three times over. Consider something more direct per
   class, e.g. `# Bee pollinates:`. Needs a re-sync (`make verify`) if
   applied.
2. **Listing comment, first person.** `flower_visitors.py` line 82:
   `# Now we can perform Bug operations on Flowers:`. The book is
   second person; the "we" doesn't match. Suggest `# Now perform Bug
   operations on the flowers:`. Needs a re-sync if applied.

## Considered and not flagged

- **Repeated italics on *Visitor*, *Multiple Dispatching*, and *GoF
  Design Patterns*.** These recur through the chapter (lines 3, 6, 13,
  134, 206, 211, 269). This is the book's standing convention for GoF
  pattern names, not the generic "first use only" rule the emphasis
  check looks for, so it's a different case from A3's stray "*which*".
- **"The `Any` is the quiet price of the empty base, the same bargain
  [Data Transfer Objects] paid for its attribute bag" (line 124-126).**
  Reads like an aphorism formula on the surface, but it's anchored to a
  specific, real cross-reference and states an actual shared tradeoff
  between two chapters rather than gesturing at vague profundity. Left
  alone.
- **"Adding a new operation is a new function. Adding a new flower is a
  class and, where needed, a one-line registration" (lines 201-202).**
  Looks like a broken parallel, but the asymmetry is real: an operation
  genuinely needs only a function, while a flower can need an extra
  registration step. Fixing the parallelism would misstate the code.
- **"Bee"/"Fly"/"Worm" and "Gladiolus"/"Ranunculus"/"Chrysanthemum"
  triples.** These look like a Rule-of-Three, but they're the actual
  domain classes in the listing, inherited from this pattern's running
  example, not a prose device.
- **"never" at line 185** ("`nectar()` calls it through the dispatcher,
  never by its own name") is a literal, factual claim about how
  `singledispatch` calls registered functions, not the rhetorical
  "never" the watch list targets. Left alone.
- **"hook" at lines 135 and 208** ("the `accept()` hook"). Standard
  software-engineering term for an extension point, not the marketing
  sense the watch list means. Left alone.
- **"hierarchy" recurring past the A1 paragraph.** It's the chapter's
  central technical noun and can't be avoided when explaining a pattern
  that's entirely about class hierarchies. Only the tight cluster in
  lines 6-11 reads as an echo; the rest is unavoidable vocabulary.

## Scan coverage

Clean, no hits: §7 AI-vocabulary word list, curly quotes, em dashes
(none appear in this chapter at all, not even the author's own), spaced
` -- `, emoji, boldface-header lists, inline-header vertical lists,
"Challenges and Future Prospects" formula, vague weasel attribution,
collaborative-communication artifacts, sycophantic tone, hedging,
false ranges, hyphenated-pair overuse, signposting/announcements,
fragmented headers, and `[[ ]]` draft notes. First-person "we" appears
exactly once, inside a listing comment (Housekeeping #2), not in prose.
