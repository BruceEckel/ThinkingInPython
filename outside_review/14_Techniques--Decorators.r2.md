<!-- outside review of Chapters/14_Techniques--Decorators.md, model gemini-3.8-flash-high, 2026-10-10 -->

**Please apply the following technical and structural refinements to the `14_Techniques--Decorators.md` chapter:**

**1. Section: What @ Does Not Require (type inference contradiction)**

* **Target Text:** "The lambda's parameter has no annotation, so `ty` reports `fib_table` as `Unknown`, where the generic `run_once` carries `T` through to `str`."
* **Issue:** In `lambda_decorator.py`, `fib_table()` returns `list[int]`. Saying `run_once` carries `T` through to `str` mistakenly repeats the return type of `greeting` from `run_once.py` rather than the return type of `fib_table`.
* **Instruction:** Change `str` to `list[int]`: "The lambda's parameter has no annotation, so `ty` reports `fib_table` as `Unknown`, where the generic `run_once` carries `T` through to `list[int]`."

**2. Section: Decorators With Optional Parentheses (caveat on callable decorator arguments)**

* **Target Text:** "The `callable(func)` test assumes that only the decorated function can arrive in that first position. Where a decorator's own argument could be callable, checking `func is None` instead of `callable(func)` removes the ambiguity."
* **Issue:** If a decorator argument can be callable and is accepted positionally, passing it as `@dec(my_callable)` places `my_callable` in `func`. Because `my_callable` is not `None`, checking `func is None` evaluates to `False` and still mistakes the configuration argument for the decorated function. The ambiguity is resolved only if the decorator forces its configuration arguments to be keyword-only, guaranteeing that `func` remains `None` when called with arguments.
* **Instruction:** Clarify that keyword-only parameters are required: "Where a decorator's own argument could be callable, making configuration arguments keyword-only and checking `func is None` instead of `callable(func)` removes the ambiguity."

**3. Section: A Limitation: Methods Need a Descriptor (overbroad qualification)**

* **Target Text:** "The class form has one limitation. A method decorated this way becomes an instance rather than a function, and the call then fails."
* **Issue:** This limitation only applies when the decorator class instance directly replaces the decorated method (as in `logged` or `trace_class.py`). As the chapter points out shortly after with `repeat_class.repeat`, class decorators taking arguments return an ordinary wrapper function from `__call__()` and therefore bind to instances without issue.
* **Instruction:** Clarify that the limitation applies specifically when the decorator instance stands in for the function: "The class form has one limitation when the decorator instance itself replaces the method: it becomes an instance rather than a function, and the call then fails."

**4. Section: What @ Does Not Require (omitted grammar targets)**

* **Target Text:** "`@` constrains the statement below it. A decorator line must sit directly above a `def` or a `class`."
* **Issue:** In Python syntax, a decorator line can also sit directly above another decorator line (as shown in `## Stacking Decorators`), or above an `async def` function (as discussed in `### A Coroutine Function Needs an async Wrapper`).
* **Instruction:** Update the sentence to enumerate the actual syntactic targets: "`@` constrains the statement below it. A decorator line must sit directly above a `def`, `async def`, `class`, or another decorator line."

## Verdicts

Second run, on the Flash model. Applied in commit 6cb041e8, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied, with a different fix. The `str` is right: `run_once.py` decorates `greeting() -> str`, and the sentence contrasts that listing's inference with `lambda_decorator.py`'s `Unknown`. The reviewer read it as a claim about `fib_table`, which the wording allowed, so the sentence now says "carries `T` through to `greeting`'s `str`" and keeps the type.
2. Applied, with a different fix. A probe decorator with a positional `times` parameter and a `func is None` test took `opt_pos(print)` as the decorated function, while the keyword-only form did not, so the `is None` test alone leaves the ambiguity the reviewer names. `label`'s `prefix` is already keyword-only (`*, prefix: str = "LOG"`), so the sentence now says to keep the arguments keyword-only as `label` does, check `func is None`, and why: a callable passed positionally lands in `func` and passes either test.
3. Applied, with a different fix. The section's own later paragraph says `repeat_class.repeat` escapes the limitation because its `__call__()` returns an ordinary function, so "A method decorated this way" overreached. The first sentence now names the condition, "when the instance replaces the function it decorates", and the second says "decorated that way".
4. Applied. A probe compiled a decorator above `async def` and two stacked decorators above a `def`, and the chapter's own Stacking Decorators and `async` wrapper sections use both forms. The sentence now lists `def`, `async def`, `class`, and another decorator line.
