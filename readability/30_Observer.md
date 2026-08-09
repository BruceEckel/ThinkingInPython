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

The clear-cut fixes were applied to the chapter directly (listed below);
the two blocks that remain are the ones needing your judgment.

## Applied directly

- Line 264: "Two more things about Observer need saying." → "A few more
  things about Observer need saying." (the section now covers three: the
  raising observer, the lapsed listener, and the re-entrancy paragraph added
  this pass; the countless opener also survives the next added caveat).
- Line 231: the spliced middle clause is now its own sentence: "An observer
  may react to a notification by unsubscribing. A one-shot listener that
  detaches after its first call is the natural example, and the detach
  mutates `self._observers` in the middle of the loop walking it." (comma
  splice, flourish "itself," and "that" without a clear referent).
- Line 275: "conditional on the value actually changing" → "conditional on
  the value changing" (empty adverb; deletion changes nothing).
- Line 354: "which is what calling an `async` function produces" → "which
  calling an `async` function produces" (cleft; the deletion test passes).

Line numbers below refer to the chapter before these edits
(the line-231 fix did not change line counts).

***

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

[] Reject

***

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

[] Reject

***

## Noted, no change

**Line 163 — "amounts to nothing more than a list of callbacks."**
"Nothing more than" is on the watch list, but the global rule's carve-out names
this exact construction: a comparative where the diminishing is the point, and
its example is this sentence. Recorded so a later pass does not cut it.

**Line 174 — "a lambda equals only itself."**
Both watched words are load-bearing here: the claim is identity-equality, and
"a lambda equals itself" without "only" would be trivially true of everything.
Recorded because a mechanical watch-list sweep would flag it, and it should
survive that sweep.
