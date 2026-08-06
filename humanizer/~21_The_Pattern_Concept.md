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

## Verdict

The chapter reads as older *Thinking in Patterns* prose with several newer
passages spliced in, and every finding sat in the newer material.
Three passages carried all of Tier A: the "discovered, not predicted"
paragraph (57-62), the "sign of something missing in a language"
paragraph (81-92), and the two-sentence pair that opened Design Principles.
The largest single finding was the language-absorbs-patterns paragraph,
which packed a doubled "enough," a repeated "scaffolding," a tense break
across one conjunction, and two long-range word echoes into eleven lines.
The word-level half of the scan came back empty except for one "actually."
No em dashes exist anywhere in this chapter, so §14 had nothing to protect.

All Tier A and Tier B edits have been applied.

## Housekeeping

1. **Semantic Line Break drift.** Thirteen prose lines run past 80
   characters with clause punctuation available to break at, including
   lines 18, 45, 50, 78, 130, 134, 154, and 213. `make reflow CH=21`
   fixes them; no gate catches it. The two footnote lines (85 and 193,
   at 203 and 265 characters) are masked by `md_prose.py` and will stay
   long, which is expected rather than drift. Line numbers will have
   shifted after the edits above.
2. **The chapter ends without a closing section.** The last body line is
   a single trailing sentence after the Design Principles bullet list,
   with no heading of its own. Structural, not a humanizer finding, but
   worth a look if the chapter gets a deeper pass.
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
  replacement tried either kept the pair or loosened the antecedent
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
- **The *Simplicity before generality* material.** The footnote attributes
  it to an email from Kevlin Henney, so it is secondhand text: its "we
  find," its rule of three ("unused, misused or not useful"), and its
  missing Oxford comma all stay.
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
