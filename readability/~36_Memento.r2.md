> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/36_Memento.md` (r2)

The chapter's older prose still holds up: a full vocabulary scan turns up no
Tier 1A or Tier 2 hits, no boldface, no curly quotes, and no spaced ` -- `.
All five findings from the first review are applied and none was rejected.

Everything below was in prose added since that review, either by the deep
review while it was being written or by today's apply.
Every finding cleared the direct-application bar, so this run leaves no
blocks: the fixes are listed for the record, and the `git diff` is the place
to veto any of them.

## Applied directly

- "The caretaker's side of the contract is restraint" paragraph: restored the
  parentheses today's apply had flattened into commas, so "an honest mistake
  (swapping the snapshot's strokes for different ones) fails loudly" reads as
  one subject and verb again. The deep review's correction of *which* mistake
  stays; only the punctuation came back.
- "When either limitation rules out `pickle`, other libraries answer them
  separately." → "...answer drift and security separately." (singular "either
  limitation" left plural "them" with no antecedent; naming the two also
  hands off better to the sentences that pair each library with one).
- Paragraph after `frozen_sketch.py`: "under a different name so the two
  never get confused; its extra `title` field..." → "under a different name
  so a reader never has to ask which one a listing means. Its extra `title`
  field..." (classes do not get confused, readers do; the semicolon joined
  two separate answers to two separate questions).
- Immutability closing paragraph: "The classic form has not disappeared, it
  has narrowed." → two sentences (comma splice; the second clause is the
  paragraph's whole job).
- Paragraph after `ghost_field.py`: "The three prints are the lesson side by
  side." → "Each print contradicts the one before it." (the old sentence
  rated the listing instead of reading it, and miscounted: the listing was
  split into three prints for line length, so "side by side" no longer
  described the layout. The review's primary proposal was to cut the lead-in
  entirely; the replacement keeps one that carries information. Delete the
  sentence if you would rather open on the `repr()` claim.)
