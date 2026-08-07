[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/04_Control_Flow.md`

This chapter reads as human throughout.
A scan for the Tier 1A/1B/2 vocabulary, banned literals (`reach for`, `from __future__ import annotations`), spaced ` -- `, curly quotes, boldface stacking, rule-of-three padding, signposting, and hedge stacking turned up nothing;
the three findings below are one grammar slip and two small clarity edits, not AI tells.

[] Reject

**Section:** Pattern Matching (line 229)
**Pattern:** §7 Tier 3, vague praise instead of the specific (P2)

Current:
> It is reminiscent of a C `switch`, but is much more powerful:

Proposed:
> It is reminiscent of a C `switch`, but a pattern can look inside a value and pull out its parts:

Why: "much more powerful" is an unsupported comparative at the point it appears; the concrete reason is already in the chapter two paragraphs later ("The first `case` destructures the split command ... binds the second item to `direction`").
The proposal also fixes the subjectless "but is."

***

[] Reject

**Section:** Errors and Exceptions (line 263)
**Pattern:** grammar, dangling comparison (no §; skill step 5, "fix the patterns, errors, and tangled passages") (P1)

Current:
> Like C++ and Java, an exception propagates up the call stack until it finds a handler.

Proposed:
> As in C++ and Java, an exception propagates up the call stack until it finds a handler.

Why: as written, the sentence compares an exception to two programming languages.
Every other "Like ..." opener in the book compares like things (`Like the `dict`, it has fast membership tests`), so this one is an outlier rather than a house style.

***

[] Reject

**Section:** Context Managers (lines 440-442)
**Pattern:** tangled relative clause (P2)

Current:
> Closing the file is cleanup that runs whether or not the block succeeds,
> which [Cleanup](10_Cleanup.md)
> contrasts with letting Python's garbage collector do it.

Proposed:
> Closing the file is cleanup that runs whether or not the block succeeds.
> [Cleanup](10_Cleanup.md) contrasts this with letting Python's garbage collector do it.

Why: the "which" has no noun to attach to, so the reader has to reconstruct that the contrast is between guaranteed cleanup and collector-timed cleanup.
Borderline: the sentence is followable as written, and the only change is splitting it in two.
