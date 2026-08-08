[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/15_Context_Managers.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written during the deep review.

***

[] Reject

**Section:** The `__exit__()` Arguments (lead-in to `ignore_one.py`)
**Pattern:** §23 clarity, ambiguous pronoun (P1)

Current:
> Writing it as a class shows the suppression directly,
> in the two lines that decide the return value:

Proposed:
> Writing your own version as a class shows the suppression directly,
> in the two lines that decide the return value:

Why: the nearest antecedent for "it" is `contextlib.suppress`, named in the
sentence just before, and `suppress` is already a class, so the sentence reads
as a claim about the standard library rather than about the listing below it.

***

[] Reject

**Section:** The Async Protocol (paragraph after `async_manager.py`)
**Pattern:** global rule, cut "is what"; §23 dangling relative (P2)

Current:
> The shape is the generator form with `async` in front of it,
> and `asyncio.run()` is what starts the event loop the awaits need,
> which [Concurrency](19_Concurrency.md) covers.

Proposed:
> This is the generator form with `async` in front of it.
> `asyncio.run()` starts the event loop those awaits need,
> which [Concurrency](19_Concurrency.md) covers.

Why: a verb follows the cleft ("is what starts"), so it only delays the verb.
Splitting the sentence also gives the trailing "which" a single candidate to
attach to instead of three.

***

[] Reject

**Section:** The Async Protocol (last sentence)
**Pattern:** cross-reference convention (P2)

Current:
> Chapter 19 uses `async with` throughout, for `asyncio.TaskGroup`, locks,
> and semaphores; each of those is an object with the two `a`-prefixed methods.

Proposed:
> That chapter uses `async with` throughout, for `asyncio.TaskGroup`, locks,
> and semaphores; each of those is an object with the two `a`-prefixed methods.

Why: the chapter refers to its neighbors by title through a link, never by
number, and the link to Concurrency sits two sentences earlier.
A bare "Chapter 19" also goes stale silently if the book is renumbered.

***

[] Reject

**Section:** Choosing a Form (first sentence)
**Pattern:** §70 interpretive metadiscourse (P2)

Current:
> The chapter now offers four ways to get a context manager, in this order.

Proposed:
> There are four ways to get a context manager. Try them in this order.

Why: "The chapter now offers" describes the book rather than the subject, and
"now" dates the sentence against a reader who arrives from the table of
contents. The replacement gives the same instruction without the frame.

***

[] Reject

**Section:** Choosing a Form (last sentence)
**Pattern:** accuracy (P2)

Current:
> Whichever form you choose, the borrower's side stays two lines,
> and every change you make later happens on the other side of the `yield`.

Proposed:
> Whichever form you choose, the borrower's side contains two lines,
> and every change you make later happens inside the manager.

Why: two of the four forms have no `yield`, so the closing image contradicts the
paragraph it closes. The Object Pool section can keep the `yield` phrasing,
where the manager is a generator.
