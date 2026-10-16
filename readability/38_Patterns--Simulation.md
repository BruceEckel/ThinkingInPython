> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 38_Patterns--Simulation

This chapter carried almost no AI-writing tells.
Its prose had already been through a straighten pass with the and-split rule, a terminology round, and a metadiscourse pass, and a watch-list scan found no hit that the recurring keeps in `readability_db.md` do not cover.
One fix had one sensible answer and is applied below.
The file holds no live block, so it is the record of the applied change and of the findings judged and kept.
`readability_db.md` was read first, and no prior `readability/~38_*` review exists.

## Applied directly

- Line 15, and-split (global rule): "The formula determines its shape, and the grains gather on it." -> "The formula determines its shape." / "The grains gather on it."
  The subject changes and the relation is a contrast ("while" fits): the formula sets the figure, and the grains' own motion puts them on it, which is the point the "Order from Noise" section makes.

## Considered and declined

- Line 7 and line 1435, "A simulation models a set of objects that act on their own and interact through shared state" and its near-verbatim repeat in "The Less the Agents Know".
  §70 restatement by shape, but the closing section quotes the opening definition on purpose, so that "The grains are the limiting case of that definition" has a definition to point at.
- Lines 13-16 and 1164-1174, the "confirm a design" versus "discover behavior" contrast stated in the introduction and again at the head of "Order from Noise".
  The second statement opens the section that delivers the contrast and adds the concrete half (`amplitude()` sets the shape, no line computes how the walks reach it), so it is not a recap.
- Line 175, "`claim()` holds the rule on which the whole program depends."
  §1 significance by shape, but the claim is literal: the one-rat-per-cell guarantee and the next three sentences rest on it.
- Lines 361-362 and 427-428, "the race that `claim()`'s atomicity resolves" and "That is the race `claim()`'s atomicity exists to resolve. A perfect maze like `amaze.txt` cannot produce it."
  Restatement across a heading, but the second ties `ring_contention.py`'s output back to the claim the earlier paragraph set up, which is the listing's reason to exist.
- Line 50, "the rat has reached a dead end and its task ends".
  An "and" across a subject change, but the two clauses are consecutive steps of one event (the dead end ends `run()`), and the straighten pass kept it.
- Line 1043, "The teleports are not shortcuts but the only way through."
  §9 negative parallelism by shape, but it corrects the assumption a reader brings to a teleport, and the next sentence supports it with the `ValueError` `solve()` raises without them.
- Lines 1337-1339, "Noise can carry a grain into a quiet place. It cannot carry the grain back out. The randomness produces the order instead of opposing it."
  Three short sentences closing a section (§31, §32), but each states the mechanism in concrete terms, and the last is the section's conclusion rather than a decorative kicker.
- Lines 1455-1456, "When behavior emerges, reading the code is not enough. Run it."
  A short closing beat; the readability_db keep for a beat that does work applies, and the instruction is the chapter's lesson.
- Line 492, "because each view drives or replays its model itself."
  "itself" draws the contrast with the *Observer* subscription the sentence says is absent, so it is load-bearing.
- Line 941, "so it works entirely in rooms and the moves between them."
  "entirely" carries the exclusion (no grid coordinates); deleting it weakens the claim.
- Line 1450, "Real sand on a real bowed plate".
  §34 by shape, with the contrast named: the model's sand.
- Line 1371, "the collapse as it happens".
  "happen" is on the watch list, but the phrase echoes the section heading, which stays.
