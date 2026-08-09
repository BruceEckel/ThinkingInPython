> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/47_Stateless_in_Practice.md`

Second review of this chapter.
The findings in `readability/~47_Stateless_in_Practice.md` were all accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one cut the
`Why retry() Decorates the Function` subsection, retitled two headings, added a
motivation sentence to "Abilities Are Not Special", tightened the type-bound
paragraph, added three explanatory sentences and a closing paragraph, and added
three exercises. Every finding was in that new or rewritten prose.

Every finding was resolved directly and applied (listed below).
No blocks remain.

## Applied directly

- Closing paragraph: "Name each contact with the outside, the clock, the
  feed, the pool, the console, and bind it at the edge..." → the example
  list moved into parentheses, so the resumption at "and bind it" no longer
  reads as a fifth list item. (The deep review's draft used em dashes here,
  which are yours to write rather than mine; parentheses do the same
  structural work.)
- "Abilities Are Not Special" opening: added "A custom Ability is a request
  you design." ahead of the `Need` contrast, so the section's first sentence
  states its own topic instead of comparing to the previous chapter.
- "Switching Implementations Mid-Run": "`catch()` matches yielded values,
  and a handler yields nothing" → "`catch()` matches values an Effect
  yields, and a handler is not part of the Effect" (kills the yield-yield-
  yield tongue-twister and states the real reason, which now agrees with
  "A handler sits outside the channel it feeds" in the next sentence).
- "The Success Path": cut "Lifting a function takes it away from its
  unlifted callers." and added "directly" to the sentence before it (the
  aphorism overstated: an unlifted caller can still `run()` a lifted
  function, as the chapter shows a dozen times).
- Final section retitled: "One Type for Four Mechanisms" → "What Survives
  the Library" (the section opens on adoption advice, then a habit
  paragraph, then the four-mechanisms argument in the middle, so the old
  heading named an argument the section makes third rather than first. The
  new title covers the habit paragraph, which is the section's most useful
  content and sets up the adoption advice as the question it answers, and
  still fits the closing line about capacity. The deep review's alternative,
  moving the composition paragraph to the section's top, would reorder the
  book's last section for a smaller gain, so the retitle was the cheaper
  correct fix. `heading_links.py` confirms nothing links to the old
  anchor.)

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter. The deep
  review's draft closing paragraph contained "reaching for", which was replaced
  with "calling it in the middle" before it was applied.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- `### 4. The discipline is all-or-nothing` now matches its four siblings, which
  all state a limit as a sentence. Scanning the five headings works again.
- The new intro line ("The chapter then collects every tool in one table and
  weighs what the whole approach costs") was checked against both sections it
  announces. Both exist and both do what it says.
- The two-sentence replacement for the cut `Why retry() Decorates the Function`
  subsection was checked against chapter 46's `An Effect Runs Once`, which now
  carries the explanation. The claim is not repeated, only cited, which is what
  the cut was for.
- The three new exercises were checked against their solutions. Exercise 12's
  two annotation-deletion questions have different answers (one silently
  weakens caller checking, one raises at decoration time), which is what makes
  the pairing worth asking.
