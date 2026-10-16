> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 22_Patterns--Data_Transfer_Objects

The chapter reads as finished technical prose: no Tier 1A vocabulary, no stacked transitions, no signposting, no staccato runs, and sentence lengths that vary.
The claims sweep and continuity read earlier today left little for this pass.
One mechanical fix was applied directly.
This file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 197, §7 Tier 1B ("serves as"): "so a `Color` can serve as a `dict` key or a `set` element" -> "so a `Color` can be a `dict` key or a `set` element".

## Considered and declined

- Line 48, §23 empty adverb: "the `dict` that the `**kwargs` parameter automatically creates". The deletion test barely fires, but "automatically" tells the reader that Python builds the `dict` with no code from the class, which is the point of the one-line constructor. Kept.
- Line 199-205, §32 aphorism by shape: "An immutable type needs immutable fields." It states the paragraph's rule in concrete terms (the list leak and the `hash()` failure precede it), not a metaphor. Kept.
- Line 435, colon after "Tuple operations return plain tuples": the colon delivers the example, and "plain" contrasts `tuple` with `Point` (recurring keep).
- Line 447, "worth writing only to show how `SimpleNamespace` works underneath": the `readability_db.md` "worth" keep names this sentence.
- Line 444-446 and 453-462, the "Use X for... Choose Y when..." run: a decision table written as prose, covered by the parallel-decision-table convention.
- Line 463, link text "cannot validate itself": reflexive and load-bearing, and it echoes the target heading.
- Line 468, "the data stays a real dict": "real" contrasts the dict at runtime with the key names that exist for the type checker alone (§34 carve-out, named contrast).
- Line 372, "sets that order implicitly": the word marks the contrast with `order=True`'s explicit request two sentences later.
