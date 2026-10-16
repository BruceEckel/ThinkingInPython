> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Context Managers

The 2026-10-16 readability sweep found this chapter close to clean:
no Tier 1A vocabulary, no chatbot artifacts, and no clusters of tells.
Six small fixes are applied directly below.
The file holds no live block, so it is the record of those edits and of the declined findings.
`tip verify-ch CH=15` passed after the edits.

## Applied directly

- Line 182, empty adverb: "because `__enter__()` just runs again" -> "because `__enter__()` runs again".
- Lines 975-976, tangled logic ("removes ... for good, until a borrower waits forever"): split into "Each missed return removes an object from the pool for good." and "Enough missed returns empty the pool, so the next borrower waits forever."
- Line 1068, §34 real/actual inflation with no named contrast: "puts the pool under real contention" -> "puts the pool under contention".
- Line 1163, pointer with no antecedent (the refinements before it are not mistakes, so "the opposite mistake" points at nothing): "The opposite mistake is on the borrower's side." -> "The borrower's side has a mistake of its own."
- Line 1216, stand-in noun: "the shortest thing that can express" -> "the shortest form that can express", the paragraph's own noun.
- Lines 1223-1224, "and" joining two claims with different subjects: split into "the borrower's side contains two lines." and "Every change you make later goes inside the manager."

## Considered and declined

- Line 76, "for what is really a spent manager": §34, but the sentence names the contrast (the missing `args` attribute the message blames), the recurring keep in `readability_db.md`.
- Line 113, "The generator silently skips the cleanup on the one path where it matters most.": a mild punchline by shape (§31), but it states the consequence of the listing (cleanup lost on the exception path) and sits alone among long sentences.
- Line 118, "What does `with` call?": the chapter's one rhetorical question, and the section answers it; recurring keep.
- Line 284, "One of the most common context-manager bugs": an unsupported superlative by shape, covered by the 11/21/27 superlative precedent in `readability_db.md`.
- Line 972, "Lending is the dangerous half.": a short beat among long sentences, not a staccato run.
- Line 1059, "the way a real database connection pool does": the contrast with the book's skeleton pool is the point.
- Line 1191, "that `second` now legitimately holds": the contrast with `stale` is in the sentence.
