[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/03_Containers.md

This chapter is clean. A full pass over the prose turned up no Tier 1A vocabulary,
no significance inflation, no signposting, no hedging, no boldface or bullet slop,
no chatbot artifacts, and no rule-of-three padding; sentence and paragraph lengths
vary the way human technical prose does. The three findings below are small clarity
edits, not AI tells, and one of them is explicitly borderline.

***

[] Reject

**Section:** Lists (paragraph after `sorting.py`)
**Pattern:** §7 Tier 1B, clarity edit (P2)

Current:
> `sorted(x)` returns the result,
> so `x = x.sort()` binds `None` and loses the list.

Proposed:
> `sorted(x)` returns the result while `x.sort()` returns `None`,
> so `x = x.sort()` binds `None` and loses the list.

Why: The "so" currently hangs off the wrong clause: `sorted()` returning a result
is not what makes `x = x.sort()` bind `None`. The missing half of the contrast is
already stated two paragraphs up and in the listing itself, so nothing new is
introduced.

***

[] Reject

**Section:** Sets (paragraph after `sets.py`)
**Pattern:** §35 Moral-Adjective Category Errors (related note: category slips) (P2)

Current:
> The order these sets print is CPython's hashing rather than a guarantee.

Proposed:
> The order these sets print comes from CPython's hashing and is not a guarantee.

Why: An order is not a hashing, so the copula equates two different kinds of thing.
The Dictionaries section already made this point ("the order it prints is an
artifact of hashing"), so cutting the sentence outright is also defensible if you
would rather not say it twice.

***

[] Reject

**Section:** Sets (paragraph introducing `membership_cost.py`)
**Pattern:** §7 Tier 1B, clarity edit (P2), borderline

Current:
> The speed is the reason to convert a `list` to a `set` before repeated lookups.

Proposed:
> Speed is the reason to convert a `list` to a `set` before repeated lookups.

Why: "The speed" reads as a definite reference to a speed the reader has already
been shown, and the preceding paragraph was about operators and methods, not timing.
Borderline: the sentence is understandable as written, and this is a one-word edit.
