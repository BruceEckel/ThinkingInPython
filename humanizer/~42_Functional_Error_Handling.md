[[Reviewed]]
# Humanizer candidates: Chapters/42_Functional_Error_Handling.md

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

Clean at the word level: no §7 AI-vocabulary hits, no curly quotes, no
emoji, no promotional or notability language, no hedging, no filler
phrases, no signposting, no staccato drama, no aphorism formulas. No em
dashes anywhere in the chapter, so nothing to preserve there either.

The findings are small and structural: two first-person-plural "we"
slips against the book's second person (A1), one emphasis italic that
isn't introducing a term (A2), and one arguable §29 fragmented header
(B1). The clearest single fix is three literal `CLAUDE.md`-banned
words used as ordinary metaphor: "rides on" (A3), "spelling" (A4), and
"near-miss" (A5), each with a one-word literal replacement. No
housekeeping issues turned up at all.

## Tier A

### A1 — lines 98, 594 — person consistency

The book is second person. These two "we" sightings are the author
addressing the reader as a collaborator, the pattern chapters 46 and 47
converted everywhere except a couple of deliberate exceptions. Neither
site here matches those exceptions (no acknowledgment, no "let's see").
Delete individual rows you want left alone.

**line 98**

CURRENT
```text
We need something that says "success" or "failure" no matter what types they carry.
```

PROPOSED
```text
You need something that says "success" or "failure" no matter what types they carry.
```

**line 594**

CURRENT
```text
the same `@safe` decorator we just built,
```

PROPOSED
```text
the same `@safe` decorator built earlier in the chapter,
```

### A2 — line 178 — emphasis italic

The chapter has three term-introducing italics (*sum type*, *Total
Function*, *monad*), all correct on first use. This one emphasizes an
ordinary word instead.

CURRENT
```text
Both force the caller to unpack, but `None` says only "no answer,"
while an `Err` carries *why*.
```

PROPOSED
```text
Both force the caller to unpack, but `None` says only "no answer,"
while an `Err` carries the reason for the failure.
```

### A3 — line 96 — banned metaphor "rides on"

On `CLAUDE.md`'s "Don't use" list. Says what it means.

CURRENT
```text
But the distinction rides on the types `int` and `str`, which is fragile.
```

PROPOSED
```text
But the distinction depends on the types `int` and `str`, which is fragile.
```

### A4 — lines 175-176 — banned word "spelling"

Also on the "Don't use" list; the example there is almost this exact
sentence shape ("the annotation's spelling" means its written form).

CURRENT
```text
Python's humbler spelling of the same idea is `int | None`,
and the comparison locates `Result`'s value.
```

PROPOSED
```text
Python's humbler form of the same idea is `int | None`,
and the comparison locates `Result`'s value.
```

### A5 — line 302 — banned word "near-miss"

Also on the "Don't use" list. What follows describes an actual mistake
(feeding `bind()` a plain function), not something that almost
happened and didn't.

CURRENT
```text
One near-miss to expect when you start chaining:
```

PROPOSED
```text
One mistake to expect when you start chaining:
```

## Tier B

### B1 — lines 61-66 — §29 fragmented header

"Return the Error as a Value" is immediately restated as "The
alternative is to return the error." before the real content starts.
Same pattern as chapter 47's B1, which was applied, and chapter 46's
A5, which was declined; a per-instance call. Heading text is unchanged
in both fences.

CURRENT
```text
## Return the Error as a Value

The alternative is to return the error.
The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Nothing disappears, because the error is just another return value:
```

PROPOSED
```text
## Return the Error as a Value

The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Nothing disappears, because the error is just another return value:
```

## Housekeeping

None. No double blank line before any heading, no Semantic Line Break
drift, no `[[ ]]` draft notes, no spaced ` -- `, no em dashes to check
in either direction.

## Considered and not flagged

- **Two more §29 near-misses.** "A Result Type" opens with "Make
  success and failure explicit by defining them as types," and
  "Composing by Hand" opens with "Real programs chain steps." Both
  echo their heading's topic, but each moves straight into real content
  rather than pausing on a pure restatement, so only line 61's instance
  (B1) is worth flagging.
- **Line 513, "the exception you already have."** On the avoid-if-
  possible list, but it draws a real contrast with "raise a new one" in
  the sentence just before it. Left alone.
- **"only" at lines 57, 177, 357, 428.** Each is load-bearing
  (a genuine single way, a genuine contrast, a genuine sole survivor,
  a genuine restriction on what `@safe` changes), not a filler
  intensifier.
- **Lines 354-357, three short sentences in a row** ("Nested binds
  carry each answer inward. An `Err` anywhere short-circuits to the
  end. Only the last input passes all three steps..."). Reads as a
  compact recap of the trace just shown, not manufactured staccato
  drama.
- **Lines 578-579, the three-part "Err says / exception says / note
  says" sentence.** A rule of three, but each of the three names a
  distinct real thing the chapter just built, not padding.
- **Exercise imperatives.** "Add a `func_e()`," "Give `Err` a
  `map_error()` method," "Rewrite `combined`." Real instructions,
  exempt from the imperative-plus-consequence rule.
- **Listing comments.** Every `#` comment inside a fenced block was
  checked; none carries a watch-list word, an editorial "we," or
  anything else reviewable. All are either filename headers or short
  code annotations.

## Scan coverage

The word-level half of the skill found nothing: no hits on the §7
AI-vocabulary list, no curly quotes, no emoji, no boldface-header
vertical lists, no promotional language (§4), no vague attributions
(§5), no challenges-and-prospects section (§6), no copula avoidance
(§8), no negative parallelisms (§9), no false ranges (§12), no
collaborative artifacts (§20), no cutoff disclaimers (§21), no
sycophancy (§22), no filler phrases (§23), no hedging stacks (§24), no
generic positive conclusion (§25), no hyphenated-pair overuse (§26), no
persuasive authority tropes (§27), no signposting (§28), no
manufactured staccato drama (§31), no aphorism formulas (§32), no
conversational rhetorical openers (§33), no diff-anchored writing
(§30). Every finding above is either person, an emphasis italic, one
fragmented header, or a `CLAUDE.md` banned-word hit.
