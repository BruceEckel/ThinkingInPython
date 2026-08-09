> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/35_Flyweight.md` (r2)

The chapter is still one of the cleanest in the run.
A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, there
is no boldface, no curly quotes, and no spaced ` -- `.
All three findings from the first review are applied and none was rejected.

Everything below sat in prose that had never had a readability pass: the ten
manifest edits the deep review made while it was being written, and the seven
prose additions today's apply made.

The clear-cut fixes were applied to the chapter directly (listed below);
one block remains for your judgment.

## Applied directly

- `Which Pool Should You Use?` opener: "Four mechanisms, and the question
  that decides between them..." → "The chapter showed four mechanisms, and
  the question that decides between them..." (the bare noun phrase had
  nothing to attach to).
- `_pool` subclass paragraph: "so `Color` here is a leaf: a subclass would
  collide with it" → "so `Color` cannot be subclassed safely. A subclass
  would collide with it" (§69 reveal introducing *leaf*, a term the book has
  not used; the consequence stated outright costs the same words; "here" was
  filler).
- "Every field here is immutable, which is what makes the sharing safe." →
  "which makes the sharing safe" (cleft; the deletion test passes).
- "The object count is what the listing can show" → "The listing can show
  the object count" (buried subject; the listing does the showing).
- Lead-in to `interned_color.py`: "instead of a single fixed key, a pool of
  singletons sometimes called *Multiton*:" → "instead of a single fixed key.
  A pool of singletons keyed this way is sometimes called *Multiton*:" (the
  appositive had no head: neither the cache nor the key is a pool of
  singletons).

***

**Section:** `## Which Pool Should You Use?` (the new closing section)
**Pattern:** Sentence-length uniformity (Structure and Rhythm Tests) (P2)

With the opener fixed, the remaining question is rhythm. Three consecutive
`If X, do Y` sentences and then an `Otherwise` is a decision table written as
prose, and the parallelism is exact enough that the four run together on a
read-aloud. The deep review asked for four sentences organized by the deciding
question, so the shape is deliberate; the question is whether it is too
regular. Breaking one of the four fixes it, and the `Enum` case is the natural
one because it is the only mechanism that needs no runtime pool at all:

> If you know it as you write the program, an `Enum` holds the pool for you and
> nothing runs at all.
> If callers must keep writing `C(...)`, intern in `__new__()` and pay the
> bookkeeping.
> If the set is unbounded, use a `WeakValueDictionary` so the pool cannot become
> a leak.
> Otherwise use a `@cache` factory, which is the least machinery for the job.

This is a voice call, and a case can be made that a decision table *should*
read as one.

[] Reject
