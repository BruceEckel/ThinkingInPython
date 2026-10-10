<!-- outside review of Chapters/02_Foundations--Tour.md, model gemini-3.8-flash-high, 2026-10-10 -->

**Please apply the following technical and structural refinements to the `02_Foundations--Tour.md` chapter:**

**1. Section: Indentation and Blocks (scope of TabError)**

* **Target Text:** "and mixing tabs and spaces inconsistently inside one block raises a `TabError`."
* **Issue:** In Python 3, mixing tabs and spaces anywhere within the same file raises a `TabError`, even if each individual block consistently uses only one or the other. Saying "inside one block" recalls the Python 2 rule and suggests to a reader that different blocks in the same file could choose different indentation characters.
* **Instruction:** Replace "inconsistently inside one block" with "in the same file" (e.g., "and mixing tabs and spaces in the same file raises a `TabError`.").

**2. Section: Naming Conventions (built-in types vs. callable classes)**

* **Target Text:** "The standard library names `contextlib.suppress`, `functools.partial`, and the built-ins `property` and `staticmethod` that way."
* **Issue:** `property` and `staticmethod` are not written in `snake_case` (they contain no underscores; `staticmethod` is run-together lowercase), nor are they named after actions. They are built-in types that follow PEP 8's separate convention for built-in names (single words or run-together lowercase, like `classmethod` and `frozenset`), distinct from function-like standard library classes such as `contextlib.suppress` or `contextlib.redirect_stdout`.
* **Instruction:** Remove the built-ins or replace them with genuine standard-library `snake_case` classes, such as `contextlib.redirect_stdout`.

**3. Section: t-Strings (alternation of template pieces)**

* **Target Text:** "Iteration skips empty literal strings, so the leading `''` in `message.strings` does not reach the loop. That skipping is why a consumer cannot assume that literals and interpolations alternate."
* **Issue:** While skipping empty strings explains why a consumer might see two consecutive `Interpolation` objects (for instance, in `t"{first}{second}"`), it does not explain why a consumer cannot assume alternation in general: even if empty strings were kept, adjacent literals or adjacent interpolations without an interleaved element would still violate naive alternation once empty strings are dropped. Clarifying that adjacent interpolations produce consecutive `Interpolation` items during iteration directly grounds why consumers must check types with `isinstance` rather than assuming a rigid `str`, `Interpolation`, `str` cadence.
* **Instruction:** Clarify the second sentence to note that adjacent interpolations (or leading/trailing interpolations) mean consumers encounter consecutive interpolations rather than an alternating sequence of `str` and `Interpolation`.

## Verdicts

Second run, on the Flash model. Applied in commit b5fb0b58, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. A probe compiled a file whose first function body is tab-indented and whose second is space-indented, each block consistent, and it ran (`1 2`); `TabError: inconsistent use of tabs and spaces in indentation` came only when one block's lines mixed the two. The "anywhere in the same file" rule the reviewer states is not Python 3's, so the chapter's "inconsistently inside one block" stands.
2. Applied, with a different fix. PEP 8 gives built-in names their own convention (single words or words run together), and `staticmethod` is run-together rather than `snake_case`, so the two built-ins were weak examples of the rule the paragraph states. The sentence now names `contextlib.suppress`, `contextlib.redirect_stdout`, and `functools.partial`, each confirmed a class with `inspect.isclass()`, and drops the built-ins rather than explaining a second convention in a paragraph about the first.
3. Applied, with a different fix. The reviewer's reasoning is wrong: `Template.strings` always holds one more entry than the interpolations, empties included, so kept empties would alternate strictly, and the skipping is the cause the chapter names. A probe of `t"{a}{b}"` gave `strings == ('', '', '')` and an iteration of two `Interpolation`s in a row, which is the concrete case the reviewer asked for, so the sentence keeps its causal claim and now ends with that example.
