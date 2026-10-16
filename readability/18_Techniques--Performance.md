> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 18_Techniques--Performance

This chapter carried few AI-writing tells.
Three fixes had one sensible answer and are applied below.
The file holds no live block, so it is the record of the applied changes and of the findings judged and kept.
`readability_db.md` was read first, and no prior `readability/~18_*` review exists.

## Applied directly

- Line 617, §58 list-label period: "- String concatenation. `"".join(parts)` is faster..." -> "- For string concatenation, `"".join(parts)` is faster...".
  The other two bullets in that list are full sentences with no label, so the first one now matches them.
- Line 1470, §53 endorsement frame: "The saving shows up at a size worth measuring:" -> "The saving shows up clearly in a million-byte buffer:".
  The size comes from `memory_view_size.py`'s `bytearray(1_000_000)`.
- Line 1840, forward pointer: "and the rest of this list depends on that answer." -> "and which strategy fits depends on that answer."
  The list does not appear until twelve lines later, and the paragraph's next sentence already says "The list below".

## Considered and declined

- Line 11, "Python addresses the first issue with clear syntax and extensive power and flexibility."
  Vague praise by the portability test, but it is the chapter's first-edition opening, and the sentence that follows answers it.
- Line 434, "Later releases have continued that work."
  Short, and it states a fact (the speedups did not stop at 3.11) rather than padding.
- Lines 1548-1549 and 1603-1604, "The 3x threshold sits far below any multiple you should see." appears twice, verbatim, in the NumPy and Numba sections, and line 1666 varies it.
  The two sections are parallel by design, like the book's prose decision tables, so the repetition helps a reader comparing them.
- Line 1813, "The question is not the object count on its own but the work done per object crossed."
  §9 by shape, but both halves are named, and the sentence generalizes the `collatz_lengths()` case into the rule a reader takes away.
- Line 1828, "Sometimes the fix is not a faster function but a different architecture."
  §9 by shape; the contrast is real and introduces the section's one point.
- Lines 1868-1869, "The goal is not the fastest possible program. It is a program that is fast enough..."
  §9 by shape, but "fastest possible" against "fast enough" is the chapter's thesis, and the negative half names it.
- Line 1102, "Multiply by a population in the millions to see why it matters."
  An instruction to the reader, which the global rules leave imperative.
- "cost" at lines 310, 932-935, 951, 1400, and 1812 measures time or memory, the R2 carve-out.
- "real" at lines 1427 ("a real protocol parser") and 1811 ("real work") each name the contrast in the same sentence (a demo buffer; the conversion overhead).
