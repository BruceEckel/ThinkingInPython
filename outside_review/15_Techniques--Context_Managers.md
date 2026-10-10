<!-- outside review of Chapters/15_Techniques--Context_Managers.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `15_Techniques--Context_Managers.md` chapter:

**1. A Basic Context Manager (factual error)**
* **Target Text:** "so reusing the same object in a second `with` fails with a message that names nothing useful: `AttributeError: '_GeneratorContextManager' object has no attribute 'args'`."
* **Issue:** Reusing a `@contextmanager` object attempts to advance an already-exhausted generator. In modern Python, this raises `RuntimeError: generator didn't yield`, not an `AttributeError`.
* **Instruction:** Replace the sentence with: "so reusing the same object in a second `with` fails with `RuntimeError: generator didn't yield`."

**2. The `__exit__()` Arguments (factual error)**
* **Target Text:** "An `__exit__()` that returns the result of its last cleanup call, such as a count or a status string, swallows every exception its block raises."
* **Issue:** A returned cleanup result only suppresses the exception if it evaluates to true (like a non-zero count or a non-empty string). If the cleanup call returns a falsy value (such as `0` or `""`), the exception propagates, making the suppression unpredictable rather than absolute.
* **Instruction:** Change the sentence to: "An `__exit__()` that returns the result of its last cleanup call, such as a count or a status string, accidentally swallows the block's exception whenever that result is truthy."

**3. Guaranteed Cleanup (clarification)**
* **Target Text:** "The ones that entered still exit, and the failing one alone gets no `__exit__()` call."
* **Issue:** The phrase "the failing one alone" ignores managers listed after the failing one in a comma-separated `with`. If a manager fails to enter, any subsequent managers in the list are never evaluated and also receive no `__enter__()` or `__exit__()` calls.
* **Instruction:** Update the sentence to: "The ones that entered still exit, and the failing one gets no `__exit__()` call, nor do any managers listed after it."

## Verdicts

Applied in commit 70ba346a, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. A probe that reused one `@contextmanager` object in a second `with` raised `AttributeError: '_GeneratorContextManager' object has no attribute 'args'`, the chapter's message to the character; `RuntimeError: generator didn't yield` is what an exhausted generator raises in other paths, and the chapter's point is that this message names nothing useful.
2. Applied. A probe `__exit__()` returning `0` let a `ValueError` propagate, so "swallows every exception" overstated it; the paragraph's own "Any truthy value suppresses" is the condition. The sentence now reads "swallows the block's exception whenever that result is truthy".
3. Applied, with a different fix. A probe `with M("a"), M("b", fail=True), M("c"):` printed `enter a`, `enter b`, `exit a`, and nothing for `c`, so "the failing one alone" left out the managers after it, which the statement never reaches. The sentence now says the failing one gets no `__exit__()` call and the statement stops there, leaving the managers listed after it alone.
