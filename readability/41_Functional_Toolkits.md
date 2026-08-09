> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/41_Functional_Toolkits.md`

Second review of this chapter.
All seven findings in `readability/~41_Functional_Toolkits.md` were accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one changed the chapter substantially:
Recursion and Lazy Evaluation swapped places, a `### Composing the Pieces`
subsection closes the `itertools` catalog, the case study gained a named
`met()` helper and a paragraph on why caching it would be wrong, and the chapter
gained both a `## Choosing From the Toolkits` conclusion and its first
`## Exercises` set. Every finding was in that new prose.

One problem was corrected during the apply rather than recorded here, because it
breaks a stated rule rather than a judgment call: the new `singledispatch`
sentence ended "a keyword-only argument cannot be dispatched on at all," a
stranded preposition, and now reads "cannot drive the dispatch at all" with the
sentence's subject changed from a passive to `singledispatch()`.

Every finding cleared the direct-application bar, so this run leaves no
blocks: the fixes are listed for the record, and the `git diff` is the place
to veto any of them.

## Applied directly

- "Composing the Pieces" opening: "This section opened by saying they
  combine, and combining them is where the catalog pays off:" → "Stacked,
  they are a pipeline:" (§41 restated what the reader was told, and put
  "combine"/"combining" in adjacent clauses; the intro's promise is redeemed
  by the listing, not by announcing the redemption).
- Same section: "The second `print()` is the one that teaches. The source
  resumes at 16..." → "The second `print()` shows the source resuming at
  16..." (§39: the label announced importance instead of delivering it; the
  pointer to which `print()` is meant survives).
- Same section, closing line: "A pull-based pipeline reads one item further
  than it keeps." → "reads one value further than it keeps, and that one
  value cost three squares." (the sentence above counts in batches and
  squares, where the overshoot is three; naming both units connects the rule
  to the numbers the reader just saw).
- `repeat`: "it supplies an argument that never changes without materializing
  anything" → "that never changes, without building a list to hold it" (the
  missing comma let "without materializing" attach to "changes"; the concrete
  phrase replaces a word the book has not introduced in this sense).
- Case study: cut "this is the shape the mistake takes in practice" (three
  closing sentences asserted the same thing at different altitudes; the kept
  neighbor, "however simple its body looks," is the part a reader can carry
  to their own code).

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- "The infinite form is the one that earns the import" echoes the chapter's own
  "`reduce()` earns its keep for every other fold," so it reads as the book's
  voice rather than a new metaphor. Not flagged.
- "Choosing From the Toolkits" opens "The rule for both modules is the same,"
  then "The second rule is that the pieces are meant to be stacked." Numbered
  rules in a conclusion are §54 by shape, but there are two of them and both
  are load-carrying, so the count is not inflation. Not flagged.
- The new exercises are imperatives addressed to the reader, which the global
  rules exempt from the imperative-plus-consequence ban.
- The `met()` helper's name was checked against the surrounding code for
  soft-keyword collisions and shadowing; it collides with nothing.
