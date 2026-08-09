> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/33_Visitor.md` (r2)

The chapter's older prose still reads clean.
A full sweep of the Tier 1A, Tier 1B, and Tier 2 vocabulary tables (§7) returned
zero hits, the specifics are checkable throughout, and the two `simply` adverbs
the first review flagged are gone.

Everything below sits in prose added or moved by the deep review that ran just
before this pass: the `dispatch_trace.py` lead-in and follow-through, the new
`The Price of the Empty Base` heading, the registry paragraph, and the reworked
`*Visitor* still has a place` sentence.

The clear-cut fix was applied to the chapter directly (listed below);
the two blocks that remain are the ones needing your judgment.

## Applied directly

- Paragraph after `dispatch_trace.py`: "The first hop lands on
  `Predator.visit`" → "The first hop reaches `Predator.visit`" ("lands" is on
  the global "Don't use" list; the same paragraph already uses "reaches" two
  sentences later, so the two hops now read parallel).

***

**Section:** `## The Price of the Empty Base` (heading), and the paragraph
beginning "Notice where the behavior lives"
**Pattern:** §29 Fragmented Headers / §57 Excessive Structure (P2)

The new heading covers two paragraphs, and it names only the first.
The `Any`/`Protocol` paragraph really is about the price of an empty visitor
base. The "Notice where the behavior lives" paragraph that follows it is about
a different price: Python's lack of method overloading pushing the operation
bodies onto the flowers. A reader who takes the heading as a contract will read
the second paragraph wondering what it has to do with the base class.

Three ways out, and this is the one finding here where I cannot pick for you.

**Option A: retitle to cover both.** Something like `## What the Classic Shape
Costs` or `## Two Prices`. Both paragraphs are prices, so one heading can hold
them. Cost: the title stops naming the concrete thing (`Any`, the empty base)
and gets vaguer.

**Option B: leave it.** The second paragraph ends on the line that motivates
the whole `singledispatch` section, so it wants to sit last no matter what the
heading says, and a slightly wide heading is a small price. Cost: nothing,
beyond the mismatch above.

**Option C: give the second paragraph its own `##`.** Cost: three short
sections in a row where the chapter had one, and a new anchor to maintain.
I would not do this one.

I lean toward A if you want the heading honest, B if you want the chapter to
stop changing shape. Not C.

[] Reject

***

**Section:** Paragraph after `dispatch_trace.py`
**Pattern:** §39 Self-Labeling Significance (P1)

Current:
> The second hop is the one that earns the listing.
> For `Chrysanthemum` it reaches the override,
> and for `Gladiolus` it reaches `Flower.eat`,
> which is the visible form of the flower-side dispatch having nothing to say.

Proposed:
> The second hop is the interesting one.
> For `Chrysanthemum` it reaches the override,
> and for `Gladiolus` it reaches `Flower.eat`,
> the flower-side dispatch having nothing to say, now visible in the output.

Why: two problems in one passage.

"is the one that earns the listing" labels the content as important instead of
letting it be important, and it talks about the book's editorial decisions
rather than about dispatch. The reader does not care whether a listing earned
its place.

"the visible form of X" is a nominalization that buries the verb. The sentence
is saying the output now shows something the previous paragraph could only
assert, and it can say that with the noun phrase and a short tail.

If the proposed replacement first line reads too flat, the alternative is to
cut it and let the two cases carry the paragraph: "For `Chrysanthemum` the
second hop reaches the override, and for `Gladiolus` it reaches `Flower.eat`,
..." That drops a sentence and loses nothing, and it is what I would do if you
dislike "the interesting one."

This stays a block because both fixes are defensible and the first line of the
replacement is itself a (milder) self-label: the choice between softening the
sentence and cutting it is yours.

[] Reject

***

## Considered and declined

**Lead-in above `dispatch_trace.py` — "The output above shows results, not
mechanism."**
Flagged as §70 metadiscourse, with "names what happened, not which methods
ran" as the candidate. Declined by the block's own criterion: "mechanism" is
established book vocabulary (thirty-plus uses across the chapters, including
"the open-method mechanism that *Visitor* fakes" later in this chapter).

**"or when a framework you do not own already calls that hook."**
"Already" is on the "Avoid if possible" list, but here it earns its place:
the call site exists whether you want it or not. The global rule keeps a
watched word that draws a real contrast. Left alone.
