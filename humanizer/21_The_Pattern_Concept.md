[[Reviewed]]
# Humanizer candidates: Chapters/21_The_Pattern_Concept.md

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

No block overlaps another, so any subset applies cleanly.

## Verdict

The chapter reads as older *Thinking in Patterns* prose with several newer
passages spliced in, and every finding sits in the newer material.
Three passages carry all of Tier A: the "discovered, not predicted"
paragraph (57-62), the "sign of something missing in a language"
paragraph (81-92), and the two-sentence pair that opens Design Principles.
The largest single finding is the language-absorbs-patterns paragraph,
which packs a doubled "enough," a repeated "scaffolding," a tense break
across one conjunction, and two long-range word echoes into eleven lines.
The word-level half of the scan came back empty except for one "actually."
No em dashes exist anywhere in this chapter, so §14 had nothing to protect.

## Tier A

### A1 — line 27 — §7 AI vocabulary, and the watch list

"actually" is the one hit from the AI-vocabulary list in the whole chapter,
and it does no work here: a problem is either present or it isn't.

CURRENT
```text
A pattern earns its place only when the problem it solves is actually present.
```

PROPOSED
```text
A pattern earns its place only when the problem it solves is present.
```

### A2 — line 57 — §28 signposting

"Notice that" tells the reader to notice instead of saying the thing.
The contrast after it is doing the work on its own.

CURRENT
```text
Notice that a vector of change is discovered, not predicted.
```

PROPOSED
```text
A vector of change is discovered, not predicted.
```

### A3 — lines 58-59 — §11 restatement

Both sentences say the guess was wasted. The second adds only the word
"complexity," so folding that word into the first loses nothing and
drops a "never" along with it.

CURRENT
```text
Guessing at it up front often builds flexibility in a direction that doesn't get used.
This creates complexity to produce generality that never pays off.
```

PROPOSED
```text
Guessing at it up front often builds complexity for flexibility in a direction that doesn't get used.
```

### A4 — lines 78-79 — word echo in adjacent sentences

"generic code" opens one sentence and then opens the next.
A pronoun carries the reference and the second sentence gets shorter.

CURRENT
```text
You can write generic code that performs an operation on all of the elements in a sequence without regard to the sequence's construction.
Generic code can work with any object that produces an iterator.
```

PROPOSED
```text
You can write generic code that performs an operation on all the elements in a sequence without regard to that sequence's construction.
The code works with any object that produces an iterator.
```

### A5 — lines 82-83 — "enough" twice in one sentence, "scaffolding" twice in two

"Enough programmers ... often enough" reads as a slip, and repeating
"scaffolding" as the next subject compounds it. One "enough" and a
pronoun fix both.

CURRENT
```text
Enough programmers wrote the same scaffolding often enough to name it.
That scaffolding exists only because the language does not write it for them.
```

PROPOSED
```text
Programmers wrote the same scaffolding often enough that it acquired a name.
It exists only because the language does not write it for them.
```

### A6 — line 88 — broken parallel across one conjunction

"Iterator became" and "Strategy and Command shrink" are joined by a
single "and" in past and present tense. The present tense is defensible
alone, as a standing fact rather than a history, but not inside this
sentence.

CURRENT
```text
and *Strategy* and *Command* shrink to passing a function
```

PROPOSED
```text
and *Strategy* and *Command* shrank to passing a function
```

### A7 — lines 170-171 — §31 staccato pair with an unmarked contrast

The second sentence names the exceptions to the first, and the period
hides that. The reader has to work out the relationship.

CURRENT
```text
Most hold for any code.
*Reflexivity* and the *Law of Demeter* assume classes and objects.
```

PROPOSED
```text
Most hold for any code, but *Reflexivity* and the *Law of Demeter* assume classes and objects.
```

### A8 — lines 98 and 190 — first person plural

Two "we" sites in a second-person book. Delete individual rows you want
left alone. The third "we" in the chapter, at line 195, is inside the
Kevlin Henney material the footnote on line 194 attributes, so it is
quoted and stays.

**line 98**

CURRENT
```text
1.  **Idiom**: how we write code in a particular language to do this particular type of thing.
```

PROPOSED
```text
1.  **Idiom**: how you write code in a particular language to do this particular type of thing.
```

**line 190**

CURRENT
```text
    Simply declaring that we should have "low coupling" in a design is usually too vague.
```

PROPOSED
```text
    Simply declaring that a design should have "low coupling" is usually too vague.
```

## Tier B

### B2 — lines 38-39 — missing contrast connective

"you might expect it to appear no earlier than low-level design" sets up
an expectation, and the next line overturns it with no signal.
I lean toward applying: one word restores the turn, and you already open
sentences with "But" elsewhere in this chapter (line 148).

CURRENT
```text
you might expect it to appear no earlier than low-level design.
It appears at every level,
```

PROPOSED
```text
you might expect it to appear no earlier than low-level design.
But it appears at every level,
```

### B3 — lines 91-92 — "dissolves" echoing line 85

Line 85 has "the pattern dissolves into it" and line 92 has "how much
dissolves into functions, data, and protocols," seven lines apart in one
paragraph. I lean toward applying, weakly: the repetition may be a
deliberate return to the word, and if so, keep it.

CURRENT
```text
posed: how much of each pattern's machinery does Python still need,
and how much dissolves into functions, data, and protocols?
```

PROPOSED
```text
posed: how much of each pattern's machinery does Python still need,
and how much of it becomes functions, data, and protocols?
```

### B5 — line 169 — §3 infinitive tail

", to apply tests for quality" hangs off the end as a purpose clause that
restates the first half. A conjunction makes it a second thing principles
do. I lean toward applying, but this may be your original wording, in
which case ignore me.

CURRENT
```text
Principles ask questions about your proposed design, to apply tests for quality.
```

PROPOSED
```text
Principles ask questions about your proposed design and test it for quality.
```

## Housekeeping

1. **Semantic Line Break drift.** Thirteen prose lines run past 80
   characters with clause punctuation available to break at, including
   lines 18, 45, 50, 78, 130, 134, 154, and 213. `make reflow CH=21`
   fixes them; no gate catches it. The two footnote lines (85 and 193,
   at 203 and 265 characters) are masked by `md_prose.py` and will stay
   long, which is expected rather than drift.
2. **The chapter ends without a closing section.** Line 213 is a single
   trailing sentence after the Design Principles bullet list, with no
   heading of its own. Structural, not a humanizer finding, but worth a
   look if the chapter gets a deeper pass.
3. **Nothing else structural.** No `[[ ]]` draft notes, no spaced ` -- `,
   no double blank line before any heading, no trailing whitespace.

## Considered and not flagged

- **No em dashes anywhere in the chapter.** §14 had nothing to preserve
  and nothing to flag, the same as chapters 46 and 47.
- **No emphasis italics.** Every italic is a book title, a pattern name,
  a *GoF* category name, a design principle name, or a term on first use.
  The maxim at line 45, *separate things that change from things that stay
  the same*, is italicized again at 37_Pattern_Refactoring.md:404, so it
  is a named principle rather than emphasis, and line 45 is its first use.
- **The bolded-header numbered lists** at lines 98-109 and 128-140 match
  §16's shape, but each header names a defined term the sentence then
  defines. That is a glossary, not AI list padding.
- **"varies" and "variation" in line 28.** A real echo, but every
  replacement I tried either kept the pair or loosened the antecedent
  ("machinery to isolate it"). Left alone.
- **"machinery" at lines 28, 87, and 91.** The 87/91 pair is close
  enough to notice, but the word means the same thing at both sites, and
  swapping one for a synonym would be exactly the elegant variation §11
  warns about.
- **"treats" three times and "structure" four times in lines 154-163.**
  Deliberate parallel across three list-like sentences, which is what
  makes the three groupings scan as one claim.
- **Line 161, "treats both of its patterns as one recursive-data
  structure,"** where the other two sentences name their patterns.
  Naming them here would repeat the link text one line above.
- **"This is why the chapters ahead keep asking"** at line 90. Reads like
  §28 signposting, but the causal link is real: Python absorbing patterns
  is the reason the question recurs. Cutting "This is why" would lose it.
- **"I introduce the basic concepts of design patterns"** at line 14.
  An opening paragraph saying what the chapter covers is book convention,
  not the "let's dive in" announcement §28 targets.
- **"Composition also qualifies as a pattern"** (line 70) and
  **"[Singleton](24_Singleton.md) counts as a creational pattern"**
  (line 131). Both are §8 copula avoidance on paper, but both are
  classification claims where "is" would overstate: qualifying and
  counting as are the point.
- **"A significant portion of those examples provides inspiration"**
  (line 13). "significant" sits on §1's list, but here it quantifies
  rather than puffs.
- **"Coupling happens"** (line 191). On the watch list under `happen`,
  and kept: it is a deliberate idiom and the sentence is built on it.
- **"already" (line 65) and "only" (lines 27, 40, 83, 181).** Each marks
  a real prior state or a real exclusion.
- **The negative parallelisms** at line 57 ("discovered, not predicted"),
  line 179 ("not a linear factor, but an exponential one"), and inside
  the Saint-Exupéry footnote at line 193. All three are genuine
  contrasts, and the third is a quotation.
- **The rule-of-three lists**: "analysis, design, and implementation"
  (33-34), "functions, data, and protocols" (92), and the Law of Demeter's
  four-item list (181-183). Real enumerations.
- **Lines 195-202**, the *Simplicity before generality* material. The
  footnote at line 194 attributes it to an email from Kevlin Henney, so
  it is secondhand text: its "we find," its rule of three ("unused,
  misused or not useful"), and its missing Oxford comma all stay.
- **The Norvig footnote at line 85.** Specific, dated, attributed, and
  hard to fabricate, which is a human-writing signal rather than a
  finding.

## Scan coverage

Everything found was structural. The word-level half of the skill turned
up one hit in 214 lines ("actually" at line 27) and nothing else: no
curly quotes, no emoji, no promotional or advertisement language, no
vague attributions, no hedging stacks, no filler phrases, no sycophancy,
no collaborative-chatbot artifacts, no knowledge-cutoff disclaimers, no
false ranges, no persuasive-authority tropes, no hyphenated-pair overuse,
no diff-anchored writing, no conversational rhetorical openers, and no
generic positive conclusion. §17 does not apply to book headings, and no
heading was touched. §29 was checked at all four headings and none opens
by restating itself; the closest, "## Design Principles" followed by
"Design principles are at least as important as design structures," adds
a comparative claim rather than restating.
