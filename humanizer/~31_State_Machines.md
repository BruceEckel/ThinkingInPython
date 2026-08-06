# Humanizer candidates: Chapters/31_State_Machines.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied, one block that another block
superseded, and what was never flagged. This is a changelog now, not a
worklist.

## Applied

Every block survived review. Twelve prose edits plus one listing comment:

- A1, five first-person-plural sites converted to second person or to an
  impersonal subject (lines 36-37, 38, 42, 380-382, 672). The line-380 row
  also straightened the three-question list into parallel form.
- A2, the "not only... but also" correlative at line 47.
- A3, the emphasis italic on *unexpected* at line 359.
- A4, the emphasis italic on *entire* at line 376.
- A5, the stranded "warned about" at line 74.
- B1, the emphasis italic on *other* at line 246.
- B2, the emphasis italic on *exactly* at line 440.
- B3, the stranded "hear about" at line 370.
- B4, the word echo at lines 14-17.
- Housekeeping 1, the `vending_machine.py` comment reworded to "so the
  model does not touch the screen," and re-synced.

The review leaned toward keeping B3 and B4. Both stayed in the file and were
applied; recorded here so a later pass does not read the lean as the decision.

## Superseded, not separately applied

**B3's line-16 row.** B3 and B4 both rewrote line 16. B4's replacement
("each `State` object makes that decision on its own") drops the phrase
"what other states it can move to" entirely, so the stranded preposition
B3 targeted no longer exists and B3's own wording ("which other states to
enter") never landed. B4 was applied as the larger of the two; B3's
line-370 row was applied separately. Nothing was lost, but a later pass
comparing this file against the chapter will not find B3's line-16 text.

## Considered and not flagged

- **Pattern-name italics** (`*State*`, `*StateMachine*`, `*Template Method*`,
  `*Proxy*`). Confirmed via chapters 21, 25, and 26 that the book
  italicizes pattern names on every mention, not just first use. This is a
  book-wide convention, not an emphasis-italics violation.
- **"plain methods"** (line 453). Directly contrasts with the
  `Condition`/`Transition` class hierarchy described two sentences earlier
  (the Java version's approach), so it earns its place per CLAUDE.md's
  "plain" test.
- **The word "exactly" in plain prose** (line 353, "the output continues
  exactly as in the first version"). A genuine precise/logical match,
  allowed under CLAUDE.md's carve-out. Distinct from the italics markup on
  the *other* "exactly" at line 440 (B2), which is what was flagged there.
- **The staccato pair at lines 368-371** ("Ignoring suits a machine fed from
  a noisy source..." / "Failing fast suits a table you are still
  building..."). Each half states a distinct concrete claim rather than
  manufacturing drama, so left alone.
- **"### The Engine" and "### A Vending Machine" opening sentences.**
  Considered as possible fragmented headers (§29), but neither restates the
  heading text; both move straight into specific mechanism ("the engine
  walks the candidate transitions in order...", "It collects money, takes a
  two-digit selection..."), so they don't match the pattern.
- **The "three questions" list at lines 380-382.** Reflects the actual
  three-field transition tuple `(condition, action, next_state)` shown in
  the table sketch two lines later, not a decorative rule-of-three. Only its
  broken parallel structure was flagged (A1's last row).
- **"never" in ordinary prose** (line 668, "the model never draws
  anything"). A plain factual statement, not a hedge. Distinguished from the
  listing-comment instance that was reworded.
- No promotional language, vague attributions, "Challenges and Future"
  section, copula avoidance, elegant variation, false ranges, curly quotes,
  emoji, boldface, or inline-header-colon lists found anywhere in the
  chapter.

## Scan coverage

Clean: §1 (significance/legacy), §2 (notability), §3 (-ing analysis
padding), §4 (promotional language), §5 (vague attributions), §6
("Challenges" sections), §7 (AI-vocabulary word list, aside from the one §9
hit), §8 (copula avoidance), §10 (decorative rule-of-three), §11 (elegant
variation), §12 (false ranges), §13 (passive/subjectless fragments), §15-§19
(boldface, inline-header lists, title case, emoji, curly quotes), §20-§25
(collaborative artifacts, cutoff disclaimers, sycophancy, filler phrases,
hedging, generic conclusions), §27-§30 (authority tropes, signposting,
fragmented headers, diff-anchored writing). No em dashes exist in this
chapter at all. `tools/reflow_prose.py` reported zero paragraphs needing
reflow; no double blank lines, `[[ ]]` notes, or spaced ` -- ` found.
