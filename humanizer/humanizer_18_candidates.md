# Humanizer candidates: Chapters/18_Performance.md

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

Mostly clean. No AI vocabulary, no curly quotes, no em-dash issues,
no boldface-header lists, no signposting, no chatbot artifacts, no
`[[ ]]` notes. The chapter's real findings are small and specific: one
direct hit on the promotional-language watch list ("boasts a"), one
banned word ("wants"), one leftover "we" in an otherwise second-person
chapter, an "is what" cleft, and two italics used for emphasis instead
of term introduction. The single biggest finding is "boasts a" at
line 35, a verbatim match against §4/§8's watch list, the kind of hit
chapters 46 and 47 didn't have at all.

## Tier A

### A1 — line 35 — promotional language / copula avoidance

"Boasts a" is a verbatim hit on both the §4 (promotional language) and
§8 (copula avoidance) watch lists.

CURRENT
```text
Alternative interpreters for Python exist, notably PyPy,
which boasts a 4x to 10x speedup.
```

PROPOSED
```text
Alternative interpreters for Python exist, notably PyPy,
which claims a 4x to 10x speedup.
```

### A2 — line 46 — person consistency

The book is second person, but this sentence starts in "you" and
finishes in "we" mid-thought.

CURRENT
```text
Although it is tempting to think you "have a pretty good idea where the slowdown is,"
we turn out to be bad at guessing this.
```

PROPOSED
```text
Although it is tempting to think you "have a pretty good idea where the slowdown is,"
you turn out to be bad at guessing this.
```

### A3 — lines 189 and 203 — italics for emphasis, not term introduction

CLAUDE.md's rule: italics only introduce a new term on first use. Neither
"at this location" nor "where" is a term being introduced; both are
emphasis, the misuse the rule exists to catch. Delete individual rows
you want left alone.

**line 189**

CURRENT
```text
Returning `monitoring.DISABLE` tells the interpreter to stop reporting this event *at this location*,
```

PROPOSED
```text
Returning `monitoring.DISABLE` tells the interpreter to stop reporting this event at this location,
```

**line 203**

CURRENT
```text
A profiler tells you *where* the time goes.
```

PROPOSED
```text
A profiler tells you where the time goes.
```

### A4 — line 192 — "is what" cleft

Deleting "is what" changes nothing: "That makes coverage measurement
affordable" reads the same.

CURRENT
```text
That is what makes coverage measurement affordable:
```

PROPOSED
```text
That makes coverage measurement affordable:
```

### A5 — line 612 — banned word "wants"

"Wants" is on CLAUDE.md's "Don't use" tier ("the function wants a
string" means it takes or requires one). It also sits one line below
"needs the same thing," so swapping to "needs" would create a new echo;
"requires" avoids both problems.

CURRENT
```text
It wants a whole array in memory, not values arriving one at a time.
```

PROPOSED
```text
It requires a whole array in memory, not values arriving one at a time.
```

### A6 — lines 1005-1006 — word echo in adjacent sentences

"Your AI" opens one sentence and closes the previous one. A pronoun in
the second sentence removes the echo without losing the antecedent.

CURRENT
```text
More importantly, you can pass the hot Python function to your AI for conversion to Rust.
Your AI can also walk you through the process.
```

PROPOSED
```text
More importantly, you can pass the hot Python function to your AI for conversion to Rust.
It can also walk you through the process.
```

## Tier B

### B1 — lines 1003-1009 — choppy run of short sentences with filler transitions

Seven sentences in a row, several of them clipped ("It just runs
faster."), bookended by "More importantly" and "In addition," two
transition words doing no real work. I lean toward tightening this:
it reads like a bullet list unrolled into prose rather than a
paragraph someone spoke aloud. But it's also the chapter's most
conversational stretch, right where it pitches an unusual workflow
(asking your AI to port a function to Rust), so some of the looseness
may be deliberate voice. Taking this supersedes A6 above, since the
rewrite removes the "your AI"/"Your AI" echo along with everything else.

CURRENT
```text
One effective technique is to move the hot function into a compiled language.
Rust is excellent for this because its tooling makes the bridge nearly painless.
More importantly, you can pass the hot Python function to your AI for conversion to Rust.
Your AI can also walk you through the process.
Once you're done, you import a module that looks from the outside like any other Python module.
It just runs faster.
In addition, you can do things in Rust that might be much more difficult in Python.
```

PROPOSED
```text
One effective technique is to move the hot function into a compiled language.
Rust is excellent for this because its tooling makes the bridge nearly painless: you can hand the hot Python function to your AI for conversion, and it can walk you through the rest of the process.
Once you're done, you import a module that looks from the outside like any other Python module, except that it runs faster, and lets you do things that are difficult in Python.
```

### B2 — line 149 — clarity, not a classic AI tell

Not on any watch list, but "claiming one another tool is holding"
drops the relative pronoun ("that") in a spot dense enough to slow a
reader down. Genuinely arguable: the terser original may be exactly
the register Bruce wants here.

CURRENT
```text
and claiming one another tool is holding raises a `ValueError`,
```

PROPOSED
```text
and claiming one that another tool already holds raises a `ValueError`,
```

## Housekeeping

None found. No double blank lines before headings, no `[[ ]]` draft
notes, no spaced ` -- `, and no em dashes anywhere in the chapter. The
long lines a raw column-width scan flags (e.g. line 39, line 99) are
each a single clause with no internal comma or colon to break at, so
they're already compliant with Semantic Line Breaks rather than drift.

## Considered and not flagged

- **Italics used correctly.** *premature optimization* (13), *profiler*
  (44), *sampling* (62), and *heap* (419) each introduce a term on its
  first formal use in prose, immediately after the heading names the
  topic. This is a repeated, deliberate convention, not a tell.
- **Fragmented headers (§29).** Checked every heading in the chapter.
  Several opening sentences echo the heading's own word ("Profilers" /
  "A *profiler* looks for...", "Heap" / "a *heap* keeps...", "Choose
  Better Algorithms" / "a better algorithm") but each is a real,
  substantive definition or claim, not the vacuous "Speed matters."
  restatement the pattern describes. None qualify.
- **"Numba shines" (line 927).** Adjacent in spirit to promotional
  language but not a verbatim hit on the §4 list, and "shines at X" is
  ordinary idiomatic usage for describing a tool's strength. Left alone.
- **"Hook"/"hooks" (lines 93, 150).** Literal PEP 669 vocabulary (the
  interpreter's actual "hook mechanism"), not the metaphorical "hooks"
  CLAUDE.md's banned list targets. Left alone.
- **Rule-of-three groupings.** Three membership-testing methods in
  "Comparison," three memory tools under "Reduce Memory Overhead,"
  three deferred NumPy/Numba/Rust examples. Each is a real, distinct
  count from the material, not an invented triad. Left alone.
- **Repeated parenthetical refrain** ("Expect a different, but still
  large, multiple on yours," lines 888, 936, 996). Verbatim three
  times, but across three structurally parallel deferred-example
  asides; consistent framing, not filler repetition. Left alone.
- **"The goal is not the fastest possible program. It is a program that
  is fast enough..." (lines 1172-1173).** Reads close to the §9
  negative-parallelism formula but makes one specific, real claim
  rather than a formulaic double negation. Left alone.
- **"Only," "already," "even," "plain."** All appear (e.g. "only
  O(log n)," "the plain Python loop"), each doing real, precise work
  contrasting one approach against another. None are flourish uses.

## Scan coverage

No hits anywhere in the chapter for: §7 AI vocabulary (crucial, delve,
tapestry, testament, underscore, etc.), §15 boldface overuse, §16
inline-header vertical lists, §18 emoji, §19 curly quotes, §20-22
chatbot-communication artifacts/disclaimers/sycophancy, §23-24 filler
phrases and hedging, §26 hyphenated-pair overuse, §27 persuasive-
authority tropes ("at its core," "the real question"), §28 signposting
("let's," "here's what"), §32 aphorism formulas, §33 rhetorical
openers ("honestly," "look,"), the "nothing else" family (already swept
book-wide), stranded prepositions, and `raise`/`raises` without an
object (the one instance in the chapter already has one). Person
consistency was checked in full: the single "we" at line 46 is the
only first-person-plural slip in the chapter.
