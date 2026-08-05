# Humanizer candidates: Chapters/47_Stateless_in_Practice.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All proposed edits were accepted and applied on 2026-08-05, then removed
from this file. What remains is the record. This is a changelog now,
not a worklist.

## Applied

Every Tier A and Tier B block, plus the stray blank line from Housekeeping.
Nothing was declined.

- A1, the "The trace shows two things worth noticing" announcement,
  with the following "And" reworked to "also."
- A2, "One restriction is worth understanding" to "The checker enforces
  one restriction."
- A3, the emphasis italic on *function* at line 1283. This was the only
  emphasis italic in the chapter; the other five all introduce a term.
- A4, "products are produced" to "products are made."
- A5, the collision/collide echo. **Wording is Bruce's, not the proposal:**
  the two-line original became the single line
  "Every pair of abilities with a wide cast raises the odds of a collision."
- A6, three first-person-plural sites converted (lines 592, 979, 983).
- B1, both §29 fragmented headers: "A coin toss is a side cause" became
  "Tossing a coin is a side cause," and "Effects can also run at the same
  time" was cut from the head of Running Effects in Parallel.
- B2, "Be fair about what this comparison shows" to "The comparison has
  limits."
- B3, "Here's" to "Here is," matching the other four listing lead-ins.
- B4, the "Naming the machinery precisely" announcement.
- Housekeeping 2, the double blank line before `## Exercises`.

Note for a future pass: B1 was applied here but its equivalent in chapter
46 (that chapter's A5) was declined. The two chapters now differ on whether
a section may open by restating its heading. That was a deliberate
per-instance call rather than a rule, so don't normalize one to the other
without asking.

## Draft note at line 236, carried out

The `[[ ]]` placeholder in `### A Clock` asked for two things,
and both were done on 2026-08-05 at Bruce's instruction:

1. *"Start by describing the overview and clock.py."*
   The section now opens with why a clock is a side cause worth its own
   Ability (a real clock reports the present moment and nothing else,
   so a test cannot ask it about tomorrow), then presents `clock.py`,
   then describes it: `Now` carries no data the way `Flip` does, and its
   answer type is its whole content.
2. *"Move the stamp and batch_due material right before frozen_clock.py."*
   Those four lines now sit directly above the `frozen_clock.py` listing
   they describe, rather than above `clock.py`.

The old opener, "A clock is another side cause that makes testing tricky,"
restated its own heading, so the rewrite also resolves the §29 case that
B1 handled at the two other sites. No listing changed.
`make verify` passed afterward.

No `[[ ]]` draft notes remain anywhere in `Chapters/`.

## Outstanding

**Semantic Line Breaks drift.** Several lines run past a sentence or clause
boundary, and line 1157 breaks oddly ("it type-checks, / and it runs").
Line numbers shifted by the edits above, so re-check rather than trusting
old ones. `make reflow CH=47` fixes these. No gate catches them.

## Considered and not flagged

Recorded so a later pass doesn't re-litigate them.

- **No em dashes in this chapter at all.** §14 had nothing to preserve
  and nothing to flag.
- **Line 555**, "Four implementations, one Ability, one running program."
  A verbless fragment and a rule of three (§31, §10). Kept: it tallies
  what the trace above it just showed, so every term is carrying weight.
- **The closing lines**, "What is missing is not the capacity. / It is a
  language that does the encoding for you." A negative parallelism (§9)
  and a manufactured closer (§31). Kept: it is the chapter's last line
  and the contrast is the argument.
- **"Nine is also a fair warning about the design."** Slightly odd to call
  a number a warning, but the point lands.
- **"it cannot also be a plain function."** "Plain" earns its place: it
  contrasts with "generator function" one line above.
- **Rule-of-three lists** ("rate limiting, bulkheads, and circuit
  breakers", and the Converting Effectful to Pure list). Real
  enumerations, not padding.
- **"already" x2.** Both mark a real prior state.
- **§3 participle tails** ("holding every failure," "listing the overloads
  it failed to match"). Both modify a real noun rather than adding fake
  depth.
- **The five term-introducing italics**: *accessors*, *scenario*,
  *defect*, *continuation*, *tail-resumptive*. All correct on first use.

## Scan coverage

For reference if this is re-run. The word-level half of the skill found
nothing whatsoever in this chapter: no hits on the §7 AI-vocabulary list,
no curly quotes, no emoji, no boldface-header lists, no promotional
language, no filler phrases, no hedging stacks, no sycophancy.
Every finding above was structural.
