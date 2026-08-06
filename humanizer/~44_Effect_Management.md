[[Reviewed]]
# Humanizer candidates: Chapters/44_Effect_Management.md

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
quotes, no emoji, no promotional language, no hedging stacks, no filler
phrases, no upbeat send-off. The one non-ASCII pair is your ⊥.

The largest finding is person. Fourteen first-person-plural sites, against
two survivors in each of chapters 46 and 47. Five are editorial "we"
(A1); five more form the collective "we" of the closing section, which
may be deliberate (B1). Everything else is structural and small:
one announcement, one word echo, one stranded preposition, three emphasis
italics.

One housekeeping item matters more than any edit here: line 791's "The next
chapter" now means Generators, not Stateless.

## Tier A

### A1 — lines 3, 41, 106, 197, 489 — person consistency

The book is second person, and chapters 46 and 47 were converted to it.
These five are editorial "we" (the author addressing the reader), not the
genuine plural you kept at 46's line 28. The closing section's "we" is a
different case and sits in B1. Delete individual rows you want left alone.

**lines 3-4**

CURRENT
```text
In numerous places throughout this book,
we have emphasized the benefits of pure functions:
```

PROPOSED
```text
This book has emphasized the benefits of pure functions in numerous places:
```

**line 41** (also fixes "other than returning" to "other than return",
and brings a 100-character line under the limit)

CURRENT
```text
We say that a function has *side effects* if calling it does anything other than returning a result.
```

PROPOSED
```text
A function has *side effects* if calling it does anything other than return a result.
```

**line 106**

CURRENT
```text
    as we saw in [Error Handling](42_Functional_Error_Handling.md).
```

PROPOSED
```text
    as you saw in [Error Handling](42_Functional_Error_Handling.md).
```

**lines 197-199** — also §28: the paragraph announces itself twice before
doing anything. Note the precedent: you kept one "Let's see what happens
when we don't supply" in chapter 46, so this is a per-instance call.

CURRENT
```text
Let's revisit `slope()` from `divide_by_zero_impurity.py`.
We can transform the exception Effect, which makes the function pure again.
Here are three ways to do it.
```

PROPOSED
```text
Transforming the exception Effect in `slope()` from `divide_by_zero_impurity.py`
makes the function pure again.
Here are three ways to do it.
```

**line 489**

CURRENT
```text
We'll call this a *native* Effect system.
```

PROPOSED
```text
This is a *native* Effect system.
```

### A2 — lines 34-36 — §28 announcement, plus a nominalization

"perform purity verification" is the "has the ability to process" shape from
§23. The trailing clause announces the chapter instead of starting it, and
the heading above already says Effect Management.

CURRENT
```text
It would be great if the type checking system could perform purity verification.
This is called an *Effect Management System*,
and this chapter explores aspects of Effect Management.
```

PROPOSED
```text
It would be great if the type checking system could verify purity for you.
A system that does this is called an *Effect Management System*.
```

### A3 — lines 141-142 — §13 subjectless fragment

The second line is a verbless fragment plus a semicolon-spliced tag, and it
repeats the first line's claim. One sentence carries both.

CURRENT
```text
Neither `compute_and_discard()` nor `do_nothing()` produces anything.
No prints, writes, or returns; nothing a caller can act on.
```

PROPOSED
```text
Neither `compute_and_discard()` nor `do_nothing()` prints, writes,
or returns anything a caller can act on.
```

### A4 — line 184 — §28 "Notice that"

Telling the reader to notice rather than stating the point. Same family as
chapter 47's "The trace shows two things worth noticing," which was applied.
The next line, "That is not a coincidence," still lands.

CURRENT
```text
Notice that in almost every case, testing is a benefit of Effect Management.
```

PROPOSED
```text
In almost every case, testing is a benefit of Effect Management.
```

### A5 — lines 342-343 — word echo in adjacent clauses

"hidden life" twice in one sentence.

CURRENT
```text
Most functions in most programs have this hidden life,
and the hidden life makes code hard to understand:
```

PROPOSED
```text
Most functions in most programs have this hidden life which makes code hard to understand:
```

### A6 — line 474 — stranded preposition

Ends on "for" with its object moved, the "what it is for" case from
`CLAUDE.md`.

CURRENT
```text
It removes the parameter along with the one thing the parameter was good for.
```

PROPOSED
```text
It removes the parameter along with the one benefit the parameter provided.
```

### A7 — line 793 — §28 announcement

"it is worth naming here" is the same construction as chapter 47's "One
restriction is worth understanding," which became a direct statement.

CURRENT
```text
The guarantee has a boundary, and it is worth naming here.
```

PROPOSED
```text
The guarantee has a boundary.
```

### A8 — lines 83, 379, 794 — emphasis italics

The chapter has fourteen italics that introduce a term on first use
(*Effect*, *side causes*, *bottom*, *Effect row*, *handler*, *continuation*,
and the rest), all correct. These three are emphasis, which the outliers
confirm. Delete individual rows you want left alone.

**lines 82-83**

CURRENT
```text
This always produces the same result for the same inputs,
*except when `run` is zero*.
```

PROPOSED
```text
This always produces the same result for the same inputs,
except when `run` is zero.
```

**line 379** — the contrast survives without the italics, and "which"
reads better than italicized "what"

CURRENT
```text
   A function declares *what* Effects it uses, not *how* they are fulfilled.
```

PROPOSED
```text
   A function declares which Effects it uses, not how they are fulfilled.
```

## Tier B

### B1 — lines 846, 847, 852, 869 — the closing section's collective "we"

This is a different "we" from A1's: the profession, not the author. Line
856's "an enormous share of professional programming is this activity"
depends on the collective reading, and line 869 contrasts "we" now with
"future programmers" later. I lean toward converting the first three rows
and leaving line 869, but the whole cluster is defensible as written.
Delete individual rows you want left alone.

**lines 852-856**

CURRENT
```text
We discover these behaviors by trusting documentation, reading source,
and observing failures.
Then we write compensating code.
An enormous share of professional programming is this activity,
and we have accepted it as normal for so long that we no longer notice ourselves doing it.
```

PROPOSED
```text
You discover these behaviors by trusting documentation, reading source,
and observing failures.
Then you write compensating code.
An enormous share of professional programming is this activity,
and it has been normal for so long that it goes unnoticed.
```

**line 869** (the line is also 126 characters, so the proposal breaks it)

CURRENT
```text
and future programmers will regard a function with hidden Effects the way we regard a program written in one global namespace.
```

PROPOSED
```text
and future programmers will regard a function with hidden Effects
the way you regard a program written in one global namespace.
```

### B2 — lines 169, 402 — §29 fragmented headers

Two sections open by restating their own heading. You declined this in 46
and accepted it in 47, so it stays a per-instance call. I lean toward
declining the first row (the "phase" thread from line 163 is doing real
work) and applying the second (line 403 is a stronger opener).

**lines 169-170**

CURRENT
```text
The next phase subdivides the impure portion,
and each subdivision produces its own benefit:
```

PROPOSED
```text
The next phase produces one benefit per subdivision:
```

**line 402** — cut the line; the section then opens on line 403

CURRENT
```text
You have already seen Effect Management by hand.
Every technique in [Converting Effectful to Pure](#converting-effectful-to-pure)
```

PROPOSED
```text
Every technique in [Converting Effectful to Pure](#converting-effectful-to-pure)
```

### B3 — lines 148-151 — two negative parallelisms in a row

"not X, it is Y" twice in four lines (§9). Merging the second pair keeps
the contrast without the second setup. This also drops "entire" (flourish
intensifier) and fixes the lowercase "effects" at line 150, which is
capitalized as the book's term everywhere else in the paragraph. Apply the
capitalization even if you decline the rest.

CURRENT
```text
Effects are not a defect to design away.
They are the entire reason a program exists.
The goal of Effect Management is not to eliminate effects.
It is to isolate Effects so the rest of the program can stay pure
```

PROPOSED
```text
Effects are not a defect to design away.
They are the reason a program exists.
The goal of Effect Management is not to eliminate Effects
but to isolate them so the rest of the program can stay pure
```

### B4 — lines 157, 162 — abstract puff in A Taxonomy of Benefits

"effortlessly" and "a cascade of value" are both vaguer than the sentences
around them. I lean toward applying both. Delete individual rows you want
left alone.

### B5 — line 371 — "for sure" and "or not"

Both redundant; the sentence's own next line handles the impure case. Also
brings a 96-character line under the limit.

CURRENT
```text
An EMS allows you to look at the function signature and know for sure whether it is pure or not.
```

PROPOSED
```text
An EMS allows you to look at the function signature and know whether it is pure.
```

### B6 — line 384 — "it has leverage"

An abstract claim that the next four sentences make concrete. Cutting it
loses nothing, but it does work as a signal that the paragraph is coming.

CURRENT
```text
The third item is called *delayed binding*, and it has leverage.
```

PROPOSED
```text
The third item is called *delayed binding*.
```

### B7 — line 796 — vocabulary agreement with chapters 46 and 47

"Ability" is chapter 46's term, introduced there and used 39 times in 46
and 53 in 47. Chapter 44 says "Effects" throughout and then uses
"abilities" once, here, before anything has defined it. I lean toward
applying: this chapter's vocabulary is Effects.

CURRENT
```text
Nothing stops a function from calling `print()` directly,
adjacent to its carefully declared abilities.
```

PROPOSED
```text
Nothing stops a function from calling `print()` directly,
adjacent to its carefully declared Effects.
```

### B8 — lines 688-689 — §1 puff, and a grammar fix

"the world is in the midst of" inflates a claim the rest of the sentence
already makes. The second line is the real problem: "balance between X
while Y" is not a construction that resolves; it needs "balance X against
Y." That half is a copyedit, not an AI tell. Both lines also exceed the
line limit.

CURRENT
```text
At this writing the world is in the midst of an explosion of experimental languages designed for AI code generation.
Designs try to balance between improving code generation for the AI while maintaining human verifiability.
```

PROPOSED
```text
At this writing there is an explosion of experimental languages
designed for AI code generation.
Their designs try to balance better code generation for the AI
against human verifiability.
```

### B9 — lines 627-632 — §31 staccato run

Four verbless fragments and a closer. **I lean toward declining this one.**
Every fragment names a real item in the listing above it, the way chapter
47's "Four implementations, one Ability, one running program" tallies its
trace, and "All of that, to print one string" is the paragraph's argument.
Included only because the pattern is a listed one and the run is longer
than the pairs applied in 46.

CURRENT
```text
Everything else in the listing is machinery, and there is a lot of it.
A trait for the interface.
A companion object to lift that interface into the `ZIO` type.
A `ZLayer` to package the implementation.
A `provide()` call to bind it.
All of that, to print one string.
```

PROPOSED
```text
Everything else in the listing is machinery: a trait for the interface,
a companion object to lift that interface into the `ZIO` type,
a `ZLayer` to package the implementation,
and a `provide()` call to bind it.
All of that, to print one string.
```

### B10 — seven small copyedits

Watch-list words and wording nits, grouped so they cost one delete each.
Delete individual rows you want left alone.

**line 27** — a hyphen after an "-ly" adverb

CURRENT
```text
What happens if your potentially-pure function calls other functions?
```

PROPOSED
```text
What happens if your potentially pure function calls other functions?
```

**line 59** — "is going to be different" is a wordy future; also a
105-character line

CURRENT
```text
However, the result of your function is almost certainly going to be different from one call to the next.
```

PROPOSED
```text
However, the result of your function will almost certainly differ
from one call to the next.
```

**line 97** — Python raises; "throwing" is Java and C++ vocabulary. Line
278's "thrown" is correct, because that sentence is about C++. Also a
117-character line.

CURRENT
```text
    Because ⊥ is a valid theoretical value, throwing an uncatchable error is technically referentially transparent.
```

PROPOSED
```text
    Because ⊥ is a valid theoretical value, raising an uncatchable error
    is technically referentially transparent.
```

**line 311** — "happens" from the watch list

CURRENT
```text
The check still happens, but only once, when a `NonZero` comes into existence.
```

PROPOSED
```text
The check still runs, but only once, when a `NonZero` comes into existence.
```

**line 339** — "actually" from the watch list; line 338 already drew the
contrast with the signature

CURRENT
```text
To discover what the function actually does, you had to read every line of it,
```

PROPOSED
```text
To discover what the function does, you had to read every line of it,
```

**line 370** — §11 synonym cycling: the same guarantee, two verbs, four
lines apart

CURRENT
```text
the EMS ensures that the new function also reports whatever Effects it produces.
```

PROPOSED
```text
the EMS guarantees that the new function also reports whatever Effects it produces.
```

**line 813** — "are what" delays the verb with no gain

CURRENT
```text
If one arrives, the ideas in this chapter are what it will contain.
```

PROPOSED
```text
If one arrives, it will contain the ideas in this chapter.
```

## Housekeeping

1. ~~**Line 791, stale relative cross-reference.**~~ **FIXED 2026-08-05,
   ahead of the rest of this review.** "The next chapter builds it up one
   step at a time" followed the Stateless link, but chapter 45 is now
   Generators; Stateless is 46. This was the split trap from `CLAUDE.md`,
   and no gate catches it. Now reads "That chapter builds it up one step
   at a time," resolving against the `[Stateless](46_Stateless.md)` link
   seven lines above rather than repeating the hyperlink, per the
   clustered-reference convention in `CLAUDE.md`. Line 683-684's reference
   was already correct. A book-wide sweep of every relative chapter
   reference found no other casualty of the split: chapter 45's two both
   point at 46 as intended, and chapter 46's names its target explicitly.
2. **Semantic Line Break drift.** Prose lines past 95 characters, none of
   them broken at a clause boundary: 41, 59, 95, 96, 97, 98, 239, 272,
   275, 278, 371, 543, 633, 673, 688, 689, 727, 771, 785, 869, 887.
   A1, B1, B5, B8, and B10 already shorten 41, 59, 97, 371, 688, 689, and
   869, so run `make reflow CH=44` after applying, not before.
3. **Line 833's spaced ` -- `.** Reported per the process, but this one is
   deliberate: it is the Zen of Python quoted verbatim, and the two `vale
   House.EmDash` comments around it exist to allow it. No action.
4. **"Effect" capitalization in the AI-languages section.** The chapter
   capitalizes Effect as its term, but lines 705, 708, 710, 712, 716, 717,
   720, and 727 use lowercase "effect(s)" while lines 692, 695, and 723
   capitalize it in the same section. If the lowercase is deliberate
   (quoting each language's own terminology) it is worth being consistent
   about which is which; line 727's "an effect's interface" is your own
   prose, not a quotation. Line 150's lowercase "effects" is covered by B3.
5. **Line 860, "the questions from the beginning of this chapter."** The
   four questions are at 345-348 and the depends/changes/goes-wrong trio at
   351-353, both roughly forty percent in, under Effect Management Systems.
   "Beginning" may want to be "the questions this chapter opened with" only
   if you move them, otherwise a section name would be more accurate.
6. **Line 498, "four Effect-managing languages."** This section and the
   next show Koka and Flix (languages) plus ZIO in Scala and Effect in
   TypeScript (libraries in two more languages). Worth confirming the count
   says what you mean, since the section boundary at 579 separates languages
   from libraries.
7. No `[[ ]]` draft notes, no double blank lines before headings, no
   trailing whitespace, no curly quotes, no emoji. The only non-ASCII
   characters are the two ⊥ at lines 95 and 97.

## Considered and not flagged

- **No em dashes anywhere in the chapter.** §14 had nothing to preserve and
  nothing to flag. The only dash form present is the deliberate ` -- ` in
  the Zen quotation (Housekeeping 3).
- **Lines 848-851**, "It might change something in the world. / It might
  read from an unreliable source. / It might fail and take the system
  down." A staccato triple and a rule of three (§31, §10). Kept: the three
  map onto side effect, side cause, and exception, this chapter's own
  taxonomy, so every item is carrying weight.
- **Line 146**, "A perfectly pure computation, followed to its logical end,
  is a space heater with extra steps." §32 aphorism formula on paper, but
  it is a joke with a dated reference, which the skill lists as a sign of
  human writing.
- **Lines 91 and 117-118**, "reads nothing outside itself and changes
  nothing outside itself" / "reads nothing from its environment and changes
  nothing in its environment." Word echoes inside single sentences, but
  this is the chapter's definition of purity restated on purpose, and both
  halves are needed.
- **Lines 361-364**, three sentences starting "You don't know." Anaphora,
  and it answers the four questions at 345-348 in order.
- **Lines 387-393**, "a hundred functions" three times. Deliberate: the
  point is that the number does not change the work.
- **Lines 799-800**, "A library checks the Effects you wrote down. / Only
  the language can check the ones you didn't." Negative parallelism (§9)
  and a manufactured closer (§31). Kept for the same reason as chapter 47's
  closing lines: the contrast is the argument.
- **Lines 667-668**, "The description/execution split is not a feature of
  Effect Management. / It is an artifact of building the system as a
  library." Also §9, also the argument.
- **Line 549**, "This decoupling is the core of every Effect system."
  Reads near §32, but it is a specific structural claim the next three
  lines cash out.
- **Bolded list labels** (**Pure**/**Functional**, **Tracks Effects**,
  **Exceptions**/**Side causes**/**Side effects**). §16 on sight, but this
  is a book-wide convention, not an AI artifact. Line 695's lone bold
  **track** is emphasis rather than a label; left alone because it marks
  the distinction the following paragraph turns on.
- **Line 755**, "and it can now be read with new eyes." A flourish, but it
  is doing the pointing-back work the sentence needs.
- **"already" x3** (402, 733, 805). On the avoid-if-possible list; each
  marks a real prior state. 402 is in B2 for a different reason.
- **Rule-of-three lists** at 165, 337, 352, 396, 680. All real
  enumerations of things the chapter names elsewhere.
- **"However"** (line 59, the chapter's only one). Never a tell alone.
  It is in B10 for wordiness, not for being a transition word.
- **§29 near-misses.** "What Is an Effect?" answered by "An *Effect*
  causes impurity," and "A Program Can Never Be Pure" opened by "A
  perfectly pure program computes something but never lets anyone see it."
  Both looked like fragmented headers; both are definitions or new claims,
  not warm-up restatements. The two real cases are in B2.
- **Line 498's "my research."** First person singular and an unnamed
  source, so §5 on paper. It is the author's own work, which is not a
  vague attribution.
- **Exercise imperatives.** "Write the production bindings," "Count how
  many signatures," "Build a `PositiveInt`." Real instructions, exempt
  from the imperative-plus-consequence rule.

## Scan coverage

The word-level half of the skill found nothing: no hits on the §7
AI-vocabulary list, no curly quotes, no emoji, no promotional or
advertisement language (§4), no vague attributions (§5), no
challenges-and-prospects section (§6), no copula avoidance (§8), no false
ranges (§12), no boldface-header vertical lists beyond the book's own
convention (§15, §16), no collaborative artifacts (§20), no cutoff
disclaimers (§21), no sycophancy (§22), no filler phrases beyond A2's
nominalization (§23), no hedging stacks (§24), no generic positive
conclusion (§25), no hyphenated-pair overuse beyond B10's "potentially-pure"
(§26), no persuasive authority tropes (§27), no diff-anchored writing
(§30), no conversational rhetorical openers (§33). Every finding above is
structural or person, except the copyedits grouped in B10.
