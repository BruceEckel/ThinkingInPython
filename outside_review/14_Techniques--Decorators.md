<!-- outside review of Chapters/14_Techniques--Decorators.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `14_Techniques--Decorators.md` chapter:

**1. Section: Maintaining the Wrapped Interface (Metadata copied by `wraps`)**

* **Target Text:** "`__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotate__`, and `__type_params__`, the tuple `functools.WRAPPER_ASSIGNMENTS`"
* **Issue:** `__type_params__` is intentionally excluded from `functools.WRAPPER_ASSIGNMENTS` (since PEP 695). Copying it is unsupported because doing so would incorrectly assign type parameters to a wrapper that might not be generic or might have its own distinct type parameters.
* **Instruction:** Change to "`__module__`, `__name__`, `__qualname__`, `__doc__`, and `__annotate__`, the tuple `functools.WRAPPER_ASSIGNMENTS`"

**2. Section: Maintaining the Wrapped Interface (Generators also suspend execution)**

* **Target Text:** "`trace` assumes `func` runs to completion inside the call that invokes it, which is true of an ordinary function and false of an `async def` function."
* **Issue:** Generator functions also return immediately without running their bodies. A generator yields a generator object just as an `async def` function yields a coroutine object, so tracing one records its creation rather than its execution.
* **Instruction:** Change to "`trace` assumes `func` runs to completion inside the call that invokes it, which is true of an ordinary function but false of a generator or an `async def` function."

**3. Section: Decorating Classes (Type checker rejection for bare `type`)**

* **Target Text:** "If `register`'s annotation is `(cls: type) -> type`, `register()` hands back a bare `type`, and `ty` and Pyright see `Espresso()` as an `Any`."
* **Issue:** If the decorator returns a bare `type`, Pyright infers `Espresso` as the built-in `type` class itself. Calling `Espresso()` then fails type checking outright because the `type` constructor requires one or three arguments; it does not silently fall back to `Any`.
* **Instruction:** Change to "If `register`'s annotation is `(cls: type) -> type`, `register()` hands back a bare `type`, and `ty` and Pyright reject `Espresso()` because the built-in `type` constructor requires arguments."

## Verdicts

Applied in commit 163c7074, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2, `ty` 0.0.84, and Pyright 1.1.414.

1. Rejected. On 3.15.0rc2 `functools.WRAPPER_ASSIGNMENTS` is `('__module__', '__name__', '__qualname__', '__doc__', '__annotate__', '__type_params__')`, so the chapter's list is the tuple's contents and `__type_params__` belongs in it; the reviewer's exclusion claim is wrong for this Python.
2. Applied. A probe generator printed nothing when called and returned a `generator` object, the same deferred shape the section describes for a coroutine, and the chapter nowhere mentioned generators. The sentence now says the assumption is "false of a generator function or an `async def` function"; the rest of the section stays about the coroutine case it fixes.
3. Rejected. With `def register(cls: type) -> type`, both checkers agree with the chapter: `ty` reveals `Espresso` as `type` and `Espresso()` as `Any` with no error, and Pyright reports `Type of "e" is "Any"` with 0 errors. Neither rejects the call, so the sentence stands.
