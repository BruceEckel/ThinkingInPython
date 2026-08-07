[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/12_Data_Classes_as_Types.md`

This chapter reads as human throughout.
A vocabulary scan for the Tier 1A/1B/2 word lists returned zero hits,
there is no boldface padding, no rule-of-three inflation, no signposting or
generic conclusion, no curly quotes, and no spaced ` -- `.
Sentence and paragraph lengths vary, and the explanations are anchored to named
listings rather than to abstractions.
Three small findings, all P2, and two of them borderline.

***

[] Reject

**Section:** Data Classes (paragraph after `display_messenger_class.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The dunder methods have indeed been generated,
> and you can see that the constructor arguments cover all the fields in `Messenger`.

Proposed:
> The dunder methods have indeed been generated,
> and the constructor arguments cover all the fields in `Messenger`.

Why: "you can see that" tells the reader to look at the listing they are already
looking at; the fact stands on its own without the frame.
The "indeed" is left in place, since it confirms the claim made just above the
listing rather than padding it.

***

[] Reject

**Section:** A Type Is a Set of Values (the *parse, don't validate* paragraph)
**Pattern:** §31 Manufactured Punchlines and Staccato Drama (P2, borderline)

Current:
> No other code repeats the check, because it cannot fail.
> An illegal value never produces a `Stars`.
> Illegal values are unrepresentable.

Proposed:
> No other code repeats the check, because it cannot fail.
> Illegal values are unrepresentable.

Why: three short declaratives in a row make the same claim, and the middle one
restates what the section already established
("the constructor refuses anything outside that set").
Borderline: the run may be deliberate emphasis, and the `Stars` sentence is the
concrete instance of the general line that follows it.

***

[] Reject

**Section:** The General Form of `replace()` (paragraph after `copy_replace.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2, borderline)

Current:
> The last case matters more than the convenience.

Proposed:
> Cut this sentence.

Why: the next two sentences make the point concretely, that `copy.replace()`
rebuilds through the constructor so `__post_init__()` runs on the copy,
so the label only tells the reader how much weight to give what follows.
Borderline: cutting it also drops the explicit contrast with the convenience
uses shown in the listing above, so this is a judgment call rather than a clear
win.
