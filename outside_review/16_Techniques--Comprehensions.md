<!-- outside review of Chapters/16_Techniques--Comprehensions.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `16_Techniques--Comprehensions.md` chapter:

**1. List Comprehensions: Components (Terminology)**

* **Target Text:** 
```markdown
-   An input sequence.
-   A variable representing members of the input sequence.
```
* **Issue:** Comprehensions accept any iterable (such as sets, dictionary keys, or generators), not just sequences. Using the term "sequence" artificially limits the concept, as sequences are a specific type of iterable that require integer indexing and a defined length.
* **Instruction:** Change both lines to:
```markdown
-   An input iterable.
-   A variable representing members of the input iterable.
```

**2. List Comprehensions: The map() and filter() Equivalent (Terminology)**

* **Target Text:** "`filter()` applies a predicate to a sequence and retains the members that pass it."
* **Issue:** Just like comprehensions, `filter()` operates on any iterable, not just sequences. Calling it a sequence incorrectly implies it cannot be used with non-sequence iterables like generators or sets.
* **Instruction:** Change to: "`filter()` applies a predicate to an iterable and retains the members that pass it."

**3. Supplying the Input Sequence: zip() (Terminology and Missing Alternative)**

* **Target Text:**
```markdown
`zip()` walks two sequences together, taking one element from each:
```
and
```markdown
`zip()` stops at the end of the shorter sequence. Pass `strict=True` to make a length mismatch raise a `ValueError` instead of silently truncating.
```
* **Issue:** `zip()` works on any iterables, not just sequences. Furthermore, while `strict=True` catches mismatches, readers processing unequal iterables often need to pad the shorter one rather than truncating it, which is a common use case solved by `itertools.zip_longest()`.
* **Instruction:** Change the first text block to: "`zip()` walks two iterables together, taking one element from each:"
Change the second text block to: "`zip()` stops at the end of the shorter iterable. Pass `strict=True` to make a length mismatch raise a `ValueError` instead of silently truncating, or use `itertools.zip_longest()` to pad the shorter iterable with a fill value."

**4. A Generator Expression Runs Once: Re-traversing (Caveat)**

* **Target Text:** "When you must traverse something twice, either materialize it with `list()` or write the generator expression again."
* **Issue:** Writing the generator expression again only works if its underlying source data can be iterated again (like a `list` or a `range`). If the source is an already-exhausted iterator (such as a file stream or network socket), recreating the generator expression will silently yield zero elements.
* **Instruction:** Change to: "When you must traverse something twice, either materialize it with `list()` or, if the underlying data source is re-iterable, write the generator expression again."

## Verdicts

Applied in commit 429f6125, after each item was tested against the chapter and run under `uv run`.

1. Applied. The chapter's own Supplying the Input Sequence section says "Everything to the right of `in` is an ordinary iterable expression", and a set or a generator works there, so the components list's "sequence" named a narrower kind than the construct accepts. Both bullets now say "iterable".
2. Applied. `filter()` takes any iterable, and the sentence defines the built-in in general rather than describing one call, so "sequence" was the same narrowing. It now reads "an iterable".
3. Applied, with a different fix. The two `zip()` sentences now say "iterables", the same correction. The `itertools.zip_longest()` addition stays out: the listing's four names and three values show the truncation that `strict=True` guards, padding is a case the listing never needs, and an alternative API is the shape the review rules rank below a correction.
4. Applied, with a different fix. The caveat is right: a generator expression written again over an exhausted iterator yields nothing. The chapter already states the condition two paragraphs earlier ("a `range` is re-iterable"), so the sentence now says "or, over a re-iterable source such as `range`, write the generator expression again", naming the source the listing uses in place of the reviewer's conditional clause.
