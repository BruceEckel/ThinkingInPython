<!-- outside review of Chapters/42_Functional--Error_Handling.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `42_Functional--Error_Handling.md` chapter:

**1. Section: Combining Multiple Results (Misdescribing step count as input count)**

* **Target Text:** "A third input adds a third level:"
* **Issue:** In `combining.py`, `combined(i, j)` accepts exactly two parameters (`i` and `j`), just like `pair(i, j)` in `combining_two.py`. The third level of nesting introduces a third `Result`-returning operation (`func_c(i + j)`), not a third input parameter.
* **Instruction:** Change "A third input adds a third level:" to "A third step adds a third level:".

**2. Section: Combining Multiple Results (Misdescribing call dependencies)**

* **Target Text:** "`func_a()`, `func_b()`,
and `func_c()` in `combining.py` take independent inputs,
so stopping at the first `Err` discards whatever the later steps would have found
(see exercise 3)."
* **Issue:** `func_c(i + j)` receives the sum `i + j`, so its argument is derived directly from the inputs to `func_a` and `func_b` rather than being an independent input. What makes these calls distinct from `composing_with_bind.py` is that none of the three functions depends on the return value (`a` or `b`) of an earlier step.
* **Instruction:** Update the sentence to clarify that the functions do not depend on earlier results: "`func_a()`, `func_b()`, and `func_c()` in `combining.py` do not depend on each other's answers, so stopping at the first `Err` discards whatever the later steps would have found (see exercise 3)."

**3. Section: Combining Multiple Results (Misdescribing nesting metric)**

* **Target Text:** "Three inputs need three levels of nesting,
and each input you add nests one level deeper."
* **Issue:** `combined(i, j)` takes two inputs, not three. The nesting depth corresponds to the number of intermediate `Result` values kept in scope to feed into `add(a, b, c)`, not the number of input parameters to the enclosing function.
* **Instruction:** Change to: "Three combined results need three levels of nesting, and each step you add nests one level deeper."

**4. Section: Attaching Context to an Exception (Inaccurate explanation of attribute type-checking and narrowing)**

* **Target Text:** "The `Err` branch reads `error.__notes__`,
and that read type-checks because the `match` narrowed the `Result` to `Err`.
The narrowing works because `Result` is a union of exactly two classes,
and it works the same way with `isinstance()`."
* **Issue:** In `noted_result.py`, `case Err(error):` binds `error` to the wrapped exception payload. The read `error.__notes__` type-checks because `error` has type `Exception` (declared by `parse_field`), where typeshed declares `__notes__`, not because `Err` itself has `__notes__`. Furthermore, pattern matching and union narrowing in Python do not depend on a union having "exactly two classes."
* **Instruction:** Replace the passage with: "The `Err` branch reads `error.__notes__`, and that read type-checks because the payload `error` has type `Exception`, where typeshed declares `__notes__`. Narrowing `Result` to `Err` extracts that exception payload, and it works the same way with `isinstance()`."

**5. Section: Composing by Hand (Conflating error checking with type alias limitations)**

* **Target Text:** "The check names `Err`, one of the two concrete classes,
because `Result` is a `type` alias rather than a class.
The type checker rejects `isinstance(a, Result)`,
and at runtime the call raises a `TypeError`."
* **Issue:** `composed()` checks `isinstance(a, Err)` because it needs to detect failure to return early; even if `Result` were a class (such as a base class of `Ok` and `Err`), testing `isinstance(a, Result)` would match both successes and failures and could not detect errors. While `isinstance(a, Result)` is indeed rejected because `Result` is a type alias, that is not why the code tests for `Err`.
* **Instruction:** Clarify the rationale: "The check tests for `Err` because `composed()` must distinguish failure from success to return early. It cannot check against `Result`, because `Result` is a `type` alias rather than a class: the type checker rejects `isinstance(a, Result)`, and at runtime the call raises a `TypeError`."

## Verdicts

Second run, on the Flash model. Applied in commit b37d71d3, after each item was tested against the chapter and run under `uv run`.

1. Applied. `combined(i, j)` takes two parameters, the same as `pair(i, j)`, so "a third input" counted something the listing does not add; the line now reads "A third step adds a third level:".
2. Applied, with a different fix. The Pro run's item 4 kept `func_c(i + j)` because the steps are independent of each other's answers, and the solution to exercise 3 says so; the sentence now says the three functions "take their inputs from `i` and `j` rather than from an earlier step's answer," the positive form of the reviewer's point.
3. Applied, with a different fix. The sentence now reads "Three steps need three levels of nesting, and each step you add nests one level deeper," matching item 1's "step" rather than introducing "combined results."
4. Applied, with a different fix. A `ty` probe with a three-member union `Ok[int] | Err[Exception] | Third` revealed `error` as `Exception` in a `case Err(error):` branch and `r.error` as `Exception` after `isinstance(r, Err)`, so narrowing does not depend on a two-class union. The paragraph now says the `match` narrows to `Err[Exception]`, so `error` is an `Exception`, and typeshed declares `__notes__` on `BaseException`; the "exactly two classes" sentence is gone.
5. Applied, with a different fix. `isinstance(Ok(1), Result)` raised `TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union`, so the facts stand, but the "because" gave the alias as the reason for testing `Err`. The paragraph now says each check tests for `Err`, the failure class, and states the alias fact as a separate consequence.
