# Humanizer candidates: Chapters/32_Multiple_Dispatching.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Every block survived review. Six prose edits plus nine listing comments:

- A1, two first-person-plural sites (lines 53, 71). The line-71 rewrite
  also dropped the repeated italics on *Multiple Dispatching*, already
  introduced at line 17.
- A2, the emphasis italic at line 151.
- A3, the italicized "exactly" at line 214 and the filler "exactly" at
  line 218.
- B1, the redundant third sentence at line 29.
- Housekeeping 1, the nine `eval_*()` comments in `paper_scissors_rock.py`
  reworded from "we're in Paper" to "this is Paper's case" (and likewise
  for Scissors and Rock), and re-synced. The surrounding code is unchanged,
  and the `#:` output markers still match.

The review leaned toward cutting B1 but called it a real judgment call.
It stayed in the file and was applied.

## Considered and not flagged

- **"A tuple serves as a key just as easily as a single object."**
  (line 212). §8's copula-avoidance list includes "serves as," but this
  is a single plain statement of fact, not an inflated substitute for
  "is." Left alone.
- **"Declining is not failing; the error appears only when nobody
  volunteers."** (line 316). Shaped like §9's "not X, it's Y," but it
  draws a real technical distinction the paragraph needs (an operand
  declining a type is not the same as the operation failing), and it's
  a single instance, not a stacked pair. Left alone.
- **"The answer starts with something you probably never consider."**
  (line 11). A mild lead-in hook, but it's one sentence, not a
  standalone theatrical opener ("Honestly?", "Here's the thing") from
  §33, and nothing else near it clusters with it. Left alone.
- **Three forms of polymorphism** (lines 20-24: overloading, generics,
  runtime dispatch). Looks like a rule-of-three (§10) on the surface,
  but each item is a genuinely distinct answer to "what does
  polymorphism mean," not decorative padding. Left alone.
- **"Here is the machinery, with each dispatch traced:"** (line 262).
  A mild announcement before a listing, but it matches how the chapter
  introduces its other listings (e.g. line 160's "like this:") and
  isn't part of a cluster of signposting. Left alone.

## Scan coverage

No hits on §4 promotional language, §5 vague attributions, §6
challenges-and-prospects sections, §7 AI vocabulary, §12 false ranges,
§15/§16 boldface or inline-header lists, §19 curly quotes, §20
collaborative artifacts, §21 knowledge-cutoff disclaimers, §22
sycophantic tone, §23 filler phrases, §24 excessive hedging, §25 generic
positive conclusions, §26 hyphenated-pair overuse, §27 persuasive
authority tropes, §29 fragmented headers, §30 diff-anchored writing, §31
staccato drama beyond one ordinary short sentence, §32 aphorism
formulas, or emoji. Person, italics, and one redundant sentence were the
whole of it. No double blank line before a heading, no `[[ ]]` draft
note, no spaced ` -- `, no em dash anywhere, and no Semantic Line Break
drift.
