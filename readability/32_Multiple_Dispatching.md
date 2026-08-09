> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/32_Multiple_Dispatching.md`

Run right after the deep-review edits landed, so the rewritten opening
sentence, the new `Protocol` clause, the new `exact_match.py` prose, the
`singledispatchmethod` paragraph, the rewritten double-dispatch criterion, the
`getattr()` explanation, the three new section headings, and the new closing
section get the same scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose. Its best writing is the duel walkthrough
("`Paper.eval_scissors()` returns `WIN` ... scissors cut paper") and the
`isinstance()`-ladder paragraph, which names the thing most readers would have
written and says why not.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation.
The findings are two collisions created by this pass, one paragraph whose
subject drifts, and a few watch-list words.

Line numbers refer to the chapter as it stands now.

***

**Lines 280 and 283 — "the version a reader writes first," twice, meaning
different things**
**Pattern:** repetition that reads as a contradiction

The new `singledispatchmethod` paragraph ends:
> registering on a shared base gives every subclass one dispatcher,
> so the first dispatch never happens,
> and that is the version a reader writes first.

and the next paragraph opens:
> The version most programmers write first is neither of these:
> it is an `isinstance()` ladder inside `compete()`,

Two consecutive paragraphs claim to name what a reader writes first, and they
name different things. Both claims are true of different situations, and read
back to back they cancel.

Proposed for the first:
> registering on a shared base gives every subclass one dispatcher,
> so the first dispatch never happens.
> That mistake is easy to make and hard to see.

That keeps the warning and leaves "the version most programmers write first"
to the paragraph that earns it.

[] Reject

***

**Line 231 — "worth watching happen"**
**Pattern:** §53 endorsement frame

Current (prose added this pass):
> Exact matching is the property that surprises people,
> so it is worth watching happen.

The clause rates the demonstration instead of introducing it, and "watching
happen" is awkward besides.

Proposed:
> Exact matching is the property that surprises people, so here it is failing.

Or, if that reads too clipped:
> Exact matching is the property that surprises people.
> This listing shows it refusing a subclass.

I recommend the second.

[] Reject

***

**Lines 296-299 (the rewritten double-dispatch criterion)**
**Pattern:** a three-part sentence whose last clause answers a question the
first two did not raise

Current:
> Use the double-dispatch version when the behavior for a combination belongs to the class rather than to the pairing:
> when it reads the object's own state,
> or when a subclass should be able to override one combination and inherit the rest.
> A table cell can hold a function, so size alone never forces the choice.

The first three lines give the criterion. The fourth rebuts a criterion the
paragraph never stated, so a reader who did not see the old "will not fit in a
table cell" wording will wonder who suggested size.

Proposed: put the rebuttal first, as the thing being corrected.
> A table cell can hold a function, so the size of the behavior never forces the choice.
> Use the double-dispatch version when the behavior for a combination belongs to the class rather than to the pairing:
> when it reads the object's own state,
> or when a subclass should be able to override one combination and inherit the rest.

[] Reject

***

**Line 316 — "a type written decades after `int` was"**
**Pattern:** none flagged; noting a keeper

No change proposed.
This is the sentence that makes reflected operators matter, and the elision at
the end ("after `int` was") is the kind of thing a person writes and a model
does not.
Recorded so a later tightening pass leaves it alone.

[] Reject

***

**Line 303 — "already perform"**
**Pattern:** watch list, "already"

Current:
> Python's own operators already perform a two-step dispatch,
> and it answers the `Number + Number` question that opened this chapter.

"Already" is doing real work here: the point is that you get this dispatch
without building it, in contrast to the two hand-built versions above. The
rule's test (does deleting it change the meaning?) says keep.

The pronoun is the problem instead. "It answers" has "a two-step dispatch" as
its nearest antecedent but means the operator mechanism as a whole.

Proposed:
> Python's own operators already perform a two-step dispatch,
> which answers the `Number + Number` question that opened this chapter.

[] Reject

***

**Line 222 — "just as easily"**
**Pattern:** §23 filler

Current:
> Notice the flexibility of dictionaries.
> A tuple works as a key just as easily as a single object.

"Just as easily" compares ease where the real claim is that it works at all.

Proposed:
> Notice the flexibility of dictionaries.
> A tuple works as a key exactly as a single object does.

Or drop the comparison: "A tuple works as a key." The two-line version above is
the one I would take, since the contrast with a single object is the point.

[] Reject

***

**Line 11 — "something you probably never consider"**
**Pattern:** §68 faux-insight setup

Current:
> The answer starts with something you probably never consider.
> Python dispatches on one type at a time.

The sentence tells the reader they have not thought about this, then states an
ordinary fact about the language. Cutting it costs nothing.

Proposed:
> The answer starts with a fact about the language that rarely comes up.
> Python dispatches on one type at a time.

Or cut the line and open on "Python dispatches on one type at a time."

Low confidence: this sentence carries over from *Thinking in Java* and the
voice call is yours. The second option is the stronger edit if you want one.

[] Reject

***

**Line 393 — "describes nothing at all"**
**Pattern:** watch list, "at all"

Current:
> Widening the return to `Any` describes nothing at all and turns off checking for every caller.

The second half already states the consequence, so "at all" only intensifies.

Proposed:
> Widening the return to `Any` describes nothing and turns off checking for every caller.

[] Reject
