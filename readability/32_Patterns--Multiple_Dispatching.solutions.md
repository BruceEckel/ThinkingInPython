> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Multiple Dispatching, Solutions

The Solutions file for chapter 32 has no Tier 1 or Tier 2 vocabulary
clusters, no signposting, no significance inflation, and no curly quotes.
The thirteen changes below split "and" joins whose clauses change subject,
cut three restatements and one filler opener, replace one anthropomorphic
"wants" and one "genuine", and correct a pointer in exercise 1 that read
as though the table version's demonstration had moved to
`methods_demo.py`. Each touched sentence was checked against its listing
or against the chapter: the chapter's table listing has no demonstration,
`methods_demo.py` drives the method version, and `__add__()` has the same
three cases as `__sub__()`.
`tip verify-ch CH=32 ISOLATED=1` passed after the edits (27 passed).
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 144-146, pointer with two candidates: "The chapter moves its demonstration to `methods_demo.py` instead" -> "The chapter keeps the method version's demonstration in a separate file, `methods_demo.py`". "Its" could mean this module's (the table version), and the chapter's table listing has no demonstration to move.
- Line 476, "and" hiding a contrast: "Each module defines its own `Outcome`, and the comparison still works" -> two sentences ("but" fits the seam).
- Line 669, watch list ("wants" with a code subject): "A caller that wants the tally" -> "A caller that needs the tally", matching "a caller that needs only the pairs" four lines above.
- Line 758, vague comparison: "The three cases of `__sub__()` line up the same way:" -> "Its three cases match those of `__add__()`:", naming what "the same way" compared against. The paragraph was rewrapped.
- Lines 773-774, treadmill: "Addition commutes, so in `__radd__()` the swap leaves every result the same. The same mistake gives the right answer in `__radd__()` and the wrong answer in `__rsub__()`." -> "Addition commutes, so the same copied body in `__radd__()` gives the right answer every time." The cut sentence restated the two before it.
- Lines 778-779, "and" joining different subjects: "Python raises the `TypeError`, and the message names both types" -> "Python raises the `TypeError`, whose message names both types".
- Line 938, word echo: "The match now follows inheritance. Three consequences follow." -> "... That change has three consequences."
- Lines 947-948, "and" joining different subjects: "picks the one that wins, and that rule lives in `compete()`" -> two sentences; the second is a claim of its own.
- Line 1277, filler opener: "Here, each `Inhabitant` kind holds" -> "Each `Inhabitant` kind holds".
- Line 1500, §34 adjective inflation: "a genuine cycle" -> "a cycle". Nothing in the sentence names what a non-genuine cycle would be.
- Lines 1505-1507, awkward pointer: "each of the three kinds wins `meeting(5)` for some of them" -> "each of the three kinds wins `meeting(5)` at least once"; "Over" -> "Across".
- Line 1684, treadmill: cut "A table of callables keeps the method-call syntax.", the third statement of "the call site stays the same" (the exercise statement and the sentence before it make it).
- Lines 1697-1698, "and" joining different subjects: "The chapter gives two reasons ..., and the first is behavior that reads the object's own state" -> two sentences, which also parallels "The second reason survives" below.

## Considered and declined

- The bold step labels in every exercise (§15/§16 by shape): the Solutions files' convention for a labeled step, not emphasis.
- Long first lines after the bold labels (lines 136, 343, 346, 924, 933, 1678, 1690, and others): uneven hand-wrapping leaves the rendered page unchanged, so only edited paragraphs were rewrapped.
- Lines 255-256, "That `AttributeError` is the first sign of the mistake, so the solution adds `eval_lizard()` to all three existing classes." The "so" is a loose causal link, but the opening paragraph's job is to show the failure the solution guards against, and every Solutions file in this sweep uses the same "so the solution ..." close.
- Line 930, "That is what the chapter's "matches classes exactly" means." The "is what" complement is a noun clause that cannot attach without it (recurring keep).
- Lines 961-962, "That subclass is the new type most likely to receive an old type's answers by mistake." A superlative by shape, but it states the reason the lost fail-fast matters for this case.
- Lines 964-967, "Which behavior you want" and "`Origami` really is paper": "want" addresses the reader's intent, and "really" contrasts with the `WetPaper` named in the next sentence (recurring keeps).
- Line 1507, "a real rock-paper-scissors tournament": "real" contrasts with the simulated `meeting()`.
- Lines 1106, 1279, and 1285, "even count", "even number": arithmetic "even".
- Lines 1712-1714, the `Origami(Paper)` paragraph sits between "The second reason survives" and the `isinstance()` step. It answers whether callable cells change exact matching, which follows from the second reason's discussion of the table, so it stays where it is.
