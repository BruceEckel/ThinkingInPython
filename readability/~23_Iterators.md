[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/23_Iterators.md`

This chapter is close to clean. A full sweep of the Tier 1A/1B/2/3 vocabulary tables
turns up exactly one hit, "unpacking" at line 10, which is the Python term of art and
not a finding. There are no curly quotes, no spaced ` -- `, no boldface stacking, no
banned phrases, no bullet lists, no hedging, no promotional register, and the sentence
rhythm varies the way human technical prose does (two-word fragments like "`seen` is
how." next to 30-word explanatory sentences). Only two findings, both small: one
self-labeling aside and one restated sentence.

***

[] Reject

**Section:** The Pattern That Disappeared (the paragraph after `gof_iterator.py`)
**Pattern:** §39 Self-Labeling Significance (P1)

Current:
> The second pass is the part to notice.

Proposed:
> Cut this sentence.

Why: The label does the work the next sentence already does, and does it better:
"The generator was spent by the end of the first one, yet `first()` rewinds and
`traverse()` produces the same three values" makes the reader see the surprise
instead of being told where to look for it. Deleting the line loses no information.

***

[] Reject

**Section:** Reusable Algorithms (opening paragraph, before `reusable_algorithms.py`)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> Such a pipeline draws from an infinite source but computes only what the consumer takes.

Proposed:
> Cut this sentence.

Why: The next sentence makes the same point with the mechanism attached and a
condition this one omits ("Each stage pulls one item at a time, so an infinite source
is fine as long as something downstream stops it"), so the earlier sentence asserts
the infinite-source claim unqualified and is then immediately superseded.
