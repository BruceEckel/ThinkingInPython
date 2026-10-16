When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability review of `Solutions/30_Patterns--Observer/README.md`, run
2026-10-16 against `readability_db.md` (no earlier review of this
Solutions file exists). The prose carries few AI-writing tells: no Tier 1A
vocabulary, no stacked hedges, no recap openers, and the bold step labels
follow the Solutions convention. Most of what fired was the global "and"
rule (two clauses with different subjects where "but" or "so" fits) plus
one restated paragraph and one synonym swap. Every finding had one
sensible answer, so all of them are applied below, and this file holds no
live block: it is the applied-directly record.

## Applied directly

- 301, "and" joining different subjects: "`Display.update()` now declares `subject: Thermometer` and `t.attach(Display())` type-checks" -> "With `Display.update()` declaring `subject: Thermometer`, `t.attach(Display())` now type-checks".
- 304, §70 restatement: cut "A display written for a `Thermometer` therefore cannot attach to a different `Subject[float]`."; the paragraph's last two sentences state the same restriction as a contrast with the wider `Subject[float]`.
- 959, "and" where "but" fits: "names `GridModel`, and a `FloodGame` is not one" -> "names `GridModel`, which a `FloodGame` is not".
- 1074, "and" where "while" fits: split "...advanced one color, and the other nine cells are as they were" into two sentences (checked against `exercise_7.py`: 4x4, seven cells change, nine stay).
- 1078, "and" where "while" fits: "changes what the window does, and `grid_view.py` runs as it stands" -> two sentences.
- 1337, long compound with a subject change: split "...since it is not zero, and `pow(x, -1, MOD)` then raises..." at the "and".
- 1588, §11 synonym cycling and restatement: cut "so each attribute has its own watchers" after "separate responder lists".
- 1593, "and" joining different subjects: "with `obj` set to `None`, and returning the descriptor there lets..." -> two sentences.
- 1598, "and" where "so" fits: "the declared return type is the union, and the type checker rejects" -> "...is the union. The type checker then rejects".
- 1682, "and" where "so" fits: "refers to `None`, and calling `display(5.0)` raises a `TypeError`" -> two sentences, "Calling `display(5.0)` then raises...".
- 1690, "and" joining different subjects: "would bind that name to `None`, and `respond()` exists to return the function" -> two sentences.
- 1749, "and" joining different subjects: "nothing to pass to `disconnect()`, and that problem goes away with `disconnect()`" -> "...to `disconnect()`. That problem disappears along with `disconnect()`."

## Considered and declined

- 444, "A plain `except`": "plain" contrasts with `except*` in the sentence before (recurring keep).
- 625, "which is what a cancelled `await` propagates": the complement is a clause that cannot attach without "is what" (recurring keep).
- 1593, "the part a validating descriptor never needs": the "never" is the claim, the contrast with chapter 17's validating descriptor.
- 1747, "disconnect itself": reflexive and load-bearing.
- 245, "a requirement the protocol cannot express: this `Display` works for a `Thermometer` and fails on any other `Subject[float]`": the colon delivers the one requirement named, and both verbs share a subject.
- 505-506, "`except*` wraps a bare exception in a group, and `record()` finishes before `main()` resumes": two parallel reasons the demo still prints, so the "and" is additive.
- 1770, "does not run, and nothing reports its absence": two additive facts about the same unimported module; neither "but" nor "so" fits.
- 1080-1083, the view's two selection places joined by "and": the two items the sentence before counts.
- Bold step labels (**Collect the responders.** and the rest): the Solutions files' standing convention, not §15 boldface overuse.
