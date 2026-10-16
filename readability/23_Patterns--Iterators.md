> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/23_Patterns--Iterators.md` (2026-10-16).
The chapter carries few AI-writing tells: no Tier 1A or Tier 2 vocabulary,
no boldface, no signposting openers, no generic conclusion.
Two small edits went in directly.
This file holds no live block, so it is the applied-directly record,
plus the findings considered and kept.
No earlier `~` review of this chapter exists; `readability_db.md` was read
and nothing below re-raises an entry in it.

## Applied directly

- Line 140, empty adverb: "so it works equally well on the generator, the list, and the custom `Countdown`" -> "so it works on the generator, the list, and the custom `Countdown`". (Line 312's "equally well" stays: there it is the claim, that the annotation describes a list and a half-spent generator alike.)
- Line 855, two sentence-opening "That"s in a row with different referents: "That leaves `advance()` to return the value it reached." -> "With those two gone, `advance()` returns the value it reached." The following "That method is `__next__()`." now has one candidate.

## Considered and declined

- Lines 555-561, §70 restatement. "On infinite data of that kind, `takewhile()` finishes. The `if` clause runs forever." repeats what lines 555-557 say. Kept: the pair returns to the infinite case after the finite sentence shows the two forms agreeing, and that contrast is the paragraph's point.
- Line 983 (exercise 7), commerce word R2: "What has `first()` cost you on an infinite source?" Kept: the cost is a measured quantity, the memory `len(stream.seen)` reports, which R2 carves out; and exercise imperatives and questions are exempt from rewording for style.
- Line 290, `only` before a code span: "Only `produce()` waits." Sentence-initial "Only" is a ruled-fine shape (2026-10-04), and the restriction is the claim.
- Lines 343 and 354, both say `Collection` requires `__len__()` and `__contains__()`. Kept: the second use applies the requirement to `Countdown`, a different subject, and the reader needs it restated there to see why a reiterable class fails.
- Lines 614-615, "real program" (§34). The sentence names its contrast, the test that fails at 1,000 values.
- Line 253, "a plain function". "Plain" contrasts with the generator function `lazy_squares()` beside it (recurring keep).
- Line 619, "whether an iterator ever ends". The "ever" states the undecidability claim (recurring keep for absolutes).
- Lines 943-947, the closing section's "The only way ... The only way ..." anaphora and its "reports nothing" repeated in the next sentence. Deliberate parallelism; the section adds the chapter's synthesis rather than restating it, so §25 does not apply.
- Line 949, "Each tool in this chapter that answers in advance holds a buffer: `tee()`, `OverStream`, and a peekable wrapper." The peekable wrapper is built only in exercise 8, though line 890 names it in the body. Kept: naming exercise 8 here would add an exercise reference the gate's baseline does not hold, for a small gain.
