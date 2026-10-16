> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: Error Handling

This chapter has been through several deep reviews and prose passes, and it reads clean:
no curly quotes, no spaced ` -- `, no Tier 1A vocabulary, no signposting or endorsement frames,
and every watch-list hit is a keep under `readability_db.md`.
One redundancy was applied directly.
The file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 253, §70 restatement: "The listing shows each limit once, one on the author's side and one on the caller's side:" -> "The listing shows both limits:". The two paragraphs above already name the author's side and the caller's side. The close alternative, "both limits, the caller's first", strands a possessive.

## Considered and declined

- Line 70, "so only the value's runtime type says which side you received": the "only the X" shape is one of the six ruled fine (2026-10-04), and the restriction is the claim.
- Line 202, "The only way to the answer is narrowing": "the only X" shape, ruled fine; the restriction is the point of the paragraph.
- Line 281, "Real programs chain steps." §34 by shape, but the contrast is with the single-call demos above it, and the sentence is a short beat among long ones.
- Lines 429, 439, 442, "plain value", "plain function": each contrasts with a `Result`-returning or wrapped value, the named-alternative keep.
- Lines 776 and 824, "never receives", "never sees a field name": each `never` is the claim (the locals the raising frame cannot see; the loop that still reports the field).
- Line 854, "truly exceptional conditions": §34, but the next paragraph names the contrast ("Those are not exceptional. They are routine").
- Lines 388-392, the `e`-deletion sentence contrasted with `sum_type.py`: the pairing asks the reader to connect a deleted exception object with a list of kept results, but the point (an error as a value persists, an exception object does not) is recoverable, and a rewrite would change what the sentence claims.
- Lines 828-830, "The note applies the chapter's opening argument to the exception inside the `Err`": §70 by shape, but the sentence links the section back to the chapter's thesis and the following sentence delivers the content.
- Lines 865-868, the closing recap: §25 by shape, but each sentence is concrete (three chained functions, no `try`, the type checker's role) and the paragraph hands off to two named chapters.
- Lines 293, 404, 460, colons that end a full claim and introduce a listing: the book's listing-introduction convention.
