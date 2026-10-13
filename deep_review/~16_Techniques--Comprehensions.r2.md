> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 16_Techniques--Comprehensions (2026-10-13)

No live blocks: everything I found had one sensible answer, so it is in the chapter or the Solutions file.
I reread both files against `~16_Techniques--Comprehensions.md` and `deep_review_db.md`, and re-probed every claim on the pinned interpreter (`uv run python`, 3.15.0) and `ty` 0.0.86.
Runtime probes confirmed the three walrus `SyntaxError`s and their messages, `[x for x in xs if a else b]` as a `SyntaxError`, the unparenthesized two-argument `sum()`, the class-body `NameError` and the `range(base)` exception to it, the parenthesized `path_walk_comprehension.py` printing nothing, the shallow PEP 798 splice, and the `[[0] * 3] * 3` aliasing.
`ty` 0.0.86 reveals `filter[int | str]` for the `lambda` predicate, `list[int | str]` for a `bool` predicate, `list[int]` for `TypeIs[int]`, `TypeGuard[int]`, and `filter(None, ...)`, and reports the two Solutions diagnostics as quoted (`unresolved-attribute`, `invalid-return-type`).
Pyright 1.1.414 still reveals `list[Unknown]` for `a_list`.
`tip verify-ch CH=16 ISOLATED=1` passed 27 of 27 before the edits and 26 of 27 after; the one failure is the new "exercise 9" reference, which is correct and waits for `tip exercise-refs-accept`.
`tip prose CH=16` is clean apart from three stale baseline entries the edits retired.

## Applied directly

Chapter, corrections and wording:

- Bullets after the figure: "The iterator walks through each member" named no part of the comprehension; the figure labels that clause by its pieces, so it is now "The `for` clause walks through".
- "The `map()` and `filter()` Equivalent": "funnels every element through `lambda` calls" became "passes" (a figure for a call).
- "Scope and the Walrus Operator": "The walrus operator escapes the comprehension's scope" is now the literal statement, that inside a comprehension the walrus binds its name in the enclosing scope, with a link to chapter 4's "The Walrus Operator", where the operator is taught.
- Same section: the paragraph held the deliberate leak and the three `SyntaxError` restrictions; split at that seam.
- "Supplying the Input Sequence": the paragraph explained a generator expression's lazy pull from `sorted()` four sections before the chapter teaches generator expressions. It keeps the hook (parentheses print nothing and raise no exception) and points to "The Gap Between Creation and Consumption", which now carries the mechanism: `sorted()` runs after the directory is deleted, `Path.walk()` ignores the scan error without `on_error`, and the generator produces no paths.
- Same section: the `py_paths` paragraph held the flattening and the filter's design reason; split.
- Same section: "not just the files at the bottom of it" misdescribed `walk()`, whose filenames come from every level; now "not just a list of the files in it".
- "The Gap Between Creation and Consumption": the closing paragraph held the `path_walk` case, the `lambda` late-binding parallel, and the further-reading links; now three paragraphs. "for the same reason" became "by the same mechanism", stated in one sentence with its contrast.
- "Unpacking in Comprehensions": "splicing only the outer iterable" read as if the outer iterable itself were spliced; now "splicing each `row` one level deep". The paragraph after the listing held three topics (the flat list, `**` and the braces rule, the generator and async forms); split into three.
- Exercise 1: "only `str` has `isdigit()`" made the reader compute the excluded types; now "`isdigit()` is a `str` method, and `a_list` also holds integers". `tip statements` copied the change into the Solutions quote.

Chapter, teaching:

- "Nested Comprehensions": added the near-miss a reader writes for a matrix, `[[0] * SIZE] * SIZE`, which repeats one row object so a diagonal assignment lands in every row, with a link to chapter 3's "Two List Traps". The inner comprehension building a new row per `row` is the reason the listing works.
- Exercise 9, on `walrus_filter.py`: count `cube_if_even()`'s calls with and without the walrus. The section's claim (two calls for every element that passes) had no exercise, and the walrus section had none at all. Added at the end so no number moves; the section points to it with "(see exercise 9)".

Solutions:

- Exercise 9's solution, `exercise_9.py`, with a `Hint:` paragraph for the ladder. Its markers show 6 calls, 9 calls, and the call order `[0, 0, 1, 2, 2, 3, 4, 4, 5]`, checked by the gate.
- Exercise 3: "The filter tests the original name, not the upper-cased key, so the filter judges a name before the output expression runs" put the consequence before its cause; now "The filter runs before the output expression, so it tests the original name".
- Exercise 2: "Only the literal ... changes" became "The literal ... is the one change", and "Two nested loops" became "Two nested comprehensions", which is what the listing has.
- Exercises 1 through 8 otherwise do what their exercises ask, and their claims match their listings and `ty` 0.0.86.

## Considered and declined

- "the throwaway list costs time and memory" in "Set Comprehensions": the commerce rule keeps a measured quantity, and time and memory are what the extra list takes.
- The "None of these builds" paragraph after `genexp_consumers.py` holds the consumers and the `str.join()` exception. The two halves are a contrast, which the paragraph rule keeps together.
- A listing for the `[[0] * SIZE] * SIZE` trap: chapter 3's `list_traps.py` already runs it, and the sentence links there.
- "especially if you consume the result only once" in "Generator Expressions": the `only` carries the contrast with consuming it several times, which the next section takes up.
- Earlier declines stand: `flatten_wrong_order.py` keeps its `try`/`except`, the existing comments in `path_walk_comprehension.py` and `unpacking_comprehensions.py` stay, and "Choosing a Form" keeps its verbless closing list.

## For the session

- `tip exercise-refs` reports one NEW pair, `Chapters/16_Techniques--Comprehensions.md:200` "(see exercise 9)" -> "9. Counting the calls the walrus saves". The sentence is right (it follows the double-call claim in `walrus_filter.py`'s paragraph); run `tip exercise-refs-accept`.
- The watch-words baseline has three stale entries for chapter 16 and its Solutions file (`only CODE has CODE`, `splicing only the outer iterable`, `Only the literal in the conditional expression changes`), retired by these edits.
- No error found in another chapter.
