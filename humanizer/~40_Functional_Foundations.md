[[Reviewed]]
# Humanizer candidates: Chapters/40_Functional_Foundations.md

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

A clean chapter. Ten Tier A blocks, and half of those are single words
from your own watch list ("spells"/"spelling", "ships", "exactly",
"way out", "at all") rather than anything the humanizer skill would catch.
The largest finding is structural and not a word at all: the payoff of
purity is stated three times in the first two pages, once in the chapter
opener, once before `pure_functions.py`, and once after it, with the
middle statement adding nothing the third does not say better (A2).
A second, smaller echo of the same kind closes the Composing section (A9).
Zero first-person-plural slips, zero hits on the §7 vocabulary list,
no fragmented headers, no curly quotes, no emoji, no boldface.
Housekeeping is empty except for two observations.

## Tier A

### A1 — line 4 — §28 announcement, plus "buy"

The sentence announces the list that follows instead of starting it,
and "buy" is on the avoid-if-possible list. The rewrite keeps the point
(payoffs first, terms later) as a claim rather than a preamble.
Deleting the line outright also works; the list reads fine unannounced.

CURRENT
```text
Here is what its ideas buy you, before the vocabulary arrives.
```

PROPOSED
```text
The ideas pay off before the vocabulary arrives.
```

### A2 — lines 36-40 — the payoff stated twice, ten lines apart

The paragraph after `pure_functions.py` (lines 66-75) makes both of these
points at more length: "You test it with a single assertion and no fixture,
since there is nothing to set up or restore" is the testing claim, and
"A cache can store its results, knowing the answer will never go stale"
is the caching claim. Even "because what you pass in fully determines its
behavior" comes back as "because its behavior is fully described by its
inputs." Cutting the two middle sentences here also removes an
anaphoric "You can / You can / You can" triple, and leaves the paragraph
doing one job: lead into the listing. The chapter opener at lines 5-6
previews the same two payoffs a third time, so nothing is lost.

CURRENT
```text
Purity is the foundation on which everything else in these chapters builds.
You can test a pure function in isolation,
because what you pass in fully determines its behavior.
You can cache its result, because the answer never changes.
You can reason about it the way you reason about an equation:
```

PROPOSED
```text
Purity is the foundation on which everything else in these chapters builds.
You can reason about a pure function the way you reason about an equation:
```

### A3 — line 121 — "spells" and "spelling"

Both are on the don't-use list, and the sentence uses them twice in
fourteen words. "Writes" and "form" say the same thing literally.

CURRENT
```text
The demonstration spells the assignment `setattr(p, "x", 5)` because the direct spelling `p.x = 5` never gets to run:
```

PROPOSED
```text
The demonstration writes the assignment as `setattr(p, "x", 5)` because the direct form `p.x = 5` never gets to run:
```

### A4 — lines 123, 286 — emphasis italics

The chapter's other italics all introduce a term on first use
(*pure function*, *side effects*, *immutable*, *hashable*, *first-class*,
*higher-order function*, *lambda*, *closure*, *partial application*,
*function composition*). These two are emphasis, so they read as the odd
ones out. Both sentences already carry the contrast in their own words.
Delete individual rows you want left alone.

**line 123**

CURRENT
```text
`setattr()` slips past the static check so the listing can show the *runtime* rejection too.
```

PROPOSED
```text
`setattr()` slips past the static check so the listing can show the runtime rejection too.
```

**line 286**

CURRENT
```text
`map()` and `filter()` earn their keep when the function *already exists*:
```

PROPOSED
```text
`map()` and `filter()` earn their keep when the function already exists:
```

### A5 — line 159 — imperative plus consequence

"Declare X and Y still succeeds" commands the reader and then reports the
result. Written as a condition it stays one sentence and one line.

CURRENT
```text
declare `CONFIG: Final[list[int]] = [...]` and `CONFIG.append(...)` still succeeds,
```

PROPOSED
```text
if you declare `CONFIG: Final[list[int]] = [...]`, `CONFIG.append(...)` still succeeds,
```

### A6 — lines 203-204 — §9 negative parallelism

"A function value is not X. It is Y." is the "not just X, it's Y" shape,
split across two sentences. The preceding sentence has already said a
function is an object like any other, so the denial has nothing left to
correct and only delays the useful half.

CURRENT
```text
A function value is not special syntax.
It is data you can move around.
```

PROPOSED
```text
A function value is data you can move around.
```

### A7 — line 282 — "exactly" as an intensifier

Not a precise match, so the word is doing nothing.

CURRENT
```text
and for exactly these cases Python offers a lookalike you should usually prefer:
```

PROPOSED
```text
and for these cases Python offers a lookalike you should usually prefer:
```

### A8 — line 425 — "way out" and "at all"

Two watch-list hits in four words, and the metaphor stands in for a
literal statement. "Recourse" says it and drops both.

CURRENT
```text
A function whose parameters are positional-only
(see [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters))
had no way out at all.
```

PROPOSED
```text
A function whose parameters are positional-only
(see [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters))
had no recourse.
```

### A9 — line 490 — word echo across the paragraph break

Line 486 already says "Each piece stays small and pure," so "Each stage
stays small, pure, and testable on its own" repeats four of its words two
sentences later. Only "testable on its own" is new, and the rewrite keeps
it while pointing back at the earlier claim.

CURRENT
```text
Each stage stays small, pure, and testable on its own,
```

PROPOSED
```text
Each stage is also testable on its own,
```

### A10 — line 496 — "ships"

Don't-use list. "Provides" is the literal verb.

CURRENT
```text
The standard library ships these building blocks ready-made;
```

PROPOSED
```text
The standard library provides these building blocks ready-made;
```

## Tier B

### B1 — lines 124-125 — §31 staccato pair

Two three-word sentences in a row, each a single fact about the listing.
I lean toward merging: joined, they read as one observation about what the
non-mutating build produced, which is the point. Declining is reasonable
if you want the beat after the longer sentence above them.

CURRENT
```text
The original `p` is untouched.
`moved` is a separate value.
```

PROPOSED
```text
The original `p` is untouched, and `moved` is a separate value.
```

### B2 — lines 158, 375 — italics marking a contrast, not a term

The same rule as A4, but these two are the arguable cases: both italicize
one half of a real distinction (the binding against the object, assigning
against reading) rather than emphasizing for volume. I lean toward
dropping them for consistency with the rest of the chapter, and I would
not argue if you keep both. Delete individual rows you want left alone.

**line 158**

CURRENT
```text
It locks the *binding*, not the object:
```

PROPOSED
```text
It locks the binding, not the object:
```

**line 375**

CURRENT
```text
The `nonlocal` statement lets `increment()` *assign* to the captured variable.
```

PROPOSED
```text
The `nonlocal` statement lets `increment()` assign to the captured variable.
```

### B3 — line 307 — "already" twice in five lines

Line 311 needs its "already" ("where the reader already is" is the whole
argument for locality). This one marks nothing the reader could have
missed, since "The examples above" has said it. I lean toward cutting it.

CURRENT
```text
The examples above already used lambdas as inline arguments,
```

PROPOSED
```text
The examples above used lambdas as inline arguments,
```

### B4 — line 443 — "wants"

Don't-use list. A caller is closer to a person than a function is, so this
is the mildest form of the pattern, and line 407 already says "needs" for
the same relationship. I lean toward applying it for that consistency.

CURRENT
```text
which is the specialization a caller wants and the one `partial()` could not previously express.
```

PROPOSED
```text
which is the specialization a caller needs and the one `partial()` could not previously express.
```

### B5 — lines 447-448 — §8 copula avoidance, plus "just"

"Trailing placeholders are a syntax the library rejects" buries the actor
in a relative clause and makes the subject a syntax rather than the
placeholders. The rewrite names the actor and drops "just," which was
softening a claim that does not need it. I lean toward applying it, but
it is a rhythm change in a paragraph you may have tuned.

CURRENT
```text
Trailing placeholders are a syntax the library rejects for the same reason,
since a gap at the end is just an unbound parameter.
```

PROPOSED
```text
The library rejects trailing placeholders for the same reason:
a gap at the end is an unbound parameter.
```

## Housekeeping

1. Nothing to fix. No `[[ ]]` draft note, no spaced ` -- `, no em dash
   anywhere in the chapter, no curly quotes, no double blank line before
   any heading, no trailing whitespace.
2. Semantic Line Breaks look compliant. Fourteen prose lines run past 100
   characters (64, 121, 161, 194, 250, 287, 387, 409, 416, 424, 452, 458,
   504, 506), but each is a single clause or a long inline link with no
   top-level `,`/`;`/`:` to break at, so `make reflow CH=40` should have
   nothing to do. A3 and A8 shorten two of them anyway.

## Considered and not flagged

- **Line 30, "It reads nothing else and changes nothing else."** This is
  the allowed subject-or-object use, and it is the example `CLAUDE.md`
  itself gives for keeping the phrase. Left alone deliberately.
- **Line 66, "The payoff is trust."** One short emphatic sentence, not a
  run of them, and it is the paragraph's topic sentence. If A2 is applied
  this paragraph becomes the only place these points are made, which
  strengthens the case for keeping the opener.
- **Line 96, "the practical core of the functional style."** §27 shape,
  but the sentence that follows is not a restatement with ceremony, and
  the claim (removing shared mutable state is the practical part) is
  substantive.
- **Line 250, "This is the structure behind dispatch tables and the
  plugin registries that let a program grow without editing its core."**
  A §1 significance tail, but it names two real mechanisms rather than
  gesturing at a broader trend.
- **Lines 89-90, "is, in part, a way to keep more of your code pure."**
  "In part" reads as §24 hedging, but the qualifier is accurate: some
  later features are about more than purity. Deleting it overclaims.
- **Lines 200 and 301, "This is what *first-class* means" and "This is
  what a decorator does."** Both are the keep case for "is what": what
  follows cannot attach without it.
- **Line 346, "A closure is the functional answer to 'an object with one
  method and some stored data.'"** §32 aphorism shape, but the quoted
  phrase is the concrete claim, not a substitute for one.
- **"never" x8** (7, 39, 75, 97, 121, 126, 194, 249). On the
  avoid-if-possible list, but this is a chapter about values that do not
  change and answers that do not go stale. Every hit is the literal word.
- **"already" x5** (8, 286, 307, 311, 405). A4 drops the italics on one
  and B3 proposes cutting one; the other three mark a real prior state.
- **Rule-of-three lists** (14, 194, 300, 315, 317-318). Real enumerations
  where each item carries its own information, not padding to sound
  comprehensive.
- **Line 255, "Three built-ins are the workhorses."** Colloquial and
  human; the count is real.
- **Line 166, "Immutability also unlocks abilities a mutable value
  lacks."** Figurative "unlocks," but the next three lines name both
  abilities, so it introduces rather than decorates.
- **Line 421, "Positional arguments have no such freedom."** Mild
  personification, ordinary in technical prose, and it sets up the
  restriction the section exists to lift.
- **§26 predicate-position hyphens.** "are positional-only" (423) is
  predicate position, but it is Python's own term (and the anchor text of
  the heading it links to), so the hyphen stays. Every other compound
  ("higher-order", "first-class", "read-only", "single-argument",
  "off-by-one", "shallow-freezing") is attributive.
- **Lines 18-25, the chapter roadmap.** Four forward links with one clause
  each. Not §28: it is a genuine map, not an announcement of the next
  paragraph.
- **All eight `##` headings.** None is followed by a line restating it, so
  §29 found nothing here, and no heading edit is proposed by rule anyway.
- **Everything inside a fence.** The `# type: ignore` comments at 435-436
  and every `#:` marker are out of scope by rule.

## Scan coverage

The word-level half of the skill was clean: no hits on the §7
AI-vocabulary list, no curly quotes (§19), no emoji (§18), no boldface
(§15), no inline-header vertical lists (§16), no promotional language
(§4), no vague attributions (§5), no false ranges (§12), no filler
phrases (§23), no collaborative artifacts (§20), no cutoff disclaimers
(§21), no sycophancy (§22), no diff-anchored writing (§30), no
conversational rhetorical openers (§33), and no generic positive
conclusion (§25: the chapter ends on two lines pointing at Toolkits).
§29 fragmented headers: none. Person: zero instances of "we", "us", or
"our" anywhere in the chapter, so no conversion is needed. §11 elegant
variation found nothing either, and note that the chapter's deliberate
term reuse (pure, immutable, closure) is correct rather than an echo. All
ten Tier A findings came from structure (§9, §28, §31, echoes) or
from the `CLAUDE.md` watch list, not from the pattern vocabulary.
