# Humanizer candidates: Chapters/46_Stateless.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was declined, and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Seventeen prose edits, plus the stray blank line from Housekeeping:

- A2, staccato pair at "No test had to exercise the path" merged into one sentence.
- A3, "but look closer" replaced with "but it is accidental."
- A4, the "Errors Propagate" section no longer opens by restating its heading.
- A6, the DI paragraph: "swappable" said once, the emphasis italic on
  *relocates* dropped, "un-validated" closed up.
- A7, the broken infinitive/noun parallel in the EMS goal sentence.
- A8, "Two questions are being answered" given an actor.
- A9, nine first-person-plural sites converted to second person
  (lines 83, 326, 345, 427, 458, 529, 836, 1005, 1198).
- A10, "un-supplied" and "un-awaited" closed up.
- A11, `both` and `one` unbackticked before the listing introduces them.
- A12, the "indicating there is no score" participle tail.
- B2, "produces three consequences" to "has three consequences."
- Housekeeping 1, the double blank line before `## Nothing Runs Yet`.

## Declined

Recorded so a later pass doesn't re-flag them.

- **A1**, line 410, "Let's see what happens when we don't supply a required
  `Need`." Flagged as §28 signposting. Kept. This is also the one surviving
  editorial "we" in the chapter besides the acknowledgment at line 28,
  so A9 should not be re-run against it.
- **A5**, "Declaring an error does not oblige you to handle it."
  Flagged as a §29 fragmented header restating "Declaring Is Not Handling."
  Kept as the section's topic sentence.
- **B1**, "Type checking is the optimal time to discover errors."
  The proposed "earliest" narrowed the claim. Kept as written: optimal.
- **B3**, "In `greeter.py`, two details deserve attention:". Kept.
- **B4**, "The two halves of this chapter taught two vocabularies:". Kept.

## Housekeeping outstanding

**Semantic Line Breaks drift.** Lines running past a sentence or clause
boundary without breaking. Line numbers below are from before the edits above,
so re-check rather than trusting them: 28, 303, 529, 1007, 1016, 1640, 1647.
A9's rewrites shortened 529 and 1005, so that list is now shorter than it was.
`make reflow CH=46` fixes these. No gate catches them.

## Considered and not flagged

From the original scan. These were looked at and deliberately left alone.

- **Line 404's em dash.** Preserved per §14. Yours, deliberate, stays.
- **Lines 10-11**, the "If you forget to declare / If you forget to supply"
  pair. Deliberate parallel repetition doing real work, not §9.
- **Line 179**, "That signature is a lie by omission."
  Reads as an aphorism formula (§32) but names a specific, checkable defect.
- **Line 402**, "A Stateless Effect is a one-shot token: build it, run it,
  discard it." Hits both §32 and §10. Kept: "one-shot token" is precise,
  and the three verbs are the actual lifecycle, not padding.
- **Lines 1471-1472**, "A raised `KeyError` is a failure. / A returned
  `KeyError` is data." Two short parallel sentences, but the contrast is
  the point of the section.
- **Lines 938-940**, "a recorder in a test, a terminal in production, and a
  scripted one in a demo." A rule of three, but all three are grounded:
  exercise 1 asks for the scripted and real cases.
- **"already" x7** (lines 524, 1054, 1103, 1143, 1151, 1183, 1194).
  On your avoid-if-possible list, but each one marks a real prior state.
- **"However" x2** (lines 181, 805). Only a tell when piled up.

## Scan coverage

For reference if this is re-run. The word-level half of the skill found
nothing in this chapter: no hits on the §7 AI-vocabulary list, no curly
quotes, no emoji, no boldface-header lists, no promotional language, no
generic upbeat conclusion. Every finding above was structural.
