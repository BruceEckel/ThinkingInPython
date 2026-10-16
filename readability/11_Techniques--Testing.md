> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/11_Techniques--Testing.md`, 2026-10-16.
The chapter carries few AI-writing tells after its October editing passes:
two edits were clear enough to apply directly,
and nothing needed your judgment, so this file holds no live block.
It is the record of the applied edits and of the hits examined and kept.
`readability_db.md`'s keeps for this chapter ("One of the most valuable habits",
"justifies the effort") were honored.

## Applied directly

- Line 15, §42/§24 (importance cue stacked on a hedge):
  "Perhaps more importantly, tests tell you immediately if a change you've made causes a failure"
  -> "Tests report a failure immediately, as soon as a change you've made causes it."
  The close alternative was to keep the opener as voice;
  revert this line if "Perhaps more importantly" is yours.
- Line 86, §62 (transition-phrase opener):
  "That said, TDD requires" -> "But TDD requires".
  "however" sits two lines below, so "But" avoids a second one.

## Considered and declined

- Line 6, "one of the most valuable habits in modern programming":
  a superlative by shape, kept by `readability_db.md` (confirmed 2026-10-04).
- Line 13, "refactor boldly, change designs, and clean up code":
  a triple, but first-edition text and three distinct activities.
- Line 32, "A team that stops at the patch fixes the same kind of bug forever.":
  a kicker by shape, but it states the consequence the paragraph argues,
  and the hyperbole is voice.
- Line 206, "Those three cover most of a working day.":
  a short beat after the three command-line options, not staccato.
- Lines 270-273, the four short sentences after `test_overdraft_message.py`
  ("The assertions after the block belong outside it." through "Inside the block neither assertion runs."):
  a run of short sentences, but each carries a separate step of the reasoning,
  and the lines were reworked in the October passes.
- Line 445, "The reuse is the risk as well as the point.":
  aphoristic by shape, but the next sentence delivers the mechanism.
- Line 470, "Both tests pass, and that is the problem.":
  a beat, kept by the recurring short-fragment keep.
- Line 705, "As with any seed, you record the value it gives you rather than pick one.":
  close to line 674's "record the values it produces rather than choose them,"
  but here it gives the reason the `4` match is a coincidence
  (it was a colon clause until the 2026-10-04 split sweep).
- Line 778, "That rejection justifies the effort of injection":
  your wording from the 2026-10-04 Sweep Decisions page.
- Line 814, "the standard answer for code built around `datetime`":
  a mild unattributed claim, kept as the author's recommendation.
- Lines 288 and 900, "exactly": a precise numeric match and a call count.
- Line 956 (exercise 5) "a plain function passed in" and line 977 "plain programs":
  each contrasts with a named alternative (a `monkeypatch`ed function, a test file).
