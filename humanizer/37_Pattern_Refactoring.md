# Humanizer candidates: Chapters/37_Pattern_Refactoring.md

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

Clean of the classic content-pattern tells: no AI vocabulary, curly quotes,
boldface-header lists, rule-of-three padding, or sycophantic/filler language.
The real findings are structural: a cluster of five first-person-plural
slips ("we"), a word echo on "honest" in the closing paragraph, and two
literal hits against Bruce's own watch list ("ships," "wants") used as
code/behavior metaphors. The single largest finding is the "we" cluster.

## Tier A

### A1 — lines 5, 12, 96, 270, 330 — person consistency ("we")

Five first-person-plural slips, the same pattern flagged and converted in
chapters 46 and 47. None of these look like a deliberate "let's work through
this together" aside; each reads as leftover drafting voice.
Delete individual rows you want left alone.

**line 5**

CURRENT
```text
then we ask "what will change?" and reshape the design to absorb that change cheaply.
```

PROPOSED
```text
then you ask "what will change?" and reshape the design to absorb that change cheaply.
```

**line 12**

CURRENT
```text
We will point that out as it happens.
```

PROPOSED
```text
This chapter points that out as it happens.
```

**line 96**

CURRENT
```text
We test that each subclass registers itself, `create()` builds one by name,
```

PROPOSED
```text
The tests confirm that each subclass registers itself, `create()` builds one by name,
```

**line 270**

CURRENT
```text
We can use a dictionary keyed by type:
```

PROPOSED
```text
You can use a dictionary keyed by type:
```

**line 330**

CURRENT
```text
We have changed *types* cheaply so far.
```

PROPOSED
```text
This chapter has changed *types* cheaply so far.
```

### A2 — lines 410, 413 — word echo, "honest"

"Honest" twice in four lines, in a chapter's closing paragraph, and it is on
your own "Avoid if possible" watch list. Neither use is load-bearing.
Delete individual rows you want left alone.

**line 410**

CURRENT
```text
This chapter discovered its vectors the honest way, one requirement at a time,
```

PROPOSED
```text
This chapter discovered its vectors one requirement at a time,
```

**line 413**

CURRENT
```text
The honest measure of a pattern is whether it is still useful once the language does part of the work.
```

PROPOSED
```text
The true measure of a pattern is whether it is still useful once the language does part of the work.
```

### A3 — line 261 — flourish word, "exactly"

On the watch list under "Avoid 'exactly.'" It intensifies a claim of identity
that the sentence can carry without it.

CURRENT
```text
This is a `match` over an open set,
exactly what [Pattern Matching](13_Pattern_Matching.md#when-not-to-match)
warned against.
```

PROPOSED
```text
This is a `match` over an open set,
which is what [Pattern Matching](13_Pattern_Matching.md#when-not-to-match)
warned against.
```

### A4 — line 251 — emphasis italics, not a term introduction

Nothing new is being named here; the italics just lean on the word for
emphasis, which CLAUDE.md's italics rule reserves for first-use terms.

CURRENT
```text
It tests for *every type in the system*.
```

PROPOSED
```text
It tests for every type in the system.
```

### A5 — line 332 — "ships" as a stand-in for the real thing

"Ships" is on the "Don't use" tier of the watch list. The literal claim is
that the hierarchy comes from code you don't own or edit; say that.

CURRENT
```text
Suppose the `Trash` hierarchy is fixed (maybe it ships from a vendor)
```

PROPOSED
```text
Suppose the `Trash` hierarchy is fixed (maybe it comes from a third-party library)
```

### A6 — line 325 — "wants" as a stand-in for the real thing

Also on the "Don't use" tier. "A sorter usually wants X" anthropomorphizes
where "needs" says the same thing plainly.

CURRENT
```text
not its parent's, which a sorter usually wants,
```

PROPOSED
```text
not its parent's, which a sorter usually needs,
```

## Tier B

### B1 — line 331 — italics on "operations," paired with line 330's "types"

The concluding section restates the same pair, "new types versus new
operations" (line 408), with no italics at all. That consistency argument
cuts against these being term introductions rather than plain emphasis.
Arguable because this is the first mention of the operations side of the
vector-of-change pair, so a case exists for keeping it. If you drop this
one, the paired `*types*` in A1's line-330 row should probably match, edit
that PROPOSED fence too rather than leaving one italicized and one not.

CURRENT
```text
The other axis of change is adding new *operations*.
```

PROPOSED
```text
The other axis of change is adding new operations.
```

### B2 — line 404 — italics over a full clause

A whole clause in italics reads more like typographic emphasis than a term
introduction. The paragraph's actual new term, `*vector of change*`, arrives
two sentences later and is the one that gets a chapter link, which is the
stronger claim to italics.

CURRENT
```text
Design patterns are about *separating things that change from things that stay the same*.
```

PROPOSED
```text
Design patterns are about separating things that change from things that stay the same.
```

### B3 — lines 319, 396 — "even" as intensifier

Both are on the "Avoid if possible" tier, and both arguably earn their place:
one marks that runtime-registered types still work with no special case, the
other underlines that some operations need no dispatch construct at all. I
lean toward keeping these; flagging for completeness.
Delete individual rows you want left alone.

**line 319**

CURRENT
```text
`type(t)` is the perfect key because it adapts to new types,
even ones added at runtime.
```

PROPOSED
```text
`type(t)` is the perfect key because it adapts to new types,
including ones added at runtime.
```

**line 396**

CURRENT
```text
When the operation is the same for every type,
you do not even need single dispatch.
```

PROPOSED
```text
When the operation is the same for every type,
you do not need single dispatch.
```

### B4 — line 87 — "already" as timing marker

On the "Avoid if possible" tier. It marks that the declaration on `Trash`
precedes the subclass, which is a real (if minor) point about the MRO
lookup. Borderline; I lean toward keeping it.

CURRENT
```text
They don't need to because the checker resolves `value` through the MRO and finds it already declared `ClassVar[float]` on `Trash`.
```

PROPOSED
```text
They don't need to because the checker resolves `value` through the MRO and finds it declared `ClassVar[float]` on `Trash`.
```

## Housekeeping

None found. No double blank lines, no `[[ ]]` draft notes, no spaced ` -- `,
and no Semantic Line Break drift: the prose already breaks by sentence and
clause throughout.

## Considered and not flagged

- **`*closed*` (line 257).** Introduces the technical qualifier a closed
  union needs for exhaustiveness checking, contrasted against the open
  registry two lines later. Reads as a genuine first-use term, not emphasis.
- **`*exact*` (line 321).** Recalls the exact-type dispatch concept
  established in [Multiple Dispatching](32_Multiple_Dispatching.md), linked
  in the same sentence. Marks a real technical nuance (exact class versus
  `isinstance`-style matching), not decoration.
- **`*double dispatch*`, `*Visitor*` (lines 340, 346).** Legitimate term and
  pattern-name introductions, consistent with how the chapter treats other
  pattern names elsewhere.
- **"Nothing needs maintaining, and nothing gets forgotten." (line 320).**
  Reads like a parallel-negation pair on first glance, but each clause pays
  off a distinct concern raised in the previous section (the maintenance
  burden of enumerating cases, and the risk of a missed one). Not vague
  filler; left alone.
- **"No `Visitor` class exists, no `accept()` method bolted onto every
  material, and no decorator gymnastics to fake overloading." (lines
  392-393).** Looks like Rule-of-Three padding, but each item is a specific,
  concrete technical claim rather than synonym-cycling on one vague idea.
- **"never" (lines 94, 153).** Both state a real invariant about the code
  (the function never inspects a type, the parser never names a material),
  not a filler intensifier.
- **Heading-echo after "Let a Dictionary Do the Sorting" (line 270, fixed
  in A1).** The line right after the heading restates its content, which
  looks like the fragmented-header tell. Judged a legitimate one-line lead-in
  ending in a colon before the code block, not padding; not flagged
  separately from the person fix already proposed there.
- **"Testing parses a small in-memory file..." (line 173).** "Testing" as a
  bare gerund subject reads slightly informal but is clear; left alone.

## Scan coverage

Zero hits on: AI vocabulary (testament, underscore, delve, crucial, pivotal,
showcase, tapestry, intricate, garner, enduring, vibrant, landscape, align
with, fostering), curly quotes, emoji, boldface-header lists, inline-header
vertical lists, promotional/advertisement language, vague attribution,
"Challenges and Future Prospects" sections, sycophantic tone,
knowledge-cutoff disclaimers, generic positive conclusions, false ranges,
elegant variation, negative parallelism ("not only... but"), aphorism
formulas, persuasive-authority tropes, diff-anchored writing, signposting
announcements, and conversational rhetorical openers. Word-level scanning
was, as with chapters 46 and 47, mostly a dead end; the real findings came
from structure (person, echo, italics-as-emphasis) and from Bruce's own
watch list.
