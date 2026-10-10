<!-- outside review of Chapters/10_Foundations--Cleanup.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `10_Foundations--Cleanup.md` chapter:

**1. Section: Reference Cycles Delay Destruction (Factual error)**
* **Target Text:** "The only referrer is `node`, which confirms the self-reference."
* **Issue:** At the moment `gc.get_referrers(node)` runs, the local variable `node` still exists, so the local frame is also a referrer. Because the list contains multiple referrers, `node` is not the *only* referrer, which is why the code checks index `[0]` instead of asserting the list has a length of one.
* **Instruction:** Change to "One of the referrers is `node` itself, which confirms the self-reference."

**2. Section: The Rule (Technical refinement)**
* **Target Text:** "catching a forgotten `close()` rather than replacing it:"
* **Issue:** Because `__del__()` successfully closes the file, it actually does act as a fallback replacement for the forgotten `close()`. The crucial distinction the `ResourceWarning` provides is that it refuses to do so *silently* as a primary design mechanism.
* **Instruction:** Change to "catching a forgotten `close()` rather than silently replacing it:"

**3. Section: The Rule (Structural refinement)**
* **Target Text:** "Give a class that owns a resource a `close()` method and a `with` block that calls it, so the cleanup runs at a point in the program you can see."
* **Issue:** A class itself does not possess a `with` block; rather, it implements the context manager protocol to allow callers to use it in one. The current phrasing implies the `with` block is part of the class's definition.
* **Instruction:** Change to "Give a class that owns a resource a `close()` method and the context manager methods (`__enter__` and `__exit__`) that let a `with` block call it, so the cleanup runs at a point in the program you can see."

## Verdicts

Applied in commit 03766d2e, after each item was tested against the chapter and run under `uv run`.

1. Rejected. A probe of the listing's shape on 3.15.0rc2, with `gc.disable()` in force, gave `len(gc.get_referrers(node)) == 1` and that one referrer of type `Node`: a function's locals live in the frame's fast-locals array, which the collector does not report as a referring object, so `node` is the only referrer and the sentence stands.
2. Rejected. The participle "catching a forgotten `close()` rather than replacing it" modifies the `ResourceWarning` report, which catches the mistake and replaces nothing; the `__del__()` close is named separately in the same sentence. The next paragraph's "exists to catch the mistake, not to be the plan" already draws the distinction the reviewer wants, and "silently" would add a second negative to a sentence that reads clearly.
3. Applied, with a different fix. A class gets methods, and the chapter's own `Socket` listing gives it `__enter__()` and `__exit__()`, with `__exit__()` calling `close()`. The sentence now reads "a `close()` method and an `__exit__()` that calls it, so the cleanup runs as a `with` block ends"; naming `__enter__()` too, as the reviewer proposed, is not needed for the point about where the cleanup runs.
