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

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

## Applied directly

- Line 222: "A tuple works as a key just as easily as a single object." →
  "A tuple works as a key, the same as a single object." (the comparison was
  about ease where the claim is that it works; the review's own proposal used
  "exactly," which the watch list avoids, so this wording keeps the contrast
  without it).
- Line 231: "so it is worth watching happen" → "This listing shows it
  refusing a subclass." (§53 endorsement frame; the clause rated the
  demonstration instead of introducing it).
- Line 280: "so the first dispatch never happens, and that is the version a
  reader writes first." → "so the first dispatch never happens. That mistake
  is easy to make and hard to see." (two consecutive paragraphs claimed to
  name what a reader writes first and named different things; the phrase now
  belongs only to the `isinstance()`-ladder paragraph that earns it).
- Lines 296-299: the "table cell can hold a function" rebuttal moved to the
  front of the double-dispatch criterion, so it corrects the old size claim
  before the criterion is stated instead of rebutting a question nobody
  raised after it.
- Line 303: "and it answers the `Number + Number` question" → "which answers
  the `Number + Number` question" (the pronoun's nearest antecedent was
  wrong; "already" stays, since it carries the you-get-this-without-building-
  it contrast).
- Line 393: "describes nothing at all" → "describes nothing" (watched "at
  all"; the second half of the sentence already states the consequence).

- Line 11: "The answer starts with something you probably never consider."
  → "The answer starts with a fact about the language that rarely comes
  up." (§68 faux-insight setup told the reader they had not thought about
  it; the fix keeps the bridge from the opening question rather than
  cutting the line, since the sentence carries over from *Thinking in
  Java* and the bridge is doing work).

Line numbers above refer to the chapter before these edits
(none of the edits changed line counts).

***

## Noted, no change

**Line 316 — "a type written decades after `int` was."**
This is the sentence that makes reflected operators matter, and the elision at
the end ("after `int` was") is the kind of thing a person writes and a model
does not. Recorded so a later tightening pass leaves it alone.
