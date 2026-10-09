<!-- outside review of Chapters/22_Patterns--Data_Transfer_Objects.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `22_Patterns--Data_Transfer_Objects.md` chapter:

**1. Section: A Hand-Rolled Messenger (Parameter precision)**

* **Target Text:** "Because `**kwargs` is the only parameter,"
* **Issue:** `self` is also a parameter of `__init__()`. Because `self` is not marked as positional-only in this snippet, passing `self=1` as a keyword argument would clash with the implicit `self` and raise a `TypeError`, meaning the class does not unconditionally accept every possible keyword name.
* **Instruction:** Change to "Because `**kwargs` is the only parameter besides `self`,"

**2. Section: A Hand-Rolled Messenger (Type declaration accuracy)**

* **Target Text:** "(its read half is `__getattribute__()`, which intercepts every attribute access),"
* **Issue:** The type stub for `SimpleNamespace` in `typeshed` actually declares `__getattr__`, not `__getattribute__`. In Python type hinting, `__getattr__` is the standard mechanism to signal to type checkers that arbitrary missing attributes are permitted.
* **Instruction:** Remove the parenthetical entirely, or change it to `(its read half is \`__getattr__()\`, which intercepts missing attribute access),`.

**3. Section: Returning Multiple Values (Type checker inference behavior)**

* **Target Text:** "`count, mean = summarize(data)` runs, passes the type checker,"
* **Issue:** The type checker only passes this assignment because it blindly infers the types of the unannotated local variables from the returned tuple's positions (inferring `count` as a `float` and `mean` as an `int`). If the reader were to explicitly annotate their local variables (e.g., `count: int`), the type checker *would* catch the positional mismatch.
* **Instruction:** Change to "`count, mean = summarize(data)` runs, passes the type checker (which infers the reversed types for the local variables unless you annotate them),"

## Verdicts

Applied in commit 7df73c3c, after each item was tested against the chapter and run under `uv run`.

1. Applied. `self` is a parameter too: a probe of the listing's class with `Messenger(self=1)` raised `TypeError: M.__init__() got multiple values for argument 'self'`. The sentence now reads "the only parameter after `self`"; the `self=1` clash is a case the listing never exercises, so the chapter does not mention it.
2. Rejected. `ty` 0.0.84's vendored stub declares `__getattribute__()` on `SimpleNamespace`: `reveal_type(SimpleNamespace.__getattribute__)` shows `def __getattribute__(self, name: str, /) -> Any`, and `SimpleNamespace.__getattr__` draws `unresolved-attribute`. Pyright's bundled typeshed (`stdlib/types.pyi`, line 307) has the same `__getattribute__` and no `__getattr__`, so the parenthetical is right.
3. Rejected. The sentence is accurate: `ty` infers `count` as `float` and `mean` as `int` and reports nothing. Annotating the locals catches one half (`c2: int` drew `invalid-assignment`, while `m2: float` accepts the `int`), and catches nothing when the fields share a type, so the parenthetical would offer a partial guard in place of the chapter's point that reading by name has no order to get wrong.
