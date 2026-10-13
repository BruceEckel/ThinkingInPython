> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 08_Foundations--Static_Types (2026-10-13)

No live blocks: nothing here needs your decision.
I checked every claim against its listing under `uv run` (Python 3.15.0, `ty` 0.0.86, Pyright 1.1.414):
the `ty` 0.0.86 misspelled-keyword claim and Pyright's `No parameter named "fil"`,
the `invalid-argument-type` and `missing-argument` diagnostics in the `TypedDict` section,
`CACHE: Final = []` revealing `list[Unknown]`, the bare `BareStack` revealing `Unknown`,
`text` revealing `None` after the `if` in `narrowing.py`,
the `class Table[K = str, V]` syntax error, `reveal_type()` and `assert_never()` at runtime,
and each quoted diagnostic in the Solutions file.
I also ran every extracted listing and solution directly against its `#:` markers,
read the 15 sections the chapter links in other chapters for what the chapter says they contain,
and confirmed by grep that no other listing writes a bare `Final` or annotates with `bytes` or `complex`.
`tip verify-ch CH=08 ISOLATED=1` passed 27 of 27 before the edits
and 27 of 27 after.

## Applied directly

Chapter, prose:

- "Gradual Typing": the `Any`/`object` paragraph said the same thing twice ("guarantees nothing about the value" and "a checked value with the methods every class shares"). It now says it once: an `object` value carries the methods every class shares, and the checker rejects everything beyond them.
- "Narrowing": "An `object` parameter depends on narrowing" read oddly. Now "Narrowing also makes an `object` parameter usable."
- "Narrowing": "the type checker has no way to see inside that call" is inaccurate, since `ty` can read `reset()`'s body. Now "assumes the call leaves the attribute as it was", which matches the mechanism the next paragraph describes.
- "Constants with Final": the misconception sentence came after the point it introduces and restated it. The paragraph now opens with the misconception.
- "Structural Typing with Protocols": "A *Protocol* expresses shape" and "A `Protocol` instead describes a required shape" were the same sentence twice. Cut the first and moved the italic term to the second.
- "Structural Typing with Protocols": the `isinstance()` paragraph interrupted the walk through `protocols.py` between the `Circle`/`Square` paragraph and the `Blob` paragraph. Moved it to the end of the section.
- "The `Self` Return Type": "A `@classmethod` that ends with `return cls(...)` returns `Self`" mixed the runtime return with the annotation. Now it "declares `-> Self`, so a call on a subclass has the subclass's type, not the base's."
- "How Much to Annotate": "The value of a hint ... a value's creation" used "value" in two senses in one sentence. Now "A hint helps in proportion to the distance between a value's creation and its use."
- Summary, `object` row: "with no behavior assumed" contradicted the prose (an `object` has `object`'s methods). Now "with the methods every class shares and no others".
- Summary, `frozenset[T]` row: "because nothing can be written into it" (passive, negative) is now "because it has no method that adds an element".

Chapter, teaching:

- "Structural Typing with Protocols": the "weaker check" link now says what is weaker: `isinstance()` confirms that each method exists and ignores its signature (chapter 26's own caveat).
- "Constants with Final": added the near-miss fix. A reader who wants a constant collection learns to hold a tuple or `frozenset` under the `Final` name, with a pointer to new exercise 10.
- "`**P` and the Older `TypeVar` Syntax": the heading promised the older syntax, but the section gave it one sentence and no example, so a reader could not recognize it in older code. Added an unextracted snippet of `first()` and `Box` written with `TypeVar` and `Generic[T]`, and one sentence on what the bracket form changes. I checked the snippet under `ty` (it reveals `int` and `Box[str]`). It is a bare fence, not a `# slug.py` listing, because `UP` is selected in ruff and a listing would invite a per-file ignore for code shown only to be recognized.
- Exercise 10 added: put a `Final` tuple in place of the list, read the `unresolved-attribute`, and explain why the entry goes in at the definition. Until now the `Final` section had no exercise, and it is the chapter's main misconception.

Solutions:

- Exercise 10 written: a near-miss paragraph (`append()` draws `unresolved-attribute`, and `HISTORY = HISTORY + (...)` runs but is rejected as a `Final` reassignment, both probed under `ty` 0.0.86), the listing, and a short discussion. `tip statements` and `tip steps` generated the quote and the ladder. The ladder has no "shape" step, since the listing declares constants alone.

## Considered and declined

- **No exercise for `typed_kwargs.py`.** The section's sharpest case is the misspelled keyword that `ty` 0.0.86 accepts and Pyright rejects. An exercise built on it would go stale when `ty` closes the gap.
- **`narrowing_attribute.py`'s comment "ty can't see this clears val".** It is loose for the same reason the prose sentence was, but it is a three-word listing comment and the prose beside it now states the mechanism.
- **`# ty:` summaries paraphrase the diagnostic** (`cannot assign to final name "MAX_RETRIES"`, where `ty` prints "Reassignment of `Final` symbol ... is not allowed"). The chapter defines the summary as a summary, and the full-quote gate covers the verbatim quotes.
- **Bounds and constraints have no listing.** The summary table cites the two sentences, the 2026-10-08 outside review probed both forms, and the book uses neither form often enough to support a listing.
- Carried forward from `~08_Foundations--Static_Types.md`: exercise 5 repeating `type_defaults_bare.py`, the three type-parameter-default listings, the position of "Gradual Typing", quoting `ty`'s variance hint, "earn their keep", and the missing blank line after `area.py`'s header (exempt in `deep_review_db.md`).

## For the session

- The new reference at `Chapters/08_Foundations--Static_Types.md:286`, "(see exercise 10)", pairs with "10. A `Final` tuple", which is correct. Its baseline entry went into commit 183959fc (the Tour review commit), so `exercise-refs` already passes; that commit carries a line belonging to this chapter.
- The isolated `verify-ch` sync wrote a new generated file, `Solutions/08_Foundations--Static_Types/exercise_10.py`, which needs to be committed with the README.
