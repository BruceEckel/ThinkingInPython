<!-- outside review of Chapters/16_Techniques--Comprehensions.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `16_Techniques--Comprehensions.md` chapter:

**1. Section: Unpacking in Comprehensions (misidentified flattening example)**

* **Target Text:** "`path_walk_comprehension.py` flattens a tree with two `for` clauses.
Python 3.15 ([PEP 798](https://peps.python.org/pep-0798/))
adds a way to flatten with one `for` clause."
* **Issue:** PEP 798 cannot reduce `path_walk_comprehension.py` to a single `for` clause because constructing each path requires `(dirpath / f)`, combining variables from both the directory loop and the file loop. The two-`for` listing that is actually replaced by `[*row for row in rows]` in this section is `flatten.py` (`[x for row in rows for x in row]`), which is the exact listing quoted and contrasted in the prose below `unpacking_comprehensions.py`.
* **Instruction:** Reference `flatten.py` instead of `path_walk_comprehension.py`: "`flatten.py` flattens nested lists with two `for` clauses. Python 3.15 ([PEP 798](https://peps.python.org/pep-0798/)) adds a way to flatten with one `for` clause."

**2. Section: Choosing a Form (omission of dictionary unpacking syntax)**

* **Target Text:** "Braces for a set, or for a dict when a colon separates a key from a value."
* **Issue:** This summary repeats the pre-Python 3.15 delimiter rule and contradicts the preceding section, which demonstrated that `{**d for d in dicts}` builds a dictionary without a colon. As the previous section explained, unpacking comprehensions use `**` or `*` rather than a colon to decide between a dictionary and a set.
* **Instruction:** Update the sentence to account for PEP 798 unpacking: "Braces for a set (or with `*`), or for a dict when a colon separates a key from a value (or with `**`)."

**3. Section: The `map()` and `filter()` Equivalent (stale type checker claim)**

* **Target Text:** "Pyright infers the mixed list literal as `list[Unknown]` and checks nothing there."
* **Issue:** The book uses `ty` as its type checker, making remarks about Pyright off-topic. In addition, Pyright infers a literal list containing integers and strings (`[1, "4", 9, "a", 0, 4]`) as `list[int | str]`, not `list[Unknown]`.
* **Instruction:** Delete the sentence: "Pyright infers the mixed list literal as `list[Unknown]` and checks nothing there."

## Verdicts

Second run, on the Flash model. Applied in commit cdd67cfe, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2, `ty` 0.0.84, and Pyright 1.1.414.

1. Applied, with a different fix. `path_walk_comprehension.py`'s output expression is `(dirpath / f)`, which needs both loop variables, so PEP 798's single `for` cannot replace it, while `flatten.py`'s `[x for row in rows for x in row]` is the shape `[*row for row in rows]` replaces and the listing the section goes on to contrast. The sentence now names `flatten.py` and "nested lists"; the PEP sentence after it stands.
2. Applied, with a different fix. The section before shows `{**d for d in dicts}` building a dict with no colon, so the delimiter summary had fallen behind it. The sentence now reads "or for a dict when a colon separates a key from a value or `**` splices in a mapping", one clause rather than two parentheses; a bare `*` in braces still builds a set, which the "Braces for a set" head already covers.
3. Rejected. Under this repository's Pyright configuration, `reveal_type([1, "4", 9, "a", 0, 4])` reports `list[Unknown]` (`ty` reports `list[int | str]`), so the sentence states what Pyright does here, and the book's rule is that a claim holding for `ty` alone names `ty` and says what the other checkers do, which is this sentence's job.
