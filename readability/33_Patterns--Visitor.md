> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/33_Patterns--Visitor.md`, 2026-10-16.
The chapter has had straighten, colon, metadiscourse, and continuity passes this month,
and it carries few AI-writing tells.
Two fixes had one sensible answer and are applied below.
This file holds no live block, so it is the applied-directly record.
The declined section lists the watch-list hits examined and kept,
so a later sweep does not raise them again.

## Applied directly

- Line 328, §53 "worth" frame: "The cases worth covering are the registered types," -> "The tests cover the registered types,". The frame rated the cases instead of stating them; checked against `test_visitor.py`, whose three tests cover the registered types and the default (two parametrized tests) and the inherited subclass (`Hybrid`). A "three cases:" lead-in was tried and dropped, since the sentence already ends on the colon that introduces the listing.
- Line 429, and-split rule: "*Visitor* dispatches twice, and `singledispatch` dispatches once." -> two sentences. The subjects differ and "whereas" fits where the "and" sat.

## Considered and declined

- Line 121, §34: "(chrysanthemums really do produce a natural insecticide)". A deliberate aside; "really do" affirms that the toxicity in the listing is a botanical fact, which is the contrast the word carries.
- Line 199, "plain": "turns a plain function into one that dispatches on the type of its first argument". The sentence names the contrast (an ordinary function against a dispatching one), the recurring keep for "plain".
- Line 326, "plain": "Because each operation is a plain function". The contrast is with the visitor methods reached through `accept()` earlier in the chapter, and the word carries the reason a test can call the operation directly. A borderline keep; deleting it leaves "Because" with less to stand on.
- Line 127, §70: "`bug_visits.py`'s output shows results, not mechanism." Binding keep in `readability_db.md`.
- Line 13, §43: "How do you add them from outside the base class?" The question is the chapter's problem statement and its only rhetorical question.
- Line 444, §9: "exists not because two types are unknown, but because the operation must be a method on some class." Both halves are real claims, and the next paragraph builds on the contrast with *Multiple Dispatching*.
- Line 456, "itself": "*Multiple Dispatching* is the end in itself." The fixed idiom "an end in itself", paired with "the means" in the sentence before it.
- Line 253, positive statement: "Nothing edits `Flower`." The negation is the claim: `singledispatch` adds operations with no edit to the hierarchy.
- Line 187, "So" opener two sentences after a "therefore": a consequence summing up the paragraph, and the only adjacent pair of connectives in the chapter.
