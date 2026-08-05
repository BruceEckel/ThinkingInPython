# Humanizer candidates: Chapters/13_Pattern_Matching.md

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

This chapter is clean. No word-level AI vocabulary, no curly quotes,
no boldface-header lists, no sycophancy, no rule-of-three padding,
no person-consistency slips, and no em dashes to protect (the chapter
has none). What surfaced is small: two italics used for emphasis rather
than term introduction, two short-range word echoes, and one
heading immediately followed by a one-line restatement of itself. The
single largest finding is the "When Not to Match" fragmented header,
and even that is a judgment call Bruce has gone either way on before.

## Tier A

### A1 — lines 160, 583 — italics used for emphasis, not term introduction

Both italicize an ordinary word for emphasis. The chapter's other
italics (`*patterns*`, `*capture pattern*`, `*exhaustive*`,
`*expression problem*`) all introduce a term on first use; these two
don't introduce anything new.

**line 160**

CURRENT
```text
`Point(0, y)` matches when `x` is zero and *captures* `y`.
```

PROPOSED
```text
`Point(0, y)` matches when `x` is zero and captures `y`.
```

**line 583**

CURRENT
```text
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union *without* adding its `case`.
```

PROPOSED
```text
2.  Add a `Rectangle` type to `exhaustive.py`'s `Shape` union without adding its `case`.
```

Delete individual rows you want left alone.

### A2 — lines 170-174 — word echo, "Keyword patterns work..."

The paragraph opens and re-opens with the same subject and verb three
sentences apart. The second occurrence carries a different point
("these also work on any object") that doesn't need the repeated
subject to make it.

CURRENT
```text
Keyword patterns work differently.
`Point(x=0, y=y)` matches by attribute name directly, through attribute access,
not through `__match_args__`.
Keyword patterns work on any object with the named attributes, dataclass or not,
and they let you match a subset of attributes while ignoring the rest:
```

PROPOSED
```text
Keyword patterns work differently.
`Point(x=0, y=y)` matches by attribute name directly, through attribute access,
not through `__match_args__`.
They also work on any object with the named attributes, dataclass or not,
and let you match a subset of attributes while ignoring the rest:
```

### A3 — lines 311-312 — word echo, two sentences opening with "This"

Adjacent sentences both start with "This," and the second "This is"
reads as a restatement of the first rather than a new point.

CURRENT
```text
This error is caught during type checking rather than silently falling through.
This is the static-typing payoff applied to control flow:
```

PROPOSED
```text
This error is caught during type checking rather than silently falling through.
That is the static-typing payoff applied to control flow:
```

## Tier B

### B1 — lines 373-377 — fragmented header, "When Not to Match"

The heading is followed by a one-line paragraph that just restates the
heading's negative framing before the real content (the dictionary
comparison) starts. This is the same pattern flagged in chapters 46 and
47, where Bruce declined it once and accepted it once, so it's a
per-instance call rather than a rule. I lean toward cutting it: the
sentence doesn't add information the heading and the following
paragraph don't already carry.

CURRENT
```text
## When Not to Match

`match` is not a replacement for everything.

For a value-to-value lookup, a dictionary is shorter and faster:
```

PROPOSED
```text
## When Not to Match

For a value-to-value lookup, a dictionary is shorter and faster:
```

## Housekeeping

1. Line 348 has a stray comma before the verb: "A `switch` in C,
   JavaScript, or traditional Java, cannot do this." The comma after
   "Java" splits subject from verb; it likely should read "...or
   traditional Java cannot do this." Not a humanizer pattern, just a
   copyediting nit noticed during the read.

## Considered and not flagged

- **"and nothing else changes" (line 558).** Matches the CLAUDE.md
  exception directly: "nothing else" as a subject/object is ordinary
  English and stays. This is the same construction the rule's own
  example uses.
- **"The channels become plain data," (line 482).** "Plain" draws a
  real contrast here, data versus the behavior-carrying objects of the
  preceding OO paragraph, the same test the CLAUDE.md rule applies to
  "a plain `for` loop." Kept.
- **Asymmetric italics on "open" vs. "closed" (lines 395, 399).**
  `*open*` is italicized as a first-use technical term; its paired
  opposite "closed" two sentences later isn't. Read as an authorial
  choice (only the less obvious member of the pair gets the
  introduction), not a clear tell. Near-miss, left alone.
- **"matches any point" / "matches any `Point` instance" (lines 201,
  204).** Same verb reused to describe what two different patterns
  match. Reads as necessary technical parallelism (both sentences are
  answering "what does this pattern match"), not an accidental echo.
  Near-miss, left alone.
- **"valuable" (line 40).** On the §7 AI-vocabulary watch list, but a
  single ordinary use ("`match` becomes valuable once..."), not part of
  a cluster. Left alone per the false-positive guidance: one hit means
  nothing.
- **"Try growing the system in each direction. First, add a new
  type... Now try adding a new operation..." (lines 554-565).** Reads
  like tutorial narration but is a genuine second-person instruction to
  the reader to work through both directions of the expression-problem
  tradeoff, not a meta-announcement of what the prose is about to do.
  Left alone.

## Scan coverage

Zero hits on: §7 AI vocabulary (delve, crucial, tapestry, testament,
underscore, pivotal, etc.), copula avoidance, negative parallelisms and
tailing negations, rule-of-three padding, elegant variation, false
ranges, hyphenated-pair overuse, boldface/inline-header lists, emoji,
curly quotes, knowledge-cutoff disclaimers, sycophantic tone, filler
phrases, excessive hedging, generic positive conclusions, persuasive-
authority tropes ("at its core," "the real question"), signposting
("let's dive in"), aphorism formulas, manufactured punchlines/staccato
drama, conversational rhetorical openers, stranded prepositions, bare
"raise," and first-person-plural slips (no "we"/"us"/"our" anywhere in
the chapter). The chapter also has no em dashes at all, so there was
nothing to protect. Listing comments: the only inline comment in any
code block is `# Default` on line 27, one word, no finding.
