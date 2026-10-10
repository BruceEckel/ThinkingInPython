<!-- outside review of Chapters/05_Foundations--Functions.md, model gemini-3.8-flash-high, 2026-10-10 -->

**Please apply the following technical and structural refinements to the `05_Foundations--Functions.md` chapter:**

**1. Section: Positional-Only and Keyword-Only Parameters (missing mechanism and kwargs collision)**

* **Target Text:** "Marking a parameter positional-only also keeps its name out of the method's contract.
That matters when a subclass overrides a method.
The subclass can rename the parameter, and the type checker accepts the rename."
* **Issue:** Method contracts and subclass renaming are only part of the motivation for positional-only parameters. A primary mechanism introduced in PEP 570 is that marking a parameter positional-only frees its name to appear in `**kwargs` without collision—a direct solution to the wrapper forwarding clash demonstrated in [`forwarding_collision.py`](file:///C:/git/ThinkingInPython/Chapters/05_Foundations--Functions.md#forwarding_collision.py) and the exact design required by Exercise 7's [`describe(name, /, **facts)`](file:///C:/git/ThinkingInPython/Chapters/05_Foundations--Functions.md#exercises).
* **Instruction:** After the quoted sentence, add a note explaining that positional-only parameters also prevent collisions with `**kwargs`: "Positional-only parameters also allow parameter names to be reused in `**kwargs` without collision. In a wrapper like `trace(func, /, *args, **kwargs)`, marking `func` positional-only guarantees that a caller can pass a keyword argument named `func` without triggering a duplicate argument error."

**2. Section: Lambdas (clarifying unbound class methods vs `operator.methodcaller`)**

* **Target Text:** "For a key that calls a method on each element,
`operator.methodcaller("lower")` replaces `lambda w: w.lower()`."
* **Issue:** Earlier in this section, the text notes that when an existing function computes the key, callers should pass it directly (`key=len`). For an argumentless method like `w.lower()`, the unbound class method [`str.lower`](file:///C:/git/ThinkingInPython/Chapters/05_Foundations--Functions.md#lambdas) already serves as that function without requiring `lambda` or the `operator` module; [`operator.methodcaller`](file:///C:/git/ThinkingInPython/Chapters/05_Foundations--Functions.md#lambdas) is primarily needed when the method call requires arguments (such as `methodcaller("strip", "!")`) or dispatches polymorphically across heterogeneous objects.
* **Instruction:** Replace the target sentence with: "For a method that takes no arguments, pass the class method directly: `key=str.lower` needs no lambda and no import. Use `operator.methodcaller()` when the method call requires arguments, such as `operator.methodcaller("strip", "!")`, or when elements share a method name across different classes."

**3. Section: Names Inside a Function (redundant compilation scope explanation)**

* **Target Text:** "Python decides which names are local when it compiles the function,
before any of it runs:
a name assigned anywhere in the body is local throughout the body."
* **Issue:** This sentence duplicates the concept and phrasing stated three sentences earlier immediately preceding [`function_scope.py`](file:///C:/git/ThinkingInPython/Chapters/05_Foundations--Functions.md#function_scope.py) ("Python decides which names are local when it compiles the function body, so where the assignment sits makes no difference.").
* **Instruction:** Trim the redundant declaration and connect directly to the behavior of `rebinds()`: "`rebinds()` leaves the module-level `count` alone because assigning to `count` inside the body binds a local name rather than modifying the global."

**4. Section: Default Arguments (clarifying keyword-only default exemption)**

* **Target Text:** "A parameter with a default cannot come before one with no default.
`def f(a=1, b):` is a `SyntaxError`:
`parameter without a default follows parameter with a default`.
[Keyword-only parameters](#positional-only-and-keyword-only-parameters)
are exempt, because the caller names them."
* **Issue:** Stating that keyword-only parameters are exempt because "the caller names them" can obscure the rule for readers new to Python: the restriction applies strictly to positional-or-keyword and positional-only ordering where argument binding depends on sequence. Readers often assume parameters without defaults must never follow defaults anywhere in a signature.
* **Instruction:** Clarify the exemption by specifying the syntax: "Keyword-only parameters are exempt: after `*` or `*args`, a parameter without a default can freely follow one with a default (such as `def f(*, a=1, b):`), because the caller must supply `b` by name and position cannot cause ambiguity."

## Verdicts

Second run, on the Flash model. Applied in commit 2e47d3f6, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied, with a different fix. A probe of `def trace(func, /, *args, **kwargs)` accepted `trace(print, func=3)` with `{'func': 3}` in `kwargs`, while the same signature without the `/` raised `TypeError: trace2() got multiple values for argument 'func'`, so the mechanism is real and the section had not named it. The reviewer's framing is wrong in one respect: `forwarding_collision.py`'s clash is on `report()`'s `label`, which a `/` on `trace()`'s `func` leaves untouched, so the new sentence gives the `trace()` signature as its own example and claims nothing about that listing.
2. Applied, with a different fix. `sorted(words, key=str.lower)` and `key=operator.methodcaller("lower")` gave the same order in a probe, and the section's own rule three paragraphs up is "When an existing function computes the key, pass that function", so the paragraph now adds that when every element is a `str`, `str.lower` replaces the lambda too. The `methodcaller()` sentence stays, since it is the one of the three `operator` helpers the paragraph is listing; the reviewer's longer rewrite about arguments and heterogeneous classes is an alternative-API comment.
3. Applied, with a different fix. Lines 315-317 state the compile-time rule before `function_scope.py`, and the three lines after the listing repeated it. They are gone; the sentence now reads "`rebinds()` leaves the module-level `count` alone, because its `count = 99` binds a local", and the `+=` sentence that follows gets a "too" so it still reads as a second assignment.
4. Applied, with a different fix. `def f(*, a=1, b): ...` compiled and `f(b=2)` returned `(1, 2)`, so the exemption is real and the sentence lacked its shape. It now reads "are exempt: `def f(*, a=1, b):` is legal, because the caller names `b`", one clause in place of the reviewer's four.
