[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/34_Composite_and_Interpreter.md

This chapter reads as human throughout.
A scan of the full Tier 1A/1B/2/3 vocabulary tables against the ~2,080 words of prose returned zero hits,
sentence and paragraph lengths vary, and nearly every paragraph carries a specific mechanism rather than a restatement.
Two findings only: one self-labeling tell, and one sentence whose description does not match the code beside it.

***

[] Reject

**Section:** Interpreter (paragraph beginning "The `Operators` base class...")
**Pattern:** §39 Self-Labeling Significance (P1)

Current:
> The `Operators` base class is the clever part.

Proposed:
> Cut this sentence.

Why: The label tells the reader the move is clever before showing it, and the next three sentences ("Every node inherits `__add__()` and `__mul__()`, and those methods do not compute anything. They build nodes.") already demonstrate exactly that.
Cutting leaves the paragraph opening on the mechanism, and `Operators` is still the running subject from the paragraph above.
Note the interaction with the later "The reason is structural rather than clever:" in the `t`-string section; if that line is a deliberate echo of this one, reject this block.

***

[] Reject

**Section:** Interpreter (same paragraph, four sentences later)
**Pattern:** Accuracy/clarity, outside the AI-tell catalogue (P0)

Current:
> Writing `x + 1` on two `Expr` values produces an `Add`,

Proposed:
> Writing `x + 1` produces an `Add`,

Why: `x + 1` is not an operation on two `Expr` values.
`1` is an `int`, which is why the very next sentence has to introduce `wrap()` and the reflected forms.
The cut keeps the sentence true without changing the example; if the intent was a different expression (`x + y`, say), that is a call only you can make, and I have not guessed at it.
