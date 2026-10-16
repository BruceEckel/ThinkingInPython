> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 30_Patterns--Observer

The chapter reads as finished technical prose.
It has no Tier 1A vocabulary, no stacked transitions, no signposting, no staccato runs, and sentence lengths that vary.
Today's metadiscourse, colon, straighten, and claims passes left little for this one: a restated pair of sentences, one superficial "-ing" tail, an idiom, and a missing comma.
All four were applied directly.
This file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 283-284, treadmill (the two sentences restated the discard the paragraph had stated already): "That alternative accepts more callables, including mistaken ones. If a responder returns a value, `announce()` quietly drops it." -> "That alternative also accepts a responder that returns a value by mistake. `announce()` quietly drops the value."
- Line 356, idiom: "but for most cases the *Observer* pattern is only a list of responders" -> "but in most cases ...".
- Line 583, §3 superficial "-ing" tail: "Over a long run the broadcaster accumulates lapsed listeners, creating a memory leak." -> "Lapsed listeners that accumulate over a long run are a memory leak."
- Line 1494, comma before "but" joining two independent clauses: "The window looks the same but the canvas's list of items grows" -> "The window looks the same, but the canvas's list of items grows".

## Considered and declined

- Line 159-160, "copying `_observers` via `list(self._observers)` appears redundant. It is not." A short beat answering a real objection a reader brings to the listing, and the section then explains it. Kept (recurring keep: a short emphatic fragment is a beat).
- Line 484, "a lambda equals only itself": binding keep in `readability_db.md`.
- Line 623-626, "With `Broadcaster`, a responder that needs a weak reference creates and holds that reference." Close to a restatement of the paragraph's first sentence, but it frames the per-responder choice against the alternative broadcaster named just before it. Cutting it leaves the paragraph ending on the alternative. Kept.
- Line 950-957, the paragraph saying `published()` "writes the pair once, as nested functions" and the next saying it "builds the two functions a `property` needs": overlapping, but the first contrasts `published()` with the `@property` form and the second opens the tagged walkthrough. Kept.
- Line 804 and 888, "We can simplify both using `__setattr__()`" and "Using decorators, we can simplify and automate ...": the author's "we", left as written.
- Line 1117, "turning each coroutine into its own argument": an "-ing" phrase by shape, but it states what the `*` unpacking does, not a vague significance claim.
- Line 1267, "but a real caller rarely adds that wait": "real" contrasts a caller in a program with this listing's `main()` (§34 carve-out, named contrast).
- Line 1762, "Measuring is the thermometer's actual job.": "actual" contrasts with the two jobs *Observer* adds, named in the next sentence (§34 carve-out).
- Line 345-346, "because that is the shortest way ..., not because the pattern requires a base class": a negative parallelism by shape, but the contrast is the claim.
