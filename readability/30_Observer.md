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

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

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
- Lines 72-76: the `changed`-flag paragraph split after "nothing here needs
  it," so what the flag buys and why the clearing line sits where it does
  read as the two thoughts they are. No wording changed; the
  clearing-order sentence stays because it explains a line that would
  otherwise look arbitrary.

Line numbers above refer to the chapter before these edits.

## Considered and declined

**Line 86 — "It is simply a callable."**
"Simply" is an empty adverb by the deletion test, but the sentence is the
deflating beat in the two-sentence pair doing the chapter's central move,
and the word carries that spoken rhythm. Left alone; recorded so a later
sweep does not re-raise it.

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
