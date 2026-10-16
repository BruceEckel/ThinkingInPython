> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/08_Foundations--Static_Types.md`, 2026-10-16.
The chapter carries few AI-writing tells after its earlier passes, so this run found nothing that needs Bruce's judgment and the file holds no live block.
It is the record of seven direct edits, mostly "and" joins between clauses with different subjects, plus the declines a later sweep would otherwise re-find.
`tip reflow CH=08` and `tip verify-ch CH=08 ISOLATED=1` pass (27 of 27).

## Applied directly

- Line 10: different-subject "and" split. "few type declarations, and on a small program you may not miss them" -> two sentences.
- Line 217: different-subject "and" split (the clauses contrast, "but" fits). "checks too, and `describe(42)` then fails" -> two sentences.
- Line 254: §35, a narrowing that "becomes false". "becomes false when a call rebinds the attribute" -> "holds until a call rebinds the attribute", which also echoes "A narrowing on a local variable holds" in the line above.
- Line 557: different-subject "and" split, each clause a claim of its own. "accepts `Shape` and its subclasses, and `T` keeps the subclass" -> two sentences, matching the constraint sentences that follow.
- Line 638: different-subject "and" whose second clause restated the first. "`reveal_type()` shows that inferred type, and the type checker reports `str`" -> "At the `reveal_type()` call, the type checker reports that inferred type, `str`." Checked against `type_defaults.py` (`reveal_type(words.top())  # ty: str`).
- Line 641: different-subject "and" (the relation is "while"). "omit the brackets, and the annotation stays precise" -> "omit the brackets and still get a precise annotation", one subject throughout.
- Line 958: different-subject "and" carrying a consequence. "exist for the type checker and the reader, and at runtime most of them do nothing" -> two sentences, so "Two act when a call reaches them" contrasts with a sentence of its own.

## Considered and declined

- Lines 315-317, the two sentences after "the same idea checked at different moments" (§70 restatement by shape): standing rejection in `readability_db.md`, confirmed again on the 2026-10-04 Sweep Decisions page. Kept.
- Line 459 "even though `"purple"` is a valid `str`" and line 992 (exercise 8) "even though the type checker accepts either version": watch-list "even", both judged keeps in `tools/data/watch_words_baseline.txt`. The conjunction carries the concession.
- Lines 9, 16, 265, 267, 443, 689, 800, the "only"s: each is one of the shapes ruled fine on 2026-10-04 (only when, only a, sentence-initial Only, the only X, only in), and five are baseline keeps.
- Line 15 "The Python runtime never acts on a type hint": a guarantee, baseline keep.
- Lines 18 and 152, "want" addressed to the reader: the carve-out.
- Line 381 "A plain `SomeType` annotation": "plain" contrasts with `type[SomeType]` in the next sentence.
- Lines 805 and 818, "worth the words" and "worth annotating precisely": §53 by shape, but the frame weighs the hint's length against the distance a value travels, which the paragraph states.
- Lines 39-40, "the public interfaces, the tricky data, the code on which other people depend" (§10): an inventory that line 806 then makes concrete, not padding.
- Line 567 "that surprises most people the first time": an unsupported generalization by shape, kept as voice that motivates the `variance.py` listing.
- Line 694 "What should the type hint be?": a rhetorical question that names the problem the section solves (recurring keep).
- Lines 366-367, "A protocol accepts any class with the right methods, as dynamic typing does, and reports a mismatch before the program runs": restates lines 315-317, but here it closes the `protocols.py` walkthrough with the protocol as subject, so it stays alongside the standing rejection.
- Line 247, "The `if` narrows `b.val` to `str`, and the checker keeps that narrowing": two subjects, but the clauses are steps of one sequence, so the additive "and" is right.
- Line 862, "`Iterator[T]` is enough when it only produces values": the "only" sits beside the phrase it restricts, and the positive alternatives name send and return types the table cell already lists.
