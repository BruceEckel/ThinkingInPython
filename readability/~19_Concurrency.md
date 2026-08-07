[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/19_Concurrency.md`

This chapter reads as human technical prose throughout.
No Tier-1A vocabulary, no curly quotes, no spaced ` -- `, no banned strings ("reach for", `from __future__ import annotations`), no boldface or bullet inflation, and the bold labels in Guidelines are full sentences so the §58 carve-out applies.
The only tells are four small ones near the ends of sections: a fake-profound closer, one bare "real" intensifier, one restatement loop, and one rhetorical question asked for the third time in ten lines.

***

[] Reject

**Section:** Structured Concurrency with `TaskGroup` (end of the `gather_with_exceptions.py` discussion)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> `TaskGroup` has no such mode.
> Its contract is all-or-cancel.
> Keeping siblings alive past a failure means catching exceptions inside each task yourself.
> Use `TaskGroup` where a failure should stop the batch.
> `gather()` provides failure-as-data.

Proposed:
> `TaskGroup` has no such mode.
> Keeping siblings alive past a failure means catching exceptions inside each task yourself.

Why: "Its contract is all-or-cancel" repeats "`TaskGroup`'s all-or-cancel contract" from the first line of this same paragraph, and the closing two sentences restate the paragraph's own point (and the Guidelines bullet that already says it).
The trimmed version ends on the concrete consequence instead of a summary of what was just said.

***

[] Reject

**Section:** One Task, Many Backends (final paragraph, just before the `_images/concurrency_models` figure)
**Pattern:** §32 Aphorism Formulas, fake-profound kicker ending (P1)

Current:
> Most of what concurrency asks of you is knowing what a shared interface hides,
> and what it leaves different underneath.

Proposed:
> Cut both lines.

Why: The two preceding sentences already state this concretely ("`Executor` unifies backends that share a blocking, submit-and-wait shape. `await` unifies backends that share only a result that arrives later. Everything else about the backends stays different.").
The closer generalizes them into an unearned claim about concurrency as a whole and adds no information; §32 says to delete the kicker and end on the clearest concrete sentence already in the draft.

***

[] Reject

**Section:** Are Threads Still Necessary?
**Pattern:** §43 Rhetorical Question Openers, self-answered Question/Answer pair (P2)

Current:
> What role remains for threads?
> Creating bridges to code that doesn't cooperate with an event loop.

Proposed:
> The remaining role for threads is in creating bridges to code that doesn't cooperate with an event loop.

Why: This is the third time the same question is posed in ten lines: the heading asks it, then "does new code ever need threads?" asks it, then this asks it again and answers with a fragment.
Folding the question into its answer keeps the two earlier askings intact and gets to the point.

***

[] Reject

**Section:** Measuring the Difference (first line of the section)
**Pattern:** §34 Real/Actual Adjective Inflation (P1)

Current:
> You can support the claim that a thread costs real memory while a task costs much less.

Proposed:
> You can support the claim that a thread costs far more memory than a task.

Why: "real memory" is a bare intensifier with no contrast named, and it works against the section's own closing precision, which says the thread figure is "address space set aside whether every byte is touched or not" while the task figure is measured heap.
"far more memory" is supported by the same section's "hundreds to one."
