> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 03_Foundations--Containers (Solutions)

The solutions carry no AI-writing tells: no vocabulary clusters, no curly quotes or spaced `--`, no metadiscourse, and each claim checked against its listing's `#:` output.
Six small sentence-level fixes were applied directly.
This file holds no live block, so it is the record of the applied changes and of what was examined and left alone.

## Applied directly

- Lines 115-116 (exercise 2), §70 treadmill: the after-listing sentence repeated "`defaultdict(int)` supplies `0`" from the paragraph above the listing. "`defaultdict(int)` supplies `0` the first time the loop reads a key, because `int()` returns `0`." -> "The `0` that `defaultdict(int)` supplies for a missing key comes from `int()`, which returns `0` when called with no arguments." (The hint already says the factory is called with no arguments.)
- Lines 187-188 (exercise 4), two "because" sentences back to back: "Because its contents stay the same after creation, its hash stays valid." -> "Its contents stay the same after creation, so its hash stays valid."
- Line 257 (exercise 6), "and" standing for a consequence: "ranks the lowest counts first, and the slice prints" -> "..., so the slice prints". Checked: after the `counts["dog"]` read, an ascending stable sort starts `('dog', 0), ('sat', 1)`.
- Lines 331-332 (exercise 7), "and" joining two claims with different subjects: "Line `[1]` reads fields by name, and `person.height` names ..." -> two sentences.
- Line 417 (exercise 9), hand-wrap defect: three sentences jammed on one 170-column source line, rewrapped one per line to match the paragraph. No wording change.
- Line 528 (exercise 10), §31 trailing flourish: "any equal configuration reaches the same entry, whoever built it and whenever." -> "any equal configuration reaches the same entry." The paragraph already says `config` and `same` are built separately, in different orders.

## Considered and declined

- Lines 17 and 70-72, "the cost of operations", "the whole loop costs O(n²)": commerce words, but they name a measured quantity (time, complexity), which R2 keeps.
- Lines 69-70, "holds at ... But the margin grows with `n`": the "But" answers the exercise's "what changes about the comparison", so kept.
- Lines 75-76, "so the list falls further behind the `deque` as `n` grows" restates "the margin grows with `n`", but it closes the explanation by naming the quadratic term as the cause.
- Lines 278-291, 373-386, 444-455, 519-535, bold step labels opening paragraphs (§16 by shape): the Solutions convention for walking a solution's steps (`CLAUDE.md` names "a bold step label"), so kept.
- Line 288, "The rest is what `Counter` supplies after the tally": "is what" with a clause complement, the recorded keep.
- Lines 450-451, "states an exact count, two, and `row` holds five": an "and" between different subjects, but both clauses sit inside one `because` reason and together make it; a period would cut the reason in half.
- Line 460, "Only an empty list has too few items.": sentence-initial "Only", a shape ruled fine on 2026-10-04.
- Line 460, "The star turns a fixed-shape assertion into a flexible one.": restates "states a minimum instead" by shape, but the next sentence's "The same flexibility" depends on it.
- Lines 530-531 and 537, "and" between different subjects ("the type checker rejects the assignment too", "hashing a `list` raises a `TypeError`"): additive in the first (the "too") and two steps of one chain in the second, so kept.
- Mixed wrapping: several hand-wrapped paragraphs carry one or two lines past 70 columns (73, 101, 117-118, 211-215, 377-392, 523-541). Rewrapping prose that no other finding touched would be diff churn with no rendered change, so only line 417, which jammed three sentences together, was rewrapped.
