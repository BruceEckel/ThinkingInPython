<!-- outside review of Chapters/43_Functional--Confidence.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `43_Functional--Confidence.md` chapter:

**1. Section: Referential Transparency (qualifying external reads)**

* **Target Text:** "Substitution stops working the moment a function reads or writes outside itself."
* **Issue:** Reading outside a function does not break substitution if the referenced value is immutable, such as a module constant or a pure library function. Substitution fails only when reading mutable state, non-deterministic inputs (such as system clocks or environment variables), or writing side effects.
* **Instruction:** Change the sentence to: "Substitution stops working the moment a function reads mutable state or writes outside itself."

**2. Section: The Same Law in Hypothesis (decorator wrapping vs execution)**

* **Target Text:** "`@given(strategies.text())` calls `test_roundtrip()` once per generated string."
* **Issue:** `@given` is a decorator that returns a wrapped test function; decorating the function does not call it, and executing `test_property.py` as a script runs zero test cases. The underlying test function is called once per generated input only when executed by a test runner such as `pytest` or when invoked directly.
* **Instruction:** Change the sentence to: "When executed by a test runner, `@given(strategies.text())` calls `test_roundtrip()` once per generated string."

**3. Section: Shrinking a Failure (mischaracterization of the bug)**

* **Target Text:** "The next codec has a bug, and the bug is the unusual-Unicode case [The Same Law in Hypothesis](#the-same-law-in-hypothesis) mentions:"
* **Issue:** The preceding section did not mention a bug; it only noted that Hypothesis's strategy generates inputs beyond ASCII, such as unusual Unicode. The bug in `shrinking.py` is an asymmetric encoding/decoding mismatch (decoding with Latin-1 instead of UTF-8), which non-ASCII inputs expose rather than constitute.
* **Instruction:** Change the sentence to: "The next codec has a bug—decoding with Latin-1 instead of UTF-8—which surfaces on the non-ASCII characters [The Same Law in Hypothesis](#the-same-law-in-hypothesis) mentions:"

**4. Section: Shrinking a Failure (Hypothesis database configuration)**

* **Target Text:** "`database=None` discards the example database, so every run searches from scratch."
* **Issue:** In Hypothesis, `database=None` disables example database storage and lookup for that test run; it does not discard or delete existing database entries on disk. Discarding cached failures requires deleting the `.hypothesis/` directory, as described in Exercise 4.
* **Instruction:** Change the sentence to: "`database=None` disables the example database, so every run searches from scratch."

## Verdicts

Second run, on the Flash model. Applied in commit 9c7d9e25, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The sentence was looser than the book's own definition in [Pure Functions](../Chapters/40_Functional--Foundations.md#pure-functions), "It reads nothing that can change," since reading a module constant leaves substitution intact. The sentence now reads "reads something that can change, or writes outside itself," matching chapter 40 rather than introducing "mutable state."
2. Applied, with a different fix. A probe counting body calls printed 0 after decorating and 100 after one direct call to the decorated function, so `@given` wraps and the wrapper does the calling; the reviewer's "when executed by a test runner" is too narrow, since `shrinking.py` calls its wrapper directly. The sentence now says `@given(strategies.text())` wraps `test_roundtrip()` and each call to the wrapper runs the original body once per generated string.
3. Applied, with a different fix. The bug is the Latin-1 `decode()`, which the next paragraph already explains, and the non-ASCII input exposes it; the old sentence equated the two. The sentence now says the unusual Unicode the earlier section mentions exposes the bug; the reviewer's wording carried an em-dash and repeated the next paragraph's explanation.
4. Applied. Hypothesis's own `settings.database` docstring says "If ``None``, no storage will be used," and existing entries on disk stay, so "discards" misled; the sentence now says `database=None` turns off the example database.
