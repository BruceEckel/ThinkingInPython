> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/35_Flyweight.md` (r2)

The chapter is still one of the cleanest in the run.
A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, there
is no boldface, no curly quotes, and no spaced ` -- `.
All three findings from the first review are applied and none was rejected.

Everything below sits in prose that has never had a readability pass: the ten
manifest edits the deep review made while it was being written, and the seven
prose additions today's apply made.

***

**Section:** `## Which Pool Should You Use?` (the new closing section)
**Pattern:** Sentence-length uniformity (Structure and Rhythm Tests), plus a
dangling opener (P2)

Current:
> Four mechanisms, and the question that decides between them is how much you know about the set of values.
> If you know it as you write the program,
> use an `Enum` and let the language hold the pool.
> If callers must keep writing `C(...)`,
> intern in `__new__()` and pay the bookkeeping.
> If the set is unbounded,
> use a `WeakValueDictionary` so the pool cannot become a leak.
> Otherwise use a `@cache` factory, which is the least machinery for the job.

Two problems, and the second is the one I cannot settle for you.

The opener dangles. "Four mechanisms" is a noun phrase with nothing to attach
to; the sentence's real subject is "the question," so the count is left
hanging in front of it. The fix is one word:

> The chapter showed four mechanisms, and the question that decides between them
> is how much you know about the set of values.

The second problem is rhythm. Three consecutive `If X, do Y` sentences and then
an `Otherwise` is a decision table written as prose, and the parallelism is
exact enough that the four run together on a read-aloud. The deep review asked
for four sentences organized by the deciding question, so the shape is
deliberate; the question is whether it is too regular. Breaking one of the four
fixes it, and the `Enum` case is the natural one because it is the only
mechanism that needs no runtime pool at all:

> If you know it as you write the program, an `Enum` holds the pool for you and
> nothing runs at all.
> If callers must keep writing `C(...)`, intern in `__new__()` and pay the
> bookkeeping.
> If the set is unbounded, use a `WeakValueDictionary` so the pool cannot become
> a leak.
> Otherwise use a `@cache` factory, which is the least machinery for the job.

Take the opener fix regardless. The rhythm change is a voice call, and a case
can be made that a decision table *should* read as one.

[] Reject

***

**Section:** "Interning in the Constructor," the new `_pool` subclass paragraph
**Pattern:** §69 Colon Reveals, plus undefined jargon (P2)

Current:
> `_pool` is keyed by the components alone and inherited by every subclass,
> so `Color` here is a leaf: a subclass would collide with it,
> receiving whichever object asked for those components first.

Proposed:
> `_pool` is keyed by the components alone and inherited by every subclass,
> so `Color` cannot be subclassed safely.
> A subclass would collide with it,
> receiving whichever object asked for those components first.

Why: *leaf* is standard vocabulary for a class not meant to be subclassed, but
the book has not used it, and the sentence introduces it with a colon and then
explains it, which is the reveal shape rather than a definition. Saying the
consequence outright costs the same number of words and needs no new term.
"Here" is filler in the same clause: `Color` is the only `Color` under
discussion.

This paragraph is new with today's apply.

[] Reject

***

**Section:** "Intrinsic and Extrinsic State," end of the frozen-all-the-way-down
paragraph
**Pattern:** Global watch list, "Consider rewriting" tier: `is what` (P2)

Current:
> Every field here is immutable, which is what makes the sharing safe.

Proposed:
> Every field here is immutable, which makes the sharing safe.

Why: the deletion test passes, so the cleft is filler. The giveaway is the verb
sitting right after it, which the global rule names: "is what makes" only delays
"makes."

From the deep review's manifest, not from today's apply.

[] Reject

***

**Section:** "Intrinsic and Extrinsic State," end of the paragraph after
`tile_map.py`
**Pattern:** Global watch list, `is what`, plus an abstract subject (P2)

Current:
> The object count is what the listing can show;
> exercise 2 measures the memory behind it.

Proposed:
> The listing can show the object count;
> exercise 2 measures the memory behind it.

Why: the cleft here does survive a bare deletion, so this is a rewrite rather
than a cut. Fronting "the object count" puts an abstraction in the subject slot
and pushes the actor (the listing) into the predicate, which is the buried-subject
shape. The proposed version says the same in fewer words with the listing doing
the showing.

New with today's apply, added because the memory measurement stayed an exercise
rather than becoming a listing.

[] Reject

***

**Section:** "Interning in the Constructor," lead-in to `interned_color.py`
**Pattern:** Loose apposition (no §; skill step 5, tangled passages) (P2)

Current:
> Here the cache is keyed by the constructor arguments instead of a single fixed key,
> a pool of singletons sometimes called *Multiton*:

Proposed:
> Here the cache is keyed by the constructor arguments instead of a single fixed key.
> A pool of singletons keyed this way is sometimes called *Multiton*:

Why: as written, the appositive has no clear head. It cannot be the cache (a
cache is not a pool of singletons) and it cannot be the key, so the reader has
to attach it to the whole clause. Making it its own sentence names what is being
named, and the colon still hands off to the listing.

Lowest-confidence item here. If you would rather the term arrive without a
sentence of its own, the parenthetical form works too: "...instead of a single
fixed key (a pool of singletons is sometimes called *Multiton*):".

New with today's apply, from the deep review's block about chapter 39's catalog
row linking to a section that never used the word.

[] Reject
