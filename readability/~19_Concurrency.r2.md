[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/19_Concurrency.md`

Run after the deep-review edits landed, so the new and moved prose gets the same
scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written or moved during the deep review.

***

[] Reject

**Section:** A Single Thread Still Races, end of the moved Locks subsection
**Pattern:** forward reference created by the move (P1)

Current:
> An `asyncio.Lock` is not thread-safe,
> for the same reason `asyncio.Queue` is not.

Proposed:
> An `asyncio.Lock` is not thread-safe either.

Why: the `asyncio.Queue` thread-safety warning is in "Coordinating Threads with
Queues", which is now roughly 700 lines *after* this sentence rather than before
it. The comparison pointed backward when the Locks subsection sat at the end of
the chapter; since the move it points forward at something the reader has not
met. The two sentences after it already give the reason in full, so the
comparison is not carrying information.

***

[] Reject

**Section:** the chapter introduction
**Pattern:** §23 clarity, an awkward compound preposition (P2)

Current:
> The second big shift was in where parallelism gets decided.

Proposed:
> The second big shift changed who decides to use parallelism.

Why: "was in where" stacks two prepositions on a copula, and the paragraph is
about an actor moving (from the OS to the language), which "who decides" names
directly.

***

[] Reject

**Section:** Why Speedup Isn't Linear (after `task_scaling.py`'s output)
**Pattern:** §23 clarity, stacked nouns (P2)

Current:
> and can turn back upward once the cost of one more chunk to pickle outweighs the better load balancing.

Proposed:
> and can turn back upward once pickling one more chunk costs more than the better load balancing saves.

Why: "the cost of one more chunk to pickle" makes the reader assemble a noun, a
number, and an infinitive before the verb arrives.
Putting the two activities in subject position lets the sentence compare them
directly, which is what it is doing.

***

[] Reject

**Section:** Measuring the Difference (after `task_vs_thread_memory.py`)
**Pattern:** §57 structure, a note inserted mid-argument (P2)

The paragraph now runs: a thread's stack could hold hundreds of tasks → *the
figures vary, so the listing asserts bounds and prints numbers under
`--numbers`* → the stack figure is address space, the task figure is measured
heap → the comparison favors tasks by hundreds to one.

Proposed: move the two `--numbers` sentences to the end of the paragraph, after
"The comparison favors tasks over threads by hundreds to one."

Why: the inserted note is about how the listing reports, and it currently splits
the claim from the explanation of what the two figures actually measure.
At the end it reads as the natural "and here is how to see your own numbers"
close.

***

[] Reject

**Section:** Locks, Semaphores, and Failure Modes (opening)
**Pattern:** accuracy, a section as the subject of an action (P2)

Current:
> [A Single Thread Still Races](#a-single-thread-still-races)
> lost updates to shared mutable state, and an `asyncio.Lock` restored them,

Proposed:
> `async_race.py` in [A Single Thread Still Races](#a-single-thread-still-races)
> lost updates to shared mutable state, and an `asyncio.Lock` restored them,

Why: a section cannot lose an update; the listing did.
Naming the listing also tells a reader which program to look back at, which is
the point of the sentence.
