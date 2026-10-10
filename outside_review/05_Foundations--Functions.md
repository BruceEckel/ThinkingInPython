<!-- outside review of Chapters/05_Foundations--Functions.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `05_Foundations--Functions.md` chapter:

**1. Positional-Only and Keyword-Only Parameters (Semantics of *args)**

* **Target Text:** "A `*args` parameter has the same effect as a bare `*`. `*args` absorbs every remaining positional argument, so a parameter declared after it can arrive by name alone."
* **Issue:** Stating that `*args` has the same effect as a bare `*` is technically inaccurate for the function as a whole; a bare `*` strictly forbids additional positional arguments, while `*args` explicitly collects them. They only share the specific effect of making subsequent parameters keyword-only.
* **Instruction:** Replace these two sentences with: "A `*args` parameter makes the parameters that follow it keyword-only, just as a bare `*` does. Because `*args` absorbs every remaining positional argument, any parameter declared after it must arrive by name."

**2. Variable Argument Lists (Terminology clarification)**

* **Target Text:** "The `*` and `**` do the collecting, so `*values` and `**options` behave identically."
* **Issue:** "Behave identically" by itself implies `*values` and `**options` behave identically to each other, which is false (one collects into a tuple, the other into a dictionary). The intent is that they behave exactly like the conventionally named `*args` and `**kwargs`.
* **Instruction:** Change the text to: "The `*` and `**` do the collecting, so `*values` and `**options` behave exactly like `*args` and `**kwargs`."

**3. Positional-Only and Keyword-Only Parameters (Forwarding collisions)**

* **Target Text:** "That matters when a subclass overrides a method. The subclass can rename the parameter, and the type checker accepts the rename."
* **Issue:** The chapter just showed how a forwarding function's `**kwargs` can collide with the wrapped function's parameters, but misses that the forwarding function itself is vulnerable to collisions if its own parameter name appears in `**kwargs` (e.g., `trace` crashing if `opts` contains `"func"`). Positional-only parameters solve this exact problem by keeping the wrapper's parameter names out of the keyword arguments.
* **Instruction:** Add a sentence at the end of the paragraph: "It also protects a forwarding function like `trace()` from collisions: if declared as `def trace(func, /, *args, **kwargs):`, a caller can safely pass `func` as a keyword argument for the wrapped function to consume."

**4. Unpacking Arguments (Scope accuracy)**

* **Target Text:** "The same `func(*args, **kwargs)` call spreads `nums` positionally, so `report()`'s first parameter, `label`, also receives `1`, and no parameter can take two values."
* **Issue:** Inside `trace()`, the tuple being spread by the `*` operator is the local parameter `args`, not `nums`. `nums` is a variable in the caller's scope that `trace()` has no access to; it only sees the collected `args` tuple.
* **Instruction:** Change "`nums`" to "`args`" in the sentence: "The same `func(*args, **kwargs)` call spreads `args` positionally, so `report()`'s first parameter, `label`, also receives `1`, and no parameter can take two values."

## Verdicts

Applied in commit 9abe5b0d, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. A bare `*` rejects extra positional arguments (`f(1, 2, b=3)` against `def f(a, *, b)` raised "takes 1 positional argument but 2 ... were given") while `*args` collects them, so "the same effect" overstated the match. The sentence now says `*args` "also begins the keyword-only parameters", the one effect the two share, and keeps the chapter's own explanation of why.
2. Applied. "Behave identically" read as a comparison between `*values` and `**options`, a tuple and a dictionary. The sentence now says they "behave like `*args` and `**kwargs`".
3. Rejected. The listing never passes `func` as a keyword, so the collision is a case it does not run, and the paragraph is about a subclass renaming an overridden method's parameter. The chapter already gives the reader this use of `/` as exercise 7, `describe(name, /, **facts)`. (The claim is right: a probe of `trace(report, "p", func=1)` raised "got multiple values for argument 'func'" and the `func, /` form forwarded `func=1` to `report()`'s `**options`.)
4. Applied. `trace()` spreads its parameter `args`, a tuple holding the items of `nums`, which is a name in the caller's scope. The sentence now says "spreads `args`, which holds the items of `nums`".
