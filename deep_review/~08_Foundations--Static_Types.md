> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 08_Foundations--Static_Types (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing with `ty` 0.0.84 probes (every `# ty:` summary, every quoted diagnostic run against an edited copy of its listing, `reveal_type()` on each inference the prose states),
against the sections the chapter links in chapters 04, 07, 09, 12, 13, 14, 17, 22, 26, 34, 35, 38, and 45,
against the inbound links from other chapters,
and against docs.python.org and docs.astral.sh for every external anchor.
`tip verify-ch CH=08` passes 24 of 24.

## Applied directly

Chapter, corrections:

- Opening: "Pyright runs over the same listings as a second opinion, outside that gate" pointed at a gate the chapter had not mentioned. Now says the book's build does not depend on Pyright's verdict.
- "Structural Typing with Protocols": the `@runtime_checkable` link went to chapter 26's `#proxy`, the whole *Proxy* section. It now lands on `#what-the-implementation-supplies`, the subsection that introduces the decorator and the one the summary table links.
- "Type Hint Summary": "Each subsection heading links to the associated Python documentation" was stale, since the links moved to the line under each heading. Now "Each subsection opens with a link".
- Summary, Structural Typing: the documentation link's `#protocols` anchor is the list of predefined protocols (`SupportsAbs` and the rest). Retargeted to `#nominal-vs-structural-subtyping`, which explains `Protocol`.
- Summary, Generics: the `[T: Base]`, `[T: (int, str)]` row links `#type-parameters` and the `TypeVar`, `Generic[T]` row links `#paramspec-and-typevar`, the subsections that cover each. Both pointed at the parent heading.
- Summary, `NamedTuple` row: link moved from chapter 22's `#the-standard-library-versions` to its `#namedtuple` subsection.
- "Type Parameter Defaults": "The same applies to a `type` alias" followed the no-default listing, so "the same" read as the unsolved parameter. Now "A `type` alias takes a default the same way".
- `variance.py`: `add_square()` appended a `Shape()`, and the listing had no `Square`. Added `class Square(Shape)` and the function appends one. The prose and Solutions exercise 7 follow.

Chapter, teaching:

- "Type Hints": added the tuple near-miss. `tuple[int]` is a tuple of one `int`, not the analog of `list[int]`, and the summary table's `tuple[A, B]` row cited this section for a form it did not contain.
- "Catching Mistakes": `reveal_type()` appeared in the shorthand paragraph, a listing, an exercise, and the summary with no explanation anywhere in chapters 01-08. One sentence now says what it asks and where the answer shows up.
- "Catching Mistakes": the `# ty:` summary looks like `ty`'s own `# ty: ignore[rule]` directive. A short paragraph separates them and says `# type: ignore` silences every diagnostic on its line while the `ty` form silences one rule.
- "Narrowing": new listing `object_narrowing.py`. The chapter stated the `Any`/`object` difference and the `isinstance()` narrowing in prose only. The listing shows an `object` parameter rejected before the test and accepted after it, and the prose says what `Any` does in its place. Verified both ways with `ty` and at runtime.
- "Narrowing": the stale-attribute paragraph told the reader to recheck after a call. Added the usual fix, a local copy, with a pointer to new exercise 9.
- "Constants with Final": added that the book's listings write the type out on every `Final` (90 typed uses, no bare one outside this listing).
- "Type Parameters": the summary's "constrained" form had no sentence in the chapter. Added one, and changed "A *bound* constrains" to "limits" so the two terms stay apart.
- Exercise 9 added (narrow a local copy of the attribute), with its solution. `tools/data/exercise_refs_baseline.txt` gained the one new reference.

Chapter, prose:

- "Type Parameter Defaults": the paragraph after `type_defaults.py` described the no-default case, then the next paragraph and listing demonstrated it again. The first paragraph now says what the default does, and the `Queue` lead-in is one sentence.
- "A type parameter closes this hole" cut: the next sentence opens the same point.
- "`Drawable` annotates `render()`'s parameter alone" could read as "the parameter, not the return". Now "`Drawable` appears in one place, the annotation on `render()`'s parameter."
- "The crash proves the narrowing was already stale": `expect()` catches the exception, so nothing crashes. Now "The `AttributeError` shows the narrowing was stale".

Solutions:

- Exercise 6: the quoted diagnostic stopped after the first block. Added the `info: Function defined here` block `ty` prints.
- Exercises 1, 2, 3, 4, 5, 6, 7, 8: style-rule fixes in the explanations ("purely", "exactly as", "actually", "plain `Tally`", "plain `str`", "at all", "genuinely", "both spellings", the "promises"/"promise" metaphor in 7, and "Remove the default and `ty` reports" in 5). No claim changed.
- Exercise 7: "That pairing is the whole of variance in one edit" and the two sentences after it restated as what invariance and covariance are.

## Considered and declined

- **Exercise 5 repeats `type_defaults_bare.py`.** The listing shows a bare annotation revealing `Unknown`, and the exercise has the reader produce the same result on `Stack`. The solution adds the `no_such_method()` consequence, and the exercise is the chapter's one hands-on use of `reveal_type()`, so it stays.
- **Three listings on type parameter defaults, a feature no later chapter uses.** The section is heavier than its use in the book. Cutting it is a scope call, and the section is correct as written.
- **Moving "Gradual Typing" after "Type Hints".** The section names `Any`, `Unknown`, and `object` before the reader sees an annotation. It reads as motivation and needs no syntax, and `#gradual-typing` is linked from the summary.
- **`ty`'s variance diagnostic names the fix** ("Consider using the covariant supertype `collections.abc.Sequence`"). Quoting it would tie the section to one release's wording.
- **"where they earn their keep"** in "Gradual Typing" is an idiom, not a mechanism stated as a metaphor. Left.
- **Solutions exercise 3 has no blank line after its header comment.** Fourteen listings in Solutions 02-09 share the shape.
