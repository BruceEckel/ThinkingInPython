> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/30_Observer.md`

Run right after the deep-review edits landed, so the new `changed`-flag
paragraph, the `source`-argument sentences, the re-entrancy caveat, the async
`list()`-copy and `gather()`-ordering additions, and the new exercise 4 get the
same scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose and its explanations are unusually concrete:
"a line of waits," "the same quiet accumulation as a lapsed listener," and the
`self_removing_observer.py` walkthrough all earn their place.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation.
The findings are one sentence added this pass that needs its actor named, one
paragraph that now carries four caveats, and a handful of watch-list words.

Line numbers refer to the chapter as it stands now.

***

[] Reject

**Lines 264-277 (the caveats paragraph, now four items)**
**Pattern:** §57 density, and a heading sentence that no longer counts correctly

The section opens:
> Two more things about Observer need saying.

and then covers the raising observer, the lapsed-listener leak, and, added this
pass as its own paragraph, re-entrant notification.
Three things, not two, and the count is stated in the text.

Proposed: drop the count from the opener and let the paragraphs stand.
> A few more things about Observer need saying.

Or, if you would rather keep a number, "Three more things about Observer need
saying." The first is safer: the next review that adds a caveat will not have
to touch the sentence again.

Note this is the same defect the deep review flagged in its own words when it
declined to apply the re-entrancy paragraph. The paragraph is now in and the
opener was not updated with it.

***

[] Reject

**Line 275 — "the value actually changing"**
**Pattern:** §23 empty adverb, watch list

Current (prose added this pass):
> Either make the write conditional on the value actually changing,
> or guard the setter with a re-entry flag.

Deleting "actually" changes nothing: "conditional on the value changing" is the
whole condition.

Proposed:
> Either make the write conditional on the value changing,
> or guard the setter with a re-entry flag.

***

[] Reject

**Line 86 — "It is simply a callable"**
**Pattern:** §23 empty adverb

Current:
> In Python an *observer* need not be an object implementing an `Observer` interface.
> It is simply a callable.

The contrast with the preceding sentence already carries the deflation, so
"simply" repeats it.

Proposed:
> In Python an *observer* need not be an object implementing an `Observer` interface.
> It is a callable.

Low confidence: this is a rhetorical beat in a two-sentence pair, and the pair
is doing the chapter's central move. Reject if you hear it as rhythm.

***

[] Reject

**Line 354 — "which is what calling an `async` function produces"**
**Pattern:** "is what" cleft (global rule)

Current:
> an observer must return an awaitable,
> which is what calling an `async` function produces.

Proposed:
> an observer must return an awaitable,
> which calling an `async` function produces.

***

[] Reject

**Line 231 — "a one-shot listener detaching itself is the natural example"**
**Pattern:** watch list, "itself" as flourish; also a comma splice into the
surrounding sentence

Current:
> An observer may react to a notification by unsubscribing,
> a one-shot listener detaching itself is the natural example,
> and that mutates `self._observers` in the middle of the loop walking it.

The middle clause is spliced between two others joined by "and," so the
sentence has to be read twice to see which clause "that" refers to.

Proposed:
> An observer may react to a notification by unsubscribing.
> A one-shot listener that detaches after its first call is the natural example,
> and the detach mutates `self._observers` in the middle of the loop walking it.

That also names what "that" was pointing at.

***

[] Reject

**Lines 72-76 (the new `changed`-flag paragraph)**
**Pattern:** two claims of different kinds in one paragraph

Current:
> The flag lets several mutations coalesce into one broadcast,
> and lets a subclass decide a change is not worth announcing;
> `set_celsius()` calls both halves at once, so nothing here needs it.
> Clearing the flag before the loop, not after,
> lets a change raised during notification survive to the next broadcast.

The first two lines say what the flag buys; the last two say why one line of
the listing sits where it does. They read as one thought and are two.

Proposed: split after "nothing here needs it," so the ordering point stands on
its own. No wording change.

Alternative, if you want the section shorter: cut the clearing-order sentence
entirely. The listing is a straw man the next section dismantles, and the
detail is only visible to a reader who knows `java.util.Observable`. I
recommend the split; the sentence explains a line that would otherwise look
arbitrary.

***

[] Reject

**Line 163 — "amounts to nothing more than a list of callbacks"**
**Pattern:** none; noting a keeper

No change proposed.
"Nothing more than" is on the watch list, but the global rule's carve-out names
this exact construction: a comparative where the diminishing is the point, and
its example is this sentence. Recorded so a later pass does not cut it.

***

[] Reject

**Line 174 — "a lambda equals only itself"**
**Pattern:** watch list, "only" and "itself" in four words

Current:
> `unsubscribe()` matches by equality, and a lambda equals only itself,

Both words are load-bearing here: the claim is identity-equality, and "a lambda
equals itself" without "only" would be trivially true of everything.

No change proposed. Recorded because a mechanical watch-list sweep would flag
it, and it should survive that sweep.
