> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Deep review of `Chapters/41_Functional--Toolkits.md` and
`Solutions/41_Functional--Toolkits.md`, run after the six rewrite passes
(elements-of-style, literal, positive, straighten, cohesion, antecedents).
Every error message, marker, and count the prose quotes was checked against
the pinned 3.15 interpreter: the `reduce`, `batched(strict=True)`, and
`zip(strict=True)` messages, the 2,692,537 undecorated `fib(30)` calls, the
`partial(pad, 5)` failure, `list(groupby(data))`'s empty groups, the
pipeline's 590 discard, the 14 repeat meetings, and `cached_property` taking
no lock. I also ran the history section's claim that caching `met()` on tuples
makes the schedule worse. It does: 20 of 21 pairs covered and 15 repeats,
against 21 and 14. The chapter uses no third-party library. The prose pass ran
without the global `~/.claude/CLAUDE.md` watch list, which is not present in
cloud sessions. It used this skill's rules, `banned_phrases.py`, and the repo
`CLAUDE.md` instead.

## Applied directly

- `partialmethod`: "Since Python 3.14 a `partial` object is a descriptor too" is now "A `partial` object is a descriptor too". The change follows the standing "modernize, don't narrate versions" ruling. The positive pass had added a similar "Since Python 3.12" to `cached_property`, and I cut it before committing that pass.
- `wraps`: the sentence said `help()` "reports `wrapper - None`". `help()` reports the wrapper, but that string comes only from the listing's `print()`. The two claims are now separate.
- `repeat`: "however many that is" had no clear referent. It now reads "however many calls there are".
- Composing the Pieces: "Four stages read from an infinite source" suggested four independent readers. It now says the pipeline stacks four stages on the source and none runs until `list()` pulls.
- Recursion: "the loop is as fast and as short as the recursion" understated the loop, which makes no calls and is faster. The sentence now says so.
- Recursion: in "you get the push and pop correct at every depth", the burden read as a guarantee. It now says "you must get the push and pop right".
- Groups of Any Size: the 1-factorization question was jargon quoted as a question without a question mark. It is now plain English: split every pair into rounds where each player appears once.
- Groups of Any Size: Kirkman's schoolgirl problem is the fifteen-student instance, and the chapter called it the general problem. The sentence now names the instance and states the real existence condition: a perfect trio schedule exists exactly when the roster size is 3 mod 6 (Ray-Chaudhuri and Wilson). It then says seven students have none, which ties the fact to the listing. The replaced wording, "each by a construction of its own", was not accurate.
- Choosing From the Toolkits: "holds one item in memory at a time" is false once `batched()` is a stage. It now says the pipeline holds "only the few items in flight".
- Exercise 1 asked for off-by-one errors. The solution's three pitfalls (the aliased seed list, `append()` for `extend()`, and the pop end) are not off-by-ones. The exercise now asks for "the mistakes the loop version allows that the recursive one cannot make".
- Solutions 1: the loop version is two lines longer than the recursive one, not one line.
- Solutions 1: the old text said `pop(0)` gives "a different order from the recursive version's", which implied that `pop()` matches. It does not: `pop()` visits right to left (`[6, 5, 4, 3, 2, 1]`). The paragraph now says neither end gives the recursive left-to-right order.
- During the passes, three fixes to what a pass wrote: the roadmap now names both dispatch tools, not only `singledispatch`; `takewhile()` pulls the total 590, not the batch; and "the counts it summed have moved" became "have grown".

## `student_pairs.py`: `closest` and `roomiest` name the opposite of what they hold

`closest = min(pool, key=lambda c: met(group, c))` picks the candidate the
group has met *least*, the most distant one in acquaintance terms.
`roomiest = min(groups, key=lambda g: met(g, extra))` picks the group whose
members `extra` has met least, not the group with the most room. A reader who
takes either name at face value will misread the greedy rule. The prose around
it says "adding whoever the current members have met the fewest times".

I would rename them `stranger` and `host`:
`stranger = min(pool, ...)` and `host = min(groups, ...)`, then
`host.append(extra)`. I did not make the change, because the same two names
appear in Solutions 41 exercise 6 and in three listings in
`Solutions/43_Functional--Confidence.md` (lines 249-320), which copy this
algorithm. The rename is mechanical, with no output change, but it reaches
another chapter's Solutions file. Whether 43's copies should follow is yours to
say.

[] Reject

## Note: `deep_review_db.md` calls chapter 41 exercise-free

`deep_review_db.md`'s standing rejection "39_Patterns--Pattern_Catalog: do not
add a conclusion or exercises" says "Chapters 39 and 41 are the book's only
two without exercises, and the absence is deliberate for both." Chapter 41 now
has six exercises and a Solutions file, which the shallow clone cannot date.
The exercises look intended, since each is answerable from the chapter and
together they cover its main claims. So the db sentence is probably stale and
should drop "and 41". I did not edit `deep_review_db.md`, which is outside
this run's files.

[] Reject

## Considered and declined

- The case-study title "Pairing Rotations" describes the circle-method setup, while the listing drops rotation for a greedy search. "Rotations" reads as the rounds of a schedule, which the listing produces, so the title still fits.
- `cmp_to_key` is also implemented in C, but the intro's list of C-implemented tools is framed as "the ones where speed matters most", so leaving it out is not an error.
- `recursion.py` carrying `sys.getrecursionlimit()` is a standing exemption in `deep_review_db.md`. Not raised.
- Hand-written `__init__` in `Weight` (`functools_total_ordering.py`): the prose explains it ("The plain class exists to show the tool"). Not raised.
